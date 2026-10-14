# RAG Run Comparison

- Baseline: `eval/reports/ragas_full_20260601_180627.json`
- Candidate: `eval/reports/ragas_full_ids_q19_20260604_225628.json`
- Common questions: 1
- Acceptance gate: FAIL
- Improved metrics: faithfulness, id_based_context_precision, id_based_context_recall
- Regressions over 0.03: answer_relevancy

## Metric Means

| Metric | baseline | candidate | delta |
|---|---:|---:|---:|
| `faithfulness` | 0.5102 | 0.88 | 0.3698 |
| `answer_relevancy` | 0.9973 | 0.0 | -0.9973 |
| `id_based_context_precision` | 0.5 | 0.8 | 0.3 |
| `id_based_context_recall` | 0.4 | 0.8 | 0.4 |

## Per-Question Context Movement

| ID | scenario | metric deltas | off-target docs | missing expected docs | context changes |
|---|---|---|---|---|---|
| q19 | sme_loan | faithfulness:+0.3698, answer_relevancy:-0.9973, id_based_context_precision:+0.3000, id_based_context_recall:+0.4000 | 2 -> 1 (+1/-2) | 3 -> 1 (+0/-2) | +3/-2 |