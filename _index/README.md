# _index — 자료 색인 만드는 곳

최상위 `index.html`을 만드는 파일들입니다.

| 파일 | 내용 |
|---|---|
| `catalog.py` | 레포 안 인터랙션 html 목록 |
| `chats.py` | 대화에서 만든 인쇄물 목록 (대화 링크) |
| `guides.py` | 프로젝트 지침 8개 |
| `gen.py` | 위 셋을 읽어 `index.html`을 만듦 |

새 파일을 올렸으면 `catalog.py`에 한 줄 넣고 레포 최상위에서:

```
python3 _index/gen.py
```

한글 폰트는 `assets/Jua.woff2`에 들어 있습니다 (주아체, OFL).
