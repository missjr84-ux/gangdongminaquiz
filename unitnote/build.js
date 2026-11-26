// 강동미나 중고등부 단원노트 PPT 빌더 — node build.js data.json out_dir "Lesson N  제목" 파일접두어  (unitnote/HANDOFF.md 참고)
const pptxgen = require("pptxgenjs");
const fs = require("fs");
const D = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const OUT = process.argv[3];
const LESSON = process.argv[4] || "Lesson 7  Save Earth, Save Us";
const FILE = process.argv[5] || "중1_능률_7과";

const W = 8.27, H = 11.69, MX = 0.6, CW = W - 2 * MX, BOTTOM = 10.95;
const HEAD = "Jua", BODY = "Malgun Gothic";
const INK = "000000", GRAY = "666666", RULE = "9A9A9A";
const ACAD = D.acad || "강동미나 중고등부 · 중1 능률(김기택)";

// ---------- text size estimate (inches)
function units(s) { let u = 0; for (const ch of s) u += /[ㄱ-힣←-⇿]/.test(ch) ? 1.0 : (/[A-Z]/.test(ch) ? 0.64 : (ch === " " ? 0.27 : 0.49)); return u; }
function lines(s, pt, w) { const per = w / (pt / 72); return Math.max(1, Math.ceil(units(s) / (per * 0.97))); }

function makePres() {
  const p = new pptxgen();
  p.defineLayout({ name: "A4P", width: W, height: H });
  p.layout = "A4P";
  p.theme = { headFontFace: HEAD, bodyFontFace: BODY };
  p.defineSlideMaster({
    title: "NOTE", background: { color: "FFFFFF" },
    objects: [
      { text: { text: LESSON, options: { x: MX, y: 0.3, w: 4.6, h: 0.32, fontFace: HEAD, fontSize: 12, color: INK, margin: 0 } } },
      { text: { text: ACAD, options: { x: W - MX - 3.6, y: 0.3, w: 3.6, h: 0.32, fontFace: HEAD, fontSize: 11, color: GRAY, align: "right", margin: 0 } } },
    ],
    slideNumber: { x: W / 2 - 0.3, y: 11.12, w: 0.6, h: 0.3, fontFace: HEAD, fontSize: 11, color: INK, align: "center" },
  });
  return p;
}

// ---------- shared pieces
function title(s, t, withName) {
  s.addText(t, { x: MX, y: 0.78, w: withName ? 4.3 : CW, h: 0.5, fontFace: HEAD, fontSize: 22, color: INK, margin: 0, isTextBox: true, valign: "middle" });
  if (withName) s.addText("이름 ____________   날짜 ________", { x: W - MX - 2.9, y: 0.86, w: 2.9, h: 0.36, fontFace: BODY, fontSize: 11, color: INK, align: "right", margin: 0, isTextBox: true });
}
function guide(s, t, y) {
  const h = 0.3 * lines(t, 12, CW) + 0.08;
  s.addText(t, { x: MX, y, w: CW, h, fontFace: BODY, fontSize: 12, color: INK, margin: 0, isTextBox: true, valign: "top", lineSpacingMultiple: 1.2 });
  return y + h + 0.12;
}
function rule(s, x, y, w) { s.addShape("line", { x, y, w, h: 0, line: { color: RULE, width: 0.75 } }); }

// runs with [blank] markers → student: (   ) / answer: bold underlined
function blankRuns(str, answer, pt) {
  const out = []; const re = /\[([^\]]+)\]/g; let i = 0, m;
  while ((m = re.exec(str))) {
    if (m.index > i) out.push({ text: str.slice(i, m.index), options: { fontSize: pt, fontFace: BODY } });
    if (answer) out.push({ text: m[1], options: { fontSize: pt, fontFace: BODY, bold: true, underline: { style: "sng" } } });
    else out.push({ text: "(" + " ".repeat(Math.max(14, Math.round(units(m[1]) * 3.6))) + ")", options: { fontSize: pt, fontFace: BODY } });
    i = re.lastIndex;
  }
  if (i < str.length) out.push({ text: str.slice(i), options: { fontSize: pt, fontFace: BODY } });
  return out;
}
function fillAns(str) { return str.replace(/\[([^\]]+)\]/g, "$1"); }

