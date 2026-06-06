# Verification

How to run the services, run the eval suites, and quickly verify F1/F2/F3 changes.

## Commands

Use the project venv `.venv` (the deployed host uses `/opt/crossbridge/venv`).

```bash
# Function 1 (loan matching) — seed catalog, migrate, run
.venv/bin/python scripts/crawl_bochk_products.py
.venv/bin/alembic -c alembic.ini upgrade head                 # root alembic.ini = Function 1 schema
CROSSBRIDGE_CATALOG_MODE=official .venv/bin/uvicorn server.business.app:app --host 127.0.0.1 --port 8081

# Function 2 (document preparation) — has its OWN alembic.ini
.venv/bin/python scripts/sync_document_preparation_catalog.py
.venv/bin/alembic -c server/document_preparation/alembic.ini upgrade head
.venv/bin/uvicorn server.document_preparation.app:app --host 127.0.0.1 --port 8082

# Function 3 (application timeline) — its OWN alembic.ini; reads submission-readiness from F2 over HTTP
.venv/bin/uvicorn server.application_timeline.app:app --host 127.0.0.1 --port 8083
# hidden bank-operator console: http://127.0.0.1:8083/crossbridge-admin/timeline

# RAG + UI
.venv/bin/uvicorn server.api:app --host 127.0.0.1 --port 8080
cd chatraw-fork/backend && python main.py                     # serves :51111
```

`server.business.app:create_app(migrate_on_startup=True)` (the default) runs Alembic on boot, so restarting the business/documents services applies new migrations automatically. New migrations go in `migrations/versions/` (F1; current head `20260602_0008`), `server/document_preparation/migrations/versions/` (F2), or `server/application_timeline/migrations/versions/` (F3), `down_revision` pointing at the current head.

**Tests are eval runners**, not pytest (there is no unit-test suite beyond `chatraw-fork/backend/test_context_compaction.py`):

```bash
.venv/bin/python eval/run_eval.py                              # RAG recall@k + citation hit (24-question set)
.venv/bin/python eval/run_ragas.py                             # RAGAS faithfulness
.venv/bin/python eval/run_function1_eval.py                    # Function 1 matching
.venv/bin/python eval/run_function1_official_catalog_eval.py   # Function 1 catalog
.venv/bin/python eval/run_function2_eval.py                    # Function 2 (+ submission-readiness)
.venv/bin/python eval/run_function3_eval.py                    # Function 3 (application timeline)
.venv/bin/python eval/run_language_following_eval.py           # bilingual response-language behavior
```

When changing F1/F2/F3 logic, quickest verification is an in-process FastAPI `TestClient` against `create_app(database_url="sqlite:///<tmp>")` (migrations run in the lifespan; F1 also seeds the catalog) — no live ports needed. F3's `create_app(..., readiness_checker=<stub>)` injects a fake Function 2 readiness check so `eval/run_function3_eval.py` stays hermetic (it never starts F2). End-to-end SSE (bank advances a node → SME sees it with no refresh) is verified in the browser, not the eval.
