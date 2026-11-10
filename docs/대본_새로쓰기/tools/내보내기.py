"""원고를 내보내기/ 폴더로 내보낸다: docx, txt, 줄바꿈한 md.

md는 한 줄을 WIDTH 글자 안팎에서 끊어, 휴대폰이나 메모장에서
가로로 밀지 않고 읽을 수 있게 한다(마크다운으로 보여 줄 때 모양은 같다).
사용: python3 tools/내보내기.py  (원고 폴더에서 실행)
"""
import re, subprocess, os

WIDTH = 38
CH = [
    ("1장_복양.md", "ch1_puyang"), ("2장_연주_허도.md", "ch2_yeonju"),
    ("3장_완성.md", "ch3_wanseong"), ("4장_하비.md", "ch4_habi"),
    ("5장_백마.md", "ch5_baekma"), ("6장_연진.md", "ch6_yeonjin"),
    ("7장_관도_토산.md", "ch7_gwando"), ("8장_관도_발밑.md", "ch8_balmit"),
    ("9장_관도_허유.md", "ch9_heoyu"), ("10장_관도_목책.md", "ch10_mokchaek"),
    ("11장_관도_장합.md", "ch11_jangha"), ("12장_관도_완결.md", "ch12_wangyeol"),
]
BAD_START = re.compile(r'^(#|[-*+>|]|\d+[.)]|=+$|`{3})')

def wrap_line(line):
    if len(line) <= WIDTH or line.startswith(('#', '|', '![', '```')) or line.strip() in ('/', '---'):
        return [line]
    m = re.match(r'^(\s*(?:[-*+] |\d+\. |> )?)', line)
    lead = m.group(1)
    cont = ' ' * len(lead) if not lead.strip().startswith('>') else lead
    words = line[len(lead):].split(' ')
    out, cur, has = [], lead, False
    for w in words:
        trial = (cur + ' ' + w) if has else cur + w
        if len(trial) > WIDTH and has and not BAD_START.match(w):
            out.append(cur.rstrip())
            cur = cont + w
        else:
            cur = trial
        has = True
    out.append(cur.rstrip())
    return out

def main():
    os.makedirs('내보내기', exist_ok=True)
    for src, name in CH:
        base = os.path.join('내보내기', name)
        subprocess.run(['pandoc', src, '-o', base + '.docx'], check=True)
        subprocess.run(['pandoc', src, '-t', 'plain', '-o', base + '.txt'], check=True)
        text = open(src, encoding='utf-8').read().replace('](img/', '](../img/')
        lines, fence = [], False
        for l in text.split('\n'):
            if l.startswith('```'):
                fence = not fence
            lines.extend([l] if fence else wrap_line(l))
        open(base + '.md', 'w', encoding='utf-8').write('\n'.join(lines))
        print(name)

if __name__ == '__main__':
    main()
