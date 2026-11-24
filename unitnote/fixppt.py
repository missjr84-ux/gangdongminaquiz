# pptxgenjs가 한 문단 안 run 사이에 <a:pPr>를 반복해서 넣는 문제 정리 — 문단마다 첫 pPr만 남김
import re, sys, zipfile, shutil, os

def fix(path):
    tmp = path + ".tmp"
    zin = zipfile.ZipFile(path)
    zout = zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED)
    n = 0
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename.startswith("ppt/slides/slide") and item.filename.endswith(".xml"):
            s = data.decode("utf8")
            def para(m):
                global_n = [0]
                body = m.group(0)
                first = True
                def p(mm):
                    nonlocal first
                    if first:
                        first = False
                        return mm.group(0)
                    return ""
                return re.sub(r"<a:pPr\b[^>]*?(?:/>|>.*?</a:pPr>)", p, body, flags=re.S)
            s2 = re.sub(r"<a:p>.*?</a:p>", para, s, flags=re.S)
            n += s.count("<a:pPr") - s2.count("<a:pPr")
            data = s2.encode("utf8")
        zout.writestr(item, data)
    zout.close(); zin.close()
    shutil.move(tmp, path)
    print(os.path.basename(path), "removed", n)

for f in sys.argv[1:]:
    fix(f)
