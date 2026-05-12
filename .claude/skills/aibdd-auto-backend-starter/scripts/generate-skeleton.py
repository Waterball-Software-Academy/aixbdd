# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""Generate backend project skeleton from templates.

Usage:
    uv run generate-skeleton.py --project-dir <path> --project-name <name> --variant python-e2e
    uv run generate-skeleton.py --project-dir <path> --project-name <name> --variant java-e2e

Reads .aibdd/arguments.yml, resolves template variables, and writes
the full project skeleton in one shot.
"""

import argparse
import re
import sys
from pathlib import Path
from string import Template

import yaml


SUPPORTED_VARIANTS = ("python-e2e", "java-e2e")


def slugify(name: str) -> str:
    """Convert project name to URL-safe slug."""
    slug = name.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def resolve_args_variables(args_data: dict) -> dict:
    """Resolve ${VAR} references within arguments.yml values."""
    resolved = {}
    for key, value in args_data.items():
        if isinstance(value, str):
            # Iteratively resolve ${VAR} references
            prev = None
            current = value
            while current != prev:
                prev = current
                current = Template(current).safe_substitute(resolved)
            resolved[key] = current
        else:
            resolved[key] = value
    return resolved


def build_variables_python(args_data: dict, project_name: str) -> dict:
    """Build the variable dict for python-e2e template substitution."""
    resolved = resolve_args_variables(args_data)
    slug = slugify(project_name)
    py_app_dir = resolved.get("PY_APP_DIR", "app")
    py_app_module = py_app_dir.replace("/", ".")
    py_test_features_dir = resolved.get("PY_TEST_FEATURES_DIR", "tests/features")
    py_test_module = py_test_features_dir.replace("/", ".")

    variables = {
        **resolved,
        "PROJECT_NAME": project_name,
        "PROJECT_SLUG": slug,
        "PROJECT_DESCRIPTION": resolved.get(
            "PROJECT_DESCRIPTION", f"{project_name} — BDD Workshop Python E2E"
        ),
        "PY_APP_MODULE": py_app_module,
        "PY_TEST_MODULE": py_test_module,
        "DB_NAME": resolved.get("DB_NAME", slug.replace("-", "_") + "_dev"),
    }
    return variables


def build_variables_java(args_data: dict, project_name: str) -> dict:
    """Build the variable dict for java-e2e template substitution."""
    resolved = resolve_args_variables(args_data)
    slug = slugify(project_name)
    artifact_id = resolved.get("ARTIFACT_ID", slug)
    group_id = resolved.get("GROUP_ID", "com.example")
    base_package = resolved.get("BASE_PACKAGE", f"{group_id}.{artifact_id.replace('-', '')}")
    base_package_path = base_package.replace(".", "/")
    db_name = resolved.get("DB_NAME", artifact_id.replace("-", "_"))

    variables = {
        **resolved,
        "PROJECT_NAME": project_name,
        "PROJECT_SLUG": slug,
        "PROJECT_DESCRIPTION": resolved.get(
            "PROJECT_DESCRIPTION", f"{project_name} — BDD Workshop Java E2E"
        ),
        "GROUP_ID": group_id,
        "ARTIFACT_ID": artifact_id,
        "BASE_PACKAGE": base_package,
        "BASE_PACKAGE_PATH": base_package_path,
        "JAVA_VERSION": resolved.get("JAVA_VERSION", "25"),
        "SPRING_BOOT_VERSION": resolved.get("SPRING_BOOT_VERSION", "4.0.6"),
        "CUCUMBER_VERSION": resolved.get("CUCUMBER_VERSION", "7.34.3"),
        "JJWT_VERSION": resolved.get("JJWT_VERSION", "0.12.6"),
        "SPRINGDOC_VERSION": resolved.get("SPRINGDOC_VERSION", "3.0.3"),
        "POSTGRES_IMAGE_VERSION": resolved.get("POSTGRES_IMAGE_VERSION", "18"),
        "DB_NAME": db_name,
        "DB_USER": resolved.get("DB_USER", "postgres"),
        "DB_PASSWORD": resolved.get("DB_PASSWORD", "postgres"),
        "DB_PORT": resolved.get("DB_PORT", "5432"),
    }
    return variables


def build_variables(args_data: dict, project_name: str, variant: str) -> dict:
    """Dispatch variable construction by variant."""
    if variant == "python-e2e":
        return build_variables_python(args_data, project_name)
    if variant == "java-e2e":
        return build_variables_java(args_data, project_name)
    raise ValueError(f"Unsupported variant: {variant}")


def write_template(template_path: Path, output_path: Path, variables: dict) -> None:
    """Read template, substitute variables, write output."""
    content = template_path.read_text(encoding="utf-8")
    result = Template(content).safe_substitute(variables)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        print(f"  SKIP (exists): {output_path}")
        return
    output_path.write_text(result, encoding="utf-8")
    print(f"  {output_path.relative_to(output_path.parent.parent.parent) if len(output_path.parts) > 3 else output_path.name}")


def template_name_to_path_python(name: str) -> str:
    """Convert python-e2e template filename (__ = /) to output path."""
    # Protect Python's __init__ before replacing __ with /
    name = name.replace("__init__", "\x00INIT\x00")
    path = name.replace("__", "/")
    path = path.replace("\x00INIT\x00", "__init__")
    if path.endswith(".tmpl"):
        path = path[:-5]
    return path


def template_name_to_path_java(name: str, base_package_path: str) -> str:
    """Convert java-e2e template filename (__ = /, BASE_PKG → base_package_path) to output path."""
    path = name.replace("__", "/")
    path = path.replace("BASE_PKG", base_package_path)
    if path.endswith(".tmpl"):
        path = path[:-5]
    return path


def template_name_to_path(name: str, variant: str, variables: dict) -> str:
    """Dispatch filename-to-path conversion by variant."""
    if variant == "python-e2e":
        return template_name_to_path_python(name)
    if variant == "java-e2e":
        return template_name_to_path_java(name, variables["BASE_PACKAGE_PATH"])
    raise ValueError(f"Unsupported variant: {variant}")


def create_empty_dirs_python(project_dir: Path, variables: dict) -> None:
    """Create empty __init__.py files for python-e2e packages that don't have templates."""
    py_app_dir = variables.get("PY_APP_DIR", "app")
    dirs_needing_init = [
        f"{py_app_dir}/repositories",
        f"{py_app_dir}/services",
        f"{py_app_dir}/schemas",
    ]
    for d in dirs_needing_init:
        init_path = project_dir / d / "__init__.py"
        if not init_path.exists():
            init_path.parent.mkdir(parents=True, exist_ok=True)
            init_path.write_text("", encoding="utf-8")
            print(f"  {d}/__init__.py (empty)")


