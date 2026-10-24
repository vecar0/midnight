#!/usr/bin/env python3
"""Céleste 리깅 레이어: 몸(앞머리·귀걸이 없는 밑그림) + 머리카락 다발 + 귀걸이.

  python3 tools/celeste_layers.py      (먼저 tools/celeste_parts.py 를 돌려 char.webp 가 있어야 함)

입력  work/celeste/parts/char.webp        원화 배경 제거본 (반 크기 1228×2416)
      work/celeste/underlayer_edit.png    원화에서 앞머리 다발·귀걸이를 지운 편집본
출력  work/celeste/parts/base.webp, hair_*.webp, ear_*.webp, mask.webp(덮어씀), layers.json
"""
import json
from pathlib import Path
import cv2, numpy as np
import importlib.util

ROOT = Path(__file__).resolve().parent.parent
W = ROOT / 'work/celeste'
OUT = W / 'parts'
spec = importlib.util.spec_from_file_location('cp', ROOT / 'tools/celeste_parts.py')
cp = importlib.util.module_from_spec(spec); spec.loader.exec_module(cp)

# 반 크기 좌표. 머리카락 다발: 다각형, 뿌리(흔들림 축) 좌표
HAIR = {
    'hairL': ([(270, 985), (430, 985), (470, 1100), (470, 1240), (440, 1300), (390, 1400), (375, 1500),
               (352, 1580), (320, 1730), (270, 1730), (285, 1600), (240, 1450), (215, 1300), (215, 1230),
               (250, 1100)], (360, 1000)),
    'hairO': ([(190, 1150), (228, 1200), (150, 1280), (110, 1400), (95, 1550), (70, 1720), (10, 1760),
               (10, 1600), (60, 1400), (120, 1250)], (200, 1120)),
    'hairR': ([(800, 985), (905, 985), (960, 1100), (1010, 1200), (1062, 1268), (1062, 1300), (960, 1300),
               (880, 1276), (820, 1270), (800, 1150)], (850, 1000)),
}
EARS = {'earMoon': ((402, 942, 528, 1152), (452, 962)), 'earStar': ((832, 878, 884, 1062), (852, 890))}
HEAD_Y = 1075                       # 이 위는 원화(얼굴·정수리)를 그대로 쓴다


def poly_mask(shape, pts):
    m = np.zeros(shape, np.uint8)
    cv2.fillPoly(m, [np.int32(pts)], 1)
    return m.astype(bool)


def align(src, ref):
    g1, g2 = (cv2.cvtColor(m, cv2.COLOR_BGR2GRAY) for m in (ref, src))
    keep = np.zeros(g1.shape, np.uint8); keep[:HEAD_Y] = 255           # 얼굴 위쪽으로 맞춘다
    sift = cv2.SIFT_create(6000)
    k1, d1 = sift.detectAndCompute(g1, keep)
    k2, d2 = sift.detectAndCompute(g2, None)
    good = [m for m, n in cv2.BFMatcher().knnMatch(d2, d1, k=2) if m.distance < 0.7 * n.distance]
    M, _ = cv2.estimateAffinePartial2D(np.float32([k2[m.queryIdx].pt for m in good]),
                                       np.float32([k1[m.trainIdx].pt for m in good]), ransacReprojThreshold=2)
    return cv2.warpAffine(src, M, ref.shape[1::-1], flags=cv2.INTER_CUBIC, borderValue=(255, 255, 255))


def crop_save(name, col, a, meta, anchor=None):
    ys, xs = np.where(a > 0.02)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    cp.webp(OUT / f'{name}.webp', col[y0:y1, x0:x1], a[y0:y1, x0:x1])
    meta[name] = {'xy': [int(x0), int(y0)], 'size': [int(x1 - x0), int(y1 - y0)]}
    if anchor:
        meta[name]['root'] = list(anchor)


