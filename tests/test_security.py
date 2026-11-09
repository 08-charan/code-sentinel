import unittest
import ast
from sentinel.core.security import SecurityScanner


class TestSecurity(unittest.TestCase):
    def test_detects_dangerous_eval(self):
        code = """
def execute_payload(raw):
    return eval(raw)
"""
        tree = ast.parse(code)
        scanner = SecurityScanner(file_path="test_eval.py", raw_content=code)
        violations = scanner.scan(tree)
        self.assertTrue(any(v.rule_id == "SEC-002" for v in violations))

    def test_detects_shell_true_injection(self):
        code = """
import subprocess
def run_command(cmd):
    subprocess.run(cmd, shell=True)
"""
        tree = ast.parse(code)
        scanner = SecurityScanner(file_path="test_shell.py", raw_content=code)
        violations = scanner.scan(tree)
        self.assertTrue(any(v.rule_id == "SEC-004" for v in violations))

    def test_detects_silent_error_suppression(self):
        code = """
def risky():
    try:
        do_something()
    except Exception:
        pass
"""
        tree = ast.parse(code)
        scanner = SecurityScanner(file_path="test_suppress.py", raw_content=code)
        violations = scanner.scan(tree)
        self.assertTrue(any(v.rule_id == "SEC-007" for v in violations))


if __name__ == "__main__":
    unittest.main()
