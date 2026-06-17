# Paper-Ready Result Tables

Evidence boundary: these tables aggregate existing deterministic/offline evaluation JSON. They are not live cross-harness agent task results.

## Main Results

| Paper | Skill rubric | Skill coverage | Generic summary coverage | Abstract-only coverage | Skill vs generic delta | Skill vs abstract delta | Transfer readiness | Source support rate | Skill words |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AI Scientist-v2 | 20/20 | 7.867/9 | 1.733/9 | 1.2/9 | 6.134 | 6.667 | 10/10 | 0.938 | 782 |
| Reflexion | 20/20 | 8.267/9 | 3.483/9 | 2.533/9 | 4.784 | 5.734 | 10/10 | 1 | 479 |
| AIDE | 20/20 | 9.1/10 | 1.916/10 | 1.333/10 | 7.184 | 7.767 | 10/10 | 1 | 927 |
| Toolformer | 20/20 | 8.9/10 | 2.5/10 | 1.534/10 | 6.4 | 7.366 | 10/10 | 1 | 943 |

## Transfer Ablation

| Paper | Variant | Average readiness | Codex-style readiness | Claude-style readiness | Word count | Dropped sections |
| --- | --- | --- | --- | --- | --- | --- |
| AI Scientist-v2 | Full skill | 10/10 | 10/10 | 10/10 | 782 | none |
| AI Scientist-v2 | No transfer notes | 7.6/10 | 7.6/10 | 7.6/10 | 738 | Transfer Notes |
| AI Scientist-v2 | Generic summary | 1.2/10 | 1.2/10 | 1.2/10 | 154 | none |
| Reflexion | Full skill | 10/10 | 10/10 | 10/10 | 479 | none |
| Reflexion | No transfer notes | 7.6/10 | 7.6/10 | 7.6/10 | 435 | Transfer Notes |
| Reflexion | Generic summary | 2.25/10 | 2.25/10 | 2.25/10 | 111 | none |
| AIDE | Full skill | 10/10 | 10/10 | 10/10 | 927 | none |
| AIDE | No transfer notes | 7.6/10 | 7.6/10 | 7.6/10 | 883 | Transfer Notes |
| AIDE | Generic summary | 1.5/10 | 1.5/10 | 1.5/10 | 89 | none |
| Toolformer | Full skill | 10/10 | 10/10 | 10/10 | 943 | none |
| Toolformer | No transfer notes | 7.6/10 | 7.6/10 | 7.6/10 | 899 | Transfer Notes |
| Toolformer | Generic summary | 1.45/10 | 1.45/10 | 1.45/10 | 78 | none |

## Compactness And Source Grounding

| Paper | Skill words | Compactness budget | Compactness score | Source anchors | Supported spans | Weak spans | Unsupported spans | Invalid ranges | Source support rate | Unsupported instruction rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AI Scientist-v2 | 782 | 1200 | 2/2 | 16 | 15 | 1 | 0 | 0 | 0.938 | 0.2 |
| Reflexion | 479 | 1200 | 2/2 | 12 | 11 | 0 | 0 | 0 | 1 | n/a |
| AIDE | 927 | 1200 | 2/2 | 22 | 21 | 0 | 0 | 0 | 1 | n/a |
| Toolformer | 943 | 1200 | 2/2 | 23 | 22 | 0 | 0 | 0 | 1 | n/a |
