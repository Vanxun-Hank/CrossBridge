# Deployment (production host)

Live demo runs on a Tencent Lighthouse VM at `43.156.240.20` (`ssh ubuntu@43.156.240.20`, passwordless, passwordless sudo). Deploy root `/opt/crossbridge` is **NOT a git repo** — updates are pushed by **rsync from this local repo**, never `git pull`. **Never use `rsync --delete`** (the host holds runtime SQLite DBs and state under `data/`). Secrets live in `/opt/crossbridge/.env` (`DASHSCOPE_API_KEY`, `QWEN_BASE_URL`, `QWEN_MODEL`), never committed.

systemd units (`deploy/systemd/`, restart with `sudo systemctl restart <unit>`):
- `crossbridge-fastapi` → RAG :8080
- `crossbridge-business` → Function 1 :8081 (restart = re-run migrations + re-seed catalog)
- `crossbridge-documents` → Function 2 :8082 (restart = re-run migrations)
- `crossbridge-timeline` → Function 3 :8083 (restart = re-run migrations)
- `crossbridge-chatraw` → UI :51111 (restart only for `main.py`/Python changes, not static)

nginx on :80 fronts :51111 with HTTP Basic Auth + an IP allowlist, so the public URL cannot be browser-tested from an unlisted IP — verify against the host's own localhost over SSH (`curl 127.0.0.1:8081/...`, `127.0.0.1:51111/api/...`). `qpdf` and `node` are not installed on the host. Typical update: rsync the changed `server/...`, `chatraw-fork/backend/...`, and any edited `data/...` or `migrations/...`, then restart the affected unit.

**Function 3 (application timeline) routing.** The SME-facing timeline calls and the live SSE stream go through ChatRaw like F1/F2 — `/api/crossbridge-timeline/...` is proxied to :8083, and the dedicated streaming route `/api/crossbridge-timeline/v1/events` forwards SSE unbuffered (it sets `X-Accel-Buffering: no`), so **no extra nginx location is needed for the SME side**. The hidden bank-operator backend is reached directly via nginx (bypassing ChatRaw), so add two locations that `proxy_pass http://127.0.0.1:8083` and sit behind the **same** `auth_basic` + IP allowlist as the main site:
- `location /crossbridge-admin/` — the operator HTML console (page at `/crossbridge-admin/timeline`).
- `location /crossbridge-timeline-admin/v1/` — the admin API that console calls.

F3 reads submission-readiness from F2 over HTTP (`CROSSBRIDGE_DOCUMENTS_API_URL`, default `http://127.0.0.1:8082`); both that and `CROSSBRIDGE_TIMELINE_API_URL` (default `http://127.0.0.1:8083`, used by ChatRaw) are correct on the host, so no new secrets/env are required. First deploy of F3: rsync `server/application_timeline/`, install + enable `crossbridge-timeline.service`, then restart `crossbridge-chatraw`. **Demo-only**: the admin backend has no app-level auth/RBAC — it relies entirely on the nginx Basic Auth + IP allowlist; add RBAC + operator audit before any real use.

## Server-side git-pull deploy (primary update path)

`/opt/crossbridge` **stays the runtime root and is still NOT a git repo** (the invariant holds). Updates now pull `main` into a **separate source clone** and sync code into the runtime — no dependency on a local machine.

One-time setup (server, as `ubuntu`):
```bash
git clone https://github.com/Vanxun-Hank/CrossBridge-AI.git /opt/crossbridge-src   # anonymous https works
git clone https://github.com/massif-01/ChatRaw ~/chatraw-upstream                  # patch base for the frontend
```

Each update is one script — `git pull main` + sync backend + rebuild the patched frontend over upstream `9408fa8` + reinstall units + restart + health-check (it **never** uses `rsync --delete` on the runtime root):
```bash
bash /opt/crossbridge-src/deploy/server-update.sh
```

**One-button deploy console** (`server/deploy_console`, port :8090, `crossbridge-deploy.service`): a page at `/deploy/` lets a teammate click "deploy latest main" and watch the streamed log — no SSH, no server key. It runs the same `server-update.sh` (`flock`-guarded; the script deliberately does **not** restart `crossbridge-deploy`, so the console survives its own deploy). Add an nginx location behind the same Basic Auth:
```nginx
location /deploy/ {
    proxy_pass http://127.0.0.1:8090;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_buffering off;          # stream the deploy log live
    proxy_read_timeout 300s;
}
```
Demo-grade: a fixed, no-argument script behind Basic Auth + IP allowlist. Before real use, scope ubuntu's sudo to specific commands and add per-user auth + a "who deployed" audit. The old rsync-from-local path still works as a fallback.
