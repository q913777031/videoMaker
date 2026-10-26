"""《毛选》系列的彩色水墨主题：宣纸底 + 远山淡墨、元素边缘晕染（取代纸片投影）、水墨人物（取代纸片人）。

install() 在 maoxuan.build 中调用，只替换本系列运行时的 kit.paper / kit.figure / core.bg_image，
其他系列不受影响。人物用 Fig(..., role="elder") 指定角色造型，未指定时按 hair 推断为现代人物。
"""

import functools
import math
from contextlib import contextmanager

import numpy as np
import skia

from adler import core
from adler import kit as K
from engine import gfx
from engine.gfx import clamp01, lerp

INK = "#26241F"
INK_SOFT = "#5A564C"
RICE = "#F3EBDA"
SKIN = "#F2D6BA"
WHITE_HAIR = "#E9E6DE"

# 角色造型：dress = modern / robe / short（短褐）；top 上衣、bottom 下装为默认颜色（人物 color 覆盖 top）
ROLES = {
    "worker": dict(dress="modern", top="#6E9CC2", bottom="#3E4656", hair="short"),
    "worker_f": dict(dress="modern", top="#D98E8A", bottom="#4A4F5E", hair="long"),
    "boss": dict(dress="suit", top="#3B4250", bottom="#2E333E", hair="short", tie="#B8322A"),
    "elder": dict(dress="robe", top="#9C6B45", bottom="#7A5236", hair="white_bun", beard="white", stoop=6),
    "sage": dict(dress="robe", top="#8FA6A0", bottom="#6F8580", hair="white_hat", beard="goatee"),
    "scholar": dict(dress="robe", top="#6F8FB0", bottom="#58748F", hair="fangjin"),
    "farmer": dict(dress="short", top="#8C9A6A", bottom="#6B6650", hair="douli"),
    "hero": dict(dress="robe", top="#4F7A5E", bottom="#3E5E48", hair="toujin", beard="black"),
    "soldier": dict(dress="short", top="#7C8579", bottom="#5E665C", hair="army_cap"),
    "merchant": dict(dress="robe", top="#A4744A", bottom="#6E5038", hair="guapi"),
    "youth": dict(dress="short", top="#C98B5A", bottom="#5E5547", hair="bun"),
    "woman": dict(dress="robe", top="#C77F86", bottom="#9A5E68", hair="lady_bun"),
    "immortal": dict(dress="robe", top="#EDE6D6", bottom="#D9D0BC", hair="white_bun", beard="white", ribbon=True),
}


# ---------------------------------------------------------------- 边缘晕染图层（取代纸片投影）

@functools.lru_cache(maxsize=1)
def _noise_img() -> skia.Image:
    import cv2

    rng = np.random.default_rng(5)
    out = []
    for _ in range(2):
        a = cv2.GaussianBlur(rng.normal(0, 1, (512, 512)).astype(np.float32), (0, 0), 5)
        b = cv2.GaussianBlur(rng.normal(0, 1, (512, 512)).astype(np.float32), (0, 0), 1.5)
        v = a / (a.std() + 1e-6) + 0.45 * b / (b.std() + 1e-6)
        out.append(np.clip(128 + 40 * v, 0, 255).astype(np.uint8))
    rgba = np.dstack([out[0], out[1], np.full((512, 512), 128, np.uint8), np.full((512, 512), 255, np.uint8)])
    return skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType)


@functools.lru_cache(maxsize=1)
def _grain_img() -> skia.Image:
    """颜料沉淀纹理：深浅不一的斑驳（透明度编码），用 SrcATop 叠在色块上。"""
    import cv2

    rng = np.random.default_rng(9)
    a = cv2.GaussianBlur(rng.normal(0, 1, (768, 768)).astype(np.float32), (0, 0), 9)
    b = cv2.GaussianBlur(rng.normal(0, 1, (768, 768)).astype(np.float32), (0, 0), 1.2)
    v = a / (a.std() + 1e-6) * 0.8 + b / (b.std() + 1e-6) * 0.35
    dark = np.clip(v, 0, None)
    light = np.clip(-v, 0, None)
    alpha = np.clip(dark * 38 + light * 30, 0, 110)
    lum = np.where(v > 0, 40, 250).astype(np.float32)
    rgba = np.dstack([lum, lum * 0.97, lum * 0.9, alpha]).astype(np.uint8)
    return skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kUnpremul_AlphaType)


