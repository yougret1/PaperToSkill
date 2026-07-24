from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
from types import ModuleType
from typing import Any, Iterable


FORWARD_ROOT = Path(__file__).resolve().parent
RUNTIME_PATH = (
    FORWARD_ROOT
    / "materialization_remote_only_2026-07-23"
    / "support"
    / "task_runtime.py"
)
DEFAULT_OUTPUT = (
    FORWARD_ROOT
    / "fg5_development_2026-07-24"
    / "output_contract_registry.json"
)
PROBE_VERSION = "fg5-public-output-shape-v1"
PROBES_PER_TASK = 64

DYNAMIC_MAP_SOURCES: dict[str, dict[tuple[str, ...], str]] = {
    "NLP-LLM-01": {("by_name",): "case.segments[*].name"},
    "DATA-LEI-01": {("communities",): "case.communities.keys()"},
    "DATA-LEI-02": {("members",): "case.refinement.values()"},
}


class ContractRegistryError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractRegistryError(message)


def canonical_json(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_runtime(path: Path = RUNTIME_PATH) -> ModuleType:
    spec = importlib.util.spec_from_file_location("fg5_public_task_runtime", path)
    require(spec is not None and spec.loader is not None, "cannot load public runtime")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _rename_data_lei_nodes(case: dict[str, Any], index: int) -> None:
    old_nodes = sorted(str(key) for key in case["communities"])
    mapping = {
        old: f"fg5_node_{index:03d}_{position:02d}"
        for position, old in enumerate(old_nodes)
    }
    case["communities"] = {
        mapping[str(key)]: value for key, value in case["communities"].items()
    }
    case["edges"] = [
        [mapping[str(left)], mapping[str(right)], weight]
        for left, right, weight in case["edges"]
    ]


def public_probe_case(
    runtime: ModuleType,
    task_id: str,
    index: int,
) -> dict[str, Any]:
    require(0 <= index < PROBES_PER_TASK, "probe index is out of range")
    seed = f"{PROBE_VERSION}|{task_id}|{index:03d}"
    case = runtime.generate_case(task_id, seed)

    # These public identifier changes expose input-derived map keys without
    # consulting either private registry or persisting a solved output.
    if task_id == "NLP-LLM-01":
        for position, segment in enumerate(case["segments"]):
            segment["name"] = f"fg5_segment_{index:03d}_{position:02d}"
    elif task_id == "DATA-LEI-01":
        _rename_data_lei_nodes(case, index)
    elif task_id == "DATA-LEI-02":
        labels = sorted(set(str(value) for value in case["refinement"].values()))
        mapping = {
            old: f"fg5_group_{index:03d}_{position:02d}"
            for position, old in enumerate(labels)
        }
        case["refinement"] = {
            key: mapping[str(value)] for key, value in case["refinement"].items()
        }
    elif task_id == "AGENT-RF-02" and index == 0:
        case["attempts"] = []
    elif task_id == "AGENT-RA-02" and index == 0:
        case["initial_state"] = "fg5_missing_state"
    elif task_id == "AGENT-RA-02" and index == 1:
        case["tool_observations"].pop("lookup", None)
    elif task_id == "AGENT-RA-02" and index == 2:
        case["max_steps"] = 0
    return case


def _scalar_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    raise ContractRegistryError(f"unsupported JSON value type: {type(value)!r}")


def infer_shape(
    values: list[Any],
    *,
    path: tuple[str, ...] = (),
    dynamic_maps: dict[tuple[str, ...], str] | None = None,
) -> dict[str, Any]:
    require(bool(values), f"no observations for output path {path!r}")
    dynamic_maps = dynamic_maps or {}
    observed = {_scalar_type(value) for value in values}
    non_null_types = observed - {"null"}
    if "null" in observed and non_null_types:
        non_null = [value for value in values if value is not None]
        return {
            "anyOf": [
                {"type": "null"},
                infer_shape(non_null, path=path, dynamic_maps=dynamic_maps),
            ]
        }
    if observed == {"null"}:
        return {"type": "null"}
    if observed <= {"integer", "number"} and "number" in observed:
        return {"type": "number"}
    require(len(observed) == 1, f"incompatible output types at {path!r}: {observed}")
    kind = next(iter(observed))
    if kind in {"boolean", "integer", "number", "string"}:
        return {"type": kind}
    if kind == "array":
        lengths = {len(value) for value in values}
        if len(lengths) == 1 and next(iter(lengths)) > 0:
            length = next(iter(lengths))
            positional = [
                infer_shape(
                    [value[index] for value in values],
                    path=path + (str(index),),
                    dynamic_maps=dynamic_maps,
                )
                for index in range(length)
            ]
            if len({canonical_json(item) for item in positional}) > 1:
                return {
                    "type": "array",
                    "prefixItems": positional,
                    "items": False,
                    "minItems": length,
                    "maxItems": length,
                }
        items = [item for value in values for item in value]
        return {
            "type": "array",
            "items": (
                infer_shape(items, path=path + ("*",), dynamic_maps=dynamic_maps)
                if items
                else {"type": "unknown"}
            ),
        }

    objects = values
    dynamic_source = dynamic_maps.get(path)
    if dynamic_source is not None:
        items = [item for value in objects for item in value.values()]
        require(bool(items), f"dynamic output map is always empty at {path!r}")
        return {
            "type": "object",
            "dynamicKeysFrom": dynamic_source,
            "additionalProperties": infer_shape(
                items,
                path=path + ("<dynamic-key>",),
                dynamic_maps=dynamic_maps,
            ),
        }

    all_keys = sorted({str(key) for value in objects for key in value})
    required = sorted(
        key for key in all_keys if all(key in value for value in objects)
    )
    properties = {
        key: infer_shape(
            [value[key] for value in objects if key in value],
            path=path + (key,),
            dynamic_maps=dynamic_maps,
        )
        for key in all_keys
    }
    return {
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": False,
    }


def contract_prompt(task_id: str, output_shape: dict[str, Any]) -> str:
    schema = json.dumps(output_shape, sort_keys=True, indent=2, ensure_ascii=False)
    return (
        "[EXACT OUTPUT CONTRACT]\n"
        f"For task {task_id}, solve(case) must return a JSON value matching the "
        "structural schema below. This is a schema, not an example and not a set "
        "of expected answers. Every name under properties is a literal output key. "
        "Every key listed under required must be present. additionalProperties=false "
        "forbids unlisted keys at that object level. dynamicKeysFrom means the object "
        "keys are arbitrary JSON strings that must be copied verbatim from the "
        "indicated input location; never parse, coerce, numerically validate, or "
        "impose a naming pattern on those keys. anyOf denotes the allowed JSON types. "
        "Do not rename fields or change their nesting.\n"
        "OUTPUT STRUCTURAL SCHEMA:\n"
        f"{schema}\n\n"
    )


def shape_violations(
    value: Any,
    shape: dict[str, Any],
    *,
    path: str = "$",
) -> list[str]:
    if "anyOf" in shape:
        alternatives = [shape_violations(value, item, path=path) for item in shape["anyOf"]]
        if any(not issues for issues in alternatives):
            return []
        return [f"{path}: value matches none of the allowed schemas"]

    kind = shape.get("type")
    if kind == "unknown":
        return []
    if kind == "null":
        return [] if value is None else [f"{path}: expected null"]
    if kind == "boolean":
        return [] if isinstance(value, bool) else [f"{path}: expected boolean"]
    if kind == "integer":
        return (
            []
            if isinstance(value, int) and not isinstance(value, bool)
            else [f"{path}: expected integer"]
        )
    if kind == "number":
        return (
            []
            if isinstance(value, (int, float)) and not isinstance(value, bool)
            else [f"{path}: expected number"]
        )
    if kind == "string":
        return [] if isinstance(value, str) else [f"{path}: expected string"]
    if kind == "array":
        if not isinstance(value, list):
            return [f"{path}: expected array"]
        issues: list[str] = []
        if "prefixItems" in shape:
            minimum = int(shape.get("minItems", len(shape["prefixItems"])))
            maximum = int(shape.get("maxItems", len(shape["prefixItems"])))
            if not minimum <= len(value) <= maximum:
                issues.append(f"{path}: expected {minimum}..{maximum} items")
            for index, item_shape in enumerate(shape["prefixItems"]):
                if index < len(value):
                    issues.extend(
                        shape_violations(value[index], item_shape, path=f"{path}[{index}]")
                    )
            return issues
        item_shape = shape.get("items", {"type": "unknown"})
        for index, item in enumerate(value):
            issues.extend(shape_violations(item, item_shape, path=f"{path}[{index}]"))
        return issues
    if kind == "object":
        if not isinstance(value, dict):
            return [f"{path}: expected object"]
        if "dynamicKeysFrom" in shape:
            issues = []
            item_shape = shape["additionalProperties"]
            for key, item in value.items():
                if not isinstance(key, str):
                    issues.append(f"{path}: expected string object key")
                issues.extend(shape_violations(item, item_shape, path=f"{path}.{key}"))
            return issues
        properties = shape.get("properties", {})
        required = set(shape.get("required", []))
        actual = set(value)
        issues = [f"{path}: missing required key {key!r}" for key in sorted(required - actual)]
        if shape.get("additionalProperties") is False:
            issues.extend(
                f"{path}: unexpected key {key!r}" for key in sorted(actual - set(properties))
            )
        for key in sorted(actual & set(properties)):
            issues.extend(shape_violations(value[key], properties[key], path=f"{path}.{key}"))
        return issues
    raise ContractRegistryError(f"unsupported shape kind at {path}: {kind!r}")


def build_registry_value(runtime: ModuleType | None = None) -> dict[str, Any]:
    runtime = runtime or load_runtime()
    task_ids = sorted(runtime.SOLVERS)
    require(len(task_ids) == 24, "public runtime task count changed")
    tasks: list[dict[str, Any]] = []
    for task_id in task_ids:
        cases = [
            public_probe_case(runtime, task_id, index)
            for index in range(PROBES_PER_TASK)
        ]
        outputs = [runtime.solve(task_id, case) for case in cases]
        shape = infer_shape(
            outputs,
            dynamic_maps=DYNAMIC_MAP_SOURCES.get(task_id, {}),
        )
        prompt = contract_prompt(task_id, shape)
        tasks.append(
            {
                "task_id": task_id,
                "input_set_sha256": sha256_bytes(canonical_json(cases)),
                "output_set_sha256": sha256_bytes(canonical_json(outputs)),
                "output_shape": shape,
                "prompt": prompt,
                "prompt_sha256": sha256_bytes(prompt.encode("utf-8")),
            }
        )
    return {
        "schema_version": "effectslice-fg5-public-output-contracts.v1",
        "probe_version": PROBE_VERSION,
        "task_count": len(tasks),
        "probes_per_task": PROBES_PER_TASK,
        "tasks": tasks,
    }


def write_registry(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(canonical_json(value) + b"\n")
    os.replace(temporary, path)


def build_registry(path: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    value = build_registry_value()
    write_registry(path, value)
    return value


def verify_registry(path: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    require(path.is_file(), "output contract registry is missing")
    stored = json.loads(path.read_text(encoding="utf-8"))
    expected = build_registry_value()
    require(stored == expected, "output contract registry is not reproducible")
    require(
        all("type\":\"unknown" not in canonical_json(row["output_shape"]).decode("utf-8")
            for row in stored["tasks"]),
        "one or more output array item shapes are unknown",
    )
    return {
        "status": "passed",
        "task_count": stored["task_count"],
        "probes_per_task": stored["probes_per_task"],
        "registry_sha256": sha256_bytes(canonical_json(stored)),
    }


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build", "verify"))
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "build":
        value = build_registry(args.output)
        result = {
            "status": "passed",
            "task_count": value["task_count"],
            "probes_per_task": value["probes_per_task"],
            "registry_sha256": sha256_bytes(canonical_json(value)),
        }
    else:
        result = verify_registry(args.output)
    print(json.dumps(result, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ContractRegistryError as exc:
        print(f"ERROR: {exc}", file=os.sys.stderr)
        raise SystemExit(2)
