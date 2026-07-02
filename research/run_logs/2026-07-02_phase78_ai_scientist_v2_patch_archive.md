# Phase 78: AI-Scientist-v2 Local Patch Archive

Date: 2026-07-02

## Purpose

Back up the local `ai-scientist-v2` source/config adaptations that supported the
bounded PaperToSkill smoke/full live-run evidence, without pushing to the
SakanaAI upstream remote.

## Evidence

- PaperToSkill repo status before this node: clean and synced at
  `38c663b feat: sync PaperToSkill evidence gates`.
- `D:\a_work\gitee\ai-scientist-v2` remote:
  `https://github.com/sakanaai/ai-scientist-v2.git`.
- The local `ai-scientist-v2` checkout has tracked modifications in LLM
  routing, BFTS launch/config, backend wrappers, and journal/best-node handling.
- Because the remote is an upstream project, the local adaptations are archived
  inside PaperToSkill instead of pushed to that remote.

## Artifact

- `external/ai_scientist_v2_patches/2026-07-02_local_coderxiaoc_bfts_adaptation.patch.zip`
- `external/ai_scientist_v2_patches/README.md`

Archive SHA256:

```text
2CEA03F4C8870FFB0F686B12320D413794BF24B983C5DCEA2BA4D96FFC1E7371
```

Decompressed patch SHA256:

```text
45523E06C70D33C0F6B2FB769CD26D3701EF397B07D02DFBF781DA85ECEF7AF1
```

## Boundary

The patch archive is a reproducibility backup for the local integration path.
It does not include raw API keys, does not include `work/` presentation
artifacts, does not include AI-Scientist-v2 experiment outputs, and does not
claim upstream-ready compatibility.

## Verification

```powershell
cd D:\a_work\gitee\ai-scientist-v2
Expand-Archive D:\a_work\gitee\PaperToSkill\external\ai_scientist_v2_patches\2026-07-02_local_coderxiaoc_bfts_adaptation.patch.zip -DestinationPath D:\a_work\gitee\PaperToSkill\external\ai_scientist_v2_patches\expanded -Force
git apply --reverse --check D:\a_work\gitee\PaperToSkill\external\ai_scientist_v2_patches\expanded\2026-07-02_local_coderxiaoc_bfts_adaptation.patch
cd D:\a_work\gitee\PaperToSkill
rg -n "sk-[A-Za-z0-9]{20,}" external\ai_scientist_v2_patches
git diff --check
rg -n "sk-[A-Za-z0-9]{20,}" .
python -c "import json; files=['results/reproducibility/goal_completion_report.json','results/reproducibility/package_report.json']; [print(f, json.load(open(f, encoding='utf-8')).get('overall_status')) for f in files]"
```

Expected status remains:

- Goal completion: `not_complete_pending_external_evidence`.
- Package: `ready_with_pending_external_evidence`.
- Remaining human-side item: fill
  `results/human_fidelity_packets/annotation_template.csv`.
