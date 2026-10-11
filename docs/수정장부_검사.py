import re,sys
md=open(__import__('os').path.join(__import__('os').path.dirname(__file__),'수정장부.md'),encoding='utf-8').read()
h=open(__import__('os').path.join(__import__('os').path.dirname(__file__),'..','index.html'),encoding='utf-8').read()
sec=None
for line in md.split('\n'):
    if line.startswith('## '): sec=line[3:].split(' —')[0]; continue
    if not line.startswith('| ') or line.startswith('| 번호') or line.startswith('|---'): continue
    cells=[c.strip() for c in line.strip('|').split('|')]
    ids=cells[0]; m=re.search(r'`(.+?)`',line)
    if not m: continue
    old=m.group(1)
    n=h.count(old)
    print(f'{sec}\t{ids}\t{n}\t{old[:40]}')
