/* 원고 재생기 규칙표.
   원고에는 표지 이름만 있고 계산은 없다. 그 계산을 여기 모은다.
   - L[장][표지] : 참/거짓을 돌려주는 함수
   - V[장][이름] : `이름=값` 꼴 판정의 값을 돌려주는 함수 (한 번 정하면 그 판에서 바뀌지 않는다)
   - S[장][칸]   : {칸} 자리에 들어갈 글
   - on(장, 값이름, 값, R) : 선택했을 때 생기는 일 (유대, 은, 기록, 옛 깃발)
   - start(장, R), end(장, R)
   R 은 재생기가 넘겨주는 도구: R.v(키,장) R.has(키,값,장) R.L(표지,장) R.V(이름,장) R.c(조건문,장)
   R.chance(이름,확률) R.bond(id,n,기억) R.b(id) R.F(=state.flags) R.st(=state) R.rec(id,n) R.susp() */
var MS_RULES=(function(){
const L={},V={},S={};
for(let i=1;i<=12;i++){L[i]={};V[i]={};S[i]={};}
const G={}; /* 어느 장에서나 쓰는 표지 */

/* ---------- 공통 ---------- */
G['조노 유대 높음']=R=>R.b('jono')>=6;
G['조노 유대 8 이상']=R=>R.b('jono')>=8;
G['소칠 유대 높음']=R=>R.b('sochil')>=6;
G['의심 4 이상']=R=>R.susp()>=4;
G['의심 8 이상']=R=>R.susp()>=8;
G['4장 살림']=R=>R.L('살림',4);
G['3장 조앙 생존']=R=>R.L('조앙 생존',3);
G['3장 전위 생존']=R=>R.L('전위 생존',3);
G['석두 생존']=R=>R.L('석두 생존',2)&&!R.L('조원 죽음',3);

/* ---------- 2장 ---------- */
L[2]['왕삼과 가까움']=R=>R.has('wang','give')||R.has('askNext','give');
L[2]['조노 유대 낮음']=R=>R.b('jono')<3;
L[2]['단서 있음']=R=>['ledger','store','people'].some(x=>R.has('probe',x));
L[2]['단서 없음']=R=>!R.L('단서 있음',2);
L[2]['찾음']=R=>(R.has('spot','desk')&&(R.has('probe','ledger')||R.has('probe','store')))||(R.has('spot','keeper')&&R.has('probe','people'))||(R.has('spot','sacks')&&R.has('probe','store'));
L[2]['빈손']=R=>R.v('spot')!==undefined&&!R.L('찾음',2);
L[2]['석두 죽음']=R=>R.L('빈손',2)&&R.chance('2-seokdu',0.5);
L[2]['석두 생존']=R=>!R.L('석두 죽음',2);
L[2]['소칠 쇠약']=R=>R.L('빈손',2)||R.has('silver','meat')||R.has('silver','none');
L[2]['소칠 가르침']=R=>R.has('teach','teach');
V[2]['설득']=R=>{ if(!R.has('use','report')) return undefined;
  const p={proof:R.L('찾음',2)?0.75:0.5,men:0.3,trade:0.5}[R.v('how')]||0.4; return R.chance('2-persuade',p)?'성공':'실패'; };
V[2]['담판']=R=>R.has('use','deal')?(R.chance('2-deal',0.55)?'성공':'실패'):undefined;

/* ---------- 3장 ---------- */
V[3]['미행']=R=>{ const t=R.v('tail'); if(t==='go') return R.chance('3-tail',0.6)?'성공':'실패';
  if(t==='jono') return R.chance('3-tail',R.b('jono')>=3?0.75:0.4)?'성공':'실패'; return undefined; };
V[3]['물']=R=>R.has('dw','water')?(R.chance('3-water',0.6)?'성공':'실패'):undefined;
V[3]['말']=R=>(R.has('ca','horse')&&!R.c('2장 use=hold',3)&&!R.c('2장 담판=성공',3))?(R.chance('3-horse',0.6)?'성공':'실패'):undefined;
V[3]['경고']=R=>{ if(!R.has('ca','warn')) return undefined; if(R.V('미행',3)==='성공') return '성공'; return R.chance('3-warn',0.5)?'성공':'실패'; };
V[3]['둘째 준비']=R=>{ const p=R.v('prep'); return Array.isArray(p)&&p[1]&&p[1]!=='stop'?p[1]:undefined; };
L[3]['말을 얻음']=R=>R.has('ca','horse')&&(R.c('2장 use=hold',3)||R.c('2장 담판=성공',3)||R.V('말',3)==='성공');
L[3]['말을 몰래 끌어냄']=R=>R.V('말',3)==='성공';
L[3]['극 되찾음']=R=>R.has('dw','tell')||(R.V('경고',3)==='성공'&&R.V('미행',3)==='성공')||(R.has('ca','horse')&&R.V('미행',3)==='성공'&&R.L('말을 얻음',3))||R.has('gate','fetch');
L[3]['전위 맑음']=R=>R.V('물',3)==='성공'||R.V('경고',3)==='성공'||(R.L('말을 얻음',3)&&R.V('미행',3)==='성공')||(R.has('dw','tell')&&R.V('미행',3)!=='성공');
L[3]['아무것도 안 함']=R=>{ const p=R.v('prep'); return !p||(Array.isArray(p)&&p.filter(x=>x!=='stop').length===0); };
L[3]['하나 이상 함']=R=>!R.L('아무것도 안 함',3);
L[3]['prep 두 번을 다 쓴 뒤']=R=>{ const p=R.v('prep'); return Array.isArray(p)&&p.filter(x=>x!=='stop').length>=2; };
L[3]['은 두 덩이 이상']=R=>(R.st().silver||0)>=2;
L[3]['아직 안 한 준비가 있을 때']=R=>{ const p=R.v('prep')||[]; return ['dianwei','caoang','men'].some(x=>!p.includes(x)); };
L[3]['전위 생존']=R=>{ if(R.L('극 되찾음',3)) return true;
  if(R.has('first','dianwei')){ const g=R.v('gate'); if(g==='fetch') return true; if(g==='spear') return R.L('전위 맑음',3); if(g==='stand') return R.L('전위 맑음',3)&&R.chance('3-stand',0.5); }
  return false; };
V[3]['cs판정']=R=>{ const c=R.v('cs'); if(c==='shout') return R.chance('3-shout',0.4+(R.v('ca')?0.2:0))?'성공':'실패';
  if(c==='mine') return R.chance('3-mine',0.5+(R.has('men','armed')?0.1:0))?'성공':'실패'; return undefined; };
L[3]['성공']=R=>R.V('cs판정',3)==='성공';
L[3]['실패']=R=>R.V('cs판정',3)==='실패';
L[3]['조앙 생존']=R=>R.L('말을 얻음',3)||R.V('경고',3)==='성공'||(R.has('first','caoang')&&(R.has('cs','horse')||R.V('cs판정',3)==='성공'));
L[3]['위험']=R=>!(R.has('first','men')||R.has('men','route'));
const SQ3=R=>{ const fm=R.v('first'); const risky=fm==='dianwei'?['sochil','wangsam']:fm==='caoang'?['jono','sochil']:['sochil','jono','wangsam'];
  return risky.slice().sort((a,b)=>R.b(a)-R.b(b))[0]; };
const NM={jono:'조노',wangsam:'왕삼',sochil:'소칠'};
V[3]['빠진 사람']=R=>R.L('위험',3)?NM[SQ3(R)]:undefined;
L[3]['다치는 사람 있음']=R=>R.has('first','men')&&!R.has('men','armed')&&!R.has('men','route');
V[3]['다친 사람']=R=>{ if(!(R.v('men')!=='armed'&&R.v('men')!=='route')) return undefined; const o=['wangsam','jono','sochil'].sort((a,b)=>R.b(a)-R.b(b)); return NM[o[0]]; };
L[3]['조원 죽음']=R=>R.has('river','leave')&&R.L('석두 생존',2);
L[3]['빠진 사람 다침']=R=>R.has('river','leave')&&R.L('석두 죽음',2);
L[3]['조원 다 삶']=R=>!R.L('조원 죽음',3);
V[3]['부축']=R=>{ const hurt=R.V('다친 사람',3), fell=R.L('빠진 사람 다침',3)?R.V('빠진 사람',3):null;
  return ['왕삼','조노','소칠'].find(n=>n!==hurt&&n!==fell); };
L[3]['군후 됨']=R=>R.L('전위 생존',3)||R.L('조앙 생존',3);
L[3]['바꿈']=R=>R.L('전위 생존',3)||R.L('조앙 생존',3);
L[3]['2장 왕삼과 가까움']=R=>R.L('왕삼과 가까움',2);
S[3]['빠진사람']=R=>R.V('빠진 사람',3)||'석두';
S[3]['다친사람']=R=>R.V('다친 사람',3)||'왕삼';

/* ---------- 4장 ---------- */
V[4]['old']=R=>R.has('dig','old')?(R.chance('4-old',0.55+(R.b('jono')>=6?0.15:0))?'성공':'실패'):undefined;
V[4]['folk']=R=>R.has('dig','folk')?(R.chance('4-folk',0.55)?'성공':'실패'):undefined;
const HELD=R=>(R.has('dig','survey')?1:0)+(R.V('old',4)==='성공'?1:0)+(R.V('folk',4)==='성공'?1:0);
L[4]['가진 것 둘']=R=>HELD(R)>=2;
L[4]['가진 것 하나']=R=>HELD(R)===1;
L[4]['가진 것 없음']=R=>HELD(R)===0;
L[4]['가진 것 있음']=R=>HELD(R)>0;
V[4]['물길']=R=>{ if(R.has('tent','same')) return 'late'; const p=R.v('pin'); if(p===undefined) return undefined;
  return p==='w'?'ok':p==='none'?'late':'half'; };
V[4]['사면']=R=>{ const d=R.v('defect'); if(d==='one') return R.chance('4-defect',0.6)?'성공':'실패';
  if(d==='three') return R.chance('4-defect',0.55)?'성공':'실패'; return undefined; };
L[4]['살림']=R=>{ if(!R.has('lvbu','spare')||R.v('spare')===undefined) return false;
  const ok=R.V('물길',4)==='ok'; let p={leash:ok?0.6:0.5,dianwei:ok?0.55:0.45,future:ok?0.4:0.3}[R.v('spare')];
  if(R.has('guard','water')) p+=0.05; if(R.has('defect','three')) p+=0.05; if(!ok&&R.L('바꿈',3)) p+=0.05;
  return R.chance('4-spare',Math.min(0.7,p)); };
L[4]['못 살림']=R=>!R.L('살림',4);

/* ---------- 5장 ---------- */
V[5]['5장 성과']=R=>R.V('물길',4)==='ok'?'인정':(R.V('물길',4)==='half'?'부분':'미인정');
V[5]['성과']=V[5]['5장 성과'];
L[5]['장료가 불러 세움']=R=>R.V('5장 성과',5)==='인정'&&R.susp()>=4;
L[5]['호거아를 앎']=R=>R.V('미행',3)==='성공';
V[5]['밤손님']=R=>{ if(!R.L('호거아를 앎',5)) return undefined;
  if(R.L('전위 생존',3)) return R.c('3장 dw=tell',5)?'전위':undefined; return '전만'; };
L[5]['2장 찾음']=R=>R.L('찾음',2);
L[5]['전위 근신']=R=>R.V('밤손님',5)==='전위'&&R.has('dq_go','go',5);
G['밤손님=전위']=R=>R.V('밤손님',5)==='전위';
G['밤손님=전만']=R=>R.V('밤손님',5)==='전만';
G['전위 근신']=R=>R.L('전위 근신',5);
G['장수 군 앙금']=R=>R.has('well','defend',5)||R.has('dq_go','go',5);
G['2장 소칠 가르침']=R=>R.L('소칠 가르침',2);

/* ---------- 7장 ---------- */
G['꿈이라 함']=R=>R.has('c1',4,7)||R.v('c1',7)==='4';
G['4장 물길=ok']=R=>R.V('물길',4)==='ok';

/* ---------- 8장 ---------- */
G['곽가가 찾아옴']=R=>R.susp()>=7;

/* ---------- 10장 ---------- */
G['왕삼 왼팔']=R=>R.has('fall','carry',6)||R.has('fall','wang',6);
/* 10장 피해: 장마다 판에 따라 쌓는다 */
const LOSS=R=>{ let n=0;
  if(R.has('relief','half',10)) n++; if(R.has('position','breach',10)) n++; if(R.has('attention','signals',10)) n++;
  if(R.has('empty','half',10)) n++; if(R.has('gate','open',10)) n++; if(R.has('endure','last',10)) n++; if(R.has('flag','wait',10)) n++;
  return n; };
G['loss 1 이상']=R=>LOSS(R)>=1;
G['loss 2 이상']=R=>LOSS(R)>=2;
G['12A 전사자 있음']=R=>!R.L('4장 살림',10)&&(R.has('position','breach',10)||R.has('relief','half',10));
S[10]['fitK']=R=>MSkr(Math.max(60,(R.st().troop||160)-LOSS(R)*12));
S[10]['reserve']=R=>'마흔 명';
S[10]['halfReserve']=R=>'스무 명';
S[11]['출격K']=R=>MSkr(Math.max(60,Math.min(220,(R.st().troop||160)-LOSS(R)*20-40)));
S[11]['지원K']=R=>MSkr(Math.max(80,300-Math.max(60,Math.min(220,(R.st().troop||160)-LOSS(R)*20-40))));
S[11]['죽은사람']=R=>'덕배'; S[12]['죽은사람']=R=>'덕배';
S[12]['빠진사람']=R=>'석두'; S[12]['다친사람']=R=>'왕삼';

/* ---------- 11·12장 만총 쪽 ---------- */
const REC=R=>{ const r=[];
  if(R.has('b9_stir','make',8)) r.push('쇠고리');
  if(R.has('question','ready',5)||R.has('a6_granary','why',5)) r.push('원소 기병');
  if(R.has('dr','know',7)) r.push('병기 그림');
  if(R.has('a9_wuchao','point',8)||R.has('b9_wuchao','point',8)) r.push('오소');
  if(R.has('a9_map','give',8)||R.has('b9_map','give',8)) r.push('걸음 지도');
  if(R.has('dig','survey',4)) r.push('우물');
  if(R.has('vouch','seen',11)) r.push('가후 꾀');
  if(R.has('count','num',2)) r.push('장부');
  return r; };
G['기록 있음']=R=>REC(R).length>0;
G['기록 3개 이상']=R=>REC(R).length>=3;
V[11]['기록 으뜸']=R=>REC(R)[0];
G['기록=쇠고리']=R=>REC(R).includes('쇠고리');
G['기록=병기 그림']=R=>REC(R).includes('병기 그림');
G['기록=원소 기병']=R=>REC(R).includes('원소 기병');
G['고향 거짓']=R=>R.has('origin','lie',1);
const TWO=R=>{ const well=R.has('origin','lie',1)||R.has('learn','well',2)||R.has('gj','oldlie',4); const mer=R.has('learn','merchant',2)||R.has('gj','newlie',4); return well&&mer; };
G['스승 둘']=R=>TWO(R);
G['서역 상인']=R=>String(R.v('c1',7))==='3';
G['여포 살림 말함']=R=>R.L('살림',4);
G['여포 목줄']=R=>R.has('spare','leash',4);
G['하후씨 물음']=R=>R.has('use','report',2)&&R.V('설득',2)==='성공';
const NUMS=R=>{ const a=[]; if(R.has('count','num',2)||R.has('gjLend','give',8)||R.has('gjtest','fast',8)) a.push('장부'); if(R.has('count','num',4)) a.push('우물'); if(R.has('dr','know',7)) a.push('그림'); return a; };
V[11]['숫자']=R=>NUMS(R)[0];
G['숫자=장부']=R=>NUMS(R).includes('장부');
G['숫자=우물']=R=>NUMS(R).includes('우물');
G['숫자=그림']=R=>NUMS(R).includes('그림');
G['숫자 0개']=R=>NUMS(R).length===0;
G['숫자 1개']=R=>NUMS(R).length===1;
G['숫자 2개 이상']=R=>NUMS(R).length>=2;
G['숫자 기록']=R=>NUMS(R).length>0;
G['만총 조사']=R=>R.has('a10_warn','name',9)||R.has('b11_warn','name',9)||R.susp()>=8;
const SPY=R=>(R.has('a10_warn','name',9)||R.has('b11_warn','name',9)?2:0)+(REC(R).includes('오소')?1:0)+(R.has('vouch','neck',11)?1:0)+(TWO(R)?1:0)+(String(R.v('c1',7))==='3'?1:0)+(R.has('gjtest','slow',8)||R.has('gjtest','dunno',8)?1:0);
const SEER=R=>(REC(R).includes('원소 기병')?2:0)+(R.L('꿈이라 함',7)?1:0);
V[11]['판정']=R=>{ if(!R.L('만총 조사',11)) return 'plain'; const sp=SPY(R),se=SEER(R); return (se>=2&&se>=sp)?'앞일':(sp>=3?'간자':'스승'); };
G['원소 안의 일']=R=>R.has('a10_warn','name',9)||R.has('b11_warn','name',9)||REC(R).includes('오소')||R.has('vouch','neck',11);
G['감춤']=R=>R.has('dr','plain',7)||R.has('gjLend','tear',8)||R.has('gjtest','slow',8);
G['말 바뀜']=R=>TWO(R)||String(R.v('c1',7))==='3';
G['말 바꾼 기록']=R=>R.has('origin','lie',1)||R.L('꿈이라 함',7)||TWO(R)||R.has('simaSrc','lie',12);
G['편지 병사 있음']=R=>R.has('b9_rescue','hold',8)||R.has('b9_letter','report',8);
G['도망']=R=>R.L('만총 조사',12)&&R.has('who','read',12)&&R.L('말 바꾼 기록',12)&&!R.L('조노 유대 8 이상',12);

/* ---------- 선택했을 때 ---------- */
function on(ch,key,val,R){
  const F=R.F, b=(id,n,m)=>R.bond(id,n,m);
  const k=ch+':'+key+'='+val;
  switch(k){
    /* 1장 */
    case '1:night=cover': b('jono',1,'수색 기병이 지날 때 내가 그의 기침을 막았다'); F.ch1_night='cover'; break;
    case '1:night=stone': b('jono',1,'돌을 던져 수색 기병을 딴 데로 돌렸다'); F.ch1_night='stone'; break;
    case '1:thirst=dig': b('jono',3,'복양 도랑에서 마실 물을 파냈다'); F.ch1_water=true; break;
    case '1:thirst=wait': b('jono',2,'복양 도랑에서 밤새 순찰 시각을 세었다'); F.ch1_patrol=true; break;
    case '1:thirst=drink': b('jono',-1,'복양에서 썩은 물을 마시고 앓아누웠다'); F.ch1_sick=true; break;
    case '1:origin=lie': F.ch1_origin='lie'; break;
    case '1:origin=vague': F.ch1_origin='vague'; break;
    /* 2장 */
    case '2:wang=pass': b('wangsam',-2,'얻어맞는 것을 보고 지나쳤다'); break;
    case '2:askNext=leave': b('wangsam',-1,'사정을 다 듣고도 그냥 일어섰다'); break;
    case '2:style=share': b('wangsam',4,'국 한 그릇을 같이 나눠 먹자고 했다'); break;
    case '2:style=respect': b('wangsam',4,'맞으면서도 주먹을 들지 않은 것을 알아봐 주었다'); break;
    case '2:style=plain': b('wangsam',3,'쏟아진 국 대신 내 국을 내밀었다'); break;
    case '2:teach=teach': b('sochil',5,'창 쥐는 법을 한 달간 붙잡고 가르쳤다'); F.ch2_taught=true; break;
    case '2:teach=back': b('sochil',2,'첫 훈련에서 뒷줄에 세워 주었다'); break;
    case '2:teach=ignore': b('sochil',-2,'정강이를 걷어차이는 것을 보고만 있었다'); break;
    case '2:learn=cover': b('jono',1,'백부장 앞에서 내 말을 맞춰 주었다'); F.ch2_teacher='well'; break;
    case '2:learn=well': F.ch2_teacher='well'; break;
    case '2:learn=merchant': F.ch2_teacher='merchant'; break;
    case '2:learn=servant': F.ch2_teacher='servant'; break;
    case '2:fence=push': R.alive().forEach(x=>b(x,1,'첫 명령을 사흘 밤을 새워 지켰다')); break;
    case '2:fence=buy': R.st().silver=Math.max(0,(R.st().silver||0)-1); break;
    case '2:count=num': R.rec('lit2'); break;
    case '2:use=report': R.alive().forEach(x=>b(x,4,'우리 밥그릇을 위해 위쪽을 물고 늘어졌다')); break;
    case '2:use=deal': R.alive().forEach(x=>b(x,2,'우리 조만은 굶지 않게 해 주었다')); R.st().silver=(R.st().silver||0)+2; break;
    case '2:use=bribe': R.alive().forEach(x=>b(x,-4,'우리가 굶는 동안 뒷돈을 받았다')); R.st().silver=(R.st().silver||0)+3; break;
    case '2:use=hold': R.st().silver=(R.st().silver||0)+2; break;
    case '2:silver=doc': R.st().silver=Math.max(0,(R.st().silver||0)-2); b('sochil',3,'앓아누웠을 때 의원을 불러 주었다'); break;
    case '2:silver=meat': R.st().silver=Math.max(0,(R.st().silver||0)-1); b('sochil',2,'앓아누웠을 때 고기를 사다 먹였다'); break;
    case '2:silver=none': b('sochil',-2,'앓아누웠을 때 아무것도 해 주지 않았다'); break;
    /* 3장 */
    case '3:buy=buy': R.st().silver=Math.max(0,(R.st().silver||0)-2); return {again:'prep'};
    case '3:river=dive': case '3:river=reach': R.alive().forEach(x=>b(x,2,'육수에서 물에 빠진 사람을 건져 냈다')); break;
    case '3:river=leave': R.alive().forEach(x=>b(x,-2,'육수에서 떠내려가는 사람을 돌아보지 않았다')); break;
    case '3:men=armed': F.armed=true; break;
    case '3:tail=jono': b('jono',1,'연회의 사내 뒤를 밟는 일을 맡겼다'); break;
    case '3:vow=promise': case '3:vow=call': R.alive().forEach(x=>b(x,1,'완성에서 돌아온 밤, 모닥불 앞에서 한 말')); break;
    case '4:dig=old': b('jono',1,'하비 마을 노인들에게서 말을 끌어내 주었다'); break;
    case '5:well=jono': b('jono',2,'우물가 다툼을 맡기고 뒤를 믿어 주었다'); break;
    case '5:well=defend': R.alive().forEach(x=>b(x,1,'우물가에서 우리 편을 들어 막아섰다')); break;
    case '6:withdraw=cart': b('jono',2,'수레를 맡기고 뒤처리를 믿어 주었다'); break;
    case '10:fake=jono': b('jono',1,'위장 행렬을 맡겼다'); break;
    case '11:bye=jono': b('jono',2,'떠나기 전 마지막 말을 나눴다'); break;
    case '11:bye=wangsam': b('wangsam',2,'떠나기 전 마지막 말을 나눴다'); break;
    case '11:bye=sochil': b('sochil',2,'떠나기 전 마지막 말을 나눴다'); break;
    /* 4장 */
    case '4:dig=survey': R.rec('well'); F.ch5_gauge=true; break;
    case '4:count=num': R.rec('well',1); break;
    case '4:gj=oldlie': F.ch5_gjAnswer='oldlie'; break;
    case '4:gj=newlie': F.ch5_gjAnswer='newlie'; break;
    case '4:guard=water': F.ch5_water=true; break;
    /* 5장 이후: 의심에 쌓이는 것 */
    case '5:question=ready': case '5:a6_granary=why': R.rec('yuanCav'); break;
    case '5:zlSeat=front': R.rec('zlSeat'); break;
    case '6:early6=go': R.rec('early6'); break;
    case '7:c1=4': R.rec('dream'); break;
    case '7:dr=know': R.rec('drawKnow'); break;
    case '7:dr=plain': R.rec('withheld'); break;
    case '8:b9_stir=make': R.rec('stirrup'); break;
    case '8:a9_wuchao=point': case '8:b9_wuchao=point': R.rec('oso'); break;
    case '8:a9_map=give': case '8:b9_map=give': R.rec('map'); break;
    case '8:gjtest=fast': R.rec('gjFast'); break;
    case '8:gjtest=slow': case '8:gjtest=dunno': R.rec('gjHide'); break;
    case '8:gjLend=give': R.rec('gjLedger'); break;
    case '9:a10_warn=name': case '9:b11_warn=name': R.rec('zhanghe'); break;
    case '11:vouch=neck': R.rec('neck'); break;
    case '11:vouch=seen': R.rec('jiaxu'); break;
    case '12:plead2=sima': case '12:plead=sima': R.rec('sima'); break;
  }
  return null;
}

function start(ch,R){
  const st=R.st();
  if(ch===1){ st.rank='졸'; st.squad=[]; R.addSq('jono','조노(趙老)','노련한 병사'); st.silver=0; }
  if(ch===2){ if(!R.sq('wangsam')) R.addSq('wangsam','왕삼(王三)','방패병'); if(!R.sq('sochil')) R.addSq('sochil','소칠(小七)','어린 병사'); }
  if(ch===3){ st.rank='십장'; }
  if(ch===4){ st.rank=R.L('군후 됨',3)?'군후':'십장'; }
  if(ch>=5){ st.rank='군후'; if(ch===5) st.troop=R.V('5장 성과',5)==='인정'?200:160; }
  if(ch>=5){ const F=R.F; F.lubuSpared=R.L('살림',4); F.dianweiLives=R.L('전위 생존',3); F.caoangLives=R.L('조앙 생존',3); F.xiapi=R.V('물길',4); }
}
function end(ch,R){
  const F=R.F;
  if(ch===3){ F.dianweiLives=R.L('전위 생존',3); F.caoangLives=R.L('조앙 생존',3); }
  if(ch===4){ F.lubuSpared=R.L('살림',4); }
}
return {L,V,S,G,on,start,end};
})();
function MSkr(n){ n=Math.round(n/10)*10; const h=Math.floor(n/100), t=n%100; return ((['','백','이백','삼백','사백'][h]||'')+({0:'',10:'열',20:'스물',30:'서른',40:'마흔',50:'쉰',60:'예순',70:'일흔',80:'여든',90:'아흔'})[t])||'몇'; }
