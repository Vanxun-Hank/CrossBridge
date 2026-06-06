"""Self-contained HTML for the hidden bank-operator console (Function 3).

Served by the F3 service at ``GET /crossbridge-admin/timeline``. It is intentionally
NOT part of the SME navigation and is protected in production by the nginx IP
allowlist + the site's existing HTTP Basic Auth (see deployment.md). No build step:
one inline page that calls the admin API on the same origin.

The DOM is built with ``createElement`` / ``textContent`` (never string-interpolated
HTML), so bank- and SME-entered free text can never inject markup.
"""
from __future__ import annotations

# Plain (non-f) string: all { } are literal JS/CSS braces.
ADMIN_PAGE_HTML = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CrossBridge · 申请进度后台</title>
<style>
  /* Light operator console — coherent with ChatRaw's minimal monochrome system:
     system font, white/grey/black, ink + grey status (ChatRaw red only for rejected),
     no rainbow. DOM is built with createElement/textContent (never innerHTML). */
  :root {
    --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif;
    --bg:#f6f6f7; --surface:#ffffff; --ink:#1a1a1a; --ink-soft:#6b6b6b; --ink-faint:#a0a0a0;
    --line:#e7e7ea; --line-strong:#d6d6da; --accent:#111111; --on-accent:#ffffff; --error:#dc2626;
    --radius:12px; --radius-sm:8px;
  }
  * { box-sizing:border-box; }
  body { margin:0; font-family:var(--sans); font-size:14px; line-height:1.55; color:var(--ink); background:var(--bg); -webkit-font-smoothing:antialiased; -moz-osx-font-smoothing:grayscale; }
  header { display:flex; align-items:center; gap:14px; padding:16px 28px; background:var(--surface); border-bottom:1px solid var(--line); }
  header .wordmark { font-size:15px; font-weight:600; letter-spacing:-.01em; }
  header .tag { font-size:11px; font-weight:500; color:var(--ink-soft); background:var(--bg); border:1px solid var(--line); border-radius:999px; padding:3px 10px; }
  header .spacer { flex:1; }
  button { font-family:var(--sans); font-size:13px; font-weight:500; cursor:pointer; border-radius:var(--radius-sm); padding:8px 14px; background:var(--accent); color:var(--on-accent); border:1px solid var(--accent); transition:opacity .15s ease; }
  button:hover { opacity:.85; }
  button:active { transform:translateY(.5px); }
  button.ghost { background:var(--surface); color:var(--ink); border-color:var(--line-strong); }
  button.ghost:hover { opacity:1; background:var(--bg); }
  button.danger { background:var(--surface); color:var(--error); border-color:#eccaca; }
  button.danger:hover { opacity:1; background:#fdf3f3; }
  main { display:grid; grid-template-columns:340px 1fr; gap:18px; padding:20px 28px; align-items:start; }
  .card { background:var(--surface); border:1px solid var(--line); border-radius:var(--radius); overflow:hidden; }
  #list .app { position:relative; padding:14px 17px; border-bottom:1px solid var(--line); cursor:pointer; transition:background .14s ease; }
  #list .app:last-child { border-bottom:none; }
  #list .app:hover { background:var(--bg); }
  #list .app.active { background:var(--bg); }
  #list .app.active::before { content:''; position:absolute; left:0; top:0; bottom:0; width:2px; background:var(--accent); }
  #list .app .name { font-weight:600; font-size:14.5px; }
  #list .app .meta { font-size:12px; color:var(--ink-soft); margin-top:5px; display:flex; gap:9px; align-items:center; flex-wrap:wrap; }
  .badge { font-size:12px; font-weight:500; color:var(--ink-soft); display:inline-flex; align-items:center; gap:5px; white-space:nowrap; }
  .badge::before { content:''; width:6px; height:6px; border-radius:50%; background:currentColor; }
  .badge.in_progress { color:var(--ink); }
  .badge.completed { color:var(--ink-soft); }
  .badge.rejected { color:var(--error); }
  .badge.supplement_required { color:var(--ink-soft); }
  .badge.pending { color:var(--ink-faint); }
  #detail .head { padding:18px 22px; border-bottom:1px solid var(--line); display:flex; gap:12px; align-items:baseline; flex-wrap:wrap; }
  #detail .head h2 { margin:0; font-size:17px; font-weight:600; }
  #detail .head .sub { font-size:12px; color:var(--ink-soft); }
  .empty { padding:56px 20px; text-align:center; color:var(--ink-soft); }
  .node { position:relative; padding:16px 22px; border-bottom:1px solid var(--line); }
  .node:last-child { border-bottom:none; }
  .node.current { background:var(--bg); }
  .node.current::before { content:''; position:absolute; left:0; top:0; bottom:0; width:2px; background:var(--accent); }
  .node .row { display:flex; align-items:center; gap:11px; }
  .node .dot { width:13px; height:13px; border-radius:50%; background:var(--surface); border:1.5px solid var(--line-strong); flex:none; }
  .node.completed .dot { background:var(--accent); border-color:var(--accent); }
  .node.in_progress .dot { background:var(--surface); border:2px solid var(--accent); }
  .node.rejected .dot { background:var(--error); border-color:var(--error); }
  .node.supplement_required .dot { background:var(--surface); border:2px dashed var(--ink-soft); }
  .node .title { font-weight:600; font-size:15px; }
  .node.pending .title { color:var(--ink-soft); font-weight:500; }
  .node .current-tag { font-size:11px; font-weight:500; color:var(--ink); background:var(--surface); border:1px solid var(--line-strong); border-radius:999px; padding:1px 9px; }
  .fields { margin-top:13px; display:grid; gap:12px; grid-template-columns:210px 1fr; }
  .fields .full { grid-column:1 / -1; }
  .fields label { display:block; font-size:12px; font-weight:500; color:var(--ink-soft); margin-bottom:6px; }
  textarea, input, select { width:100%; font-family:var(--sans); font-size:13.5px; color:var(--ink); background:var(--surface); border:1px solid var(--line-strong); border-radius:var(--radius-sm); padding:8px 10px; }
  textarea { resize:vertical; min-height:50px; line-height:1.5; }
  textarea:focus, input:focus, select:focus { outline:none; border-color:var(--accent); box-shadow:0 0 0 3px rgba(17,17,17,.06); }
  .actions { margin-top:13px; display:flex; gap:10px; align-items:center; }
  .msg { font-size:12.5px; color:var(--ink-soft); }
  .msg.err { color:var(--error); }
  .msg.ok { color:var(--ink); }
  @media (prefers-reduced-motion: reduce) { * { transition:none !important; } }
</style>
</head>
<body>
<header>
  <span class="wordmark">CrossBridge · 申请进度后台</span>
  <span class="tag">银行端 · 内部</span>
  <span class="spacer"></span>
  <button class="ghost" id="refresh">刷新</button>
</header>
<main>
  <section id="list" class="card"></section>
  <section id="detail" class="card"></section>
</main>
<script>
const API = '/crossbridge-timeline-admin/v1';
const STATE_LABELS = { pending:'待处理', in_progress:'进行中', completed:'已完成', rejected:'已拒绝', supplement_required:'需补件' };
const SETTABLE = ['in_progress','completed','rejected','supplement_required'];
let apps = [];
let selectedId = null;
const listEl = document.getElementById('list');
const detailEl = document.getElementById('detail');

// Tiny hyperscript: createElement + textContent only, no HTML string interpolation.
function h(tag, props) {
  const el = document.createElement(tag);
  if (props) for (const k in props) {
    const v = props[k];
    if (k === 'class') el.className = v;
    else if (k === 'onclick') el.addEventListener('click', v);
    else if (k === 'value') el.value = v;
    else el.setAttribute(k, v);
  }
  for (let i = 2; i < arguments.length; i++) {
    const kids = Array.isArray(arguments[i]) ? arguments[i] : [arguments[i]];
    for (const c of kids) {
      if (c == null || c === false) continue;
      el.appendChild(typeof c === 'object' ? c : document.createTextNode(String(c)));
    }
  }
  return el;
}
function badge(state) { return h('span', { class: 'badge ' + state }, STATE_LABELS[state] || state); }

async function load() {
  try {
    const res = await fetch(API + '/applications');
    const data = await res.json();
    apps = data.applications || [];
    if (selectedId && !apps.some(a => a.id === selectedId)) selectedId = null;
    renderList();
    renderDetail();
  } catch (e) {
    listEl.replaceChildren(h('div', { class: 'empty' }, '加载失败: ' + e.message));
  }
}

function renderList() {
  if (!apps.length) { listEl.replaceChildren(h('div', { class: 'empty' }, '暂无申请')); return; }
  listEl.replaceChildren.apply(listEl, apps.map(a => {
    const stage = a.nodes.find(n => n.node_code === a.current_node_code) || {};
    return h('div', { class: 'app' + (a.id === selectedId ? ' active' : ''), onclick: () => selectApp(a.id) },
      h('div', { class: 'name' }, a.product_label_zh || a.product_id || a.origin_package_id),
      h('div', { class: 'meta' }, a.sme_id + ' · 当前: ' + (stage.label_zh || a.current_node_code) + ' ', badge(a.status))
    );
  }));
}

function selectApp(id) { selectedId = id; renderList(); renderDetail(); }

function field(labelText, inputEl, full) {
  return h('div', { class: full ? 'full' : '' }, h('label', null, labelText), inputEl);
}

function renderNode(a, n) {
  const isCurrent = n.node_code === a.current_node_code;
  const zhTa = h('textarea'); zhTa.value = n.customer_note_zh || '';
  const enTa = h('textarea'); enTa.value = n.customer_note_en || '';
  const intTa = h('textarea'); intTa.value = n.internal_note || '';
  const remInput = h('input', { type: 'datetime-local' }); remInput.value = n.reminder_at ? n.reminder_at.slice(0, 16) : '';
  let stateSel = null;
  const fields = [];
  if (isCurrent) {
    stateSel = h('select');
    for (const s of SETTABLE) {
      const o = h('option', { value: s }, STATE_LABELS[s]);
      if (s === n.state) o.selected = true;
      stateSel.appendChild(o);
    }
    fields.push(field('状态', stateSel));
  }
  fields.push(field('提醒时间', remInput));
  fields.push(field('客户可见说明(中文)', zhTa, true));
  fields.push(field('客户可见说明(English)', enTa, true));
  fields.push(field('内部备注(客户永不可见)', intTa, true));

  const msg = h('span', { class: 'msg' });
  const refs = { zh: zhTa, en: enTa, internal: intTa, reminder: remInput, state: stateSel, msg: msg };
  const btn = h('button', { onclick: () => saveNode(a.id, n.node_code, refs) }, '保存');

  return h('div', { class: 'node ' + n.state + (isCurrent ? ' current' : '') },
    h('div', { class: 'row' },
      h('span', { class: 'dot' }),
      h('span', { class: 'title' }, n.label_zh + ' / ' + n.label_en),
      badge(n.state),
      isCurrent ? h('span', { class: 'current-tag' }, '当前节点') : null
    ),
    h('div', { class: 'fields' }, fields),
    h('div', { class: 'actions' }, btn, msg)
  );
}

function renderDetail() {
  const a = apps.find(x => x.id === selectedId);
  if (!a) { detailEl.replaceChildren(h('div', { class: 'empty' }, '请选择左侧的一条申请')); return; }
  const head = h('div', { class: 'head' },
    h('h2', null, a.product_label_zh || a.product_id || '申请'),
    badge(a.status),
    h('span', { class: 'sub' }, 'SME: ' + a.sme_id + ' · package: ' + a.origin_package_id),
    h('button', { class: 'danger', style: 'margin-left:auto', onclick: () => resetApp(a.id) }, '重置(演示)')
  );
  detailEl.replaceChildren.apply(detailEl, [head].concat(a.nodes.map(n => renderNode(a, n))));
}

async function saveNode(appId, nodeCode, refs) {
  const body = {
    customer_note_zh: refs.zh.value || '',
    customer_note_en: refs.en.value || '',
    internal_note: refs.internal.value || '',
    reminder_at: refs.reminder.value || ''
  };
  if (refs.state) body.state = refs.state.value;
  refs.msg.textContent = '保存中…'; refs.msg.className = 'msg';
  try {
    const res = await fetch(API + '/applications/' + appId + '/nodes/' + nodeCode, {
      method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail));
    refs.msg.textContent = '已保存'; refs.msg.className = 'msg ok';
    await load();
  } catch (e) {
    refs.msg.textContent = '失败: ' + e.message; refs.msg.className = 'msg err';
  }
}

async function resetApp(appId) {
  if (!confirm('确定重置这条申请的进度到初始状态?(仅供演示)')) return;
  try {
    const res = await fetch(API + '/applications/' + appId + '/reset', { method: 'POST' });
    if (!res.ok) throw new Error('reset failed');
    await load();
  } catch (e) { alert('重置失败: ' + e.message); }
}

document.getElementById('refresh').addEventListener('click', load);
load();
</script>
</body>
</html>
"""
