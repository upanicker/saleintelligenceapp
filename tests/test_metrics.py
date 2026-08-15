from pathlib import Path
import sys
import unittest

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data_loader import normalize_data
from src.metrics import executive_metrics, filtered_data


class MetricsTests(unittest.TestCase):
    def setUp(self):
        raw = pd.DataFrame({
            "Opportunity ID": ["1", "2", "3"], "Opportunity Name": ["Alpha", "Beta", "Gamma"],
            "Account": ["Acme", "Bravo", "Acme"], "Territory": ["North", "South", "North"],
            "Country": ["India", "India", "India"], "Sales Rep": ["A", "B", "A"],
            "Stage": ["Qualification", "Closed Won", "Closed Lost"], "Amount ($)": [100, 200, 50],
            "Probability %": [0.5, 1, 0], "Close Date": ["2026-04-01"] * 3,
            "Product": ["P"] * 3, "Industry": ["Tech"] * 3,
        })
        self.data = normalize_data(raw)

    def test_executive_metrics_uses_open_pipeline(self):
        stats = executive_metrics(self.data, revenue_target=200)
        self.assertEqual(stats["total_pipeline"], 100)
        self.assertEqual(stats["weighted_pipeline"], 50)
        self.assertEqual(stats["won_revenue"], 200)
        self.assertEqual(stats["win_rate"], 0.5)
        self.assertEqual(stats["pipeline_coverage"], 0.5)

    def test_filtering_searches_account(self):
        results = filtered_data(self.data, {"Region": ["North"]}, "acme")
        self.assertEqual(len(results), 2)


if __name__ == "__main__":
    unittest.main()
