from __future__ import annotations

import json
import os
from pathlib import Path

from materialization_verifier_v3 import audit_materialization


CANONICAL_ROOT = Path(__file__).resolve().parent
ROOT = (
    Path("\\\\?\\" + str(CANONICAL_ROOT))
    if os.name == "nt"
    else CANONICAL_ROOT
)


if __name__ == "__main__":
    print(
        json.dumps(
            audit_materialization(
                ROOT / "materialization_remote_only_2026-07-23"
            ),
            indent=2,
            sort_keys=True,
        )
    )
