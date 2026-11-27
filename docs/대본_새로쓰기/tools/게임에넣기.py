#!/usr/bin/env python3
"""원고 재생기를 index.html 에 넣는다. 원고를 고친 뒤에는 이것만 다시 돌리면 게임 본문이 따라온다.

    python3 tools/게임에넣기.py

1. tools/게임변환.py 로 원고를 데이터로 바꾸고
2. 데이터 · 규칙(게임규칙.js) · 엔진(게임엔진.js) · 화면 연결을 index.html 의 <!--MS_BEGIN--> … <!--MS_END--> 사이에 넣는다.
3. 시작 화면 다음에 원고 1장이 이어지게 한다(옛 1장 대신).
"""
import json
import subprocess
import sys
from pathlib import Path

T = Path(__file__).resolve().parent
ROOT = T.parent.parent.parent
HTML = ROOT / "index.html"

UI = r"""
/* 원고 재생기를 게임 화면에 잇는다 */
const MS_SAVE_KIND='ms';
/* 게임 화면은 옛 장 번호(14장)를 받아 지금 번호(12장)로 바꿔 보여 준다. 원고 장 번호를 옛 번호로 넘긴다 */
const MS_OLD={1:1,2:2,3:4,4:5,5:6,6:7,7:8,8:9,9:10,10:12,11:13,12:14};
const MSG={
  random:()=>Math.random(), flags:()=>state.flags, state:()=>state,
  bond:(id,n,m)=>{ if(sq(id)){ bond(id,n,m); render(); } }, bondOf:id=>(sq(id)||{bond:0}).bond,
  rec:(id,n)=>{ try{ rec(id,n); render(); }catch(e){} }, susp:()=>state.suspicion||0,
  alive:()=>alive().map(s=>s.id), addSq:(id,n,t)=>{ addSquad(id,n,t); render(); }, sq:id=>sq(id),
  warn:w=>console.warn('[원고 재생기] 조건을 못 풀었다:',w),
  say:(who,text,cb,kind)=>{
    const act = who==='나' ? 'me' : (who ? (AB_ACTORS[who]||'general') : null);
    setActor(act, who||'');
    say(who, kind==='book'?text:q96(who,text), ()=>read74Ready(cb));
  },
  engrave:(lines,cb)=>{ setActor(null); engrave(lines.map(l=>['',l]), cb); },
  scene:(bg,title,cb)=>{ setActor(null); document.getElementById('a74Location').textContent=title.replace(/<[^>]+>/g,' · ').replace(/\s+·\s+$/,''); scene(bg,title,()=>read74Ready(cb)); },
  choose:(list,timer,cb)=>{
    const L=list.map(o=>({text:o.text, sub:o.sub, act:o.val, need:o.need||undefined, needMsg:o.lock||undefined}));
    choose(L, c=>cb(list.find(o=>o.val===c.act)));
  },
  chapterEnd:(ch,cb)=>{ setActor(null); state.chapter=MS_OLD[ch+1]||state.chapter; render(); engrave([['','제'+MS_OLD[ch]+'장 끝']], cb); },
  finish:()=>{ setActor(null); engrave([['','끝'],['','관도는 여기서 끝난다.']], ()=>{ try{ location.reload(); }catch(e){} }); },
  save:s=>{ state.chapter=MS_OLD[s.ch]; render(); try{ save82Mark({kind:MS_SAVE_KIND, ms:s}); }catch(e){} }
};
function msStart(saved){
  document.body.classList.add('a74Reading');
  if(!saved){ state.squad=[]; state.suspicion=0; state.flags=state.flags||{}; }
  state.flags.msMode=true;
  MS.start(MSG, saved||null);
}
/* 불러오기: 원고 재생기에서 남긴 자리는 원고 재생기로 다시 연다 */
const save82LoadMS0=save82Load;
save82Load=function(s){
  if(s&&s.ptr&&s.ptr.kind===MS_SAVE_KIND){
    try{ abStop(); abMenu(false); }catch(e){}
    ['engrave','interlude','overwrite','slipDeath'].forEach(id=>{ const el=document.getElementById(id); if(el) el.className=''; });
    dom.center.innerHTML=''; dom.choices.classList.remove('show'); dom.narr.classList.remove('show'); dom.cont.classList.remove('show');
    document.getElementById('nameCard')?.classList.remove('show'); document.getElementById('titleCard')?.classList.remove('show');
    document.querySelectorAll('.ov.show').forEach(o=>o.classList.remove('show'));
    for(const k of Object.keys(state)) delete state[k];
    Object.assign(state, JSON.parse(JSON.stringify(s.ptr.state)));
    LOG=(s.log||[]).slice(); dom.topBar.classList.add('show'); dom.black.classList.add('hide'); render();
    msStart(JSON.parse(JSON.stringify(s.ptr.ms)));
    return;
  }
  return save82LoadMS0(s);
};
/* 장 이동: 원고 재생기의 그 장 처음으로 간다. A선은 여포가 죽은 판, B선은 여포를 살린 판 */
dev75Go=function(r,c){
  try{ abStop(); abMenu(false); }catch(e){}
  document.getElementById('titleCard')?.classList.remove('show'); document.getElementById('nameCard')?.classList.remove('show');
  dom.topBar.classList.add('show'); dom.black.classList.add('hide');
  state.flags={}; state.squad=[]; state.suspicion=0; state.silver=0; LOG=[];
  const B=r==='B';
  const saved={ch:c,i:0,loop:null,seen:{},rnd:{'4-spare':B},choices:{4:{lvbu:B?'spare':'kill',spare:'leash',tent:'obs',pin:'w'}}};
  document.body.classList.add('a74Reading'); state.flags.msMode=true;
  MS.start(MSG, saved, c);
  ['jono','wangsam','sochil'].forEach(id=>{ const s=sq(id); if(s) s.bond=Math.max(s.bond,6); }); render();
};
"""

