"""Centralized filesystem paths for the training repo.

Keeping paths in one module prevents every backend file from guessing where
config, generated data, and output artifacts live.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Config is edited by students; generated/output folders are produced by code.
CONFIG_DIR = ROOT / "config"
DATA_DIR = ROOT / "data"
GENERATED_DIR = DATA_DIR / "generated"
OUTPUT_DIR = DATA_DIR / "outputs"
