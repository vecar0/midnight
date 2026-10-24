# PixAI 프롬프트 — MIDNIGHT v5

그릴 것: **캐릭터 5장(단계 0~4) + 배경 2장(세로·가로).**
기준은 `design/plan.md`의 2장(캐릭터)과 4-1(아트 디렉션)입니다.

## 0. 설정

| 항목 | 값 |
|---|---|
| 모델 | Tsubaki.3 추천 (자연어, 2048까지, 자연어 편집 가능). 레퍼런스 그림을 만든 모델을 알면 그 모델로 |
| 캐릭터 크기 | **세로 2:3, 최대 해상도** (예: 1344×2016) |
| 배경 크기 | 세로 9:16 (예: 1152×2048), 가로 16:9 (예: 2048×1152) |
| 레퍼런스 | 단계 0: `design/ref/outfit_ref.jpg`를 이미지 참조로 넣고, 강도는 중간 정도(옷과 그림체만 따라오고 구도는 따라오지 않게) |
| 시드 | 단계 0에서 고른 그림의 시드를 적어 둠 |

**순서가 중요해요.** 단계 0을 여러 장 뽑아서 하나 고르기 → 그 그림을 **편집**해서 조각을 하나씩 더하기(0→1→2→3→4). 그래야 5장의 얼굴·포즈가 똑같아서 갈아입는 연출이 자연스럽습니다.
편집 기능이 마음에 안 들면: 고른 단계 0 그림을 레퍼런스로 넣고 시드를 고정한 다음, 아래 "새로 생성용" 문단을 덧붙여 생성하세요.

---

## 1. 단계 0 — PRELUDE (처음 생성)

공통 문단 4개를 순서대로 이어 붙입니다.

### 그림체

```
A semi-realistic anime fashion illustration in a near-monochrome palette of black, white and soft cool greys. Fine, thin dark line art with delicate hair strands. Soft diffused studio light from the front-left with gentle shadows and a faint rim light. Her long hair is very glossy with bright highlight bands. Pale porcelain skin, soft pink blush on the cheeks and under the eyes, soft pink lips. Fabrics are rendered with realism: sheer black mesh shows the skin faintly through it, patent leather has sharp white reflections, and silver metal is bright and liquid-looking. Clean, elegant, high-fashion magazine look, highly detailed, crisp focus.
```

### 인물

```
She is a cool, aloof young woman in her early twenties, a fashion model and university student. She has long, straight, glossy black hair falling to below her waist, heavy straight-cut bangs covering her eyebrows, and a few thin side locks framing her face. Her eyes are half-lidded and languid, pale grey, with long dark lashes and a faint pink tint around the eyes. Her expression is cold and unbothered, lips closed, looking straight at the camera with her head tilted very slightly. She is slender with a model's figure.
```

### 옷 (단계 0)

```
Her outfit: a sheer black mesh long-sleeve top with a high fitted turtleneck collar and sleeves to the wrists, a black satin bustier worn underneath, glossy black patent leather high-waisted shorts, a wide black leather corset belt cinched at the waist with sculptural molten-silver buckles, black fishnet tights, and black leather ankle boots with a block heel. Layered thin silver chain necklaces with a small silver cross pendant. No coat, no jacket, no fur.
```

### 포즈·구도 (5장 공통 — 바꾸지 마세요)

```
Full body, head to toe fully visible, with a little empty space above her head and below her feet. She stands facing the camera in a relaxed fashion pose with her weight on one leg. Her right hand rests lightly on her corset belt at the hip, and her left arm hangs naturally at her side, both arms clearly visible in front of her body and not covered by hair. Her long hair falls behind her shoulders and down her back. Eye-level camera. Plain light grey seamless studio background, no props.
```

### 피할 것 (끝에, 또는 네거티브 칸에)

