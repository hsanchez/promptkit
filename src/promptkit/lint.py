"""Prompt linting."""

from __future__ import annotations

from pathlib import Path

import yaml

from promptkit.config import PromptSpec
from promptkit.render import template_name_for, undeclared_variables


def lint_prompts(spec: PromptSpec) -> list[str]:
  """Return a list of lint errors. Empty list means success."""
  errors: list[str] = []

  for file_name in spec.files:
    template_path = spec.drafts_dir / template_name_for(file_name)
    if not template_path.exists():
      errors.append(f"Missing draft template: {template_path}")
      continue

    if template_path.stat().st_size > spec.max_file_bytes:
      errors.append(f"Draft exceeds max_file_bytes: {template_path}")

    source = template_path.read_text()
    found_variables = undeclared_variables(source, spec.drafts_dir)
    missing_required = set(spec.required_variables) - found_variables
    if missing_required:
      errors.append(
        f"{template_path} does not reference required variables: "
        f"{sorted(missing_required)}"
      )

    try:
      rendered_without_vars = source
      yaml.safe_load(rendered_without_vars)
    except yaml.YAMLError:
      # Drafts may contain Jinja and therefore may not parse as YAML pre-render.
      pass

  return errors
