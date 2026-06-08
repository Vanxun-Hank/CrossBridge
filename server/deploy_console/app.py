from __future__ import annotations

import asyncio
import os
import shlex
from pathlib import Path

import httpx
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse

# Fixed script + paths (no user input ever reaches a shell — no injection surface).
SCRIPT = os.environ.get("CB_UPDATE_SCRIPT", "/opt/crossbridge-src/deploy/server-update.sh")
SRC = os.environ.get("CB_SRC", "/opt/crossbridge-src")
RUNTIME = os.environ.get("CB_RUNTIME", "/opt/crossbridge")
LOCK = "/tmp/crossbridge-deploy.lock"
PREFIX = "/deploy"

# Services to health-check on the status line.
SERVICES = [
    ("RAG", "http://127.0.0.1:8080/healthz"),
    ("F1 贷款匹配", "http://127.0.0.1:8081/healthz"),
    ("F2 材料准备", "http://127.0.0.1:8082/healthz"),
    ("F3 申请进度", "http://127.0.0.1:8083/healthz"),
    ("ChatRaw UI", "http://127.0.0.1:51111/"),
]

app = FastAPI(title="CrossBridge Deploy Console")

_running = False  # single-worker in-process guard (flock guards across processes)


async def _sh(cmd: str) -> str:
    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL
    )
    out, _ = await proc.communicate()
    return out.decode(errors="replace").strip()


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get(f"{PREFIX}/status")
async def status() -> JSONResponse:
    sha = await _sh(f"git -C {shlex.quote(SRC)} rev-parse --short HEAD 2>/dev/null")
    subject = await _sh(f"git -C {shlex.quote(SRC)} log -1 --pretty=%s 2>/dev/null")
    last = ""
    marker = Path(RUNTIME) / ".last-deploy"
    if marker.exists():
        last = marker.read_text(encoding="utf-8", errors="replace").strip()
    services = []
    async with httpx.AsyncClient(timeout=3.0) as client:
        for name, url in SERVICES:
            try:
                r = await client.get(url)
                services.append({"name": name, "ok": r.status_code == 200, "code": r.status_code})
            except httpx.HTTPError:
                services.append({"name": name, "ok": False, "code": 0})
    return JSONResponse(
        {"sha": sha, "subject": subject, "last_deploy": last, "running": _running, "services": services}
    )


