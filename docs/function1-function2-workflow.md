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

## Function 3: Application Timeline

```mermaid
flowchart TD
    A["F2 工作台页脚『提交申请』"] --> B["flush 草稿（落盘当前官方表单 + 等待自动保存队列）"]
    B --> C["调用 F2 submission-readiness（唯一事实来源）"]
    C --> D{"ready?"}
    D -->|"否"| E["留在 F2 工作台，内联展示 blocking 原因（复用校验文案）"]
    D -->|"是"| F["POST 创建申请；origin_package_id 唯一 → 幂等"]
    F --> G["初始化 6 个固定节点：已提交=completed、材料审核=in_progress、其余 pending"]
    G --> H["右侧面板切到时间线 + 聊天插入常驻概览卡 + 打开 SSE"]
    H --> I["银行端隐藏后台推进当前节点（禁跳级；完成自动推进下一节点）"]
    I -->|"rejected / supplement_required"| J["强制中英文客户说明非空"]
    I --> K["写库并 bump updated_at"]
    K --> L["SME 端 SSE（DB 轮询）检测变化 → 重拉详情 → 无刷新更新卡片与面板"]
```

The SME submits a completed F2 package as a loan application. Submission-readiness is decided **only** by Function 2 (the same high-trust checks the client ran on the active form, now applied server-side across every applicable official form): malformed SWIFT/BIC, supplier-vs-beneficiary mismatch, invoice-vs-payment mismatch, pending charge bearer, unchecked published product materials, and core-field completeness are **blocking**; unaccepted trade terms is a non-blocking **warning**. One application per package (`origin_package_id` is unique, so re-submitting the same package returns the original). The bank advances six fixed nodes (`submitted → material_review → credit_assessment → approval_result → signing → disbursement`) from a hidden operator console: the current node cannot be skipped, completing it auto-advances the next, and `rejected` / `supplement_required` require bilingual customer notes. The SME watches progress update live over SSE without refreshing; the bank's `internal_note` is stripped from every SME-facing response.

Data boundary: F3 owns its FastAPI service on 8083, a separate SQLite database (`data/crossbridge_application_timeline.db`), a separate Alembic environment, the applications, their six nodes, and audit events. It snapshots the product label and scenario at submit time (decoupled from F2's catalog) and reads readiness from F2 over HTTP; it never reads or writes the F1/F2 database tables. The SME-facing serialization never includes `internal_note`. The SME-facing timeline calls and the SSE stream go through ChatRaw (the SSE via a dedicated unbuffered streaming route); the hidden bank-operator console (`/crossbridge-admin/timeline`) is not part of the SME navigation and is protected in production by the nginx IP allowlist + the site's HTTP Basic Auth.

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
    C --> F3["Function 3 timeline API :8083"]
    F3 -. "submission-readiness (HTTP)" .-> F2
    C -. "live SSE (unbuffered proxy)" .-> F3
    BK["Bank operator"] --> ADM["nginx /crossbridge-admin · Basic Auth + IP allowlist"]
    ADM --> F3
```
