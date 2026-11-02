# 그림 최종 목록 (이번에 한꺼번에 뽑을 것)

지난번 목록(6장)을 지금 화면에 맞춰 다시 검토했습니다.

**뺀 것 2장**
- `frame_bronze`(청동 창틀): 창이 모두 비단 족자 모양으로 통일됐습니다. 청동 틀을 넣으면 오히려 섞여 보입니다.
- `brush_stroke`(붉은 붓 자국): 마우스를 올릴 때만 잠깐 보입니다. 휴대폰에서는 아예 안 보입니다.

**공통 규칙**
- 배경과 같은 화풍으로 그립니다. 프롬프트 앞에 아래 문장을 붙입니다.
  ```
  cinematic semi-realistic digital painting, late Eastern Han dynasty China around 200 AD, muted earthy palette, dramatic warm light, highly detailed, no text, no watermark
  ```
- "가운데 검게"라고 적은 것은 가운데를 **완전한 검은색**으로, "흰 바탕"이라고 적은 것은 **완전한 흰색**으로 뽑아 주세요. 제가 그 부분을 투명하게 따냅니다.
- 이름 없이 주셔도 됩니다. 제가 보고 나누겠습니다.

---

## A. 게임 화면 (8장)

| # | 파일 | 쓰는 곳 | 크기 | 프롬프트 |
|---|---|---|---|---|
| 1 | `menu_bg` | 명부·사서·기록 창을 열었을 때 뒤에 깔림 | 1920×1080 | `night, inside an army tent, a low wooden desk with bamboo slip scrolls, ink brush and inkstone, a single oil lamp, a rolled map, warm lamplight, deep shadows, no people` |
| 2 | `seal_shang` | 명부에서 다친 사람에게 찍는 `傷` 도장 | 315×320 | 지금 `歿` 도장 그림(`assets/ui/seal_mo.webp`)을 레퍼런스로 넣고: `same red square seal stamp, same carving style and wear, the single character 傷, plain white background` |
| 3 | `card_frame` | 명부 얼굴 액자, 들것 고르기 카드 | 600×600 | `round aged bronze medallion frame, Han dynasty cloud pattern on the rim, front view, flat even lighting, center completely flat pure black` |
| 4 | `ink_empty` | 빈 창 (지금은 연한 `無` 글자) | 800×500 | `sumi-e ink wash painting on plain white paper, one empty army tent and a bare flagpole, minimal, lots of empty space, light grey ink` |
| 5 | `paper_plan` | **발석거 설계 퍼즐** 바탕 | 1600×1000 | `top view of an old wooden work board covered with a sheet of rough hemp paper, blank, slight stains and charcoal smudges at the edges, a charcoal stick and a ruler stick at the side, flat lighting, nothing drawn in the middle` |
| 6 | `aim_field` | **조준 미니게임**: 위에서 비스듬히 본 표적 | 1920×1080 | `high angle view from behind a wooden palisade looking across a no-man's land at an enemy earth mound with three tall wooden archer towers on top, one tower covered with hanging leather hides, yellow banners, clear visibility, daytime, dust` |
| 7 | `triage_bg` | **들것 고르기** 배경 | 1920×1080 | `aftermath of a battle at a broken camp gate, wounded soldiers lying behind a fallen wooden door used as cover, three empty wooden stretchers on the ground, smoke, grey morning light, no faces visible` |
| 8 | `cart_escape` | **12장 B 수레** 장면 순간 그림 (사건 그림처럼 잠깐 뜸) | 1920×1080 | `a supply cart loaded with wounded soldiers bursting out between burning tents straight toward the viewer, a line of spearmen in the foreground lowering spears, yellow 袁 banners behind, dust and chaos` |

- 5·6·7번은 새 미니게임 세 개에 꼭 필요합니다.
- 8번은 없어도 됩니다. 없으면 그 장면의 배경을 그대로 씁니다.

---

## B. Steam 출시용 (3장)

Steam 상점과 라이브러리에 넣을 그림입니다. 아래 3장만 주시면 규격 7가지(920×430, 462×174, 1232×706, 748×896, 600×900, 3840×1240, 로고)는 제가 잘라 만들고 제목 붓글씨(`官渡之路`)도 얹습니다.

| # | 파일 | 크기 | 프롬프트 |
|---|---|---|---|
| 9 | `keyart_wide` | 3840×2160 | `a lone Han dynasty foot soldier seen from behind standing on a wooden palisade at dusk, looking out over a vast army camp of countless tents and torches stretching to the horizon, smoke columns, navy banners with golden 曹 near him and yellow 袁 banners far away, epic scale, leave the upper left third as calm sky for a title` |
| 10 | `keyart_tall` | 1500×2250 | 9번과 같은 장면을 세로 구도로: `vertical composition, the soldier small at the bottom, towering smoke and torches above, upper half calm sky for a title` |
| 11 | `icon` | 1024×1024 | `a single red square Chinese seal stamp with the character 渡, carved stone texture, on plain white background, centered, nothing else` |

---

## C. 전에 말씀드리고 아직 기다리는 것

| 그림 | 상태 |
|---|---|
| 여포 전신 (`lvbu`, `lvbu_free`) | 방천화극을 길게 해서 다시 뽑기로 하셨습니다 |
| 전위 사건 그림 | 무기를 짧고 무거운 卜자 모양 극 둘로 고쳐서 다시 뽑기로 하셨습니다 |
| 목책 무너지는 그림 (새 원본) | 전에 보내 주신 파일이 작업 환경이 새로 시작되면서 지워졌습니다. **다시 보내 주세요.** 그림은 바퀴 달린 충차이고 대본은 "통나무를 메고 온다"라서, 대본 한 줄("큰 방패 뒤로 적병들이 굵은 통나무를 얹은 수레를 밀고 오는 것이 보였다")을 바꿔야 맞습니다 |
| 사건 그림 원본 5장 (문추·땅굴·오소·이별·전위) | 지금은 여러 장이 모인 시트에서 잘라 써서 흐릿합니다. 원본이 있으면 바꿔 넣겠습니다 |

---

**합계**: 꼭 필요한 것 10장 (A 1~7, B 9~11) + 있으면 좋은 것 1장 (A 8) + 다시 뽑기로 한 것들.
