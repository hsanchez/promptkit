from pathlib import Path

from promptkit.manager import PromptManager


def test_init_and_release(tmp_path: Path) -> None:
  prompts_dir = tmp_path / "prompts"
  manager = PromptManager(prompts_dir)

  manager.init()
  version = manager.release()

  assert version == "v0.0.1"
  assert (prompts_dir / "current" / "system.yaml").exists()
  assert (prompts_dir / ".vault" / "v0.0.1" / "system.yaml").exists()
  assert (prompts_dir / "current" / "metadata.json").exists()


def test_diff_has_changes(tmp_path: Path) -> None:
  prompts_dir = tmp_path / "prompts"
  manager = PromptManager(prompts_dir)

  manager.init()
  manager.release()

  draft = prompts_dir / "drafts" / "system.yaml.j2"
  draft.write_text(
    "model: gpt-5.5\n"
    "temperature: 0.1\n"
    "system_prompt: |\n"
    "  You are a careful verifier.\n"
  )

  assert "careful verifier" in manager.diff()
