# -*- coding: utf-8 -*-
"""자료 색인 index.html 생성. 사용법: python3 _index/gen.py (레포 최상위에서)"""
import json, os, sys, html, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import catalog, chats, guides

# 레포가 공개라 최상위 index.html은 쓰지 않습니다.
# 주소만 치면 자료 목록 전체가 보이게 되므로, 추측 불가 파일명으로 서비스합니다.
OUTNAME = 'jaryo-7q2m4x8b1e.html'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', OUTNAME)

WITH_EXAM = {"중고등 자료", "모의고사"}
NO_COMMON = {"창작"}

def build_guides():
    out = []
    for name, body in guides.GUIDES:
        parts = [body]
        if name not in NO_COMMON:
            parts.append(guides.COMMON)
        if name in WITH_EXAM:
            parts.append(guides.EXAM)
        out.append({"name": name, "text": "\n\n".join(parts)})
    return out

items = [{"f": f, "g": g, "b": b, "l": l, "u": u, "k": k, "n": n}
         for f, g, b, l, u, k, n in catalog.ROWS]
chat_items = [{"p": p, "t": t, "d": d, "id": i} for p, t, d, i in chats.ROWS]
guide_items = build_guides()

# 확인 필요 — 손봐야 하는 것만 (단순 메모는 제외)
TROUBLE = ("같음", "오타", "확인 필요", "오표기", "둘", "⚠", "확장자")
for i in items:
    i["w"] = 1 if (i["n"] and any(t in i["n"] for t in TROUBLE)) else 0
flags = [i for i in items if i["w"]]

DATA = json.dumps({"items": items, "chats": chat_items,
                   "guides": guide_items, "flags": flags},
                  ensure_ascii=False)

TODAY = datetime.date.today().strftime("%Y.%m.%d")

PAGE = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>강동미나 자료 색인</title>
<link href="https://fonts.googleapis.com/css2?family=Jua&display=swap" rel="stylesheet">
<style>
@font-face{font-family:'JuaLocal';src:url('assets/Jua.woff2') format('woff2');
  font-display:swap;font-weight:400;font-style:normal}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
body{margin:0;background:#fff;color:#111;
  font-family:'JuaLocal','Jua','BM JUA_TTF',system-ui,-apple-system,'Malgun Gothic',sans-serif;
  font-size:16px;line-height:1.6}
