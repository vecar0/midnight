# PixAI 프롬프트 — Minuit 캐릭터 Vol. I~IV (자연어)

## 1. 모델 · LoRA · 해상도

| 항목 | 추천 | 이유 |
|---|---|---|
| 모델 | **Tsubaki.3** | PixAI 최신 애니 모델(2026-09). 자연어·태그 둘 다 받고, 최대 2048×2048, 결과를 자연어로 고치는 편집이 강화됨 |
| 대안 | Tsubaki.2 | 자연어 모델(DiT), LoRA 지원. 해상도는 약 1024×1024급 |
| (참고) 태그식 | Haruka v2 | SDXL, 태그 프롬프트용. SDXL LoRA 생태계 전부 사용 가능 → 레퍼런스가 이걸로 만들어졌다면 이쪽이 그림체 재현에 유리 |
| 해상도 | **세로 2:3, 긴 변 최대** (Tsubaki.3 기준 약 1344×2016) | 전신 그림을 세로는 무릎 위로 잘라 쓰고 가로는 전신으로 쓰기 때문에 크게 |
| (Tsubaki.2) | 832×1248 근처 2:3 | |
| LoRA | 레퍼런스 게시물에 쓰인 LoRA를 그대로. 없으면 PixAI LoRA 목록에서 작가 이름(sushispin 등)으로 검색해 **고른 모델과 호환되는 것만** | LoRA 호환은 모델마다 다름. 강도 0.6~0.8, 2개 이하 |

- **가장 확실한 방법:** 레퍼런스 PixAI 게시물을 열어 모델·LoRA·설정을 확인하고 "같은 설정으로 생성(Remix)"에서 시작.
- Tsubaki.2는 Steps·CFG·Sampler 설정이 없다(문서 기준). Tsubaki.1·Haruka v2는 설정 가능.
- 얼굴 유지: Vol. I 결과가 마음에 들면 **그 이미지를 레퍼런스로 넣거나 시드를 고정**하고 옷·포즈 문단만 바꾼다.

## 2. 프롬프트 구조

`[그림체 문단] + [캐릭터 문단] + [Vol.별 문단] + [피할 것 문단]` — 영어 그대로 붙여 넣는다.

### 그림체 문단 (모든 Vol. 공통)

```
A Korean game-CG style anime illustration with a near-monochrome palette of black, white and cool greys, where the only warm color is the pink in her skin. Crisp dark ink line art with slightly jagged hand-drawn edges, a thicker outer contour and very thin inner lines. Her hair is drawn as dozens of separate ultra-thin strands with loose flyaway strands crossing her face, and it is very glossy, with a sharp white highlight band across the top of the head and deep shadows underneath. Hard-edged cel shading with detailed cast shadows, such as hair shadows falling on her face and neck. Porcelain-pale skin with small glossy shine spots and strong pink blush on the cheeks, nose tip and ears, and glossy coral-pink lips slightly parted. Strong backlight and a white rim light around her silhouette, high contrast, cinematic lighting, soft bright haze behind her, shallow depth of field.
```

(Tsubaki.3은 태그도 받으므로, 그림체를 더 당기고 싶으면 이 문단 끝에 한 줄 추가:
`Style tags: sushispin, kithera, yd (orange maru), channel (caststation), modare, game cg, jaggy lines, thick outlines.`)

### 캐릭터 문단 (모든 Vol. 공통)

```
She is a young woman with long, straight silver-grey hair and blunt, straight-cut bangs with side locks framing her face. She has droopy, half-closed grey eyes with a thick black upper lash line flicked outward, red eyeshadow smudged under her eyes, and a thin black choker. Her expression is cool and a little bored, and she looks straight into the camera.
```

### Vol. I — 밤샘 공부 (고프코어 스트리트)

```
She is a hip, modern Cinderella in a street fashion magazine photoshoot, pulling an all-nighter. She wears an oversized heather-grey hoodie layered under a cropped black puffer vest, baggy washed-grey carpenter jeans, chunky silver-grey trail sneakers, big over-ear headphones around her neck, thin rectangular silver glasses, stacked silver rings, black nail polish, and a small black crossbody bag hanging from her shoulder with a tiny silver pumpkin keychain. Her hair is loosely half tied up with a black claw clip. She sits on a metal bar stool with her left foot on the footrest so that knee is raised, her left forearm resting across that knee and her hand propping up her chin while loosely holding a single silver pen. Her right leg hangs down toward the floor and her right hand rests on the seat. The camera angle is slightly low, and she is shown in full body from head to shoes against a plain light grey background.
```

### Vol. II — 마법이 걸리기 시작 (Y2K 레이어드)

```
She is a hip, modern Cinderella in a street fashion magazine photoshoot, as the magic begins. She wears a cropped grey knit bolero over a white lace-trimmed camisole, a low-rise black pleated micro skirt layered over baggy grey track pants, slouchy white leg warmers, chunky black Mary Jane platform shoes, a vintage black leather racer jacket slipping off both shoulders, black ribbon bows clipped into her hair, and a small silver bird charm necklace. She sits on a metal bar stool, leaning forward with both forearms crossed on her raised knee, a small notebook held loosely in one hand. The camera angle is slightly low, and she is shown in full body against a plain light grey background.
```

### Vol. III — 나갈 준비 끝 (고딕 테크웨어)

```
She is a hip, modern Cinderella in a street fashion magazine photoshoot, ready to go out. She wears a sheer black mesh long-sleeve top with an asymmetric cutout, a thin silver chain harness over it, black satin parachute cargo pants with silver buckles, a cropped black bomber jacket with a faux fur collar slipping off one shoulder, black fingerless gloves, silver ear cuffs, and knee-high lace-up black platform boots. She sits on a metal bar stool with her legs crossed, one hand running through her hair. The camera angle is slightly low, and she is shown in full body against a plain light grey background.
```

### Vol. IV — 자정 (완성 룩)

```
She is a hip, modern Cinderella in a street fashion magazine photoshoot at midnight, in her finished look. She wears a metallic silver cropped corset top, an oversized black tailored blazer worn off her shoulders, low-rise baggy black jeans with a silver wallet chain, a rhinestone hair chain draped across her head like a modern tiara, and a small silver clock pendant stopped at twelve. On her feet are clear transparent platform heels, and one heel is slipping off and dangling from her toes, like Cinderella's glass slipper about to fall. She sits on a metal bar stool with one knee raised, her forearm across it and her chin resting on her hand. The camera angle is slightly low, and she is shown in full body against a plain light grey background.
```

### 피할 것 문단 (모든 Vol. 공통, 프롬프트 끝에)

```
Avoid: ball gowns, frilly princess dresses, any text, logos or watermarks, extra fingers or limbs, a 3D or photographic look, airbrushed soft rendering, flat webtoon coloring, other hair colors, glowing eyes, and extra people.
```

- 네거티브 칸이 있는 모델(Haruka v2 등)이면 이 문단 대신 네거티브 칸에 같은 내용을 쓴다.

## 3. 뽑은 뒤

1. 마음에 드는 걸 Claude에게 보낸다 → `illust` 스킬 점검표로 점검
2. 힉스필드로 배경 제거 · 업스케일 (소량 크레딧)
3. 앱 화면(큰 틀 + 흑백 장식)에 넣어 확인
