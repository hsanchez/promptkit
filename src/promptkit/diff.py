"""Prompt diff helpers."""

from __future__ import annotations

from difflib import unified_diff
from pathlib import Path

from promptkit.config import PromptSpec
from promptkit.render import render_prompts


def diff_current_against_drafts(spec: PromptSpec) -> str:
  """Return a unified diff between current rendered prompts and drafts."""
  rendered = render_prompts(spec)
  chunks: list[str] = []

  for file_name, draft_content in rendered.items():
    current_path = spec.current_dir / file_name
    current_content = current_path.read_text() if current_path.exists() else ""

    chunks.extend(
      unified_diff(
        current_content.splitlines(keepends=True),
        draft_content.splitlines(keepends=True),
        fromfile=f"current/{file_name}",
        tofile=f"drafts/{file_name}",
      )
    )

  return "".join(chunks)
