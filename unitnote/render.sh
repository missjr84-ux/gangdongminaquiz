#!/bin/bash
# 미리보기:  bash render.sh out/festivals  → out/festivals/r/g_d1_0.png … (8쪽씩 한 장)
# 주아 폰트가 없으면 미리보기 글자가 다르게 보여요: mkdir -p ~/.fonts && cp fonts/Jua-Regular.ttf ~/.fonts/ && fc-cache -f
cd "$1" && rm -rf r && mkdir r && i=0
for f in *.pptx; do i=$((i+1)); cp "$f" r/d$i.pptx; done
cd r && soffice --headless --convert-to pdf *.pptx >/dev/null 2>&1
for p in d*.pdf; do b=${p%.pdf}; pdftoppm -r 45 -png $p $b 2>/dev/null; done
python3 -c "
import glob
from PIL import Image
for p in sorted(set(f.split('-')[0] for f in glob.glob('d*-*.png'))):
    fs=sorted(glob.glob(p+'-*.png'))
    for k in range(0,len(fs),8):
        t=[Image.open(f) for f in fs[k:k+8]]; w,h=t[0].size
        g=Image.new('RGB',(w*4,h*2),'white')
        for i,im in enumerate(t): g.paste(im,((i%4)*w,(i//4)*h))
        g.save(f'g_{p}_{k//8}.png')
print(sorted(glob.glob('g_*.png')))"
