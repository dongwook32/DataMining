"""Paths independent of the terminal's working directory."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / 'research_web'
RESULTS_JSON = WEB / 'data' / 'research_data.json'
SUMMARY = ROOT / 'output' / 'summary'
VALIDATION = ROOT / 'docs' / 'validation'