def create_empty_dirs_java(project_dir: Path, variables: dict) -> None:
    """Create empty directories for java-e2e (Java has no __init__.py equivalent)."""
    base_package_path = variables["BASE_PACKAGE_PATH"]
    empty_dirs = [
        f"src/main/java/{base_package_path}/model",
        f"src/main/java/{base_package_path}/repository",
        f"src/main/java/{base_package_path}/service",
        "src/main/resources/db/migration",
        "src/main/resources/static",
        "src/main/resources/templates",
    ]
    for d in empty_dirs:
        dir_path = project_dir / d
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  {d}/ (empty)")


def create_empty_dirs(project_dir: Path, variables: dict, variant: str) -> None:
    """Dispatch empty-dir creation by variant."""
    if variant == "python-e2e":
        create_empty_dirs_python(project_dir, variables)
    elif variant == "java-e2e":
        create_empty_dirs_java(project_dir, variables)


def post_process_python(project_dir: Path, variables: dict) -> None:
    """Python-specific post-processing: alembic versions dir."""
    versions_dir = project_dir / variables.get("ALEMBIC_VERSIONS_DIR", "alembic/versions")
    versions_dir.mkdir(parents=True, exist_ok=True)


def post_process(project_dir: Path, variables: dict, variant: str) -> None:
    """Dispatch post-processing by variant."""
    if variant == "python-e2e":
        post_process_python(project_dir, variables)
    # java-e2e: no extra post-processing beyond create_empty_dirs


def main():
    parser = argparse.ArgumentParser(description="Generate backend project skeleton")
    parser.add_argument("--project-dir", required=True, help="Backend project root directory")
    parser.add_argument("--project-name", required=True, help="Project display name")
    parser.add_argument(
        "--variant",
        default="python-e2e",
        choices=SUPPORTED_VARIANTS,
        help="Template variant",
    )
    parser.add_argument("--arguments", required=True, help="Path to arguments.yml")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    arguments_yml = Path(args.arguments).resolve()

    if not arguments_yml.exists():
        print(f"Error: {arguments_yml} not found. Run /aibdd-kickoff first.", file=sys.stderr)
        sys.exit(1)

    with open(arguments_yml) as f:
        args_data = yaml.safe_load(f) or {}

    args_rel = args_data.get("AIBDD_ARGUMENTS_PATH", ".aibdd/arguments.yml")
    if not isinstance(args_rel, str) or not args_rel.strip():
        print("Error: AIBDD_ARGUMENTS_PATH missing in arguments.yml.", file=sys.stderr)
        sys.exit(1)
    variables_for_path = resolve_args_variables(args_data)
    args_rel = variables_for_path.get("AIBDD_ARGUMENTS_PATH", args_rel)
    expected_args = (project_dir / args_rel).resolve()
    if arguments_yml != expected_args:
        print(
            "Error: backend starter only reads specs already in the project root. "
            f"Expected arguments.yml at {expected_args}, got {arguments_yml}.",
            file=sys.stderr,
        )
        sys.exit(1)

    variables = build_variables(args_data, args.project_name, args.variant)

    # Locate templates
    script_dir = Path(__file__).resolve().parent
    templates_dir = script_dir.parent / "templates" / args.variant

    if not templates_dir.exists():
        print(f"Error: templates directory not found at {templates_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Generating skeleton in: {project_dir}")
    print(f"  variant: {args.variant}")
    print(f"  project: {args.project_name} ({variables['PROJECT_SLUG']})")
    print()

    # Process each template file
    count = 0
    for template_path in sorted(templates_dir.iterdir()):
        if template_path.is_file():
            output_rel = template_name_to_path(template_path.name, args.variant, variables)
            output_path = project_dir / output_rel
            write_template(template_path, output_path, variables)
            count += 1

    # Create empty directories / placeholder __init__.py files
    create_empty_dirs(project_dir, variables, args.variant)

    # Variant-specific post-processing
    post_process(project_dir, variables, args.variant)

    print(f"\nSkeleton generated: {count} files written")


if __name__ == "__main__":
    main()
