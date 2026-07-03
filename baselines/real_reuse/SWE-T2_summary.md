# Real-Reuse Summary Baseline: SWE-T2

SWE-agent improves software-engineering agents by shaping the agent-computer
interface. The method gives the language model concise search, navigation,
file-viewing, editing, execution feedback, and context-management tools so the
agent can inspect a repository, localize a bug, edit a focused patch, and verify
the result with tests.

For this locked task, use the issue or failing-test context, inspect files
before editing, produce a minimal unified diff, and verify with the requested
test command. Do not claim that tests passed unless the verification command
actually ran successfully.
