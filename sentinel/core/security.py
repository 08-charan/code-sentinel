import ast
import re
from typing import List
from pydantic import BaseModel


class SecurityViolation(BaseModel):
    file_path: str
    line: int
    rule_id: str
    severity: str  # HIGH, MEDIUM, LOW
    message: str


class SecurityScanner(ast.NodeVisitor):
    """
    AST-based vulnerability scanner for Python source code.
    Identifies common antipatterns and security flaws without external network calls.
    """

    SUSPICIOUS_TOKEN_REGEX = re.compile(
        r"(?i)(api[_-]?key|secret|token|password|passwd|auth)[_-]?([a-z0-9_]*)\s*=\s*['\"][a-zA-Z0-9_\-\.]{16,}['\"]"
    )

    def __init__(self, file_path: str, raw_content: str):
        self.file_path = file_path
        self.raw_content = raw_content
        self.violations: List[SecurityViolation] = []

    def scan(self, tree: ast.AST) -> List[SecurityViolation]:
        self.violations.clear()
        self._check_secrets_in_text()
        self.visit(tree)
        return self.violations

    def _check_secrets_in_text(self):
        for idx, line in enumerate(self.raw_content.splitlines(), start=1):
            if self.SUSPICIOUS_TOKEN_REGEX.search(line):
                # Avoid flagging comment or test tokens
                if not line.strip().startswith("#"):
                    self.violations.append(
                        SecurityViolation(
                            file_path=self.file_path,
                            line=idx,
                            rule_id="SEC-001",
                            severity="HIGH",
                            message="Possible hardcoded secret or token detected in source code.",
                        )
                    )

    def visit_Call(self, node: ast.Call):
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        # Rule SEC-002: eval() or exec() usage
        if func_name in ("eval", "exec"):
            self.violations.append(
                SecurityViolation(
                    file_path=self.file_path,
                    line=node.lineno,
                    rule_id="SEC-002",
                    severity="HIGH",
                    message=f"Use of dangerous dynamic execution function '{func_name}' detected.",
                )
            )

        # Rule SEC-003: os.system()
        if func_name == "system" and isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "os":
                self.violations.append(
                    SecurityViolation(
                        file_path=self.file_path,
                        line=node.lineno,
                        rule_id="SEC-003",
                        severity="HIGH",
                        message="Use of 'os.system' is vulnerable to command injection; prefer 'subprocess.run(..., shell=False)'.",
                    )
                )

        # Rule SEC-004: subprocess with shell=True
        if func_name in ("call", "check_call", "check_output", "Popen", "run"):
            for kw in node.keywords:
                if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                    self.violations.append(
                        SecurityViolation(
                            file_path=self.file_path,
                            line=node.lineno,
                            rule_id="SEC-004",
                            severity="HIGH",
                            message="Subprocess invocation with 'shell=True' enables shell injection vulnerabilities.",
                        )
                    )

        # Rule SEC-005: Insecure deserialization with pickle
        if func_name in ("load", "loads") and isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id in ("pickle", "_pickle", "cPickle"):
                self.violations.append(
                    SecurityViolation(
                        file_path=self.file_path,
                        line=node.lineno,
                        rule_id="SEC-005",
                        severity="MEDIUM",
                        message="Pickle deserialization of untrusted payloads is insecure; use json or safetensors.",
                    )
                )

        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        # Rule SEC-006: Bare except or catching BaseException
        if node.type is None:
            self.violations.append(
                SecurityViolation(
                    file_path=self.file_path,
                    line=node.lineno,
                    rule_id="SEC-006",
                    severity="LOW",
                    message="Bare 'except:' suppresses system exits and keyboard interrupts; specify explicit exception types.",
                )
            )
        elif isinstance(node.type, ast.Name) and node.type.id in ("BaseException", "Exception"):
            # Check if body is just pass
            if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                self.violations.append(
                    SecurityViolation(
                        file_path=self.file_path,
                        line=node.lineno,
                        rule_id="SEC-007",
                        severity="MEDIUM",
                        message=f"Silent error suppression ('except {node.type.id}: pass') masks critical runtime failures.",
                    )
                )
        self.generic_visit(node)
