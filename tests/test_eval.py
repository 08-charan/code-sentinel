import unittest
from sentinel.ai.mock_eval import CodeEvaluationEngine, ModelResponsePair


class TestEvaluation(unittest.TestCase):
    def test_eval_prefers_valid_syntax_over_broken(self):
        pair = ModelResponsePair(
            prompt="Write a fibonacci function",
            response_a="def fib(n):\n    return n if n <= 1 else fib(n-1) + fib(n-2)",
            response_b="def fib(n)\n    return broken syntax!!",
        )
        score = CodeEvaluationEngine.evaluate_pair(pair)
        self.assertEqual(score.winner, "A")
        self.assertGreater(score.score_a, score.score_b)

    def test_eval_prefers_lower_cyclomatic_complexity(self):
        pair = ModelResponsePair(
            prompt="Check positive",
            response_a="def check(x):\n    return x > 0",
            response_b="def check(x):\n    if x > 0:\n        if x > 1:\n            if x > 2:\n                return True\n    return False",
        )
        score = CodeEvaluationEngine.evaluate_pair(pair)
        self.assertEqual(score.winner, "A")


if __name__ == "__main__":
    unittest.main()
