import json, re, sys
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.cell.rich_text import CellRichText, TextBlock
from openpyxl.cell.text import InlineFont

D = json.load(open(sys.argv[1]))
OUT = sys.argv[2]
LESSON = sys.argv[3]
H, B = "Jua", "Malgun Gothic"
thin = Side(style="thin", color="777777")
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
HEADB = Border(bottom=Side(style="medium", color="000000"))
wrap = Alignment(wrap_text=True, vertical="center")
center = Alignment(horizontal="center", vertical="center", wrap_text=True)

wb = Workbook(); wb.remove(wb.active)

def sheet(name, title, guide, head, widths):
    ws = wb.create_sheet(name)
    ws["A1"] = f"{LESSON} · {title}"; ws["A1"].font = Font(name=H, size=16)
    ws["A2"] = guide; ws["A2"].font = Font(name=B, size=11)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(head))
    ws["A2"].alignment = Alignment(wrap_text=True, vertical="top"); ws.row_dimensions[2].height = 34
    for i, (h, w) in enumerate(zip(head, widths), 1):
        c = ws.cell(row=4, column=i, value=h); c.font = Font(name=H, size=12); c.alignment = center; c.border = HEADB
        ws.column_dimensions[chr(64 + i)].width = w
    ws.print_title_rows = "4:4"
    ws.page_setup.paperSize = ws.PAPERSIZE_A4; ws.page_setup.orientation = "portrait"
    ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0; ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.oddFooter.center.text = "&P"; ws.oddHeader.right.text = D.get("acad", "강동미나 중고등부")
    ws.freeze_panes = "A5"
    return ws

def row(ws, r, vals, h=30, styles=None):
    for i, v in enumerate(vals, 1):
        c = ws.cell(row=r, column=i, value=v); c.font = Font(name=B, size=12); c.alignment = wrap; c.border = BOX
        if styles and i in styles: styles[i](c)
    ws.row_dimensions[r].height = h

gray = lambda c: (setattr(c, "font", Font(name=B, size=11, color="8A8A8A")), setattr(c, "alignment", center))
bold = lambda c: setattr(c, "font", Font(name=B, size=12, bold=True))
ctr = lambda c: setattr(c, "alignment", center)

def words(name, title, lst, answer):
    ws = sheet(name, title, ("정답 — '—'는 짝으로 외울 유의어·반의어가 없는 단어" if answer else
              "영단어를 보고 뜻·유의어(=)·반의어(↔)를 쓰세요. '없음' 칸은 비워 두세요."),
              ["번호", "영단어", "뜻", "유의어 (=)", "반의어 (↔)"], [6, 20, 30, 18, 18])
    for i, w in enumerate(lst, 1):
        if answer: vals = [i, w["w"], w["m"], w["syn"] or "—", w["ant"] or "—"]; st = {1: ctr, 2: bold, 4: ctr, 5: ctr}
        else: vals = [i, w["w"], "", "" if w["syn"] else "없음", "" if w["ant"] else "없음"]; st = {1: ctr, 2: bold, 4: gray, 5: gray}
        row(ws, i + 4, vals, 32, st)

