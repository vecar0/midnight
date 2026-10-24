#!/usr/bin/env python3
"""Céleste 원화 → 앱용 부품(배경 제거, 눈 감은 패치, 파란색 마스크).

  python3 tools/celeste_parts.py

입력  work/celeste/base_4k.png          PixAI 원화(4K 업스케일 + 위 여백)
      work/celeste/eyes_closed_edit.png  얼굴 부분(base_4k 의 FACE 영역)을 눈 감게 편집한 그림
출력  work/celeste/parts/*.webp, parts.json, preview.png
필요  pip install opencv-python-headless
"""
import json
from pathlib import Path
import cv2, numpy as np

ROOT = Path(__file__).resolve().parent.parent
W = ROOT / 'work/celeste'
OUT = W / 'parts'
S = 0.5                                  # 4K 원화를 반으로 줄여서 쓴다 (1228×2416)
FACE = (760, 1120, 1960, 2400)           # 눈 감은 편집에 보낸 얼굴 영역 (4K 좌표)
# 흰 배경이 머리카락·팔에 갇혀 테두리와 이어지지 않은 곳 (반 크기 좌표)
BG_SEEDS = [(256, 915), (268, 1047), (242, 1151), (962, 1148), (90, 1540),
            (79, 2205), (1102, 2214), (977, 2217), (295, 2319)]
# 눈 감은 패치를 붙일 타원 (얼굴 영역 기준 반 크기 좌표): 중심, 반지름, 각도
EYES = [(148, 322, 72, 56, -12), (345, 256, 112, 66, -14)]
NAILS_Y = 1620                           # 이보다 아래의 파란색은 손톱(+머리끝)


