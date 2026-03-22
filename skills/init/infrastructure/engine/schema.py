"""Schema registry for Knowledge Engine.

Discovers YAML type schemas from skill folders, resolves inheritance,
dynamically builds Pydantic v2 models, and resolves which schema applies
to a given file path.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class TypeSchema:
    name: str
    description: str = ""
    folder: str = ""
    file_pattern: str = "{slug}/README.md"
    kind_value: str = ""
    inherits: str = ""
    status_lifecycle: dict[str, list[str]] = field(default_factory=dict)
    fields: dict[str, dict[str, Any]] = field(default_factory=dict)
    overrides: dict[str, dict[str, Any]] = field(default_factory=dict)
    # Names of fields inherited from base (used by build_pydantic_model to
    # keep base required-ness authoritative for those fields)
    base_field_names: frozenset[str] = field(default_factory=frozenset)
    # Required field names as declared in base schema (authoritative for base fields)
    base_required_names: frozenset[str] = field(default_factory=frozenset)


def _load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_schemas(skills_dir: Path) -> dict[str, TypeSchema]:
    """Discover and load all type schemas from skills_dir.

    Loads base.yaml first, then globs skills/*/types/*.yaml for type schemas.
    For each type schema that inherits base: merges base fields, then applies
    the type's own fields on top (type-specific fields override base fields
    for the same key), then applies explicit overrides.
    """
    base_path = skills_dir / "core" / "types" / "base.yaml"
    base_data = _load_yaml(base_path)
    base_fields: dict[str, dict[str, Any]] = base_data.get("fields", {})

    schemas: dict[str, TypeSchema] = {}

    for yaml_path in skills_dir.glob("*/types/*.yaml"):
        # Skip base.yaml itself
        if yaml_path == base_path:
            continue

        data = _load_yaml(yaml_path)
        schema_name = data.get("name", yaml_path.stem)

        # Start with a copy of base fields if this schema inherits base
        inherits = data.get("inherits", "")
        if inherits == "base":
            merged_fields: dict[str, dict[str, Any]] = {
                k: dict(v) for k, v in base_fields.items()
            }
        else:
            merged_fields = {}

        # Apply type-specific fields on top (override base for same-name fields)
        type_fields: dict[str, dict[str, Any]] = data.get("fields", {})
        for fname, fdef in type_fields.items():
            merged_fields[fname] = dict(fdef)

        # Apply explicit overrides section (if present)
        overrides: dict[str, dict[str, Any]] = data.get("overrides", {})
        for fname, override_def in overrides.items():
            if fname in merged_fields:
                merged_fields[fname] = {**merged_fields[fname], **override_def}
            else:
                merged_fields[fname] = dict(override_def)

        schema = TypeSchema(
            name=schema_name,
            description=data.get("description", ""),
            folder=data.get("folder", ""),
            file_pattern=data.get("file_pattern", "{slug}/README.md"),
            kind_value=data.get("kind_value") or data.get("type_value", ""),
            inherits=inherits,
            status_lifecycle=data.get("status_lifecycle", {}),
            fields=merged_fields,
            overrides=overrides,
            base_field_names=frozenset(base_fields.keys()) if inherits == "base" else frozenset(),
            base_required_names=frozenset(
                k for k, v in base_fields.items() if v.get("required", False)
            ) if inherits == "base" else frozenset(),
        )
        schemas[schema_name] = schema

    return schemas


def _map_field_type(field_def: dict[str, Any]):
    """Map a schema field definition to a Python type annotation."""
    from typing import Any as AnyType

    ftype = field_def.get("type", "any")

    if ftype == "string":
        # Check for inline enum on string fields
        enum_values = field_def.get("enum", [])
        if enum_values:
            from typing import Literal
            return Literal[tuple(enum_values)]
        return str
    elif ftype == "enum":
        values = field_def.get("values", [])
        if values:
            from typing import Literal
            return Literal[tuple(values)]
        return str
    elif ftype == "float":
        return float
    elif ftype == "integer":
        return int
    elif ftype == "list":
        return list
    elif ftype == "date":
        import datetime
        from typing import Union
        return Union[str, datetime.date]
    elif ftype == "any":
        return AnyType
    else:
        return AnyType


def build_pydantic_model(schema: TypeSchema) -> type:
    """Dynamically build a Pydantic v2 model from a TypeSchema.

    Required fields become (type, ...).
    Optional fields become (type | None, None).
    The model is configured with extra="allow" so unknown frontmatter fields
    do not cause validation errors.
    """
    from pydantic import create_model, ConfigDict

    field_definitions: dict[str, Any] = {}

    for fname, fdef in schema.fields.items():
        python_type = _map_field_type(fdef)
        schema_required = fdef.get("required", False)

        # For fields inherited from base, type schemas may declare required: true
        # for documentation purposes (e.g. "this type always needs updated").
        # However, at the Pydantic validation layer we only enforce required for
        # fields that are truly new to this type (not in base), keeping base fields
        # optional so partial frontmatter still validates without errors.
        # Exception: if the base itself marked a field required (type/id/name/status/
        # created), that required-ness came through the merge and is enforced.
        is_base_field = fname in schema.base_field_names
        if is_base_field:
            # For fields inherited from base, use the base schema's required
            # declaration as authoritative.  Type schemas may re-declare a field
            # with required: true for documentation/validation-rule purposes, but
            # at the Pydantic layer we keep the base's intent so that partial
            # frontmatter (e.g. missing `updated`) still validates.
            required = fname in schema.base_required_names
        else:
            required = schema_required

        if required:
            field_definitions[fname] = (python_type, ...)
        else:
            # Optional: allow None, default to None
            from typing import Union
            optional_type = Union[python_type, None]
            field_definitions[fname] = (optional_type, None)

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    Model = create_model(
        schema.name.replace("-", "_"),
        __config__=model_config,
        **field_definitions,
    )
    return Model


def resolve_schema_for_path(path: Path, schemas: dict[str, TypeSchema]) -> TypeSchema | None:
    """Resolve which schema applies to a given file path.

    Checks whether any parent directory name of the path matches a schema's
    folder. Returns the first matching schema, or None if no match found.
    """
    # Collect all parent directory names for the path
    parent_names = {p.name for p in path.parents}

    for schema in schemas.values():
        if schema.folder and schema.folder in parent_names:
            return schema

    return None