// runs highlighting substrings (underline or bold)
function markRuns(text, keys, style, pt) {
  const spans = [];
  for (const k of keys) { const i = text.indexOf(k); if (i >= 0) spans.push([i, i + k.length]); }
  spans.sort((a, b) => a[0] - b[0]);
  const out = []; let i = 0;
  for (const [a, b] of spans) {
    if (a < i) continue;
    if (a > i) out.push({ text: text.slice(i, a), options: { fontSize: pt, fontFace: BODY } });
    const o = { fontSize: pt, fontFace: BODY };
    if (style === "u") o.underline = { style: "sng" }; else { o.bold = true; o.underline = { style: "sng" }; }
    out.push({ text: text.slice(a, b), options: o }); i = b;
  }
  if (i < text.length) out.push({ text: text.slice(i), options: { fontSize: pt, fontFace: BODY } });
  return out;
}

// slashed chunks with key spans bold (spans found in the plain sentence)
function slashRuns(r, pt) {
  const plain = r.en; const mark = new Array(plain.length).fill(false);
  for (const [, k] of r.key) { const i = plain.indexOf(k); if (i >= 0) for (let j = i; j < i + k.length; j++) mark[j] = true; }
  const segs = []; // [text, bold]
  const push = (t, b) => { if (segs.length && segs[segs.length - 1][1] === b) segs[segs.length - 1][0] += t; else segs.push([t, b]); };
  if (!r.ch) { for (let j = 0; j < plain.length; j++) push(plain[j], mark[j]); }
  else {
    // place each chunk by searching the sentence, so quotes or spacing differences don't shift letters
    let pos = 0; const cuts = []; let ok = true;
    for (const c of r.ch) {
      const t = c[0].trim(); const at = plain.indexOf(t, pos);
      if (at < 0) { ok = false; break; }
      cuts.push(at + t.length); pos = at + t.length;
    }
    let ci = 0;
    for (let j = 0; j < plain.length; j++) {
      push(plain[j], mark[j]);
      if (ok && ci < cuts.length - 1 && j + 1 === cuts[ci]) {
        ci++;
        // skip the following space, put the slash there
        if (plain[j + 1] === " ") { push(" / ", false); j++; } else push(" / ", false);
      }
    }
  }
  return segs.map(([t, b]) => ({ text: t, options: b ? { fontSize: pt, fontFace: BODY, bold: true, underline: { style: "sng" } } : { fontSize: pt, fontFace: BODY } }));
}

// ---------- flow pagination: items {h, draw(s,y)}
function flow(pres, sectionTitle, guideText, items, withName, toc, tocLabel, tocNote) {
  let s = null, y = 0, first = true, start = null;
  const newPage = () => {
    s = pres.addSlide({ masterName: "NOTE" });
    pres._count = (pres._count || 0) + 1;
    if (start === null) start = pres._count;
    title(s, sectionTitle + (first ? "" : "  (이어서)"), first && withName);
    y = 1.42;
    if (first && guideText) y = guide(s, guideText, y);
    first = false;
  };
  newPage();
  items.forEach((it, idx) => {
    if (it.newPage && y > 2.0) newPage();
    const nx = it.keepNext && items[idx + 1] ? items[idx + 1].h : 0;
    if (y + it.h + nx > BOTTOM) newPage();
    it.draw(s, y); y += it.h;
  });
  const end = pres._count;
  if (toc) toc.push([start === end ? String(start) : `${start}–${end}`, tocLabel, tocNote]);
}

