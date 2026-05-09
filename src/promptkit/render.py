"""Prompt rendering."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined, meta

from promptkit.config import PromptSpec
from promptkit.errors import PromptRenderError


def template_name_for(file_name: str) -> str:
  """Return the draft template name for a rendered prompt file."""
  return f"{file_name}.j2"


def undeclared_variables(template_source: str, drafts_dir: Path) -> set[str]:
  """Return Jinja undeclared variables."""
  env = Environment(loader=FileSystemLoader(str(drafts_dir)), undefined=StrictUndefined)
  ast = env.parse(template_source)
  return set(meta.find_undeclared_variables(ast))


def render_prompts(
  spec: PromptSpec, variables: dict[str, Any] | None = None
) -> dict[str, str]:
  """Render all prompt templates declared in promptspec.yaml."""
  variables = variables or {}
  env = Environment(
    loader=FileSystemLoader(str(spec.drafts_dir)), undefined=StrictUndefined
  )

  rendered: dict[str, str] = {}
  for file_name in spec.files:
    template_name = template_name_for(file_name)
    template_path = spec.drafts_dir / template_name
    if not template_path.exists():
      raise PromptRenderError(f"Missing draft template: {template_path}")

    try:
      rendered_content = env.get_template(template_name).render(**variables)
    except Exception as exc:
      raise PromptRenderError(f"Failed to render {template_name}: {exc}") from exc

    try:
      yaml.safe_load(rendered_content)
    except yaml.YAMLError as exc:
      raise PromptRenderError(
        f"Rendered YAML is invalid for {file_name}: {exc}"
      ) from exc

    rendered[file_name] = rendered_content

  return rendered
