# CrossBridge AI Function 1 and Function 2 Workflow

![CrossBridge AI Function 1 and Function 2 user workflow](assets/function1-function2-user-workflow.png)

## Function 1: Loan Matching

![Function 1 loan-matching workflow](assets/function1-loan-matching-workflow.svg)

```mermaid
flowchart TD
    A["聊天输入或左侧贷款匹配入口"] --> B["意图路由"]
    B -->|"找贷款、申请融资、推荐产品"| C["展示 CTA"]
    B -->|"政策解释类问题"| D["继续进入 Function 5 RAG"]
    C --> E["创建匹配草稿 Session"]
    E --> F["载入已确认企业画像，并合并可识别信息"]
    F --> G["表单填写 + AI 逐轮澄清"]
    G --> H{"四个必填字段完整？"}
    H -->|"否"| I["最多澄清 3 次，仍缺失则停留草稿"]
    H -->|"是"| J["Python 确定性筛选官方目录"]
    J --> K["显示候选卡片、官方来源、待客户经理确认项"]
    K --> L{"用户明确保存画像？"}
    L -->|"保存"| M["写入 sme_profiles 长期画像"]
    L -->|"取消"| N["丢弃草稿，仅保留审计事件"]
```

The four required fields are cross-border scenario, annual turnover, financing purpose, and requested amount. Enum chips update the draft deterministically. Free-text answers use the Qwen clarifier when configured, and visible clarification questions follow the user's Chinese or English input language.

Data boundary: F1 owns its FastAPI service on 8081, SQLite database, Alembic migrations, session drafts, saved SME profiles, matching results, audit events, official catalog snapshot, and deterministic matching rules.

## Function 2: Document Preparation

1. The user enters from the sidebar or clicks `Prepare Documents` on an F1 product card.
2. F1-to-F2 handoff passes only product preselection and optional context for recommendation highlighting. The user still chooses the import or export scenario inside F2.
3. ChatRaw opens the F2 workbench as a right-side panel while preserving the chat transcript.
4. The 8082 service creates or restores a document package for the SME and selected scenario.
5. The panel combines the scenario base checklist with the selected product overlay. Publicly documented materials are labelled as public-source requirements; preparation suggestions remain suggestions; unpublished requirements remain relationship-manager confirmation items.
6. The user checks items, edits the scenario-specific transaction form and financing cover sheet, reviews non-blocking validation warnings, switches compatible products, resets the package, or prints the preparation pack.
7. Template drafts and checklist state auto-save. Switching products keeps base checklist progress and restores product-overlay progress when switching back.

Data boundary: F2 owns its FastAPI service on 8082, separate SQLite database, separate Alembic environment, read-only document catalog snapshot, package state, template drafts, checklist states, and audit events. It never reads or writes F1 database tables.

## Service Flow

```mermaid
flowchart LR
    U["SME user"] --> C["ChatRaw UI :51111"]
    C --> R["Policy RAG :8080"]
    C --> F1["Function 1 business API :8081"]
    F1 --> O["BOCHK official catalog snapshot"]
    F1 --> Q["Qwen clarifier via DashScope"]
    C --> F2["Function 2 documents API :8082"]
    F2 --> D["F2 document catalog snapshot"]
    F1 -. "product preselection only" .-> F2
```
