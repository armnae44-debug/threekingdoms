# 5~12장 데이터 구조 검사: 죽었을 수 있는 사람이 조건 없이 나오는 줄, 쓰이지 않는 선택지 값, 나올 수 없는 조건
import re, json, os, collections
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H=open(os.path.join(ROOT,'index.html'),encoding='utf8').read()
def grab(n): return json.loads(re.search(n+r'\s*=\s*([\[{].*?[\]}]);\n',H,re.S).group(1))
C67,CH8,AB=grab('C67_DATA'),grab('CH8_DATA'),grab('AB_DATA')
DISP={6:5,7:6,8:7,9:8,10:9,11:9,12:10,13:11,14:12}
def conds(w):
    if isinstance(w,dict):
        out=[]
        for k,v in w.items():
            if k=='cond': out+=v
            elif k=='lvbu': out.append('lvbu=%s'%v)
            else: out.append('%s=%s'%(k,v))
        return out
    return list(w or [])
PARTS=[('5장',['6A','6B'],C67),('6장',['7A','7B'],C67),('7장',['CH8'],None),('8장',['9A','9B'],C67),('9장',['10A','11B'],C67),('10장',['12A','12B'],AB),('11장',['13A','13B'],AB),('12장',['14A','14B'],AB)]
MORTAL=['조노','왕삼','소칠','조앙','전위','관우']
# 선택지 값 모으기 (모든 장)
setvals=collections.defaultdict(set)
alltexts=[]
for ch,keys,D in PARTS:
    for k in keys:
        L=CH8 if k=='CH8' else D[k]
        for e in L:
            if e.get('type')=='choice':
                for o in e['options']: setvals[e.get('key')].add(str(o.get('value')))
used=collections.Counter()
for ch,keys,D in PARTS:
    for k in keys:
        L=CH8 if k=='CH8' else D[k]
        for e in L:
            for c in conds(e.get('when'))+[c for o in e.get('options',[]) for c in (o.get('when') or [])]:
                m=re.match(r'^!?(?:숨김:)?(?:cond:)?([A-Za-z_0-9]+)=(.+)$',c)
                if m: used[(m.group(1),m.group(2))]+=1
# 코드 쪽에서 쓰는 값도 센다 (choices['key']==='v' 같은 것)
code=re.sub(r'(C67_DATA|AB_DATA|CH8_DATA)\s*=\s*[\[{].*?[\]}];\n','',H,flags=re.S)
rep=collections.defaultdict(list)
for ch,keys,D in PARTS:
    for k in keys:
        L=CH8 if k=='CH8' else D[k]
        scene=[]; sc_title=''
        for i,e in enumerate(L):
            cs=conds(e.get('when'))
            if e.get('type')=='scene': scene=cs; sc_title=(e.get('title') or '')+' '+(e.get('location') or ''); continue
            if '__removed' in ' '.join(cs): continue
            allc=' '.join(cs+scene)
            if e.get('type')=='line':
                who=re.sub(r'\(.*','',e.get('who') or '').strip(); txt=e.get('text','')
                for p in MORTAL:
                    if (who==p or p in txt) and (p+' 생존' not in allc and p+' 있음' not in allc and p+'생존' not in allc and 'flag:'+{'조앙':'caoangLives','전위':'dianweiLives'}.get(p,'~') not in allc):
                        rep[ch].append(('생존조건 없음',k,i,p,(e.get('who') or '')+': '+txt[:50],sc_title))
            for c in cs:
                m=re.match(r'^!?(?:cond:)?([A-Za-z_0-9]+)=(.+)$',c)
                if m and m.group(1) in setvals and m.group(2) not in setvals[m.group(1)] and not re.match(r'^[<>]',m.group(2)):
                    rep[ch].append(('없는 값',k,i,c,(e.get('text') or '')[:50],sc_title))
for key,vals in setvals.items():
    for v in vals:
        if not used[(key,v)] and not re.search(r"""['"]%s['"]\]?\s*[=!]==\s*['"]%s['"]|%s\s*===?\s*['"]%s['"]|\.%s\s*===?\s*['"]%s['"]"""%(re.escape(key),re.escape(v),re.escape(key),re.escape(v),re.escape(key),re.escape(v)),code):
            rep['(전체)'].append(('안 쓰이는 선택 값',key,v,'','',''))
for ch in [p[0] for p in PARTS]+['(전체)']:
    items=rep.get(ch,[])
    c=collections.Counter(x[0] for x in items)
    print('==',ch,dict(c))
    for x in items[:400]: print('  ',x)
