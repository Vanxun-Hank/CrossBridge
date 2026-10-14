# RAG Run Comparison

- Baseline: `eval/reports/ragas_full_20260601_180627.json`
- Candidate: `eval/reports/ragas_full_20260604_165215.json`
- Common questions: 24
- Acceptance gate: FAIL
- Improved metrics: faithfulness, id_based_context_precision, id_based_context_recall
- Regressions over 0.03: answer_relevancy

## Metric Means

| Metric | baseline | candidate | delta |
|---|---:|---:|---:|
| `faithfulness` | 0.6019 | 0.7448 | 0.1429 |
| `answer_relevancy` | 0.6673 | 0.514 | -0.1533 |
| `id_based_context_precision` | 0.4618 | 0.6167 | 0.1549 |
| `id_based_context_recall` | 0.7 | 0.7681 | 0.0681 |

## Per-Question Context Movement

| ID | scenario | metric deltas | off-target docs | missing expected docs | context changes |
|---|---|---|---|---|---|
| q01 | compliance_cross_border_payment | faithfulness:+0.1176, answer_relevancy:-0.0999, id_based_context_precision:-0.1333 | 2 -> 4 (+2/-0) | 0 -> 0 (+0/-0) | +2/-0 |
| q02 | compliance_cross_border_payment | faithfulness:+0.1460, answer_relevancy:-0.0449 | 0 -> 0 (+0/-0) | 0 -> 0 (+0/-0) | +0/-0 |
| q03 | compliance_cross_border_payment | faithfulness:-0.1313, answer_relevancy:-0.5361, id_based_context_precision:-0.3333 | 0 -> 1 (+1/-0) | 0 -> 0 (+0/-0) | +1/-0 |
| q04 | compliance_cross_border_payment | faithfulness:+0.2656, answer_relevancy:-0.0107, id_based_context_precision:-0.0500 | 3 -> 4 (+1/-0) | 2 -> 2 (+0/-0) | +1/-0 |
| q05 | sme_loan | faithfulness:+0.2727, answer_relevancy:-0.0840, id_based_context_precision:+0.5000 | 2 -> 0 (+0/-2) | 0 -> 0 (+0/-0) | +0/-2 |
| q06 | sme_loan | faithfulness:+0.0555, answer_relevancy:-0.8553, id_based_context_precision:+0.6000, id_based_context_recall:+0.2500 | 3 -> 0 (+0/-3) | 2 -> 1 (+0/-1) | +1/-3 |
| q07 | sme_loan | faithfulness:+0.2032, answer_relevancy:-0.0927, id_based_context_precision:+0.3333 | 1 -> 0 (+0/-1) | 0 -> 0 (+0/-0) | +0/-1 |
| q08 | sme_loan | faithfulness:-0.0069, answer_relevancy:-0.0754 | 2 -> 2 (+1/-1) | 0 -> 0 (+0/-0) | +1/-1 |
| q09 | gba_market_entry | faithfulness:+0.0558, answer_relevancy:-0.1064, id_based_context_precision:-0.2500 | 1 -> 3 (+2/-0) | 0 -> 0 (+0/-0) | +2/-0 |
| q10 | gba_market_entry | faithfulness:+0.4275, answer_relevancy:-0.0252, id_based_context_precision:-0.2667 | 1 -> 3 (+2/-0) | 0 -> 0 (+0/-0) | +2/-0 |
| q11 | gba_market_entry | faithfulness:+0.0418, answer_relevancy:+0.1294 | 2 -> 2 (+0/-0) | 0 -> 0 (+0/-0) | +0/-0 |
| q12 | gba_market_entry | faithfulness:-0.0678, answer_relevancy:+0.0852, id_based_context_precision:-0.0833 | 2 -> 3 (+1/-0) | 0 -> 0 (+0/-0) | +1/-0 |
| q13 | vietnam_supplier | faithfulness:+0.3943, answer_relevancy:+0.0329, id_based_context_precision:-0.1333 | 2 -> 4 (+2/-0) | 0 -> 0 (+0/-0) | +2/-0 |
| q14 | vietnam_supplier | faithfulness:-0.1471, answer_relevancy:+0.9492, id_based_context_precision:+0.2667, id_based_context_recall:+0.4000 | 2 -> 2 (+1/-1) | 4 -> 2 (+0/-2) | +3/-1 |
| q15 | vietnam_supplier | faithfulness:+0.0659, answer_relevancy:+0.8738, id_based_context_precision:-0.1333 | 2 -> 4 (+2/-0) | 2 -> 2 (+0/-0) | +2/-0 |
| q16 | remittance_compare | faithfulness:+0.0773, id_based_context_precision:+0.6667 | 2 -> 0 (+0/-2) | 0 -> 0 (+0/-0) | +0/-2 |
| q17 | remittance_compare | faithfulness:+0.0309 | 1 -> 1 (+0/-0) | 1 -> 1 (+0/-0) | +0/-0 |
| q18 | remittance_compare | faithfulness:+0.1047, answer_relevancy:-0.7252, id_based_context_precision:-0.1667 | 1 -> 2 (+1/-0) | 0 -> 0 (+0/-0) | +1/-0 |
| q19 | sme_loan | faithfulness:+0.2327, id_based_context_precision:+0.5000, id_based_context_recall:+0.2000 | 2 -> 0 (+0/-2) | 3 -> 2 (+0/-1) | +1/-2 |
| q20 | sme_loan | faithfulness:+0.2583, answer_relevancy:-0.7112, id_based_context_precision:+0.4167, id_based_context_recall:+0.3334 | 3 -> 1 (+0/-2) | 2 -> 1 (+0/-1) | +1/-2 |
| q21 | sme_loan | faithfulness:+0.1333, answer_relevancy:-0.6364, id_based_context_precision:+0.6667 | 2 -> 0 (+0/-2) | 2 -> 2 (+0/-0) | +0/-2 |
| q22 | sme_loan | answer_relevancy:-0.8707, id_based_context_precision:+0.7500 | 3 -> 0 (+0/-3) | 3 -> 3 (+0/-0) | +0/-3 |
| q23 | sme_loan | answer_relevancy:-0.7999, id_based_context_precision:+0.1500, id_based_context_recall:+0.2500 | 3 -> 3 (+0/-0) | 3 -> 2 (+0/-1) | +1/-0 |
| q24 | sme_loan | faithfulness:+0.5644, answer_relevancy:-0.0761, id_based_context_precision:+0.4167, id_based_context_recall:+0.2000 | 3 -> 1 (+0/-2) | 4 -> 3 (+0/-1) | +1/-2 |