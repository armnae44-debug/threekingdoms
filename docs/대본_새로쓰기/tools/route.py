#!/usr/bin/env python3
"""원고(md)에서 한 판(경로)만 골라 조건 없이 이어 붙인 읽기용 원고를 만든다.

쓰는 법:
    python3 route.py 원고.md 경로.json > 출력.md

경로.json 예:
    {"이름": "다 살리는 판",
     "값": {"tail": "go", "prep": ["dianwei", "caoang"], "1장 thirst": "dig"},
     "표지": ["미행=성공", "전위 생존"],
     "칸": {"다친사람": "왕삼"}}

- "값"은 선택지 값. 여러 개를 고르는 선택지는 목록으로 준다.
- "표지"는 판정 결과나 상태처럼 `=` 없는 조건, 또는 `미행=성공`처럼 값으로 쓰지 않는 조건.
- "칸"은 원고의 {이름} 자리를 채운다.

조건 문법: 〔A, B〕는 A 그리고 B, "A 또는 B"는 둘 중 하나, "!A"는 아님, "k≠v"는 값이 v가 아님.
`#` 소제목에 붙은 조건은 다음 같은 급(또는 더 높은 급) 소제목까지의 묶음 전체에 적용된다.
"""
import json
import re
import sys

COND = re.compile(r"\s*〔([^〔〕]*)〕\s*$")


def split_top(s, sep):
    out, depth, cur, i = [], 0, "", 0
    while i < len(s):
        if s[i] == "(":
            depth += 1
        elif s[i] == ")":
            depth -= 1
        if depth == 0 and s.startswith(sep, i):
            out.append(cur)
            cur = ""
            i += len(sep)
            continue
        cur += s[i]
        i += 1
    out.append(cur)
    return [x.strip() for x in out if x.strip()]


class Route:
    def __init__(self, spec):
        self.name = spec.get("이름", "")
        self.vals = spec.get("값", {})
        self.flags = set(spec.get("표지", []))
        self.slots = spec.get("칸", {})
        self.unknown = set()

    def has(self, k, v):
        cur = self.vals.get(k)
        if isinstance(cur, list):
            return v in cur
        return cur == v

    def atom(self, t):
        t = t.strip()
        if t.startswith("(") and t.endswith(")"):
            return self.expr(t[1:-1])
        if t.startswith("!"):
            return not self.atom(t[1:])
        if t in self.flags:
            return True
        if "≠" in t:
            k, v = t.split("≠", 1)
            return not self.has(k.strip(), v.strip())
        if "=" in t:
            k, v = t.split("=", 1)
            k, v = k.strip(), v.strip()
            if k in self.vals:
                return self.has(k, v)
            return False
        self.unknown.add(t)
        return False

    def expr(self, s):
        parts = split_top(s, ", ")
        for p in parts:
            alts = split_top(p, " 또는 ")
            if not any(self.atom(a) for a in alts):
                return False
        return True


def render(lines, route):
    out = []
    stack = []  # (level, ok)
    last_cond = None
    choice_key = None
    choice_ok = False
    in_body = False
    for raw in lines:
        line = raw.rstrip("\n")
        if not in_body:
            if line.strip() == "---":
                in_body = True
            continue
        m = re.match(r"^(#+)\s+(.*)$", line)
        if m:
            level = len(m.group(1))
            while stack and stack[-1][0] >= level:
                stack.pop()
            title = m.group(2)
            ok = True
            cm = COND.search(title)
            if cm:
                ok = route.expr(cm.group(1))
                title = title[: cm.start()]
            stack.append((level, ok))
            if all(o for _, o in stack) and level <= 2:
                out.append("")
                out.append("#" * level + " " + title.strip())
            choice_key = None
            continue
        if not all(o for _, o in stack):
            continue
        s = line.strip()
        if not s:
            continue
        if s.startswith("(") and s.endswith(")"):
            continue  # 작업 메모
        cm = COND.search(s)
        cond = cm.group(1) if cm else None
        body = s[: cm.start()].rstrip() if cm else s
        if cond == "위와 같음":
            cond = last_cond
        if s.startswith("**[선택]**"):
            km = re.search(r"값 이름:\s*([^)]+)\)", s)
            choice_key = km.group(1).strip() if km else None
            choice_ok = route.expr(cond) if cond else True
            continue
        if s.startswith("- ▸"):
            if not (choice_key and choice_ok):
                continue
            vm = re.search(r"\(`([^`]+)`\)", body)
            lm = re.search(r"\*\*(.+?)\*\*", body)
            if vm and route.has(choice_key, vm.group(1)) and (cond is None or route.expr(cond)):
                out.append("")
                out.append("> ▸ " + (lm.group(1) if lm else body))
            continue
        choice_key = None
        if cond is not None:
            last_cond = cond
            if not route.expr(cond):
                continue
        body = re.sub(r"\{([^{}]+)\}", lambda mm: route.slots.get(mm.group(1), mm.group(0)), body)
        if body == "/":
            out.append("")
            out.append("—")
            continue
        out.append("")
        out.append(body)
    return out


def main():
    src, spec = sys.argv[1], sys.argv[2]
    route = Route(json.load(open(spec, encoding="utf-8")))
    lines = open(src, encoding="utf-8").readlines()
    out = render(lines, route)
    print("# 읽기용: " + route.name)
    print("\n".join(out).strip())
    if route.unknown:
        sys.stderr.write("처리 못 한 조건: " + " | ".join(sorted(route.unknown)) + "\n")


if __name__ == "__main__":
    main()
