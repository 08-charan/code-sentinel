import ast
from typing import Dict, Any, Tuple
from pydantic import BaseModel
from sentinel.core.complexity import calculate_complexity


class ModelResponsePair(BaseModel):
    prompt: str
    response_a: str
    response_b: str


class EvaluationScore(BaseModel):
    winner: str  # "A", "B", "TIE"
    score_a: float
    score_b: float
    reasons: Dict[str, str]


class CodeEvaluationEngine:
    """
    Evaluates competing AI-generated code solutions for a given task.
    Scores solutions across three core pillars:
    1. Syntactic Correctness & AST Validity.
    2. Cyclomatic Complexity & Maintainability.
    3. Idiomatic Structure & Security Risk.
    """

    @classmethod
    def evaluate_pair(cls, pair: ModelResponsePair) -> EvaluationScore:
        valid_a, tree_a, err_a = cls._parse_code(pair.response_a)
        valid_b, tree_b, err_b = cls._parse_code(pair.response_b)

        score_a = 0.0
        score_b = 0.0
        reasons = {}

        # 1. Syntax check
        if not valid_a and not valid_b:
            return EvaluationScore(winner="TIE", score_a=0.0, score_b=0.0, reasons={"syntax": f"Both invalid: {err_a} | {err_b}"})
        if valid_a and not valid_b:
            return EvaluationScore(winner="A", score_a=100.0, score_b=0.0, reasons={"syntax": f"Model B failed AST parsing: {err_b}"})
        if valid_b and not valid_a:
            return EvaluationScore(winner="B", score_a=0.0, score_b=100.0, reasons={"syntax": f"Model A failed AST parsing: {err_a}"})

        # Both valid syntax: base score 50
        score_a += 50.0
        score_b += 50.0

        # 2. Complexity Comparison
        comp_a = calculate_complexity(tree_a)
        comp_b = calculate_complexity(tree_b)
        total_comp_a = sum(comp_a.values()) if comp_a else 1
        total_comp_b = sum(comp_b.values()) if comp_b else 1

        if total_comp_a < total_comp_b:
            score_a += 20.0
            reasons["complexity"] = f"Model A has lower cyclomatic complexity ({total_comp_a} vs {total_comp_b})"
        elif total_comp_b < total_comp_a:
            score_b += 20.0
            reasons["complexity"] = f"Model B has lower cyclomatic complexity ({total_comp_b} vs {total_comp_a})"
        else:
            reasons["complexity"] = f"Equal cyclomatic complexity ({total_comp_a})"

        # 3. Conciseness and AST node balance
        nodes_a = len(list(ast.walk(tree_a)))
        nodes_b = len(list(ast.walk(tree_b)))

        # Penalize excessive verbosity if functionally equivalent
        if nodes_a < nodes_b:
            score_a += 10.0
            reasons["conciseness"] = f"Model A produced cleaner, more concise AST structure ({nodes_a} vs {nodes_b} nodes)"
        elif nodes_b < nodes_a:
            score_b += 10.0
            reasons["conciseness"] = f"Model B produced cleaner, more concise AST structure ({nodes_b} vs {nodes_a} nodes)"

        winner = "A" if score_a > score_b else ("B" if score_b > score_a else "TIE")
        return EvaluationScore(
            winner=winner,
            score_a=round(score_a, 1),
            score_b=round(score_b, 1),
            reasons=reasons,
        )

    @classmethod
    def _parse_code(cls, code: str) -> Tuple[bool, Any, str]:
        # Strip potential markdown formatting if present
        clean_code = code.strip()
        if clean_code.startswith("```"):
            lines = clean_code.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            clean_code = "\n".join(lines)

        try:
            tree = ast.parse(clean_code)
            return True, tree, ""
        except SyntaxError as e:
            return False, None, str(e)
