#!/usr/bin/env python3
"""1~12장 원고(md)를 게임이 그대로 읽는 데이터(JSON)로 바꾼다.

쓰는 법:
    python3 tools/게임변환.py            # tools/게임데이터.json 을 만든다
    python3 tools/게임변환.py --check    # 조건 문법만 검사

한 장은 사건(event)의 목록이다.
    {"t":"scene","title":..,"loc":..,"c":[..]}      ## 절 제목
    {"t":"line","who":..,"text":..,"c":[..]}         서술(who="") · 대사 · 책 인용(book=1)
    {"t":"page","c":[..]}                             `/` 화면 끊기
    {"t":"choice","key":..,"mode":..,"c":[..],"opts":[{"text","sub","val","c","need","lock"}]}
c 는 조건 문자열 목록이고, 모두 참이어야 그 사건이 나온다. 조건 문법은 route.py 와 같다.
소제목(###, #### …)의 조건은 그 묶음 안의 사건마다 앞에 붙는다.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = ["1장_복양.md", "2장_연주_허도.md", "3장_완성.md", "4장_하비.md", "5장_백마.md",
         "6장_연진.md", "7장_관도_토산.md", "8장_관도_발밑.md", "9장_관도_허유.md",
         "10장_관도_목책.md", "11장_관도_장합.md", "12장_관도_완결.md"]
COND = re.compile(r"\s*〔([^〔〕]*)〕\s*$")
HEAD = re.compile(r"^(#+)\s+(.*)$")
SAY = re.compile(r"^\*\*([^*]+)\*\*:\s*(.*)$")
OPT = re.compile(r"^- ▸ \*\*(.+?)\*\*(?:\s*—\s*(.*?))?\s*\(`([^`]+)`\)\s*$")


def strip_cond(s):
    m = COND.search(s)
    if not m:
        return s.strip(), None
    return s[: m.start()].rstrip(), m.group(1).strip()


def mode_of(cond):
    if not cond:
        return None, None
    if cond.startswith("판정:"):
        return None, None
    if "시간 제한" in cond:
        return "timer", None
    if "되풀이" in cond or "고른 것은 사라짐" in cond:
        n = 2 if "두 번" in cond else 0
        return "repeat", n
    return None, cond


def convert(path):
    lines = path.read_text(encoding="utf-8").split("\n")
    try:
        start = lines.index("---") + 1
    except ValueError:
        start = 0
    ev = []
    stack = []  # (level, cond or None)
    last_cond = None
    cur_choice = None
    para = []

    def ctx():
        return [c for _, c in stack if c]

    engr = None
    for raw in lines[start:]:
        s = raw.strip()
        if not s:
            engr = None
            continue
        if engr is not None:
            body, cond = strip_cond(s)
            engr["lines"].append({"text": body, "c": [cond] if cond else []})
            continue
        if s == "*〈새김〉*":
            engr = {"t": "engrave", "lines": [], "c": ctx()}
            ev.append(engr)
            continue
        if s.startswith("*〈장면〉"):
            ev.append({"t": "card", "text": s.strip("*").replace("〈장면〉", "").strip(), "c": ctx()})
            continue
        m = HEAD.match(s)
        if m:
            cur_choice = None
            level = len(m.group(1))
            title, cond = strip_cond(m.group(2))
            while stack and stack[-1][0] >= level:
                stack.pop()
            if title.strip() == "이어서":
                cond_use = None
            else:
                cond_use = cond
            stack.append((level, cond_use))
            if level <= 2 and title.strip() != "이어서":
                ev.append({"t": "scene", "title": title.strip(), "loc": "", "c": ctx()})
            continue
        if s.startswith("(") and s.endswith(")"):
            continue
        if s.startswith("*〈장소〉") or s.startswith("*<장소>"):
            loc = s.strip("*").replace("〈장소〉", "").strip()
            for e in reversed(ev):
                if e["t"] == "scene":
                    e["loc"] = loc
                    break
            continue
        if s.startswith("**[선택]**"):
            body, cond = strip_cond(s)
            km = re.search(r"값 이름:\s*([^)]+)\)", body)
            md, real = mode_of(cond)
            cur_choice = {"t": "choice", "key": km.group(1).strip(), "mode": md, "n": real if md != "repeat" else None,
                          "c": ctx() + ([real] if (real and md is None) else []), "opts": []}
            if md == "repeat":
                rm = re.search(r"두 번", cond)
                cur_choice["times"] = 2 if rm else 0
            cur_choice.pop("n", None)
            ev.append(cur_choice)
            continue
        if s.startswith("- ▸") and cur_choice is not None:
            body, cond = strip_cond(s)
            om = OPT.match(body)
            if not om:
                raise SystemExit(f"{path.name}: 선택지 줄을 못 읽음: {s}")
            opt = {"text": om.group(1).strip(), "sub": (om.group(2) or "").strip(), "val": om.group(3).strip()}
            if cond:
                if cond.startswith("필요:"):
                    need, _, lock = cond[3:].partition("· 잠김:")
                    opt["need"] = need.strip()
                    opt["lock"] = lock.strip()
                else:
                    parts = [x.strip() for x in cond.split(" · ")]
                    tags = [x for x in parts[1:] if not re.search(r"[=≠!]|장 ", x)]
                    real = " · ".join([parts[0]] + [x for x in parts[1:] if x not in tags])
                    if real:
                        opt["c"] = real
                    if "운명" in tags:
                        opt["kind"] = "fate"
            cur_choice["opts"].append(opt)
            continue
        cur_choice = None
        body, cond = strip_cond(s)
        if cond == "위와 같음":
            cond = last_cond
        elif cond is not None:
            last_cond = cond
        c = ctx() + ([cond] if cond else [])
        if body == "/":
            ev.append({"t": "page", "c": c})
            continue
        sm = SAY.match(body)
        if sm:
            who = sm.group(1).strip()
            text = sm.group(2).strip()
            if text.startswith('"') and text.endswith('"') and text.count('"') == 2:
                text = text[1:-1]
            elif text.startswith('"') and text.endswith('"'):
                text = text[1:-1]
            ev.append({"t": "line", "who": who, "text": text, "c": c})
            continue
        if body.startswith(">"):
            ev.append({"t": "line", "who": "", "text": body.lstrip("> ").strip(), "book": 1, "c": c})
            continue
        ev.append({"t": "line", "who": "", "text": body, "c": c})
    return ev


def main():
    out = {}
    for i, f in enumerate(FILES, 1):
        out[str(i)] = convert(ROOT / f)
    if "--check" in sys.argv:
        for k, v in out.items():
            print(k, len(v), sum(1 for e in v if e["t"] == "choice"))
        return
    dst = ROOT / "tools" / "게임데이터.json"
    dst.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(dst, sum(len(v) for v in out.values()))


if __name__ == "__main__":
    main()
