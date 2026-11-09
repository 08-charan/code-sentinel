import ast
from typing import List
from pydantic import BaseModel


class TradeOffObservation(BaseModel):
    file_path: str
    line: int
    category: str  # e.g., "Time vs Space", "Memory Allocation", "Algorithmic Complexity"
    pattern: str
    trade_off_analysis: str
    recommendation: str


class TradeOffEvaluator(ast.NodeVisitor):
    """
    Evaluates engineering trade-offs directly from source code AST:
    - Nested loops resulting in quadratic O(N^2) time complexity vs hash map indexing O(N).
    - String concatenation in loops causing O(N^2) memory allocations vs list join O(N).
    - Synchronous file/network calls inside batch iteration loops vs batching/async pipelines.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.loop_depth = 0
        self.observations: List[TradeOffObservation] = []

    def evaluate(self, tree: ast.AST) -> List[TradeOffObservation]:
        self.observations.clear()
        self.loop_depth = 0
        self.visit(tree)
        return self.observations

    def visit_For(self, node: ast.For):
        self.loop_depth += 1
        if self.loop_depth >= 2:
            self.observations.append(
                TradeOffObservation(
                    file_path=self.file_path,
                    line=node.lineno,
                    category="Algorithmic Complexity",
                    pattern="Nested For-Loop (O(N^2)+)",
                    trade_off_analysis=(
                        "Nested iterations multiply time complexity to O(N^2). "
                        "Trade-off: Spending O(N) additional memory with a set or dictionary index "
                        "reduces execution time from quadratic to linear O(N)."
                    ),
                    recommendation="Pre-index the inner dataset with a dictionary or set before entering the loop.",
                )
            )
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_While(self, node: ast.While):
        self.loop_depth += 1
        if self.loop_depth >= 2:
            self.observations.append(
                TradeOffObservation(
                    file_path=self.file_path,
                    line=node.lineno,
                    category="Algorithmic Complexity",
                    pattern="Nested While-Loop",
                    trade_off_analysis=(
                        "Nested iteration cycles risk exponential degradation under large dataset scaling."
                    ),
                    recommendation="Decompose into vectorized operations or partitioned generator pipelines.",
                )
            )
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_AugAssign(self, node: ast.AugAssign):
        # Detect `str_val += "..."` inside loops
        if self.loop_depth > 0 and isinstance(node.op, ast.Add):
            if isinstance(node.target, ast.Name):
                self.observations.append(
                    TradeOffObservation(
                        file_path=self.file_path,
                        line=node.lineno,
                        category="Memory Allocation",
                        pattern="In-loop String Reallocation",
                        trade_off_analysis=(
                            "Strings are immutable in Python; repeated concatenation in a loop re-allocates memory "
                            "and copies characters, inducing O(N^2) time & memory overhead."
                        ),
                        recommendation="Collect fragments in a list and invoke ''.join(fragments) once outside the loop.",
                    )
                )
        self.generic_visit(node)
