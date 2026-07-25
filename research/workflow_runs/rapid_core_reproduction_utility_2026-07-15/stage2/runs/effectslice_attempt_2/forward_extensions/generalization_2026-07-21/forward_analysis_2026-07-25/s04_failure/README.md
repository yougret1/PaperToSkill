# Section 04: Failure Decomposition

This section separates three concepts that must not be conflated:

1. the original technical diagnosis used to route an FG3 row;
2. the retained or successor source supplying its final result; and
3. the final experimental endpoint after all forward repairs.

## Reproduce

```powershell
python .\extract_failure_evidence.py
python .\analyze_failure_decomposition.py
python .\verify_failure_decomposition.py --require-source-extraction
```

The extractor verifies all 1,296 terminal result-source hashes and commits the
aggregate two-bit scorer vectors needed for portable replay. The verifier reruns
the analysis in a temporary directory and compares every output byte for byte.

## Boundary

`response_format`, `integrity_or_digest`, `payload_input_interface`,
`provider_availability`, and `exact_output_contract` are routing or provenance
labels. They are not experiment stages and not final model-quality outcomes.

`no_patch` is not a registered cross-domain endpoint and is not identifiable
from the common two-bit scorer vector, so this section does not fabricate a
no-patch count.
