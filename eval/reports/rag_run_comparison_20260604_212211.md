# RAG Run Comparison

- Baseline: `eval/reports/ragas_full_20260601_180627.json`
- Candidate: `eval/reports/ragas_full_ids_q06_20260604_212157.json`
- Common questions: 1
- Acceptance gate: PASS
- Improved metrics: faithfulness, answer_relevancy, id_based_context_precision, id_based_context_recall
- Regressions over 0.03: none

## Metric Means

| Metric | baseline | candidate | delta |
|---|---:|---:|---:|
| `faithfulness` | 0.7778 | 0.875 | 0.0972 |
| `answer_relevancy` | 0.8553 | 0.8685 | 0.0132 |
| `id_based_context_precision` | 0.4 | 1.0 | 0.6 |
| `id_based_context_recall` | 0.5 | 1.0 | 0.5 |

## Per-Question Context Movement

| ID | scenario | metric deltas | off-target docs | missing expected docs | context changes |
|---|---|---|---|---|---|
| q06 | sme_loan | faithfulness:+0.0972, answer_relevancy:+0.0132, id_based_context_precision:+0.6000, id_based_context_recall:+0.5000 | 3 -> 0 (+0/-3) | 2 -> 0 (+0/-2) | +2/-3 |