"""High-level PromptKit manager."""

from __future__ import annotations

import shutil
from pathlib import Path

import yaml

from promptkit.config import PromptSpec, default_spec, load_spec
from promptkit.diff import diff_current_against_drafts
from promptkit.lint import lint_prompts
from promptkit.release import create_release
from promptkit.render import template_name_for


class PromptManager:
  """Manage prompt drafts, current prompts, and immutable vault releases."""

  def __init__(self, prompts_dir: Path = Path("prompts")) -> None:
    self.prompts_dir = prompts_dir

  def init(self) -> None:
    """Initialize prompt directories and promptspec.yaml."""
    self.prompts_dir.mkdir(exist_ok=True)
    (self.prompts_dir / "drafts").mkdir(exist_ok=True)
    (self.prompts_dir / "current").mkdir(exist_ok=True)
    (self.prompts_dir / ".vault").mkdir(exist_ok=True)

    spec_path = self.prompts_dir / "promptspec.yaml"
    if not spec_path.exists():
      spec_path.write_text(
        yaml.safe_dump(default_spec(self.prompts_dir), sort_keys=False)
      )

    draft = self.prompts_dir / "drafts" / "system.yaml.j2"
    if not draft.exists():
      draft.write_text(
        "model: gpt-5.5\n"
        "temperature: 0.2\n"
        "system_prompt: |\n"
        "  You are a helpful assistant.\n"
      )

  def spec(self) -> PromptSpec:
    """Load prompt spec."""
    return load_spec(self.prompts_dir)

  def draft_from_current(self) -> None:
    """Create drafts from current prompts."""
    spec = self.spec()
    spec.drafts_dir.mkdir(parents=True, exist_ok=True)

    for file_name in spec.files:
      current_path = spec.current_dir / file_name
      draft_path = spec.drafts_dir / template_name_for(file_name)
      if current_path.exists():
        draft_path.write_text(current_path.read_text())
      elif not draft_path.exists():
        draft_path.write_text("")

  def check(self) -> list[str]:
    """Lint prompts."""
    return lint_prompts(self.spec())

  def release(self, bump: str = "patch") -> str:
    """Create a release."""
    return create_release(self.spec(), bump=bump)

  def diff(self) -> str:
    """Diff current prompts against rendered drafts."""
    return diff_current_against_drafts(self.spec())

  def rollback(self, version: str) -> None:
    """Set current prompts to a prior vault version."""
    spec = self.spec()
    source = spec.vault_dir / version
    if not source.exists():
      raise FileNotFoundError(f"Unknown release: {version}")

    if spec.current_dir.exists():
      shutil.rmtree(spec.current_dir)
    shutil.copytree(source, spec.current_dir)
