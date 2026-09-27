"""Generate reproducible EDA figures from the supplied datasets."""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("data_dir", type=Path, help="Directory containing the CSV datasets")
    parser.add_argument("--output", type=Path, default=ROOT / "reports" / "figures")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    ocean = pd.read_csv(args.data_dir / "synthetic_ocean_quality_realistic.csv")
    features = [c for c in ocean.columns if c != "Quality"]
    ocean[features].hist(figsize=(14, 8), bins=30)
    plt.tight_layout(); plt.savefig(args.output / "ocean_feature_histograms.png", dpi=160); plt.close("all")

    corr = ocean[features].corr()
    fig, ax = plt.subplots(figsize=(9, 7))
    image = ax.imshow(corr, aspect="auto")
    ax.set_xticks(range(len(features)), features, rotation=45, ha="right")
    ax.set_yticks(range(len(features)), features)
    fig.colorbar(image, ax=ax, label="Correlation")
    ax.set_title("Environmental Feature Correlation")
    fig.tight_layout(); fig.savefig(args.output / "ocean_correlation_heatmap.png", dpi=160); plt.close(fig)

    counts = ocean["Quality"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(6, 4)); counts.plot(kind="bar", ax=ax)
    ax.set_xlabel("Quality"); ax.set_ylabel("Samples"); ax.set_title("Quality Label Distribution")
    fig.tight_layout(); fig.savefig(args.output / "ocean_quality_distribution.png", dpi=160); plt.close(fig)

    beach_path = args.data_dir / "Beach_Clean.csv"
    if beach_path.exists():
        beach = pd.read_csv(beach_path, usecols=["Unnamed: 0", "EXO3(Chlorophyll_ug_L)"])
        beach["timestamp"] = pd.to_datetime(beach["Unnamed: 0"])
        fig, ax = plt.subplots(figsize=(12, 4)); ax.plot(beach["timestamp"], beach["EXO3(Chlorophyll_ug_L)"], linewidth=.35)
        ax.set_ylabel("Chlorophyll (ug/L)"); ax.set_title("Beach Chlorophyll Time Series")
        fig.tight_layout(); fig.savefig(args.output / "beach_chlorophyll_timeseries.png", dpi=160); plt.close(fig)

    print(f"EDA figures saved to {args.output}")


if __name__ == "__main__":
    main()
