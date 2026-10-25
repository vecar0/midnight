# illust 기록

확정된 그림마다 아래 형식으로 덧붙인다.

<!--
## <키> — YYYY-MM-DD
- 모델:
- 레퍼런스: (그림체용 / 캐릭터용)
- 시드:
- 프롬프트:
- 고친 내용:
-->

## (시안) Vol. IV 자정 — 2026-10-24
- 모델: gpt_image_2_5 / flare / low / 1k / 2:3 (0.25크레딧)
- 레퍼런스: 포즈 = 사용자 제공 화보 사진(로고 잘라냄) / 얼굴 = `p1` 상반신 / 그림체 = 사용자 제공 일러스트
- 프롬프트 요지: 패션 화보 포즈(의자에 앉아 무릎 세우고 턱 괴기, 정면 응시, 살짝 아래 시점), 얼굴·머리 원본 유지, 은빛 블루 오프숄더 드레스·장갑·티아라·유리구두, 스튜디오 조명, 회색 배경, 글자·안경 없음
- 결과: 얼굴·머리·포즈 잘 따라옴. 의자가 금색(흑백 원칙과 충돌), 선이 매끈해 그림체 약함, 붉은 눈가 약함

## (시안) Vol. I 서곡 — 2026-10-24
- 모델: nano_banana_pro / 1k / 2:3 (2크레딧)
- 레퍼런스: 그림체 = 사용자 제공 일러스트 1장 / 얼굴 = `p1` 상반신 (실사 포즈 사진은 뺌)
- 프롬프트 요지: 첫 이미지 그림체 그대로(가는 손그림 선, 잔머리, 강한 명암, 매트 피부+분홍 혈색, 에어브러시 금지), 둘째 이미지는 얼굴만. 힙한 현대식 신데렐라 스트리트 화보, 철제 스툴에 무릎 세우고 턱 괴기·형광펜, 크롭 회색 후드 집업+흰 탱크톱+검은 와이드 트랙 팬츠+청키 스니커즈+헤드폰+은테 안경
- 결과: 컨셉·얼굴·그림체 방향은 맞음. 다리 구조가 깨짐(두 발이 의자 위인데 바지 한쪽이 바닥까지), 형광펜이 양손에 하나씩 중복

## (시안) Vol. I 서곡 2차 — 2026-10-24
- 모델: nano_banana_pro 요청 (작업 결과에는 nano_banana_2로 표시됨) / 1k / 2:3 (2크레딧)
- 레퍼런스: 사용자 제공 NovelAI 결과물 2장(그림체만), `p1` 뺌, 얼굴은 글로 설명
- 프롬프트: SKILL.md "Minuit 그림체 규칙"을 문장으로 + 포즈를 좌우 다리까지 구체적으로
- 결과: 포즈·다리 구조·소품 개수는 맞음. 그림체는 여전히 레퍼런스와 다름(평평한 채색, 머리 하이라이트·역광 대비 없음)

## Céleste 원화 (새 컨셉 Bleu Minuit) — 2026-10-24
- 원본: PixAI(사용자 생성, LoRA 사용) 768×1280, 앞머리 없음 → `work/celeste/base_nobangs_768.png`
- PixAI 프롬프트: 태그형. facing viewer, straight-on, crossed arms on horizontal ledge, horizontal black railing, both eyes visible,
  half-closed eyes, blue eyes, mole under eye, black hair + blue inner hair, turtleneck, black see-through shirt, black bustier,
  layered silver chains, large silver star pendant, black corset belt, patent leather, liquid metal buckle, single crescent moon earring,
  gradient black→blue nails, plain white background (네거티브 칸 없음 → 넣는 태그만으로 밀어줌)
- 앞머리: PixAI 인페인트 실패 → Higgsfield gpt_image_2_5 (medium, 1k, 0.5크레딧/장) 편집 "add straight blunt bangs… keep everything else identical"
  2장 중 A(job 545d292a) 채택. 전체를 다시 그리는 편집이라 원본과 픽셀 정렬은 안 맞음(768×1296)
