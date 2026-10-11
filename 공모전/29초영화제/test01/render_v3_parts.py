# =========================================================== v3 전용 (render.py에 병합됨, 원본 보관용)
def sun_sprite_v3(t, st):
    """절차형 코어(쌀알무늬 ±5%, 셀 6~10px, 초당 2px 흐름 + 노이즈 변위 3px/48f) + 구면 얼굴 + 코어 블룸."""
    core = G['sun_core_rgb']; a = G['sun_core_a']; cor = G['sun_corona']; gran = G['gran']
    N = core.shape[0]; C = N / 2 - 0.5; R2 = SUN_R * SS
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
    ph = 2 * np.pi * t / 48.0; amp = 3.0 * SS
    dx = amp * (G['SDX1'][:N, :N] * np.cos(ph) + G['SDX2'][:N, :N] * np.sin(ph))
    dy = amp * (G['SDY1'][:N, :N] * np.cos(ph) + G['SDY2'][:N, :N] * np.sin(ph))
    flow = t * (2.0 / 24.0) * SS
    gr = map_coordinates(gran, [yy + dy, xx + dx + 200 - flow], order=1, mode='wrap')
    rr = np.hypot(xx - C, yy - C) / R2
    mu = np.sqrt(np.clip(1 - rr ** 2, 0, 1))
    body = core * (1 + 0.05 * gr * (0.4 + 0.6 * mu))[..., None]
    ca = 5.0 * SS * 230 / 300
    ring = np.clip((rr - 0.95) / 0.1, 0, 1)
    cdx = ca * (G['CDX'][:N, :N] * np.cos(ph * 1.7) + G['SDX2'][:N, :N] * np.sin(ph * 1.7)) * ring
    cdy = ca * (G['CDY'][:N, :N] * np.cos(ph * 1.7) + G['SDY1'][:N, :N] * np.sin(ph * 1.7)) * ring
    corona = np.stack([map_coordinates(cor[..., c], [yy + cdy - 1.2 * SS * np.sin(ph * 2), xx + cdx], order=1, mode='constant') for c in range(3)], -1)
    flk = G['FLK']; fl = sum(w_ * np.sin(2 * np.pi * t / P + p) for P, p, w_ in flk) / flk[:, 2].sum()
    corona = corona * (1 + 0.10 * fl)
    frgb, fa, half = sun_face(st)
    s0 = int(C - half + 0.5); n = frgb.shape[0]
    fy, fx = np.mgrid[0:n, 0:n].astype(np.float32)
    px, py = fx + s0 - C, fy + s0 - C
    rho = np.hypot(px, py) / R2
    k = 1 + 0.25 * np.clip(rho, 0, 1.2) ** 2
    sx_, sy_ = px * k + C - s0, py * k + C - s0
    frgb = np.stack([map_coordinates(frgb[..., c], [sy_, sx_], order=1, mode='constant') for c in range(3)], -1)
    fa = map_coordinates(fa, [sy_, sx_], order=1, mode='constant')
    sig_ = 0.7 * SS
    fa = gaussian_filter(fa, sig_); frgb = gaussian_filter(frgb, (sig_, sig_, 0))
    sl = (slice(s0, s0 + n), slice(s0, s0 + n))
    fa = fa * a[sl] * 0.90
    out = body.copy()
    out[sl] = out[sl] * (1 - fa[..., None]) + frgb * fa[..., None]
    bloom = gaussian_filter(body[sl], (6, 6, 0))
    fm = np.clip(gaussian_filter(fa, 4) * 1.6, 0, 1)
    out[sl] = screen(out[sl], bloom * 0.13 * fm[..., None])
    return out * a[..., None], a, corona