```
Avoid: fur, coats, jackets, dresses, gowns, any blue or other colors in this image, text, logos, watermarks, cropped feet or head, sitting, extra fingers, fused fingers, extra limbs, hair covering the arms or hands, a 3D or photographic look, heavy outlines, extra people.
```

---

## 2. 단계 1~4 — 편집 지시

바로 이전 단계 그림을 넣고 아래 문장으로 편집합니다. 문장마다 끝에 **유지 문장**을 붙이세요.

**유지 문장(매번 끝에):**
```
Keep everything else exactly the same: the same face, hair, pose, body, lighting, line art, framing, background and all other clothing. The rest of the image stays black, white and grey; only the new item is ice blue.
```

| 단계 | 편집 문장 |
|---|---|
| 1 GLASS | `Replace her black ankle boots with elegant clear glass platform high heels tinted pale ice blue, transparent like Cinderella's glass slippers, with sharp light reflections and a faint cold blue glow on the edges.` |
| 2 GLOVES | `Add long opera gloves reaching above her elbows, made of semi-transparent pale ice-blue mesh with a glossy latex sheen at the fingertips, worn over the sleeves of her mesh top.` |
| 3 CROWN | `Add a delicate headpiece of fine silver chains strung with small ice-blue crystals, draped across the top of her head and over her bangs like a modern tiara, and a matching ice-blue crystal ear cuff on her visible ear.` |
| 4 MIDNIGHT | `Add a long, floor-length sheer trench coat of translucent pale ice-blue organza draped over her shoulders and slipping slightly off them, flowing down past her ankles and pooling softly on the floor, so her whole outfit is still visible through the sheer fabric.` |

### 편집 대신 새로 생성할 때

단계 0의 그림체·인물·옷·포즈 문단을 그대로 쓰고, 옷 문단 뒤에 해당 단계까지의 문장을 **누적해서** 붙입니다(예: 단계 3 = 1+2+3 문장). 피할 것 문단에서 `coats, jackets,` 와 `any blue or other colors in this image,` 는 빼고 `any blue except the ice-blue items,` 로 바꾸세요. 단계 4에서는 `coats`만 빼면 됩니다.

---

## 3. 배경 — 세로 1장, 가로 1장 (같은 문장, 크기만 다르게)

인물 뒤에 깔리는 그림이라 **흐릿하고 단순하게**. 인물은 넣지 않습니다.

```
An empty luxury fashion photo studio interior, no people. Floor-to-ceiling sheer grey curtains in soft vertical folds, a polished pale marble floor with soft reflections, and a tall arched mirror leaning against the wall, its surface faintly cracked with a cold ice-blue glint along the cracks. Near-monochrome palette of white, soft greys and black, with the only color being that faint ice blue. Soft diffused light, misty and dreamy atmosphere, shallow depth of field so the whole background is softly out of focus. Semi-realistic anime illustration style, clean, elegant, high-fashion magazine mood. Calm, low detail in the center of the frame.
```

```
Avoid: people, characters, text, logos, watermarks, furniture clutter, bright colors, strong patterns, harsh shadows.
```

- 세로: 아치 거울이 화면 위쪽 2/3 안에 오면 좋아요.
- 가로: 거울이 오른쪽에 오도록(가로 화면은 인물이 오른쪽). 안 맞으면 Claude가 좌우 반전·자르기로 맞춥니다.

---

## 4. 뽑은 뒤 보내 주세요

- 캐릭터 5장은 **원본 크기 그대로**(PNG 또는 고화질 JPG). 배경 제거·잘라내기·webp 변환은 Claude가 합니다.
- 단계 0을 고를 때 볼 것: 손가락 5개, 두 발이 다 보임, 머리카락이 팔을 가리지 않음, 얼굴이 정면에 가까움.
- 단계 0은 먼저 보내 주시면 점검한 뒤 1~4로 넘어가는 걸 추천해요(나머지 4장이 전부 단계 0을 기준으로 하기 때문).
