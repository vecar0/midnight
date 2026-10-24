---
name: illust
description: Higgsfield로 이 앱(Minuit)에 넣을 일러스트·캐릭터·오브젝트 그림을 만들 때 쓴다. 레퍼런스 분석 → 문장형 프롬프트 → 저해상도 시험 → AI 티 점검 → 부분 편집 → 업스케일·webp 변환 순서로, AI 특유의 느낌을 줄이고 퀄리티를 높인다. "그림 뽑아줘", "일러스트 새로", "옷 바꿔줘", "AI 티 나", "레퍼런스처럼" 같은 요청이면 이 스킬을 먼저 불러온다.
---

# illust — AI 티 덜 나는 일러스트 만들기

목표: **한 번 뽑고 끝내지 않는다.** 분석하고, 작게 시험하고, 직접 보고, 고친다.
AI 그림이 AI처럼 보이는 이유는 대부분 모델 한계가 아니라 "균일함"이다 —
선 굵기, 디테일 밀도, 광택, 대칭, 초점이 화면 전체에서 똑같다. 사람은 강약을 준다.

## 0. 시작 전에

- 크레딧을 아낀다(CLAUDE.md 사용자 선호). `balance` 로 잔액을 보고, 이번 작업에 쓸
  대략의 생성 횟수를 사용자에게 한 줄로 말한 뒤 진행한다. 큰 해상도·여러 장은 허락 받고.
- Higgsfield 도구는 지연 로딩이다. `ToolSearch` 로 필요한 것만 불러온다
  (`generate_image`, `models_explore`, `media_upload`, `media_confirm`, `jobs_wait`,
  `upscale_image`, `remove_background`, `manage_reference_elements`).
- 사용자가 준 레퍼런스 파일은 `media_upload` → curl PUT → `media_confirm` 으로 올린다.
  앱의 기존 그림(`assets/images/*.webp`)도 같은 방법으로 캐릭터 레퍼런스로 쓸 수 있다.

## 1. 레퍼런스 분석 (생성 전, 크레딧 0)

레퍼런스 이미지를 `Read` 로 직접 열어 보고 아래 표를 채워서 사용자에게 보여 준다.
"예쁘다" 같은 말 대신 **눈에 보이는 사실**로 쓴다.

| 항목 | 적을 내용 (예) |
|---|---|
| 선 | 굵기 변화 있음/없음, 외곽선이 안쪽 선보다 굵은지, 끝이 날카로운지, 손떨림·끊김 |
| 채색 | 셀 그림자 단계 수(2단/3단), 그러데이션 쓰는 곳은 어디뿐인지, 붓 질감 |
| 명암 | 광원 방향, 역광·림라이트 여부, 가장 어두운 곳이 순흑인지 |
| 색 | 주요 색 3~5개, 채도 범위, 포인트 색이 어디에 몇 군데 |
| 디테일 밀도 | 어디가 빽빽하고(얼굴·손) 어디가 비었는지(옷 넓은 면·배경) |
| 구도 | 카메라 높이, 화각, 자르는 위치, 시선 흐름 |
| 질감 | 종이 결, 노이즈, 인쇄 느낌 |

**그림체 레퍼런스는 주 1장(많아야 비슷한 그림체 2장)으로 한다.** 그림체가 다른 이미지를
여러 장 넣으면 모델이 평균을 내서 흐리멍덩한 "AI 평균 그림"이 되고, 그게 오히려 AI 티다.
다른 그림에서 빌리고 싶은 요소(예: 조명만)는 이미지로 넣지 말고 1번 표처럼 글로 적어 넣는다.

레퍼런스가 다른 작가의 그림이면 **그 그림 자체를 다시 그리지 않는다.** 이 앱은 Pages에
공개돼 있으므로 그림체(선·채색·조명)만 빌리고, 구도·포즈·의상·캐릭터는 우리 것으로 정한다.

## 2. 요청 체크리스트

생성 전에 사용자와 맞춘다. 빠진 게 있으면 기본값을 제안하고 한 번에 묻는다.

- **고정(캐릭터 원본 유지)**: 은발, 일자 앞머리, 처진 회색 눈 + 붉은 아이라인, 초커.
  `assets/images/p1.webp` 를 캐릭터 레퍼런스로 함께 넣는다.
