from __future__ import annotations
import importlib.util
from pathlib import Path

_PATH = Path(__file__).resolve().parents[3] / 'support' / 'task_runtime.py'
_SPEC = importlib.util.spec_from_file_location('fg1_task_runtime', _PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError('cannot load frozen task runtime')
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)

TASK_ID = 'SE-PE-01'

def expected_registry(registry_id: str):
    cases, expected = _MODULE.build_registry(TASK_ID, registry_id)
    return cases, expected

def score_outputs(registry_id: str, outputs: list[dict]):
    _, expected = expected_registry(registry_id)
    expected_by_id = {row['case_id']: row['output'] for row in expected}
    supplied = {row['case_id']: row['output'] for row in outputs}
    passed = sum(supplied.get(case_id) == value for case_id, value in expected_by_id.items())
    complete = set(supplied) == set(expected_by_id)
    return {'private_score': passed / len(expected_by_id), 'hard_contract_vector': [complete, passed == len(expected_by_id)]}