// ---------- sections
function wordTables(pres, list, label, answer, toc, note, perPage) {
  const colW = [0.5, 1.75, 2.42, 1.2, 1.2];
  const hb = { fontFace: HEAD, fontSize: 13, align: "center", border: [{ pt: 0 }, { pt: 0 }, { pt: 1.5, color: INK }, { pt: 0 }] };
  const sym = (a, b) => ({ text: [{ text: a, options: { fontFace: HEAD, fontSize: 13 } }, { text: b, options: { fontFace: BODY, fontSize: 12 } }], options: hb });
  const head = [{ text: "", options: hb }, { text: label, options: hb }, { text: "뜻", options: hb }, sym("유의어 ", "(=)"), sym("반의어 ", "(↔)")];
  const pages = [];
  for (let i = 0; i < list.length; i += perPage) pages.push(list.slice(i, i + perPage));
  let startNo = null;
  pages.forEach((pg, pi) => {
    const s = pres.addSlide({ masterName: "NOTE" }); pres._count++;
    if (startNo === null) startNo = pres._count;
    title(s, (label === "숙어" ? "숙어 노트" : "단어 노트") + (pi ? "  (이어서)" : ""), pi === 0 && !answer);
    let y = 1.42;
    if (pi === 0) y = guide(s, answer ? (D.wordNoteAns || "정답 — 뜻은 교과서에 나온 뜻을 모두 적었어요. '—'는 짝으로 외울 유의어·반의어가 없는 단어예요.")
      : "왼쪽 영단어를 보고 뜻, 유의어(=), 반의어(↔)를 쓰세요. '없음'이라고 적힌 칸은 비워 두세요.", y);
    const bd = { type: "solid", pt: 0.75, color: GRAY };
    const rows = [head];
    pg.forEach((w, k) => {
      const n = pages.slice(0, pi).reduce((a, b) => a + b.length, 0) + k + 1;
      const cell = (t, o = {}) => ({ text: t, options: Object.assign({ fontFace: BODY, fontSize: 12, valign: "middle", border: [bd, bd, bd, bd] }, o) });
      const sa = (v) => answer ? cell(v || "—", { align: "center", fontSize: 11 }) : cell(v ? "" : "없음", { align: "center", fontSize: 11, color: "8A8A8A" });
      rows.push([
        cell(String(n), { align: "center", fontFace: HEAD, fontSize: 12 }),
        cell(w.w, { fontSize: 13, bold: true }),
        answer ? cell(w.m, { fontSize: 11 }) : cell(""),
        sa(w.syn), sa(w.ant),
      ]);
    });
    const rowH = Math.min(0.56, (BOTTOM - y - 0.45) / pg.length);
    s.addTable(rows, { x: MX, y, w: CW, colW, rowH: [0.42].concat(pg.map(() => rowH)), margin: [0.03, 0.06, 0.03, 0.06] });
  });
  toc.push([pages.length > 1 ? `${startNo}–${pres._count}` : String(startNo), label === "숙어" ? "숙어 노트" : "단어 노트", note]);
}

function defsSection(pres, answer, toc) {
  const items = D.defs.map((d, i) => {
    const L = lines(d.d, 12.5, CW - 2.15);
    const h = Math.max(0.4, 0.3 * L + 0.1) + 0.56;
    return {
      h, draw: (s, y) => {
        s.addText(`${i + 1}`, { x: MX, y, w: 0.4, h: 0.34, fontFace: HEAD, fontSize: 14, margin: 0, isTextBox: true });
        s.addText(d.w, { x: MX + 0.4, y, w: 1.7, h: 0.34, fontFace: BODY, fontSize: 13, bold: true, margin: 0, isTextBox: true });
        s.addText(d.d, { x: MX + 2.15, y, w: CW - 2.15, h: 0.3 * L + 0.05, fontFace: BODY, fontSize: 12.5, margin: 0, isTextBox: true, valign: "top", lineSpacingMultiple: 1.15 });
        const y2 = y + Math.max(0.42, 0.3 * L + 0.12);
        s.addText("해석", { x: MX + 0.4, y: y2 + 0.06, w: 0.6, h: 0.32, fontFace: HEAD, fontSize: 12, margin: 0, isTextBox: true });
        if (answer) s.addText(d.ko, { x: MX + 1.05, y: y2 + 0.04, w: CW - 1.05, h: 0.36, fontFace: BODY, fontSize: 12, margin: 0, isTextBox: true });
        else rule(s, MX + 1.05, y2 + 0.4, CW - 1.05);
      }
    };
  });
  flow(pres, "영영풀이 노트", answer ? "정답 — 해석은 이 정도 뜻이면 맞은 걸로 봐요."
    : "영영풀이를 소리 내어 읽고, 밑줄에 우리말로 해석을 쓰세요. 뜻을 정해 주는 핵심어에 동그라미를 치며 읽으면 쉬워요.",
    items, !answer, toc, "영영풀이 노트", `${D.defs.length}개 · 영영풀이 읽고 해석 쓰기`);
}

