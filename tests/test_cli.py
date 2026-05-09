from pathlib import Path

from typer.testing import CliRunner

from promptkit.cli import app
from promptkit.manager import PromptManager


def test_versions_command_lists_available_versions(tmp_path: Path) -> None:
  prompts_dir = tmp_path / "prompts"
  manager = PromptManager(prompts_dir)
  manager.init()
  manager.release()
  manager.release()
  runner = CliRunner()

  result = runner.invoke(app, ["versions", "--prompts-dir", str(prompts_dir)])

  assert result.exit_code == 0
  assert result.output.splitlines() == ["v0.0.1", "v0.0.2"]


def test_versions_command_outputs_nothing_without_releases(tmp_path: Path) -> None:
  prompts_dir = tmp_path / "prompts"
  PromptManager(prompts_dir).init()
  runner = CliRunner()

  result = runner.invoke(app, ["versions", "--prompts-dir", str(prompts_dir)])

  assert result.exit_code == 0
  assert result.output == ""