- 구도·포즈: 세로(`p*`, 서서 모래시계를 두 손으로 듦) / 가로(`l*`, 엎드려 뺨 괴고 모래시계 윗부분을 쥠)
- 옷·소품 세부
- 앱 톤: 흑·백·회색 + 투명 유리, 고딕 콜라주. 포인트 색은 붉은 아이라인 정도로 절제
- 용도와 크기: 배경 투명 필요 여부, 최종 해상도, 들어갈 키 이름

## 3. 프롬프트 작성 규칙

- **문장으로 쓴다.** NovelAI식 `1.3::tag::` 가중치, `artist:` 태그, 긴 네거티브 목록은 쓰지 않는다
  (힉스필드 모델은 이해하지 못하고, 단어가 오히려 그림에 섞인다).
- 순서: 매체/그림체 → 인물·외모 → 포즈·구도 → 의상 세부 → 조명 → 배경 → 금지 몇 개.
- 1단계 분석표를 그대로 문장으로 옮긴다. "high quality, masterpiece" 같은 빈 수식어는 넣지 않는다.
- **AI 티를 줄이는 문구** (상황에 맞게 골라 쓴다):
  - `varied line weight, thicker outer contour, tapered line ends, slightly rough hand-inked lines`
  - `flat cel shading with two tones, hard shadow edges, gradients only on hair and glass`
  - `matte skin, no airbrushed smoothness, minimal bloom`
  - `detail concentrated on the face and hands, simplified large fabric areas, empty negative space`
  - `slight asymmetry in pose and hair, natural imperfection`
  - `limited palette of black, white, greys, one small accent`
- 금지는 문장 끝에 3~5개만: `no text, no extra fingers, no glowing particles everywhere, no ornate filler patterns`
- 레퍼런스는 역할을 나눠서 넣는다: 그림체용 1장(비슷한 그림체면 2장까지) + 캐릭터 외모용 1장.
  프롬프트에 "first image: style only, second image: character face and hair"처럼 역할을 적는다.

모델은 `models_explore(action:'recommend')` 로 고른다. 레퍼런스 여러 장을 받는 모델
(Nano Banana Pro, Seedream, GPT Image 계열)을 우선한다. 고른 이유를 한 줄로 남긴다.

## 4. 저해상도 시험

- 가장 낮은 해상도·1~2장으로 방향만 본다. 여러 개가 필요하면 **한 장에 모아서** 뽑는다
  (예: 오브젝트 4개를 2×2로).
- 방향이 틀리면 프롬프트를 고쳐서 다시 시험한다. 이 단계에서 고해상도로 가지 않는다.

## 5. AI 티 점검 (매 결과마다, 직접 보고)

결과 이미지를 내려받아 `Read` 로 열고, 필요하면 얼굴·손을 잘라서 확대해서 본다
(`python3 -c` + PIL 로 crop). 아래 항목마다 ✅/❌ 를 매기고 ❌ 는 위치를 적는다.

**그림체**
- [ ] 피부·머리가 플라스틱처럼 매끈하거나 광택이 과하지 않은가
- [ ] 선 굵기가 일정해서 기계적이지 않은가 (외곽선 > 안쪽 선이어야 자연스러움)
- [ ] 화면 전체가 똑같이 선명하고 디테일이 고르게 빽빽하지 않은가 (강약이 있어야 함)
- [ ] 빛 번짐·반짝이 파티클·안개가 의미 없이 많지 않은가
- [ ] 그러데이션이 모든 면에 깔려 있지 않은가

**형태**
- [ ] 손가락 수·관절, 모래시계를 쥔 손의 접촉이 맞는가
- [ ] 눈 좌우, 아이라인, 초커가 원본과 같은가 (`p1` 과 나란히 비교)
- [ ] 머리카락 끝이 녹아내리거나 배경과 섞이지 않는가
- [ ] 장식 무늬가 의미 없는 꼬불이로 뭉개지지 않았는가 (레이스·자수·문양)
- [ ] 좌우 대칭이 지나치게 완벽하지 않은가, 액세서리 좌우가 서로 안 맞지 않는가
- [ ] 글자처럼 보이는 낙서가 없는가

