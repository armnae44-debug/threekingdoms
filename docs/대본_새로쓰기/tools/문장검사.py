# 원고 문장 검사기
# 쓰는 법: python3 tools/문장검사.py 원고.md [원고2.md ...]
# 그동안 지적받은 문장 버릇을 기계적으로 잡는다. 걸린 줄은 하나씩 사람이 보고 고친다.
# 걸렸다고 다 틀린 건 아니다. 다만 "왜 이 줄은 괜찮은지" 말할 수 없으면 고친다.
import re, sys

# 1. 금지어 (지침표)
BANNED = ["시선", "머물", "무거웠다", "공기", "한참", "천천히", "한동안", "……"]

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
    # 숨 한 번 류 시간 끊기
    (r"^숨 한 번", "시간 끊기 상투", "숨 한 번. 그 사이에 정해야 했다"),
]

# 3. 짧은 조각 문단: 대사가 아닌데 한 줄이 아주 짧은 것 ("왔다." "오소." "서른." "등자.")
SHORT = 8
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
        for sent in re.split(r"(?<=[.?!])\s+", body):
            for pat, name, ex in PATTERNS:
                if re.search(pat, sent):
                    hits.append((i, name, ex, s))
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