def signal_column(img, v, t, mix):
    """1 100% 절차형 반사 기둥. 폭 0.5D(지평선)->0.9D(아래), #FFC24A->#FE9C00, 은빛 반짝임 30%.
    v=1에서 행별 최고 휘도 = P7c 기둥의 85%(col_target)."""
    if v <= 0.002: return img
    m = G['meta']; sx = m['SUN_X']; wt = int(m['WATER_TOP'])
    D = 2 * SUN_R
    ys = np.arange(wt, H, dtype=np.float32)[:, None]; xs = np.arange(W, dtype=np.float32)[None]
    depth = np.clip((ys - wt) / (H - wt), 0, 1)
    wid = D * (0.5 + 0.4 * depth)
    sig = wid / 2.355
    shape = np.exp(-0.5 * ((xs - sx) / sig) ** 2)
    yw0 = int(G['yw0']); off = wt - yw0
    ph = 2 * np.pi * t / 24.0
    st = (G['STR1'] * np.cos(ph) + G['STR2'] * np.sin(ph))[off:off + (H - wt)]
    streak = np.clip(0.62 + 0.55 * st, 0.15, 1.25)
    dd = depth[:, 0] ** 0.8
    colr = hexc('#FFC24A')[None] * (1 - dd[:, None]) + hexc('#FE9C00')[None] * dd[:, None]
    T = G['col_target'][wt:H] * v
    xc = int(round(sx))
    Lb = luma(img[wt:H, xc - 3:xc + 4]).mean(1)
    Lc = luma(colr)
    a_ = np.clip((T - Lb) / np.maximum((1 - Lb) * Lc, 1e-3), 0, 1.0)
    warm = (a_[:, None] * shape * streak * 0.70)[..., None] * colr[:, None, :]
    S = G['SPK']; acc = np.zeros((H - wt, W), np.float32)
    py = wt + (S[:, 1] ** 0.85) * (H - wt)
    pd = np.clip((py - wt) / (H - wt), 0, 1)
    px = sx + S[:, 0] * (D * (0.5 + 0.4 * pd)) / 2.355 * 0.9
    tw = np.clip(np.sin(2 * np.pi * t * S[:, 3] / 2.0 + S[:, 2]), 0, 1) ** 5 * S[:, 4]
    ok = (px >= 1) & (px < W - 1) & (py >= wt) & (py < H - 1)
    np.add.at(acc, ((py[ok] - wt).astype(int), px[ok].astype(int)), tw[ok] * 7.0)
    acc = np.clip(gaussian_filter(acc, (0.8, 2.4)), 0, 1.2)
    silver = (acc * (0.30 / 0.70) * 1.6 * a_[:, None] * np.clip(shape * 1.3, 0, 1))[..., None] * hexc('#EEF2F8')[None, None]
    lay = (warm + silver) * G['water'][wt:H][..., None]
    out = img.copy()
    out[wt:H] = screen(out[wt:H], lay)
    return out

def sky_band(img, mix):
    """하늘 반사: 넓고 흐린 띠(최대 6%, 신호와 무관)."""
    m = G['meta']; wt = int(m['WATER_TOP'])
    ys = np.arange(wt, H, dtype=np.float32)[:, None]; xs = np.arange(W, dtype=np.float32)[None]
    depth = np.clip((ys - wt) / (H - wt), 0, 1)
    b = np.exp(-((xs - m['SUN_X']) / 300.) ** 2) * np.exp(-depth * 2.2) * G['water'][wt:H] * (0.06 * (0.4 + 0.6 * mix))
    out = img.copy(); out[wt:H] = screen(out[wt:H], b[..., None] * hexc('#F6B98A')[None, None]); return out

def vhs_v3(img, t, rng, strength=1.0):
    out = img.copy()
    jy = int(rng.choice([-2, -1, 1, 2])) if strength > 0.5 else 0
    if jy: out = np.roll(out, jy, 0)
    yy = np.arange(H, dtype=np.float32)
    rows = gaussian_filter(rng.normal(0, 1, H), 2) * 1.6 * strength
    bands = np.zeros(H, np.float32)
    for (hgt, speed, phase, push) in ((84, 61, 0, 1), (64, 47, 900, -1)):
        yc = (H + 200) - ((t * speed + phase) % (H + 400))
        bm = sstep((hgt / 2 - np.abs(yy - yc)) / 6.0) * strength
        shift = push * rng.uniform(12, 20) + rng.normal(0, 2.5, H)
        rows = rows + bm * shift
        bands = np.maximum(bands, bm)
    R = _shift_rows(out[..., 0], rows + 5 * strength); Bc = _shift_rows(out[..., 2], rows - 5 * strength); Gc = _shift_rows(out[..., 1], rows)
    o2 = np.stack([R, Gc, Bc], -1)
    Yo = luma(o2)[..., None]
    o2 = Yo + gaussian_filter(o2 - Yo, (0, 3.0, 0)) * 0.9
    nz = rng.random((H, W)).astype(np.float32)
    streak = gaussian_filter((nz > 0.985).astype(np.float32) * bands[:, None], (0.5, 6))
    o2 = o2 + (streak * 1.4 + (nz - 0.5) * 0.12 * bands[:, None])[..., None]
    o2[1::2] *= (1 - 0.12 * strength)
    hs = 24
    o2[-hs:] = np.roll(o2[-hs:], int(rng.integers(10, 30)), 1) * 0.8 + rng.random((hs, W, 1)).astype(np.float32) * 0.15
    Yo = luma(o2)[..., None]
    o2 = Yo + (o2 - Yo) * (1 - 0.12 * strength)
    o2 = o2 * (1 - 0.04 * strength) + 0.03 * strength
    return np.clip(o2, 0, 1).astype(np.float32)

