from __future__ import annotations

import json

from verify_forward_preregistration_v2 import VerificationError, audit

__all__ = ["VerificationError", "audit"]


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, sort_keys=True))
