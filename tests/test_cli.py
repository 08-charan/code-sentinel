from click.testing import CliRunner
from sentinel.cli import cli


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "code-sentinel" in result.output


def test_cli_analyze_current():
    runner = CliRunner()
    result = runner.invoke(cli, ["analyze", "sentinel/core/complexity.py"])
    assert result.exit_code == 0
    assert "Analysis Overview" in result.output
