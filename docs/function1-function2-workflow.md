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

![Function 2 document-preparation workflow](assets/function2-document-preparation-workflow.svg)

```mermaid
flowchart TD
    A["侧边栏材料准备入口，或 F1 产品卡点击准备材料"] --> B["打开聊天概览气泡 + 右侧材料面板"]
    B --> C{"用户手选进口或出口场景？"}
    C -->|"未选择"| D["停留场景选择器，等待用户确认"]
    C -->|"已选择"| E["创建或恢复该 SME + 场景的材料包"]
    E --> H["加载场景三档清单 + 产品叠加 + 官方 BOCHK 表单清单"]
    H --> S["选择官方表单（精确匹配当前产品的表单置顶）"]
    S --> T{"该表单需要贸易融资条款？"}
    T -->|"需要且未接受"| U["弹出条款确认；接受后按 sme + 条款SHA 记录"]
    T -->|"不需要 / 已接受"| V{"官方 PDF 已在本地缓存？"}
    U --> V
    V -->|"否"| W["显示缺失提示 + BOCHK 官方下载链接（绝不伪造表单）"]
    V -->|"是"| X["内嵌 PDF.js 直接填写官方 AcroForm（同源 iframe）"]
    X --> Y["字段变更 500ms 防抖 → 白名单过滤后按 source SHA 保存草稿"]
    Y --> Z{"用户下一步操作"}
    Z -->|"导出"| Z1["saveDocument() 下载填好的真实官方 PDF + 写 exported 审计"]
    Z -->|"打印"| Z2["写 printed 审计 → 查看器打印真实 PDF"]
    Z -->|"重置"| Z3["清空清单与官方表单草稿（保留同版本条款接受）+ 审计"]
```

F1-to-F2 handoff passes only product preselection and optional context for recommendation highlighting. The user still chooses the import or export scenario inside F2. Document preparation fills **genuine official BOCHK PDF forms** in-place via PDF.js (ENABLE_FORMS + `annotationStorage`, exported with `saveDocument()` — no flattening, no coordinate overlays), instead of self-made fill-in templates. Trade-finance forms are gated behind explicit acceptance of BOCHK's terms; an official PDF that is not present in the deployment's local cache shows a download hint rather than a fabricated form. Publicly documented materials remain public-source labelled; unpublished requirements remain relationship-manager confirmation items.

Data boundary: F2 owns its FastAPI service on 8082, separate SQLite database, separate Alembic environment, read-only document catalog snapshot, the official-form registry, package state, official-form drafts (keyed by `package_id + form_id + source_sha256`), trade-terms acceptance (keyed by `sme_id + terms_sha256`), checklist states, and audit events. It never reads or writes F1 database tables. The encrypted official PDFs live only in a git-ignored local cache (`data/document_preparation/official_forms_cache/`); they are never committed.

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
