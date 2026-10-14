# RAG Run Comparison

- Baseline: `eval/reports/ragas_full_20260601_180627.json`
- Candidate: `eval/reports/ragas_full_ids_q20-q22_20260604_223323.json`
- Common questions: 2
- Acceptance gate: FAIL
- Improved metrics: faithfulness, id_based_context_precision, id_based_context_recall
- Regressions over 0.03: answer_relevancy

## Metric Means

| Metric | baseline | candidate | delta |
|---|---:|---:|---:|
| `faithfulness` | 0.4051 | 0.75 | 0.3449 |
| `answer_relevancy` | 0.791 | 0.0 | -0.791 |
| `id_based_context_precision` | 0.25 | 0.6 | 0.35 |
| `id_based_context_recall` | 0.2916 | 0.875 | 0.5834 |

## Per-Question Context Movement

| ID | scenario | metric deltas | off-target docs | missing expected docs | context changes |
|---|---|---|---|---|---|
| q20 | sme_loan | faithfulness:+0.5378, answer_relevancy:-0.7112, id_based_context_precision:+0.3500, id_based_context_recall:+0.6667 | 3 -> 2 (+1/-2) | 2 -> 0 (+0/-2) | +3/-2 |
| q22 | sme_loan | faithfulness:+0.1521, answer_relevancy:-0.8707, id_based_context_precision:+0.3500, id_based_context_recall:+0.5000 | 3 -> 2 (+0/-1) | 3 -> 1 (+0/-2) | +2/-1 |