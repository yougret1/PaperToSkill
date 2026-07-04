#!/usr/bin/env python
"""Issue-aligned hidden check for the SWE-T1 SQLFluff fixture.

This script is intended to run after a candidate patch is applied to the
locked SQLFluff workspace with that workspace's `src/` directory on
PYTHONPATH. It directly exercises the model-visible issue reproduction: a TSQL
single-table query with an alias must not trigger L031.
"""

from __future__ import annotations

import sys

from sqlfluff.core import Linter


NO_ALIAS_QUERY = """SELECT [hello]
FROM
    mytable
"""

ALIAS_NO_JOIN_QUERY = """SELECT a.[hello]
FROM
    mytable AS a
"""

JOIN_ALIAS_QUERY = """SELECT a.[hello]
FROM
    mytable AS a
JOIN
    othertable AS b
ON
    a.id = b.id
"""


def l031_descriptions(sql: str) -> list[str]:
    result = Linter(dialect="tsql").lint_string(sql)
    return [
        violation.desc()
        for violation in result.get_violations()
        if violation.rule_code() == "L031"
    ]


def main() -> int:
    failures: list[str] = []
    if l031_descriptions(NO_ALIAS_QUERY):
        failures.append("no_alias_query_unexpected_l031")
    if l031_descriptions(ALIAS_NO_JOIN_QUERY):
        failures.append("alias_no_join_query_unexpected_l031")
    if not l031_descriptions(JOIN_ALIAS_QUERY):
        failures.append("join_alias_query_missing_l031_regression_guard")

    if failures:
        print("SWE-T1 issue-aligned check failed: " + ", ".join(failures))
        return 1
    print("SWE-T1 issue-aligned check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
