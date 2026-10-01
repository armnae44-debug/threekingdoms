# 관도지로

- `index.html` — 모바일(UI1) 버전
- `pc.html` — PC 버전 (`index.html`과 같고, 맨 위 PC 설정 한 줄만 다름)

## 그림·음악 넣는 법

파일을 아래 이름으로 `assets/` 폴더에 넣으면 게임이 알아서 불러온다. 없으면 기존 그라데이션/무음으로 진행된다.

| 종류 | 폴더 | 파일 이름 | 예 |
|---|---|---|---|
| 배경 | `assets/bg/` | `ch{장}_{배경키}.webp` (없으면 `{배경키}.webp`) | `ch1_ditch_day.webp` |
| 초상 | `assets/portrait/` | `{인물키}.webp` (배경 투명, 무릎 위까지) | `jono.webp` |
| 음악 | `assets/bgm/` | `{곡이름}.ogg` / `.m4a` / `.mp3` | `title.m4a` |

### 지금 들어 있는 것

| 파일 | 쓰이는 곳 |
|---|---|
| `portrait/jono.webp` | 조노 |
| `bg/ch9_camp.webp` | 9장 · 관도 본영 (목책) |
| `bg/ch1_fire.webp` | 1장 · 복양 야습 |
| `bg/ch1_ditch_night.webp` | 1장 · 도랑 밤 (첫날 밤 포함) |
| `bg/ch1_ditch_day.webp` | 1장 · 도랑 낮 |
| `bg/ch1_ditch_dawn.webp` | 1장 · 도랑 새벽 |
| `bg/ch2_camp.webp` | 2장 · 연주 군영 겨울 |
| `bg/ch2_camp_spring.webp` | 2장 · 건안 원년 봄 (신병 소칠 ~ 편성 개편) |
| `bg/ch2_camp_dusk.webp` | 2장 · 마무리 |
| `bgm/title.m4a` | 타이틀 |
| `bgm/ch1_raid.m4a` | 1장 · 복양 야습 (불) |
| `bgm/ch1_ditch.m4a` | 1장 · 도랑 (밤·낮·새벽) |

1장 배경 키: `fire`(야습), `ditch_night`, `ditch_day`, `ditch_dawn`
인물 키: 조조 `caocao`, 조노 `jono`, 여포 `lvbu`, 왕삼 `wangsam`, 소칠 `sochil`, 조홍 `caohong` … (`index.html`의 `NAME85` 참고)

### 음악 흐름

- 한 곡은 최소 1분 이어서 튼 뒤, 3.5초에 걸쳐 다음 곡과 겹쳐 넘어간다.
- 장면이 확 바뀌는 곡(지금은 `ch1_raid`)만 기다리지 않고 바로 넘어간다. `index.html`의 `URGENT86`에서 고친다.
- 한 번 나온 곡으로 다시 돌아오면 처음부터가 아니라 듣던 자리에서 이어진다.

### 인물 첫 등장

처음 나오는 인물은 섬광 + 화면 흔들림 + 이름패(한자 · 한글 · 한 줄 소개)로 등장한다.
한 줄 소개는 `index.html`의 `HERO86`에 적는다.

### 1인칭 시점

- 주인공 '나'는 화면에 그리지 않는다. 내가 말할 때는 듣는 상대가 화면에 남는다.
- 초상 그림이 없는 인물도 실루엣으로 세우지 않는다. `assets/portrait/`에 그림을 넣으면 그때부터 나온다.
- 다친 상태(`state.wounds`)면 시야 가장자리가 붉게 천천히 맥동한다.
