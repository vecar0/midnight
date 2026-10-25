#!/usr/bin/env python3
"""See-through 레이어 + 원화 → 리깅용 레이어.

  python3 tools/celeste_st_layers.py      (먼저 tools/celeste_parts.py 로 char.webp 를 만들어 둘 것)

See-through(AI)가 나눈 레이어는 구조와 '가려진 부분'이 완전하지만 그림이 원화보다 흐리다.
그래서 각 픽셀에서 맨 위에 보이는 레이어에는 원화 색을 넣고, 가려진 부분에만 AI 그림을
(원화 색에 맞춰 보정해서) 남긴다 → 가만히 있을 땐 원화와 똑같고, 움직일 때만 채운 부분이 드러난다.

입력  work/celeste/seethrough/*.png, order.json   See-through 결과 (1024 정사각, seethrough_input.png 기준)
      work/celeste/parts/char.webp                원화 배경 제거본 (반 크기 1228×2416)
출력  work/celeste/rig/*.webp, rig.json, check.png
"""
import json
from pathlib import Path
import cv2, numpy as np

ROOT = Path(__file__).resolve().parent.parent
ST = ROOT / 'work/celeste/seethrough'
OUT = ROOT / 'work/celeste/rig'
SQ = 1520                    # seethrough_input.png 크기
OX, OY = 146, 620            # 입력 그림 좌표 → 원화 좌표: x - OX, y + OY
FACE_X = 650                 # 얼굴 가운데 x (귀걸이 좌우 나누기)
RAIL_Y = 2040                # 이 아래는 난간·허리 (움직이지 않는 레이어)
NECK_Y = 1130                # 이 위는 머리 (고개와 같이 움직임)

# 레이어별 무리: 리깅에서 같이 움직이는 단위
GROUP = {'back_hair': 'hairBack', 'front_hair': 'hairFront', 'neck': 'body', 'topwear': 'body',
         'handwear-l': 'body', 'handwear-r': 'arms', 'rest': 'static', 'restHead': 'head',
         'face': 'face', 'ears-l': 'ears', 'ears-r': 'ears', 'mouth': 'feature', 'nose': 'feature',
         'eyebrow-l': 'feature', 'eyebrow-r': 'feature', 'eyelash-l': 'feature', 'eyelash-r': 'feature',
         'eyewhite-l': 'eyewhite', 'eyewhite-r': 'eyewhite', 'irides-l': 'iris', 'irides-r': 'iris',
         'earMoon': 'earring', 'earStar': 'earring'}


def premul_resize(rgba, size):
    a = rgba[..., 3:4].astype(np.float32) / 255
    pm = np.dstack([rgba[..., :3].astype(np.float32) * a, a * 255])
    r = cv2.resize(pm, size, interpolation=cv2.INTER_LANCZOS4)
    r = np.clip(r, 0, 255)
    aa = r[..., 3:4] / 255
    rgb = np.where(aa > 1e-3, r[..., :3] / np.maximum(aa, 1e-3), 0)
    return np.clip(rgb, 0, 255), np.clip(aa[..., 0], 0, 1)


def to_char(rgb, a, H, W):
    """입력 정사각 좌표의 그림을 원화 캔버스로 옮긴다"""
    C = np.zeros((H, W, 3), np.float32); A = np.zeros((H, W), np.float32)
    ys, ye = OY, min(H, OY + SQ)
    C[ys:ye] = rgb[:ye - ys, OX:OX + W]
    A[ys:ye] = a[:ye - ys, OX:OX + W]
    return C, A


