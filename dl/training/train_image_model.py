"""Train the image component on the supplied paddy algae archive.

The dataset has three genuine visual classes: algae, early_stage and not_algae.
It is not a validated HAB image dataset, so this model reports visible algae only.
"""
from __future__ import annotations

import argparse
import json
import shutil
import zipfile
from pathlib import Path

import numpy as np
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix

ROOT = Path(__file__).resolve().parents[2]


def extract_if_needed(archive: Path, destination: Path) -> Path:
    dataset = destination / "dataset"
    if dataset.exists():
        return dataset
    with zipfile.ZipFile(archive) as bundle:
        safe_members = [member for member in bundle.infolist() if not Path(member.filename).is_absolute() and ".." not in Path(member.filename).parts]
        bundle.extractall(destination, safe_members)
    return dataset


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True, help="Path to the paddy algae ZIP archive")
    parser.add_argument("--epochs", type=int, default=15)
    args = parser.parse_args()
    if not args.archive.exists():
        raise FileNotFoundError(f"Archive not found: {args.archive}")
    tf.keras.utils.set_random_seed(42)
    data_dir = extract_if_needed(args.archive, ROOT / "data" / "image_dataset")
    train_ds = tf.keras.utils.image_dataset_from_directory(data_dir, validation_split=.20, subset="training", seed=42, image_size=(224, 224), batch_size=24)
    validation_ds = tf.keras.utils.image_dataset_from_directory(data_dir, validation_split=.20, subset="validation", seed=42, image_size=(224, 224), batch_size=24, shuffle=False)
    class_names = train_ds.class_names
    autotune = tf.data.AUTOTUNE
    train_ds = train_ds.shuffle(512, seed=42).prefetch(autotune)
    validation_ds = validation_ds.prefetch(autotune)
    augmentation = tf.keras.Sequential([tf.keras.layers.RandomFlip("horizontal"), tf.keras.layers.RandomRotation(.06), tf.keras.layers.RandomZoom(.08)])
    base = tf.keras.applications.MobileNetV2(include_top=False, weights="imagenet", input_shape=(224, 224, 3))
    base.trainable = False
    model = tf.keras.Sequential([augmentation, tf.keras.applications.mobilenet_v2.preprocess_input, base, tf.keras.layers.GlobalAveragePooling2D(), tf.keras.layers.Dropout(.25), tf.keras.layers.Dense(len(class_names), activation="softmax")])
    model.compile(optimizer=tf.keras.optimizers.Adam(1e-3), loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    out = ROOT / "dl" / "saved_models"; out.mkdir(parents=True, exist_ok=True)
    callbacks = [tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=4, restore_best_weights=True), tf.keras.callbacks.ModelCheckpoint(out / "algae_mobilenetv2.keras", monitor="val_loss", save_best_only=True)]
    history = model.fit(train_ds, validation_data=validation_ds, epochs=args.epochs, callbacks=callbacks)
    y_true = np.concatenate([y.numpy() for _, y in validation_ds]); y_prob = model.predict(validation_ds); y_pred = y_prob.argmax(axis=1)
    metrics = {"classification_report": classification_report(y_true, y_pred, target_names=class_names, output_dict=True), "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(), "history": history.history}
    (out / "image_metadata.json").write_text(json.dumps({"class_names": class_names, "image_size": [224, 224], "dataset_note": "Visual algae screening only; not a HAB confirmation."}, indent=2), encoding="utf-8")
    (out / "image_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"Saved model and real validation metrics to {out}")


if __name__ == "__main__":
    main()
