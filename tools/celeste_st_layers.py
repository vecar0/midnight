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
import json, sys
from pathlib import Path
import cv2, numpy as np

ROOT = Path(__file__).resolve().parent.parent
ST = ROOT / 'work/celeste/seethrough'
OUT = ROOT / 'work/celeste/rig'
SQ = 1520                    # seethrough_input.png 크기
OX, OY = 146, 620            # 입력 그림 좌표 → 원화 좌표: x - OX, y + OY
FACE_X = 650                 # 얼굴 가운데 x (귀걸이 좌우 나누기)
RAIL_Y = 2040                # 이 아래는 난간·허리 (움직이지 않는 레이어)
BEAD_BOXES = [(841, 998, 860, 1038)]   # 별 귀걸이 아래 구슬 (반 크기 좌표)
NECK_Y = 1130                # 이 위는 머리 (고개와 같이 움직임)

# 레이어별 무리: 리깅에서 같이 움직이는 단위
GROUP = {'back_hair': 'hairBack', 'front_hair': 'hairFront', 'neck': 'body', 'topwear': 'body',
         'handwear-l': 'body', 'handwear-r': 'arms', 'rest': 'static', 'restHead': 'head',
         'face': 'face', 'ears-l': 'ears', 'ears-r': 'ears', 'mouth': 'feature', 'nose': 'feature',
         'eyebrow-l': 'feature', 'eyebrow-r': 'feature', 'eyelash-l': 'feature', 'eyelash-r': 'feature',
         'eyewhite-l': 'eyewhite', 'eyewhite-r': 'eyewhite', 'irides-l': 'iris', 'irides-r': 'iris',
         'earMoon': 'earring', 'earStar': 'earring'}


