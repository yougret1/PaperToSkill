# Real-Reuse Condition: papertoskill

You are running a locked SWE-agent PaperToSkill real-reuse task. Use only the model-visible context and task prompt below. Do not request gold patches, hidden test patches, or scorer-only assets.

# Condition Context

---
name: swe-agent-paper-skill
description: Use when applying the paper-derived method from SWE-agent Agent-Computer Interfaces Enable Automated Software Engineering as an agent skill. Extracts workflow steps, assumptions, validation checks, failure cases, and transfer notes.
---

# SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering

This skill converts the source paper's operational contribution into an agent
workflow. It is a scaffolded extraction and should be audited against the source
before being used as validated paper knowledge.

## Source

- Source file: `papers/auto_notes/swe_agent_auto_note.md`

## Paper Snapshot

... performance of language model agents. As a result of this exploration, we introduce
SWE-agent: a system that facilitates LM agents to autonomously use computers to solve
software engineering tasks. SWE-agents custom agent-computer interface (ACI)
significantly enhances an agents ability to ... Source anchors: lines 14-32.

## Central Contribution

As a result of this exploration, we introduce SWE-agent: a system that facilitates LM
agents to autonomously use computers to solve software engineering tasks.

## Inputs

- The source paper or paper excerpt.
- The target task where the paper's method should be reused.
- Available tools, runtime constraints, and output format expectations.

## Workflow

1. Frame the method as an agent-computer interface that shapes commands, documentation, state, history, and feedback: ... back to the LM. It also tracks the history of all previous commands and observations and, at each step, manages how these should be formatted and combined with .... Source anchors: lines 135-139.
2. Keep ACI actions simple, compact, efficient, and paired with concise environment feedback: ... Actions should be simple and easy to understand for agents. Many bash commands have documentation that includes dozens of options. Simple commands with a few options and .... Source anchors: lines 148-152.
3. Use SWE-agent's ReAct loop with thoughts, commands, execution feedback, and common Linux utilities when needed: ... search, navigate, edit, and execute code commands. The ACI com- prises several principal components, including search/navigation, file viewer, file editor, and context .... Source anchors: lines 173-177.
4. Localize code with LM-friendly search and navigation commands such as find_file, search_file, and search_dir: ... an issue. We introduce the special commands find_file, search_file, and search_dir, which output a summary of search results when searching for filenames and strings within files .... Source anchors: lines 178-182.
5. Inspect code through the file viewer with bounded windows, line numbers, scrolling, and goto: ... that the agent write a more specific query. File viewer. After finding a file they want to view, agents use the interactive file viewer by calling the command open on the .... Source anchors: lines 235-239.
6. Apply focused multiline edits through the edit command and immediately inspect the updated file view: ... with the file viewer, allowing agents to replace a specific range of lines in the open file. This command takes 3 required arguments: the start line, end line, and replacement .... Source anchors: lines 244-248.
7. Use editing guardrails such as linting feedback and discarded invalid edits to avoid error propagation: ... files in an IDE, we integrate a code linter into the edit function to alert the agent of mistakes it may have introduced when editing a file. Select errors from the linter .... Source anchors: lines 250-254.
8. Manage context with command documentation, demonstrations, malformed-response feedback, and collapsed old observations: Context management. The SWE-agent system uses informative prompts, error messages, and history processors to keep agent context concise and informative. Agents receive .... Source anchors: lines 255-259.

## Validation

