# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

CrossBridge AI is an AI assistant for cross-border SME finance and individual loan/financing support.

Core context:
- `README.md`: product overview, demo, and pitch background.
- `service_architecture.md`: authoritative architecture overview, service topology, proxy layer, DB isolation.
- `function-workflow.md`: per-function workflow, data boundaries, cross-function handoffs, frontend conventions.
- `verification.md`: local venv usage, service startup commands, Alembic migration notes, eval runners.
- `deployment.md`: production deployment, systemd units, server-update script, safety constraints. Read only for deploy tasks.

Progressive disclosure:
Read only task-relevant docs before working. Do not load unrelated docs by default.

Important:
- The project is not a monolith; it is split into independent services.
- Keep changes scoped to the requested service/function.
- When changing a service, sync the corresponding section in `function-workflow.md` or `service_architecture.md`.
- Do not deploy or touch production unless explicitly asked.
- Use deterministic tools for formatting, migrations, tests, and verification.

## Response style

End every reply with `喵～` (on its own, after the final line).

## Frontend convention: cache-buster

If editing `chatraw-fork/backend/static/{app.js,index.html,styles.css}` or the PDF viewer static assets, bump the `?v=cbdevNN` cache-buster in `index.html`. Static-only changes do not require restarting ChatRaw.

## Deployment (production host)

Live demo on Tencent Lighthouse VM `43.156.240.20` (`ssh ubuntu@43.156.240.20`, passwordless sudo). Deploy root `/opt/crossbridge` is **NOT a git repo**. Primary update: `bash /opt/crossbridge-src/deploy/server-update.sh` (git pull main into source clone + sync + rebuild patched frontend + restart + health-check). One-button deploy console at `/deploy/` (:8090). Fallback: rsync from local repo. **Never use `rsync --delete`** (runtime SQLite DBs and state under `data/`). Secrets in `/opt/crossbridge/.env`, never committed.

systemd units (`deploy/systemd/`, restart with `sudo systemctl restart <unit>`):
- `crossbridge-fastapi` → RAG :8080
- `crossbridge-business` → F1 :8081 (restart = re-run migrations + re-seed catalog)
- `crossbridge-documents` → F2 :8082 (restart = re-run migrations)
- `crossbridge-timeline` → F3 :8083 (restart = re-run migrations)
- `crossbridge-chatraw` → UI :51111 (restart only for Python changes, not static)
- `crossbridge-deploy` → deploy console :8090

nginx :80 fronts :51111 with HTTP Basic Auth + IP allowlist. Verify via SSH: `curl 127.0.0.1:{8081,8082,8083}/healthz`, `127.0.0.1:51111/api/...`.
