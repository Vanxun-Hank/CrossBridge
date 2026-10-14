# RAG Run Comparison

- Baseline: `eval/reports/ragas_full_20260601_180627.json`
- Candidate: `eval/reports/ragas_full_ids_q17_20260604_214023.json`
- Common questions: 1
- Acceptance gate: FAIL
- Improved metrics: none
- Regressions over 0.03: faithfulness

## Metric Means

| Metric | baseline | candidate | delta |
|---|---:|---:|---:|
| `faithfulness` | 0.9091 | 0.75 | -0.1591 |
| `answer_relevancy` | 0.0 | 0.0 | 0.0 |
| `id_based_context_precision` | 0.6667 | 0.6667 | 0.0 |
| `id_based_context_recall` | 0.6667 | 0.6667 | 0.0 |

## Per-Question Context Movement

| ID | scenario | metric deltas | off-target docs | missing expected docs | context changes |
|---|---|---|---|---|---|
| q17 | remittance_compare | faithfulness:-0.1591 | 1 -> 1 (+0/-0) | 1 -> 1 (+0/-0) | +0/-0 |