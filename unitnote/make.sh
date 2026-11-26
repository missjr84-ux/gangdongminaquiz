#!/bin/bash
# 단원노트 한 단원 만들기:  bash make.sh festivals
# 결과: out/<단원>/  (학생용 pptx · 정답 pptx · xlsx)
set -e
cd "$(dirname "$0")"
U="$1"
case "$U" in
  l7)        L="Lesson 7  Save Earth, Save Us";         F="중1_능률_7과" ;;
  l8)        L="Lesson 8";                              F="중1_능률_8과" ;;
  heroes)    L="Lesson 6  Discovering Heroes";          F="중2_천재이상기_6과" ;;
  poem)      L="Lesson 5  A Poet Who Loved Stars";      F="중3_천재이재영_윤동주" ;;
  commons)   L="Lesson 6  The Story of the Commons";    F="중3_천재이재영_커먼스" ;;
  festivals) L="Lesson 7  Let's Enjoy Festivals";       F="중2_동아윤정미_7과" ;;
  *) echo "사용법: bash make.sh <단원>   (l7 l8 heroes poem commons festivals — 새 단원은 여기 한 줄 추가)"; exit 1 ;;
esac
# pptxgenjs 찾기 (없으면 이 폴더에 설치)
if ! NODE_PATH="$NODE_PATH:/opt/npm-tools/node_modules:$PWD/node_modules" node -e "require('pptxgenjs')" 2>/dev/null; then
  npm install --no-save --prefix . pptxgenjs >/dev/null
fi
python3 -c "import openpyxl" 2>/dev/null || pip install --break-system-packages -q openpyxl
O="out/$U"; rm -rf "$O"; mkdir -p "$O"
python3 "units/mk_$U.py"
NODE_PATH="$NODE_PATH:/opt/npm-tools/node_modules:$PWD/node_modules" node build.js "data/data_$U.json" "$O" "$L" "$F"
for f in "$O"/*.pptx; do python3 fixppt.py "$f"; done
python3 xl.py "data/data_$U.json" "$O/${F}_단원노트.xlsx" "$L"
ls "$O"