@app.post(f"{PREFIX}/run", response_model=None)
async def run() -> StreamingResponse | JSONResponse:
    global _running
    if _running:
        return JSONResponse({"error": "a deploy is already running"}, status_code=409)

    async def stream():
        global _running
        _running = True
        # flock -n: refuse a second concurrent deploy even across processes / an ssh run.
        cmd = f"flock -n {shlex.quote(LOCK)} bash {shlex.quote(SCRIPT)} 2>&1"
        proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE)
        try:
            assert proc.stdout is not None
            async for line in proc.stdout:
                yield line
            await proc.wait()
            yield f"\n[exit {proc.returncode}]\n".encode()
        finally:
            _running = False

    return StreamingResponse(
        stream(),
        media_type="text/plain; charset=utf-8",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# Raw (non-f) string: { } are literal CSS/JS braces AND backslash escapes like \n in the
# JS stay literal (a plain string would let Python turn them into real newlines, breaking
# the inline script). Log uses textContent only (no innerHTML).
_PAGE = r"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CrossBridge · 一键部署</title>
<style>
  :root { --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif;
    --mono:ui-monospace,SFMono-Regular,Menlo,monospace; --bg:#f6f6f7; --surface:#fff; --ink:#1a1a1a;
    --soft:#6b6b6b; --faint:#a0a0a0; --line:#e7e7ea; --accent:#111; --ok:#16a34a; --bad:#dc2626; }
  * { box-sizing:border-box; }
  body { margin:0; font-family:var(--sans); color:var(--ink); background:var(--bg); font-size:14px; line-height:1.55; }
  .wrap { max-width:860px; margin:0 auto; padding:28px 22px 48px; }
  h1 { font-size:18px; font-weight:600; margin:0 0 2px; }
  .sub { color:var(--soft); font-size:13px; margin-bottom:20px; }
  .card { background:var(--surface); border:1px solid var(--line); border-radius:12px; padding:16px 18px; margin-bottom:16px; }
  .row { display:flex; align-items:center; gap:12px; flex-wrap:wrap; }
  .sha { font-family:var(--mono); font-size:12px; color:var(--soft); }
  .svc { display:flex; gap:14px; flex-wrap:wrap; margin-top:12px; }
  .svc span { display:inline-flex; align-items:center; gap:6px; font-size:12.5px; color:var(--soft); }
  .dot { width:8px; height:8px; border-radius:50%; background:var(--faint); }
  .dot.ok { background:var(--ok); } .dot.bad { background:var(--bad); }
  button { font-family:var(--sans); font-size:14px; font-weight:600; cursor:pointer; border:1px solid var(--accent);
    background:var(--accent); color:#fff; border-radius:10px; padding:11px 20px; transition:opacity .15s ease; }
  button:hover:not(:disabled) { opacity:.85; } button:disabled { opacity:.45; cursor:default; }
  .ghost { background:var(--surface); color:var(--ink); border-color:var(--line); font-weight:500; padding:8px 14px; font-size:13px; }
  pre { font-family:var(--mono); font-size:12px; line-height:1.5; background:#0d0d0f; color:#e6e6e6; border-radius:10px;
    padding:14px 16px; margin:0; max-height:440px; overflow:auto; white-space:pre-wrap; word-break:break-word; }
  .muted { color:var(--faint); }
</style>
</head>
<body>
<div class="wrap">
  <h1>CrossBridge · 一键部署 <span class="muted" style="font-weight:400;font-size:13px">/ One-click deploy</span></h1>
  <div class="sub">点下面的按钮 = 服务器从 GitHub <b>main</b> 拉最新代码、重建前端、重启服务。日志实时显示。</div>

  <div class="card">
    <div class="row">
      <button id="go">部署最新 main</button>
      <button class="ghost" id="refresh">刷新状态</button>
      <span class="sha" id="sha">…</span>
    </div>
    <div class="svc" id="svc"></div>
  </div>

  <div class="card" style="padding:0;border:none;background:none">
    <pre id="log"><span class="muted">日志会显示在这里 …</span></pre>
  </div>
</div>
<script>
const logEl = document.getElementById('log');
const goBtn = document.getElementById('go');
let started = false;
function append(text) {
  if (!started) { logEl.textContent = ''; started = true; }
  logEl.textContent += text;
  logEl.scrollTop = logEl.scrollHeight;
}
async function loadStatus() {
  try {
    const res = await fetch('/deploy/status');
    const d = await res.json();
    document.getElementById('sha').textContent = 'main @ ' + (d.sha || '?') + (d.subject ? ' · ' + d.subject : '') + (d.last_deploy ? ' · ' + d.last_deploy : '');
    const svc = document.getElementById('svc');
    svc.replaceChildren.apply(svc, (d.services || []).map(s => {
      const dot = document.createElement('span'); dot.className = 'dot ' + (s.ok ? 'ok' : 'bad');
      const wrap = document.createElement('span'); wrap.appendChild(dot);
      wrap.appendChild(document.createTextNode(s.name + (s.ok ? '' : ' (' + s.code + ')')));
      return wrap;
    }));
  } catch (e) { /* ignore */ }
}
async function deploy() {
  goBtn.disabled = true; started = false; append('开始部署 …\n');
  try {
    const res = await fetch('/deploy/run', { method: 'POST' });
    if (res.status === 409) { append('⚠ 已有一个部署在进行中,请稍候。\n'); goBtn.disabled = false; return; }
    const reader = res.body.getReader();
    const dec = new TextDecoder();
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      append(dec.decode(value, { stream: true }));
    }
  } catch (e) {
    append('\n[错误] ' + e.message + '\n');
  } finally {
    goBtn.disabled = false;
    loadStatus();
  }
}
goBtn.addEventListener('click', deploy);
document.getElementById('refresh').addEventListener('click', loadStatus);
loadStatus();
setInterval(loadStatus, 15000);
</script>
</body>
</html>
"""


@app.get(f"{PREFIX}/", response_class=HTMLResponse)
def page() -> HTMLResponse:
    return HTMLResponse(_PAGE, headers={"Cache-Control": "no-store"})
