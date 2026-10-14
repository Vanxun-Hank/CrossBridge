# RAG Run Comparison

- Baseline: `eval/reports/ragas_full_20260601_180627.json`
- Candidate: `eval/reports/ragas_full_ids_q03-q06-q16-q17-q18-q20-q21-q22-q23_20260604_220204.json`
- Common questions: 9
- Acceptance gate: PASS
- Improved metrics: faithfulness, answer_relevancy, id_based_context_precision, id_based_context_recall
- Regressions over 0.03: none

## Metric Means

| Metric | baseline | candidate | delta |
|---|---:|---:|---:|
| `faithfulness` | 0.7064 | 0.8368 | 0.1304 |
| `answer_relevancy` | 0.5705 | 0.5773 | 0.0068 |
| `id_based_context_precision` | 0.4611 | 0.8037 | 0.3426 |
| `id_based_context_recall` | 0.5926 | 0.7222 | 0.1296 |

## Per-Question Context Movement

| ID | scenario | metric deltas | off-target docs | missing expected docs | context changes |
|---|---|---|---|---|---|
| q03 | compliance_cross_border_payment | faithfulness:-0.1625, answer_relevancy:+0.0235, id_based_context_precision:-0.3333 | 0 -> 1 (+1/-0) | 0 -> 0 (+0/-0) | +1/-0 |
| q06 | sme_loan | faithfulness:+0.0972, answer_relevancy:-0.0002, id_based_context_precision:+0.6000, id_based_context_recall:+0.5000 | 3 -> 0 (+0/-3) | 2 -> 0 (+0/-2) | +2/-3 |
| q16 | remittance_compare | faithfulness:+0.1368, answer_relevancy:+0.7811, id_based_context_precision:+0.6667 | 2 -> 0 (+0/-2) | 1 -> 0 (+0/-1) | +1/-2 |
| q17 | remittance_compare | faithfulness:+0.0909, id_based_context_precision:+0.3333, id_based_context_recall:+0.0833 | 1 -> 0 (+0/-1) | 2 -> 1 (+0/-1) | +1/-1 |
| q18 | remittance_compare | faithfulness:+0.2278, answer_relevancy:+0.0814, id_based_context_precision:-0.1667 | 1 -> 2 (+1/-0) | 0 -> 0 (+0/-0) | +1/-0 |
| q20 | sme_loan | faithfulness:+0.5833, answer_relevancy:-0.7112, id_based_context_precision:+0.4167, id_based_context_recall:+0.3334 | 3 -> 1 (+0/-2) | 2 -> 1 (+0/-1) | +1/-2 |
| q21 | sme_loan | faithfulness:-0.1667, answer_relevancy:+0.0328, id_based_context_precision:+0.6667 | 2 -> 0 (+0/-2) | 2 -> 2 (+0/-0) | +0/-2 |
| q22 | sme_loan | faithfulness:+0.3066, answer_relevancy:-0.1739, id_based_context_precision:+0.7500 | 3 -> 0 (+0/-3) | 3 -> 3 (+0/-0) | +0/-3 |
| q23 | sme_loan | faithfulness:+0.0605, answer_relevancy:+0.0276, id_based_context_precision:+0.1500, id_based_context_recall:+0.2500 | 3 -> 3 (+0/-0) | 3 -> 2 (+0/-1) | +1/-0 |