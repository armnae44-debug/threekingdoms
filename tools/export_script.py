# 5~12장 대본을 게임 데이터(index.html)에서 그대로 뽑아 docs/대본/ 에 md로 쓴다.
# 쓰는 법: python3 tools/export_script.py
import re, json, os, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = open(os.path.join(ROOT, 'index.html'), encoding='utf8').read()

def grab(name):
    m = re.search(name + r'\s*=\s*([\[{].*?[\]}]);\n', H, re.S)
    return json.loads(m.group(1))

C67, CH8, AB = grab('C67_DATA'), grab('CH8_DATA'), grab('AB_DATA')
DISP = {6: 5, 7: 6, 8: 7, 9: 8, 10: 9, 11: 9, 12: 10, 13: 11, 14: 12}

def disp_title(t):
    return re.sub(r'제(\d+)장', lambda m: '제%d장' % DISP.get(int(m.group(1)), int(m.group(1))), t or '')

def cond_list(w):
    if isinstance(w, dict):
        out = []
        for k, v in w.items():
            if k == 'cond': out += v
            elif k == 'lvbu': out.append('여포 판' if v else '여포 없는 판')
            else: out.append('%s=%s' % (k, v))
        return out
    return list(w or [])

def removed(w):
    return any('__removed' in c for c in cond_list(w))

def cond_txt(w):
    c = cond_list(w)
    return (' 〔조건: %s〕' % ', '.join(c)) if c else ''

class Out:
    def __init__(self): self.lines = []; self.n = 0
    def num(self): self.n += 1; return '`#%d`' % self.n
    def add(self, s=''): self.lines.append(s)

def who_fmt(who):
    who = (who or '').strip()
    return ('**%s**: ' % who) if who else ''

def emit(o, L):
    epi = False
    for e in L:
        if removed(e.get('when')): continue
        t = e.get('type')
        if t == 'scene':
            if e.get('epilogue') and not epi:
                epi = True; o.add(); o.add('## 후일담 ([그 뒤의 이야기] 버튼을 눌렀을 때)'); o.add()
            head = ' · '.join(x for x in [disp_title(e.get('title')), e.get('location')] if x)
            o.add(); o.add('### %s%s' % (head, cond_txt(e.get('when')))); o.add()
        elif t == 'line':
            o.add('%s %s%s%s  ' % (o.num(), who_fmt(e.get('who')), e.get('text', ''), cond_txt(e.get('when')))); o.add()
        elif t == 'choice':
            o.add('%s **[선택]** (값 이름: %s)%s' % (o.num(), e.get('key', ''), cond_txt(e.get('when'))))
            for op in e.get('options', []):
                ws = op.get('when') or []
                hid = [c.replace('숨김:', '', 1) for c in ws if c.startswith('숨김:')]
                need = [c for c in ws if not c.startswith('숨김:')]
                hid_t = ((' 〔숨김:%s〕' % ', '.join(hid)) if hid else '') + ((' 〔필요: %s〕' % ', '.join(need)) if need else '')
                lock = (' 〔잠김: %s〕' % op['lock']) if op.get('lock') else ''
                sub = (' — %s' % op['sub']) if op.get('sub') else ''
                o.add('  - ▸ **%s**%s (`%s`)%s%s' % (op.get('text', ''), sub, op.get('value', ''), hid_t, lock))
            o.add()

FILES = [
    ('대본_05장_백마.md', '5장 백마', [('A선 (여포가 죽은 판)', C67['6A']), ('B선 (여포가 산 판)', C67['6B'])]),
    ('대본_06장_연진.md', '6장 연진', [('A선 (여포가 죽은 판)', C67['7A']), ('B선 (여포가 산 판)', C67['7B'])]),
    ('대본_07장_관도_토산.md', '7장 관도 · 토산', [('A·B선 같이 (여포 판 줄은 조건에 적음)', CH8)]),
    ('대본_08장_발밑.md', '8장 발밑', [('A선 (여포가 죽은 판)', C67['9A']), ('B선 (여포가 산 판)', C67['9B'])]),
    ('대본_09장_허유.md', '9장 허유', [('A선 (여포가 죽은 판)', C67['10A']), ('B선 (여포가 산 판)', C67['11B'])]),
    ('대본_10장_목책.md', '10장 목책', [('A선 (여포가 죽은 판)', AB['12A']), ('B선 (여포가 산 판)', AB['12B'])]),
    ('대본_11장_장합.md', '11장 장합', [('A선 (여포가 죽은 판)', AB['13A']), ('B선 (여포가 산 판)', AB['13B'])]),
    ('대본_12장_관도_완결.md', '12장 관도 · 완결', [('A선 (여포가 죽은 판)', AB['14A']), ('B선 (여포가 산 판)', AB['14B'])]),
]

today = datetime.date.today().isoformat()
for fn, title, parts in FILES:
    o = Out()
    o.add('# 대본 · %s' % title); o.add()
    o.add('%s 기준, 지금 게임에 들어 있는 그대로 뽑았다. 장 번호는 화면에 나오는 번호다.' % today); o.add()
    o.add('- 읽는 법: **이름**: 대사. 이름 없는 줄은 서술이다. `〔조건: …〕`은 그 판에서만 나오는 줄이다.')
    o.add('- 선택지는 `▸ 선택지 이름 — 설명 (값)`으로 적었다. `〔숨김〕`은 조건이 맞아야 보이는 선택지, `〔잠김〕`은 보이지만 고를 수 없는 선택지다.')
    o.add('- 줄 앞의 `#번호`는 수정 요청 때 위치를 짚는 번호다.'); o.add()
    for name, L in parts:
        o.add(); o.add('## ' + name); o.add()
        emit(o, L)
    open(os.path.join(ROOT, 'docs', '대본', fn), 'w', encoding='utf8').write('\n'.join(o.lines).rstrip() + '\n')
    print(fn, o.n)
