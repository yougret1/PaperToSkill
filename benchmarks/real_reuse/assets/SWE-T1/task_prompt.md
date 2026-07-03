# SWE-T1 Locked SWE-agent Task Prompt

Task type: issue-to-patch

You have a local repository snapshot in the starter workspace. The issue or
failing-test context is:

TSQL - L031 incorrectly triggers "Avoid using aliases in join condition" when no join present
## Expected Behaviour

Both of these queries should pass, the only difference is the addition of a table alias 'a':

1/ no alias

```
SELECT [hello]
FROM
    mytable
```

2/ same query with alias

```
SELECT a.[hello]
FROM
    mytable AS a
```

## Observed Behaviour

1/ passes
2/ fails with: L031: Avoid using aliases in join condition.

But there is no join condition :-)

## Steps to Reproduce

Lint queries above

## Dialect

TSQL

## Version

sqlfluff 0.6.9
Python 3.6.9

## Configuration

N/A

Verification command:

```powershell
D:\a_work\gitee\venvs\sqlfluff__sqlfluff-1625\Scripts\python.exe -m pytest test/cli/commands_test.py::test__cli__command_directed -q
```

Return a single unified diff patch. The patch must apply cleanly from the
workspace root. Keep the change minimal, inspect files before editing, and do
not claim success unless the verification command passes.