function grammarSection(pres, answer, toc) {
  D.grammar.forEach((g, gi) => {
    const items = [];
    // formula box
    items.push({ h: 0.88, draw: (s, y) => {
      s.addShape("rect", { x: MX, y, w: CW, h: 0.72, line: { color: INK, width: 1.25 }, fill: { color: "FFFFFF" } });
      s.addText(g.formula, { x: MX + 0.2, y, w: CW - 0.4, h: 0.72, fontFace: HEAD, fontSize: 17, align: "center", valign: "middle", margin: 0, isTextBox: true });
    } });
    items.push({ h: 0.45, keepNext: true, draw: (s, y) => s.addText(answer ? "개념 빈칸 정답" : "개념 빈칸 채우기 — 괄호 안에 알맞은 말을 쓰세요.", { x: MX, y, w: CW, h: 0.36, fontFace: HEAD, fontSize: 14, margin: 0, isTextBox: true }) });
    g.concept.forEach(([k, v]) => {
      const txt = answer ? fillAns(v) : v.replace(/\[([^\]]+)\]/g, (m, a) => "(" + " ".repeat(Math.max(14, Math.round(units(a) * 3.6))) + ")");
      const L = lines(txt, 12, CW - 1.5);
      const h = 0.33 * L + 0.2;
      items.push({ h, draw: (s, y) => {
        s.addText(k, { x: MX, y: y + 0.02, w: 1.4, h: 0.34, fontFace: HEAD, fontSize: 12.5, margin: 0, isTextBox: true, valign: "top" });
        s.addText(blankRuns(v, answer, 12), { x: MX + 1.5, y, w: CW - 1.5, h: 0.35 * L + 0.06, fontFace: BODY, margin: 0, isTextBox: true, valign: "top", lineSpacingMultiple: 1.4 });
        rule(s, MX, y + h - 0.1, CW);
      } });
    });
    // 영작 10
    items.push({ h: 0.5, newPage: true, keepNext: true, draw: (s, y) => s.addText(answer ? "예문 영작 정답" : "예문 영작 — 주어진 말을 써서 영어 문장으로 쓰세요. (서술형 10문제)", { x: MX, y: y + 0.08, w: CW, h: 0.36, fontFace: HEAD, fontSize: 14, margin: 0, isTextBox: true }) });
    g.write.forEach(([ko, hint, en], wi) => {
      const two = !answer && units(en) > 46;
      const h = answer ? 0.84 : (two ? 1.24 : 0.84);
      items.push({ h, draw: (s, y) => {
        s.addText(`${wi + 1}`, { x: MX, y, w: 0.4, h: 0.34, fontFace: HEAD, fontSize: 14, margin: 0, isTextBox: true });
        s.addText([{ text: ko, options: { fontSize: 12.5, fontFace: BODY } }, { text: "   주어진 말: " + hint, options: { fontSize: 11, color: GRAY, fontFace: BODY } }],
          { x: MX + 0.4, y, w: CW - 0.4, h: 0.34, fontFace: BODY, margin: 0, isTextBox: true, fit: "none" });
        if (answer) s.addText(en, { x: MX + 0.4, y: y + 0.42, w: CW - 0.4, h: 0.36, fontFace: BODY, fontSize: 13, bold: true, margin: 0, isTextBox: true });
        else { rule(s, MX + 0.4, y + 0.72, CW - 0.4); if (two) rule(s, MX + 0.4, y + 1.12, CW - 0.4); }
      } });
    });
    flow(pres, g.short, null, items, !answer, toc, g.title, "개념 빈칸 · 예문 영작 10문제");
  });
}

