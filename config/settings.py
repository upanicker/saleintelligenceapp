"""Application-level settings."""

DEFAULT_REVENUE_TARGET_USD = 500_000.0
DEFAULT_LARGE_DEAL_THRESHOLD_USD = 25_000.0
CURRENCY_CACHE_TTL_SECONDS = 60 * 60
OPEN_STAGES = ("Prospecting", "Qualification", "Proposal", "Negotiation")
CLOSED_STAGES = ("Closed Won", "Closed Lost")
