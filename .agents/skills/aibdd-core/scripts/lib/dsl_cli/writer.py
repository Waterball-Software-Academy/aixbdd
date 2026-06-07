"""Route templates to dsl.yml files and append them as HARNESS skeleton blocks.

We bypass ruamel for output and emit YAML text directly. Rationale:

  - Existing entries (which may carry SEMANTIC comments from a previous round)
    are preserved verbatim, because append is just textual concatenation.
  - The HARNESS skeleton needs a specific multi-line `# candidate parameters`
    comment block above `param_bindings: {}`. Constructing this through
    ruamel's comment API is fragile (comment-key ownership rules) — string
    templating is easier to reason about and to verify byte-for-byte.

`route_template_to_file()` is a pure function — `Path(source).stem` is
normalized by stripping any format-suffix (`.api` / `.openapi` for OpenAPI;
`.mysql` / `.pg` / `.mssql` for SQL DDL dialects), then `.dsl.yml` is
appended. DBML stems carry no such suffix, so the regex is a no-op there.

`append_templates()` accepts a list of templates targeting the same file. The
caller (orchestrator) is responsible for batching templates that route to the
same file and calling append_templates once per file.
"""

from __future__ import annotations

import re
from pathlib import Path

from dsl_cli.models import DSLInstructionTemplate

_STEM_SUFFIX_RE = re.compile(r"\.(api|openapi|mysql|pg|mssql)$")


def route_template_to_file(template: DSLInstructionTemplate) -> Path:
    spec_file = template.source_spec_path
    normalized_stem = _STEM_SUFFIX_RE.sub("", spec_file.stem)
    return spec_file.parent / f"{normalized_stem}.dsl.yml"


def append_templates(file_path: Path, templates: list[DSLInstructionTemplate]) -> None:
    if not templates:
        return
    new_entries_text = "".join(_render_template(t) for t in templates)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if not file_path.is_file():
        file_path.write_text("dsl_steps:\n" + new_entries_text)
        return
    existing = file_path.read_text()
    stripped = existing.strip()
    if stripped in ("", "dsl_steps:", "dsl_steps: []"):
        file_path.write_text("dsl_steps:\n" + new_entries_text)
        return
    if not existing.endswith("\n"):
        existing += "\n"
    file_path.write_text(existing + new_entries_text)


_INDENT = "  "


def _render_template(t: DSLInstructionTemplate) -> str:
    lines: list[str] = []
    lines.append(f'{_INDENT}- format: "{t.format}"')
    lines.append(f"{_INDENT}  name: {t.name}")
    lines.append(f"{_INDENT}  handler: {t.handler}")
    lines.append(f"{_INDENT}  target_part_path: {t.target_part_path}")
    if t.candidate_bindings:
        lines.append(
            f"{_INDENT}  # 候選參數（請挑選後分別填入 param_bindings / datatable_bindings；"
            "填完整段註解一併刪除）："
        )
        for cb in t.candidate_bindings:
            lines.append(f"{_INDENT}  #   {cb.key}:")
            lines.append(f"{_INDENT}  #     target: {cb.target}")
    lines.append(_render_bindings("param_bindings", _param_bindings_dump(t.param_bindings)))
    lines.append(_render_bindings("datatable_bindings", _datatable_bindings_dump(t.datatable_bindings)))
    return "\n".join(lines) + "\n"


def _render_bindings(key: str, body: str) -> str:
    if body == "":
        return f"{_INDENT}  {key}: {{}}"
    return f"{_INDENT}  {key}:\n{body}"


def _param_bindings_dump(bindings) -> str:
    lines: list[str] = []
    for k, v in bindings.items():
        lines.append(f"{_INDENT}    {k}:")
        lines.append(f"{_INDENT}      target: {v.target}")
    return "\n".join(lines)


def _datatable_bindings_dump(bindings) -> str:
    lines: list[str] = []
    for k, v in bindings.items():
        lines.append(f"{_INDENT}    {k}:")
        lines.append(f"{_INDENT}      required: {'true' if v.required else 'false'}")
        lines.append(f"{_INDENT}      target: {v.target}")
        if v.default_value is not None:
            lines.append(f'{_INDENT}      default_value: "{v.default_value}"')
        elif not v.required:
            lines.append(f'{_INDENT}      default_value: ""')
    return "\n".join(lines)
