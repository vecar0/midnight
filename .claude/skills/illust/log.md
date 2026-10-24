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
