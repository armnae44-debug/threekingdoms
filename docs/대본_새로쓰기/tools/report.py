#!/usr/bin/env python3
"""해설본처럼 읽히는 문단을 찾는다.

쓰는 법:
    python3 report.py 원고.md [연속=3]

대사·속말·감각 없이 과거형 서술("~었다." "~였다." "~했다.")만
연속으로 N개 이상 이어지는 문단을 줄 번호와 함께 보여 준다.
물음표가 있거나 현재형 문장이 섞이면 끊긴 것으로 본다.
"""
import re
import sys

PAST = re.compile(r"(었|았|였|했|됐|졌|웠|렸|겼|냈|섰|왔|갔|났|봤|줬|뒀|쳤|켰|텄|셌|댔|랐|웠|혔|었었)다$")
COND = re.compile(r"\s*〔[^〕]*〕\s*$")


def sentences(p):
    p = COND.sub("", p)
    parts = re.split(r"(?<=[.?!])\s+", p.strip())
    return [s.strip() for s in parts if s.strip()]


def run(path, n):
    lines = open(path, encoding="utf-8").read().split("\n")
    body = False
    hits = 0
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if not body:
            body = s == "---"
            continue
        if not s or s.startswith(("#", "**", "-", ">", "(", "*", "/")):
            continue
        run_len, best = 0, 0
        for sent in sentences(s):
            core = sent.rstrip(".")
            if sent.endswith(".") and PAST.search(core) and "?" not in sent:
                run_len += 1
                best = max(best, run_len)
            else:
                run_len = 0
        if best >= n:
            hits += 1
            print(f"{i}: ({best}연속) {s[:90]}")
    print(f"-- {hits}곳", file=sys.stderr)


if __name__ == "__main__":
    run(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 3)
