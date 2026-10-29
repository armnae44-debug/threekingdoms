"""초상 그림에 그림자를 미리 그려 넣는다 (assets/portrait → assets/portrait_s).
게임에서 CSS drop-shadow 필터를 매 순간 계산하면 화면이 느려져서, 같은 그림자를 파일에 구워 둔다.
새 초상을 넣으면 이 스크립트를 다시 돌린다:  python3 tools/portrait_shadow.py
"""
import os, sys
from PIL import Image, ImageFilter, ImageChops
ROOT=os.path.join(os.path.dirname(__file__),'..','assets')
SRC=os.path.join(ROOT,'portrait'); DST=os.path.join(ROOT,'portrait_s')
os.makedirs(DST,exist_ok=True)
PAD=44                     # 옆으로 번지는 그림자 자리 (위·아래는 늘리지 않는다: 키와 발 위치를 그대로 두려고)
names=sys.argv[1:] or sorted(f for f in os.listdir(SRC) if f.endswith('.webp'))
for f in names:
    im=Image.open(os.path.join(SRC,f)).convert('RGBA'); w,h=im.size
    a=im.getchannel('A')
    big=Image.new('L',(w+2*PAD,h),0); big.paste(a,(PAD,0))
    # drop-shadow(0 20px 28px rgba(0,0,0,.85))
    s1=Image.new('L',big.size,0); s1.paste(big,(0,20)); s1=s1.filter(ImageFilter.GaussianBlur(14)).point(lambda v:int(v*.85))
    # drop-shadow(0 0 2px rgba(0,0,0,.6))
    s2=big.filter(ImageFilter.GaussianBlur(1)).point(lambda v:int(v*.6))
    sh=ImageChops.lighter(s1,s2)
    out=Image.new('RGBA',big.size,(0,0,0,0)); out.putalpha(sh)
    out.alpha_composite(im,(PAD,0))
    out.save(os.path.join(DST,f),'WEBP',quality=88,method=6)
print(len(names),'장')
