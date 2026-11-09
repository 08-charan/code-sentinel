import unittest
import ast
from sentinel.core.complexity import calculate_complexity


class TestComplexity(unittest.TestCase):
    def test_simple_function_complexity(self):
        code = """
def simple():
    return 42
"""
        tree = ast.parse(code)
        scores = calculate_complexity(tree)
        self.assertEqual(scores["simple"], 1)

    def test_branching_complexity(self):
        code = """
def process(a, b):
    if a > 0:
        return a
    elif b > 0 and a < -5:
        return b
    else:
        for x in range(10):
            print(x)
        return 0
"""
        tree = ast.parse(code)
        scores = calculate_complexity(tree)
        self.assertGreaterEqual(scores["process"], 4)


if __name__ == "__main__":
    unittest.main()
