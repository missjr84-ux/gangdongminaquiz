"""레포 인터랙션 html 안의 데이터를 json으로 꺼내요.

    python3 extract.py ../heroesreading.html src/heroesreading.json

두 가지 형식을 다 읽어요.
  - 예전 엔진: window.DATA={...}
  - 새 엔진(동아 7과 festivals 등): var CFG={...}  (DATA START ~ DATA END 사이)
"""
import json, sys

src, out = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf-8").read()
for mark in ("window.DATA=", "window.DATA =", "var CFG=", "var CFG ="):
    i = s.find(mark)
    if i >= 0:
        d = json.JSONDecoder().raw_decode(s[i + len(mark):].lstrip())[0]
        break
else:
    sys.exit("데이터를 못 찾았어요: window.DATA / var CFG 둘 다 없음")
json.dump(d, open(out, "w", encoding="utf-8"), ensure_ascii=False)
print(out, d.get("title", ""), [t["name"] for t in d.get("tabs", [])])
