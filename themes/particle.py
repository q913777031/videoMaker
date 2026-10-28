"""粒子风主题：深空底，舞台上的一切（人物、图形、大字）都由发光粒子组成；切镜时粒子从四散处飞来聚合成画面，
重拍（镜头 shake 拍）时粒子向外炸开再收回；页眉与字幕保持清晰，改为霓虹色。

实现：每帧先按原样（浅色底）画出整帧与只含舞台的帧，把舞台按 6px 网格采样成粒子（颜色提亮为霓虹色），
加上位移后累加到画布并做两级模糊（粒子本体 + 辉光），叠在深空底上。install() 只影响当前进程。
"""

import functools
import math

import numpy as np
import skia

from adler import core

STEP = 5
TOP, BOTTOM = 320, 1280


@functools.lru_cache(maxsize=4)
def _dark_bg() -> np.ndarray:
    import cv2

    W, H = core.W, core.H
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    t = (yy / H)[..., None]
    img = np.array([10, 14, 32], np.float32) * (1 - t) + np.array([22, 12, 40], np.float32) * t
    glow = np.exp(-(((xx - W / 2) / (W * 0.6)) ** 2 + ((yy - H * 0.42) / (H * 0.3)) ** 2))
    img += glow[..., None] * np.array([18, 30, 60], np.float32)
    rng = np.random.default_rng(2)
    stars = np.zeros((H, W), np.float32)
    idx = rng.integers(0, H * W, 900)
    stars.flat[idx] = rng.random(900) * 255
    stars = cv2.GaussianBlur(stars, (0, 0), 0.8) * 2.5
    img += stars[..., None] * np.array([0.6, 0.7, 1.0], np.float32)
    return np.clip(img, 0, 255)


def _neon(rgb: np.ndarray) -> np.ndarray:
    """把浅底上的颜色转成深底上的霓虹色：低饱和的深色（墨色）变青白，彩色提亮到满亮度。"""
    mx = rgb.max(-1, keepdims=True)
    mn = rgb.min(-1, keepdims=True)
    sat = (mx - mn) / np.maximum(mx, 1)
    bright = rgb / np.maximum(mx, 1) * 255
    cyan = np.array([150, 225, 255], np.float32)
    dim = np.array([38, 58, 104], np.float32)
    v = mx / 255.0
    gray = cyan * (1 - v) + dim * v              # 灰阶反相：深色（墨字）→ 亮青，浅色（纸卡）→ 暗蓝
    k = np.clip((sat - 0.12) / 0.2, 0, 1)
    return bright * k + gray * (1 - k)


@functools.lru_cache(maxsize=1)
def _clear_img() -> skia.Image:
    return skia.Image.fromarray(np.zeros((core.H, core.W, 4), np.uint8), colorType=skia.kRGBA_8888_ColorType)


def _snapshot(fn) -> tuple[np.ndarray, np.ndarray]:
    """在透明底上绘制，返回（去预乘的 RGB，alpha 0–1）。"""
    surf = skia.Surface.MakeRaster(skia.ImageInfo.Make(core.W, core.H, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType))
    saved = core.bg_image
    core.bg_image = lambda accent: _clear_img()
    try:
        fn(surf.getCanvas())
    finally:
        core.bg_image = saved
    arr = surf.makeImageSnapshot().toarray().astype(np.float32)
    a = arr[..., 3:4] / 255.0
    return arr[..., :3] / np.maximum(a, 1e-3), a[..., 0]