@functools.lru_cache(maxsize=16)
def _ink_filter(scale: float, bleed: float) -> skia.ImageFilter:
    img = _noise_img()
    noise = skia.ImageFilters.Image(img, skia.Rect.MakeWH(512, 512), skia.Rect.MakeXYWH(-1300, -1300, 2600, 2600),
                                    skia.SamplingOptions(skia.FilterMode.kLinear))
    disp = skia.ImageFilters.DisplacementMap(skia.ColorChannel.kR, skia.ColorChannel.kG, scale, noise, skia.ImageFilters.Offset(0, 0))
    m = [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, bleed, 0]
    halo = skia.ImageFilters.ColorFilter(skia.ColorFilters.Matrix(m), skia.ImageFilters.Blur(5, 5, skia.TileMode.kDecal, disp))
    return skia.ImageFilters.Merge([halo, disp])


@contextmanager
def ink_layer(c, alpha: float = 1.0, lift: float = 1.0, bounds: skia.Rect | None = None):
    """水墨图层：边缘按纸纹轻微抖动（笔触感）并向外晕开一圈淡色（水渍），不再有投影。"""
    if alpha <= 0:
        c.save()
        c.clipRect(skia.Rect.MakeWH(0, 0))
        try:
            yield
        finally:
            c.restore()
        return
    p = skia.Paint(Alphaf=clamp01(alpha))
    p.setImageFilter(_ink_filter(4.5, 0.3))
    c.saveLayer(bounds, p)
    try:
        yield
        gp = skia.Paint(Alphaf=0.18, BlendMode=skia.BlendMode.kSrcATop)
        c.drawImageRect(_grain_img(), skia.Rect.MakeXYWH(-1300, -1300, 2600, 2600),
                        skia.SamplingOptions(skia.FilterMode.kLinear), gp)
    finally:
        c.restore()


# ---------------------------------------------------------------- 宣纸底

_BG: dict = {}


def bg_image(accent: str) -> skia.Image:
    """宣纸底：暖白纸色 + 纤维 + 顶部与底部的远山淡墨 + 一抹强调色淡彩（按强调色缓存）。"""
    if accent in _BG:
        return _BG[accent]
    import cv2

    W, H = core.W, core.H
    rng = np.random.default_rng(23)
    img = np.ones((H, W, 3), np.float32) * np.array(gfx.rgb(RICE), np.float32)
    low = cv2.resize(rng.normal(0, 1, (24, 14)).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
    img += low[..., None] * np.array([3.0, 2.6, 2.0], np.float32)
    fib = rng.normal(0, 1, (H, W)).astype(np.float32)
    fib = cv2.GaussianBlur(fib, (0, 0), sigmaX=6, sigmaY=0.8) * 9 + cv2.GaussianBlur(fib, (0, 0), 0.8) * 3
    img += fib[..., None]
    xx = np.arange(W, dtype=np.float32)
    yy = np.arange(H, dtype=np.float32)[:, None]

    def ridge(base, amp, seed, freq):
        r = np.random.default_rng(seed)
        y = np.full(W, base, np.float32)
        for k in range(1, 6):
            y += amp / k * np.sin(xx * freq * k / W * 2 * math.pi + r.random() * 6)
        return y

    layers = [(1600, 110, 3, 1.3, 0.10, "#7F9A93"), (1720, 80, 8, 1.9, 0.14, "#5B7570"), (1840, 60, 13, 2.6, 0.18, INK_SOFT)]
    for base, amp, seed, freq, a, colr in layers:
        top = ridge(base, amp, seed, freq)[None, :]
        d = yy - top
        m = np.clip(d / 60, 0, 1) * np.exp(-np.clip(d, 0, None) / 200)
        m = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 6)
        colv = np.array(gfx.rgb(colr), np.float32)
        img = img * (1 - a * m[..., None]) + colv * a * m[..., None]
    for base, amp, seed, freq, a in ((150, 50, 31, 1.2, 0.06), (230, 40, 37, 2.0, 0.05)):
        bot = ridge(base, amp, seed, freq)[None, :]
        d = bot - yy
        m = np.clip(d / 40, 0, 1) * np.exp(-np.clip(d, 0, None) / 180)
        img = img * (1 - a * m[..., None]) + np.array(gfx.rgb("#7E8F8A"), np.float32) * a * m[..., None]
    acc = np.array(gfx.rgb(accent), np.float32)
    blob = np.exp(-(((xx[None, :] - W * 0.82) / (W * 0.35)) ** 2 + ((yy - H * 0.2) / (H * 0.1)) ** 2))
    img = img * (1 - 0.08 * blob[..., None]) + acc * 0.08 * blob[..., None]
    r = np.hypot((xx[None, :] - W / 2) / (W * 0.8), (yy - H * 0.46) / (H * 0.62))
    img -= (np.clip(r - 0.6, 0, 1) ** 1.6)[..., None] * np.array([30, 32, 36], np.float32)
    rgba = np.dstack([np.clip(img, 0, 255).astype(np.uint8), np.full((H, W), 255, np.uint8)])
    _BG[accent] = skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType)
    return _BG[accent]


