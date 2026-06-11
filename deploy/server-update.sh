#!/usr/bin/env bash
# CrossBridge — pull latest `main` from GitHub and roll it onto the runtime dir.
#
# Safe by design: /opt/crossbridge stays the runtime root (.env, venv, data/ DBs,
# chatraw-fork runtime untouched). This only syncs code + rebuilds the patched
# frontend, then restarts units. It NEVER uses `rsync --delete` on the runtime root.
#
# Run on the server as the ubuntu user (passwordless sudo). Also invoked by the
# one-button deploy console (server/deploy_console) — keep its output line-buffered.
set -euo pipefail

SRC="${CB_SRC:-/opt/crossbridge-src}"               # clean git clone of main (NOT the runtime)
RUNTIME="${CB_RUNTIME:-/opt/crossbridge}"           # runtime root (intentionally NOT a git repo)
UPSTREAM="${CB_UPSTREAM:-$HOME/chatraw-upstream}"    # upstream ChatRaw clone (the patch base)
FORK_BASE="${CB_FORK_BASE:-9408fa8}"                # upstream commit the patch is diffed against
UPSTREAM_URL="https://github.com/massif-01/ChatRaw"

log() { printf '\n==> %s\n' "$*"; }

log "1/6  pull source (main)"
git -C "$SRC" fetch --quiet origin
git -C "$SRC" checkout --quiet main
git -C "$SRC" pull --ff-only --quiet origin main
echo "    source @ $(git -C "$SRC" rev-parse --short HEAD)  —  $(git -C "$SRC" log -1 --pretty=%s)"

log "2/6  sync backend code (no data/ .env venv chatraw-fork; no --delete)"
rsync -a --exclude='__pycache__' --exclude='*.pyc' \
  "$SRC"/server "$SRC"/eval "$SRC"/scripts "$SRC"/files "$SRC"/migrations \
  "$SRC"/deploy "$SRC"/docs "$SRC"/alembic.ini "$SRC"/*.md \
  "$RUNTIME"/

log "3/6  rebuild patched frontend (upstream ChatRaw @ $FORK_BASE + patch)"
if [ ! -d "$UPSTREAM/.git" ]; then git clone --quiet "$UPSTREAM_URL" "$UPSTREAM"; fi
git -C "$UPSTREAM" fetch --quiet origin
git -C "$UPSTREAM" checkout -f --quiet "$FORK_BASE"
git -C "$UPSTREAM" clean -fdq
# --binary matches scripts/apply_chatraw_patch.sh. Pinned vendor (PDF.js etc.) is
# preserved in the runtime fork by the rsync --exclude=vendor below (rarely changes).
git -C "$UPSTREAM" apply --binary --whitespace=nowarn "$SRC/patches/chatraw-function1-function2.patch"
# Copy the rebuilt customized files into the runtime fork; never touch runtime vendor/ or data/.
rsync -a --exclude='vendor' --exclude='data' \
  "$UPSTREAM"/backend/main.py "$UPSTREAM"/backend/static \
  "$RUNTIME"/chatraw-fork/backend/

log "4/6  python deps (idempotent, best-effort)"
"$RUNTIME"/venv/bin/pip install -q -r "$RUNTIME"/files/requirements.txt || true

log "5/6  install systemd units + restart services"
sudo cp "$SRC"/deploy/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
# NOTE: crossbridge-deploy is intentionally NOT restarted here — it is the service
# running this very script; restarting it would kill the in-progress deploy.
sudo systemctl restart crossbridge-fastapi crossbridge-business crossbridge-documents crossbridge-timeline crossbridge-dashboard crossbridge-chatraw

log "6/6  health check (polls up to ~90s — RAG boots slowly: jieba + embeddings + Chroma)"
# Poll each service until 200 or timeout, so a slow-booting RAG isn't a false warning.
check() {  # $1=label  $2=url
  local code=000 i
  for i in $(seq 1 30); do
    code=$(curl -s -o /dev/null -w '%{http_code}' "$2" || echo 000)
    [ "$code" = 200 ] && break
    sleep 3
  done
  printf '    %-8s %s\n' "$1" "$code"
  [ "$code" = 200 ]
}
ok=1
check ":8080" "127.0.0.1:8080/healthz" || ok=0
check ":8081" "127.0.0.1:8081/healthz" || ok=0
check ":8082" "127.0.0.1:8082/healthz" || ok=0
check ":8083" "127.0.0.1:8083/healthz" || ok=0
check ":8084" "127.0.0.1:8084/healthz" || ok=0
check ":51111" "127.0.0.1:51111/" || ok=0
curl -s -o /dev/null -w '    admin    %{http_code}\n' "127.0.0.1:8083/crossbridge-admin/timeline" || true
date -u +'    deployed at %Y-%m-%dT%H:%M:%SZ' | tee "$RUNTIME/.last-deploy"
if [ "$ok" = 1 ]; then log "DEPLOY OK ✓"; else log "DEPLOY FINISHED WITH WARNINGS (some health checks != 200)"; fi
