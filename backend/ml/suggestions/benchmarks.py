# backend/ml/suggestions/benchmarks.py

# Based on the 50/30/20 budgeting framework — these are the
# "max healthy %" benchmarks per category, not arbitrary numbers.
CATEGORY_BENCHMARKS = {
    "Food": 25,
    "Shopping": 25,
    "Transport": 15,
    "Utilities": 10,
    "Subscription": 8,
    "Health": 10,
    "Entertainment": 10,
}

# Categories not in the map above (e.g. "Uncategorized", "Other")
DEFAULT_BENCHMARK = 15

# % reduction used for savings calculator
SAVINGS_REDUCTION_PCT = 20

# Flag if top-3 categories exceed this % of total spend
CONCENTRATION_THRESHOLD = 60

# Max number of anomaly-based suggestions to surface
ANOMALY_FOLLOWUP_LIMIT = 3

# Flag forecast if predicted spend exceeds last month by this %
FORECAST_INCREASE_THRESHOLD = 10