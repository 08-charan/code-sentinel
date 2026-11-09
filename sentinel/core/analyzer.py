import ast
import os
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel

from .complexity import calculate_complexity
from .security import SecurityScanner, SecurityViolation
from .trade_offs import TradeOffEvaluator, TradeOffObservation


class FunctionMetrics(BaseModel):
    name: str
    cyclomatic_complexity: int
    status: str  # "LOW", "MODERATE", "HIGH", "CRITICAL"


class FileAnalysisReport(BaseModel):
    file_path: str
    loc: int
    functions: List[FunctionMetrics]
    security_violations: List[SecurityViolation]
    trade_offs: List[TradeOffObservation]
    maintainability_score: float  # Scale 0 - 100


class AnalysisResult(BaseModel):
    total_files_analyzed: int
    total_loc: int
    average_complexity: float
    total_security_issues: int
    total_trade_off_suggestions: int
    file_reports: List[FileAnalysisReport]


class SourceAnalyzer:
    """
    Coordinates static AST analysis across files and directories.
    Computes Maintainability Index based on LOC, cyclomatic complexity, and issue counts.
    """

    def __init__(self):
        pass

    def analyze_source_code(self, source_code: str, file_path: str = "inline_snippet.py") -> Optional[FileAnalysisReport]:
        try:
            tree = ast.parse(source_code, filename=file_path)
        except SyntaxError as e:
            # Report syntax failure
            return FileAnalysisReport(
                file_path=file_path,
                loc=len(source_code.splitlines()),
                functions=[],
                security_violations=[
                    SecurityViolation(
                        file_path=file_path,
                        line=e.lineno or 1,
                        rule_id="SYN-001",
                        severity="HIGH",
                        message=f"Syntax Error: {e.msg}",
                    )
                ],
                trade_offs=[],
                maintainability_score=0.0,
            )

        loc = len([line for line in source_code.splitlines() if line.strip() and not line.strip().startswith("#")])
        complexity_dict = calculate_complexity(tree)

        func_metrics: List[FunctionMetrics] = []
        total_comp = 0
        for func_name, comp in complexity_dict.items():
            total_comp += comp
            if comp <= 5:
                status = "LOW"
            elif comp <= 10:
                status = "MODERATE"
            elif comp <= 15:
                status = "HIGH"
            else:
                status = "CRITICAL"
            func_metrics.append(FunctionMetrics(name=func_name, cyclomatic_complexity=comp, status=status))

        sec_scanner = SecurityScanner(file_path=file_path, raw_content=source_code)
        security_violations = sec_scanner.scan(tree)

        trade_off_eval = TradeOffEvaluator(file_path=file_path)
        trade_offs = trade_off_eval.evaluate(tree)

        # Maintainability index heuristic (normalized 0 to 100)
        penalty = (len(security_violations) * 15.0) + (len(trade_offs) * 5.0)
        avg_func_comp = (total_comp / len(func_metrics)) if func_metrics else 1.0
        comp_penalty = max(0.0, (avg_func_comp - 5.0) * 4.0)
        raw_score = 100.0 - penalty - comp_penalty
        maintainability_score = max(0.0, min(100.0, round(raw_score, 1)))

        return FileAnalysisReport(
            file_path=file_path,
            loc=loc,
            functions=func_metrics,
            security_violations=security_violations,
            trade_offs=trade_offs,
            maintainability_score=maintainability_score,
        )

    def analyze_path(self, target_path: str) -> AnalysisResult:
        p = Path(target_path)
        file_reports: List[FileAnalysisReport] = []

        if p.is_file() and p.suffix == ".py":
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                report = self.analyze_source_code(f.read(), str(p))
                if report:
                    file_reports.append(report)
        elif p.is_dir():
            for root, _, files in os.walk(p):
                # Ignore hidden dirs or virtualenvs
                if any(ignored in root for ignored in [".git", "__pycache__", "venv", ".venv", "env"]):
                    continue
                for file in files:
                    if file.endswith(".py"):
                        full_path = os.path.join(root, file)
                        try:
                            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                                report = self.analyze_source_code(f.read(), full_path)
                                if report:
                                    file_reports.append(report)
                        except Exception:
                            continue

        total_files = len(file_reports)
        total_loc = sum(r.loc for r in file_reports)
        all_comps = [f.cyclomatic_complexity for r in file_reports for f in r.functions]
        avg_complexity = round(sum(all_comps) / len(all_comps), 2) if all_comps else 1.0
        total_sec = sum(len(r.security_violations) for r in file_reports)
        total_trade = sum(len(r.trade_offs) for r in file_reports)

        return AnalysisResult(
            total_files_analyzed=total_files,
            total_loc=total_loc,
            average_complexity=avg_complexity,
            total_security_issues=total_sec,
            total_trade_off_suggestions=total_trade,
            file_reports=file_reports,
        )
