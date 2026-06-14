# Function Workflow — CrossBridge AI

How each function works, what it owns, and how they connect. For ports, env vars, and proxy details see `service_architecture.md`.

---

## Function 1: Loan Matching (:8081)

**Flow**: chat input → `route_intent` (regex, no LLM) → CTA card → create draft session → form fill + AI clarification → 4 required fields complete → deterministic product match → candidate cards → user saves SME profile.

- **Required fields**: cross-border scenario, annual turnover, financing purpose, requested amount. Enum chips update the draft; free text goes to `LlmClarifier` (Qwen) when configured.
- **Session lifecycle**: `draft → awaiting_clarification → ready_to_match → matched|saved|discarded`. Creating a new session discards any open one (never resumes old state).
- **Multi-draft**: `saved_drafts` table holds multiple snapshots, each with selected products. Distinct from the legacy single-row `sme_profiles`.
- **Data boundary**: owns `data/crossbridge_app.db` (SQLite + Alembic). Tables: `sme_profiles`, `matching_sessions`, `loan_products`, `match_results`, `saved_drafts`, `audit_events`. Startup seeds catalog from `data/official_products/bochk_products_latest.json`.

## Function 2: Document Preparation (:8082)

**Flow**: sidebar or F1 candidate card "Prepare Documents" → choose import/export scenario → create or resume package → load 3-tier checklist + product overlays + official BOCHK form list → select form → accept trade terms if required → fill genuine PDF in embedded PDF.js viewer → export/print real PDF.

- **Official PDF forms**: filled in-place via PDF.js (`ENABLE_FORMS` + `annotationStorage`, exported with `saveDocument()`). Forms are git-ignored; fetched by `scripts/fetch_official_forms.py --accept-bochk-trade-terms` into `data/document_preparation/official_forms_cache/`. Missing PDF → download hint, never a fabricated form.
- **`validation_bindings`**: per-form map of semantic code → AcroForm field name (defined in `data/document_preparation/form_registry.json`). Used by both frontend validation and backend submission-readiness.
- **Submission-readiness** (`GET /packages/{id}/submission-readiness`): server-side check mirroring frontend `runDocValidation`. Blocking: malformed SWIFT/BIC, supplier-vs-beneficiary mismatch, invoice-vs-payment mismatch, pending charge bearer, unchecked published documents, core-field emptiness. Warning: unaccepted trade terms (non-blocking).
- **Link-on-save**: when user clicks "Confirm and Save SME Profile" in F1, `PATCH /packages/{id}/saved-draft` binds the current package to that loan draft. Resume from either entry point (saved drafts or document drafts) returns the same package.
- **Data boundary**: owns `data/crossbridge_document_preparation.db` (SQLite + Alembic). Key table: `document_packages` (with `selected_product_id`, `origin_matching_session_id`, `saved_draft_id`). Never reads/writes F1 tables.

## Function 3: Application Timeline (:8083)

**Flow**: F2 footer "Submit Application" → flush drafts → check F2 submission-readiness → ready → `POST /applications` (idempotent per `origin_package_id`) → initialize 6 fixed nodes → right panel switches to timeline + chat card inserted + SSE opens.

- **6 fixed nodes** (sort order): `submitted` → `material_review` → `credit_assessment` → `approval_result` → `signing` → `disbursement`. Initial state: `submitted=completed`, `material_review=in_progress`, rest `pending`.
- **Bank operator console** (`/crossbridge-admin/timeline`, hidden, nginx-protected): advance current node (no skipping), `rejected`/`supplement_required` require bilingual customer notes, completing a node auto-advances the next. `internal_note` never serialized to SME. Demo-only **reset** and **delete** per application: delete removes the application + its nodes (audit `timeline_application_deleted` kept), frees the `origin_package_id` UNIQUE slot for resubmission, and — since app and console read the same table — it disappears from the SME app on its next list reload (SSE pushes updates only, not deletions).
- **SSE**: DB polling ~2s; pushes `{application_id, updated_at}`; frontend re-fetches detail on each event (prevents `internal_note` leak). Streams through ChatRaw unbuffered proxy (`X-Accel-Buffering: no`).
- **Data boundary**: owns `data/crossbridge_application_timeline.db` (SQLite + Alembic). Tables: `timeline_applications` (`origin_package_id` UNIQUE), `timeline_nodes`, `timeline_audit_events`. Snapshots product label/scenario at submit time (decoupled from F2 catalog).

## Function 5: RAG Policy Q&A (:8080)

**Flow**: chat input (Policy mode) → `POST /api/chat` → RAG pipeline: classify → multi-query → BM25(jieba) + Dense(Qwen embeddings) → RRF → cross-encoder rerank (DashScope gte-rerank-v2) → citation gating (`trust_tier × document_type`) → LLM answer.

