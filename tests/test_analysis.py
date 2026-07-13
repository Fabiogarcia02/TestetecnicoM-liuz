import unittest
from datetime import date

from growth_ab_analyzer.analysis import analyze_observations
from growth_ab_analyzer.models import DataQualityReport, Observation


class AnalysisTest(unittest.TestCase):
    def test_decision_prefers_highest_daily_net_revenue(self) -> None:
        observations = [
            Observation(date(2026, 1, 1), "Grupo 1", "Parceiro X", 10, 100, 20, 1000),
            Observation(date(2026, 1, 2), "Grupo 1", "Parceiro X", 10, 100, 20, 1000),
            Observation(date(2026, 1, 1), "Grupo 2", "Parceiro X", 12, 110, 60, 1100),
            Observation(date(2026, 1, 2), "Grupo 2", "Parceiro X", 12, 110, 60, 1100),
        ]

        result = analyze_observations(
            observations,
            DataQualityReport(row_count=len(observations), warnings=()),
            "fixture.csv",
        )

        self.assertEqual(result.decision.winner, "Grupo 1")


if __name__ == "__main__":
    unittest.main()
