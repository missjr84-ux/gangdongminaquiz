import json, re
from difflib import SequenceMatcher

clean = lambda s: re.sub(r"\s+", " ", re.sub("<[^>]+>", " ", s or "")).strip()


def rows_from_reading(path):
    d = json.load(open(path))
    rows = []
    for t in d["tabs"]:
        for b in t["blocks"]:
            if b["k"] == "analysis":
                for p in b["paras"]:
                    for it in p["items"]:
                        rows.append({"n": it["n"], "para": clean(p["title"]), "en": clean(it["en"]), "kr": clean(it["kr"]),
                                     "ch": [[clean(a), clean(b2)] for a, b2 in it["ch"]] if it.get("ch") else None,
                                     "tip": clean(it.get("tip", ""))})
                return d, rows
    raise SystemExit("no analysis")


def phrases_from_flip(d):
    out = []
    for t in d["tabs"]:
        for b in t["blocks"]:
            if b["k"] == "flip":
                for r in b["rows"]:
                    out.append(clean(r[0]))
    return out


def phrases_from_blanks(d):
    out = []
    for t in d["tabs"]:
        for b in t["blocks"]:
            if b["k"] == "qset" and "핵심 표현" in (b.get("title") or ""):
                for q in b["qs"]:
                    s = clean(q.get("s", "")); ans = q.get("a") or []
                    toks = re.split(r"(\[\])", s); k = 0; buf = []; runs = []; cur = None; gap = 0
                    words = []
                    for tk in toks:
                        if tk == "[]":
                            a = ans[k].split("|")[0] if k < len(ans) else ""; k += 1
                            words.append(("B", a))
                        else:
                            for w in tk.split():
                                words.append(("T", w))
                    # runs: blanks possibly separated by <=1 text word
                    i = 0
                    while i < len(words):
                        if words[i][0] == "B":
                            j = i; last = i
                            while j + 1 < len(words) and (words[j + 1][0] == "B" or (j + 2 < len(words) and words[j + 2][0] == "B" and words[j + 1][0] == "T")):
                                j += 1
                                if words[j][0] == "B": last = j
                            runs.append(" ".join(w for _, w in words[i:last + 1]))
                            i = last + 1
                        else:
                            i += 1
                    out += [re.sub(r"[.,!?]+$", "", r) for r in runs]
    return out


def phrases_from_ex(d):
    out = []
    for t in d["tabs"]:
        if "중요" not in t["name"]:
            continue
        for b in t["blocks"]:
            for q in b.get("qs", []):
                if q.get("t") != "ex":
                    continue
                s = clean(q.get("s", "")); ans = [a.split("|")[0] for a in q.get("a", [])]
                parts = s.split("[]")
                if len(parts) < 2:
                    continue
                # region from first blank to last blank, filled
                mid = ""
                for i, a in enumerate(ans):
                    mid += a + (parts[i + 1] if i + 1 < len(parts) - 1 else "")
                # extend to whole words on both sides when blank sits inside a word
                left = parts[0]; right = parts[-1]
                lw = re.search(r"(\S*)$", left).group(1); rw = re.match(r"^(\S*)", right).group(1)
                out.append((lw + mid + rw).strip(" .,!?\""))
    return out


def lcs(a, b):
    m = SequenceMatcher(None, a, b).find_longest_match(0, len(a), 0, len(b))
    return b[m.b:m.b + m.size]


def attach_keys(rows, phrases):
    for r in rows:
        en = r["en"]; low = en.lower(); keys = []
        for ph in phrases:
            for piece in re.split(r"\s*(?:/|~|…|\.\.\.)\s*", ph):
                piece = piece.strip(" .,!?").replace("’", "'")
                if len(piece) < 3 or "+" in piece or not re.search(r"[A-Za-z]", piece):
                    continue
                i = low.find(piece.lower())
                if i < 0 or (i > 0 and low[i - 1].isalpha()) or (i + len(piece) < len(low) and low[i + len(piece)].isalpha()):
                    continue
                enk = en[i:i + len(piece)]
                if any(enk in k[1] for k in keys):
                    continue
                keys = [k for k in keys if k[1] not in enk]
                # korean: chunks overlapping
                kr = ""
                if r["ch"]:
                    pos = 0; kparts = []
                    for c in r["ch"]:
                        a, b = pos, pos + len(c[0])
                        if a < i + len(piece) and b > i:
                            kparts.append(c[1])
                        pos = b + 1
                    for kp in kparts:
                        kp2 = re.sub(r"\(.*?\)|~", "", kp).strip()
                        cand = kp2 if kp2 and kp2 in r["kr"] else lcs(kp2, r["kr"]).strip()
                        if len(cand.replace(" ", "")) >= 2 and cand not in kr:
                            kr = (kr + "|" + cand) if kr else cand
                keys.append([kr, enk])
        r["key"] = keys
    return rows


if __name__ == "__main__":
    import sys
    d, rows = rows_from_reading(sys.argv[1])
    ph = phrases_from_ex(d) + phrases_from_flip(d) + phrases_from_blanks(d)
    print(len(rows), "rows", len(ph), "phrases")
    attach_keys(rows, ph)
    for r in rows:
        print(r["n"], r["en"], "\n    ", r["kr"], "\n    ", r["key"])
