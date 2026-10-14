# RAG Run Comparison

- Baseline: `eval/reports/ragas_full_20260601_180627.json`
- Candidate: `eval/reports/ragas_full_ids_q04_20260604_230522.json`
- Common questions: 1
- Acceptance gate: FAIL
- Improved metrics: faithfulness, id_based_context_precision, id_based_context_recall
- Regressions over 0.03: answer_relevancy

## Metric Means

| Metric | baseline | candidate | delta |
|---|---:|---:|---:|
| `faithfulness` | 0.3671 | 0.8718 | 0.5047 |
| `answer_relevancy` | 0.802 | 0.0 | -0.802 |
| `id_based_context_precision` | 0.25 | 0.75 | 0.5 |
| `id_based_context_recall` | 0.3333 | 1.0 | 0.6667 |

## Per-Question Context Movement

| ID | scenario | metric deltas | off-target docs | missing expected docs | context changes |
|---|---|---|---|---|---|
| q04 | compliance_cross_border_payment | faithfulness:+0.5047, answer_relevancy:-0.8020, id_based_context_precision:+0.5000, id_based_context_recall:+0.6667 | 3 -> 1 (+0/-2) | 2 -> 0 (+0/-2) | +2/-2 |