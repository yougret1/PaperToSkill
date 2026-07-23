from __future__ import annotations
import importlib.util
from pathlib import Path

_PATH = Path(__file__).resolve().parents[3] / 'support' / 'task_runtime.py'
_SPEC = importlib.util.spec_from_file_location('fg1_task_runtime', _PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError('cannot load frozen task runtime')
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)

TASK_ID = 'NLP-LLM-01'

def solve(case):
    return _MODULE.solve(TASK_ID, case)
