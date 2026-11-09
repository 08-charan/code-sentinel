import sys
import click
from rich.console import Console
from sentinel import __version__
from sentinel.core.analyzer import SourceAnalyzer
from sentinel.git.vcs import GitInspector
from sentinel.ai.mock_eval import CodeEvaluationEngine, ModelResponsePair
from sentinel.reports.formatter import TerminalFormatter

console = Console()
formatter = TerminalFormatter(console)


@click.group()
@click.version_option(version=__version__, prog_name="code-sentinel")
def cli():
    """
    CodeSentinel: Terminal-Native AST Code Quality Analyzer,
    Git Inspector, and AI Preference Evaluation Engine.
    """
    pass


@cli.command("analyze")
@click.argument("path", default=".", type=click.Path(exists=True))
@click.option("--min-score", default=0, type=int, help="Fail with non-zero exit code if maintainability is below threshold.")
def analyze_cmd(path: str, min_score: int):
    """
    Analyze Python files or directories for AST complexity, security flaws, and trade-offs.
    """
    analyzer = SourceAnalyzer()
    with console.status("[bold green]Analyzing AST and complexity...[/bold green]"):
        result = analyzer.analyze_path(path)

    formatter.print_summary(result)

    # Check threshold exit code
    if min_score > 0 and result.file_reports:
        lowest_score = min(r.maintainability_score for r in result.file_reports)
        if lowest_score < min_score:
            console.print(f"\n[bold red]CI Failure:[/bold red] File maintainability {lowest_score} fell below minimum required {min_score}")
            sys.exit(1)


@cli.command("diff")
@click.option("--staged", is_flag=True, help="Analyze only staged Git changes.")
def diff_cmd(staged: bool):
    """
    Inspect local Git working tree diffs and run static analysis on modified files.
    """
    inspector = GitInspector()
    if not inspector.is_git_repo():
        console.print("[bold red]Error:[/bold red] Current directory is not a Git repository.")
        sys.exit(1)

    branch = inspector.get_current_branch()
    console.print(f"[cyan]Current Branch:[/cyan] [bold]{branch}[/bold]")

    files = inspector.get_staged_files() if staged else []
    if staged and not files:
        console.print("[yellow]No staged Python files found to analyze.[/yellow]")
        return

    analyzer = SourceAnalyzer()
    target_files = files if staged else ["."]
    result = analyzer.analyze_path(target_files[0])
    formatter.print_summary(result)


@cli.command("eval-pref")
@click.option("--file-a", required=True, type=click.Path(exists=True), help="Path to Model A output code.")
@click.option("--file-b", required=True, type=click.Path(exists=True), help="Path to Model B output code.")
@click.option("--prompt", default="Implement optimized solution", help="Task prompt context.")
def eval_pref_cmd(file_a: str, file_b: str, prompt: str):
    """
    Evaluate two competing AI model solutions and score preferences with engineering justifications.
    """
    with open(file_a, "r", encoding="utf-8") as fa:
        code_a = fa.read()
    with open(file_b, "r", encoding="utf-8") as fb:
        code_b = fb.read()

    pair = ModelResponsePair(prompt=prompt, response_a=code_a, response_b=code_b)
    score = CodeEvaluationEngine.evaluate_pair(pair)
    formatter.print_eval_score(score)


def main():
    cli()


if __name__ == "__main__":
    main()