function readingStudy(pres, answer, toc) {
  const items = []; let para = null;
  for (const r of D.rows) {
    if (r.para !== para) {
      para = r.para;
      const pt = para.replace(/\s*\(.*\)\s*$/, "");
      items.push({ h: 0.5, keepNext: true, draw: (s, y) => s.addText(pt, { x: MX, y: y + 0.06, w: CW, h: 0.36, fontFace: HEAD, fontSize: 15, margin: 0, isTextBox: true }) });
    }
    const en = answer ? (r.ch ? r.ch.map(c => c[0]).join(" / ") : r.en) : r.en;
    const L = lines(en, 13, CW - 0.4);
    const eh = 0.44 * L;
    if (answer) {
      const tipL = r.tip ? lines("포인트  " + r.tip, 11, CW - 0.4) : 0;
      const kL = lines(r.kr, 12, CW - 0.4);
      const h = eh + 0.3 * kL + 0.08 + (tipL ? 0.26 * tipL + 0.04 : 0) + 0.2;
      items.push({ h, draw: (s, y) => {
        s.addText(String(r.n), { x: MX, y: y + 0.02, w: 0.4, h: 0.34, fontFace: HEAD, fontSize: 13, margin: 0, isTextBox: true });
        s.addText(slashRuns(r, 13), { x: MX + 0.4, y, w: CW - 0.4, h: eh, fontFace: BODY, margin: 0, isTextBox: true, valign: "top", lineSpacingMultiple: 1.5 });
        s.addText(r.kr, { x: MX + 0.4, y: y + eh, w: CW - 0.4, h: 0.3 * kL + 0.05, fontFace: BODY, fontSize: 12, margin: 0, isTextBox: true, valign: "top" });
        if (tipL) s.addText([{ text: "포인트  ", options: { fontFace: HEAD, fontSize: 11 } }, { text: r.tip, options: { fontSize: 11, fontFace: BODY } }],
          { x: MX + 0.4, y: y + eh + 0.3 * kL + 0.08, w: CW - 0.4, h: 0.26 * tipL + 0.04, fontFace: BODY, color: GRAY, margin: 0, isTextBox: true, valign: "top" });
      } });
    } else {
      const kt = units(r.kr) > 38;
      const h = eh + 0.58 + (kt ? 0.42 : 0);
      items.push({ h, draw: (s, y) => {
        s.addText(String(r.n), { x: MX, y, w: 0.4, h: eh, fontFace: HEAD, fontSize: 13, margin: 0, isTextBox: true, valign: "top", lineSpacingMultiple: 2.0 });
        s.addText(r.en, { x: MX + 0.4, y, w: CW - 0.4, h: eh, fontFace: BODY, fontSize: 13, margin: 0, isTextBox: true, valign: "top", lineSpacingMultiple: 2.0 });
        s.addText("해석", { x: MX + 0.4, y: y + eh + 0.12, w: 0.6, h: 0.32, fontFace: HEAD, fontSize: 12, margin: 0, isTextBox: true });
        rule(s, MX + 1.05, y + eh + 0.46, CW - 1.05);
        if (kt) rule(s, MX + 1.05, y + eh + 0.88, CW - 1.05);
      } });
    }
  }
  flow(pres, answer ? "본문 정답  구문 분석 + 해석" : "본문 노트  구문 분석 + 해석",
    answer ? "끊어 읽기(/)는 이렇게 끊으면 돼요. 굵은 밑줄은 핵심 표현이에요. 회색 '포인트'는 수업 때 짚어 줄 문법이에요."
      : "직접 구문 분석 + 해석 하세요. 영어 문장 위에 끊어 읽기(/)를 하고 주어(S)·동사(V)·목적어(O)·보어(C)를 표시한 다음, 밑줄에 해석을 쓰세요.",
    items, !answer, toc, answer ? "본문 정답" : "본문 구문 분석 + 해석", answer ? `${D.rows.length}문장 · 끊어 읽기·해석·포인트 (거꾸로 영작 답 포함)` : `${D.rows.length}문장 · 영어 보고 분석·해석`);
}

function readingWrite(pres, toc) {
  const items = []; let para = null;
  for (const r of D.rows) {
    if (r.para !== para) {
      para = r.para;
      const pt = para.replace(/\s*\(.*\)\s*$/, "");
      items.push({ h: 0.5, keepNext: true, draw: (s, y) => s.addText(pt, { x: MX, y: y + 0.06, w: CW, h: 0.36, fontFace: HEAD, fontSize: 15, margin: 0, isTextBox: true }) });
    }
    const L = lines(r.kr, 12.5, CW - 0.4);
    const kh = 0.34 * L + 0.04;
    const two = units(r.en) > 44;
    const h = kh + (two ? 0.96 : 0.56) + 0.08;
    items.push({ h, draw: (s, y) => {
      s.addText(String(r.n), { x: MX, y, w: 0.4, h: 0.34, fontFace: HEAD, fontSize: 13, margin: 0, isTextBox: true });
      s.addText(markRuns(r.kr, r.key.map(k => k[0]), "u", 12.5), { x: MX + 0.4, y, w: CW - 0.4, h: kh, fontFace: BODY, margin: 0, isTextBox: true, valign: "top", lineSpacingMultiple: 1.2 });
      rule(s, MX + 0.4, y + kh + 0.48, CW - 0.4);
      if (two) rule(s, MX + 0.4, y + kh + 0.88, CW - 0.4);
    } });
  }
  flow(pres, "본문 노트  거꾸로 영작", "한글을 보고 영어로 쓰세요. 밑줄 친 부분은 핵심 표현이에요 — 다 쓴 다음, 그 부분을 영어로 쓴 곳에 형광펜을 칠하세요.",
    items, true, toc, "본문 거꾸로 영작", `${D.rows.length}문장 · 한글 보고 영작 + 핵심 표현 형광펜`);
}

