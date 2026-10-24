# Minuit — 자정까지

신데렐라 테마 집중 타이머. 집중한 시간만큼 옷이 바뀌고, 자정(완주)에 무도회 드레스가 된다.

- 사이트: https://vecar0.github.io/midnight/
- 휴대폰 사파리에서 열고 **공유 → 홈 화면에 추가**하면 앱처럼 전체 화면으로 쓸 수 있다
- 한 번 열면 인터넷 없이도 열린다
- 기록은 이 기기의 브라우저에만 저장된다

## 고치는 법

```
src/app.html 수정  →  python3 tools/build.py  →  python3 tools/smoke.py  →  커밋·푸시
```

자세한 구조는 [CLAUDE.md](CLAUDE.md).