**앱 적합성**
- [ ] 흑·백·회색 + 유리 톤에 맞는가, 기존 배경(`bgP`/`bgL`)과 같이 놓았을 때 튀지 않는가
- [ ] 세로/가로 원래 그림과 포즈·모래시계 위치가 비슷한가 (다르면 6번 geom 작업이 생김)

점검표와 결과를 사용자에게 보여 주고, 어느 쪽으로 고칠지 짧게 제안한다.

## 6. 고치기

- **전체를 다시 뽑지 않는다.** 문제가 한두 군데면 편집(레퍼런스로 결과 이미지 + "keep everything,
  only fix the left hand")으로 그 부분만 고친다.
- 그림체 전체가 어긋났을 때만 프롬프트를 고쳐 다시 생성한다.
- 같은 문제가 두 번 반복되면 프롬프트 문구가 아니라 레퍼런스 구성을 바꾼다.
- 보통 2~3번이면 끝난다. 그 이상 걸리면 멈추고 사용자에게 방향을 묻는다.

## 7. 마무리와 앱에 넣기

1. 확정본만 `upscale_image`. 캐릭터·오브젝트는 `remove_background`.
2. 원본은 scratchpad 에 받아 두고, webp 로 변환해 `assets/images/<키>.webp` 로 덮어쓴다
   (`python3 -c "from PIL import Image; Image.open(src).save(dst,'WEBP',quality=88,method=6)"`).
   기존 파일과 비슷한 해상도·용량으로 맞춘다 — `index.html` 에 base64로 들어가므로 무거워진다.
3. 캐릭터(`p*`, `l*`)를 바꿨으면 `data/geom.json` 해당 옷의 모래시계 값(`cx`, `neck`, `floor`, `W`,
   `path`, `t`, `b`)을 새 그림에 맞춰 다시 잰다.
4. `python3 tools/build.py` → `python3 tools/smoke.py` → `.shots/` 스크린샷을 직접 열어 확인.
5. 사용자에게 전/후를 짧게 보고하고, 쓴 크레딧과 남은 잔액을 한 줄로 알린다.


## Minuit 그림체 규칙 (사용자 레퍼런스 = NovelAI 결과물 기준)

원래 조합: sushispin(가장 강함), kithera, yd (orange maru), channel (caststation), modare, ratatatat74, m m pb
+ jaggy lines, thick outlines, cel shading, detailed shadows, glossy skin, backlighting, rim light, high contrast, game cg.
(웹 검색으로 확인된 건 yd = 한국 작가·Orange Maru 서클 대표, channel = 한국 일러스트레이터·애니메이터 정도. 단부루는 접속 차단)

눈에 보이는 특징:
- 흑·백·쿨그레이 위주, 따뜻한 색은 피부의 분홍뿐
- 짙고 살짝 거친 잉크 선, 외곽선 굵고 안쪽 선 가늘다, 머리카락은 가는 선 수십 가닥 + 잔머리
- 머리에 굵은 흰 하이라이트 띠, 그 아래 깊은 어둠 (윤기)
- 반쯤 감은 처진 눈, 굵게 뻗은 윗속눈썹, 눈 아래 붉은 화장
- 도자기 피부에 광택 점, 볼·코끝·귀에 진한 홍조, 광택 있는 산호색 입술
- 각진 셀 그림자 + 머리카락 그림자가 얼굴·목에 떨어짐, 검은 옷은 반짝이는 하이라이트
- 강한 역광·윤곽 빛, 뿌연 밝은 배경

**주의: 힉스필드 모델(Nano Banana Pro, GPT Image)로는 이 그림체가 재현되지 않았다**(2026-10-24, 3회 시도).
설명·레퍼런스 2장을 넣어도 평평한 웹툰 채색으로 나온다. 캐릭터는 NovelAI에서 뽑고,
힉스필드는 배경 제거·업스케일·부분 수정에만 쓰는 것을 기본으로 한다.

## 쓴 프롬프트 남기기

확정된 그림마다 모델·프롬프트·레퍼런스·시드를 `.claude/skills/illust/log.md` 에 덧붙인다.
다음에 같은 그림체로 다른 옷을 뽑을 때 그대로 재사용한다.
