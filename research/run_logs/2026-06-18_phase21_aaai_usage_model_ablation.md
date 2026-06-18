# Phase 21: AAAI Package, Usage Examples, and Model-Ablation Prompts

## Actions

- Downloaded the official AAAI-27 author kit from `https://aaai.org/authorkit27/`.
- Extracted the author kit during setup and retained the original zip plus
  build-local `aaai2027.sty` and `aaai2027.bst`.
- Recorded template provenance and SHA256 in `paper/aaai/README.md`.
- Added an AAAI-formatted PaperToSkill draft:
  `paper/aaai/papertoskill_aaai2027.tex`.
- Added LaTeX table fragments and bibliography:
  `paper/aaai/papertoskill_tables.tex` and
  `paper/aaai/papertoskill_refs.bib`.
- Added usage examples under `examples/usage/` for:
  - loading a generated skill in a Codex-style harness;
  - converting extracted text to an auto-note scaffold and skill;
  - running the Claude/GPT-family/DeepSeek model-ablation protocol.
- Added `benchmarks/model_ablation_v0.json` and
  `scripts/build_model_ablation_prompts.py`.
- Generated six model-ablation prompt packets under
  `results/model_ablation_prompts/v0/`.
- Extended `scripts/check_reproducibility_package.py` to check the AAAI package,
  usage examples, model-ablation prompt index, model slots, and pending response
  files.

## Results

- AAAI author kit:
  - source URL: `https://aaai.org/authorkit27/`
  - downloaded file: `paper/aaai/AuthorKit27.zip`
  - SHA256: `E28C6AC9BC6EB3B4E2D849547D2CEFB5162610EE39D0A12E0DC62D1126B44A7D`
  - main style file: `paper/aaai/aaai2027.sty`
- Model-ablation prompt grid:
  - model slots: `claude_opus_4_8`, `gpt_5_5_or_gpt_family`,
    `deepseek_followup_slot`;
  - context cases: Toolformer curated-skill usage and AIDE auto-skill usage;
  - prompt packets: 6;
  - response files: pending.

## Evidence Boundary

- The AAAI paper package is prepared but not yet a submission-final manuscript.
- The prompt grid is a runnable protocol, not completed Claude/GPT/DeepSeek
  ablation evidence.
- GPT 5.5 remains a requested GPT-family alias that must be verified against
  the provider model list before a live run is claimed.
- DeepSeek is intentionally a follow-up slot for the user to fill with endpoint,
  model alias, and credentials later.

## Verification Planned

- `python -m unittest discover -s tests -v`
- `python scripts\check_reproducibility_package.py --output-json results\reproducibility\package_report.json --output-md results\reproducibility\package_report.md --strict`
- `git diff --check`
- secret scan for raw API keys
