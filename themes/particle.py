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


def install(base_bg=None):
    """切换为粒子风（只影响当前进程）。"""
    import cv2

    orig = core.draw_frame

    def draw_frame(c, ep, T, caption=True, ui=True):
        A, aA = _snapshot(lambda cc: orig(cc, ep, T, caption, ui))
        B, aB = _snapshot(lambda cc: orig(cc, ep, T, False, False))
        out = _dark_bg().copy()
        # 舞台 → 粒子
        gy, gx, nx, ny, ph = _grid()
        Bs = B[gy, gx]
        m = np.clip(aB[gy, gx] * 1.3 - 0.15, 0, 1)
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
        wob = 3.0 * np.sin(T * 3 + ph * 6.28)
        py = gy + ny * a + (gy - 780) * 0.25 * burst + wob
        px = gx + nx * a + (gx - 540) * 0.25 * burst + wob * 0.6
        sel = m > 0.05
        py, px = py[sel].astype(np.int32), px[sel].astype(np.int32)
        ok = (py >= 0) & (py < core.H) & (px >= 0) & (px < core.W)
        col = _neon(Bs[sel])[ok] * m[sel][ok, None]
        acc = np.zeros((core.H, core.W, 3), np.float32)
        np.add.at(acc, (py[ok], px[ok]), col)
        dots = cv2.GaussianBlur(acc, (0, 0), 1.3) * 7.0
        glow = cv2.GaussianBlur(acc, (0, 0), 9) * 9.0
        out = out + dots * 0.8 + glow * 0.5
        # 聚合完成后叠一层清晰霓虹轮廓，保证文字可读
        mB = np.clip(aB[TOP:BOTTOM, :, None] * 1.3 - 0.15, 0, 1)
        out[TOP:BOTTOM] += _neon(B[TOP:BOTTOM]) * mB * 0.55 * (1 - a) * (1 - 0.6 * burst)
        # 页眉与字幕：清晰霓虹字
        for y0, y1 in ((0, TOP), (BOTTOM, core.H)):
            band = A[y0:y1]
            mb = aA[y0:y1, :, None]
            out[y0:y1] = out[y0:y1] * (1 - mb) + _neon(band) * mb
            out[y0:y1] += cv2.GaussianBlur(_neon(band) * mb, (0, 0), 6) * 0.35
        rgba = np.dstack([np.clip(out, 0, 255).astype(np.uint8), np.full((core.H, core.W), 255, np.uint8)])
        c.drawImage(skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType), 0, 0)

    core.draw_frame = draw_frame