def cutout(img):
    """흰 배경을 지우고 가장자리를 부드럽게. 반환: 색(배경색 걷어낸 것), 알파 0~1"""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    white = ((img.min(axis=2) > 232) & (hsv[..., 1] < 25)).astype(np.uint8)
    _, lab = cv2.connectedComponents(white, connectivity=4)
    ids = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
    ids |= {lab[y, x] for x, y in BG_SEEDS}
    ids.discard(0)
    bg = np.isin(lab, list(ids))
    ring = cv2.dilate(bg.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & ~bg
    a = np.ones(bg.shape, np.float32)
    a[bg] = 0
    a[ring] = np.clip((250 - img.mean(axis=2)[ring]) / 160, 0, 1)
    f = img.astype(np.float32)
    aa = np.maximum(a, 1e-3)[..., None]
    col = np.where(a[..., None] >= 1, f, np.clip((f - (1 - aa) * 255) / aa, 0, 255))
    col[a == 0] = 0
    return col.astype(np.uint8), a


def closed_eyes(face_half):
    """편집본을 원본 얼굴에 맞춰 정렬하고 눈 부분만 잘라 패치로."""
    ed = cv2.imread(str(W / 'eyes_closed_edit.png'))
    fw, fh = FACE[2] - FACE[0], FACE[3] - FACE[1]
    ed = cv2.resize(ed, (fw, round(ed.shape[0] * fw / ed.shape[1])))
    orig = cv2.resize(face_half, (fw, fh))
    g1, g2 = (cv2.cvtColor(m, cv2.COLOR_BGR2GRAY) for m in (orig, ed))
    keep = np.full(g1.shape, 255, np.uint8)
    for cx, cy, ax, ay, _ in EYES:            # 바뀐 눈은 정렬 기준에서 뺀다
        keep[(cy - ay) * 2 - 40:(cy + ay) * 2 + 40, (cx - ax) * 2 - 40:(cx + ax) * 2 + 40] = 0
    sift = cv2.SIFT_create(4000)
    k1, d1 = sift.detectAndCompute(g1, keep)
    k2, d2 = sift.detectAndCompute(g2, None)
    good = [m for m, n in cv2.BFMatcher().knnMatch(d2, d1, k=2) if m.distance < 0.7 * n.distance]
    M, _ = cv2.estimateAffinePartial2D(np.float32([k2[m.queryIdx].pt for m in good]),
                                       np.float32([k1[m.trainIdx].pt for m in good]),
                                       ransacReprojThreshold=3)
    al = cv2.warpAffine(ed, M, (fw, fh), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    al = cv2.resize(al, face_half.shape[1::-1], interpolation=cv2.INTER_AREA)
    mask = np.zeros(face_half.shape[:2], np.float32)
    for cx, cy, ax, ay, ang in EYES:
        cv2.ellipse(mask, (cx, cy), (ax, ay), ang, 0, 360, 1, -1)
    mask = cv2.GaussianBlur(mask, (0, 0), 7)
    return al, mask


def soft_blue(img, s0=45):
    """클라인 블루 쪽 픽셀의 정도 0~1 (s0: 이 채도부터 파랑으로 침, 홍채는 연해서 낮게)"""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    hue = np.clip(1 - np.abs(h - 118) / 22, 0, 1)
    return hue * np.clip((s - s0) / 50, 0, 1) * np.clip((v - 30) / 40, 0, 1)


def webp(path, bgr, a=None, q=90):
    im = bgr if a is None else np.dstack([bgr, (np.clip(a, 0, 1) * 255).astype(np.uint8)])
    cv2.imwrite(str(path), im, [cv2.IMWRITE_WEBP_QUALITY, q])


def main():
    OUT.mkdir(exist_ok=True)
    src = cv2.imread(str(W / 'base_4k.png'))
    img = cv2.resize(src, None, fx=S, fy=S, interpolation=cv2.INTER_AREA)
    H, Wd = img.shape[:2]
    col, a = cutout(img)

    fx0, fy0, fx1, fy1 = (round(v * S) for v in FACE)
    al, emask = closed_eyes(img[fy0:fy1, fx0:fx1])
    ys, xs = np.where(emask > 0.01)
    ex0, ex1, ey0, ey1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    patch_a = emask[ey0:ey1, ex0:ex1]
    webp(OUT / 'eyes_closed.webp', al[ey0:ey1, ex0:ex1], patch_a)

    blue = soft_blue(img) * a
    yy, xx = np.mgrid[:H, :Wd]
    eye_zone = np.zeros((H, Wd), np.float32)
    eye_zone[fy0:fy1, fx0:fx1] = cv2.dilate(emask, np.ones((9, 9), np.uint8))
    eye_zone = np.clip(eye_zone * 2, 0, 1)
    eyes = soft_blue(img, 12) * a * eye_zone
    blue = blue * (1 - eye_zone) + eyes
    nails = blue * (yy > NAILS_Y) * (1 - eyes)
    hair = np.clip(blue - eyes - nails, 0, 1)
    # 손톱 영역 아래의 긴 머리끝은 머리로 되돌린다 (손 둘레 상자 밖)
    hands = np.zeros((H, Wd), np.float32)
    for x0, y0, x1, y1 in [(20, 1640, 330, 1900), (930, 1640, 1210, 1960)]:
        hands[y0:y1, x0:x1] = 1
    hair += nails * (1 - hands)
    nails *= hands

    lum = (0.114 * col[..., 0] + 0.587 * col[..., 1] + 0.299 * col[..., 2])[..., None]
    grey = (col * (1 - blue[..., None]) + lum * blue[..., None] * 1.05).clip(0, 255).astype(np.uint8)

    webp(OUT / 'char.webp', col, a)
    # 파란색 마스크 한 장: R=눈 G=머리 B=손톱 (앱에서 단계마다 색을 되돌린다)
    webp(OUT / 'mask.webp', (np.dstack([nails, hair, eyes]) * 255).astype(np.uint8), q=92)

    meta = {
        'size': [Wd, H],
        'eyesClosed': [int(fx0 + ex0), int(fy0 + ey0)],
        'pivot': {'neck': [680, 1120], 'chest': [640, 1500]},
        'mouth': [655, 1028],
        'earMoon': [452, 962], 'earStar': [852, 890],
        'face': [fx0, fy0, fx1, fy1],
    }
    (OUT / 'parts.json').write_text(json.dumps(meta, indent=1))

    # 확인용: 회색판 / 원본 / 눈 감은 원본
    closed = col.copy()
    r = closed[fy0:fy1, fx0:fx1].astype(np.float32)
    closed[fy0:fy1, fx0:fx1] = (r * (1 - emask[..., None]) + al * emask[..., None]).astype(np.uint8)
    bgc = np.full((H, Wd, 3), (238, 238, 236), np.float32)
    comp = lambda c: (c * a[..., None] + bgc * (1 - a[..., None])).astype(np.uint8)
    pv = np.hstack([comp(grey), comp(col), comp(closed)])
    cv2.imwrite(str(OUT / 'preview.png'), cv2.resize(pv, None, fx=1 / 3, fy=1 / 3, interpolation=cv2.INTER_AREA))
    for p in sorted(OUT.iterdir()):
        print(f'{p.name:20s} {p.stat().st_size / 1024:7.0f} KB')


if __name__ == '__main__':
    main()
