import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import json, re

V = json.load(open(os.path.join(ROOT, "src", "savetheearthvoca.json")))
R = json.load(open(os.path.join(ROOT, "src", "savetheearthreading.json")))
T = {t["name"]: t for t in V["tabs"]}
clean = lambda s: re.sub(r"\s+", " ", re.sub("<[^>]+>", "", s or "")).strip()

# ---------- 단어 (뜻은 저장소 자료 그대로, 유의어·반의어는 정리표 기준 + 보충)
SA = {
    "about": ("around (대략)", ""), "below": ("", "above"), "bin": ("trash can", ""),
    "clean": ("", "dirty"), "clever": ("intelligent, smart", "foolish"),
    "completely": ("totally", ""), "correct": ("right", "incorrect, wrong"),
    "difference": ("", "similarity"), "eco": ("ecology", ""), "global": ("worldwide", "local"),
    "hurt": ("harm", ""), "important": ("", "unimportant"), "luckily": ("fortunately", "unluckily"),
    "melt": ("", "freeze"), "ocean": ("sea", ""), "properly": ("correctly", ""),
    "protect": ("guard", ""), "quick": ("fast", "slow"), "reduce": ("", "increase"),
    "rise": ("", "drop, fall"), "save": ("", "waste"), "useful": ("", "useless"),
    "waste": ("", "save"), "without": ("", "with"),
}
words = []
for it in T["📒 단어 익히기"]["blocks"][0]["items"]:
    w = it[0]
    s, a = SA.get(w, ("", ""))
    words.append({"w": w, "m": it[1], "syn": s, "ant": a})
assert len(words) == 45, len(words)

ISA = {"turn off": ("", "turn on"), "take part in": ("participate in", ""), "for example": ("for instance", "")}
idioms = []
for it in T["🧩 숙어"]["blocks"][0]["items"]:
    w = it[0]
    m = re.sub(r"\s*\((?:= [^)]*)\)", "", it[1])
    m = re.sub(r"\s*↔.*$", "", m).strip()
    s, a = ISA.get(w, ("", ""))
    idioms.append({"w": w, "m": m, "syn": s, "ant": a})
assert len(idioms) == 14

# ---------- 영영풀이 (단어 + 영영풀이, 아래 해석)
KO = {
    "bin": "쓰레기를 넣는 데 쓰이는 용기",
    "environment": "물, 공기, 흙을 포함한 자연 세계",
    "protect": "누군가나 무언가를 위험으로부터 안전하게 지키다",
    "recycle": "무언가를 다시 사용해서 새로운 것을 만들다",
    "reduce": "무언가를 크기, 양, 수 등에서 더 작게 만들다",
    "resource": "자연에 존재하며 사람이 사용할 수 있는 것들",
    "temperature": "어떤 장소나 물건이 얼마나 뜨겁거나 차가운지를 재는 정도",
    "wizard": "이야기 속에서 마법의 힘을 가진 사람",
    "pollution": "공기, 물, 흙 등을 더럽게 만드는 행동이나 과정",
    "below": "더 낮은 높이, 위치, 장소에 또는 그곳으로",
    "clean": "더럽지 않은; 무언가를 깔끔하게 만들다",
    "important": "큰 의미나 가치를 가진",
    "item": "목록, 무리, 세트 안에 있는 것 하나",
    "rise": "더 높은 수준이나 위치에 이르다",
    "save": "필요한 것보다 무언가를 덜 쓰다",
    "useful": "무언가를 하는 데 도움이 되는",
    "waste": "무언가를 너무 많이 쓰다; 더 이상 필요 없어 버려진 것",
}
defs = []
for b in T["📖 영영풀이"]["blocks"][:2]:
    for q in b["qs"]:
        w = q["a"] if isinstance(q["a"], str) else q["o"][q["a"]]
        defs.append({"w": w, "d": clean(q["q"]), "ko": KO[w]})
assert len(defs) == 17

# ---------- 본문
rows = []
for p in R["tabs"][0]["blocks"][1]["paras"]:
    for it in p["items"]:
        rows.append({"n": it["n"], "para": p["title"], "en": it["en"], "kr": it["kr"],
                     "ch": it["ch"], "tip": clean(it["tip"])})
assert [r["n"] for r in rows] == list(range(1, 41))