function cover(pres, s, toc, answer) {
  s.addText(LESSON.replace("  ", "\n"), { x: MX, y: 1.2, w: CW, h: 1.5, fontFace: HEAD, fontSize: 34, margin: 0, isTextBox: true, valign: "top", lineSpacingMultiple: 1.1 });
  s.addText(answer ? "단원 노트 정답 (선생님용)" : "단원 노트", { x: MX, y: 2.8, w: CW, h: 0.45, fontFace: HEAD, fontSize: 18, color: GRAY, margin: 0, isTextBox: true });
  if (!answer) s.addText("학년·반 ________     이름 ________________", { x: MX, y: 3.45, w: CW, h: 0.4, fontFace: BODY, fontSize: 13, margin: 0, isTextBox: true });
  const bd = { type: "solid", pt: 0.75, color: GRAY };
  const hb = { fontFace: HEAD, fontSize: 13, align: "center", border: [{ pt: 0 }, { pt: 0 }, { pt: 1.5, color: INK }, { pt: 0 }] };
  const rows = [[{ text: "쪽", options: hb }, { text: "내용", options: hb }, { text: "하는 일", options: hb }]];
  toc.forEach(([p, a, b]) => rows.push([
    { text: p, options: { fontFace: HEAD, fontSize: 13, align: "center", valign: "middle", border: [bd, bd, bd, bd] } },
    { text: a, options: { fontFace: BODY, fontSize: 12.5, bold: true, valign: "middle", border: [bd, bd, bd, bd] } },
    { text: b, options: { fontFace: BODY, fontSize: 12, valign: "middle", border: [bd, bd, bd, bd] } },
  ]));
  s.addTable(rows, { x: MX, y: 4.3, w: CW, colW: [1.0, 2.75, 3.32], rowH: [0.45].concat(toc.map(() => 0.55)), margin: [0.03, 0.08, 0.03, 0.08] });
  const ty = 4.3 + 0.45 + toc.length * 0.55 + 0.35;
  s.addText(answer ? "학생용 노트와 쪽 순서가 같아요. 수업 전에 선생님이 보관하세요."
    : "정답은 따로 있어요. 다 풀고 선생님께 확인받으세요.", { x: MX, y: ty, w: CW, h: 0.4, fontFace: BODY, fontSize: 12, margin: 0, isTextBox: true });
}

async function build(answer) {
  const pres = makePres(); pres._count = 0;
  const cv = pres.addSlide({ masterName: "NOTE" }); pres._count++;
  const toc = [];
  wordTables(pres, D.words, "단어", answer, toc, `${D.words.length}개 · 뜻·유의어·반의어 쓰기`, 15);
  wordTables(pres, D.idioms, "숙어", answer, toc, `${D.idioms.length}개 · 뜻·유의어·반의어 쓰기`, D.idioms.length > 15 ? Math.ceil(D.idioms.length / 2) : 15);
  if (D.defs && D.defs.length) defsSection(pres, answer, toc);
  grammarSection(pres, answer, toc);
  if (D.rows && D.rows.length) { readingStudy(pres, answer, toc); if (!answer) readingWrite(pres, toc); }
  cover(pres, cv, toc, answer);
  const fn = `${OUT}/${FILE}_단원노트${answer ? "_정답" : ""}.pptx`;
  await pres.writeFile({ fileName: fn });
  console.log(fn, pres._count, "pages");
}
(async () => { await build(false); await build(true); })();