.wrap{max-width:1100px;margin:0 auto;padding:22px 18px 70px}
h1{font-size:25px;margin:0 0 4px;letter-spacing:-.4px}
.sub{font-size:14px;color:#777;margin:0 0 20px}
.sub b{color:#111;font-weight:normal}

.tabs{display:flex;gap:4px;border-bottom:2px solid #111;margin-bottom:18px;flex-wrap:wrap}
.tab{appearance:none;background:none;border:0;border-bottom:4px solid transparent;
  font:inherit;font-size:16px;color:#888;padding:9px 14px;cursor:pointer;margin-bottom:-2px}
.tab[aria-selected="true"]{color:#111;border-bottom-color:#111}
.tab .c{font-size:12px;color:#aaa;margin-left:4px}

.toolbar{display:flex;gap:9px;flex-wrap:wrap;align-items:center;margin-bottom:14px}
input[type=search]{font:inherit;font-size:16px;padding:9px 13px;border:1.5px solid #111;
  border-radius:3px;min-width:230px;flex:1;background:#fff;color:#111}
input[type=search]::placeholder{color:#aaa}
.chips{display:flex;gap:5px;flex-wrap:wrap}
.chip{appearance:none;background:#fff;border:1.5px solid #ccc;border-radius:999px;
  font:inherit;font-size:14px;padding:5px 13px;cursor:pointer;color:#555}
.chip[aria-pressed="true"]{border-color:#111;color:#111;background:#FFE9F2}

.grp{margin:22px 0 7px;font-size:17px;padding-bottom:5px;border-bottom:1.5px solid #111}
.grp .n{font-size:13px;color:#999;margin-left:6px}
table{width:100%;border-collapse:collapse}
td,th{text-align:left;padding:9px 8px;border-bottom:1px solid #e8e8e8;vertical-align:top}
th{font-size:13px;color:#888;font-weight:normal;border-bottom:1px solid #111;white-space:nowrap}
tr:hover td{background:#fafafa}
.unit{font-size:16px}
.lesson{color:#666;font-size:14px;white-space:nowrap}
.kind{white-space:nowrap;font-size:14px;color:#333}
.file{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:12px;color:#999;
  word-break:break-all;line-height:1.4}
.note{display:block;font-size:13px;color:#888;margin-top:3px;line-height:1.45}
.note.w{color:#C2185B}
a.open{color:#111;text-decoration:none;border-bottom:1.5px solid #111;white-space:nowrap;font-size:14px}
a.open:hover{background:#FFE9F2}
.hide{display:none}
.empty{color:#999;padding:28px 4px;font-size:15px}

details.g{border:1.5px solid #111;border-radius:3px;margin-bottom:9px;background:#fff}
details.g>summary{cursor:pointer;padding:12px 15px;font-size:17px;list-style:none;
  display:flex;justify-content:space-between;align-items:center;gap:10px}
details.g>summary::-webkit-details-marker{display:none}
details.g>summary::after{content:'펼치기';font-size:13px;color:#999}
details.g[open]>summary::after{content:'접기'}
details.g[open]>summary{border-bottom:1px solid #e8e8e8}
.gbody{padding:13px 15px 16px}
.copy{appearance:none;background:#111;color:#fff;border:0;border-radius:3px;font:inherit;
  font-size:14px;padding:8px 16px;cursor:pointer;margin-bottom:11px}
.copy.done{background:#C2185B}
pre.gt{white-space:pre-wrap;word-break:break-word;font-family:inherit;font-size:14.5px;
  line-height:1.75;margin:0;color:#222;background:#fafafa;border-left:3px solid #ddd;padding:13px 15px}
.how{font-size:14px;color:#666;line-height:1.75;margin:0 0 16px;
  border-left:3px solid #111;padding:2px 0 2px 13px}
.how b{color:#111;font-weight:normal}
.foot{margin-top:40px;padding-top:14px;border-top:1px solid #e8e8e8;font-size:13px;color:#aaa}
@media(max-width:620px){
  .wrap{padding:16px 13px 60px}
  h1{font-size:22px}
  .file{display:none}
  td,th{padding:8px 5px}
  input[type=search]{min-width:100%}
  .tab{padding:8px 10px;font-size:15px}
}
</style>
</head>
<body>
<div class="wrap">
<h1>강동미나 자료 색인</h1>
<p class="sub">인터랙션 <b id="cnt1">0</b>개 · 인쇄물 <b id="cnt2">0</b>건 · __TODAY__ 기준</p>

<div class="tabs" role="tablist">
  <button class="tab" role="tab" data-p="p1" aria-selected="true">자료 찾기<span class="c" id="t1"></span></button>
  <button class="tab" role="tab" data-p="p2" aria-selected="false">인쇄물<span class="c" id="t2"></span></button>
  <button class="tab" role="tab" data-p="p3" aria-selected="false">프로젝트 지침<span class="c" id="t3"></span></button>
  <button class="tab" role="tab" data-p="p4" aria-selected="false">확인 필요<span class="c" id="t4"></span></button>
</div>

<section id="p1">
  <div class="toolbar">
    <input type="search" id="q" placeholder="단원명 · 교과서 · 종류로 찾기 (예: 능률 7과, 거꾸로)" autocomplete="off">
    <div class="chips" id="chips"></div>
  </div>
  <div id="list"></div>
</section>

<section id="p2" class="hide">
  <p class="how">대화에서 만든 인쇄물입니다. 파일이 그 대화 안에 있어서 <b>열기</b>를 누르면 대화가 열려요.
  거기서 파일을 다시 받거나 고쳐 달라고 하면 됩니다.</p>
  <div class="toolbar">
    <input type="search" id="q2" placeholder="제목 · 내용으로 찾기 (예: 단어장, 시간표)" autocomplete="off">
  </div>
  <div id="list2"></div>
</section>

<section id="p3" class="hide">
  <p class="how"><b>복사하기</b>를 누른 다음, 클로드에서 그 프로젝트를 열고 프로젝트 지침 칸에 붙여 넣으면 됩니다.
  지침은 제가 읽는 내용이라 길어요. 준이 읽으실 필요는 없어요.</p>
  <div id="list3"></div>
</section>

<section id="p4" class="hide">
  <p class="how">내용이 겹치거나 파일명과 내용이 안 맞는 것들입니다.
  <b>클래스룸 링크가 깨질 수 있어서 고치지 않고 표시만 해 뒀어요.</b> 지울 것을 골라 주시면 정리합니다.</p>
  <div id="list4"></div>
</section>

<p class="foot">파일을 추가하면 <span class="file">_index/catalog.py</span>에 한 줄 넣고 다시 만들면 됩니다.</p>
</div>

<script>
const D = __DATA__;
const E = s => String(s==null?'':s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const $ = i => document.getElementById(i);

const ORDER = ['중1','중2','중3','고1','문법 개념','초등','관리'];
const gkey = it => it.b ? it.g + ' · ' + it.b : it.g;

// ── 탭
document.querySelectorAll('.tab').forEach(t => t.onclick = () => {
  document.querySelectorAll('.tab').forEach(x => {
    const on = x === t;
    x.setAttribute('aria-selected', on);
    $(x.dataset.p).classList.toggle('hide', !on);
  });
});

// ── 자료 찾기
const groups = [];
D.items.forEach(it => {
  let g = groups.find(x => x.key === gkey(it));
  if (!g) { g = {key: gkey(it), g: it.g, rows: []}; groups.push(g); }
  g.rows.push(it);
});
groups.sort((a,b) => {
  const d = ORDER.indexOf(a.g) - ORDER.indexOf(b.g);
  return d !== 0 ? d : a.key.localeCompare(b.key, 'ko');
});

const FILTERS = ORDER.filter(o => D.items.some(i => i.g === o));
let active = '';
$('chips').innerHTML = FILTERS.map(f =>
  `<button class="chip" data-f="${E(f)}" aria-pressed="false">${E(f)}</button>`).join('');
$('chips').onclick = e => {
  const b = e.target.closest('.chip'); if (!b) return;
  active = (active === b.dataset.f) ? '' : b.dataset.f;
  document.querySelectorAll('.chip').forEach(c =>
    c.setAttribute('aria-pressed', c.dataset.f === active));
  render();
};

function row(it) {
  return `<tr><td class="lesson">${E(it.l)}</td>`
    + `<td><span class="unit">${E(it.u)}</span>`
    + (it.n ? `<span class="note${it.w ? ' w' : ''}">${E(it.n)}</span>` : '')
    + `<div class="file">${E(it.f)}</div></td>`
    + `<td class="kind">${E(it.k)}</td>`
    + `<td><a class="open" href="${E(it.f)}" target="_blank" rel="noopener">열기</a></td></tr>`;
}

function tokens(v) { return v.trim().toLowerCase().split(/\s+/).filter(Boolean); }
function hit(hay, ts) { const h = hay.toLowerCase(); return ts.every(t => h.includes(t)); }

function render() {
  const ts = tokens($('q').value);
  let n = 0, out = '';
  groups.forEach(g => {
    const rows = g.rows.filter(it => {
      if (active && it.g !== active) return false;
      if (!ts.length) return true;
      return hit([it.f,it.g,it.b,it.l,it.u,it.k,it.n].join(' '), ts);
    });
    if (!rows.length) return;
    n += rows.length;
    out += `<h2 class="grp">${E(g.key)}<span class="n">${rows.length}</span></h2>`
      + `<table><tr><th>과</th><th>단원</th><th>종류</th><th></th></tr>`
      + rows.map(row).join('') + `</table>`;
  });
  $('list').innerHTML = out || `<p class="empty">찾는 자료가 없어요. 다른 말로 찾아보세요.</p>`;
  $('t1').textContent = n;
}
$('q').oninput = render;

// ── 인쇄물
function render2() {
  const ts = tokens($('q2').value);
  const by = {};
  D.chats.forEach(c => {
    if (ts.length && !hit(c.p+' '+c.t+' '+c.d, ts)) return;
    (by[c.p] = by[c.p] || []).push(c);
  });
  let out = '', n = 0;
  Object.keys(by).forEach(p => {
    n += by[p].length;
    out += `<h2 class="grp">${E(p)}<span class="n">${by[p].length}</span></h2><table>`
      + `<tr><th>제목</th><th>들어 있는 것</th><th></th></tr>`
      + by[p].map(c => `<tr><td class="unit">${E(c.t)}</td><td class="kind">${E(c.d)}</td>`
        + `<td><a class="open" href="https://claude.ai/chat/${E(c.id)}" target="_blank" rel="noopener">열기</a></td></tr>`).join('')
      + `</table>`;
  });
  $('list2').innerHTML = out || `<p class="empty">찾는 자료가 없어요.</p>`;
  $('t2').textContent = n;
}
$('q2').oninput = render2;

// ── 지침
$('list3').innerHTML = D.guides.map((g,i) =>
  `<details class="g"><summary>${E(g.name)}</summary><div class="gbody">`
  + `<button class="copy" data-i="${i}">복사하기</button>`
  + `<pre class="gt">${E(g.text)}</pre></div></details>`).join('');
$('t3').textContent = D.guides.length;
$('list3').onclick = async e => {
  const b = e.target.closest('.copy'); if (!b) return;
  const t = D.guides[+b.dataset.i].text;
  try { await navigator.clipboard.writeText(t); }
  catch (_) {
    const ta = document.createElement('textarea');
    ta.value = t; ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.appendChild(ta); ta.select();
    try { document.execCommand('copy'); } catch (_) {}
    ta.remove();
  }
  b.textContent = '복사했어요'; b.classList.add('done');
  setTimeout(() => { b.textContent = '복사하기'; b.classList.remove('done'); }, 2000);
};

// ── 확인 필요
$('list4').innerHTML = `<table><tr><th>자료</th><th>무엇이 문제인지</th><th></th></tr>`
  + D.flags.map(it => `<tr><td><span class="unit">${E(it.u || it.g)}</span>`
    + `<div class="file">${E(it.f)}</div></td>`
    + `<td class="kind">${E(it.n)}</td>`
    + `<td><a class="open" href="${E(it.f)}" target="_blank" rel="noopener">열기</a></td></tr>`).join('')
  + `</table>`;
$('t4').textContent = D.flags.length;

$('cnt1').textContent = D.items.length;
$('cnt2').textContent = D.chats.length;
render(); render2();
</script>
</body>
</html>
"""

page = PAGE.replace("__DATA__", DATA).replace("__TODAY__", TODAY)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(page)
print("index.html 생성:", round(len(page.encode())/1024, 1), "KB")
print("인터랙션", len(items), "· 인쇄물", len(chat_items), "· 지침", len(guide_items), "· 확인필요", len(flags))
