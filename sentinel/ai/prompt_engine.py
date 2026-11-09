from typing import Dict, Any
from pydantic import BaseModel


class RefactorRecommendation(BaseModel):
    title: str
    rationale: str
    diff_suggestion: str
    trade_off_impact: str


class ReviewPromptBuilder:
    """
    Constructs high-fidelity system prompts and structured evaluation payloads
    for LLM code reviews, grounding the model in AST metrics and static analysis findings.
    """

    SYSTEM_INSTRUCTION = """You are an elite Senior Staff Software Engineer and Static Analysis Evaluator.
Your goal is to inspect code changes, assess architectural correctness, highlight performance trade-offs,
and identify subtle bugs, security vulnerabilities, or anti-patterns.
Always prioritize:
1. Correctness and edge case handling.
2. Time and space complexity trade-offs.
3. Idiomatic, maintainable structure over premature optimization.
"""

    @classmethod
    def build_review_payload(cls, file_path: str, source_code: str, analysis_metrics: Dict[str, Any]) -> str:
        prompt = f"""### Target File: {file_path}
### Static Analysis Context:
- Lines of Code: {analysis_metrics.get('loc', 'N/A')}
- Security Issues Flagged: {analysis_metrics.get('security_issues', 0)}
- Complexity Outliers: {analysis_metrics.get('complexity_outliers', 'None')}

### Code Snippet:
```python
{source_code}
```

### Review Objectives:
1. Verify functional correctness and state invariants.
2. Evaluate architectural trade-offs (e.g. latency, memory footprint, maintainability).
3. Provide a concrete, minimal refactoring diff if improvements exist.
"""
        return prompt