# ---------------------------------------------------------------- 笔墨基础

def _wash(c, path, color, alpha=1.0, edge=0.3, line=0.0):
    """淡彩：一层主色 + 外圈模糊晕开 + 边缘稍深的水痕；line>0 时再勾一道淡墨轮廓。"""
    c.drawPath(path, K.paint(K.tint(color, 0.05), 0.55 * alpha, blur=6))
    c.drawPath(path, K.paint(color, 0.92 * alpha))
    if edge:
        c.drawPath(path, K.paint(K.shade(color, 0.28), edge * alpha, 3, blur=1.2))
    if line:
        c.drawPath(path, K.paint(INK, 0.5 * alpha, line, blur=0.5))


def _brush(c, pts, width, color=INK, alpha=1.0, taper=True):
    """毛笔线：沿折线由粗到细（起笔重、收笔轻），两遍叠出浓淡。"""
    n = len(pts)
    for i in range(n - 1):
        k0, k1 = i / (n - 1), (i + 1) / (n - 1)
        w0 = width * (1 - 0.55 * k0 if taper else 1)
        w1 = width * (1 - 0.55 * k1 if taper else 1)
        p = skia.Path()
        p.moveTo(*pts[i])
        p.lineTo(*pts[i + 1])
        c.drawPath(p, K.paint(color, alpha, (w0 + w1) / 2))
    if n >= 2:
        p = skia.Path()
        p.moveTo(*pts[0])
        for q in pts[1:]:
            p.lineTo(*q)
        c.drawPath(p, K.paint(color, 0.35 * alpha, width * 0.35, blur=1.5))


def _limb_shape(a, b, d, w0, w1, w2):
    """肢体轮廓：从 a 经 b 到 d 的锥形管。"""
    def norm(p, q):
        dx, dy = q[0] - p[0], q[1] - p[1]
        L = math.hypot(dx, dy) or 1
        return -dy / L, dx / L

    n1, n2 = norm(a, b), norm(b, d)
    nb = ((n1[0] + n2[0]) / 2, (n1[1] + n2[1]) / 2)
    p = skia.Path()
    p.moveTo(a[0] + n1[0] * w0, a[1] + n1[1] * w0)
    p.lineTo(b[0] + nb[0] * w1, b[1] + nb[1] * w1)
    p.lineTo(d[0] + n2[0] * w2, d[1] + n2[1] * w2)
    p.lineTo(d[0] - n2[0] * w2, d[1] - n2[1] * w2)
    p.lineTo(b[0] - nb[0] * w1, b[1] - nb[1] * w1)
    p.lineTo(a[0] - n1[0] * w0, a[1] - n1[1] * w0)
    p.close()
    return p


def _role(role, hair, color):
    if role is None:
        if hair == "cap":
            role = "soldier"
        elif hair in ("long",):
            role = "worker_f"
        else:
            role = "worker"
    spec = dict(ROLES.get(role, ROLES["worker"]))
    if color is not None and role in ("worker", "worker_f", "boss"):
        spec["top"] = color
    elif color is not None and role not in ("immortal",):
        spec["top"] = K.mix(spec["top"], color, 0.45)
    if role == "worker_f" and hair == "bun":
        spec["hair"] = "bun_modern"
    return role, spec


