# Minuit (자정까지) — 신데렐라 집중 타이머

집중한 시간만큼 캐릭터의 옷이 바뀌고, 타이머를 끝까지 채우면(자정) 무도회 드레스가 되는 웹앱.
GitHub Pages(`https://vecar0.github.io/midnight/`)에서 서비스하고, 사용자는 아이폰 사파리에서
**홈 화면에 추가**해서 앱처럼 쓴다. 답변은 한국어로.

## 구조

```
index.html            ← 빌드 결과(4.8MB, 에셋이 base64로 들어간 한 파일). 직접 고치지 말 것
sw.js                 ← 오프라인 캐시. 빌드할 때마다 CACHE 버전(midnight-vN)이 올라간다
manifest.webmanifest  ← 홈 화면 앱 이름(Minuit)·전체화면·아이콘
icon-*.png, apple-touch-icon*.png, favicon.ico  ← 시계판(11시 55분) 앱 아이콘
src/app.html          ← 실제 소스(HTML+CSS+JS). 자리표시 /*ASSETS*/ /*GEOM*/ /*SND*/ /*TICK*/
src/sound.js          ← Web Audio 소리 엔진(Snd): 종소리, 종이 부스럭(rustle), 완주 화음
assets/images/*.webp  ← 그림 51개. 파일 이름(확장자 뺀 것)이 코드의 src('키')
assets/audio/tick.mp3 ← 시계탑 초침 소리(7초 루프, 첫 똑딱이 0.05초에 오도록 잘라 둠)
data/geom.json        ← 모래시계 유리 모양·모래 부피표 (세로 P 4벌 / 가로 L 4벌)
tools/build.py        ← src + assets → index.html
tools/smoke.py        ← 세로·가로로 열어 스크린샷(.shots/) + 페이지 오류 검사
```

## 작업 순서

1. `src/app.html` (또는 `src/sound.js`, `assets/`, `data/`) 수정
2. `python3 tools/build.py` → `index.html` 생성, `sw.js` 캐시 버전 +1
   (버전을 안 올리면 이미 설치된 홈 화면 앱이 옛 파일을 계속 보여준다)
3. `python3 tools/smoke.py` 로 세로·가로 화면 확인. 스크린샷을 직접 열어 보고 판단할 것
4. 커밋 → `main` 에 푸시하면 1~2분 뒤 Pages에 반영. 사용자는 홈 화면 앱을 완전히 껐다 켜서 확인

`index.html` 만 보고 고치면 다음 빌드에서 덮어써진다. 항상 `src/` 를 고친다.

## 화면과 흐름

- 처음엔 배경 + 위쪽 **종이 팝업 UI**(아이보리 구겨진 종이 `paperIvory`).
  팝업을 위로 밀거나 "장면 펼치기" / "집중 시작" → `setScene(true)`:
  팝업은 구겨지며 옆으로 빠지고, 오브젝트와 캐릭터가 구겨진 종이 상태로 화면 옆에서 날아 들어오며 펴진다.
  위쪽 검은 종이 손잡이(`#handle`, `paperBlack`)를 탭/아래로 밀면 반대로.
- 종이 펴짐/구김은 전부 캔버스 `#tx` 에서 `drawPaper()` 가 삼각형 그물로 그림을 휘어 그린다
  (`crumple()` = 캐릭터·오브젝트, `panelPaper()` = 팝업). SVG 필터는 iOS 사파리에서 깨져서 쓰지 않는다.
- **옷 4벌**: 시간을 4등분해서 바뀐다(`applyBlend`). 바뀔 때 오른쪽에서 종이 콜라주 가림막
  (`curtainL` / `curtainP`)이 밀려 나와 가리고 그 사이 `showOutfit()` 후 다시 들어간다(`curtainSwap`).
  단계 이름: I Prélude 서곡 · II Nocturne 야상곡 · III Valse 왈츠 · IV Minuit 자정.
- **모래시계 모래**: 알갱이 약 1,400톨 격자 시뮬레이션(`simInit/simStep/simDraw`, `sandLoop`).
  목을 타이머 속도에 맞춰 한 톨씩 통과시키고, 아래는 중력+대각선 미끄러짐으로 원뿔 더미가 생긴다.
  옷마다 손에 든 모래시계 위치가 달라서 `data/geom.json` 의 `G.P[i]`, `G.L[i]` 를 옷 번호로 고른다.
