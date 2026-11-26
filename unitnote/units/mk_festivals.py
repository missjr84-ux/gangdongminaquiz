import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import json, re
from mk_common import *

clean = lambda s: re.sub(r"\s+", " ", re.sub("<[^>]+>", " ", s or "")).strip()

words = W([
    ("altar", "제단"), ("area", "지역", "region"), ("cemetery", "묘지", "graveyard"),
    ("costume", "의상, 복장", "outfit"), ("firework", "(-s) 불꽃놀이"), ("fur", "모피, (동물의) 털"),
    ("midsummer", "한여름"), ("parade", "퍼레이드, 행진"), ("pole", "기둥, 막대기", "post"),
    ("recipe book", "요리책", "cookbook"), ("reindeer", "순록 (복수도 reindeer)"), ("skeleton", "해골"),
    ("souvenir", "기념품"), ("spring", "봄"), ("star", "별; 주인공"), ("statue", "조각상"),
    ("visitor", "방문객", "guest"), ("matter", "문제, 물질; 중요하다", "count"), ("end", "끝나다; 끝", "finish", "start"),
    ("Mexican", "멕시코 사람; 멕시코의"), ("burn", "타다, 태우다"), ("call", "~라고 부르다; 전화하다"),
    ("celebrate", "축하하다, 기념하다"), ("decorate", "장식하다, 꾸미다"), ("guess", "추측하다; 추측", "suppose"),
    ("hold", "들고 있다; 개최하다, 열다"), ("miss", "놓치다; 그리워하다"), ("order", "주문하다; 주문, 순서"),
    ("participate", "참가하다 (participate in)", "take part"), ("set", "(해·달이) 지다 (set-set-set)", "", "rise"),
    ("symbolize", "상징하다", "represent"), ("wear", "입고[쓰고/신고] 있다"), ("welcome", "환영하다, 반기다"),
    ("dark", "어두운; 어둠", "", "bright"), ("dead", "죽은", "", "alive"), ("giant", "거대한; 거인", "huge"),
    ("live", "라이브의, 실황인 [laiv]"), ("playful", "장난기 많은, 놀기 좋아하는"), ("possible", "가능한", "", "impossible"),
    ("seasonal", "계절의, 계절적인"), ("spicy", "매운", "hot"), ("traditional", "전통의, 전통적인", "", "modern"),
    ("various", "다양한", "diverse"), ("wooden", "나무로 된"), ("especially", "특히", "particularly"),
    ("hardly", "거의 ~ 않다", "barely"), ("once", "한 번", "one time"), ("surprisingly", "놀랍게도"),
    ("during", "~ 동안"), ("until", "~까지", "till"),
    ("delicious", "맛있는", "tasty"), ("chef", "요리사", "cook"),
    ("invite", "초대하다"), ("world-famous", "세계적으로 유명한"), ("gift", "선물", "present"),
    ("light", "가벼운", "", "heavy"), ("perfect", "완벽한, 딱 맞는"), 
    ("gather", "모이다", "come together"), ("throw", "던지다 (throw-threw-thrown)", "", "catch"), ("director", "감독"),
])
idioms = W([
    ("take place", "열리다, 개최되다", "be held"), ("hundreds of", "수백의"),
    ("say goodbye to", "~에게 작별 인사를 하다", "", "say hello to"), ("between A and B", "A와 B 사이에"),
    ("all night long", "밤새도록"), ("set up", "세우다, 설치하다"), ("dress up", "분장하다, 차려입다"),
    ("at the end of", "~의 말[끝]에", "", "at the beginning of"), ("such as", "~ 같은", "like"),
    ("participate in", "~에 참가하다", "take part in"), ("have fun", "재미있게 놀다", "enjoy oneself"),
    ("for free", "무료로"), ("come together", "모이다", "gather"), ("each other", "서로", "one another"),
    ("for fun", "장난삼아, 재미로"), ("keep a diary", "일기를 쓰다"),
])
defs = D([
    ("altar", "a type of table used in ceremonies", "의식에 쓰이는 탁자의 한 종류"),
    ("burn", "to destroy or damage something with fire", "무언가를 불로 파괴하거나 손상시키다"),
    ("celebrate", "to show that a day or an event is important by doing something special", "특별한 일을 해서 어떤 날이나 행사가 중요하다는 것을 보여 주다"),
    ("costume", "a set of clothes worn to look like a particular person, animal, or thing", "특정한 사람, 동물, 물건처럼 보이려고 입는 한 벌의 옷"),
    ("decorate", "to make something look more attractive by putting things on it", "무언가를 붙이거나 올려서 더 보기 좋게 만들다"),
    ("fireworks", "the pattern of colorful explosions in the air planned as a show", "볼거리로 계획된 공중의 화려한 폭발 무늬"),
    ("giant", "very large", "매우 큰"),
    ("matter", "to be important", "중요하다"),
    ("parade", "a line of people or vehicles moving together through a public place in order to celebrate an important day or event", "중요한 날이나 행사를 기념하려고 공공장소를 함께 지나가는 사람이나 차량의 줄"),
    ("participate", "to take part in or become involved in an activity", "어떤 활동에 참여하거나 관여하게 되다"),
    ("pole", "a long, thin stick of wood or metal that is often used to support something", "무언가를 받치는 데 자주 쓰이는, 나무나 금속으로 된 길고 가는 막대"),
    ("possible", "able to be done or achieved", "할 수 있거나 이룰 수 있는"),
    ("skeleton", "the structure of bones that support the body of a person or an animal", "사람이나 동물의 몸을 지탱하는 뼈의 구조"),
    ("statue", "a large art object of a person or an animal that is made from a hard material like stone or metal", "돌이나 금속 같은 단단한 재료로 만든 사람이나 동물의 큰 예술품"),
    ("symbolize", "to represent something", "무언가를 나타내다"),
])