# ---------------------------------------------------------------- 水墨人物

def ink_figure(c, x, y, s, p="stand", color=K.HERO, head_color=SKIN, alpha=1.0, face: int = 1, mood="calm",
               hair=None, hair_color=None, bob: float = 0.0, lift: float = 1.0, look: float = 0.0, blink: bool = False,
               scarf=None, prop=None, role=None):
    """水墨人物（约七头身）：姿势、朝向、行走与 kit.figure 兼容，按 role 画服饰、发式、胡须与帽子；淡彩打底、淡墨勾线。"""
    if alpha <= 0 or s <= 0:
        return
    role, spec = _role(role, hair, color)
    d = K.pose(p)
    u = s * 1.1
    thigh, shin = 0.25 * u, 0.24 * u
    upper, fore = 0.19 * u, 0.18 * u
    lw = 0.07 * u
    line = 0.009 * u

    def leg_extent(a1, a2):
        (_, ey), (_, fy) = K._limb(0, 0, a1, a2, thigh, shin, 1)
        return max(ey, fy)

    if d["seat"] > 0:
        hip_y = -d["seat"] * u
    else:
        hip_y = -max(leg_extent(d["ll1"], d["ll2"]), leg_extent(d["rl1"], d["rl2"]))
    hip_y -= bob * u
    lean = math.radians(d["lean"] + spec.get("stoop", 0))
    torso = 0.29 * u
    sh_x = face * torso * math.sin(lean)
    sh_y = hip_y - torso * math.cos(lean)
    top, bottom = spec["top"], spec["bottom"]
    dress = spec["dress"]
    robe = dress == "robe"
    bounds = skia.Rect.MakeLTRB(x - u * 1.0, y - u * 1.3, x + u * 1.0, y + u * 0.2)
    with ink_layer(c, alpha, lift, bounds):
        c.save()
        c.translate(x, y)
        hips = [(-0.035 * u * face, hip_y), (0.035 * u * face, hip_y)]
        shoulders = [(sh_x - 0.09 * u * face, sh_y + 0.025 * u), (sh_x + 0.09 * u * face, sh_y + 0.025 * u)]
        k_r, f_r = K._limb(*hips[0], d["rl1"], d["rl2"], thigh, shin, face)
        k_l, f_l = K._limb(*hips[1], d["ll1"], d["ll2"], thigh, shin, face)
        e_r, h_r = K._limb(*shoulders[0], d["ra1"], d["ra2"], upper, fore, face)
        e_l, h_l = K._limb(*shoulders[1], d["la1"], d["la2"], upper, fore, face)

        if spec.get("ribbon"):
            rp = skia.Path()
            rp.moveTo(sh_x - 0.15 * u * face, sh_y)
            rp.cubicTo(sh_x - 0.55 * u * face, sh_y + 0.1 * u, -0.45 * u * face, hip_y + 0.2 * u, -0.7 * u * face,
                       hip_y + 0.05 * u)
            c.drawPath(rp, K.paint("#9DB8C9", 0.8, 0.03 * u))

        legc = K.shade(bottom, 0.18)
        if robe:
            c.drawPath(_limb_shape(hips[0], k_r, f_r, lw * 0.8, lw * 0.7, lw * 0.6), K.paint(legc, 0.9))
        else:
            _wash(c, _limb_shape(hips[0], k_r, f_r, lw * 0.6, lw * 0.5, lw * 0.42), legc, 1, 0.2, line)
        _shoe(c, f_r, face, lw)
        _arm(c, shoulders[0], e_r, h_r, K.shade(top, 0.18), lw, robe, far=True, line=line)
        if robe:
            hem_y = max(f_r[1], f_l[1]) - 0.05 * u
            mid = (f_r[0] + f_l[0]) / 2
            spread = min(abs(f_r[0] - f_l[0]) / 2, 0.07 * u) + 0.13 * u
            rp = skia.Path()
            rp.moveTo(-0.1 * u, hip_y - 0.03 * u)
            rp.quadTo(mid - spread * 0.75, (hip_y + hem_y) / 2, mid - spread, hem_y)
            rp.quadTo(mid, hem_y + 0.025 * u, mid + spread, hem_y)
            rp.quadTo(mid + spread * 0.75, (hip_y + hem_y) / 2, 0.1 * u, hip_y - 0.03 * u)
            rp.close()
            _wash(c, rp, bottom, 1, 0.35, line)
            for k_ in (-0.3, 0.05, 0.4):
                _brush(c, [(mid + spread * k_ * 0.5, hip_y + 0.06 * u), (mid + spread * k_, hem_y - 0.02 * u)],
                       0.008 * u, K.shade(bottom, 0.45), 0.55)
        else:
            _wash(c, _limb_shape(hips[1], k_l, f_l, lw * 0.62, lw * 0.52, lw * 0.44), bottom, 1, 0.3, line)
        _shoe(c, f_l, face, lw)
        # 躯干
        nx = math.cos(lean)
        bw, tw = (0.1 * u, 0.115 * u) if robe else (0.085 * u, 0.11 * u)
        tp = skia.Path()
        tp.moveTo(-bw * nx, hip_y + 0.04 * u)
        tp.lineTo(sh_x - tw * nx, sh_y + 0.04 * u)
        tp.quadTo(sh_x - tw * nx, sh_y - 0.01 * u, sh_x - 0.03 * u, sh_y - 0.015 * u)
        tp.lineTo(sh_x + 0.03 * u, sh_y - 0.015 * u)
        tp.quadTo(sh_x + tw * nx, sh_y - 0.01 * u, sh_x + tw * nx, sh_y + 0.04 * u)
        tp.lineTo(bw * nx, hip_y + 0.04 * u)
        tp.quadTo(0, hip_y + 0.07 * u, -bw * nx, hip_y + 0.04 * u)
        tp.close()
        _wash(c, tp, top, 1, 0.35, line)
        if robe:
            _brush(c, [(sh_x - 0.035 * u * face, sh_y - 0.01 * u), (sh_x + 0.03 * u * face, sh_y + 0.12 * u),
                       (0.03 * u * face, hip_y - 0.02 * u)], 0.014 * u, K.shade(top, 0.5), 0.85)
            K.seg(c, -bw * nx, hip_y - 0.02 * u, bw * nx, hip_y - 0.02 * u, K.shade(top, 0.55), 0.024 * u, 0.9)
        elif dress == "suit":
            vp = skia.Path()
            vp.moveTo(sh_x - 0.035 * u, sh_y - 0.01 * u)
            vp.lineTo(sh_x + 0.035 * u, sh_y - 0.01 * u)
            vp.lineTo(sh_x, sh_y + 0.11 * u)
            vp.close()
            c.drawPath(vp, K.paint("#F4F1EA"))
            K.seg(c, sh_x, sh_y + 0.005 * u, sh_x - 0.004 * u * face, sh_y + 0.14 * u, spec.get("tie", K.RED), 0.02 * u)
        elif dress == "modern":
            K.seg(c, sh_x - 0.03 * u, sh_y - 0.01 * u, sh_x, sh_y + 0.03 * u, K.shade(top, 0.45), 0.01 * u, 0.85)
            K.seg(c, sh_x + 0.03 * u, sh_y - 0.01 * u, sh_x, sh_y + 0.03 * u, K.shade(top, 0.45), 0.01 * u, 0.85)
        else:
            K.seg(c, -bw * nx, hip_y - 0.02 * u, bw * nx, hip_y - 0.02 * u, K.shade(top, 0.5), 0.018 * u, 0.85)
            _brush(c, [(sh_x, sh_y), (sh_x + 0.01 * u * face, hip_y - 0.03 * u)], 0.008 * u, K.shade(top, 0.45), 0.6)
        if scarf:
            c.drawCircle(sh_x, sh_y, 0.045 * u, K.paint(scarf))
        # 颈与头
        hd = math.radians(d["head"])
        hr = 0.1 * u
        ang = lean + hd * 0.5
        K.seg(c, sh_x, sh_y, sh_x + face * 0.05 * u * math.sin(ang), sh_y - 0.05 * u * math.cos(ang),
              head_color, 0.05 * u)
        hx = sh_x + face * (0.13 * u) * math.sin(ang)
        hy = sh_y - (0.13 * u) * math.cos(ang)
        _ink_head(c, hx, hy, hr, head_color, face, mood, spec, hair_color, d["head"], look, blink)
        _arm(c, shoulders[1], e_l, h_l, top, lw, robe, far=False, skin=head_color, line=line)
        if prop:
            prop(c, h_l)
        c.restore()


