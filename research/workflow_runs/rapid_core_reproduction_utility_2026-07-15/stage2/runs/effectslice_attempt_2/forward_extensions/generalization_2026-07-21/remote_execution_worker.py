from __future__ import annotations

import ast
import copy
import json
import sys
from types import MappingProxyType
from typing import Any


SAFE_MODULES = frozenset(
    {
        "bisect",
        "collections",
        "decimal",
        "fractions",
        "functools",
        "heapq",
        "itertools",
        "json",
        "math",
        "operator",
        "re",
        "statistics",
        "string",
    }
)

BANNED_NAMES = frozenset(
    {
        "breakpoint",
        "builtins",
        "compile",
        "ctypes",
        "delattr",
        "dir",
        "eval",
        "exec",
        "getattr",
        "globals",
        "help",
        "input",
        "inspect",
        "locals",
        "memoryview",
        "open",
        "os",
        "pathlib",
        "pickle",
        "random",
        "secrets",
        "setattr",
        "shelve",
        "shutil",
        "socket",
        "subprocess",
        "sys",
        "tempfile",
        "time",
        "type",
        "vars",
    }
)


class SafetyViolation(ValueError):
    pass


class SafetyVisitor(ast.NodeVisitor):
    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr.startswith("_"):
            raise SafetyViolation(f"private attribute access is forbidden: {node.attr}")
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if node.id.startswith("__") or node.id in BANNED_NAMES:
            raise SafetyViolation(f"forbidden identifier: {node.id}")
        self.generic_visit(node)

    def visit_Global(self, node: ast.Global) -> None:
        raise SafetyViolation("global declarations are forbidden")

    def visit_Nonlocal(self, node: ast.Nonlocal) -> None:
        raise SafetyViolation("nonlocal declarations are forbidden")

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            root = alias.name.split(".", 1)[0]
            if root not in SAFE_MODULES:
                raise SafetyViolation(f"module import is forbidden: {alias.name}")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.level:
            raise SafetyViolation("relative imports are forbidden")
        module = node.module or ""
        root = module.split(".", 1)[0]
        if module == "__future__":
            if any(alias.name != "annotations" for alias in node.names):
                raise SafetyViolation("only __future__.annotations is allowed")
            return
        if root not in SAFE_MODULES:
            raise SafetyViolation(f"module import is forbidden: {module}")
        self.generic_visit(node)


def validate_source(source: str) -> ast.Module:
    try:
        tree = ast.parse(source, filename="<model-submission>", mode="exec")
    except SyntaxError as exc:
        raise ValueError(f"syntax error at line {exc.lineno}: {exc.msg}") from exc
    SafetyVisitor().visit(tree)
    top_level_solve = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "solve"
    ]
    if len(top_level_solve) != 1 or isinstance(top_level_solve[0], ast.AsyncFunctionDef):
        raise ValueError("submission must define exactly one synchronous top-level solve")
    return tree


def _safe_import(
    name: str,
    globals_: dict[str, Any] | None = None,
    locals_: dict[str, Any] | None = None,
    fromlist: tuple[str, ...] = (),
    level: int = 0,
) -> Any:
    del globals_, locals_
    if level:
        raise ImportError("relative imports are forbidden")
    root = name.split(".", 1)[0]
    if name == "__future__":
        return __import__(name, fromlist=fromlist)
    if root not in SAFE_MODULES:
        raise ImportError(f"module import is forbidden: {name}")
    return __import__(name, fromlist=fromlist)


SAFE_BUILTINS = MappingProxyType(
    {
        "ArithmeticError": ArithmeticError,
        "AssertionError": AssertionError,
        "Exception": Exception,
        "IndexError": IndexError,
        "KeyError": KeyError,
        "RuntimeError": RuntimeError,
        "StopIteration": StopIteration,
        "TypeError": TypeError,
        "ValueError": ValueError,
        "ZeroDivisionError": ZeroDivisionError,
        "__import__": _safe_import,
        "abs": abs,
        "all": all,
        "any": any,
        "bool": bool,
        "dict": dict,
        "divmod": divmod,
        "enumerate": enumerate,
        "filter": filter,
        "float": float,
        "format": format,
        "frozenset": frozenset,
        "int": int,
        "isinstance": isinstance,
        "issubclass": issubclass,
        "iter": iter,
        "len": len,
        "list": list,
        "map": map,
        "max": max,
        "min": min,
        "next": next,
        "pow": pow,
        "range": range,
        "repr": repr,
        "reversed": reversed,
        "round": round,
        "set": set,
        "slice": slice,
        "sorted": sorted,
        "str": str,
        "sum": sum,
        "tuple": tuple,
        "zip": zip,
    }
)


def canonical_json(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def execute(payload: dict[str, Any]) -> dict[str, Any]:
    source = payload.get("implementation")
    cases = payload.get("cases")
    if not isinstance(source, str) or not isinstance(cases, list):
        return {"status": "invalid_submission", "reason": "invalid worker input"}
    try:
        tree = validate_source(source)
    except SafetyViolation as exc:
        return {"status": "safety_policy_violation", "reason": str(exc)}
    except ValueError as exc:
        return {"status": "invalid_submission", "reason": str(exc)}

    namespace: dict[str, Any] = {
        "__builtins__": SAFE_BUILTINS,
        "__name__": "model_submission",
    }
    try:
        code = compile(tree, "<model-submission>", "exec", dont_inherit=True)
        exec(code, namespace, namespace)
    except Exception as exc:
        return {
            "status": "invalid_submission",
            "reason": f"load failed: {type(exc).__name__}: {str(exc)[:500]}",
        }
    solve = namespace.get("solve")
    if not callable(solve):
        return {"status": "invalid_submission", "reason": "solve is not callable"}

    outputs: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    mutations: list[str] = []
    for item in cases:
        if not isinstance(item, dict) or not isinstance(item.get("case_id"), str):
            return {"status": "invalid_worker_fixture", "reason": "invalid case row"}
        case_id = item["case_id"]
        original = copy.deepcopy(item.get("payload"))
        case = copy.deepcopy(original)
        try:
            output = solve(case)
            canonical_json(output)
            outputs.append({"case_id": case_id, "output": output})
        except Exception as exc:
            errors.append(
                {
                    "case_id": case_id,
                    "error_type": type(exc).__name__,
                    "message": str(exc)[:500],
                }
            )
        if case != original:
            mutations.append(case_id)
    return {
        "status": "completed",
        "outputs": outputs,
        "errors": errors,
        "mutated_case_ids": mutations,
    }


def main() -> None:
    try:
        request = json.load(sys.stdin)
        result = execute(request)
    except Exception as exc:
        result = {
            "status": "worker_failure",
            "reason": f"{type(exc).__name__}: {str(exc)[:500]}",
        }
    sys.stdout.buffer.write(canonical_json(result))


if __name__ == "__main__":
    main()
