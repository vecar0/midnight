#!/usr/bin/env python3
"""오브젝트 시트(투명 배경 3×2) → 낱개 webp, 뻗는 손 → webp.

  python3 tools/celeste_objects.py
입력  work/celeste/objects_sheet*.png (SHEETS 표), work/celeste/hand_reach.png
출력  work/celeste/parts/obj_*.webp, hand.webp
"""
from pathlib import Path
import cv2, numpy as np

ROOT = Path(__file__).resolve().parent.parent
W = ROOT / 'work/celeste'
OUT = W / 'parts'
# 시트 파일, 칸 수(가로, 세로), 이름(왼쪽 위부터 행 순서)
SHEETS = [
    ('objects_sheet.png', 3, 2, ['moon', 'angel', 'hands', 'lily', 'chess', 'arch']),
    ('objects_sheet2.png', 4, 2, ['armillary', 'earth', 'watch', 'hourglass', 'telescope', 'astronaut', 'saturn', 'crescent']),
    ('objects_sheet3.png', 4, 2, ['bust', 'wing', 'column', 'mask', 'crown', 'cherub', 'gargoyle', 'keyhand']),
    ('objects_sheet4.png', 4, 2, ['dove', 'roses', 'iris', 'birdcage', 'mirror', 'candelabra', 'book', 'perfume']),
]
MAXW = 1100                                                   # 낱개 최대 변 길이


def save(path, im, maxw=MAXW):
    s = min(1, maxw / max(im.shape[:2]))
    if s < 1:
        im = cv2.resize(im, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    cv2.imwrite(str(path), im, [cv2.IMWRITE_WEBP_QUALITY, 88])
    return im.shape[1], im.shape[0]


def split_sheet(file, cols, rows, names):
    sh = cv2.imread(str(W / file), cv2.IMREAD_UNCHANGED)
    a = (sh[..., 3] > 8).astype(np.uint8)
    a = cv2.morphologyEx(a, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))   # 한 물체 안의 틈 메우기
    n, lab, st, cen = cv2.connectedComponentsWithStats(a)
    H, Wd = a.shape
    cells = {}                                       # 칸마다 조각을 모은다 (두 손처럼 떨어진 물체)
    for i in range(1, n):
        if st[i, 4] < 20000:
            continue
        k = int(cen[i, 1] // (H / rows)) * cols + int(cen[i, 0] // (Wd / cols))
        cells.setdefault(k, []).append(i)
    if sorted(cells) != list(range(len(names))):
        raise SystemExit(f'{file}: 칸 {sorted(cells)} 에서 물체를 찾음 (기대 {len(names)}칸)')
    for k, name in enumerate(names):
        ids = cells[k]
        x = min(st[i, 0] for i in ids); y = min(st[i, 1] for i in ids)
        w = max(st[i, 0] + st[i, 2] for i in ids) - x; h = max(st[i, 1] + st[i, 3] for i in ids) - y
        p = 6
        crop = sh[max(0, y - p):y + h + p, max(0, x - p):x + w + p].copy()
        keep = np.isin(lab[max(0, y - p):y + h + p, max(0, x - p):x + w + p], ids)
        keep = cv2.dilate(keep.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)
        crop[~keep] = 0
        print(f'obj_{name}.webp', save(OUT / f'obj_{name}.webp', crop))


def main():
    for file, cols, rows, names in SHEETS:
        if (W / file).exists():
            split_sheet(file, cols, rows, names)
    hand = cv2.imread(str(W / 'hand_reach.png'), cv2.IMREAD_UNCHANGED)
    hand = cv2.flip(hand, 1)            # 왼손으로 나와서 뒤집어 오른손으로
    print('hand.webp', save(OUT / 'hand.webp', hand, 1000))


if __name__ == '__main__':
    main()
