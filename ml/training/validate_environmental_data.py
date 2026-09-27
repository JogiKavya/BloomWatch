"""Fail fast when an environmental dataset lacks a genuine HAB target.

This is deliberately a validation step, not a label-generation script.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd

HAB_LABEL_NAMES = {"hab", "hab_occurrence", "harmful_algal_bloom", "bloom_observed", "algal_bloom"}

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("csv", type=Path); args = parser.parse_args()
    frame = pd.read_csv(args.csv, nrows=100)
    candidates = {column.strip().lower().replace(" ", "_") for column in frame.columns} & HAB_LABEL_NAMES
    if not candidates:
        raise SystemExit("No validated HAB target found. Do not train a HAB classifier or manufacture labels from environmental thresholds.")
    print("Candidate HAB target columns:", sorted(candidates))

if __name__ == "__main__": main()