def _shoe(c, f, face, lw):
    p = skia.Path()
    p.moveTo(f[0] - face * lw * 0.3, f[1] - lw * 0.08)
    p.quadTo(f[0] + face * lw * 0.4, f[1] - lw * 0.32, f[0] + face * lw * 0.8, f[1])
    p.lineTo(f[0] - face * lw * 0.3, f[1] + lw * 0.06)
    p.close()
    c.drawPath(p, K.paint(INK, 0.92))


def _arm(c, sh, e, h, colr, lw, robe, far, skin=SKIN, line=2.0):
    if robe:
        shape = _limb_shape(sh, e, h, lw * 0.55, lw * 0.7, lw * 0.9)
        _wash(c, shape, colr, 1, 0.3, line)
        # 下垂的宽袖口
        cuff = skia.Path()
        cuff.moveTo(h[0] - lw * 0.7, h[1] - lw * 0.2)
        cuff.quadTo(h[0], h[1] + lw * 1.3, h[0] + lw * 0.7, h[1] - lw * 0.2)
        cuff.close()
        c.drawPath(cuff, K.paint(colr, 0.85))
    else:
        _wash(c, _limb_shape(sh, e, h, lw * 0.48, lw * 0.42, lw * 0.36), colr, 1, 0.3, line)
    K.dot(c, h[0], h[1], lw * 0.4, K.shade(skin, 0.15) if far else skin)


