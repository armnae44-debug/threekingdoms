# 원고 문장 검사기
# 쓰는 법: python3 tools/문장검사.py 원고.md [원고2.md ...]
# 그동안 지적받은 문장 버릇을 기계적으로 잡는다. 걸린 줄은 하나씩 사람이 보고 고친다.
# 걸렸다고 다 틀린 건 아니다. 다만 "왜 이 줄은 괜찮은지" 말할 수 없으면 고친다.
import re, sys

# 1. 금지어 (지침표)
BANNED = ["시선", "머물", "무거웠다", "공기", "한참", "천천히", "한동안", "……", "셈"]

# 2. 지적받은 문장 유형 (정규식, 이름, 실제로 지적받은 예)
PATTERNS = [
    # 결론·정리문: 장면 끝에 서술자가 한 줄로 정리하는 문장
    (r"(것|뿐|하나|길|사람|손|귀|입|발|다리|날|밤)이?었다\.$", "정리문(~이었다로 닫음)",
     "그날 밤 나를 깨운 것도 그 귀였다 / 할 수 있는 건 하나였다 / 여기서부터는 내가 모르는 길이었다"),
    (r"^(할 수 있는 건|문제는|여기서부터는|그때 이|그 끝이|그 백 년|그 값은)", "주제 선언·정리 첫머리",
     "문제는 그 선을 누구 입으로 긋느냐였다 / 그 값은 내가 아니라 그가 치른다"),
    (r"(아직 그 안에|오래가지 않았다|그래서 더 [가-힣]+(했|였|렸|웠)다)", "펀치라인 꼬리",
     "우리는 아직 그 안에 있었다 / 그 웃음은 오래가지 않았다 / 그래서 더 귀에 걸렸다"),
    # 기능으로 사람 바꿔 쓰기
    (r"그 (귀|손|다리|입|눈)(이|가|은|는|였|이었)", "기능으로 사람 바꿔 쓰기",
     "그 귀였다 / 도랑에서 바구니를 빼앗던 그 손이었다"),
    # 시점 밖 단정 (주인공이 알 수 없는 남의 속)
    (r"(알아채지 못했|눈치채지 못했|안 것이다|몰랐던 것이다|줄은 몰랐|짐작하고 있을 것|모른다\. 그러니)", "시점 밖 단정",
     "전령은 장부가 얇아진 걸 알아채지 못했다 / 저들도 굴 끝에 도랑이 있을 줄은 몰랐던 것이다"),
    # 뜻보다 앞서는 비유
    (r"(매달려 내|버둥거리고 있었다\.$|손바닥 위에 있었다|사이 어디쯤에)", "뜻보다 앞서는 비유",
     "그 끝이 때 묻은 표찰에 매달려 / 그 백 년이 흙바닥에서 버둥거렸다"),
    # 시대 단정·천재 단정
    (r"(이 시대 사람은|뿐이지요|누구나 만들 수|수밖에 없소)", "단정(시대·천재·필연)",
     "이 시대 사람은 산가지부터 늘어놓는다 / 저수뿐이지요 / 나올 수밖에 없소"),
    # 무슨 동작인지 안 보이는 동작
    (r"(거꾸로 세웠|거꾸로 쥐|붓을 댔)", "흐린 동작",
     "극을 거꾸로 세웠다 / 이름에 붓을 댔다"),
    # 무엇에 맞았는지 숨기는 타격, 주인공이 모르는 추측
    (r"(무언가에 맞|아무 말이나 탄|누가 무너뜨렸는지)", "흐린 타격·추측",
     "무언가에 맞아 옆으로 날아갔다 / 아무 말이나 탄 것 같았다"),
    # 동작을 명사로 만드는 번역투
    (r"(것이 보였|것을 보고|것을 봤|들어 보였|줄 까닭)", "명사화·번역투",
     "나무를 메고 오는 것이 보였다 / 깃발을 들어 보였다 / 들어가 줄 까닭"),
    # 상투 그림·명언형 맺음 (지적받은 것)
    (r"(셈은 맞|셈은 .{0,8}하시오|그런 셈은|셈해 두|기억해 두지|기억해 두겠|목을 걸|목 하나로)", "상투 그림",
     "셈은 맞군 / 그 목, 기억해 두지 / 제 목을 걸겠습니다"),
    # 숨 한 번 류 시간 끊기
    (r"^숨 한 번", "시간 끊기 상투", "숨 한 번. 그 사이에 정해야 했다"),
]

