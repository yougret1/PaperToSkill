# Usage Example: Extracted Text to Auto Note to Skill

## Goal

Use extracted paper text to create an auditable note scaffold, then convert that
note into a PaperToSkill skill.

## Example Command Sequence

```powershell
python scripts\papertoskill_note_from_text.py `
  --source papers\extracted\aide.txt `
  --output papers\auto_notes\aide_auto_note.md `
  --paper-id aide_auto `
  --title "AIDE: AI-Driven Exploration in the Space of Code" `
  --profile aide `
  --report results\evaluations\aide_auto_note_scaffold_v0.json

python scripts\papertoskill_extract.py `
  --source papers\auto_notes\aide_auto_note.md `
  --output generated_skills\aide_auto `
  --name aide-auto-paper-skill

python scripts\evaluate_skill.py `
  --skill generated_skills\aide_auto\SKILL.md `
  --rubric benchmarks\rubric_aide_v0.json `
  --output results\evaluations\aide_auto_rubric_v0.json
```

## Audit Checklist

- Confirm selected line windows point to the intended paper regions.
- Confirm the generated skill keeps method, validation, failure, and transfer
  sections.
- Run context, transfer, and source-span evaluations before claiming readiness.
- Treat the auto note as a scaffold requiring review, not as arbitrary-PDF
  automation.
