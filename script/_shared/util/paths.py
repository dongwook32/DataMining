"""Paths anchored to the repository, independent of the current directory."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
PAPER = ROOT / "output" / "paper_20261116"
BASELINE = "RUN_PHASE5_6_20261027_184959"
