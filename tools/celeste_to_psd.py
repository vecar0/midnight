#!/usr/bin/env python3
"""리깅 레이어 → 프로크리에이트에서 손볼 PSD.

  python3 tools/celeste_to_psd.py
입력  work/celeste/rig/*.webp, rig.json, work/celeste/parts/char.webp
출력  work/celeste/procreate/celeste_hair.psd
"""
import json
from pathlib import Path
import numpy as np
from PIL import Image
from psd_tools import PSDImage
from psd_tools.api.layers import PixelLayer

ROOT = Path(__file__).resolve().parent.parent
RIG = ROOT / 'work/celeste/rig'
meta = json.loads((RIG / 'rig.json').read_text())
W, H = meta['size']
Y0, Y1 = 400, 2140                      # 머리 위 여백과 난간 아래는 잘라서 가볍게


def full(name):
    L = meta['layers'][name]
    c = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    c.alpha_composite(Image.open(RIG / f'{name}.webp').convert('RGBA'), tuple(L['xy']))
    return c.crop((0, Y0, W, Y1))


def merge(names):
    c = Image.new('RGBA', (W, Y1 - Y0), (0, 0, 0, 0))
    for n in names:
        if n in meta['layers']:
            c.alpha_composite(full(n))
    return c


psd = PSDImage.new('RGBA', (W, Y1 - Y0))
layers = [   # 아래 → 위
    ('BODY (do not edit)', merge(['under', 'neck', 'topwear', 'rest', 'handwear-r'])),
    ('HAIR BACK', full('back_hair')),
    ('FACE (do not edit)', merge(['restHead', 'ears-l', 'ears-r', 'face', 'mouth', 'nose', 'eyebrow-r', 'eyebrow-l',
                               'eyelash-r', 'eyewhite-r', 'eyewhite-l', 'irides-r', 'irides-l', 'eyelash-l'])),
    ('EARRINGS (do not edit)', merge(['earMoon', 'earStar'])),
    ('HAIR SIDE R', Image.new('RGBA', (W, Y1 - Y0), (0, 0, 0, 0))),
    ('HAIR SIDE L', Image.new('RGBA', (W, Y1 - Y0), (0, 0, 0, 0))),
    ('HAIR FRONT', full('front_hair')),
]
src = Image.open(ROOT / 'work/celeste/parts/char.webp').convert('RGBA').crop((0, Y0, W, Y1))
for name, im in layers:
    psd.append(PixelLayer.frompil(im, psd, name))
ref = PixelLayer.frompil(src, psd, 'ORIGINAL (reference)')
ref.visible = False
psd.append(ref)
out = ROOT / 'work/celeste/procreate/celeste_hair.psd'
psd.save(out)
chk = PSDImage.open(out)
print(out, round(out.stat().st_size / 1e6, 1), 'MB', [l.name for l in chk])
chk.composite().convert('RGB').resize((W // 4, (Y1 - Y0) // 4)).save('/tmp/claude-0/-home-user-midnight/5b206ca0-e98c-5fce-a967-6674d5a729de/scratchpad/psd_check.png')