def main():
    OUT.mkdir(exist_ok=True)
    ch = cv2.imread(str(ROOT / 'work/celeste/parts/char.webp'), cv2.IMREAD_UNCHANGED)
    orig, oa = ch[..., :3].astype(np.float32), ch[..., 3].astype(np.float32) / 255
    H, W = oa.shape
    order = json.loads((ST / 'order.json').read_text())['order_bottom_to_top']
    info = {}
    L = {}
    for n in order:
        im = cv2.imread(str(ST / f'{n}.png'), cv2.IMREAD_UNCHANGED)
        rgb, a = premul_resize(im, (SQ, SQ))
        L[n] = list(to_char(rgb, a, H, W))
    # 귀걸이를 달과 별로 나눈다
    rgb, a = L.pop('earwear')
    xx = np.arange(W)[None, :]
    L['earMoon'] = [rgb, a * (xx < FACE_X)]; L['earStar'] = [rgb.copy(), a * (xx >= FACE_X)]
    i = order.index('earwear'); order[i:i + 1] = ['earMoon', 'earStar']
    # 난간·허리 아래, 그리고 어느 레이어도 덮지 않는 원화 픽셀 → 'rest' 또는 앞머리
    union = np.zeros((H, W), np.float32)
    for n in order:
        union = np.maximum(union, L[n][1])
    gray = cv2.cvtColor(orig.astype(np.uint8), cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(orig.astype(np.uint8), cv2.COLOR_BGR2HSV)
    hairish = ((gray < 80) | ((np.abs(hsv[..., 0].astype(int) - 118) < 20) & (hsv[..., 1] > 60)))
    yy = np.arange(H)[:, None]
    lost = np.clip(oa - union, 0, 1) * (union < .5)
    near_hair = cv2.dilate(((L['front_hair'][1] > .3) | (L['back_hair'][1] > .3)).astype(np.uint8), np.ones((31, 31), np.uint8))
    to_hair = lost * hairish * (yy < 1780) * near_hair          # 머리카락 근처의 어두운/파란 픽셀만 (난간·허리 조각 제외)
    rest_a = np.where(yy >= RAIL_Y, oa, np.clip(lost - to_hair, 0, 1))
    L['rest'] = [orig.copy(), rest_a.astype(np.float32)]
    order.insert(order.index('handwear-r'), 'rest')          # 난간: 몸통 앞, 팔 뒤
    fh = L['front_hair']
    fh[0] = np.where(to_hair[..., None] > fh[1][..., None], orig, fh[0]); fh[1] = np.maximum(fh[1], to_hair)
    for n in ('front_hair', 'back_hair', 'topwear', 'neck', 'handwear-r', 'handwear-l'):  # 난간 아래는 rest 가 맡는다
        if n in L and n != 'rest':
            L[n][1] = L[n][1] * (1 - (yy >= RAIL_Y + 40))

    # 위에서부터: 보이는 만큼 원화 색으로, 가려진 곳은 AI 그림을 원화 색에 맞춰 보정
    remain = np.ones((H, W), np.float32)
    for n in reversed(order):
        rgb, a = L[n]
        vis = a * remain
        w = np.clip(vis * 2.5, 0, 1)
        own = (vis > .8) & (a > .9)
        if own.sum() > 200 and n != 'rest':                   # 채널마다 gen→orig 직선 맞춤
            for c in range(3):
                g, o = rgb[..., c][own], orig[..., c][own]
                k, b = np.polyfit(g, o, 1)
                rgb[..., c] = np.where(w < 1, np.clip(rgb[..., c] * k + b, 0, 255), rgb[..., c])
        rgb = rgb * (1 - w[..., None]) + orig * w[..., None]
        a = a * (1 - w) + oa * w * (a > .02)                   # 보이는 가장자리는 원화 윤곽을 따른다
        L[n] = [rgb, a]
        remain *= 1 - L[n][1]

    # 'rest' 중 머리 쪽 조각은 고개와 같이 움직이게 따로 (고정해 두면 고개만 움직일 때 떨어져 보인다)
    headw = (1 - np.clip((yy - (NECK_Y - 30)) / 60, 0, 1)).astype(np.float32)
    rgb, a = L['rest']
    L['restHead'] = [rgb.copy(), a * headw]
    L['rest'] = [rgb, a * (1 - headw)]
    order.insert(order.index('back_hair') + 1, 'restHead')
    # 맨 아래 밑판: 몸통 쪽 원화만 (머리까지 깔면 고개가 움직일 때 원래 머리 윤곽이 뒤에 겹쳐 보인다)
    L['under'] = [orig.copy(), oa * .995 * (1 - headw)]
    order.insert(0, 'under')
    GROUP['under'] = 'static'

    meta = {'size': [W, H], 'order': [], 'layers': {}}
    rest_check = np.zeros((H, W, 3), np.float32) + 236
    for n in order:
        rgb, a = L[n]
        # AI 레이어의 옅은 잡티 정리: 거의 투명한 픽셀과 작은 부스러기를 지운다
        a = np.where(a < .04, 0, a)
        n_, lab, st, _ = cv2.connectedComponentsWithStats((a > .04).astype(np.uint8))
        small = [i for i in range(1, n_) if st[i, 4] < 40]
        if small:
            a = np.where(np.isin(lab, small), 0, a)
        L[n][1] = a
        ys, xs = np.where(a > .01)
        if len(xs) == 0:
            continue
        x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        im = np.dstack([rgb[y0:y1, x0:x1], a[y0:y1, x0:x1] * 255]).astype(np.uint8)
        cv2.imwrite(str(OUT / f'{n}.webp'), im, [cv2.IMWRITE_WEBP_QUALITY, 92])
        meta['order'].append(n)
        meta['layers'][n] = {'xy': [int(x0), int(y0)], 'size': [int(x1 - x0), int(y1 - y0)], 'group': GROUP.get(n, 'body')}
        rest_check = rest_check * (1 - a[..., None]) + rgb * a[..., None]
    (OUT / 'rig.json').write_text(json.dumps(meta, indent=1))
    src = orig * oa[..., None] + 236 * (1 - oa[..., None])
    diff = np.abs(rest_check - src).mean(axis=2)
    print('원화와의 평균 차이', round(float(diff.mean()), 2), ' 99% 지점', round(float(np.percentile(diff, 99)), 1))
    cv2.imwrite(str(OUT / 'check.png'), cv2.resize(np.hstack([src, rest_check, np.dstack([diff * 4] * 3)]).clip(0, 255).astype(np.uint8)[600:2200],
                                                    None, fx=.35, fy=.35, interpolation=cv2.INTER_AREA))
    for n in meta['order']:
        print(n, meta['layers'][n])


if __name__ == '__main__':
    main()
