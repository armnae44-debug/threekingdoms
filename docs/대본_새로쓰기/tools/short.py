#!/usr/bin/env python3
"""짧은 문장(공백 빼고 N자 이하)이 셋 넘게 연달아 나오는 문단을 찾는다."""
import re, sys
N = int(sys.argv[2]) if len(sys.argv) > 2 else 10
for i, line in enumerate(open(sys.argv[1], encoding='utf-8'), 1):
    s = re.sub(r'〔[^〕]*〕', '', line).strip()
    if not s or s.startswith(('#', '-', '**', '>', '(')):
        continue
    sents = [x for x in re.split(r'(?<=[.!?])\s+', s) if x]
    run = best = 0
    for x in sents:
        run = run + 1 if len(x.replace(' ', '')) <= N else 0
        best = max(best, run)
    if best >= 3:
        print(f"{i}: ({best}연속) {s[:90]}")
