#!/usr/bin/env python
"""Prepare locked Reflexion real-reuse fixtures."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "0.1"
PREPARED_ON = "2026-07-03"
STATUS = "prepared_assets_ready_for_dry_scoring"


REFLEXION_SUMMARY_FALLBACK = """# Generic Summary: Reflexion

Reflexion is a framework for improving language agents through verbal
reinforcement instead of updating model weights. It lets an agent reflect on
feedback from failed attempts, store lessons in memory, and use those lessons
in later trials.

The paper describes an actor that performs actions, an evaluator that scores
outcomes, and a self-reflection model that converts feedback into natural
language advice. The approach is tested on decision-making, reasoning, and
programming tasks, where it improves over several baselines.

The paper also notes limitations: agents can still get stuck, memory is bounded
by a simple window, and some tasks require more creative behavior than the
method reliably discovers.
"""


HOTPOTQA_EXAMPLE: dict[str, Any] = {
    "id": "5a8b57f25542995d1e6f1371",
    "question": "Were Scott Derrickson and Ed Wood of the same nationality?",
    "answer": "yes",
    "type": "comparison",
    "level": "hard",
    "supporting_facts": {
        "title": ["Scott Derrickson", "Ed Wood"],
        "sent_id": [0, 0],
    },
    "context": {
        "title": [
            "Ed Wood (film)",
            "Scott Derrickson",
            "Woodson, Arkansas",
            "Tyler Bates",
            "Ed Wood",
            "Deliver Us from Evil (2014 film)",
            "Adam Collis",
            "Sinister (film)",
            "Conrad Brooks",
            "Doctor Strange (2016 film)",
        ],
        "sentences": [
            [
                "Ed Wood is a 1994 American biographical period comedy-drama film directed and produced by Tim Burton, and starring Johnny Depp as cult filmmaker Ed Wood.",
                " The film concerns the period in Wood's life when he made his best-known films as well as his relationship with actor Bela Lugosi, played by Martin Landau.",
                " Sarah Jessica Parker, Patricia Arquette, Jeffrey Jones, Lisa Marie, and Bill Murray are among the supporting cast.",
            ],
            [
                "Scott Derrickson (born July 16, 1966) is an American director, screenwriter and producer.",
                " He lives in Los Angeles, California.",
                ' He is best known for directing horror films such as "Sinister", "The Exorcism of Emily Rose", and "Deliver Us From Evil", as well as the 2016 Marvel Cinematic Universe installment, "Doctor Strange."',
            ],
            [
                "Woodson is a census-designated place (CDP) in Pulaski County, Arkansas, in the United States.",
                " Its population was 403 at the 2010 census.",
                " It is part of the Little Rock-North Little Rock-Conway Metropolitan Statistical Area.",
                " Woodson and its accompanying Woodson Lake and Wood Hollow are the namesake for Ed Wood Sr., a prominent plantation owner, trader, and businessman at the turn of the 20th century.",
                " Woodson is adjacent to the Wood Plantation, the largest of the plantations own by Ed Wood Sr.",
            ],
            [
                "Tyler Bates (born June 5, 1965) is an American musician, music producer, and composer for films, television, and video games.",
                ' Much of his work is in the action and horror film genres, with films like "Dawn of the Dead, 300, Sucker Punch," and "John Wick."',
                " He has collaborated with directors like Zack Snyder, Rob Zombie, Neil Marshall, William Friedkin, Scott Derrickson, and James Gunn.",
                ' With Gunn, he has scored every one of the director\'s films; including "Guardians of the Galaxy", which became one of the highest grossing domestic movies of 2014, and its 2017 sequel.',
                ' In addition, he is also the lead guitarist of the American rock band Marilyn Manson, and produced its albums "The Pale Emperor" and "Heaven Upside Down".',
            ],
            [
                "Edward Davis Wood Jr. (October 10, 1924 - December 10, 1978) was an American filmmaker, actor, writer, producer, and director."
            ],
            [
                "Deliver Us from Evil is a 2014 American supernatural horror film directed by Scott Derrickson and produced by Jerry Bruckheimer.",
                ' The film is officially based on a 2001 non-fiction book entitled "Beware the Night" by Ralph Sarchie and Lisa Collier Cool, and its marketing campaign highlighted that it was "inspired by actual accounts".',
                " The film stars Eric Bana, Edgar Ramirez, Sean Harris, Olivia Munn, and Joel McHale in the main roles and was released on July 2, 2014.",
            ],
            [
                "Adam Collis is an American filmmaker and actor.",
                " He attended the Duke University from 1986 to 1990 and the University of California, Los Angeles from 2007 to 2010.",
                " He also studied cinema at the University of Southern California from 1991 to 1997.",
                ' Collis first work was the assistant director for the Scott Derrickson\'s short "Love in the Ruins" (1995).',
                ' In 1998, he played "Crankshaft" in Eric Koyanagi\'s "Hundred Percent".',
            ],
            [
                "Sinister is a 2012 supernatural horror film directed by Scott Derrickson and written by Derrickson and C. Robert Cargill.",
                " It stars Ethan Hawke as fictional true-crime writer Ellison Oswalt who discovers a box of home movies in his attic that puts his family in danger.",
            ],
            [
                "Conrad Brooks (born Conrad Biedrzycki on January 3, 1931 in Baltimore, Maryland) is an American actor.",
                " He moved to Hollywood, California in 1948 to pursue a career in acting.",
                ' He got his start in movies appearing in Ed Wood films such as "Plan 9 from Outer Space", "Glen or Glenda", and "Jail Bait."',
                " He took a break from acting during the 1960s and 1970s but due to the ongoing interest in the films of Ed Wood, he reemerged in the 1980s and has become a prolific actor.",
                " He also has since gone on to write, produce and direct several films.",
            ],
            [
                "Doctor Strange is a 2016 American superhero film based on the Marvel Comics character of the same name, produced by Marvel Studios and distributed by Walt Disney Studios Motion Pictures.",
                " It is the fourteenth film of the Marvel Cinematic Universe (MCU).",
                " The film was directed by Scott Derrickson, who wrote it with Jon Spaihts and C. Robert Cargill, and stars Benedict Cumberbatch as Stephen Strange, along with Chiwetel Ejiofor, Rachel McAdams, Benedict Wong, Michael Stuhlbarg, Benjamin Bratt, Scott Adkins, Mads Mikkelsen, and Tilda Swinton.",
                ' In "Doctor Strange", surgeon Strange learns the mystic arts after a career-ending car accident.',
            ],
        ],
    },
}


HUMANEVAL_0: dict[str, str] = {
    "task_id": "HumanEval/0",
    "entry_point": "has_close_elements",
    "prompt": '''from typing import List


def has_close_elements(numbers: List[float], threshold: float) -> bool:
    """ Check if in given list of numbers, are any two numbers closer to each other than
    given threshold.
    >>> has_close_elements([1.0, 2.0, 3.0], 0.5)
    False
    >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)
    True
    """
''',
    "canonical_solution": """    for idx, elem in enumerate(numbers):
        for idx2, elem2 in enumerate(numbers):
            if idx != idx2:
                distance = abs(elem - elem2)
                if distance < threshold:
                    return True

    return False