def render_frame_v3(clip, f, sig=True):
    init()
    from scipy.special import erfc
    if 'gran' not in G:
        G['gran'] = np.load(os.path.join(B, 'gran.npy')); G['col_target'] = np.load(os.path.join(B, 'col_target.npy'))
    t_glob = (360 if clip == 'C07' else 542) + f
    rng = np.random.default_rng(1000 * (1 if clip == 'C07' else 2) + f)
    mix, trip, ev, vst = clip_plate_params(clip, f)
    H7 = G['H7']; ry = G['meta']['RIDGE_Y']; D = 2 * SUN_R
    sfun0 = sun_state_C07 if clip == 'C07' else sun_state_C10
    def sfun(ff, tt):
        p = list(sfun0(ff, tt))
        dist = abs(p[1] - ry)
        p[3] = p[3] * (1 - 0.04 * (1 - sstep((dist - 0.6 * D) / 20.0)))
        return p
    samples = [f + (i + 0.5) / 8 * 0.5 - 0.25 for i in range(8)]
    def sun_at(ff):
        fi = int(math.floor(ff)); fr = ff - fi
        a = sfun(fi, t_glob - f + fi); b = sfun(fi + 1, t_glob - f + fi + 1)
        return [lerp(a[i], b[i], fr) for i in range(5)]
    poses = [sun_at(s) for s in samples]
    spread = max(abs(p[1] - poses[0][1]) + abs(p[0] - poses[0][0]) for p in poses)
    if spread < 0.4: poses = [sfun(f, t_glob)[:5]]
    st = sfun(f, t_glob)[5]
    core_p, core_a, corona = sun_sprite_v3(t_glob, st)
    cys = [p[1] for p in poses]; half = 250
    box = (max(0, int(poses[0][0] - half)), max(0, int(min(cys) - half)), min(W, int(poses[0][0] + half) + 1), min(H, int(max(cys) + half) + 1))
    acc = None
    for (cx, cy, sxk, syk, rot) in poses:
        o = place([core_p[..., 0], core_p[..., 1], core_p[..., 2], core_a, corona[..., 0], corona[..., 1], corona[..., 2]], cx, cy, sxk, syk, rot, box)
        acc = o if acc is None else [x + y for x, y in zip(acc, o)]
    acc = [x / len(poses) for x in acc]
    x0, y0, x1, y1 = box
    Pc = np.stack(acc[:3], -1); Ac = acc[3]; Cor = np.stack(acc[4:], -1)
    Hb = H7[y0:y1, x0:x1]
    vis = min(1.0, float((Ac * (1 - Hb)).sum() / (math.pi * SUN_R ** 2)))
    v = vis if sig else 0.0
    bg = plate(mix, trip, ev)
    bg = sky_band(bg, mix)
    if sig: bg = horizon_glow(bg, vis)
    comp = bg.copy()
    msky = bg[480:800, 100:420].reshape(-1, 3)
    Ls = float(luma(bg[480:800, 100:420]).mean())
    La, Lb = G['_La'] if '_La' in G else G.setdefault('_La', (float(luma(G['P7a'][480:800, 100:420]).mean()), float(luma(G['P7b'][480:800, 100:420]).mean())))
    cover = float(np.clip(0.18 + 0.12 * (Ls - La) / (Lb - La), 0.08, 0.35))
    sky_col = msky.mean(0)
    mclip = 'C07' if clip == 'C07' else 'C10'
    mcx, mcy, _, _, mrot, mst = moon_state(mclip, f, t_glob)
    rim_dir = math.atan2(ry - 60 - mcy, G['meta']['SUN_X'] - mcx) - mrot
    mp, ma = moon_sprite(mst, cover, sky_col, v, rim_dir)
    def moon_at(ff):
        fi = int(math.floor(ff)); fr = ff - fi
        a = moon_state(mclip, fi, t_glob - f + fi); b = moon_state(mclip, fi + 1, t_glob - f + fi + 1)
        return [lerp(a[i], b[i], fr) for i in range(5)]
    mposes = [moon_at(s) for s in samples]
    mspread = max(abs(p[1] - mposes[0][1]) + abs(p[0] - mposes[0][0]) + 100 * abs(p[4] - mposes[0][4]) for p in mposes)
    if mspread < 0.4: mposes = [[mcx, mcy, 1, 1, mrot]]
    mbox = clipbox(mcx, mcy, 300); macc = None
    for (cx, cy, a_, b_, rot) in mposes:
        o = place([mp[..., 0], mp[..., 1], mp[..., 2], ma], cx, cy, 1, 1, rot, mbox)
        macc = o if macc is None else [x + y for x, y in zip(macc, o)]
    macc = [x / len(mposes) for x in macc]
    mx0, my0, mx1, my1 = mbox
    yy, xx = np.mgrid[my0:my1, mx0:mx1].astype(np.float32)
    d = np.hypot(xx - mcx, yy - mcy)
    mcol = np.array([0.95, 0.92, 0.82]) * (1 - cover) + sky_col * cover
    g1 = 0.5 * erfc((d - 100) / (30 * 1.4142)) * 0.35
    g2 = 0.5 * erfc((d - 160) / (80 * 1.4142)) * 0.20
    reg = comp[my0:my1, mx0:mx1]
    reg[:] = screen(reg, g1[..., None] * mcol[None, None] + g2[..., None] * hexc('#F3E9C6')[None, None] * 0.9)
    reg[:] = reg * (1 - macc[3][..., None]) + np.stack(macc[:3], -1)
    yy, xx = G['_yx'] if '_yx' in G else G.setdefault('_yx', np.mgrid[0:H, 0:W].astype(np.float32))
    gcx = float(np.mean([p[0] for p in poses])); gcy = float(np.mean(cys))
    syk_m = float(np.mean([p[3] for p in poses]))
    d = np.hypot(xx - gcx, (yy - gcy) / max(syk_m, 0.5))
    glow = 0.40 * 0.5 * erfc((d - SUN_R) / (40 * 1.4142)) + 0.20 * 0.5 * erfc((d - SUN_R) / (120 * 1.4142))
    if '_bleed3' not in G:
        below = np.maximum(yy - G['ridge_out'][None, :], 0)
        G['_bleed3'] = ((1 - H7) + H7 * 0.25 * np.clip(1 - below / 24.0, 0, 1) ** 1.5).astype(np.float32)
    kv = min(1.0, vis * 1.25)
    comp = screen(comp, (glow * kv * G['_bleed3'])[..., None] * hexc('#FFC24A')[None, None])
    reg = comp[y0:y1, x0:x1]
    sun_rgb = Pc / np.maximum(Ac, 1e-4)[..., None]
    ys = np.arange(y0, y1, dtype=np.float32)[:, None]
    R_eff = SUN_R * syk_m
    wb = sstep((ys - (gcy + 0.35 * R_eff)) / (0.30 * R_eff))
    sun_rgb = l2s(s2l(sun_rgb) * (2 ** (-0.4 * wb))[..., None])
    sun_rgb = sun_rgb * (1 - 0.40 * wb[..., None]) + hexc('#F08A00')[None, None] * (luma(sun_rgb)[..., None] / 0.52) * 0.40 * wb[..., None]
    Av = Ac * (1 - Hb)
    reg[:] = reg * (1 - Av[..., None]) + np.clip(sun_rgb, 0, 1) * Av[..., None]
    ca = np.clip(Cor[..., 0], 0, 1) * (1 - Hb)
    ccol = Cor / np.maximum(Cor[..., :1], 1e-3)
    reg[:] = reg * (1 - 0.9 * ca[..., None]) + ccol * 0.9 * ca[..., None]
    if sig:
        comp = signal_column(comp, v, t_glob, mix)
        comp = mist_backlight(comp, v, trip)
    if vst > 0:
        comp = vhs_v3(comp, t_glob, rng, strength=vst)
    comp = draw_osd(comp, osd_state(clip, f, rng), rng)
    return np.clip(comp, 0, 1), vis