# ---- 본문: festivalswriting 의 거꾸로 영작(한글·영어) + 어순 배열(끊어 읽기) + 문장별 분석 포인트
d = json.load(open(os.path.join(ROOT, "src", "festivalswriting.json")))
tips = {}
for b in d["tabs"][0]["blocks"]:
    if b["k"] == "html" and 'class="rp"' in b["html"]:
        for m in re.finditer(r'<b>(\d+)\.</b>.*?<span class="gl">(.*?)</span>', b["html"], re.S):
            tips[int(m.group(1))] = clean(m.group(2))
PARA = {"Fallas": "봄 — Fallas", "Midsummer": "여름 — Midsummer", "Day of the Dead": "가을 — Day of the Dead", "Fur Rondy": "겨울 — Fur Rondy"}
KEY = {
    1: [("봄이 오는 것을 기념한다", "celebrate the coming of spring")],
    2: [("3월 15일부터 19일까지", "from March 15 to 19"), ("열린다", "takes place")],
    3: [("축제 동안", "During the festival")],
    4: [("축제의 주인공은", "The stars of the festival"), ("거대한 나무 조각상", "giant wooden statues")],
    5: [("수백 개의 fallas를", "hundreds of them"), ("도시 곳곳에서", "all over the city")],
    6: [("놀랍게도", "Surprisingly"), ("불태워진다", "are burned"), ("축제의 마지막 날에", "on the last day of the festival")],
    7: [("그것들을 태우는 것은", "Burning them"), ("작별 인사를", "saying goodbye to"), ("상징한다", "symbolizes")],
    8: [("길고 어두워서", "is long and dark, so"), ("여름을 특히 반긴다", "especially welcome summer")],
    9: [("일 년 중 가장 긴 날을", "the longest day of the year"), ("기념하기 위해", "To celebrate")],
    10: [("그것을 Midsummer 축제라고 부른다", "call it the Midsummer festival")],
    11: [("6월 19일과 25일 사이에", "between June 19 and 25"), ("일요일에 끝난다", "ends on the Sunday")],
    12: [("꽃과 초록 잎으로 장식하고", "decorate a tall pole with flowers and green leaves"), ("그 주위에서", "around it")],
    13: [("해가 거의 지지 않기 때문에", "Because the sun hardly sets"), ("매년 이맘때", "at this time of year"), ("밤새도록", "all night long")],
    14: [("일 년에 한 번", "once a year"), ("집에 돌아온다고", "come back home"), ("만나러", "to meet")],
    15: [("이날을 죽은 자들의 날이라고 부른다", "call this day the Day of the Dead")],
    16: [("죽은 사람들을 맞이하기 위해", "To welcome dead people"), ("축제를 연다", "hold a festival")],
    17: [("죽은 사람들을 기억하는 것이 중요하다고", "it is important to remember dead people")],
    18: [("제단을 차리고", "set up altars"), ("큰 파티를 연다", "have big parties")],
    19: [("어떤 지역에서는", "In some areas"), ("해골처럼 분장하고", "dress up like skeletons")],
    20: [("2월 말에", "At the end of February"), ("가장 큰 겨울 축제 중 하나인", "one of the biggest winter festivals")],
    21: [("다양한 겨울 스포츠", "various winter sports")],
    22: [("순록 달리기 같은", "such as the Running of the Reindeer")],
    23: [("이 경주에 참가하는 사람들은", "People who participate in this race"), ("순록보다 더 빨리 달리려고 애쓴다", "try to run faster than reindeer")],
    24: [("그렇게 하는 것이 가능할까", "Is it possible to do so")],
    25: [("그건 중요하지 않다", "it doesn't matter")],
    26: [("즐겁게 놀고 있을 뿐이다", "just having fun")],
}
rows = []; n = 0
for B, O in zip(d["tabs"][3]["blocks"], d["tabs"][2]["blocks"]):
    t = re.sub(r"^[①-⑳]\s*", "", B["title"]).split(" — ")[0].strip()
    for q, o in zip(B["qs"], O["qs"]):
        n += 1
        en = q["a"].split("|")[0].strip(); kr = clean(q["q"])
        assert " ".join(o["c"]) == en, (n, o["c"], en)
        ks = KEY[n]
        for k, e in ks:
            assert k in kr, (n, k, kr); assert e in en, (n, e, en)
        rows.append({"n": n, "para": PARA[t], "en": en, "kr": kr, "ch": [[c, ""] for c in o["c"]], "tip": tips[n], "key": ks})
