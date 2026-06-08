# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

CrossBridge AI is an AI assistant for cross-border SME finance and individual loan/financing support.

Core context:
- `README.md`: product overview, demo, and pitch background.
- `service_architecture.md`: authoritative architecture overview, including service topology and pointers to service-specific docs.
- `verification.md`: local venv usage, service startup commands, Alembic migration notes, eval runners, and recommended verification paths.
- `deployment.md`: production deployment notes, systemd units, rsync rules, host-side verification, and safety constraints. Read only for deployment or production-debugging tasks.

Progressive disclosure:
Read only task-relevant docs before working. Do not load unrelated docs by default.

Important:
- The project is not a monolith; it is split into independent services.
- Keep changes scoped to the requested service/function.
- Do not deploy or touch production unless explicitly asked.
- Use deterministic tools for formatting, migrations, tests, and verification.
## Response style

End every reply with `喵～` (on its own, after the final line).

## Frontend convention: cache-buster

Frontend static changes:
If editing `chatraw-fork/backend/static/{app.js,index.html,styles.css}` or the PDF viewer static assets, bump the `?v=cbdevNN` cache-buster in `index.html`. Static-only changes do not require restarting ChatRaw.

## Deployment (production host)

Live demo runs on a Tencent Lighthouse VM at `43.156.240.20` (`ssh ubuntu@43.156.240.20`, passwordless, passwordless sudo). Deploy root `/opt/crossbridge` is **NOT a git repo** — updates are pushed by **rsync from this local repo**, never `git pull`. **Never use `rsync --delete`** (the host holds runtime SQLite DBs and state under `data/`). Secrets live in `/opt/crossbridge/.env` (`DASHSCOPE_API_KEY`, `QWEN_BASE_URL`, `QWEN_MODEL`), never committed.

systemd units (`deploy/systemd/`, restart with `sudo systemctl restart <unit>`):
- `crossbridge-fastapi` → RAG :8080
- `crossbridge-business` → Function 1 :8081 (restart = re-run migrations + re-seed catalog)
- `crossbridge-documents` → Function 2 :8082 (restart = re-run migrations)
- `crossbridge-timeline` → Function 3 :8083 (restart = re-run migrations; hidden bank-operator console at `/crossbridge-admin/timeline`)
- `crossbridge-chatraw` → UI :51111 (restart only for `main.py`/Python changes, not static)

nginx on :80 fronts :51111 with HTTP Basic Auth + an IP allowlist, so the public URL cannot be browser-tested from an unlisted IP — verify against the host's own localhost over SSH (`curl 127.0.0.1:8081/...`, `127.0.0.1:51111/api/...`). `qpdf` and `node` are not installed on the host. Typical update: rsync the changed `server/...`, `chatraw-fork/backend/...`, and any edited `data/...` or `migrations/...`, then restart the affected unit.