def _ink_head(c, x, y, r, skin, face, mood, spec, hair_color, tilt, look, blink):
    style = spec["hair"]
    with K.at(c, x, y, tilt * 0.35 * face):
        hc = hair_color or INK
        if style in ("long",):
            hp = skia.Path()
            hp.addRoundRect(skia.Rect.MakeXYWH(-r * 1.05 - face * r * 0.2, -r * 1.0, r * 2.1, r * 2.1), r, r)
            c.drawPath(hp, K.paint(hc, 0.9))
        # 脸
        c.drawCircle(0, 0, r, K.paint(K.tint(skin, 0.1), 0.5, blur=4))
        c.drawCircle(0, 0, r, K.paint(skin))
        arc = skia.Path()
        arc.addArc(skia.Rect.MakeXYWH(-r, -r, 2 * r, 2 * r), 40 if face > 0 else -40 + 180, 120)
        c.drawPath(arc, K.paint(K.shade(skin, 0.35), 0.7, r * 0.06))
        # 胡须
        beard = spec.get("beard")
        if beard:
            bc = WHITE_HAIR if beard == "white" else INK
            bp = skia.Path()
            bx = face * r * 0.35
            if beard == "goatee":
                bp.moveTo(bx - r * 0.25, r * 0.55)
                bp.quadTo(bx, r * 1.6, bx + r * 0.25, r * 0.55)
            else:
                bp.moveTo(bx - r * 0.7, r * 0.25)
                bp.quadTo(bx - r * 0.3, r * 1.9, bx + face * r * 0.1, r * 2.2)
                bp.quadTo(bx + r * 0.4, r * 1.5, bx + r * 0.75, r * 0.2)
                bp.quadTo(bx, r * 0.7, bx - r * 0.7, r * 0.25)
            bp.close()
            c.drawPath(bp, K.paint(bc, 0.95))
            c.drawPath(bp, K.paint(INK_SOFT, 0.5, r * 0.04))
        # 发 / 帽
        _hair(c, r, face, style, hc)
        # 五官（工笔小点）
        ex = face * r * 0.4
        ey = r * 0.02 - look * r * 0.12
        gap = r * 0.38
        for k, sx in enumerate((ex - gap / 2, ex + gap / 2)):
            if blink or mood == "happy":
                pth = skia.Path()
                pth.addArc(skia.Rect.MakeXYWH(sx - r * 0.1, ey - r * 0.06, r * 0.2, r * 0.16), 200, 140)
                c.drawPath(pth, K.paint(INK, 1, r * 0.06))
            else:
                rr = r * (0.09 if mood == "surprised" else 0.065)
                c.drawOval(skia.Rect.MakeXYWH(sx - rr, ey - rr * 1.2, rr * 2, rr * 2.4), K.paint(INK))
            brow_tilt = {"angry": 0.08, "worried": -0.06, "sad": -0.07}.get(mood, 0.0) * r * (1 if k == 0 else -1)
            K.seg(c, sx - r * 0.11, ey - r * 0.22 + brow_tilt, sx + r * 0.11, ey - r * 0.22 - brow_tilt,
                  WHITE_HAIR if beard == "white" else INK, r * 0.05, 0.9)
        mx, my = ex, r * 0.45 - look * r * 0.05
        if not (beard and beard != "goatee"):
            if mood in ("smile", "happy"):
                pth = skia.Path()
                pth.addArc(skia.Rect.MakeXYWH(mx - r * 0.17, my - r * 0.18, r * 0.34, r * 0.26), 20, 140)
                c.drawPath(pth, K.paint("#9C3B2E", 1, r * 0.06))
            elif mood in ("sad", "worried"):
                pth = skia.Path()
                pth.addArc(skia.Rect.MakeXYWH(mx - r * 0.14, my + r * 0.02, r * 0.28, r * 0.2), 200, 140)
                c.drawPath(pth, K.paint(INK, 1, r * 0.055))
            elif mood in ("open", "surprised"):
                c.drawOval(skia.Rect.MakeXYWH(mx - r * 0.07, my - r * 0.06, r * 0.14, r * 0.18), K.paint("#7A2E24"))
            else:
                K.seg(c, mx - r * 0.1, my, mx + r * 0.1, my, "#7A2E24", r * 0.05)
        if mood in ("happy", "smile", "calm", "open"):
            c.drawCircle(mx - face * r * 0.38, my - r * 0.18, r * 0.12, K.paint("#E07A6A", 0.22, blur=3))


