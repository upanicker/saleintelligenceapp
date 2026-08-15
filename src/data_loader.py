"""CSV ingestion, validation, and data normalization."""

from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

import pandas as pd

REQUIRED_COLUMNS = {
    "Opportunity ID", "Opportunity Name", "Account", "Territory", "Country",
    "Sales Rep", "Stage", "Amount ($)", "Probability %", "Close Date",
    "Product", "Industry",
}


def validate_columns(columns: list[str] | pd.Index) -> list[str]:
    """Return required input columns missing from an uploaded CSV."""
    return sorted(REQUIRED_COLUMNS.difference(columns))


def normalize_data(raw: pd.DataFrame) -> pd.DataFrame:
    """Create analysis-ready fields without changing the source opportunity data."""
    data = raw.copy()
    data["Amount ($)"] = pd.to_numeric(data["Amount ($)"], errors="coerce").fillna(0.0)
    probability = pd.to_numeric(data["Probability %"], errors="coerce").fillna(0.0)
    # Support both decimal probabilities (0.65) and percentage input (65).
    data["Probability"] = probability.where(probability <= 1, probability / 100).clip(0, 1)
    data["Close Date"] = pd.to_datetime(data["Close Date"], errors="coerce")
    if "Created Date" in data:
        data["Created Date"] = pd.to_datetime(data["Created Date"], errors="coerce")
    else:
        data["Created Date"] = pd.NaT
    data["Region"] = data["Territory"].fillna("Unassigned").astype(str)
    data["Close Quarter"] = data["Close Date"].dt.to_period("Q").astype(str).replace("NaT", "Unknown")
    data["Weighted Pipeline ($)"] = data["Amount ($)"] * data["Probability"]
    return data


def read_csv(source: str | Path | BinaryIO) -> tuple[pd.DataFrame | None, list[str]]:
    """Read a CSV and return either normalized data or its missing columns."""
    raw = pd.read_csv(source)
    missing = validate_columns(raw.columns)
    if missing:
        return None, missing
    return normalize_data(raw), []


def data_warnings(data: pd.DataFrame) -> list[str]:
    warnings: list[str] = []
    invalid_dates = data["Close Date"].isna().sum()
    if invalid_dates:
        warnings.append(f"{invalid_dates} row(s) have an invalid or missing close date.")
    invalid_amounts = (data["Amount ($)"] <= 0).sum()
    if invalid_amounts:
        warnings.append(f"{invalid_amounts} row(s) have a zero or missing amount.")
    return warnings