# 핵심 표현: (한글 밑줄 부분, 영어 핵심 표현)
KEY = {
    2: [("다행히", "Luckily"), ("환경을 보호하기 위해서", "to protect the environment")],
    3: [("세상을 깨끗하게 만들기를", "to make the world clean")],
    4: [("그들과 함께하시겠어요", "join them")],
    6: [("너무 많은 자원을", "too many resources")],
    7: [("하지만", "But"), ("재활용은", "recycling")],
    8: [("예를 들어", "For example"), ("종이 1,000kg을 재활용하는 것은", "recycling 1,000 kilograms of paper"), ("약", "about")],
    9: [("재활용의 마법사가", "a wizard at recycling")],
    10: [("그렇다면", "Then"), ("제대로", "properly")],
    11: [("알맞은 쓰레기통에", "in the correct bins")],
    12: [("아래 쓰레기를", "the waste below")],
    13: [("각 쓰레기 조각에서 알맞은 쓰레기통까지", "from each piece of waste to the right bin")],
    16: [("버려요", "throw away"), ("너무 자주", "too often")],
    17: [("쓰레기가 되어", "become waste and")],
    18: [("분해되는 데 200년이 넘게 걸린다", "take over 200 years to break down"), ("것을 알고 있었나요", "Did you know that")],
    19: [("사지 마세요", "Don't buy")],
    20: [("오랫동안", "for a long time")],
    21: [("헌 옷으로", "from your old clothes"), ("만들 수도", "can also create")],
    22: [("헌 옷을 유용하게 만들어", "make old clothes useful")],
    23: [("몇 가지 물건들이 있어요", "There are some items")],
    24: [("이 헌 옷들로", "with these old clothes")],
    25: [("헌 옷과 알맞은 새 물건들을 연결해", "Match the old clothes with the correct new items")],
    26: [("패션에 영리해질", "be clever at fashion")],
    29: [("그것 없이", "without it")],
    30: [("많은 물을", "a lot of water")],
    31: [("저를 슬프게 만들어요", "makes me sad")],
    33: [("샤워를 빨리 하세요", "Take quick showers")],
    34: [("이를 닦는 동안에는", "while you brush your teeth"), ("물을 잠그세요", "Turn off the water")],
    35: [("또한", "Also"), ("완전히", "completely"), ("확인하세요", "make sure that")],
    37: [("물을 절약하는 방법들", "ways to save water")],
    39: [("정답을 맞혔다", "got the right answers"), ("확신해요", "I'm sure that")],
    40: [("물을 절약하는 것에 정말 뛰어나요", "amazing at saving water")],
}
for r in rows:
    ks = KEY.get(r["n"], [])
    for kr, en in ks:
        assert kr in r["kr"], (r["n"], kr)
        assert en in r["en"], (r["n"], en)
    r["key"] = ks

