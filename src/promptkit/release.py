"""Prompt release creation."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from promptkit.config import PromptSpec
from promptkit.errors import PromptReleaseError
from promptkit.metadata import write_metadata
from promptkit.render import render_prompts

VERSION_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")


def parse_version(version: str) -> tuple[int, int, int]:
  """Parse semantic version."""
  match = VERSION_RE.match(version)
  if match is None:
    raise PromptReleaseError(f"Invalid version: {version}")
  return tuple(int(part) for part in match.groups())


def format_version(version: tuple[int, int, int]) -> str:
  """Format semantic version with v prefix."""
  return f"v{version[0]}.{version[1]}.{version[2]}"


def latest_version(spec: PromptSpec) -> str | None:
  """Return latest vault version, if any."""
  if not spec.vault_dir.exists():
    return None
  versions = []
  for child in spec.vault_dir.iterdir():
    if child.is_dir() and VERSION_RE.match(child.name):
      versions.append(child.name)
  if not versions:
    return None
  return sorted(versions, key=parse_version)[-1]


def bump_version(current: str | None, bump: str) -> str:
  """Bump a semantic version."""
  major, minor, patch = parse_version(current or "v0.0.0")
  if bump == "major":
    return format_version((major + 1, 0, 0))
  if bump == "minor":
    return format_version((major, minor + 1, 0))
  if bump == "patch":
    return format_version((major, minor, patch + 1))
  raise PromptReleaseError(f"Unknown bump type: {bump}")


def create_release(spec: PromptSpec, bump: str = "patch") -> str:
  """Render drafts, create a vault release, and update current."""
  version = bump_version(latest_version(spec), bump)
  release_dir = spec.vault_dir / version

  if release_dir.exists():
    raise PromptReleaseError(f"Release already exists: {release_dir}")

  rendered = render_prompts(spec)

  release_dir.mkdir(parents=True)
  try:
    for file_name, content in rendered.items():
      (release_dir / file_name).write_text(content)
    write_metadata(release_dir, version, spec.files)

    if spec.current_dir.exists():
      shutil.rmtree(spec.current_dir)
    spec.current_dir.mkdir(parents=True)

    for file_name in spec.files:
      shutil.copy2(release_dir / file_name, spec.current_dir / file_name)
    shutil.copy2(release_dir / "metadata.json", spec.current_dir / "metadata.json")

  except Exception:
    if release_dir.exists():
      shutil.rmtree(release_dir)
    raise

  return version
