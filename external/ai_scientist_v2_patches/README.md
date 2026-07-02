# AI-Scientist-v2 Local Patch Archive

This directory backs up local `ai-scientist-v2` adaptations that were required
to run the bounded PaperToSkill Phase 76 smoke/full live-run evidence.

The upstream `ai-scientist-v2` checkout points at
`https://github.com/sakanaai/ai-scientist-v2.git`, so these local project
adaptations are not pushed to that upstream remote. They are archived here so
the PaperToSkill GitHub backup contains enough information to reproduce the
local integration state.

## Patch

- Archive file:
  `2026-07-02_local_coderxiaoc_bfts_adaptation.patch.zip`
- Source workspace:
  `D:\a_work\gitee\ai-scientist-v2`
- Source upstream commit:
  `96bd516 Merge pull request #78 from conglu1997/main`
- Archive SHA256:
  `2CEA03F4C8870FFB0F686B12320D413794BF24B983C5DCEA2BA4D96FFC1E7371`
- Decompressed patch SHA256:
  `45523E06C70D33C0F6B2FB769CD26D3701EF397B07D02DFBF781DA85ECEF7AF1`

## Scope

The patch includes tracked source/config changes only:

- OpenAI-compatible and Anthropic/coderxiaoc routing helpers.
- Responses API fallback for GPT-family models.
- JSON fallback handling for tool/function-like calls.
- Laptop-bounded BFTS defaults for the PaperToSkill run.
- Safer dry-run, cleanup, PDF-review, and best-node handling changes.

It intentionally excludes:

- Raw API keys and local environment values.
- `MEMORY_*.md` files from the upstream checkout.
- `work/` presentation build artifacts.
- AI-Scientist-v2 experiment outputs, which are referenced from PaperToSkill
  reports instead of copied here.

## Apply

From a clean `ai-scientist-v2` checkout at the source upstream commit:

```powershell
Expand-Archive D:\a_work\gitee\PaperToSkill\external\ai_scientist_v2_patches\2026-07-02_local_coderxiaoc_bfts_adaptation.patch.zip -DestinationPath D:\a_work\gitee\PaperToSkill\external\ai_scientist_v2_patches\expanded -Force
git apply D:\a_work\gitee\PaperToSkill\external\ai_scientist_v2_patches\expanded\2026-07-02_local_coderxiaoc_bfts_adaptation.patch
```

Then set credentials through local environment variables only. Do not commit raw
keys.

## Boundary

This archive is a reproducibility backup for the local PaperToSkill evidence
path. It is not an upstream contribution, not a claim of broad AI-Scientist-v2
compatibility, and not evidence of human semantic fidelity.
