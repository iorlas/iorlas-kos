"""CLI entry point for the Knowledge Engine (ke)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def get_kb_dir() -> Path:
    """Walk up from CWD looking for a _meta/ directory to find KB root."""
    current = Path.cwd().resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "_meta").is_dir():
            return candidate
    raise SystemExit("Could not find KB root (_meta/ directory not found in any parent directory)")


def _is_folder_per_entity(schema) -> bool:
    """Return True if this schema uses the folder-per-entity pattern (README.md)."""
    return "README.md" in schema.file_pattern


def cmd_validate(args: argparse.Namespace) -> int:
    from skills.core.engine.schema import load_schemas, build_pydantic_model, resolve_schema_for_path
    from skills.core.engine.validate import validate_file, Finding

    kb_dir = get_kb_dir()
    skills_dir = kb_dir / "skills"

    if not skills_dir.exists():
        print("ERROR: skills/ directory not found — cannot load schemas", file=sys.stderr)
        return 1

    schemas = load_schemas(skills_dir)
    models = {name: build_pydantic_model(schema) for name, schema in schemas.items()}

    findings: list[Finding] = []

    if args.all:
        for schema_name, schema in schemas.items():
            if not schema.folder:
                continue

            folder = kb_dir / schema.folder

            # Skip Calls directory entirely
            if schema.folder == "Calls":
                continue

            if not folder.exists():
                continue

            if _is_folder_per_entity(schema):
                # e.g. Projects/050-knowledge-os/README.md
                files = sorted(folder.glob("*/README.md"))
            else:
                # e.g. Inbox/I0001-something.md, skip INDEX.md
                files = [
                    f for f in sorted(folder.glob("*.md"))
                    if f.name != "INDEX.md"
                ]

            model = models[schema_name]
            for fpath in files:
                findings.extend(validate_file(fpath, schema, model))

    else:
        # Single file validation
        target = Path(args.path).resolve()
        schema = resolve_schema_for_path(target, schemas)
        if schema is None:
            print(f"ERROR: no schema found for path: {args.path}", file=sys.stderr)
            return 1
        model = models[schema.name]
        findings.extend(validate_file(target, schema, model))

    if not findings:
        print("No issues found.")
        return 0

    # Apply output limit
    limit = args.limit
    shown = findings if limit == 0 else findings[:limit]

    for f in shown:
        print(str(f))

    if limit != 0 and len(findings) > limit:
        remaining = len(findings) - limit
        print(f"\n... and {remaining} more. Use --limit 0 to show all.")

    errors = sum(1 for f in findings if f.level == "ERROR")
    warnings = sum(1 for f in findings if f.level == "WARN")
    print(f"\n{errors} error(s), {warnings} warning(s)")

    return 1 if errors > 0 else 0


def cmd_transition(args):
    """Transition entity status."""
    from skills.core.engine.transition import transition_file

    kb_dir = get_kb_dir()
    skills_dir = kb_dir / "skills"
    path = Path(args.path)
    if not path.is_absolute():
        path = (kb_dir / path).resolve()

    try:
        msg = transition_file(path, args.status, kb_dir, skills_dir)
        print(msg)
    except ValueError as e:
        print(f"ERROR {e}", file=sys.stderr)
        sys.exit(1)


def cmd_create(args):
    """Create a new entity."""
    from skills.core.engine.create import create_entity

    kb_dir = get_kb_dir()
    skills_dir = kb_dir / "skills"

    try:
        path = create_entity(args.type, args.name, kb_dir, skills_dir)
        rel = path.relative_to(kb_dir)
        print(f"Created {rel}")
    except (ValueError, FileNotFoundError) as e:
        print(f"ERROR {e}", file=sys.stderr)
        sys.exit(1)


def cmd_check_links(args):
    """Check for broken wikilinks."""
    from skills.core.engine.links import check_links

    kb_dir = get_kb_dir()
    findings = check_links(kb_dir)

    for f in findings:
        print(str(f))

    phantoms = len(findings)
    if phantoms == 0:
        print("No phantom links found.")
    else:
        print(f"\n{phantoms} phantom link(s) found")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="ke",
        description="Knowledge Engine — data contract enforcement for markdown knowledge bases",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="<command>")

    # validate subcommand
    validate_parser = subparsers.add_parser("validate", help="Validate entity files against their schemas")
    validate_group = validate_parser.add_mutually_exclusive_group()
    validate_group.add_argument("path", nargs="?", help="Path to a single file to validate")
    validate_group.add_argument("--all", action="store_true", help="Validate entire KB")
    validate_parser.add_argument(
        "--limit",
        type=int,
        default=20,
        metavar="N",
        help="Max findings to show (0 = unlimited, default: 20)",
    )

    # create
    p_create = subparsers.add_parser("create", help="Create a new entity")
    p_create.add_argument("type", help="Entity type (e.g., project, research, inbox-item)")
    p_create.add_argument("--name", required=True, help="Entity name")
    p_create.set_defaults(func=cmd_create)

    # transition
    p_transition = subparsers.add_parser("transition", help="Change entity status")
    p_transition.add_argument("path", help="Path to entity file")
    p_transition.add_argument("status", help="New status value")
    p_transition.set_defaults(func=cmd_transition)

    # check-links
    p_links = subparsers.add_parser("check-links", help="Find broken wikilinks")
    p_links.set_defaults(func=cmd_check_links)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if args.command == "validate":
        if not args.all and not args.path:
            validate_parser.error("provide a path or --all")
        sys.exit(cmd_validate(args))

    if args.command == "create":
        args.func(args)

    if args.command == "transition":
        args.func(args)

    if args.command == "check-links":
        args.func(args)


if __name__ == "__main__":
    main()