def _hair(c, r, face, style, hc):
    def cap_arc(color, a=1.0, lower=0.0):
        pth = skia.Path()
        pth.addArc(skia.Rect.MakeXYWH(-r * 1.06, -r * 1.12, r * 2.12, r * 2.0), 180, 180)
        pth.cubicTo(r * 0.7 * face, -r * 0.45, r * 0.1 * face, -r * 0.75, -r * 0.35 * face, -r * 0.5)
        pth.quadTo(-r * 0.8 * face, -r * 0.3, -r * 1.06 * face, r * 0.1)
        pth.close()
        c.drawPath(pth, K.paint(color, a))

    if style in ("short", "long", "bun", "bun_modern"):
        cap_arc(hc, 0.95)
        _brush(c, [(-face * r * 0.9, -r * 0.4), (-face * r * 0.2, -r * 0.95), (face * r * 0.6, -r * 0.7)], r * 0.08,
               INK, 0.5)
        if style in ("bun", "bun_modern"):
            c.drawCircle(-face * r * 0.5 if style == "bun_modern" else 0, -r * 1.05, r * 0.34, K.paint(hc))
            if style == "bun":
                K.seg(c, -r * 0.5, -r * 1.1, r * 0.5, -r * 1.0, "#C9A24A", r * 0.06)
    elif style == "white_bun":
        cap_arc(WHITE_HAIR, 1)
        c.drawCircle(0, -r * 1.05, r * 0.32, K.paint(WHITE_HAIR))
        c.drawCircle(0, -r * 1.05, r * 0.32, K.paint(INK_SOFT, 0.6, r * 0.04))
        K.seg(c, -r * 0.45, -r * 1.08, r * 0.45, -r * 1.0, "#8A6A3A", r * 0.06)
    elif style == "white_hat":
        cap_arc(WHITE_HAIR, 1)
        K.rr(c, 0, -r * 1.05, r * 1.3, r * 0.55, r * 0.15, "#3A3F44")
        K.seg(c, -r * 0.9, -r * 0.85, r * 0.9, -r * 0.85, "#3A3F44", r * 0.09)
    elif style == "fangjin":
        cap_arc(hc, 0.95)
        K.rr(c, 0, -r * 1.0, r * 1.5, r * 0.75, r * 0.12, "#2F3A4A")
        K.seg(c, -face * r * 0.75, -r * 0.8, -face * r * 1.25, -r * 0.2, "#2F3A4A", r * 0.12)
    elif style == "douli":
        cap_arc(hc, 0.95)
        pth = skia.Path()
        pth.moveTo(-r * 1.75, -r * 0.45)
        pth.lineTo(0, -r * 1.55)
        pth.lineTo(r * 1.75, -r * 0.45)
        pth.quadTo(0, -r * 0.62, -r * 1.75, -r * 0.45)
        pth.close()
        _wash(c, pth, "#C9A86A", 1, 0.5)
        for i in range(-3, 4):
            K.seg(c, 0, -r * 1.5, i * r * 0.45, -r * 0.55, K.shade("#C9A86A", 0.3), r * 0.03, 0.7)
    elif style == "toujin":
        cap_arc(hc, 0.95)
        pth = skia.Path()
        pth.addArc(skia.Rect.MakeXYWH(-r * 1.08, -r * 1.2, r * 2.16, r * 1.6), 180, 180)
        pth.close()
        c.drawPath(pth, K.paint("#2E3B33"))
        _brush(c, [(-face * r * 0.9, -r * 0.6), (-face * r * 1.4, -r * 0.1), (-face * r * 1.6, r * 0.4)], r * 0.16,
               "#2E3B33", 0.9, taper=True)
    elif style == "army_cap":
        cap_arc(hc, 0.95)
        pth = skia.Path()
        pth.addArc(skia.Rect.MakeXYWH(-r * 1.1, -r * 1.3, r * 2.2, r * 1.6), 180, 180)
        pth.close()
        _wash(c, pth, "#7C8579", 1, 0.5)
        K.rr(c, face * r * 0.45, -r * 0.48, r * 1.0, r * 0.2, r * 0.1, K.shade("#7C8579", 0.4))
    elif style == "guapi":
        cap_arc(hc, 0.95)
        pth = skia.Path()
        pth.addArc(skia.Rect.MakeXYWH(-r * 1.02, -r * 1.12, r * 2.04, r * 1.4), 180, 180)
        pth.close()
        c.drawPath(pth, K.paint("#2B2A28"))
        K.dot(c, 0, -r * 1.14, r * 0.12, K.RED)
    elif style == "lady_bun":
        cap_arc(hc, 0.95)
        c.drawOval(skia.Rect.MakeXYWH(-r * 0.75, -r * 1.65, r * 1.5, r * 0.8), K.paint(hc))
        K.dot(c, face * r * 0.55, -r * 1.25, r * 0.12, "#C9A24A")


