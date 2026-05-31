# BOCHK 官方产品补全差异报告

- 生成时间：`2026-05-31T05:00:29.730698+00:00`
- 抽取模式：`deterministic_official_text_fallback`
- 产品数量：`9` → `26`（新增 `17`）
- 规则：仅写入官方页面明确出现的内容；示例、可能值及估算值不写入筛选字段。

## 新增产品

- `bochk_lc_issuance`：信用证开立
- `bochk_back_to_back_lc`：背对背信用证
- `bochk_import_bills_collection`：进口托收
- `bochk_shipping_guarantee`：提货担保
- `bochk_lc_advising_confirmation`：信用证通知及保兑
- `bochk_lc_transfer`：信用证转让
- `bochk_export_bills_collection`：出口托收
- `bochk_export_bills_advance`：出口押汇
- `bochk_export_bills_lc_collection`：信用证项下出口汇票托收
- `bochk_export_bills_lc_negotiation_discount`：信用证项下出口汇票议付／贴现
- `bochk_guarantee_bond_standby_lc`：担保／保函／备用信用证
- `bochk_forfaiting`：福费廷
- `bochk_factoring`：保理
- `bochk_foreign_exchange_services`：外汇服务
- `bochk_supply_chain_invoice_payment`：供应链发票付款
- `bochk_supply_chain_pre_shipment_financing`：供应链装运前融资
- `bochk_supply_chain_document_checking`：供应链审单服务

## null → 有值

- `bochk_small_business_loan_unsecured.interest_rate_text`：`促销利率：网上渠道申请可享年利率减 25 个基点（截止 2026-03-31），以 BOCHK 最新公告为准`
- `bochk_sfgs_80_guarantee_product.interest_rate_text`：`促销利率：网上渠道申请可享年利率减 25 个基点（截止 2026-06-30），以 BOCHK 最新公告为准；标准利率以 BOCHK 最终审批为准`

## 仍为 null

