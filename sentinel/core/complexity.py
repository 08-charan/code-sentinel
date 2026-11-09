import ast
from typing import Dict, List, Tuple


class ComplexityVisitor(ast.NodeVisitor):
    """
    Computes McCabe Cyclomatic Complexity per function/method using AST traversal.
    Complexity starts at 1, incrementing for each decision/branching construct.
    """

    def __init__(self):
        self.scores: Dict[str, int] = {}
        self.current_function: List[str] = []

    def _increment(self, amount: int = 1):
        if self.current_function:
            name = self.current_function[-1]
            self.scores[name] = self.scores.get(name, 1) + amount

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.current_function.append(node.name)
        if node.name not in self.scores:
            self.scores[node.name] = 1
        self.generic_visit(node)
        self.current_function.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.current_function.append(node.name)
        if node.name not in self.scores:
            self.scores[node.name] = 1
        self.generic_visit(node)
        self.current_function.pop()

    def visit_If(self, node: ast.If):
        self._increment(1)
        self.generic_visit(node)

    def visit_For(self, node: ast.For):
        self._increment(1)
        self.generic_visit(node)

    def visit_AsyncFor(self, node: ast.AsyncFor):
        self._increment(1)
        self.generic_visit(node)

    def visit_While(self, node: ast.While):
        self._increment(1)
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        self._increment(1)
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp):
        # Multiple boolean operands (e.g. a and b and c -> 2 extra decision branches)
        self._increment(len(node.values) - 1)
        self.generic_visit(node)

    def visit_Assert(self, node: ast.Assert):
        self._increment(1)
        self.generic_visit(node)

    def visit_ListComp(self, node: ast.ListComp):
        self._increment(len(node.generators))
        self.generic_visit(node)

    def visit_SetComp(self, node: ast.SetComp):
        self._increment(len(node.generators))
        self.generic_visit(node)

    def visit_DictComp(self, node: ast.DictComp):
        self._increment(len(node.generators))
        self.generic_visit(node)

    def visit_GeneratorExp(self, node: ast.GeneratorExp):
        self._increment(len(node.generators))
        self.generic_visit(node)


def calculate_complexity(tree: ast.AST) -> Dict[str, int]:
    """
    Parses an AST tree and returns a mapping of function name to Cyclomatic Complexity score.
    """
    visitor = ComplexityVisitor()
    visitor.visit(tree)
    return visitor.scores
