# RAG Run Comparison

- Baseline: `/Users/zhangxun/Documents/BOCHK/eval/reports/ragas_full_20260601_180627.json`
- Candidate: `/Users/zhangxun/Documents/BOCHK/eval/reports/ragas_full_20260601_180627.json`
- Common questions: 24
- Acceptance gate: FAIL
- Improved metrics: none
- Regressions over 0.03: none

## Metric Means

| Metric | baseline | candidate | delta |
|---|---:|---:|---:|
| `faithfulness` | 0.6019 | 0.6019 | 0.0 |
| `answer_relevancy` | 0.6673 | 0.6673 | 0.0 |
| `id_based_context_precision` | 0.4618 | 0.4618 | 0.0 |
| `id_based_context_recall` | 0.7 | 0.7 | 0.0 |

## Per-Question Context Movement

| ID | scenario | metric deltas | off-target docs | missing expected docs | context changes |
|---|---|---|---|---|---|
| q01 | compliance_cross_border_payment | 0 | 2 -> 2 (+0/-0) | 0 -> 0 (+0/-0) | +0/-0 |
| q02 | compliance_cross_border_payment | 0 | 0 -> 0 (+0/-0) | 0 -> 0 (+0/-0) | +0/-0 |
| q03 | compliance_cross_border_payment | 0 | 0 -> 0 (+0/-0) | 0 -> 0 (+0/-0) | +0/-0 |
| q04 | compliance_cross_border_payment | 0 | 3 -> 3 (+0/-0) | 2 -> 2 (+0/-0) | +0/-0 |
| q05 | sme_loan | 0 | 2 -> 2 (+0/-0) | 0 -> 0 (+0/-0) | +0/-0 |
| q06 | sme_loan | 0 | 3 -> 3 (+0/-0) | 2 -> 2 (+0/-0) | +0/-0 |
| q07 | sme_loan | 0 | 1 -> 1 (+0/-0) | 0 -> 0 (+0/-0) | +0/-0 |
| q08 | sme_loan | 0 | 2 -> 2 (+0/-0) | 0 -> 0 (+0/-0) | +0/-0 |
| q09 | gba_market_entry | 0 | 1 -> 1 (+0/-0) | 0 -> 0 (+0/-0) | +0/-0 |
| q10 | gba_market_entry | 0 | 1 -> 1 (+0/-0) | 0 -> 0 (+0/-0) | +0/-0 |
| q11 | gba_market_entry | 0 | 2 -> 2 (+0/-0) | 0 -> 0 (+0/-0) | +0/-0 |
| q12 | gba_market_entry | 0 | 2 -> 2 (+0/-0) | 0 -> 0 (+0/-0) | +0/-0 |
| q13 | vietnam_supplier | 0 | 2 -> 2 (+0/-0) | 0 -> 0 (+0/-0) | +0/-0 |
| q14 | vietnam_supplier | 0 | 2 -> 2 (+0/-0) | 4 -> 4 (+0/-0) | +0/-0 |
| q15 | vietnam_supplier | 0 | 2 -> 2 (+0/-0) | 2 -> 2 (+0/-0) | +0/-0 |
| q16 | remittance_compare | 0 | 2 -> 2 (+0/-0) | 0 -> 0 (+0/-0) | +0/-0 |
| q17 | remittance_compare | 0 | 1 -> 1 (+0/-0) | 1 -> 1 (+0/-0) | +0/-0 |
| q18 | remittance_compare | 0 | 1 -> 1 (+0/-0) | 0 -> 0 (+0/-0) | +0/-0 |
| q19 | sme_loan | 0 | 2 -> 2 (+0/-0) | 3 -> 3 (+0/-0) | +0/-0 |
| q20 | sme_loan | 0 | 3 -> 3 (+0/-0) | 2 -> 2 (+0/-0) | +0/-0 |
| q21 | sme_loan | 0 | 2 -> 2 (+0/-0) | 2 -> 2 (+0/-0) | +0/-0 |
| q22 | sme_loan | 0 | 3 -> 3 (+0/-0) | 3 -> 3 (+0/-0) | +0/-0 |
| q23 | sme_loan | 0 | 3 -> 3 (+0/-0) | 3 -> 3 (+0/-0) | +0/-0 |
| q24 | sme_loan | 0 | 3 -> 3 (+0/-0) | 4 -> 4 (+0/-0) | +0/-0 |