# ---------- 문법
G = [
    {
        "title": "핵심문법 1  동사 + 목적어 + 형용사",
        "short": "핵심문법 1",
        "formula": "주어 + make / keep / find + 목적어 + 형용사",
        "concept": [
            ("공식", "주어 + make / keep / find + [목적어] + [형용사]"),
            ("make", "make + O + 형용사 = O를 [~하게 만들다]  ·  It makes me sad."),
            ("keep", "keep + O + 형용사 = O를 [~한 상태로 유지하다]  ·  He keeps his car clean."),
            ("find", "find + O + 형용사 = O가 [~하다는 것을 알게 되다]  ·  We found the book interesting."),
            ("목적어 자리", "대명사는 [목적격] 으로 쓴다  ·  made she confused → made [her] confused"),
            ("보어 자리 ①", "\"~하게\"로 해석돼도 [부사](-ly)는 못 쓴다  ·  made me happily → made me [happy]"),
            ("보어 자리 ②", "명사형도 못 쓴다  ·  made him fame → made him [famous]"),
            ("예외", "-ly로 끝나도 형용사인 단어는 보어로 쓸 수 있다  ·  lovely, [friendly], [lonely]"),
            ("감정 형용사", "목적어가 느끼면 [-ed], 느끼게 하면 [-ing]  ·  The game made us [excited]."),
            ("확인법", "목적어 [=] 보어 관계면 이 공식  ·  Dad made me a kite. → me ≠ kite → [4]형식"),
            ("명사 보어", "make / call / name + O + [명사]  ·  The movie made him [a star]."),
        ],
        "write": [
            ("그 선물은 그를 행복하게 만들었다.", "gift, make", "The gift made him happy."),
            ("장갑은 너의 손을 따뜻하게 유지해 준다.", "gloves, keep", "Gloves keep your hands warm."),
            ("나는 그 영화가 지루하다는 것을 알게 되었다.", "find, boring", "I found the movie boring."),
            ("그 소식은 우리를 놀라게 만들었다.", "news, surprised", "The news made us surprised."),
            ("그들은 세상을 깨끗하게 만들기를 원한다.", "want, world, clean", "They want to make the world clean."),
            ("사람들은 그를 영웅이라고 불렀다.", "call, hero", "People called him a hero."),
            ("짠 음식은 우리를 목마르게 만든다.", "salty food, thirsty", "Salty food makes us thirsty."),
            ("나무들은 공기를 깨끗하고 신선하게 유지한다.", "trees, keep, fresh", "Trees keep the air clean and fresh."),
            ("헌 옷을 유용하게 만들어 봅시다.", "Let's, useful", "Let's make old clothes useful."),
            ("나는 그 수학 문제가 쉽다는 것을 알게 되었다.", "find, math problem", "I found the math problem easy."),
        ],
    },
    {
        "title": "핵심문법 2  접속사 that",
        "short": "핵심문법 2",
        "formula": "that + 주어 + 동사 ~ = \"~라는 것 / ~라고\"",
        "concept": [
            ("공식", "that + [주어] + [동사] ~ = \"~라는 것 / ~라고\""),
            ("주어 자리", "That he likes her is true. = [It] is true that he likes her.  ·  that 생략 [✗]"),
            ("목적어 자리", "I think (that) she is very kind.  ·  that 생략 [O]"),
            ("보어 자리", "The problem is [that] I lost my wallet.  ·  that 생략 [✗]"),
            ("자주 쓰는 말", "think · know · [believe] · [hope] · say · hear · agree · make sure · be sure + that절"),
            ("that 뒤", "주어와 동사가 다 있는 [완전한] 문장  ·  that the movie sad → that the movie [was] sad"),
            ("헷갈리는 말", "\"~라는 것\"이고 뒤가 완전하면 what · because ✗ → [that]"),
            ("가주어", "주어 자리 that절은 뒤로 보내고 [It]으로 시작  ·  This is true that ~ ✗"),
            ("that 구분", "뒤에 주어+동사 → [접속사]  /  뒤에 명사 → [지시형용사]  /  혼자 → [지시대명사]"),
            ("부정문", "부정은 주절에  ·  I [don't] think that he is young."),
        ],
        "write": [
            ("나는 그녀가 곧 돌아올 것이라고 생각한다.", "think, come back, soon", "I think (that) she will come back soon."),
            ("그가 그 경기에서 이겼다는 것은 놀랍다.", "가주어 It, surprising, won", "It is surprising that he won the game."),
            ("2번 문장을 That으로 시작해서 다시 쓰시오.", "That", "That he won the game is surprising."),
            ("문제는 내가 지갑을 잃어버렸다는 것이다.", "problem, lost, wallet", "The problem is that I lost my wallet."),
            ("나는 그가 정직하다고 생각하지 않는다.", "think, honest", "I don't think (that) he is honest."),
            ("수도꼭지를 완전히 잠갔는지 확인하세요.", "make sure, tap, completely", "Make sure (that) you turn off the tap completely."),
            ("나는 네가 정답을 맞혔다고 확신한다.", "sure, got, right answers", "I'm sure (that) you got the right answers."),
            ("너는 몇몇 옷들은 분해되는 데 200년이 넘게 걸린다는 것을 알고 있었니?", "know, take, break down", "Did you know (that) some clothes take over 200 years to break down?"),
            ("내가 시험에 합격한 것은 사실이다.", "가주어 It, true, passed", "It is true that I passed the test."),
            ("우리는 그가 그 경기에서 이길 것이라고 믿는다.", "believe, win", "We believe (that) he will win the game."),
        ],
    },
]
for g in G:
    assert len(g["write"]) == 10

json.dump({"words": words, "idioms": idioms, "defs": defs, "rows": rows, "grammar": G},
          open(os.path.join(ROOT, "data", "data_l7.json"), "w"), ensure_ascii=False, indent=1)
print("ok", len(words), len(idioms), len(defs), len(rows))
