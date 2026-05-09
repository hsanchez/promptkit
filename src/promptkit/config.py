"""PromptKit configuration loading."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from promptkit.errors import PromptSpecError


@dataclass(frozen=True)
class PromptSpec:
  """Configuration for a prompt repository."""

  prompts_dir: Path
  files: list[str]
  required_variables: list[str]
  max_file_bytes: int

  @property
  def drafts_dir(self) -> Path:
    return self.prompts_dir / "drafts"

  @property
  def current_dir(self) -> Path:
    return self.prompts_dir / "current"

  @property
  def vault_dir(self) -> Path:
    return self.prompts_dir / ".vault"

  @property
  def spec_path(self) -> Path:
    return self.prompts_dir / "promptspec.yaml"


def default_spec(prompts_dir: Path) -> dict[str, Any]:
  """Return a default promptspec document."""
  return {
    "files": ["system.yaml"],
    "required_variables": [],
    "max_file_bytes": 100_000,
  }


def load_spec(prompts_dir: Path) -> PromptSpec:
  """Load promptspec.yaml."""
  spec_path = prompts_dir / "promptspec.yaml"
  if not spec_path.exists():
    raise PromptSpecError(f"Missing promptspec: {spec_path}")

  raw = yaml.safe_load(spec_path.read_text()) or {}
  files = raw.get("files")
  if not isinstance(files, list) or not all(isinstance(item, str) for item in files):
    raise PromptSpecError("promptspec.yaml must contain files: list[str]")

  required_variables = raw.get("required_variables", [])
  if not isinstance(required_variables, list) or not all(
    isinstance(item, str) for item in required_variables
  ):
    raise PromptSpecError("promptspec.yaml required_variables must be list[str]")

  max_file_bytes = raw.get("max_file_bytes", 100_000)
  if not isinstance(max_file_bytes, int) or max_file_bytes <= 0:
    raise PromptSpecError("promptspec.yaml max_file_bytes must be a positive int")

  return PromptSpec(
    prompts_dir=prompts_dir,
    files=files,
    required_variables=required_variables,
    max_file_bytes=max_file_bytes,
  )
