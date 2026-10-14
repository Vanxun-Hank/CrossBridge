# RAG Run Comparison

- Baseline: `eval/reports/ragas_full_20260601_180627.json`
- Candidate: `eval/reports/ragas_full_ids_q03-q06-q16-q17-q18-q20-q21-q22-q23_20260604_213827.json`
- Common questions: 8
- Acceptance gate: FAIL
- Improved metrics: faithfulness, id_based_context_precision, id_based_context_recall
- Regressions over 0.03: answer_relevancy

## Metric Means

| Metric | baseline | candidate | delta |
|---|---:|---:|---:|
| `faithfulness` | 0.681 | 0.9058 | 0.2248 |
| `answer_relevancy` | 0.6419 | 0.5738 | -0.0681 |
| `id_based_context_precision` | 0.4354 | 0.7792 | 0.3438 |
| `id_based_context_recall` | 0.5833 | 0.7188 | 0.1355 |

## Per-Question Context Movement

| ID | scenario | metric deltas | off-target docs | missing expected docs | context changes |
|---|---|---|---|---|---|
| q03 | compliance_cross_border_payment | faithfulness:+0.0968, answer_relevancy:-0.0298, id_based_context_precision:-0.3333 | 0 -> 1 (+1/-0) | 0 -> 0 (+0/-0) | +1/-0 |
| q06 | sme_loan | faithfulness:+0.0972, answer_relevancy:+0.0005, id_based_context_precision:+0.6000, id_based_context_recall:+0.5000 | 3 -> 0 (+0/-3) | 2 -> 0 (+0/-2) | +2/-3 |
| q16 | remittance_compare | faithfulness:+0.3009, answer_relevancy:+0.7802, id_based_context_precision:+0.6667 | 2 -> 0 (+0/-2) | 1 -> 0 (+0/-1) | +1/-2 |
| q18 | remittance_compare | faithfulness:+0.2110, answer_relevancy:+0.0735, id_based_context_precision:-0.1667 | 1 -> 2 (+1/-0) | 0 -> 0 (+0/-0) | +1/-0 |
| q20 | sme_loan | faithfulness:+0.5833, answer_relevancy:-0.7112, id_based_context_precision:+0.4167, id_based_context_recall:+0.3334 | 3 -> 1 (+0/-2) | 2 -> 1 (+0/-1) | +1/-2 |
| q21 | sme_loan | faithfulness:+0.1333, answer_relevancy:-0.6364, id_based_context_precision:+0.6667 | 2 -> 0 (+0/-2) | 2 -> 2 (+0/-0) | +0/-2 |
| q22 | sme_loan | faithfulness:+0.2566, answer_relevancy:-0.1745, id_based_context_precision:+0.7500 | 3 -> 0 (+0/-3) | 3 -> 3 (+0/-0) | +0/-3 |
| q23 | sme_loan | faithfulness:+0.1188, answer_relevancy:+0.1531, id_based_context_precision:+0.1500, id_based_context_recall:+0.2500 | 3 -> 3 (+0/-0) | 3 -> 2 (+0/-1) | +1/-0 |