# Section 06: Targeted Anomaly Review And Frozen Successor

This section isolates four byte-identical identity-control pairs that remained
discordant after both arms reached the same final protocol. It registers two
independent repeats of one byte-identical request per pair: eight DeepSeek calls
in total.

The repeats are supplementary repeatability evidence. They do not overwrite
FG3, FG4, FG5, the 1,296-row terminal overlay, or the registered Section 03
control states.

## Execution Order

```powershell
python .\targeted_successor.py build
python .\targeted_successor.py verify
# Commit and privately push the frozen registration before the next command.
python .\run_targeted_successor.py --docs-dir <local-api-document-directory>
python .\analyze_targeted_successor.py
python .\verify_targeted_results.py
```

The runner reuses the registered official DeepSeek endpoint and performs at most
five transport attempts. A completed semantic response is never replayed. An
ambiguous started dispatch without a terminal row stops for manual audit.
