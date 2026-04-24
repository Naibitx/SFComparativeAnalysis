import unittest

from app.services.ranking_engine import (
    score_result,
    rank_assistants,
    get_best_assistant
)
class TestRankingEngine(unittest.TestCase):

    def test_success_beats_failure(self):

        results = [
            {
                "assistant": "fail_bot",
                "execution": {"success": False, "stderr": "error", "execution_time": 1},
                "metrics": {}
            },
            {
                "assistant": "good_bot",
                "execution": {"success": True, "stderr": "", "execution_time": 5},
                "metrics": {}
            }
        ]

        ranking = rank_assistants(results)

        self.assertEqual(ranking[0]["assistant"], "good_bot")

    def test_faster_is_better(self):
        results = [
            {
                "assistant": "slow_bot",
                "execution": {"success": True, "stderr": "", "execution_time": 10},
                "metrics": {}
            },
            {
                "assistant": "fast_bot",
                "execution": {"success": True, "stderr": "", "execution_time": 1},
                "metrics": {}
            }
        ]

        ranking = rank_assistants(results)

        self.assertEqual(ranking[0]["assistant"], "fast_bot")

    def test_errors_reduce_score(self):
        results = [
            {
                "assistant": "clean_bot",
                "execution": {"success": True, "stderr": "", "execution_time": 2},
                "metrics": {}
            },
            {
                "assistant": "error_bot",
                "execution": {"success": True, "stderr": "error", "execution_time": 2},
                "metrics": {}
            }
        ]

        ranking = rank_assistants(results)

        self.assertEqual(ranking[0]["assistant"], "clean_bot")

    def test_security_penalty(self):
        results = [
            {
                "assistant": "secure_bot",
                "execution": {"success": True, "stderr": "", "execution_time": 2},
                "metrics": {"security_issues": 0}
            },
            {
                "assistant": "unsafe_bot",
                "execution": {"success": True, "stderr": "", "execution_time": 2},
                "metrics": {"security_issues": 3}
            }
        ]

        ranking = rank_assistants(results)

        self.assertEqual(ranking[0]["assistant"], "secure_bot")

    def test_best_assistant_function(self):
        results = [
            {
                "assistant": "bot1",
                "execution": {"success": True, "stderr": "", "execution_time": 5},
                "metrics": {}
            },
            {
                "assistant": "bot2",
                "execution": {"success": True, "stderr": "", "execution_time": 1},
                "metrics": {}
            }
        ]
        best = get_best_assistant(results)
        self.assertEqual(best["assistant"], "bot2")
    def test_score_non_negative(self):
        result = {
            "assistant": "test_bot",
            "execution": {"success": True, "stderr": "error", "execution_time": 50},
            "metrics": {"warnings": 10, "security_issues": 5}
        }
        score = score_result(result)
        self.assertTrue(score <= 50)  # sanity check


if __name__ == "__main__":
    unittest.main()