for answer in (False, True):
    tag = "정답_" if answer else ""
    words(tag + "단어", "단어" + (" 정답" if answer else ""), D["words"], answer)
    words(tag + "숙어", "숙어" + (" 정답" if answer else ""), D["idioms"], answer)
    ws = sheet(tag + "영영풀이", "영영풀이" + (" 정답" if answer else ""),
               "해석은 이 정도 뜻이면 맞음" if answer else "영영풀이를 읽고 해석을 쓰세요.",
               ["번호", "단어", "영영풀이", "해석"], [6, 16, 46, 40])
    for i, d in enumerate(D["defs"], 1):
        row(ws, i + 4, [i, d["w"], d["d"], d["ko"] if answer else ""], 40, {1: ctr, 2: bold})
    ws = sheet(tag + "핵심문법", "핵심문법" + (" 정답" if answer else ""),
               "개념 빈칸 정답과 예문 영작 정답" if answer else "괄호 안에 알맞은 말을 쓰고, 예문을 영작하세요.",
               ["구분", "항목", "내용", "주어진 말", "영작"], [14, 16, 56, 22, 44])
    r = 5
    for g in D["grammar"]:
        c = ws.cell(row=r, column=1, value=g["title"]); c.font = Font(name=H, size=13); ws.row_dimensions[r].height = 26; r += 1
        for k, v in g["concept"]:
            txt = re.sub(r"\[([^\]]+)\]", (lambda m: m.group(1)) if answer else (lambda m: "(" + " " * max(8, len(m.group(1)) * 2) + ")"), v)
            row(ws, r, ["개념", k, txt, "", ""], 34, {2: bold}); r += 1
        for i, (ko, hint, en) in enumerate(g["write"], 1):
            row(ws, r, [f"영작 {i}", "", ko, hint, en if answer else ""], 36); r += 1
        r += 1
    if not D["rows"]:
        continue
    ws = sheet(tag + "본문", "본문" + (" 정답" if answer else ""),
               "끊어 읽기·해석·포인트, 거꾸로 영작 답" if answer else
               "구문 분석+해석: 영어 보고 해석 쓰기 / 거꾸로 영작: 밑줄 친 한글은 핵심 표현 — 영어로 쓴 뒤 형광펜",
               ["번호", "문단", "영어", "해석", "거꾸로 영작"] if not answer else ["번호", "문단", "끊어 읽기", "해석", "포인트 · 핵심 표현"],
               [6, 14, 48, 40, 44])
    for i, rr in enumerate(D["rows"], 1):
        para = re.sub(r"\s*\(.*\)\s*$", "", rr["para"])
        if answer:
            sl = " / ".join(c[0] for c in rr["ch"]) if rr["ch"] else rr["en"]
            pt = rr["tip"] + (("\n핵심: " + ", ".join(k[1] for k in rr["key"])) if rr["key"] else "")
            row(ws, i + 4, [rr["n"], para, sl, rr["kr"], pt.strip()], 48, {1: ctr})
        else:
            row(ws, i + 4, [rr["n"], para, rr["en"], "", ""], 44, {1: ctr})
            # 거꾸로 영작 칸 위에 한글(핵심 표현 밑줄)을 넣을 열이 따로 필요해서 해석 열 옆에 둠
            ws.cell(row=i + 4, column=5).value = None
    if not answer:
        ws2 = sheet("본문_거꾸로영작", "본문 거꾸로 영작", "한글을 보고 영어로 쓰세요. 밑줄 친 부분은 핵심 표현 — 다 쓰고 그 부분에 형광펜",
                    ["번호", "문단", "한글", "영작"], [6, 14, 52, 56])
        for i, rr in enumerate(D["rows"], 1):
            para = re.sub(r"\s*\(.*\)\s*$", "", rr["para"])
            row(ws2, i + 4, [rr["n"], para, "", ""], 48, {1: ctr})
            kr = rr["kr"]; spans = sorted((kr.index(k[0]), kr.index(k[0]) + len(k[0])) for k in rr["key"])
            parts, j = [], 0
            for a, b in spans:
                if a < j: continue
                if a > j: parts.append(TextBlock(InlineFont(rFont=B, sz=12), kr[j:a]))
                parts.append(TextBlock(InlineFont(rFont=B, sz=12, u="single"), kr[a:b])); j = b
            if j < len(kr): parts.append(TextBlock(InlineFont(rFont=B, sz=12), kr[j:]))
            ws2.cell(row=i + 4, column=3).value = CellRichText(parts)

# 학생 본문 시트의 빈 다섯째 열 정리
if D["rows"]:
    wb["본문"].delete_cols(5)
order = [n for n in ["단어", "숙어", "영영풀이", "핵심문법", "본문", "본문_거꾸로영작", "정답_단어", "정답_숙어", "정답_영영풀이", "정답_핵심문법", "정답_본문"] if n in wb.sheetnames]
wb._sheets = [wb[n] for n in order]
wb.save(OUT)
print("saved", OUT, wb.sheetnames)
