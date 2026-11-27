/* 원고 재생기. MS_DATA(게임변환.py가 만든 원고 데이터)와 MS_RULES(게임규칙.js)를 읽어 1~12장을 차례로 돌린다.
   화면은 game.say / game.choose / game.scene / game.bg 네 가지로만 건드린다(브라우저에서는 index.html의 함수, 시험할 때는 가짜). */
var MS=(function(){
const RU=MS_RULES;
const KEYS={}; /* 장마다 선택 값 이름 */
for(const ch in MS_DATA){ KEYS[ch]=new Set(MS_DATA[ch].filter(e=>e.t==='choice').map(e=>e.key)); }
/* 되풀이 선택의 범위: 선택 바로 뒤부터, 조건에 그 값 이름이 들어간 사건이 이어지는 데까지 */
const LOOP={};
for(const ch in MS_DATA){ const ev=MS_DATA[ch];
  ev.forEach((e,i)=>{ if(e.t!=='choice'||e.mode!=='repeat') return; const re=new RegExp('(^|[\\s(!,])'+e.key+'\\s*[=≠]');
    let j=i+1; while(j<ev.length&&(ev[j].c||[]).some(c=>re.test(c))) j++; LOOP[ch+':'+i]={start:i,end:j}; }); }

let S=null, game=null, warnSet=new Set();
function fresh(){ return {ch:1,i:0,choices:{},rnd:{},loop:null,seen:{}}; }
function M(){ return S; }

function splitTop(s,sep){ const out=[]; let d=0,cur='',i=0; while(i<s.length){ const c=s[i]; if(c==='(')d++; else if(c===')')d--;
  if(d===0&&s.startsWith(sep,i)){ out.push(cur); cur=''; i+=sep.length; continue; } cur+=c; i++; } out.push(cur); return out.map(x=>x.trim()).filter(Boolean); }

function keyCh(key,ch){ if(KEYS[ch]&&KEYS[ch].has(key)) return ch; for(let c=ch-1;c>=1;c--) if(KEYS[c]&&KEYS[c].has(key)) return c; return null; }
function rawV(key,ch){ const c=keyCh(key,ch); if(c===null) return undefined; return (S.choices[c]||{})[key]; }
function has(key,val,ch){ ch=ch||S.ch; val=String(val);
  const c=keyCh(key,ch);
  if(S.loop&&S.loop.ch===c&&S.loop.key===key&&c===S.ch) return S.loop.cur===val;
  const v=c===null?undefined:(S.choices[c]||{})[key];
  if(Array.isArray(v)) return v.map(String).includes(val);
  return v!==undefined&&String(v)===val; }

const API={
  v:(k,ch)=>rawV(k,ch||S.ch), has:(k,v,ch)=>has(k,v,ch),
  L:(n,ch)=>label(n,ch||S.ch), V:(n,ch)=>value(n,ch||S.ch), c:(s,ch)=>expr(s,ch||S.ch),
  chance:(id,p)=>{ if(S.rnd[id]===undefined) S.rnd[id]=(game.random?game.random():Math.random())<p; return S.rnd[id]; },
  bond:(id,n,m)=>game.bond(id,n,m), b:id=>game.bondOf(id), F:null, st:()=>game.state(), rec:(id,n)=>game.rec(id,n),
  susp:()=>game.susp(), alive:()=>game.alive(), addSq:(id,n,t)=>game.addSq(id,n,t), sq:id=>game.sq(id)
};
function label(name,ch){
  if(RU.L[ch]&&RU.L[ch][name]) return !!RU.L[ch][name](API);
  if(RU.G[name]) return !!RU.G[name](API);
  return undefined; }
function value(name,ch){
  for(let c=ch;c>=1;c--){ if(RU.V[c]&&RU.V[c][name]) return RU.V[c][name](API); }
  return undefined; }
let TEST=null; /* 시험용: route.py 와 같은 방식으로 조건을 판다 */
function tatom(t){ if(TEST.flags.has(t)) return true; const ne=t.indexOf('≠');
  if(ne>0){ const k=t.slice(0,ne).trim(), v=t.slice(ne+1).trim(); return !thas(k,v); }
  const eq=t.indexOf('='); if(eq>0){ const k=t.slice(0,eq).trim(), v=t.slice(eq+1).trim(); return (k in TEST.vals)?thas(k,v):false; } return false; }
function thas(k,v){ if(S.loop&&S.loop.key===k) return S.loop.cur===v; const c=TEST.vals[k]; return Array.isArray(c)?c.includes(v):c===v; }
function atom(t,ch){ t=t.trim();
  if(TEST){ if(t.startsWith('(')&&t.endsWith(')')) return expr(t.slice(1,-1),ch); if(t.startsWith('!')) return !atom(t.slice(1),ch); return tatom(t); }
  if(t.startsWith('(')&&t.endsWith(')')) return expr(t.slice(1,-1),ch);
  if(t.startsWith('!')) return !atom(t.slice(1),ch);
  if(RU.G[t]) return !!RU.G[t](API);
  let c=ch, rest=t; const m=t.match(/^(\d+)장\s+(.+)$/); if(m){ c=+m[1]; rest=m[2]; }
  const lb=label(rest,c); if(lb!==undefined) return lb;
  const ne=rest.indexOf('≠'), eq=rest.indexOf('=');
  if(ne>0||eq>0){ const neg=ne>0&&(eq<0||ne<eq); const i=neg?ne:eq; const k=rest.slice(0,i).trim(), v=rest.slice(i+1).trim();
    let ok; const jv=value(k,c);
    if(jv!==undefined) ok=String(jv)===v;
    else if(keyCh(k,c)!==null) ok=has(k,v,m?c:ch);
    else { const known=Object.keys(RU.V).some(cc=>RU.V[cc][k]); if(!known) warn(t,ch); ok=false; }
    return neg?!ok:ok; }
  warn(t,ch); return false; }
function expr(s,ch){ if(!s) return true; for(const p of splitTop(s,', ')){ if(!splitTop(p,' 또는 ').some(a=>atom(a,ch))) return false; } return true; }
function ok(e){ return (e.c||[]).every(c=>expr(c,S.ch)); }
function warn(t,ch){ const k=ch+':'+t; if(!warnSet.has(k)){ warnSet.add(k); if(game&&game.warn) game.warn(k); } }
function fill(text){ if(TEST&&TEST.slots) return String(text).replace(/\{([^{}]+)\}/g,(m0,n)=>TEST.slots[n]!==undefined?TEST.slots[n]:m0); return String(text).replace(/\{([^{}]+)\}/g,(m0,n)=>{ for(let c=S.ch;c>=1;c--){ const f=RU.S[c]&&RU.S[c][n]; if(f) return f(API); } return m0; }); }

const BGK=[[/불|화염|불길/, 'fire'],[/강|물속|육수|나루|개울|둑/, 'river'],[/연회|술/, 'feast'],[/새벽|동틀/, 'dawn'],[/군막|막사|천막|막간|본영 안|처소/, 'tent'],[/궁|허도|대궐/, 'palace'],[/들|길|평원|백마|연진/, 'field'],[/싸움|전장|목책|토산|성벽|사다리|진지/, 'battlefield'],[/밤/, 'night']];
function bgOf(title,loc){ const t=(title||'')+' '+(loc||''); for(const [re,k] of BGK) if(re.test(t)) return k; return 'camp'; }

function run(){ const ev=MS_DATA[S.ch];
  while(S.i<ev.length){
    const idx=S.i, e=ev[idx];
    if(S.again&&idx===S.again.at){ const ag=S.again; S.again=null;
      const back=ev.findIndex(x=>x.t==='choice'&&x.key===ag.key); const lp=LOOP[S.ch+':'+back]; const prev=(S.choices[S.ch]||{})[ag.key]||[];
      S.loop={ch:S.ch,key:ag.key,start:back,end:lp.end,times:prev.length+1,count:prev.length,picked:prev.filter(x=>x!=='stop'),cur:null};
      S.i=back; continue; }
    /* 되풀이 한 바퀴가 끝났나 */
    if(S.loop&&S.loop.ch===S.ch&&idx===S.loop.end){ const L0=S.loop;
      if(L0.cur!=='stop'&&(L0.times===0||L0.count<L0.times)&&remaining(L0).length){ S.i=L0.start; continue; }
      S.loop=null; }
    S.i++;
    if(!ok(e)) continue;
    if(e.t==='page') continue;
    if(e.t==='scene'){ game.save&&game.save(JSON.parse(JSON.stringify(Object.assign({},S,{i:idx})))); if(e.title){ return game.scene(bgOf(e.title,e.loc), e.title+(e.loc?'<br><small>'+e.loc+'</small>':''), run); } continue; }
    if(e.t==='line'){
      let text=fill(e.text);
      if(e.who===''&&!e.book){ /* 이어지는 서술 문단은 한 화면에 모은다 */
        let n=0; while(S.i<ev.length&&n<2){ if((S.loop&&S.i===S.loop.end)||(S.again&&S.i===S.again.at)) break; const f=ev[S.i]; if(f.t!=='line'||f.who!==''||f.book) break; if(!ok(f)){ S.i++; continue; } text+='\n\n'+fill(f.text); S.i++; n++; }
      }
      if(e.book){ return game.say('', '<span class="msBook">'+text+'</span>', run, 'book'); }
      return game.say(e.who, text, run);
    }
    if(e.t==='engrave'){ const ls=e.lines.filter(ok).map(x=>fill(x.text)); if(!ls.length) continue; return game.engrave(ls, run); }
    if(e.t==='card') return game.scene('camp', e.text, run);
    if(e.t==='choice') return doChoice(e,idx);
  }
  endCh(); }

function remaining(L0){ const e=MS_DATA[L0.ch][L0.start]; return e.opts.filter(o=>o.val!=='stop'&&!L0.picked.includes(o.val)&&(!o.c||expr(o.c,S.ch))); }

function doChoice(e,idx){
  const key=e.key, ch=S.ch, rep=e.mode==='repeat';
  let L0=rep?(S.loop&&S.loop.key===key&&S.loop.ch===ch?S.loop:null):null;
  if(rep&&!L0){ const lp=LOOP[ch+':'+idx]; L0=S.loop={ch,key,start:idx,end:lp.end,times:e.times||0,count:0,picked:[],cur:null}; }
  let opts=e.opts.filter(o=>!o.c||expr(o.c,ch));
  if(rep) opts=opts.filter(o=>!L0.picked.includes(o.val));
  /* 같은 값을 가진 선택지가 여럿 남으면 앞의 것만 */
  const seen=new Set(); opts=opts.filter(o=>{ if(seen.has(o.val)) return false; seen.add(o.val); return true; });
  if(!opts.length){ warn('선택지 없음 '+key,ch); S.loop=null; return run(); }
  const list=opts.map(o=>({text:o.text, sub:o.sub, val:o.val, need:o.need?(()=>expr(o.need,ch)):null, lock:o.lock}));
  game.choose(list, e.mode==='timer', pick=>{
    const val=pick.val;
    S.choices[ch]=S.choices[ch]||{};
    if(rep){ const arr=S.choices[ch][key]=Array.isArray(S.choices[ch][key])?S.choices[ch][key]:[]; arr.push(val); L0.picked.push(val); L0.cur=val; L0.count++; }
    else S.choices[ch][key]=val;
    const r=RU.on(ch,key,val,API);
    if(r&&r.again){ /* 은을 써서 한 번 더: 이 선택에 딸린 문단을 읽은 뒤 되풀이 선택으로 돌아간다 */
      const ev=MS_DATA[ch]; let j=S.i; const mine=new RegExp(key+'\\s*[=≠]');
      while(j<ev.length&&(ev[j].c||[]).some(c=>mine.test(c))) j++;
      S.again={at:j,key:r.again}; }
    run();
  });
}

function endCh(){ const ch=S.ch;
  RU.end(ch,API);
  if(ch>=12){ game.save&&game.save(S); return game.finish(); }
  game.chapterEnd(ch, ()=>{ S.ch=ch+1; S.i=0; S.loop=null; RU.start(S.ch,API); game.save&&game.save(S); run(); });
}

return {
  start(g,saved,ch){ game=g; API.F=g.flags(); S=saved||fresh(); if(ch){ S.ch=ch; S.i=0; S.loop=null; } if(!saved||ch){ if(ch&&ch>1){ RU.start(1,API); RU.start(2,API); } RU.start(S.ch,API); } run(); },
  stopAtEnd:false,
  test(spec){ TEST=spec?{flags:new Set(spec.flags),vals:spec.vals,slots:spec.slots}:null; },
  state:()=>S, expr:(s,ch)=>expr(s,ch||S.ch), label, value, warns:()=>[...warnSet]
};
})();
