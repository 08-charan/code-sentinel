from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from sentinel.core.analyzer import AnalysisResult, FileAnalysisReport
from sentinel.ai.mock_eval import EvaluationScore


class TerminalFormatter:
    """
    Renders clean, terminal-native reports using Rich.
    """

    def __init__(self, console: Console = None):
        self.console = console or Console()

    def print_summary(self, result: AnalysisResult):
        self.console.print("\n")
        self.console.rule("[bold cyan]CodeSentinel Static Analysis & Architecture Report[/bold cyan]")

        table = Table(title="Analysis Overview", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="dim", width=30)
        table.add_column("Value", style="bold")

        table.add_row("Total Files Analyzed", str(result.total_files_analyzed))
        table.add_row("Total Non-Comment LOC", str(result.total_loc))
        table.add_row("Average Cyclomatic Complexity", f"{result.average_complexity:.2f}")
        table.add_row(
            "Security Vulnerabilities",
            f"[red]{result.total_security_issues}[/red]" if result.total_security_issues > 0 else "[green]0 (Clean)[/green]",
        )
        table.add_row(
            "Trade-Off Optimization Opportunities",
            f"[yellow]{result.total_trade_off_suggestions}[/yellow]" if result.total_trade_off_suggestions > 0 else "[green]0[/green]",
        )

        self.console.print(table)

        # File details
        for file_report in result.file_reports:
            self._print_file_report(file_report)

    def _print_file_report(self, report: FileAnalysisReport):
        score_color = "green" if report.maintainability_score >= 80 else ("yellow" if report.maintainability_score >= 60 else "red")
        self.console.print(
            f"\n[bold underline]File:[/bold underline] {report.file_path} | "
            f"LOC: {report.loc} | "
            f"Maintainability: [{score_color}]{report.maintainability_score}/100[/{score_color}]"
        )

        if report.security_violations:
            sec_table = Table(title="Security & Bug Risks", show_header=True, header_style="bold red")
            sec_table.add_column("Line", width=8)
            sec_table.add_column("Rule", width=12)
            sec_table.add_column("Severity", width=10)
            sec_table.add_column("Description")
            for v in report.security_violations:
                sec_table.add_row(str(v.line), v.rule_id, f"[{'red' if v.severity == 'HIGH' else 'yellow'}]{v.severity}[/]", v.message)
            self.console.print(sec_table)

        if report.trade_offs:
            trade_table = Table(title="Engineering Trade-Offs & Complexity", show_header=True, header_style="bold yellow")
            trade_table.add_column("Line", width=8)
            trade_table.add_column("Category", width=22)
            trade_table.add_column("Trade-Off Analysis")
            trade_table.add_column("Recommendation")
            for t in report.trade_offs:
                trade_table.add_row(str(t.line), t.category, t.trade_off_analysis, f"[italic cyan]{t.recommendation}[/italic cyan]")
            self.console.print(trade_table)

    def print_eval_score(self, score: EvaluationScore):
        winner_text = Text(f"Preference Winner: Model {score.winner}", style="bold green" if score.winner != "TIE" else "bold yellow")
        panel = Panel(
            f"Model A Score: {score.score_a}\nModel B Score: {score.score_b}\n\nDetailed Justification:\n"
            + "\n".join(f"• {k.capitalize()}: {v}" for k, v in score.reasons.items()),
            title="AI Code Preference Evaluation Result",
            subtitle=winner_text,
            border_style="cyan",
        )
        self.console.print(panel)