- Evaluate on SWE-bench full test, SWE-bench Lite, and HumanEvalFix with automated software-engineering metrics: ... Experimental Setup Datasets. We primarily evaluate on the SWE-bench dataset, which includes 2,294 task instances from 12 different repositories of popular Python packages [20]. .... Source anchors: lines 268-272.
- Compare against non-interactive RAG and Shell-only or Basic CLI baselines under the reported settings: Baselines. We compare SWE-agent to two baselines. The first setting is the non-interactive, retrieval- augmented generation (RAG) baselines established in Jimenez et al. [20]. .... Source anchors: lines 287-291.
- Report % Resolved or pass@1, average cost, and the per-instance budget boundary: ... after interaction. Metrics. We report % Resolved or pass@1 as the main metric, which is the proportion of instances for which all tests pass successfully after the model .... Source anchors: lines 294-298.
- Record the main SWE-bench and HumanEvalFix performance numbers as reported references: ... solving 12.47% (286/2,294) of the full SWE-bench test set and 18.00% (54/300) of the Lite split. As shown in Table 1, compared to RAG on Lite, SWE-agent is 8-13x more costly .... Source anchors: lines 309-313.
- Use ACI ablations to separate the effect of editor, search, file viewer, context, and demonstrations: ... 3: SWE-bench Lite performance under ablations to the SWE-agent interface, which is denoted by . We consider different approaches to searching and editing (see Figures 5 and .... Source anchors: lines 366-370.
- Track configuration search over window size, history processing, and decoding temperature: ... edits were submitted automatically. Configuration search. During the design process of SWE-agent, we arrived at the final ACI design through qualitative analysis of .... Source anchors: lines 299-303.

## Failure Cases

- Run generated code in sandboxed or ephemeral containers rather than on an unprotected personal machine: ... framework are both carried out in sand-boxed code environments, which is made possible with Docker. Executing code in a Docker container ensures that its effects are .... Source anchors: lines 7688-7692.
- Verify official repositories and datasets to avoid malicious evaluation infrastructure or injected instructions: ... malicious code or instructions to generate malicious code. For instance, an unofficial repository claiming to host an inference/evaluation harness for SWE-agent/bench could .... Source anchors: lines 7696-7700.
- Do not ignore misuse risks when software-engineering agents can produce offensive or malicious code: ... of software engineering agents being deployed in the real world. Prior works have conceptualized and put forth prototypes of agents that can carry out offensive security .... Source anchors: lines 7703-7707.
- Treat the ACI development process as manually crafted unless an automated interface-design loop is actually implemented: ... in this work, the ACI development process and case studies are done manually. Many components of SWE-agent were crafted from observations of recurring behavior within a .... Source anchors: lines 7737-7741.
- Do not assume ACI principles transfer unchanged beyond programmatic software-engineering and code-generation tasks: ... the scope of SWE-agent is exclusively focused on programmatic tasks like software en- gineering and code generation. Were curious to see whether the same principles of .... Source anchors: lines 7746-7750.
- Watch for editing failure cascades, repeated failed edits, and recovery degradation: ... minority of edit actions raise a linting error; out of 2,294 task instances, 1,185 (51.7%) of SWE-agent w/ GPT-4 Turbo trajectories have 1+ failed edits. While agents .... Source anchors: lines 593-597.

## Transfer Notes

- Check whether the target harness supports the tools assumed by the paper.
- Replace framework-specific commands with local equivalents before execution.
- Keep source-backed steps separate from inferred adaptations.
- Record any failed branch as part of the skill's future revision history.

# Shared Source Context

# Model-Visible Source Context

Evidence boundary: this source slice is model-visible and is provided equally to all primary conditions for a pre-registered source-context follow-up. It excludes scorer-only gold patches and hidden test patches.

## src/sqlfluff/rules/L031.py @ 14e1a23a3166b9a645a16de96f694c77a5d4abb7

```python
"""Implementation of Rule L031."""

from collections import Counter, defaultdict
from typing import Generator, NamedTuple

from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L031(BaseRule):
    """Avoid table aliases in from clauses and join conditions.

    | **Anti-pattern**
    | In this example, alias 'o' is used for the orders table, and 'c' is used for 'customers' table.

    .. code-block:: sql

        SELECT
            COUNT(o.customer_id) as order_amount,
            c.name
        FROM orders as o
        JOIN customers as c on o.id = c.user_id


    | **Best practice**
    |  Avoid aliases.

    .. code-block:: sql

        SELECT
            COUNT(orders.customer_id) as order_amount,
            customers.name
        FROM orders
        JOIN customers on orders.id = customers.user_id

        -- Self-join will not raise issue

        SELECT
            table.a,
            table_alias.b,
        FROM
            table
            LEFT JOIN table AS table_alias ON table.foreign_key = table_alias.foreign_key

    """

    def _eval(self, segment, **kwargs):
        """Identify aliases in from clause and join conditions.

        Find base table, table expressions in join, and other expressions in select clause
        and decide if it's needed to report them.
        """
        if segment.is_type("select_statement"):
            # A buffer for all table expressions in join conditions
            from_expression_elements = []
            column_reference_segments = []

            from_clause_segment = segment.get_child("from_clause")

            if not from_clause_segment:
                return None

            from_expression = from_clause_segment.get_child("from_expression")
            from_expression_element = None
            if from_expression:
                from_expression_element = from_expression.get_child(
                    "from_expression_element"
                )

            if not from_expression_element:
                return None
            from_expression_element = from_expression_element.get_child(
                "table_expression"
            )

            # Find base table
            base_table = None
            if from_expression_element:
                base_table = from_expression_element.get_child("object_reference")

            from_clause_index = segment.segments.index(from_clause_segment)
            from_clause_and_after = segment.segments[from_clause_index:]

            for clause in from_clause_and_after:
                for from_expression_element in clause.recursive_crawl(
                    "from_expression_element"
                ):
                    from_expression_elements.append(from_expression_element)
                for column_reference in clause.recursive_crawl("column_reference"):
                    column_reference_segments.append(column_reference)

            return (
                self._lint_aliases_in_join(
                    base_table,
                    from_expression_elements,
                    column_reference_segments,
                    segment,
                )
                or None
            )
        return None

    class TableAliasInfo(NamedTuple):
        """Structure yielded by_filter_table_expressions()."""

        table_ref: BaseSegment
        whitespace_ref: BaseSegment
        alias_exp_ref: BaseSegment
        alias_identifier_ref: BaseSegment

    @classmethod
    def _filter_table_expressions(
        cls, base_table, from_expression_elements
    ) -> Generator[TableAliasInfo, None, None]:
        for from_expression in from_expression_elements:
            table_expression = from_expression.get_child("table_expression")
            if not table_expression:
                continue
            table_ref = table_expression.get_child("object_reference")

            # If the from_expression_element has no object_references - skip it
            # An example case is a lateral flatten, where we have a function segment
            # instead of a table_reference segment.
            if not table_ref:
                continue

            # If this is self-join - skip it
            if (
                base_table
                and base_table.raw == table_ref.raw
                and base_table != table_ref
            ):
                continue

            whitespace_ref = from_expression.get_child("whitespace")

            # If there's no alias expression - skip it
            alias_exp_ref = from_expression.get_child("alias_expression")
            if alias_exp_ref is None:
                continue

            alias_identifier_ref = alias_exp_ref.get_child("identifier")
            yield cls.TableAliasInfo(
                table_ref, whitespace_ref, alias_exp_ref, alias_identifier_ref
            )

    def _lint_aliases_in_join(
        self, base_table, from_expression_elements, column_reference_segments, segment
    ):
        """Lint and fix all aliases in joins - except for self-joins."""
        # A buffer to keep any violations.
        violation_buff = []

        to_check = list(
            self._filter_table_expressions(base_table, from_expression_elements)
        )

        # How many times does each table appear in the FROM clause?
        table_counts = Counter(ai.table_ref.raw for ai in to_check)

        # What is the set of aliases used for each table? (We are mainly
        # interested in the NUMBER of different aliases used.)
        table_aliases = defaultdict(set)
        for ai in to_check:
            table_aliases[ai.table_ref.raw].add(ai.alias_identifier_ref.raw)

        # For each aliased table, check whether to keep or remove it.
        for alias_info in to_check:
            # If the same table appears more than once in the FROM clause with
            # different alias names, do not consider removing its aliases.
            # The aliases may have been introduced simply to make each
            # occurrence of the table independent within the query.
            if (
                table_counts[alias_info.table_ref.raw] > 1
                and len(table_aliases[alias_info.table_ref.raw]) > 1
            ):
                continue

            select_clause = segment.get_child("select_clause")

            ids_refs = []

            # Find all references to alias in select clause
            alias_name = alias_info.alias_identifier_ref.raw
            for alias_with_column in select_clause.recursive_crawl("object_reference"):
                used_alias_ref = alias_with_column.get_child("identifier")
                if used_alias_ref and used_alias_ref.raw == alias_name:
                    ids_refs.append(used_alias_ref)

            # Find all references to alias in column references
            for exp_ref in column_reference_segments:
                used_alias_ref = exp_ref.get_child("identifier")
                # exp_ref.get_child('dot') ensures that the column reference includes a table reference
                if used_alias_ref.raw == alias_name and exp_ref.get_child("dot"):
                    ids_refs.append(used_alias_ref)

            # Fixes for deleting ` as sth` and for editing references to aliased tables
            fixes = [
                *[
                    LintFix("delete", d)
                    for d in [alias_info.alias_exp_ref, alias_info.whitespace_ref]
                ],
                *[
                    LintFix("edit", alias, alias.edit(alias_info.table_ref.raw))
                    for alias in [alias_info.alias_identifier_ref, *ids_refs]
                ],
            ]

            violation_buff.append(
                LintResult(
                    anchor=alias_info.alias_identifier_ref,
                    description="Avoid using aliases in join condition",
                    fixes=fixes,
                )
            )

        return violation_buff or None
```

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