# 2-2. 한 장 안에서 되풀이되면 걸리는 몸짓·장치 (패턴, 이름, 허용 횟수)
REPEAT = [
    (r"코(로|웃음)", "코로 웃음", 2),
    (r"등을 뗐", "벽에서 등 떼기", 1),
    (r"입술을 깨물|입 안쪽을 깨물", "입술 깨물기", 1),
    (r"고개를 숙였", "고개 숙이기", 3),
    (r"(아무도|누구도) .{0,8}보지 않았", "아무도 보지 않음", 1),
    (r"얼굴들이 .{0,10}(향했|돌아왔)", "얼굴들이 나를 향함", 1),
    (r"어깨를 으쓱", "어깨 으쓱", 0),
    (r"목소리는 크지 않았", "낮은 목소리 표시", 0),
    (r"오래 생각했", "생각했다고만 알림", 0),
    (r"누가 .{0,12}소리가 났다", "익명의 소리 긴장", 0),
    (r"대답하지 못했|대답이 바로 나오지 않|목소리가 갈라|내 목소리가 아닌", "대답 못 함·목소리 갈라짐", 1),
    (r"튕겨 나", "튕겨 나옴", 0),
    (r"(나를|내 쪽을|내 얼굴을|서로 얼굴을|(조공|조조|조홍|조노|왕삼|소칠|순유|가후|여포|장합|저수|원소|곽도|고람|관우|유비|허유|군후|장군|병사|부장|군관)[을를]) (오래 |한 번 |다시 )?(봤다|내려다봤다|올려다봤다|쳐다봤다)\.", "반응 박자로 쓰는 '봤다'", 3),
    (r"[가-힣]+[이가] 아니라 |[가-힣]+ 아니오\. ", "A가 아니라 B 대구", 2),
    (r"[아어여] 주었다|[아어여] 줬다|[아어여]주었다", "~해 주었다", 4),
]
# 2-3. 선택지 설명에 인물 반응·결과를 미리 알리는 말
CHOICE_HINT = r"(듣기에는|궁금해할|답답하다|의심을 산다|싫어할|좋아할)"
# 2-4. 현대 대입 비유 낱말 (일부러 쓴 건 남긴다)
MODERN = r"(컵라면|사발면|회사|회의실|편의점|지하철|엘리베이터|스마트폰|택배)"

# 3. 짧은 조각 문단: 대사가 아닌데 한 줄이 아주 짧은 것 ("왔다." "오소." "서른." "등자.")
SHORT = 8
# 4. 단문 나열: 한 문단 안에서 RUN_LEN자 이하 '~다.' 문장이 RUN_MAX개 이어지면 잡는다.
RUN_LEN = 22
RUN_MAX = 3
# 5. 감정을 형용사로 통보하고 끝내는 문장
FEEL = r"(싫었|무서웠|두려웠|반가웠|기뻤|슬펐|서운했|불안했|막막했|억울했|미안했|고마웠|겁이 났|화가 났|안도했|뿌듯했|창피했|부끄러웠)다\.$"
COND = re.compile(r"\s*〔[^〕]*〕\s*$")

def check(path):
    hits = []
    lines = open(path, encoding="utf8").read().split("\n")
    in_head = True
    for i, raw in enumerate(lines, 1):
        if raw.strip() == "---" and in_head:
            in_head = False
            continue
        if in_head:
            continue
        s = COND.sub("", raw).strip()
        if not s or s.startswith("#") or s == "/" or s.startswith("- ▸") or s.startswith("**[선택]**") or s.startswith("*〈"):
            continue
        is_dia = s.startswith("**")
        for w in BANNED:
            if w in s:
                hits.append((i, "금지어", w, s))
        body = re.sub(r"^\*\*[^*]+\*\*:\s*", "", s)
        if not is_dia and len(body) <= SHORT and body.endswith("."):
            hits.append((i, "짧은 조각 문단", "왔다. / 오소. / 서른. / 등자.", s))
        if len(re.findall(r"[다라]고 했다", body)) >= 2:
            hits.append((i, "간접화법 요약(~다고 했다 연달아)", "", s))
        if not is_dia:
            run = 0
            for sent in re.findall(r"[^.!?]+[.!?]", body):
                sent = sent.strip()
                if len(sent) <= RUN_LEN and sent.endswith("다."):
                    run += 1
                    if run == RUN_MAX:
                        hits.append((i, "단문 나열(짧은 '~다.' 3개 연속)", "", s))
                else:
                    run = 0
            # 6. 다다다: 길이와 상관없이 '~다.'로 끝나는 문장이 3개 연달아 나오면 잡는다.
            run = 0
            for sent in re.findall(r"[^.!?]+[.!?]", body):
                if sent.strip().endswith("다."):
                    run += 1
                    if run == 3:
                        hits.append((i, "다다다('~다.' 3개 연속, 길이 무관)", "", s))
                else:
                    run = 0
            for sent in re.findall(r"[^.!?]+[.!?]", body):
                if re.search(FEEL, sent.strip()):
                    hits.append((i, "감정 통보(형용사로 끝냄)", "", s))
        for sent in re.split(r"(?<=[.?!])\s+", body):
            for pat, name, ex in PATTERNS:
                if re.search(pat, sent):
                    hits.append((i, name, ex, s))
    body_all = [(i, COND.sub("", l).strip()) for i, l in enumerate(lines, 1)]
    start = next((i for i, l in body_all if l == "---"), 0)
    body_all = [(i, l) for i, l in body_all if i > start]
    for pat, name, limit in REPEAT:
        found = [(i, l) for i, l in body_all if re.search(pat, l) and not l.startswith("- ▸")]
        if len(found) > limit:
            for i, l in found:
                hits.append((i, f"반복 몸짓: {name} {len(found)}회(허용 {limit})", "", l))
    for i, l in body_all:
        if l.startswith("- ▸") and re.search(CHOICE_HINT, l):
            hits.append((i, "선택지 설명이 반응을 예고", "", l))
        if not l.startswith("- ▸") and re.search(MODERN, l):
            hits.append((i, "현대 대입 비유(일부러 쓴 건지 확인)", "", l))
    return hits

if __name__ == "__main__":
    total = 0
    for p in sys.argv[1:]:
        hs = check(p)
        total += len(hs)
        print(f"== {p}: {len(hs)}곳")
        for i, name, ex, s in hs:
            print(f"{i:5d} [{name}] {s[:90]}")
    sys.exit(1 if total else 0)