- `bochk_small_business_loan_unsecured`：`loan_limit_min_hkd`, `required_documents`。原因：官方页面未明确列明。
- `bochk_sfgs_80_guarantee_product`：`loan_limit_min_hkd`, `required_documents`。原因：官方页面未明确列明。
- `bochk_import_loan`：`loan_limit_min_hkd`, `loan_limit_max_hkd`, `loan_limit_text`, `interest_rate_text`, `tenor_text`, `repayment_method_text`, `required_documents`, `application_thresholds`。原因：官方页面未明确列明。
- `bochk_import_invoice_financing`：`loan_limit_min_hkd`, `loan_limit_max_hkd`, `loan_limit_text`, `interest_rate_text`, `tenor_text`, `repayment_method_text`, `application_thresholds`。原因：官方页面未明确列明。
- `bochk_trust_receipt_facilities`：`loan_limit_min_hkd`, `loan_limit_max_hkd`, `loan_limit_text`, `interest_rate_text`, `tenor_text`, `required_documents`, `application_thresholds`。原因：官方页面未明确列明。
- `bochk_packing_loan`：`loan_limit_min_hkd`, `loan_limit_max_hkd`, `loan_limit_text`, `interest_rate_text`, `tenor_text`, `repayment_method_text`, `application_thresholds`。原因：官方页面未明确列明。
- `bochk_pre_shipment_financing`：`loan_limit_min_hkd`, `loan_limit_max_hkd`, `loan_limit_text`, `interest_rate_text`, `tenor_text`, `application_thresholds`。原因：官方页面未明确列明。
- `bochk_export_invoice_discounting`：`loan_limit_min_hkd`, `loan_limit_max_hkd`, `loan_limit_text`, `interest_rate_text`, `tenor_text`, `repayment_method_text`, `application_thresholds`。原因：官方页面未明确列明。
- `bochk_supply_chain_finance_solution`：`loan_limit_min_hkd`, `loan_limit_max_hkd`, `loan_limit_text`, `interest_rate_text`, `tenor_text`, `repayment_method_text`, `required_documents`, `application_thresholds`。原因：官方页面未明确列明。
- `bochk_lc_issuance`：`loan_limit_min_hkd`, `loan_limit_max_hkd`, `loan_limit_text`, `interest_rate_text`, `tenor_text`, `repayment_method_text`, `required_documents`, `application_thresholds`。原因：官方页面未明确列明。
- `bochk_back_to_back_lc`：`loan_limit_min_hkd`, `loan_limit_max_hkd`, `loan_limit_text`, `interest_rate_text`, `tenor_text`, `repayment_method_text`, `application_thresholds`。原因：官方页面未明确列明。
- `bochk_import_bills_collection`：`loan_limit_min_hkd`, `loan_limit_max_hkd`, `loan_limit_text`, `interest_rate_text`, `tenor_text`, `required_documents`, `application_thresholds`。原因：官方页面未明确列明。
- `bochk_shipping_guarantee`：`loan_limit_min_hkd`, `loan_limit_max_hkd`, `loan_limit_text`, `interest_rate_text`, `tenor_text`, `repayment_method_text`, `required_documents`, `application_thresholds`。原因：官方页面未明确列明。
- `bochk_lc_advising_confirmation`：`loan_limit_min_hkd`, `loan_limit_max_hkd`, `loan_limit_text`, `interest_rate_text`, `tenor_text`, `repayment_method_text`, `required_documents`, `application_thresholds`。原因：官方页面未明确列明。
- `bochk_lc_transfer`：`loan_limit_min_hkd`, `loan_limit_max_hkd`, `loan_limit_text`, `interest_rate_text`, `tenor_text`, `repayment_method_text`, `application_thresholds`。原因：官方页面未明确列明。
- `bochk_export_bills_collection`：`loan_limit_min_hkd`, `loan_limit_max_hkd`, `loan_limit_text`, `interest_rate_text`, `tenor_text`, `application_thresholds`。原因：官方页面未明确列明。
- `bochk_export_bills_advance`：`loan_limit_min_hkd`, `loan_limit_max_hkd`, `loan_limit_text`, `interest_rate_text`, `tenor_text`, `repayment_method_text`, `application_thresholds`。原因：官方页面未明确列明。
- `bochk_export_bills_lc_collection`：`loan_limit_min_hkd`, `loan_limit_max_hkd`, `loan_limit_text`, `interest_rate_text`, `tenor_text`, `repayment_method_text`, `application_thresholds`。原因：官方页面未明确列明。
- `bochk_export_bills_lc_negotiation_discount`：`loan_limit_min_hkd`, `loan_limit_max_hkd`, `loan_limit_text`, `interest_rate_text`, `tenor_text`, `repayment_method_text`, `application_thresholds`。原因：官方页面未明确列明。
- `bochk_guarantee_bond_standby_lc`：`loan_limit_min_hkd`, `loan_limit_max_hkd`, `loan_limit_text`, `interest_rate_text`, `tenor_text`, `repayment_method_text`, `required_documents`, `application_thresholds`。原因：官方页面未明确列明。
- `bochk_forfaiting`：`loan_limit_min_hkd`, `loan_limit_max_hkd`, `loan_limit_text`, `interest_rate_text`, `tenor_text`, `repayment_method_text`, `required_documents`, `application_thresholds`。原因：官方页面未明确列明。
- `bochk_factoring`：`loan_limit_min_hkd`, `loan_limit_max_hkd`, `loan_limit_text`, `interest_rate_text`, `tenor_text`, `repayment_method_text`, `required_documents`, `application_thresholds`。原因：官方页面未明确列明。
- `bochk_foreign_exchange_services`：`loan_limit_min_hkd`, `loan_limit_max_hkd`, `loan_limit_text`, `interest_rate_text`, `tenor_text`, `repayment_method_text`, `required_documents`, `application_thresholds`。原因：官方页面未明确列明。
- `bochk_supply_chain_invoice_payment`：`loan_limit_min_hkd`, `loan_limit_max_hkd`, `loan_limit_text`, `interest_rate_text`, `tenor_text`, `repayment_method_text`, `application_thresholds`。原因：官方页面未明确列明。
- `bochk_supply_chain_pre_shipment_financing`：`loan_limit_min_hkd`, `loan_limit_max_hkd`, `loan_limit_text`, `interest_rate_text`, `tenor_text`, `repayment_method_text`, `application_thresholds`。原因：官方页面未明确列明。
- `bochk_supply_chain_document_checking`：`loan_limit_min_hkd`, `loan_limit_max_hkd`, `loan_limit_text`, `interest_rate_text`, `tenor_text`, `repayment_method_text`, `required_documents`, `application_thresholds`。原因：官方页面未明确列明。
