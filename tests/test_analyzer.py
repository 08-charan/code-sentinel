import unittest
from sentinel.core.analyzer import SourceAnalyzer


class TestAnalyzer(unittest.TestCase):
    def test_analyzer_handles_clean_file(self):
        code = """
def add(a: int, b: int) -> int:
    \"\"\"Add two numbers.\"\"\"
    return a + b
"""
        analyzer = SourceAnalyzer()
        report = analyzer.analyze_source_code(code, "math_utils.py")

        self.assertIsNotNone(report)
        self.assertGreaterEqual(report.maintainability_score, 90.0)
        self.assertEqual(len(report.security_violations), 0)
        self.assertEqual(len(report.trade_offs), 0)

    def test_analyzer_detects_nested_loop_trade_off(self):
        code = """
def find_pairs(nums):
    result = []
    for i in nums:
        for j in nums:
            if i + j == 10:
                result.append((i, j))
    return result
"""
        analyzer = SourceAnalyzer()
        report = analyzer.analyze_source_code(code, "pairs.py")

        self.assertIsNotNone(report)
        self.assertTrue(any(t.pattern == "Nested For-Loop (O(N^2)+)" for t in report.trade_offs))


if __name__ == "__main__":
    unittest.main()
