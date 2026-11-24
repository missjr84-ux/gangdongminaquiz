import json, re, sys
import os
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from keys import rows_from_reading


def W(lst):
    """[(word, meaning, syn, ant)] → dicts"""
    out = []
    for t in lst:
        w, m = t[0], t[1]
        s = t[2] if len(t) > 2 else ""
        a = t[3] if len(t) > 3 else ""
        out.append({"w": w, "m": m, "syn": s, "ant": a})
    return out


def D(lst):
    return [{"w": w, "d": d, "ko": ko} for w, d, ko in lst]


def rows_with_keys(path, KEY, para_rename=None):
    _, rows = rows_from_reading(path)
    for r in rows:
        r["para"] = re.sub(r"\s*—.*$", "", r["para"])
        ks = KEY.get(r["n"], [])
        for kr, en in ks:
            assert kr in r["kr"], (path, r["n"], kr, r["kr"])
            assert en in r["en"], (path, r["n"], en, r["en"])
        r["key"] = ks
    missing = [n for n in KEY if n not in [r["n"] for r in rows]]
    assert not missing, missing
    return rows


def G(title, short, formula, concept, write):
    assert len(write) == 10, (title, len(write))
    for k, v in concept:
        assert v.count("[") == v.count("]"), v
    return {"title": title, "short": short, "formula": formula, "concept": concept, "write": write}


def save(path, **kw):
    for g in kw["grammar"]:
        pass
    json.dump(kw, open(path, "w"), ensure_ascii=False, indent=1)
    print(path, {k: len(v) if isinstance(v, list) else v for k, v in kw.items()})
