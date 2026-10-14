# RAG Run Comparison

- Baseline: `eval/reports/ragas_full_20260601_180627.json`
- Candidate: `eval/reports/ragas_full_ids_q04-q20-q22_20260604_224432.json`
- Common questions: 3
- Acceptance gate: FAIL
- Improved metrics: faithfulness, id_based_context_precision, id_based_context_recall
- Regressions over 0.03: answer_relevancy

## Metric Means

| Metric | baseline | candidate | delta |
|---|---:|---:|---:|
| `faithfulness` | 0.3924 | 0.8119 | 0.4195 |
| `answer_relevancy` | 0.7946 | 0.0 | -0.7946 |
| `id_based_context_precision` | 0.25 | 0.6 | 0.35 |
| `id_based_context_recall` | 0.3055 | 0.9167 | 0.6112 |

## Per-Question Context Movement

| ID | scenario | metric deltas | off-target docs | missing expected docs | context changes |
|---|---|---|---|---|---|
| q04 | compliance_cross_border_payment | faithfulness:+0.3829, answer_relevancy:-0.8020, id_based_context_precision:+0.3500, id_based_context_recall:+0.6667 | 3 -> 2 (+0/-1) | 2 -> 0 (+0/-2) | +2/-1 |
| q20 | sme_loan | faithfulness:+0.5833, answer_relevancy:-0.7112, id_based_context_precision:+0.3500, id_based_context_recall:+0.6667 | 3 -> 2 (+1/-2) | 2 -> 0 (+0/-2) | +3/-2 |
| q22 | sme_loan | faithfulness:+0.2923, answer_relevancy:-0.8707, id_based_context_precision:+0.3500, id_based_context_recall:+0.5000 | 3 -> 2 (+0/-1) | 3 -> 1 (+0/-2) | +2/-1 |