def main():
    ch = cv2.imread(str(OUT / 'char.webp'), cv2.IMREAD_UNCHANGED)
    col, a = ch[..., :3], ch[..., 3] / 255.
    H, Wd = a.shape
    orig = (col * a[..., None] + 255 * (1 - a[..., None])).astype(np.uint8)
    under = align(cv2.imread(str(W / 'underlayer_edit.png')), orig)
    ucol, ua = cp.cutout(under)

    # 몸: 편집본 + 위쪽은 원화 (귀걸이 자리는 편집본 유지)
    keep = np.zeros((H, Wd), np.float32); keep[:HEAD_Y] = 1
    for (x0, y0, x1, y1), _ in EARS.values():
        keep[y0 - 10:y1 + 10, x0 - 10:x1 + 10] = 0
    keep = cv2.GaussianBlur(keep, (0, 0), 8)
    bcol = (col * keep[..., None] + ucol * (1 - keep[..., None])).astype(np.uint8)
    ba = a * keep + ua * (1 - keep)

    # 머리카락 다발: 다각형 안의 어두운 머리·파란 머리 (사이의 가는 하이라이트까지)
    gray = cv2.cvtColor(col, cv2.COLOR_BGR2GRAY)
    blue = cp.soft_blue(col)
    core = (((gray < 70) | (blue > .3)) & (a > .5)).astype(np.uint8)
    core = cv2.morphologyEx(core, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    taken = np.zeros((H, Wd), bool)
    meta = {'size': [Wd, H]}
    hair_alpha = np.zeros((H, Wd), np.float32)
    for name, (pts, root) in HAIR.items():
        m = poly_mask((H, Wd), pts) & ~taken & core.astype(bool)
        n, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8))
        m = np.isin(lab, [i for i in range(1, n) if st[i, 4] > 60])
        taken |= m
        ha = cv2.GaussianBlur(m.astype(np.float32), (0, 0), .8) * a
        hair_alpha = np.maximum(hair_alpha, ha)
        crop_save(name, col, ha, meta, root)

    # 귀걸이: 상자 안에서 원화에는 있고 밑그림(얼굴 쪽은 잘 맞음)에는 없는 픽셀
    diff = cv2.absdiff(cv2.GaussianBlur(orig, (0, 0), 1.2), cv2.GaussianBlur(under, (0, 0), 1.2)).max(axis=2)
    ear_all = np.zeros((H, Wd), np.float32)
    for name, ((x0, y0, x1, y1), root) in EARS.items():
        box = np.zeros((H, Wd), np.uint8); box[y0:y1, x0:x1] = 1
        hsv = cv2.cvtColor(col, cv2.COLOR_BGR2HSV)
        silver = ((hsv[..., 1] < 40) & (gray > 110)).astype(np.uint8)       # 은색 금속 근처만
        m = (box & (diff > 45) & cv2.dilate(silver, np.ones((7, 7), np.uint8))).astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        n, lab, st, cen = cv2.connectedComponentsWithStats(m)
        ids = [i for i in range(1, n) if st[i, 4] > 40]
        m = np.isin(lab, ids).astype(np.uint8)
        # 고리에서 아래로 이어진 덩어리만 (옆을 지나는 머리카락 선은 버린다)
        band = np.zeros_like(m); rx = root[0]; band[root[1]:y1, rx - 14:rx + 14] = 1
        grown = cv2.dilate(m, np.ones((3, 3), np.uint8))
        n2, lab2 = cv2.connectedComponents(grown)
        keep_ids = set(np.unique(lab2[(band > 0) & (grown > 0)])) - {0}
        m = (np.isin(lab2, list(keep_ids)) & (m > 0)).astype(np.uint8)
        m = cv2.dilate(m, np.ones((3, 3), np.uint8)).astype(np.float32)
        ea = cv2.GaussianBlur(m, (0, 0), .7) * a
        ear_all = np.maximum(ear_all, ea)
        crop_save(name, col, ea, meta, root)
    for name, (pts, root) in HAIR.items():          # 머리카락 다발에서 귀걸이 부분은 뺀다
        im = cv2.imread(str(OUT / f'{name}.webp'), cv2.IMREAD_UNCHANGED); x, y = meta[name]['xy']; h, w = im.shape[:2]
        im[..., 3] = (im[..., 3] * (1 - ear_all[y:y + h, x:x + w])).astype(np.uint8)
        cv2.imwrite(str(OUT / f'{name}.webp'), im, [cv2.IMWRITE_WEBP_QUALITY, 90])

    crop_save('base', bcol, ba, meta)
    # 파란색 마스크를 몸+머리카락 기준으로 다시 (R 손톱 G 머리 B 눈)
    old = cv2.imread(str(OUT / 'mask.webp')).astype(np.float32) / 255
    bb = cp.soft_blue(bcol) * ba
    g = np.maximum(old[..., 1] * hair_alpha, bb * (1 - old[..., 2]) * (1 - old[..., 0]))
    cp.webp(OUT / 'mask.webp', (np.dstack([old[..., 0], g, old[..., 2]]) * 255).astype(np.uint8), q=92)
    (OUT / 'layers.json').write_text(json.dumps(meta, indent=1))

    # 확인용: 몸만 / 몸+머리카락+귀걸이
    bg = np.full((H, Wd, 3), 236, np.float32)
    def over(dst, name):
        im = cv2.imread(str(OUT / f'{name}.webp'), cv2.IMREAD_UNCHANGED); x, y = meta[name]['xy']
        h, w = im.shape[:2]; al_ = im[..., 3:] / 255.
        dst[y:y + h, x:x + w] = dst[y:y + h, x:x + w] * (1 - al_) + im[..., :3] * al_
    only = bg.copy(); over(only, 'base')
    full = only.copy()
    for n_ in list(HAIR) + list(EARS):
        over(full, n_)
    tint = bg.copy()
    for n_ in list(HAIR) + list(EARS):
        im = cv2.imread(str(OUT / f'{n_}.webp'), cv2.IMREAD_UNCHANGED); x, y = meta[n_]['xy']; h, w = im.shape[:2]
        al_ = im[..., 3:] / 255.
        tint[y:y + h, x:x + w] = tint[y:y + h, x:x + w] * (1 - al_) + np.array([60, 60, 230]) * al_
    pv = np.hstack([only, full, tint]).astype(np.uint8)
    cv2.imwrite(str(OUT / 'layers_preview.png'), cv2.resize(pv[600:2200], None, fx=.4, fy=.4, interpolation=cv2.INTER_AREA))
    for k, v in meta.items():
        print(k, v)


if __name__ == '__main__':
    main()