CSS = "<style>.msBook{display:block;font-style:italic;color:#c9b98f;border-left:2px solid #6b5a3a;padding-left:10px}</style>"

OLD_WAKE = "setTimeout(()=>{ setBg('fire'); dom.black.classList.add('hide'); dom.center.innerHTML=''; ch1_open(); },1200);"
NEW_WAKE = "setTimeout(()=>{ setBg('fire'); dom.black.classList.add('hide'); dom.center.innerHTML=''; msStart(); },1200);"


def main():
    subprocess.run([sys.executable, str(T / "게임변환.py")], check=True)
    data = (T / "게임데이터.json").read_text(encoding="utf-8")
    rules = (T / "게임규칙.js").read_text(encoding="utf-8")
    engine = (T / "게임엔진.js").read_text(encoding="utf-8")
    for bad in ("</script", "<!--"):
        assert bad not in data and bad not in rules and bad not in engine, bad
    block = ("<!--MS_BEGIN-->\n" + CSS + "\n<script>\n/* 원고 재생기: 이 자리는 docs/대본_새로쓰기/tools/게임에넣기.py 가 만든다. 손으로 고치지 않는다. */\n"
             + "var MS_DATA=" + data + ";\n" + rules + "\n" + engine + "\n" + UI + "\n</script>\n<!--MS_END-->\n")
    html = HTML.read_text(encoding="utf-8")
    if "<!--MS_BEGIN-->" in html:
        a = html.index("<!--MS_BEGIN-->")
        b = html.index("<!--MS_END-->") + len("<!--MS_END-->\n")
        html = html[:a] + block + html[b:]
    else:
        i = html.rindex("</body>")
        html = html[:i] + block + html[i:]
    if OLD_WAKE in html:
        html = html.replace(OLD_WAKE, NEW_WAKE)
    assert NEW_WAKE in html, "시작 화면 연결 자리를 못 찾았다"
    HTML.write_text(html, encoding="utf-8")
    print("index.html 갱신:", len(block) // 1024, "KB")


if __name__ == "__main__":
    main()
