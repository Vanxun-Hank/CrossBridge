# RAG Run Comparison

- Baseline: `eval/reports/ragas_full_20260601_180627.json`
- Candidate: `eval/reports/ragas_full_ids_q22_20260604_231548.json`
- Common questions: 1
- Acceptance gate: FAIL
- Improved metrics: faithfulness, id_based_context_precision, id_based_context_recall
- Regressions over 0.03: answer_relevancy

## Metric Means

| Metric | baseline | candidate | delta |
|---|---:|---:|---:|
| `faithfulness` | 0.3934 | 0.8378 | 0.4444 |
| `answer_relevancy` | 0.8707 | 0.0 | -0.8707 |
| `id_based_context_precision` | 0.25 | 1.0 | 0.75 |
| `id_based_context_recall` | 0.25 | 1.0 | 0.75 |

## Per-Question Context Movement

| ID | scenario | metric deltas | off-target docs | missing expected docs | context changes |
|---|---|---|---|---|---|
| q22 | sme_loan | faithfulness:+0.4444, answer_relevancy:-0.8707, id_based_context_precision:+0.7500, id_based_context_recall:+0.7500 | 3 -> 0 (+0/-3) | 3 -> 0 (+0/-3) | +3/-3 |