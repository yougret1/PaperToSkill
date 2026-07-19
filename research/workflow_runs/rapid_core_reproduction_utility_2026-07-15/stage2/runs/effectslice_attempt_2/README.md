# EffectSlice Attempt 2

This attempt implements the PAC violation-rate protocol described in
`../../pac_protocol_design.md`.

It is isolated from `effectslice_attempt_1`. Copied source and test files are
software scaffolding only. No readiness report, experiment summary, scored row,
or scientific result from attempt 1 is inherited as attempt-2 evidence.

## Confirmation V3 Freeze And Execution

Confirmation V3 is a write-once, final-score-only DeepSeek V3.2 run. The
registered transport uses `https://api.deepseek.com`, model alias
`deepseek-v4-flash`, direct HTTPS with environment proxies disabled, a
240-second timeout, at most five same-lineage attempts, a two-second retry
delay, and at most two parallel workers. The API key is read only from
`EFFECTSLICE_DEEPSEEK_API_KEY` and is never included in public configuration or
result artifacts.

Run these commands from this directory, in order, only after the implementation
commit is final:

```powershell
python .\build_confirmation_v3.py --control identity --output-dir .\artifacts\toolformer_filter\confirmation_v3\identity --require-complete-bindings
python .\build_confirmation_v3.py --control planted --output-dir .\artifacts\toolformer_filter\confirmation_v3\planted --require-complete-bindings
python .\register_confirmation_v3.py build-preregistration
python .\evidence_ledger_v3.py build --root . --source .\artifacts\toolformer_filter\confirmation_v3\identity --source .\artifacts\toolformer_filter\confirmation_v3\planted --source .\artifacts\toolformer_filter\confirmation_v3\preregistration.json --ledger-path .\derived\confirmation_v3\evidence_ledger\preregistration\ledger.json --phase preregistration --evidence-boundary registered_final_only_confirmation_v3
python .\register_confirmation_v3.py build-anchor
python .\register_confirmation_v3.py audit
python .\run_confirmation_v3.py --max-workers 2
python .\analyze_confirmation_v3.py
```

The scheduler refuses missing or changed preregistration, ledger, anchor, code
bindings, family paths, output roots, progress path, provider settings, and
unregistered output entries. An interrupted run may audit with
`--allow-execution-started`, but it may only preserve or resume the same frozen
schedule; failed registered blocks remain in the denominator and are not
replaced.