- Wrapped as OpenAI-compatible `/v1/chat/completions` (used by ChatRaw). Depends on Qwen/DashScope (`QWEN_BASE_URL`, `DASHSCOPE_API_KEY`).
- **Engine auto-selection** (`server/api.py:_load_rag_engine`): prefers the full Qwen + Chroma + BM25 + rerank pipeline (`files/rag_engine.py`); if it can't load (missing key / deps / Chroma) it falls back to a **dependency-free local engine** (`server/function5_local.py`: BM25 + RRF + citation gating over `chunks.jsonl`) so Function 5 still runs on a fresh machine with no API key. `/healthz` reports `fallback_active` / `fallback_reason`; a runtime failure of the full engine (e.g. DashScope quota) also falls back per request.
- **Built-in demo page** (no ChatRaw needed): `GET /` serves `server/static/function5.html`, which calls `POST /function5/ask` — a structured endpoint returning `{answer, citations[], response_language, engine, trace}`. It is separate from `/v1/chat/completions` and calls `rag.ask()` exactly like the eval does, so `eval/run_eval.py` / `run_ragas.py` stay unaffected. The answer follows the spec shape: 权威回答 / 针对性合规风险提示 / 操作建议 / 官方来源 / 免责声明.
- **Dedicated ChatRaw view**: a first-class "合规问答 / Policy Q&A" sidebar entry opens a modal that calls `POST /api/crossbridge-policy/function5/ask` (ChatRaw proxy → `:8080/function5/ask`) and renders the structured answer + official-source cards (with `trust_tier` tags) + engine badge + disclaimer. Coexists with the base Policy-mode chat; both hit the same RAG engine. The customization lives in `patches/chatraw-function1-function2.patch` (the `chatraw-fork/` clone is git-ignored).
- Data: `data/chroma` (vector store), `data/processed/chunks.jsonl`. No SQL database.

---

## Cross-function handoffs

| From → To | Mechanism | Detail |
|---|---|---|
| F1 → F2 | Frontend `openDocumentPreparation(productId, sessionId)` | Soft reference strings in F2 DB; F1 doesn't know about F2. |
| F2 → F3 | F3 HTTP call to F2 `submission-readiness` | Only inter-service HTTP call. F3 `readiness_checker` injectable (stub in eval). |
| F1 save → F2 | Frontend `PATCH /packages/{id}/saved-draft` after save-draft | Binds package to loan draft for resume. |

**Cascade delete & protection** (frontend-orchestrated, no backend changes):

| Action | Pre-submission (no F3 app) | Post-submission (F3 app exists) |
|---|---|---|
| Delete loan draft (A) | Cascade-deletes linked doc package (B), then deletes A | Blocked — button disabled + tooltip |
| Delete doc package (B) | Soft-deletes B; A unaffected (user can re-fill B from A) | Blocked — button disabled + tooltip |

All inter-service references are non-FK soft strings across separate SQLite databases. F2 delete is a soft delete (`status='deleted'`); `create_or_resume_package` only queries `status='active'`, so deleting B then resuming from A correctly creates a new package.

The A→B link used by the protection/cascade (`linkedPackageForDraft` in `app.js`) prefers `package.saved_draft_id`; for legacy packages created before link-on-save (`saved_draft_id` NULL) it falls back to `package.origin_matching_session_id === draft.origin_session_id`, so old drafts are protected/cascaded too instead of failing open.

## Frontend (`chatraw-fork/backend/static/`)

- **Stack**: Alpine.js (`x-data="app()"`), monochrome Grok-style, system fonts. Single-file: `app.js`, `index.html`, `styles.css`.
- **Panels**: F2 document panel and F3 timeline panel are mutually exclusive, share `--chatraw-doc-panel-width`.
- **i18n**: `t(key)` with `i18n.en`/`i18n.zh`; F3 keys prefixed `cbTl*`, F5 Policy-panel keys `cbPolicy*`. The welcome tagline (`crossbridgeSubtitle`) and the page title/header branding ("CrossBridge AI") are i18n-driven too — they follow the UI language and are no longer read from the backend `ui_settings.subtitle`/`logo_text` fallback "ChatRaw".
- **Cross-function card persistence**: function-emitted cards in the transcript (F1 loan CTA / profile draft / candidate plans, F2 doc-prep overview, F3 timeline overview) are pushed via `pushCardMessage(card)`, which persists `{role:'assistant', content:'', metadata}` to a `messages.metadata` JSON column (backend `POST /api/chats/{id}/messages`). `loadMessages` calls `hydrateCardMetadata()` to map `metadata.kind` back onto the message props the templates read, so cards survive chat-session switches. Card-only rows (empty content + metadata) are excluded from the model history (`_is_card_only` in `main.py`). F1 cards store their `sessionId`; a restored card's session-dependent buttons lazily resume the live session via `ensureLoanSession` (GET-by-id, else recreate from the persisted snapshot) — only on click, never on chat load, so `resetBusinessModes` still prevents loan-mode leaking between chats.
- **Versioning**: `chatraw-fork/` is git-ignored; maintained via `patches/chatraw-function1-function2.patch` over upstream `massif-01/ChatRaw @ 9408fa8`. **The patch is the single source of truth, not the clone** — it is sometimes edited directly (PRs). ⚠️ Regenerating the patch from a stale clone silently drops whatever was added directly to the patch (this wiped the F5 panel in `0e645a3`, restored in `5edbccc`). Safe workflow: **(1) re-sync the clone first** — `cd chatraw-fork && git reset --hard 9408fa8 && git clean -fdq -e vendor && git apply --binary --whitespace=nowarn ../patches/chatraw-function1-function2.patch` (`-e vendor` is mandatory: `backend/static/vendor/` is ~10M untracked, not gitignored, not refetchable without node/qpdf); **(2)** edit the static files + bump the cache-buster; **(3) regenerate** — `git diff --binary 9408fa8 -- backend/ > ../patches/chatraw-function1-function2.patch`; **(4)** sanity-check it applies on a pristine base (`git worktree add --detach /tmp/base 9408fa8 && git -C /tmp/base apply --check --binary <patch>`) before committing.
- **Cache-buster**: `?v=cbdevNN` in `index.html` — bump on every static change.