""",
    "test": """

METADATA = {
    'author': 'jt',
    'dataset': 'test'
}


def check(candidate):
    assert candidate([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.3) == True
    assert candidate([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.05) == False
    assert candidate([1.0, 2.0, 5.9, 4.0, 5.0], 0.95) == True
    assert candidate([1.0, 2.0, 5.9, 4.0, 5.0], 0.8) == False
    assert candidate([1.0, 2.0, 3.0, 4.0, 5.0, 2.0], 0.1) == True
    assert candidate([1.1, 2.2, 3.1, 4.1, 5.1], 1.0) == True
    assert candidate([1.1, 2.2, 3.1, 4.1, 5.1], 0.5) == False

""",
}


FAILED_FIRST_ATTEMPT = '''from typing import List


def has_close_elements(numbers: List[float], threshold: float) -> bool:
    """Incorrect first attempt for the locked Reflexion retry fixture."""
    return False
'''


def resolve_path(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative_or_absolute(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def read_reflexion_summary(root: Path) -> str:
    path = root / "baselines" / "reflexion_generic_summary.md"
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return REFLEXION_SUMMARY_FALLBACK.strip()


def write_summary_context(task_id: str, root: Path, condition_dir: Path) -> Path:
    generic_summary = read_reflexion_summary(root)
    text = f"""# Real-Reuse Summary Baseline: {task_id}

This context is the Summary baseline for the locked Reflexion real-reuse task.
It summarizes the source-paper method only. It does not include scorer-only
answers, canonical solutions, private tests, or task labels.

{generic_summary}
"""
    path = condition_dir / f"{task_id}_summary.md"
    write_text(path, text)
    return path


def hotpotqa_task_prompt() -> str:
    titles = HOTPOTQA_EXAMPLE["context"]["title"]
    sentences = HOTPOTQA_EXAMPLE["context"]["sentences"]
    context_lines = []
    for title, paragraph_sentences in zip(titles, sentences):
        paragraph = " ".join(sentence.strip() for sentence in paragraph_sentences)
        context_lines.append(f"- {title}: {paragraph}")
    return f"""# REF-T1 Locked Task Prompt

Use the provided HotPotQA-style distractor context to answer the question.
Follow a Reflexion-style retry loop: make an attempt, read objective feedback,
write a short reflection grounded in that feedback, and produce a final answer.

Question: {HOTPOTQA_EXAMPLE['question']}

Context:
{chr(10).join(context_lines)}

Required output JSON fields:
- `first_attempt`
- `reflection`
- `final_answer`

The answer key is hidden from the model and is used only by the scorer.
"""


def prepare_ref_t1(root: Path, output_dir: Path, condition_dir: Path, papertoskill_context: Path) -> dict[str, Any]:
    question_path = output_dir / "question.json"
    context_path = output_dir / "retrieval_context_or_tool_stub.json"
    feedback_path = output_dir / "feedback_protocol.md"
    task_prompt_path = output_dir / "task_prompt.md"
    answer_key_path = output_dir / "answer_key.json"
    summary_path = write_summary_context("REF-T1", root, condition_dir)

    write_json(
        question_path,
        {
            "task_id": "REF-T1",
            "source_dataset": "hotpotqa/hotpot_qa",
            "config": "distractor",
            "split": "validation",
            "example_id": HOTPOTQA_EXAMPLE["id"],
            "question": HOTPOTQA_EXAMPLE["question"],
            "level": HOTPOTQA_EXAMPLE["level"],
            "type": HOTPOTQA_EXAMPLE["type"],
        },
    )
    write_json(
        context_path,
        {
            "task_id": "REF-T1",
            "context_kind": "hotpotqa_distractor_context",
            "context": HOTPOTQA_EXAMPLE["context"],
        },
    )
    write_text(
        feedback_path,
        """# REF-T1 Feedback Protocol

The runner must use the same two-attempt budget for Summary and PaperToSkill.
If the first attempt is not accepted by the objective checker, provide this
feedback without revealing the gold answer:

The first answer was not accepted by the objective checker. Reflect on the
provided context, identify which entities must be compared, and revise the
final answer.

No mid-run human intervention is allowed.
""",
    )
    write_text(task_prompt_path, hotpotqa_task_prompt())
    write_json(
        answer_key_path,
        {
            "task_id": "REF-T1",
            "answer": HOTPOTQA_EXAMPLE["answer"],
            "aliases": ["yes"],
            "f1_success_threshold": 1.0,
            "supporting_facts": HOTPOTQA_EXAMPLE["supporting_facts"],
            "visibility": "scorer_only",
        },
    )
    return manifest(
        root,
        "REF-T1",
        output_dir,
        summary_path,
        papertoskill_context,
        [
            (question_path, "question", "model_visible"),
            (context_path, "retrieval_context_or_tool_stub", "model_visible"),
            (feedback_path, "feedback_protocol", "model_visible"),
            (task_prompt_path, "task_prompt", "model_visible"),
            (answer_key_path, "answer_key", "scorer_only"),
            (summary_path, "summary_context", "condition_context"),
        ],
        "HotPotQA distractor validation example 5a8b57f25542995d1e6f1371.",
    )


def humaneval_task_prompt() -> str:
    return f"""# REF-T2 Locked Task Prompt

You are given a HumanEval-style programming task, an intentionally failed first
attempt, and deterministic environment feedback. Follow a Reflexion-style retry
loop: identify the failure, write a short reflection, and produce a corrected
second attempt.

Initial task:

```python
{HUMANEVAL_0['prompt'].rstrip()}
```

Failed first attempt:

```python
{FAILED_FIRST_ATTEMPT.rstrip()}
```

Environment feedback:

The first attempt failed the objective checker. It returned `False` for the
case `numbers=[1.0, 2.0, 3.9, 4.0, 5.0, 2.2]` and `threshold=0.3`, but the
expected result is `True`.

Required output:
- a short `reflection`
- a corrected Python definition for `{HUMANEVAL_0['entry_point']}`

The full test oracle and canonical solution are scorer-only assets.
"""


def prepare_ref_t2(root: Path, output_dir: Path, condition_dir: Path, papertoskill_context: Path) -> dict[str, Any]:
    initial_task_path = output_dir / "initial_task.json"
    failed_attempt_path = output_dir / "failed_first_attempt.py"
    feedback_path = output_dir / "environment_feedback.md"
    tests_path = output_dir / "tests.json"
    canonical_path = output_dir / "canonical_solution.py"
    task_prompt_path = output_dir / "task_prompt.md"
    summary_path = write_summary_context("REF-T2", root, condition_dir)

    write_json(
        initial_task_path,
        {
            "task_id": "REF-T2",
            "source_dataset": "openai/openai_humaneval",
            "split": "test",
            "humaneval_task_id": HUMANEVAL_0["task_id"],
            "entry_point": HUMANEVAL_0["entry_point"],
            "prompt": HUMANEVAL_0["prompt"],
        },
    )
    write_text(failed_attempt_path, FAILED_FIRST_ATTEMPT)
    write_text(
        feedback_path,
        """# REF-T2 Environment Feedback

The first attempt failed the objective checker. It returned `False` for
`numbers=[1.0, 2.0, 3.9, 4.0, 5.0, 2.2]` and `threshold=0.3`, but the expected
result is `True`.

Reflect on why an implementation that always returns `False` cannot satisfy a
distance-threshold task, then produce a changed second attempt.
""",
    )
    write_json(
        tests_path,
        {
            "task_id": "REF-T2",
            "humaneval_task_id": HUMANEVAL_0["task_id"],
            "entry_point": HUMANEVAL_0["entry_point"],
            "prompt": HUMANEVAL_0["prompt"],
            "test": HUMANEVAL_0["test"],
            "visibility": "scorer_only",
        },
    )
    write_text(canonical_path, HUMANEVAL_0["prompt"] + HUMANEVAL_0["canonical_solution"])
    write_text(task_prompt_path, humaneval_task_prompt())
    return manifest(
        root,
        "REF-T2",
        output_dir,
        summary_path,
        papertoskill_context,
        [
            (initial_task_path, "initial_task", "model_visible"),
            (failed_attempt_path, "failed_first_attempt", "model_visible"),
            (feedback_path, "environment_feedback", "model_visible"),
            (task_prompt_path, "task_prompt", "model_visible"),
            (tests_path, "objective_checker", "scorer_only"),
            (canonical_path, "canonical_solution", "scorer_only"),
            (summary_path, "summary_context", "condition_context"),
        ],
        "HumanEval/0 failed-attempt retry fixture.",
    )


def manifest(
    root: Path,
    task_id: str,
    output_dir: Path,
    summary_path: Path,
    papertoskill_context: Path,
    file_rows: list[tuple[Path, str, str]],
    source_snapshot: str,
) -> dict[str, Any]:
    file_entries = [
        {
            "slot": slot,
            "path": relative_or_absolute(root, path),
            "sha256": sha256_file(path),
            "visibility": visibility,
        }
        for path, slot, visibility in file_rows
    ]
    if task_id == "REF-T1":
        source_urls = [
            "https://github.com/noahshinn/reflexion",
            "https://hotpotqa.github.io/",
            "https://huggingface.co/datasets/hotpotqa/hotpot_qa",
        ]
    else:
        source_urls = [
            "https://github.com/noahshinn/reflexion",
            "https://github.com/openai/human-eval",
            "https://huggingface.co/datasets/openai/openai_humaneval",
        ]
    return {
        "schema_version": SCHEMA_VERSION,
        "benchmark_id": "papertoskill_real_reuse_v0",
        "task_id": task_id,
        "source_paper_id": "reflexion",
        "status": STATUS,
        "prepared_on": PREPARED_ON,
        "evidence_boundary": (
            "Prepared fixture assets and condition contexts for dry scoring. "
            "This manifest does not run a model, compare Summary against "
            "PaperToSkill, score downstream outputs, or claim task success."
        ),
        "source_snapshot": source_snapshot,
        "license_and_provenance": {
            "source_urls": source_urls,
            "local_use_scope": "locked small-fixture preparation for reproducible experiment setup",
            "redistribution_note": "Recheck upstream licenses before packaging these assets outside the local research repository.",
        },
        "condition_contexts": [
            {
                "condition": "summary",
                "path": relative_or_absolute(root, summary_path),
                "visibility": "model_visible",
            },
            {
                "condition": "papertoskill",
                "path": relative_or_absolute(root, papertoskill_context),
                "visibility": "model_visible",
            },
        ],
        "hidden_from_model": [
            entry["path"]
            for entry in file_entries
            if entry["visibility"] == "scorer_only"
        ],
        "asset_dir": relative_or_absolute(root, output_dir),
        "files": file_entries,
    }


def prepare(args: argparse.Namespace) -> Path:
    root = args.root.resolve()
    output_dir = resolve_path(root, args.output_dir)
    condition_dir = resolve_path(root, args.condition_dir)
    papertoskill_context = resolve_path(root, args.papertoskill_context)
    output_dir.mkdir(parents=True, exist_ok=True)
    condition_dir.mkdir(parents=True, exist_ok=True)

    task = args.task.upper()
    if task == "REF-T1":
        if args.dataset and args.dataset != "hotpotqa":
            raise ValueError("REF-T1 expects --dataset hotpotqa")
        if args.config and args.config != "distractor":
            raise ValueError("REF-T1 expects --config distractor")
        payload = prepare_ref_t1(root, output_dir, condition_dir, papertoskill_context)
    elif task == "REF-T2":
        if args.dataset and args.dataset != "humaneval":
            raise ValueError("REF-T2 expects --dataset humaneval")
        payload = prepare_ref_t2(root, output_dir, condition_dir, papertoskill_context)
    else:
        raise ValueError(f"unsupported Reflexion real-reuse task: {args.task}")

    manifest_path = output_dir / "asset_manifest.json"
    write_json(manifest_path, payload)
    return manifest_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare locked Reflexion real-reuse fixture assets.")
    parser.add_argument("--task", choices=["REF-T1", "REF-T2"], required=True)
    parser.add_argument("--dataset", choices=["hotpotqa", "humaneval"], default=None)
    parser.add_argument("--config", default=None)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--condition-dir", type=Path, default=Path("baselines/real_reuse"))
    parser.add_argument("--papertoskill-context", type=Path, default=Path("generated_skills/reflexion/SKILL.md"))
    args = parser.parse_args()

    try:
        manifest_path = prepare(args)
    except ValueError as exc:
        parser.error(str(exc))
    print(manifest_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
