# PixAI 프롬프트 — Minuit 캐릭터 Vol. I~IV

## 0. 먼저 할 일 (가장 중요)

레퍼런스를 만든 PixAI 게시물을 열어 **사용한 모델 · LoRA · 설정**을 확인한다.
게시물에 "Remix / 같은 설정으로 생성"이 있으면 그걸로 시작하고, 아래 프롬프트의 **캐릭터·옷·포즈 부분만** 바꿔 넣는다.
그림체는 프롬프트보다 **모델과 LoRA**에서 훨씬 많이 결정된다.

게시물 정보가 없으면: 단부루 작가 태그를 알아듣는 **Illustrious / NoobAI 계열 애니 모델**을 고른다.

## 1. 공통 설정

| 항목 | 값 |
|---|---|
| 크기 | 832 × 1216 (세로 2:3) |
| Steps | 28 |
| CFG | 5 ~ 6 |
| Sampler | Euler a (또는 DPM++ 2M Karras) |
| Hires fix | 1.5배, denoise 0.35 |
| Seed | 마음에 드는 Vol. I이 나오면 **그 시드를 고정**하고 Vol. II~IV는 옷·포즈 태그만 바꾼다 (얼굴 유지) |

가중치는 PixAI 문법 `(태그:1.2)`. NovelAI의 `1.7::태그::`는 PixAI에서 `(태그:1.3)` 정도로 약하게 옮겼다
(1.4를 넘기면 그림이 깨지기 쉽다).

## 2. 공통 앞부분 (그림체 · 품질) — 모든 Vol.에 그대로

```
masterpiece, best quality, amazing quality, very aesthetic, absurdres, newest,
(sushispin:1.3), (kithera:1.15), (yd (orange maru):1.15), channel (caststation), modare, (ratatatat74:0.9), (m m pb:0.6),
game cg, (jaggy lines:1.2), (thick outlines:1.2), (cel shading:1.15), (detailed shadows:1.25), glossy skin, shiny hair,
(backlighting:1.15), (rim light:1.15), (high contrast:1.2), dramatic lighting, depth of field, monochrome background,
```

## 3. 캐릭터 고정 부분 — 모든 Vol.에 그대로

```
solo, 1girl, (grey hair:1.3), silver hair, long hair, straight hair, (blunt bangs:1.2), sidelocks,
(grey eyes:1.2), (tareme:1.1), half-closed eyes, (red eyeshadow:1.2), eyeliner, long eyelashes,
pale skin, blush, black choker, expressionless, looking at viewer,
```

## 4. Vol.별 옷 · 포즈 · 배경 — 하나만 골라 붙인다

### Vol. I — 공부 모드, 꾸안꾸

```
(cropped hoodie:1.2), grey hoodie, open hoodie, white tank top, black track pants, wide leg pants, side stripe,
white sneakers, headphones around neck, (round eyewear:1.1), silver-framed eyewear, hairclip, half updo, chain necklace,
sitting, stool, knee up, (head rest:1.1), hand on own chin, holding pen, from below, full body,
simple background, grey background,
```

### Vol. II — 꾸미기 시작

```
(off-shoulder sweater:1.2), cropped sweater, white sweater, (denim skirt:1.1), pleated skirt, miniskirt, leg warmers,
black leather jacket, jacket on shoulders, chain belt, loafers, hairclip, chain necklace,
sitting, stool, leaning forward, crossed arms on knee, holding notebook, from below, full body,
simple background, grey background,
```

### Vol. III — 나갈 준비 끝

```
(black slip dress:1.2), satin, (see-through sleeves:1.1), mesh top, (oversized bomber jacket:1.1), off shoulder,
black pantyhose, platform boots, silver earrings, chain necklace,
sitting, stool, crossed legs, hand in own hair, from below, full body,
simple background, grey background,
```

### Vol. IV — 완성 룩 (자정)

```
(black corset:1.2), strapless, (layered necklace:1.1), silver chain, (leather miniskirt:1.1),
(clear heels:1.2), transparent footwear, high heels, (shoe dangle:1.2), crystal hair ornament, hairpin,
sitting, stool, knee up, head rest, hand on own chin, from below, full body,
simple background, grey background,
```

`shoe dangle` = 발끝에 걸린 구두가 벗겨지려는 모습 (유리구두를 잃어버리는 장면).

## 5. 네거티브 — 모든 Vol.에 그대로

```
lowres, worst quality, bad quality, low quality, displeasing, very displeasing, jpeg artifacts, blurry, aliasing,
text, logo, watermark, signature, artist name, username,
bad anatomy, bad hands, extra digits, fewer digits, extra arms, extra legs, missing fingers, bad feet, mutation, deformed,
multiple views, chibi, 3d, realistic, photo, sketch, unfinished,
(blue hair:1.2), (brown hair:1.2), (black hair:1.2), blonde hair, multicolored hair, gradient hair, streaked hair,
blue eyes, glowing eyes, bright pupils,
(dress:1.2), gown, wedding dress, frills, maid,
2girls, multiple girls, male, cleavage, nsfw,
```

- Vol. III은 슬립 원피스를 입으니 네거티브에서 `(dress:1.2), gown`을 **지운다**.
- 원래 NovelAI 네거티브의 액세서리 금지(목걸이·귀걸이 등)는 이번 옷과 부딪혀서 뺐다.

## 6. 뽑은 뒤

1. 마음에 드는 걸 Claude에게 보낸다 → `illust` 스킬 점검표로 점검
2. 힉스필드로 배경 제거 · 업스케일 (소량 크레딧)
3. 앱 화면(큰 틀 + 흑백 장식)에 넣어 확인
