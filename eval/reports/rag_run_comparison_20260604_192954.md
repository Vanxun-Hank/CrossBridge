# RAG Run Comparison

- Baseline: `eval/reports/ragas_full_20260601_180627.json`
- Candidate: `eval/reports/ragas_full_ids_q06_20260604_192939.json`
- Common questions: 1
- Acceptance gate: FAIL
- Improved metrics: faithfulness, id_based_context_precision, id_based_context_recall
- Regressions over 0.03: answer_relevancy

## Metric Means

| Metric | baseline | candidate | delta |
|---|---:|---:|---:|
| `faithfulness` | 0.7778 | 1.0 | 0.2222 |
| `answer_relevancy` | 0.8553 | 0.0 | -0.8553 |
| `id_based_context_precision` | 0.4 | 1.0 | 0.6 |
| `id_based_context_recall` | 0.5 | 1.0 | 0.5 |

## Per-Question Context Movement

| ID | scenario | metric deltas | off-target docs | missing expected docs | context changes |
|---|---|---|---|---|---|
| q06 | sme_loan | faithfulness:+0.2222, answer_relevancy:-0.8553, id_based_context_precision:+0.6000, id_based_context_recall:+0.5000 | 3 -> 0 (+0/-3) | 2 -> 0 (+0/-2) | +2/-3 |