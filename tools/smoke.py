#!/usr/bin/env python3
"""빌드된 index.html 을 휴대폰 세로·가로 크기로 열어 보고 스크린샷을 남긴다.

  python3 tools/smoke.py           # .shots/ 에 png 저장, 페이지 오류가 있으면 실패

필요: pip install playwright && playwright install chromium
"""
import asyncio, sys
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / '.shots'; OUT.mkdir(exist_ok=True)
URL = (ROOT / 'index.html').as_uri()

async def main():
    bad = []
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for name, w, h in [('portrait', 390, 844), ('landscape', 844, 390)]:
            ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, has_touch=True, is_mobile=True)
            pg = await ctx.new_page(); errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto(URL); await pg.wait_for_timeout(1200)
            await pg.screenshot(path=str(OUT / f'{name}-1-ui.png'))
            await pg.tap('#go'); await pg.wait_for_timeout(3500)                       # 집중 시작 → 장면이 펼쳐진다
            await pg.screenshot(path=str(OUT / f'{name}-2-scene.png'))
            await pg.evaluate("remain=Math.round(total*0.3); endAt=Date.now()+remain*1000; paint()")
            await pg.wait_for_timeout(3000)                                           # 2번째 옷 + 모래가 흘러내린 상태
            await pg.screenshot(path=str(OUT / f'{name}-3-running.png'))
            await pg.tap('#handle'); await pg.wait_for_timeout(1500)                 # 팝업 다시 열기
            await pg.screenshot(path=str(OUT / f'{name}-4-popup.png'))
            print(name, 'OK' if not errs else errs); bad += errs
            await ctx.close()
        await b.close()
    print('스크린샷:', OUT)
    sys.exit(1 if bad else 0)

asyncio.run(main())