@functools.lru_cache(maxsize=1)
def _grid():
    ys = np.arange(TOP + STEP // 2, BOTTOM, STEP)
    xs = np.arange(STEP // 2, core.W, STEP)
    gy, gx = np.meshgrid(ys, xs, indexing="ij")
    rng = np.random.default_rng(7)
    ang = rng.random(gy.shape) * 2 * np.pi
    rad = 250 + rng.random(gy.shape) * 650
    return gy, gx, np.cos(ang) * rad, np.sin(ang) * rad, rng.random(gy.shape)


def _particles(B, aB, T, a=0.0, burst=0.0) -> np.ndarray:
    """舞台（透明底 RGB + alpha）→ 粒子层 RGB（加色用）：粒子本体 + 辉光 + 聚合后的清晰霓虹轮廓。"""
    import cv2

    gy, gx, nx, ny, ph = _grid()
    Bs = B[gy, gx]
    m = np.clip(aB[gy, gx] * 1.3 - 0.15, 0, 1)
    wob = 3.0 * np.sin(T * 3 + ph * 6.28)
    py = gy + ny * a + (gy - 780) * 0.25 * burst + wob
    px = gx + nx * a + (gx - 540) * 0.25 * burst + wob * 0.6
    sel = m > 0.05
    py, px = py[sel].astype(np.int32), px[sel].astype(np.int32)
    ok = (py >= 0) & (py < core.H) & (px >= 0) & (px < core.W)
    col = _neon(Bs[sel])[ok] * m[sel][ok, None]
    acc = np.zeros((core.H, core.W, 3), np.float32)
    np.add.at(acc, (py[ok], px[ok]), col)
    out = cv2.GaussianBlur(acc, (0, 0), 1.3) * 5.6 + cv2.GaussianBlur(acc, (0, 0), 9) * 4.5
    mB = np.clip(aB[TOP:BOTTOM, :, None] * 1.3 - 0.15, 0, 1)
    out[TOP:BOTTOM] += _neon(B[TOP:BOTTOM]) * mB * 0.55 * (1 - a) * (1 - 0.6 * burst)
    return out


LIGHT = dict(INK="#EAF4FF", INK2="#AFC9E6", INK3="#7891B4")


@functools.lru_cache(maxsize=1)
def _dark_img() -> skia.Image:
    d = _dark_bg()
    rgba = np.dstack([d.astype(np.uint8), np.full((core.H, core.W), 255, np.uint8)])
    return skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType)


def install(B=None):
    """切换为粒子风（只影响当前进程）。传入 adler.build 时，单讲横屏封面、合集图与系列横屏封面也切换为粒子风。"""
    import cv2
    from contextlib import contextmanager

    from adler import fx
    from adler import kit as K

    from maoxuan import ink

    ink.install()                       # 元件先按水墨主题绘制，再整体粒子化
    orig = core.draw_frame
    orig_shot = core._draw_shot
    dark_colors = {k: getattr(K, k) for k in LIGHT}

    def plain(cc, ep, T, caption, ui):
        """与 core.draw_frame 相同，但不画闪白与首尾淡入淡出（它们会让整块舞台被当成内容）。"""
        cc.drawImage(core.bg_image(ep.accent), 0, 0)
        k = ep.shot_at(T)
        s = ep.shots[k]
        g = orig_shot(cc, ep, k, T - s.t0)
        if caption:
            core.draw_caption(cc, ep, s, g)
        if ui:
            core.draw_header(cc, ep, s, T, g)
            core.draw_progress(cc, ep, T)
        return g

    def draw_frame(c, ep, T, caption=True, ui=True):
        holder = {}
        A, aA = _snapshot(lambda cc: holder.setdefault("g", plain(cc, ep, T, caption, ui)))
        B_, aB = _snapshot(lambda cc: plain(cc, ep, T, False, False))
        k = ep.shot_at(T)
        s = ep.shots[k]
        t = T - s.t0
        a = (1 - min(1.0, t / 0.5)) ** 2 if k > 0 else 0.0
        burst = 0.0
        for it in s.shake:
            kb = it[0] if isinstance(it, tuple) else it
            dt = T - core.bt(s.b0 + kb)
            if dt >= 0:
                burst = max(burst, math.exp(-dt * 5) * math.sin(min(dt * 9, math.pi)))
        out = _dark_bg() + _particles(B_, aB, T, a, burst)
        for y0, y1 in ((0, TOP), (BOTTOM, core.H)):
            band = A[y0:y1]
            mb = aA[y0:y1, :, None]
            out[y0:y1] = out[y0:y1] * (1 - mb) + _neon(band) * mb
            out[y0:y1] += cv2.GaussianBlur(_neon(band) * mb, (0, 0), 6) * 0.35
        g = holder["g"]
        fl = 0.0
        for it in s.flashes:
            kb, pk = it if isinstance(it, tuple) else (it, 0.55)
            fl = max(fl, fx.flash_alpha(g.since(kb), pk))
        if fl > 0:
            out += np.array([170, 230, 255], np.float32) * fl * 0.5
        fade = max(1 - min(1.0, T / 0.4), min(1.0, max(0.0, (T - (core.END - 1.2)) / 1.1)))
        out *= 1 - fade
        rgba = np.dstack([np.clip(out, 0, 255).astype(np.uint8), np.full((core.H, core.W), 255, np.uint8)])
        c.drawImage(skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType), 0, 0)

    def particle_shot(c, ep, k, t):
        """封面用：把该镜头该时刻的舞台画成粒子，加色叠在当前画布上（坐标与原舞台一致）。"""
        saved = {n: getattr(K, n) for n in LIGHT}
        for n, v in dark_colors.items():
            setattr(K, n, v)
        try:
            B_, aB = _snapshot(lambda cc: orig_shot(cc, ep, k, t))
        finally:
            for n, v in saved.items():
                setattr(K, n, v)
        rgb = _particles(B_, aB, ep.shots[k].t0 + t)
        rgba = np.dstack([np.clip(rgb, 0, 255).astype(np.uint8), np.full((core.H, core.W), 255, np.uint8)])
        c.drawImage(skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType), 0, 0,
                    skia.SamplingOptions(), skia.Paint(BlendMode=skia.BlendMode.kPlus))
        return core.G(c, ep, ep.shots[k], t)

    @contextmanager
    def cover_mode():
        saved = (core.bg_image, core._draw_shot, {n: getattr(K, n) for n in LIGHT})
        core.bg_image = lambda accent: _dark_img()
        core._draw_shot = particle_shot
        for n, v in LIGHT.items():
            setattr(K, n, v)
        try:
            yield
        finally:
            core.bg_image, core._draw_shot = saved[0], saved[1]
            for n, v in saved[2].items():
                setattr(K, n, v)

    def wrap(mod, name):
        fn = getattr(mod, name)

        def inner(*args, **kw):
            with cover_mode():
                return fn(*args, **kw)

        setattr(mod, name, inner)

    core.draw_frame = draw_frame
    wrap(core, "cover")
    if B is not None:
        for name in ("episode_square", "collage", "square_cover"):
            wrap(B, name)