def sm_np(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


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

    # 움직이는 레이어가 원화의 눈동자·머리카락을 빠짐없이 덮도록 넓힌다
    #  (덜 덮으면 남은 원화 조각이 아래 레이어에 찍혀, 움직일 때 두 겹으로 보인다)
    for side in ('l', 'r'):
        ir, ew = L[f'irides-{side}'], L[f'eyewhite-{side}']
        inside = cv2.dilate((ew[1] > .3).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
        notwhite = (orig.min(axis=2) < 175) | (np.abs(hsv[..., 0].astype(int) - 118) < 25) & (hsv[..., 1] > 40)
        # 흰자 안의 어두운/파란 덩어리 중 AI 눈동자와 이어진 것만 (속눈썹 그림자는 빼기)
        cand = (inside & notwhite).astype(np.uint8)
        n_, lab = cv2.connectedComponents(cand)
        keep = set(np.unique(lab[(ir[1] > .3) & (cand > 0)])) - {0}
        extra = np.isin(lab, list(keep)) & (ir[1] < .5)
        ir[0] = np.where(extra[..., None], orig, ir[0]); ir[1] = np.maximum(ir[1], extra * oa)
    # 원화에서 머리카락으로 이어진 픽셀은 전부 머리 레이어로 (옷·밑판에 찍히면 흔들릴 때 두 겹)
    fh, bh = L['front_hair'], L['back_hair']
    hair_union = ((fh[1] > .3) | (bh[1] > .3)).astype(np.uint8)
    cand = (hairish & (oa > .5) & (yy < RAIL_Y)).astype(np.uint8)
    cand = cv2.morphologyEx(cand, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    n_, lab = cv2.connectedComponents(cand)
    touch = set(np.unique(lab[(cv2.dilate(hair_union, np.ones((7, 7), np.uint8)) > 0) & (cand > 0)])) - {0}
    allhair = np.isin(lab, list(touch))
    # 옷(뷔스티에 광택·시스루 소매)의 어두운 부분은 머리가 아니다: 몸통 레이어가 덮는 넓은 덩어리는 제외
    body_core = cv2.erode(((L['topwear'][1] > .5) | (L['handwear-r'][1] > .5)).astype(np.uint8), np.ones((25, 25), np.uint8)) > 0
    allhair &= ~(body_core & ~(cv2.dilate(hair_union, np.ones((15, 15), np.uint8)) > 0))
    to_front = allhair & (cv2.dilate((fh[1] > .3).astype(np.uint8), np.ones((9, 9), np.uint8)) > 0) & (fh[1] < .5)
    to_back = allhair & ~to_front & (fh[1] < .3) & (bh[1] < .5)
    fh[0] = np.where(to_front[..., None], orig, fh[0]); fh[1] = np.maximum(fh[1], to_front * oa)
    bh[0] = np.where(to_back[..., None], orig, bh[0]); bh[1] = np.maximum(bh[1], to_back * oa)

    # 사용자가 프로크리에이트에서 잘라낸 머리 다발 자리(strands/hole.png)를 결 방향 띠로 나눠 다발 레이어로
    STRANDS = []
    hp = ROOT / 'work/celeste/strands/hole.png'
    if hp.exists():
        hole = (cv2.imread(str(hp), 0) > 127).astype(np.uint8)
        n_, hl, st_, _ = cv2.connectedComponentsWithStats(hole)
        idx = 0
        for ci in sorted(range(1, n_), key=lambda i: st_[i, 0]):
            if st_[ci, 4] < 1500:
                continue
            C = hl == ci
            K = 1                                           # 잘라준 덩어리를 그대로 한 다발로
            rows = np.where(C.any(axis=1))[0]
            Lx = np.full(H, np.nan); Rx = np.full(H, np.nan)
            for y in rows:
                xs_ = np.where(C[y])[0]; Lx[y], Rx[y] = xs_.min(), xs_.max()
            ok = ~np.isnan(Lx)
            for arr in (Lx, Rx):                       # 줄마다 튀는 경계를 매끄럽게
                v = np.interp(np.arange(H), np.where(ok)[0], arr[ok])
                arr[:] = np.convolve(np.pad(v, 30, mode='edge'), np.ones(61) / 61, 'valid')
            u = (np.arange(W)[None, :] - Lx[:, None]) / np.maximum(Rx - Lx, 8)[:, None]
            # 경계 정리: 낮은 해상도에서 구한 자리라 가장자리 몇 픽셀은 원화의 머리/피부 구분으로 다듬는다
            inner = cv2.erode(C.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
            outer = cv2.dilate(C.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
            darkish = (gray < 120) | ((np.abs(hsv[..., 0].astype(int) - 118) < 22) & (hsv[..., 1] > 50))
            C = inner | (outer & darkish)
            Cs = cv2.GaussianBlur(C.astype(np.float32), (0, 0), .8)
            for k in range(K):
                lo, hi = k / K, (k + 1) / K
                wk = np.ones_like(u) if K == 1 else (sm_np(lo - .05, lo + .05, u) if k > 0 else 1) * (1 - sm_np(hi - .05, hi + .05, u) if k < K - 1 else 1)
                a_ = (Cs * wk * oa).astype(np.float32)
                if a_.sum() < 500:
                    continue
                name = f'strand{idx:02d}'; idx += 1
                L[name] = [orig.copy(), a_]
                ys_ = np.where(a_.max(axis=1) > .3)[0]
                xs_ = np.where(a_[ys_[0]:ys_[0] + 40].max(axis=0) > .3)[0]
                STRANDS.append((name, [int(xs_.mean()), int(ys_[0])], int(ys_[-1] - ys_[0])))
        # 다발 자리에서 머리(앞머리) 레이어는 빼고, 뒤에는 어두운 머리색 받침을 깐다
        hsoft = cv2.GaussianBlur(hole.astype(np.float32), (0, 0), 1.5)
        L['front_hair'][1] = L['front_hair'][1] * (1 - hsoft)
        at = order.index('front_hair')
        for name, _, _ in STRANDS:
            order.insert(at, name); at += 1
            GROUP[name] = 'strand'

    MOVING = {'front_hair', 'back_hair', 'irides-l', 'irides-r', 'earMoon', 'earStar'} | {n for n, _, _ in STRANDS}
    # 위에서부터: 보이는 만큼 원화 색으로, 가려진 곳은 AI 그림을 원화 색에 맞춰 보정.
    # 단, 움직이는 레이어 바로 밑은 원화를 찍지 않고 AI 그림을 둔다 (움직이면 드러나는 자리)
    remain = np.ones((H, W), np.float32)
    under_moving = np.zeros((H, W), np.float32)
    for n in reversed(order):
        rgb, a = L[n]
        vis = a * remain
        w = np.clip(vis * 2.5, 0, 1)
        if n not in MOVING and n not in ('rest', 'under'):
            w = w * (1 - under_moving)
        own = (vis > .8) & (a > .9) & (under_moving < .1)
        if own.sum() > 200 and n != 'rest':                   # 채널마다 gen→orig 직선 맞춤
            for c in range(3):
                g, o = rgb[..., c][own], orig[..., c][own]
                k, b = np.polyfit(g, o, 1)
                rgb[..., c] = np.where(w < 1, np.clip(rgb[..., c] * k + b, 0, 255), rgb[..., c])
        rgb = rgb * (1 - w[..., None]) + orig * w[..., None]
        a = a * (1 - w) + oa * w * (a > .02)                   # 보이는 가장자리는 원화 윤곽을 따른다
        L[n] = [rgb, a]
        if n in MOVING:
            under_moving = np.maximum(under_moving, cv2.GaussianBlur((a > .15).astype(np.float32), (0, 0), 1.2))
        remain *= 1 - L[n][1]

    # 'rest' 중 머리 쪽 조각은 고개와 같이 움직이게 따로 (고정해 두면 고개만 움직일 때 떨어져 보인다)
    headw = (1 - np.clip((yy - (NECK_Y - 30)) / 60, 0, 1)).astype(np.float32)
    rgb, a = L['rest']
    L['restHead'] = [rgb.copy(), a * headw]
    L['rest'] = [rgb, a * (1 - headw)]
    order.insert(order.index('back_hair') + 1, 'restHead')
    # 맨 아래 밑판: 몸통 쪽 원화만 (머리까지 깔면 고개가 움직일 때 원래 머리 윤곽이 뒤에 겹쳐 보인다)
    hairzone = cv2.GaussianBlur(cv2.dilate((under_moving > .1).astype(np.uint8), np.ones((9, 9), np.uint8)).astype(np.float32), (0, 0), 2)
    L['under'] = [orig.copy(), oa * .995 * (1 - headw) * (1 - hairzone)]
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
    # 다발 밑: Higgsfield로 옆머리·귀걸이를 지운 편집본(underlayer_edit.png)을 다발 자리 주변에서 원화에 맞춰 깐다
    if STRANDS:
        ed = cv2.imread(str(ROOT / 'work/celeste/underlayer_edit.png'))
        src_w = (orig * oa[..., None] + 255 * (1 - oa[..., None])).astype(np.uint8)
        ring = (cv2.dilate(hole, np.ones((121, 121), np.uint8)) > 0) & ~(cv2.dilate(hole, np.ones((15, 15), np.uint8)) > 0) & (oa > .5)
        g1, g2 = cv2.cvtColor(src_w, cv2.COLOR_BGR2GRAY), cv2.cvtColor(ed, cv2.COLOR_BGR2GRAY)
        sift = cv2.SIFT_create(8000)
        k1, d1 = sift.detectAndCompute(g1, ring.astype(np.uint8) * 255); k2, d2 = sift.detectAndCompute(g2, None)
        good = [m for m, n in cv2.BFMatcher().knnMatch(d2, d1, k=2) if m.distance < .7 * n.distance]
        Mu, _ = cv2.estimateAffinePartial2D(np.float32([k2[m.queryIdx].pt for m in good]), np.float32([k1[m.trainIdx].pt for m in good]), ransacReprojThreshold=2)
        uw = cv2.warpAffine(ed, Mu, (W, H), flags=cv2.INTER_CUBIC, borderValue=(255, 255, 255)).astype(np.float32)
        for c in range(3):                                       # 색을 원화에 맞춘다
            k_, b_ = np.polyfit(uw[..., c][ring], orig[..., c][ring], 1)
            uw[..., c] = np.clip(uw[..., c] * k_ + b_, 0, 255)
        # 편집본의 흰 배경과 그 가장자리 밝은 테두리는 뺀다 (배경에서 이어진 밝은 무채색 픽셀 전부)
        light = ((uw.min(axis=2) > 185) & (uw.max(axis=2) - uw.min(axis=2) < 25)).astype(np.uint8)
        n_, lab_ = cv2.connectedComponents(light)
        bgid = set(np.unique(np.concatenate([lab_[0], lab_[-1], lab_[:, 0], lab_[:, -1]]))) - {0}
        bgm = cv2.dilate(np.isin(lab_, list(bgid)).astype(np.uint8), np.ones((5, 5), np.uint8))
        ua_ = cv2.GaussianBlur(1 - bgm.astype(np.float32), (0, 0), 1)
        earm = ((L['earMoon'][1] > .1) | (L['earStar'][1] > .1)).astype(np.uint8)    # 귀걸이 뒤도 귀걸이 없는 그림으로
        # 귀걸이 자리는 얼굴만 크게 잘라 귀걸이만 지운 편집본(ears_off_edit.png)이 더 자연스러우면 그걸로
        ep = ROOT / 'work/celeste/ears_off_edit.png'
        if ep.exists():
            fx0, fy0, fx1, fy1 = 380, 560, 980, 1200                      # 얼굴 크롭 영역 (반 크기 좌표)
            e = cv2.imread(str(ep)); e = cv2.resize(e, (fx1 - fx0, round(e.shape[0] * (fx1 - fx0) / e.shape[1])), interpolation=cv2.INTER_AREA)
            ref = src_w[fy0:fy1, fx0:fx1]
            keepm = (1 - cv2.dilate(earm[fy0:fy1, fx0:fx1], np.ones((41, 41), np.uint8))) * 255
            ka, da = sift.detectAndCompute(cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY), keepm.astype(np.uint8))
            kb, db = sift.detectAndCompute(cv2.cvtColor(e, cv2.COLOR_BGR2GRAY), None)
            gd = [m for m, n in cv2.BFMatcher().knnMatch(db, da, k=2) if m.distance < .7 * n.distance]
            Me, _ = cv2.estimateAffinePartial2D(np.float32([kb[m.queryIdx].pt for m in gd]), np.float32([ka[m.trainIdx].pt for m in gd]), ransacReprojThreshold=2)
            ew = cv2.warpAffine(e, Me, (fx1 - fx0, fy1 - fy0), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_REPLICATE).astype(np.float32)
            kk = cv2.GaussianBlur(cv2.dilate(earm[fy0:fy1, fx0:fx1], np.ones((21, 21), np.uint8)).astype(np.float32), (0, 0), 4)[..., None]
            uw[fy0:fy1, fx0:fx1] = uw[fy0:fy1, fx0:fx1] * (1 - kk) + ew * kk
            ua_[fy0:fy1, fx0:fx1] = np.maximum(ua_[fy0:fy1, fx0:fx1], kk[..., 0])
            print('귀걸이 자리 편집본 정렬 점', len(gd))
            # 원화와 귀걸이 없는 그림이 크게 다른 곳 = 귀걸이 전체(아래 구슬까지) → 귀걸이 레이어에 보탠다
            near = cv2.dilate(earm[fy0:fy1, fx0:fx1], np.ones((61, 61), np.uint8)) > 0
            df = np.abs(orig[fy0:fy1, fx0:fx1] - ew).max(axis=2)
            silverish = (cv2.cvtColor(orig[fy0:fy1, fx0:fx1].astype(np.uint8), cv2.COLOR_BGR2HSV)[..., 1] < 90)
            near_s = cv2.dilate(earm[fy0:fy1, fx0:fx1], np.ones((31, 31), np.uint8)) > 0
            right = (np.arange(fx0, fx1)[None, :] >= FACE_X)
            extra = ((df > 60) & ((near & silverish) | (near_s & right))).astype(np.uint8)   # 별 쪽은 파란 구슬까지
            extra = cv2.morphologyEx(extra, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
            n_e, lab_e = cv2.connectedComponents(cv2.dilate(extra, np.ones((3, 3), np.uint8)))
            touch = set(np.unique(lab_e[cv2.dilate(earm[fy0:fy1, fx0:fx1], np.ones((9, 9), np.uint8)) > 0])) - {0}
            extra = (np.isin(lab_e, list(touch)) & (extra > 0)).astype(np.float32)
            for en in ('earMoon', 'earStar'):
                Le = meta['layers'][en]; ex, ey = Le['xy']; ewd, eh = Le['size']
                cur = np.zeros((H, W, 4), np.float32)
                cur[ey:ey + eh, ex:ex + ewd] = cv2.imread(str(OUT / f'{en}.webp'), cv2.IMREAD_UNCHANGED)
                side = (np.arange(W)[None, :] < FACE_X) if en == 'earMoon' else (np.arange(W)[None, :] >= FACE_X)
                add = np.zeros((H, W), np.float32); add[fy0:fy1, fx0:fx1] = extra
                add = cv2.GaussianBlur(add, (0, 0), .7) * side * oa
                cur[..., :3] = np.where((add > cur[..., 3] / 255)[..., None], orig, cur[..., :3])
                cur[..., 3] = np.maximum(cur[..., 3], add * 255)
                ys_, xs_ = np.where(cur[..., 3] > 2); a0, a1, b0, b1 = xs_.min(), xs_.max() + 1, ys_.min(), ys_.max() + 1
                cv2.imwrite(str(OUT / f'{en}.webp'), cur[b0:b1, a0:a1].clip(0, 255).astype(np.uint8), [cv2.IMWRITE_WEBP_QUALITY, 92])
                Le['xy'] = [int(a0), int(b0)]; Le['size'] = [int(a1 - a0), int(b1 - b0)]
                earm = np.maximum(earm, (cur[..., 3] > 25).astype(np.uint8))
        # 별 귀걸이 아래 구슬: 편집본에도 남아 있어 직접 지정. 귀걸이 레이어로 옮기고 밑그림은 주변 머리로 메운다
        bead = np.zeros((H, W), np.uint8)
        for bx0, by0, bx1, by1 in BEAD_BOXES:
            hsv_b = cv2.cvtColor(orig[by0:by1, bx0:bx1].astype(np.uint8), cv2.COLOR_BGR2HSV)
            bead[by0:by1, bx0:bx1] = ((hsv_b[..., 2] > 130) & (hsv_b[..., 1] < 90)).astype(np.uint8)   # 흰 테두리만 (파란 머리 제외)
        bead = cv2.dilate(bead, np.ones((3, 3), np.uint8))
        if bead.any():
            Le = meta['layers']['earStar']; ex, ey = Le['xy']; ewd, eh = Le['size']
            cur = np.zeros((H, W, 4), np.float32); cur[ey:ey + eh, ex:ex + ewd] = cv2.imread(str(OUT / 'earStar.webp'), cv2.IMREAD_UNCHANGED)
            ba = cv2.GaussianBlur(bead.astype(np.float32), (0, 0), .7)
            cur[..., :3] = np.where((ba > cur[..., 3] / 255)[..., None], orig, cur[..., :3]); cur[..., 3] = np.maximum(cur[..., 3], ba * 255)
            ys_, xs_ = np.where(cur[..., 3] > 2); a0, a1, b0, b1 = xs_.min(), xs_.max() + 1, ys_.min(), ys_.max() + 1
            cv2.imwrite(str(OUT / 'earStar.webp'), cur[b0:b1, a0:a1].clip(0, 255).astype(np.uint8), [cv2.IMWRITE_WEBP_QUALITY, 92])
            Le['xy'] = [int(a0), int(b0)]; Le['size'] = [int(a1 - a0), int(b1 - b0)]
            bm = cv2.dilate(bead, np.ones((5, 5), np.uint8))
            uw = cv2.inpaint(uw.clip(0, 255).astype(np.uint8), bm, 6, cv2.INPAINT_TELEA).astype(np.float32)
            earm = np.maximum(earm, bead)
        reg = cv2.GaussianBlur(cv2.dilate(hole | earm, np.ones((9, 9), np.uint8)).astype(np.float32), (0, 0), 2)
        ar = (reg * ua_ * (yy < RAIL_Y)).astype(np.float32)
        ys_, xs_ = np.where(ar > .01); x0, x1, y0, y1 = xs_.min(), xs_.max() + 1, ys_.min(), ys_.max() + 1
        cv2.imwrite(str(OUT / 'underHair.webp'), np.dstack([uw[y0:y1, x0:x1], ar[y0:y1, x0:x1] * 255]).astype(np.uint8), [cv2.IMWRITE_WEBP_QUALITY, 92])
        meta['layers']['underHair'] = {'xy': [int(x0), int(y0)], 'size': [int(x1 - x0), int(y1 - y0)], 'group': 'underHair'}
        first = min(meta['order'].index(n) for n in [n for n, _, _ in STRANDS] + ['earMoon', 'earStar'] if n in meta['order'])
        meta['order'].insert(first, 'underHair')
        # 귀걸이는 베이스(다발·앞머리 포함)에서 지우고 귀걸이 없는 그림으로 채운 뒤, 귀걸이만 다발 위로 올린다
        earw = cv2.GaussianBlur(cv2.dilate(earm, np.ones((13, 13), np.uint8)).astype(np.float32), (0, 0), 1)
        for n in [n for n, _, _ in STRANDS] + ['front_hair', 'restHead', 'face', 'neck', 'topwear']:
            if n not in meta['layers']:
                continue
            Ld = meta['layers'][n]; x0, y0 = Ld['xy']; w, h = Ld['size']
            im = cv2.imread(str(OUT / f'{n}.webp'), cv2.IMREAD_UNCHANGED).astype(np.float32)
            # 덧칠하지 않고 비운다: 아래 밑그림(귀걸이 없는 그림)이 보이게
            im[..., 3] *= 1 - earw[y0:y0 + h, x0:x0 + w]
            cv2.imwrite(str(OUT / f'{n}.webp'), im.clip(0, 255).astype(np.uint8), [cv2.IMWRITE_WEBP_QUALITY, 92])
        for e in ('earMoon', 'earStar'):
            meta['order'].remove(e)
        at = meta['order'].index('front_hair')
        meta['order'][at:at] = ['earMoon', 'earStar']
        print('밑그림 정렬 점', len(good))
    for name, root, length in STRANDS:
        if name in meta['layers']:
            meta['layers'][name]['root'] = root; meta['layers'][name]['len'] = length
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
    # 프로크리에이트에서 손본 레이어가 있으면 덮어쓴다 (tools/celeste_psd_roundtrip.py)
    import subprocess
    subprocess.run([sys.executable, str(ROOT / 'tools/celeste_psd_roundtrip.py'), 'apply'])
