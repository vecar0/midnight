#!/usr/bin/env python3
"""Bleu Minuit 배포: work/celeste/ → vecar0/Celeste 저장소(기본 /home/user/celeste)에 단독 사이트로 복사.

  python3 tools/celeste_deploy.py [대상 폴더]

경로를 배포용(./rig/, ./parts/)으로 바꾸고, 오프라인용 sw.js 를 새 캐시 버전으로 만든다.
그다음 대상 저장소에서 커밋 → main, gh-pages 에 푸시하면 Pages에 반영된다.
"""
import json, os, re, shutil, sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / 'work/celeste'
DST = Path(sys.argv[1] if len(sys.argv) > 1 else '/home/user/celeste')

(DST / 'rig').mkdir(parents=True, exist_ok=True); (DST / 'parts').mkdir(exist_ok=True)
m = json.loads((SRC / 'rig/rig.json').read_text())
files = []
for n in m['order']:
    shutil.copy(SRC / f'rig/{n}.webp', DST / f'rig/{n}.webp'); files.append(f'rig/{n}.webp')
for f in ['rig.js', 'rig.json']:
    shutil.copy(SRC / f'rig/{f}', DST / f'rig/{f}'); files.append(f'rig/{f}')
parts = ['parts.json', 'mask.webp', 'eyes_closed.webp', 'mouth_smile.webp', 'face_frown.webp'] + \
        sorted(f for f in os.listdir(SRC / 'parts') if f.startswith(('obj_', 'halo_')))
for f in parts:
    shutil.copy(SRC / f'parts/{f}', DST / f'parts/{f}'); files.append(f'parts/{f}')

s = (SRC / 'app/index.html').read_text()
for a, b in [('<script src="../rig/rig.js"></script>', '<script src="./rig/rig.js"></script>'),
             ("const PARTS = '../parts/';", "const PARTS = './parts/';"), ("{base:'../rig/',", "{base:'./rig/',")]:
    assert s.count(a) == 1, a
    s = s.replace(a, b)
s = s.replace('<title>Bleu Minuit</title>', '<title>Bleu Minuit</title>\n<link rel="manifest" href="manifest.webmanifest">\n'
              '<link rel="apple-touch-icon" href="apple-touch-icon.png">\n<link rel="icon" href="icon-192.png">\n'
              '<meta name="apple-mobile-web-app-title" content="Bleu Minuit">\n<meta name="mobile-web-app-capable" content="yes">')
(DST / 'index.html').write_text(s)
for f in ['icon-192.png', 'icon-512.png', 'apple-touch-icon.png']:                 # 앱 아이콘(work/celeste/app/icons)
    shutil.copy(SRC / f'app/icons/{f}', DST / f)
# 홈 화면 앱 설정 — 원래 Minuit 앱과 같게 fullscreen (standalone 이면 iOS가 상태 표시줄만큼 화면을 짧게 줘서 아래가 빈다)
(DST / 'manifest.webmanifest').write_text(json.dumps({
    "name": "Bleu Minuit", "short_name": "Bleu Minuit", "id": "./", "start_url": "./", "scope": "./",
    "display": "fullscreen", "display_override": ["fullscreen", "standalone"], "orientation": "any",
    "background_color": "#e9e8e3", "theme_color": "#e9e8e3",
    "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
              {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
              {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}, ensure_ascii=False, indent=1))
files += ['./', 'index.html', 'manifest.webmanifest', 'icon-192.png', 'icon-512.png', 'apple-touch-icon.png']

# 캐시 버전 +1 (안 올리면 이미 설치된 홈 화면 앱이 옛 그림을 계속 쓴다)
old = (DST / 'sw.js').read_text() if (DST / 'sw.js').exists() else ''
v = int(re.search(r"bleu-minuit-v(\d+)", old).group(1)) + 1 if 'bleu-minuit-v' in old else 1
(DST / 'sw.js').write_text(f"""// 오프라인 캐시. 배포할 때마다 버전이 오른다(tools/celeste_deploy.py)
const CACHE = 'bleu-minuit-v{v}';
const FILES = {json.dumps(files, indent=1)};
self.addEventListener('install', e=>{{ e.waitUntil(caches.open(CACHE).then(c=>c.addAll(FILES)).then(()=>self.skipWaiting())); }});
self.addEventListener('activate', e=>{{ e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k !== CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())); }});
self.addEventListener('fetch', e=>{{
  const r = e.request; if(r.method !== 'GET') return;
  // 페이지는 인터넷이 되면 새로 받고(바로 반영), 안 되면 저장본. 그림·코드는 저장본 먼저
  if(r.mode === 'navigate'){{ e.respondWith(fetch(r).then(res=>{{ const c = res.clone(); caches.open(CACHE).then(k=>k.put('index.html', c)); return res; }}).catch(()=>caches.match('index.html'))); return; }}
  e.respondWith(caches.match(r, {{ignoreSearch:true}}).then(hit=>hit || fetch(r).then(res=>{{ if(res.ok && new URL(r.url).origin === location.origin){{ const c = res.clone(); caches.open(CACHE).then(k=>k.put(r, c)); }} return res; }})));
}});
""")
print('deployed', len(files), 'files, cache v' + str(v), '→', DST)
