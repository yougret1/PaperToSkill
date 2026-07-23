from __future__ import annotations
import json
import re

def extract_implementation(text: str) -> str:
    value = json.loads(text)
    if set(value) != {'implementation'} or not isinstance(value['implementation'], str):
        raise ValueError('submission must contain only an implementation string')
    source = value['implementation']
    if re.search(r'(^|\n)\s*(import|from)\s+(socket|requests|urllib|subprocess|os)\b', source):
        raise ValueError('forbidden import')
    if 'def solve(' not in source:
        raise ValueError('solve(case) is missing')
    return source
