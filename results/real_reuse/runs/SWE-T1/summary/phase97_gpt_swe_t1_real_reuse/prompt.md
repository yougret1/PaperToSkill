# Real-Reuse Condition: summary

You are running a locked SWE-agent PaperToSkill real-reuse task. Use only the model-visible context and task prompt below. Do not request gold patches, hidden test patches, or scorer-only assets.

# Condition Context

# Real-Reuse Summary Baseline: SWE-T1

SWE-agent improves software-engineering agents by shaping the agent-computer
interface. The method gives the language model concise search, navigation,
file-viewing, editing, execution feedback, and context-management tools so the
agent can inspect a repository, localize a bug, edit a focused patch, and verify
the result with tests.

For this locked task, use the issue or failing-test context, inspect files
before editing, produce a minimal unified diff, and verify with the requested
test command. Do not claim that tests passed unless the verification command
actually ran successfully.

# Locked Task Prompt

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

# Output Contract

Return exactly one unified diff patch. The patch must apply from the starter workspace root and should be minimal.