# ---------------------------------------------------------------- 安装

def ink_ground(c, y, alpha=1.0, color=None, x0=60, x1=None):
    """地面：一笔淡墨横扫（两头飞白），代替纸条地平线。"""
    x1 = core.W - 60 if x1 is None else x1
    p = skia.Path()
    p.moveTo(x0, y + 8)
    p.cubicTo(x0 + (x1 - x0) * 0.3, y - 4, x0 + (x1 - x0) * 0.7, y + 14, x1, y + 4)
    c.drawPath(p, K.paint("#8A8270", 0.35 * alpha, 22, blur=5))
    c.drawPath(p, K.paint(INK_SOFT, 0.55 * alpha, 6, blur=0.8))
    for i in range(6):
        xx = lerp(x0 + 40, x1 - 40, i / 5)
        K.seg(c, xx, y + 14, xx + 50, y + 18, "#8A9A70", 4, 0.4 * alpha)


def install():
    """把本系列的绘制切换为彩色水墨风（只影响当前进程）：水墨图层、水墨人物、宣纸底、淡墨地面、毛笔字（大字与弹字）。"""
    K.paper = ink_layer
    K.figure = ink_figure
    K.ground = ink_ground
    core.bg_image = bg_image
    gfx.FONT_FILES["serif_black"] = "MaShanZheng-Regular.ttf"
