"""USD to INR conversion with a safe cached fallback."""

from __future__ import annotations

from datetime import datetime, timezone

import requests

FALLBACK_USD_TO_INR = 85.0
FRANKFURTER_URL = "https://api.frankfurter.dev/v1/latest?base=USD&symbols=INR"


def get_usd_to_inr_rate() -> tuple[float, str, str]:
    """Fetch the latest USD/INR rate from Frankfurter; remain usable offline."""
    try:
        response = requests.get(FRANKFURTER_URL, timeout=8)
        response.raise_for_status()
        payload = response.json()
        return float(payload["rates"]["INR"]), str(payload.get("date", "latest")), "Live Frankfurter rate"
    except (requests.RequestException, KeyError, TypeError, ValueError):
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        return FALLBACK_USD_TO_INR, timestamp, "Fallback rate (API unavailable)"
