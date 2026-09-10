"""
Download and load the Stack Overflow Developer Survey 2025 data.

The dataset is fetched from Kaggle through kagglehub and copied into
data/raw/ once, so every later run reads the same local snapshot instead of
whatever the remote dataset currently holds.
"""

import shutil
from pathlib import Path

import kagglehub
import pandas as pd

KAGGLE_DATASET = "edoardogalli/stack-overflow-annual-developer-survey-2025"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"

RESPONSES_FILE = "survey_results_public.csv"
SCHEMA_FILE = "survey_results_schema.csv"


def download_raw(force=False):
    """Copy the survey CSV files into data/raw/ and return that directory.

    Downloads from Kaggle only when a file is missing locally, or when force
    is True.
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    targets = [RAW_DIR / RESPONSES_FILE, RAW_DIR / SCHEMA_FILE]

    if not force and all(t.exists() for t in targets):
        return RAW_DIR

    source = Path(kagglehub.dataset_download(KAGGLE_DATASET))
    for name in (RESPONSES_FILE, SCHEMA_FILE):
        shutil.copy(source / name, RAW_DIR / name)
    return RAW_DIR


def load_raw(force_download=False):
    """Return the responses and schema tables as two DataFrames.

    utf-8-sig strips the BOM that sits in front of the first column name
    (ResponseId); low_memory=False avoids mixed dtype inference on the wide
    multi-select columns.
    """
    raw_dir = download_raw(force=force_download)
    responses = pd.read_csv(
        raw_dir / RESPONSES_FILE, low_memory=False, encoding="utf-8-sig"
    )
    schema = pd.read_csv(raw_dir / SCHEMA_FILE, encoding="utf-8-sig")
    return responses, schema


def question_text(schema):
    """Return a Series mapping column name to the original survey question."""
    return schema.drop_duplicates(subset="qname").set_index("qname")["question"]