- 손등 금 편집(job 9358abf6): 반영 안 됨 → 코드 레이어로 그리기로
- 업스케일: bytedance 4k (2크레딧) → 2435×4096, 위에 흰 여백 18% 덧대 2435×4833 → `work/celeste/base_bangs_4k.png`
- **변경(같은 날)**: 사용자 선택으로 앞머리 없는 원본을 최종 원화로. PixAI 원본(media 8a2c60bc)을 bytedance 4k 업스케일(2크레딧)
  → 2457×4096, 위에 흰 여백 18% → `work/celeste/base_4k.png`. 앞머리 편집본(base_bangs_4k)은 삭제

## Céleste 부품·오브젝트 — 2026-10-24 (gpt_image_2_5)
- 눈 감은 얼굴: 얼굴 크롭(4K 760,1120–1960,2400) 편집, medium 1k ×2 (1크레딧) → 1번 채택 `work/celeste/eyes_closed_edit.png`
- 입 모양: 같은 크롭 편집 medium 1k — 미소 "very faint soft satisfied closed-lip smile", 찡그림 "lips pressed into small flat frown + inner brows together"
  → `mouth_smile_edit.png`, `face_frown_edit.png` (SIFT 정렬 후 패치로 잘라 씀, tools/celeste_parts.py)
- 오브젝트 시트: medium 4k 3:2 background transparent (1.25크레딧) — 달·석고 천사상·석고 손 두 개·백합·대리석 체스 킹/나이트·고딕 창.
  "real photographs converted to grayscale, soft studio light upper left, fine film grain, matte" → 한 번에 성공. `objects_sheet.png`
- 뻗는 손: 1차(손바닥 방향)는 손바닥인데 손톱이 보이는 해부 오류 + 손톱 과하게 김 → 2차 "BACK of the hand faces the viewer…
  medium-length almond nails (not claws)" + 원화 레퍼런스, medium 2k transparent → 성공(왼손으로 나와 좌우 반전). `hand_reach.png`
- 밑그림(리깅용): 원화(4K→1229×2048) 편집 medium 2k ×2 (2크레딧) "Remove ONLY the long side locks in front of shoulders… and both
  earrings. Paint what was hidden underneath…" → 2번 채택(어깨 뒤 파란 머리 유지) `work/celeste/underlayer_edit.png`.
  편집본은 몸통이 원화보다 약간 크고 아래로 내려가 다시 그려짐 → 얼굴 위(y<1075)는 원화, 아래는 편집본으로 합침 (tools/celeste_layers.py)
- 오브젝트 추가 24개 (2026-10-25): medium 4k 3:2 transparent, 4×2 시트 3장 (3.75크레딧). 프롬프트는 1차 시트와 같은 문장틀
  ("A sheet of eight separate black-and-white photographic cut-out objects … loose 4 by 2 grid … real photographs converted to grayscale…")
  → 천체·시간 / 조각·석고 / 꽃·새·사물. 전부 한 번에 성공, 낱개 분리는 tools/celeste_objects.py SHEETS 표

## 2026-10-25 셀레스트 헤일로 (work/celeste/parts/halo_back.webp, halo_front.webp)
- 모델: gpt_image_2_5, quality low, 21:9, background transparent (0.25크레딧, 한 번에 확정)
- 레퍼런스: char.webp 목걸이·별 펜던트·달 귀걸이 크롭 1장 (금속 표현만)
- 프롬프트: "Anime illustration asset: a single elegant halo ring, seen from slightly above in perspective so it forms a wide flat ellipse (about four times wider than tall), centered, filling the width, on a fully transparent background. Use the reference image only for the metal rendering style: polished chrome silver drawn with thin black ink outlines, hard cel-shaded white highlight bands and dark grey reflections, no soft glow. The ring is slender and refined, like fine jewelry: a thin double band with a delicate engraved line between the bands, small eight-pointed silver stars set along it at irregular intervals, and one slightly larger eight-pointed star at the front center with a small deep cobalt blue (#1E22D6) gemstone in its middle as the only color. A few very fine silver threads of light crossing the ring. Luxurious, minimal, gothic, not cluttered. No text, no glow particles, no head or person, no background, no ornate filler swirls."
- 후처리: 고리 중심 (671.5, 245), 가로 반지름 637.5. 곡선 y = 245 − 28·(1−u²) 위/아래로 뒤·앞 반 분리