- **시계탑**(`tower2`): 바늘 `hHour/hMin/hSec` 이 실제 현재 시각을 가리킨다. 중심은 `DIAL`(시계판 원을
  재서 구한 비율). 초침이 넘어가는 순간에 `tick.mp3` 의 똑딱이 겹치도록 재생 위치를 맞춘다(`Tick`).
  소리는 브라우저 규칙상 첫 터치 뒤에 시작. 기록 안의 "초침 소리" 버튼으로 끔.
- **입체감**: 기울기 센서/마우스로 배경·오브젝트·캐릭터·유리구슬이 깊이별로 다르게 움직인다(`depthLoop`).
  캐릭터 앞뒤에 3D 오브젝트(`d3*`, 배치표 `F3`)가 떠 있고, 작은 오브젝트는 `MOTION` 표대로 살랑인다.
- **과목 입력 + 기록**: `localStorage` 키 `midnight.rec`(세션 목록), `midnight.subj`, `midnight.tick`.
  기기·주소마다 따로 저장된다(서버 없음).

## 배치 손보는 곳 (요청이 가장 많은 부분)

- `LAYOUT.P / LAYOUT.L` — 종이 오브젝트 `[키, left vw, top vh, 폭 vw, 회전°]`
- `F3.P / F3.L` — 3D 오브젝트 `[키, 'b'(캐릭터 뒤)|'f'(앞), 캐릭터 상자 기준 x비율, y비율, 크기(캐릭터 높이 비율), 회전°]`
- `layout()` 안의 가로 전용 보정:
  - 캐릭터(`figL`)는 화면 높이에 맞춰 오른쪽에 붙이고 밑단을 화면 밖으로 넘긴다
  - 요술봉(`oWand`)을 캐릭터 그림 왼쪽 끝에 붙여 **팔꿈치 옆 잘린 세로 경계**를 가린다
  - 유리구두(`d3Slipper`)로 아래 종이 띠(`edgeB2`) 왼쪽 끝을 가린다
- 세로 화면 아래 빈칸: `appH()` 가 홈 화면 앱일 때 `screen` 높이로 무대를 늘린다(iOS가 innerHeight를 짧게 줌).

## 그림(assets/images) 키

| 키 | 내용 |
|---|---|
| `p1`~`p4` | 세로 캐릭터(서서 모래시계를 두 손으로 듦) 1~4단계 옷 |
| `l1`~`l4` | 가로 캐릭터(엎드려 뺨 괴고 모래시계 윗부분을 쥠) 1~4단계 옷 |
| `bgP`, `bgL` | 깨진 거울 고딕 아치 배경 |
| `tower2`, `hHour`, `hMin`, `hSec` | 바늘 없는 시계탑 + 바늘 3종 |
| `swirl`, `crystals`, `watch1`, `watch2`, `shard1`~`5`, `oEnvelope`, `oWand` | 종이 콜라주 오브젝트 |
| `d3Tiara` `d3Watch` `d3Pumpkin` `d3Gears` `d3Feather` `d3Shards` `d3Slipper` `d3Key` | 입체 오브젝트 |
| `stripH`, `stripV` | 아래·오른쪽 찢긴 종이 테두리 |
| `curtainL`, `curtainP` | 옷 바꿀 때 나오는 가림막 |
| `paperIvory`, `paperBlack` | 팝업 / 손잡이 종이 |
| `fx*` | 유리 반짝임 파티클(완주·포기 연출) |
| `gKey` `gScrew` `gShard` `gShoe` `gWatch` | 예전 버전에서 남은 파티클. 코드에서 안 쓰므로 지우면 파일이 조금 가벼워진다 |

이미지를 바꿀 땐 같은 키 이름의 webp로 덮어쓰면 된다. 캐릭터 그림을 바꾸면 모래시계 위치가
달라지므로 `data/geom.json` 해당 옷의 값(`cx`, `neck`, `floor`, `W`, `path`, `t`, `b`)도 다시 맞춰야 한다.

## 사용자 선호

- 캐릭터 **얼굴·머리 디자인은 원본(은발, 일자 앞머리, 처진 회색 눈+붉은 아이라인, 초커) 유지**. 옷은 바꿔도 됨.
- 흑·백·회색 + 투명 유리 톤의 고딕 콜라주. 너무 난잡하지 않게.
- 새 그림은 Higgsfield로 생성하되 **크레딧을 아낀다**: 꼭 필요한 것만, 여러 개는 한 장에 모아서.
- 사용자는 주로 **아이폰**에서 확인한다. 사파리/홈 화면 앱 특유의 문제(키보드 뒤 화면 높이,
  SVG 필터, 자동재생 제한)를 항상 의심할 것.
- 수정할 때는 바뀐 부분만 최소한으로. 결과는 스크린샷으로 확인한 뒤 짧게 보고.