assert n == 26 and len(KEY) == 26

grammar = [
    G("핵심문법 1  가주어 It ~ to부정사", "핵심문법 1", "It is + 형용사 (+ for/of + 목적격) + to + 동사원형", [
        ("기본 문장", "[To remember] dead people is important.  →  주어가 너무 길다"),
        ("1단계", "주어 덩어리 찾기 — 동사 is [앞]까지"),
        ("2단계", "주어 덩어리를 문장 맨 [뒤]로 보낸다"),
        ("3단계", "빈 주어 자리에 [It]을 쓴다  ·  It is important to remember dead people."),
        ("이름", "It = [가주어]  /  to ~ = [진주어]"),
        ("해석", "It은 [해석하지 않는다]  ·  to부터 \"~하는 것은\"으로 읽기"),
        ("의문문", "[Is it] possible to do so?  (그렇게 하는 것이 가능할까?)"),
        ("의미상 주어 1", "보통 형용사(hard, easy, possible ...) → [for] + 목적격  ·  It is not possible for people to run faster than reindeer."),
        ("의미상 주어 2", "사람의 성격·태도 형용사(kind, nice, wise, careless ...) → [of] + 목적격  ·  It is very kind of you to invite me."),
        ("주의", "for/of 뒤에는 [목적격]  ·  for them (for they ✗)"),
    ], [
        ("죽은 사람들을 기억하는 것은 중요하다.", "It, important, remember", "It is important to remember dead people."),
        ("그렇게 하는 것이 가능할까?", "it, possible, do so", "Is it possible to do so?"),
        ("함께 김치를 담그는 것은 재미있을 것이다.", "It, fun, make, together", "It will be fun to make gimchi together."),
        ("불꽃놀이를 보는 것은 신난다.", "It, exciting, watch", "It is exciting to watch the fireworks."),
        ("여동생에게 줄 기념품을 찾는 것은 어려웠다.", "It, hard, find, souvenir", "It was hard to find a souvenir for my sister."),
        ("밤새도록 깨어 있는 것은 쉽지 않다.", "It, easy, stay up, all night long", "It isn't easy to stay up all night long."),
        ("To learn about other cultures is important.를 가주어 It으로 바꾸시오.", "It", "It is important to learn about other cultures."),
        ("사람들이 순록보다 빨리 달리는 것은 가능하지 않다.", "It, possible, for, run, faster than", "It is not possible for people to run faster than reindeer."),
        ("나를 축제에 초대해 주다니 너는 정말 친절하구나.", "It, kind, of, invite", "It is very kind of you to invite me to the festival."),
        ("그녀가 순록과 함께 달린 것은 용감했다.", "It, brave, of, run with", "It was brave of her to run with the reindeer."),
    ]),
    G("핵심문법 2  call A B", "핵심문법 2", "주어 + call + A(목적어) + B(명사)  →  A를 B라고 부르다", [
        ("공식", "주어 + call + [목적어] + [명사]  ·  A를 B라고 부르다"),
        ("A 자리", "부르는 [대상]  ·  it, this day, the race"),
        ("B 자리", "부르는 [이름] (명사)  ·  the Midsummer festival"),
        ("확인", "A [=] B  ·  it = the Midsummer festival ✓"),
        ("예문", "They call [this day] [the Day of the Dead]."),
        ("함정 1", "A가 대명사면 [목적격]  ·  call him (call he ✗)"),
        ("함정 2", "A와 B 사이에 [as]를 넣지 않는다  ·  call it as the Midsummer festival ✗"),
        ("함정 3", "A와 B의 순서를 바꾸면 [뜻이 바뀐다]"),
        ("같은 구조", "name A B (A를 B라고 [이름 짓다])  ·  make A B (A를 B로 [만들다])"),
        ("구별", "A = B면 5형식 \"A를 B로\" / A ≠ B면 [4형식] \"A에게 B를\"  ·  Mom made me a costume."),
    ], [
        ("그들은 그것을 Midsummer 축제라고 부른다.", "call, it", "They call it the Midsummer festival."),
        ("그들은 이날을 죽은 자들의 날이라고 부른다.", "call, this day", "They call this day the Day of the Dead."),
        ("사람들은 그 경주를 순록 달리기라고 부른다.", "call, the race", "People call the race the Running of the Reindeer."),
        ("내 친구들은 나를 꼬마 요리사라고 부른다.", "call, Little Chef", "My friends call me Little Chef."),
        ("발렌시아 사람들은 그 조각상들을 fallas라고 부른다.", "call, the statues", "People in Valencia call the statues fallas."),
        ("우리는 그 개를 Max라고 부른다.", "call, the dog", "We call the dog Max."),
        ("사람들은 그 도시를 꽃의 도시라고 부른다.", "call, the City of Flowers", "People call the city the City of Flowers."),
        ("우리는 그녀를 Mina라고 부른다.", "call, her", "We call her Mina."),
        ("우리는 그 조각상을 Big Joe라고 이름 지었다.", "name, the statue, 과거", "We named the statue Big Joe."),
        ("그 축제는 그 마을을 인기 있는 곳으로 만들었다.", "make, a popular place, 과거", "The festival made the town a popular place."),
    ]),
]
save(os.path.join(ROOT, "data", "data_festivals.json"), acad="강동미나 중고등부 · 중2 동아(윤정미)", words=words, idioms=idioms, defs=defs, rows=rows, grammar=grammar)
