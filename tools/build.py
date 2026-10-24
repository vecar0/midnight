#!/usr/bin/env python3
"""src/app.html 에 에셋을 base64로 넣어 저장소 루트의 index.html 한 파일로 만든다.

  python3 tools/build.py          # index.html 생성 + sw.js 캐시 버전 올리기
  python3 tools/build.py --no-bump
"""
import base64, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
b64 = lambda p: base64.b64encode(p.read_bytes()).decode()

html = (ROOT / 'src/app.html').read_text(encoding='utf-8')
images = {p.stem: b64(p) for p in sorted((ROOT / 'assets/images').glob('*.webp'))}
geom = json.loads((ROOT / 'data/geom.json').read_text())
sound = (ROOT / 'src/sound.js').read_text(encoding='utf-8')
tick = b64(ROOT / 'assets/audio/tick.mp3')

for mark in ('/*ASSETS*/', '/*GEOM*/', '/*SND*/', '/*TICK*/'):
    if html.count(mark) != 1:
        sys.exit(f'src/app.html 안에 {mark} 자리표시가 정확히 1개여야 합니다 (지금 {html.count(mark)}개)')

out = (html.replace('/*ASSETS*/', json.dumps(images))
           .replace('/*GEOM*/', json.dumps(geom))
           .replace('/*SND*/', sound)
           .replace('/*TICK*/', tick))
(ROOT / 'index.html').write_text(out, encoding='utf-8')
print(f'index.html {len(out)/1e6:.2f} MB  (이미지 {len(images)}개)')

if '--no-bump' not in sys.argv:
    sw = ROOT / 'sw.js'
    t = sw.read_text(encoding='utf-8')
    t, n = re.subn(r"midnight-v(\d+)", lambda m: f"midnight-v{int(m.group(1))+1}", t, count=1)
    sw.write_text(t, encoding='utf-8')
    print('sw.js 캐시 버전:', re.search(r"midnight-v\d+", t).group(0))
