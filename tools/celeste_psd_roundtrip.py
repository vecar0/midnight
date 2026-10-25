#!/usr/bin/env python3
"""리깅 레이어를 프로크리에이트에서 손볼 수 있게 PSD로 내보내고, 손본 PSD를 다시 들여온다.

  python3 tools/celeste_psd_roundtrip.py export        → work/celeste/procreate/celeste_rig_edit.psd
  python3 tools/celeste_psd_roundtrip.py import 파일.psd → work/celeste/rig_overrides/*.png 저장 후 rig/ 에 반영
  python3 tools/celeste_psd_roundtrip.py apply          → rig_overrides/ 를 rig/ 에 다시 반영 (celeste_st_layers.py 가 끝에 부른다)

PSD 레이어 이름 = 리깅 레이어 이름. 이름이 같은 레이어만 들여오고 나머지(REFERENCE 등)는 무시한다.
캔버스는 원화 좌표에서 Y0~Y1 만 잘라 둔 크기 — 크기·위치를 바꾸지 않아야 좌표가 맞는다.
"""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
RIG = ROOT / 'work/celeste/rig'
OVR = ROOT / 'work/celeste/rig_overrides'
OUT = ROOT / 'work/celeste/procreate/celeste_rig_edit.psd'
Y0, Y1 = 400, 2140
EDITABLE = ['underHair', 'strand00', 'strand01', 'strand02', 'earMoon', 'earStar', 'front_hair']


def meta():
    return json.loads((RIG / 'rig.json').read_text())


def full(m, name):
    W, H = m['size']
    c = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    c.alpha_composite(Image.open(RIG / f'{name}.webp').convert('RGBA'), tuple(m['layers'][name]['xy']))
    return c.crop((0, Y0, W, Y1))


def export():
    from psd_tools import PSDImage
    from psd_tools.api.layers import PixelLayer
    m = meta(); W, _ = m['size']
    psd = PSDImage.new('RGBA', (W, Y1 - Y0))
    ref = Image.new('RGBA', (W, Y1 - Y0), (0, 0, 0, 0))
    for n in m['order']:
        if n not in EDITABLE:
            ref.alpha_composite(full(m, n))
    psd.append(PixelLayer.frompil(ref, psd, 'REFERENCE (ignored)'))
    for n in m['order']:                       # 리깅과 같은 앞뒤 순서
        if n in EDITABLE:
            psd.append(PixelLayer.frompil(full(m, n), psd, n))
    OUT.parent.mkdir(exist_ok=True)
    psd.save(OUT)
    print(OUT, [l.name for l in PSDImage.open(OUT)])


def do_import(path):
    from psd_tools import PSDImage
    m = meta(); W, _ = m['size']
    psd = PSDImage.open(path)
    if psd.width != W or psd.height != Y1 - Y0:
        sys.exit(f'캔버스 크기가 다릅니다: {psd.width}×{psd.height} (기대 {W}×{Y1 - Y0})')
    OVR.mkdir(exist_ok=True)
    got = []
    for l in psd.descendants():
        name = l.name.strip()
        if name not in EDITABLE or l.is_group():
            continue
        c = Image.new('RGBA', (W, Y1 - Y0), (0, 0, 0, 0))
        im = l.topil()
        if im is not None:
            c.alpha_composite(im.convert('RGBA'), (l.left, l.top))
        c.save(OVR / f'{name}.png'); got.append(name)
    print('들여온 레이어:', got, ' 없는 것:', [n for n in EDITABLE if n not in got])
    apply()


def import_pdf(path, name):
    """프로크리에이트에서 레이어 하나를 PDF로 내보낸 파일 → 그 레이어 덮어쓰기용 PNG.
    PDF 쪽(page)은 캔버스 전체에 해당하므로, 안에 든 그림을 쪽 안의 자리 비율대로 캔버스에 놓는다."""
    import fitz                                    # pip install pymupdf
    m = meta(); W, _ = m['size']; CH = Y1 - Y0
    doc = fitz.open(path); page = doc[0]; pw, ph = page.rect.width, page.rect.height
    c = Image.new('RGBA', (W, CH), (0, 0, 0, 0))
    for info in page.get_images(full=True):
        xref, smask = info[0], info[1]
        pix = fitz.Pixmap(doc, xref)
        if smask:
            pix = fitz.Pixmap(pix, fitz.Pixmap(doc, smask))
        if pix.n - pix.alpha > 3:
            pix = fitz.Pixmap(fitz.csRGB, pix)
        im = Image.frombytes('RGBA' if pix.alpha else 'RGB', (pix.width, pix.height), pix.samples).convert('RGBA')
        for r in page.get_image_rects(xref):
            x0 = round(r.x0 / pw * W); y0 = round(r.y0 / ph * CH)
            w = round(r.width / pw * W); h = round(r.height / ph * CH)
            c.alpha_composite(im.resize((w, h), Image.LANCZOS) if (w, h) != im.size else im, (x0, y0))
    a = np.array(c)
    if a[..., 3].min() == 255:
        # 프로크리에이트 PDF는 레이어를 흰 바탕에 합친 JPEG로 저장한다 → 지운 자리를 찾는 틀로만 쓰고 색은 지금 레이어 것을 쓴다
        import cv2
        rgb = a[..., :3].astype(np.int16)
        light = ((rgb.min(axis=2) > 225) & (rgb.max(axis=2) - rgb.min(axis=2) < 30)).astype(np.uint8)
        n, lab, st, _ = cv2.connectedComponentsWithStats(light)
        border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
        bg = np.isin(lab, [i for i in range(1, n) if i in border or st[i, 4] > 600])   # 바탕 + 지워서 생긴 큰 빈자리
        keep = cv2.GaussianBlur(cv2.erode((~bg).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(np.float32), (0, 0), .8)
        cur = full(m, name)
        cur = np.array(cur).astype(np.float32); cur[..., 3] *= keep
        c = Image.fromarray(cur.clip(0, 255).astype(np.uint8))
        print(f'  {name}: 흰 바탕 PDF → 지운 자리만 반영 (남은 {int((cur[..., 3] > 30).sum())} px)')
    OVR.mkdir(exist_ok=True)
    c.save(OVR / f'{name}.png')
    print('PDF 들여옴:', name, Path(path).name)


def apply():
    if not OVR.exists():
        return
    m = meta()
    for p in sorted(OVR.glob('*.png')):
        n = p.stem
        if n not in m['layers']:
            continue
        a = np.array(Image.open(p).convert('RGBA'))
        ys, xs = np.where(a[..., 3] > 2)
        if len(xs) == 0:
            continue
        x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        Image.fromarray(a[y0:y1, x0:x1]).save(RIG / f'{n}.webp', quality=92)
        L = m['layers'][n]; L['xy'] = [int(x0), int(y0 + Y0)]; L['size'] = [int(x1 - x0), int(y1 - y0)]
        print('반영:', n)
    (RIG / 'rig.json').write_text(json.dumps(m, indent=1))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'export': export()
    elif cmd == 'import': do_import(sys.argv[2])
    elif cmd == 'import-pdf':                      # import-pdf 파일.pdf 레이어이름 [파일.pdf 레이어이름 ...]
        args = sys.argv[2:]
        for p, n in zip(args[::2], args[1::2]):
            import_pdf(p, n)
        apply()
    elif cmd == 'apply': apply()
    else: sys.exit(__doc__)
