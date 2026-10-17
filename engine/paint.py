"""梵高风格笔触渲染：把场景底稿（underpainting）转成沿流场排布、带厚涂明暗的短笔触。

流程：底稿（UW×UH，RGB 浮点）→ 结构张量求轮廓切向，与场景给定的程序化流场（漩涡 / 同心 / 火焰）混合
→ 三层笔触（大 / 中 / 细节）按流场取向、按底稿取色，用 drawAtlas 一次性绘制 → 画布纹理与暗角。

笔触位置由场景种子固定，每 BOIL 帧整体轻微抖动一次（位置、角度、颜色），形成手绘动画的"沸腾"感；
颜色每帧重新从底稿取样，因此画面内容的运动是连续的。所有随机数均由种子决定，同一帧每次渲染结果相同。
"""

import functools
import math

import cv2
import numpy as np
import skia

W, H = 1080, 1920
UW, UH = 540, 960
US = W / UW
BOIL = 3

SW, SH = 112, 40
N_BEND, N_BRISTLE = 3, 3

# (格距, 笔触长度, 长度随机幅度, 只画在细节区)
LAYERS = [(22, 66, 0.3, False), (15, 44, 0.3, False), (9, 24, 0.3, True)]


@functools.lru_cache(maxsize=1)
def atlas() -> skia.Image:
    """笔触贴图：3 种弯曲 × 3 种鬃毛纹理。灰度带明暗（上沿受光、下沿背光），两端收笔变细。"""
    rng = np.random.default_rng(7)
    img = np.zeros((SH * N_BEND * N_BRISTLE, SW, 4), np.uint8)
    u = np.linspace(0, 1, SW)[None, :]
    v = np.linspace(-1, 1, SH)[:, None]
    for b in range(N_BEND):
        for k in range(N_BRISTLE):
            bend = (b - 1) * 0.32 * (1 - 4 * (u - 0.5) ** 2)
            vv = v - bend
            taper = np.clip(np.minimum(u / 0.14, (1 - u) / 0.26), 0, 1) ** 0.55
            half = 0.9 * taper * (0.9 + 0.1 * np.sin(u * (5 + k) + k))
            edge = 0.10 + 0.06 * rng.random((SH, 1))
            a = np.clip((half - np.abs(vv)) / edge, 0, 1)
            a *= np.clip(1 - 0.35 * (rng.random((SH, 1)) < 0.12), 0, 1)
            streak = 0.6 + 0.4 * rng.random((SH, 1))
            streak = cv2.GaussianBlur(np.repeat(streak, SW, 1), (0, 0), 0.6)
            grain = 1 + rng.normal(0, 0.035, (SH, SW))
            shade = 1.0 + 0.28 * (-vv) - 0.22 * vv ** 2
            g = np.clip(shade * streak * grain * 228, 0, 255)
            row = (b * N_BRISTLE + k) * SH
            img[row: row + SH, :, 3] = (a * 255).astype(np.uint8)
            img[row: row + SH, :, :3] = (g * a).astype(np.uint8)[:, :, None]
    return skia.Image.fromarray(img, skia.ColorType.kRGBA_8888_ColorType, skia.AlphaType.kPremul_AlphaType)


@functools.lru_cache(maxsize=1)
def canvas_texture() -> np.ndarray:
    """亚麻画布纹理（乘性系数，均值约 1）。"""
    rng = np.random.default_rng(3)
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    weave = 0.5 * np.sin(x * 1.9 + 0.6 * np.sin(y * 0.05)) * np.sin(y * 1.9 + 0.6 * np.sin(x * 0.05))
    n = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 1.2)
    tex = 1 + 0.035 * weave + 0.03 * n
    r = np.hypot((x - W / 2) / (W * 0.62), (y - H / 2) / (H * 0.6))
    vig = 1 - 0.32 * np.clip(r - 0.55, 0, 1) ** 1.4
    return (tex * vig).astype(np.float32)


# ---------------------------------------------------------------- 程序化流场（底稿分辨率，返回角度）

@functools.lru_cache(maxsize=64)
def _noise(seed: int, scale: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    g = rng.random((UH // scale + 3, UW // scale + 3)).astype(np.float32)
    return cv2.resize(g, (UW + 3 * scale, UH + 3 * scale), interpolation=cv2.INTER_CUBIC)


def swirl_field(t: float, seed: int = 1, scale: int = 90, speed: float = 0.02) -> np.ndarray:
    """缓慢流动的漩涡场：两层噪声势函数的旋度方向（类似《星月夜》天空）。"""
    ox = int((t * speed * UW) % (2 * scale))
    p = _noise(seed, scale)[ox: ox + UH, : UW] + 0.5 * _noise(seed + 1, scale // 2)[: UH, ox: ox + UW]
    gy, gx = np.gradient(cv2.GaussianBlur(p, (0, 0), 6))
    return np.arctan2(-gx, gy)


def concentric_field(cx: float, cy: float) -> np.ndarray:
    """绕光源的同心环（坐标为成片像素坐标）。"""
    y, x = np.mgrid[0:UH, 0:UW].astype(np.float32)
    return np.arctan2(y - cy / US, x - cx / US) + math.pi / 2


def radial_field(cx: float, cy: float) -> np.ndarray:
    y, x = np.mgrid[0:UH, 0:UW].astype(np.float32)
    return np.arctan2(y - cy / US, x - cx / US)


def flame_field(t: float, amp: float = 0.5) -> np.ndarray:
    """向上的波动流（火焰、柏树式笔触）。"""
    y, x = np.mgrid[0:UH, 0:UW].astype(np.float32)
    return -math.pi / 2 + amp * np.sin(x * 0.06 + y * 0.025 - t * 3.0)


def const_field(angle: float) -> np.ndarray:
    return np.full((UH, UW), angle, np.float32)


def blend_fields(*items) -> np.ndarray:
    """按权重（标量或数组）混合多个轴向场（倍角向量平均）。"""
    cx = sum(w * np.cos(2 * a) for a, w in items)
    cy = sum(w * np.sin(2 * a) for a, w in items)
    return 0.5 * np.arctan2(cy, cx)


# ---------------------------------------------------------------- 底稿分析

def structure(under: np.ndarray, sigma: float = 3.0) -> tuple[np.ndarray, np.ndarray]:
    """结构张量：返回 (轮廓切向角度, 边缘强度 0..1)。"""
    lum = cv2.cvtColor(under, cv2.COLOR_RGB2GRAY)
    gx = cv2.Sobel(lum, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(lum, cv2.CV_32F, 0, 1, ksize=3)
    j11 = cv2.GaussianBlur(gx * gx, (0, 0), sigma)
    j22 = cv2.GaussianBlur(gy * gy, (0, 0), sigma)
    j12 = cv2.GaussianBlur(gx * gy, (0, 0), sigma)
    ang = 0.5 * np.arctan2(2 * j12, j11 - j22) + math.pi / 2
    mag = np.sqrt((j11 - j22) ** 2 + 4 * j12 ** 2)
    return ang, np.clip(mag / 0.02, 0, 1)


# ---------------------------------------------------------------- 绘制

@functools.lru_cache(maxsize=16)
def _seeds(seed: int, layer: int) -> np.ndarray:
    cell = LAYERS[layer][0]
    gy, gx = np.mgrid[cell / 2: H + cell: cell, cell / 2: W + cell: cell]
    pts = np.stack([gx.ravel(), gy.ravel()], 1).astype(np.float32)
    rng = np.random.default_rng(seed * 31 + layer)
    pts += rng.uniform(-0.5, 0.5, pts.shape).astype(np.float32) * cell
    return pts[rng.permutation(len(pts))]


def paint(c: skia.Canvas, under: np.ndarray, field: np.ndarray, frame: int, seed: int,
          field_weight=0.6, detail: np.ndarray | None = None, boil: float = 1.0, size: float = 1.0,
          vivid: float = 1.22):
    """把底稿画成笔触并绘制到 c（W×H）。

    under：UH×UW×3 float32 RGB（0..1）；field：程序化流场角度；field_weight：流场相对轮廓切向的权重
    （标量或数组，边缘强处自动偏向轮廓）；detail：0..1 细节区（细笔触只画在这里，缺省取边缘强度）。
    """
    edge_ang, edge = structure(under)
    fw = np.asarray(field_weight, np.float32) * (1 - 0.85 * edge)
    ang = blend_fields((field, fw), (edge_ang, 1 - fw + 1e-3))
    det = edge if detail is None else np.maximum(detail, edge * 0.6)

    ground = cv2.GaussianBlur(under, (0, 0), 2.5)
    ground = cv2.resize(ground * 0.82, (W, H), interpolation=cv2.INTER_LINEAR)
    base = np.empty((H, W, 4), np.uint8)
    base[:, :, :3] = np.clip(ground * 255, 0, 255).astype(np.uint8)
    base[:, :, 3] = 255
    c.drawImage(skia.Image.fromarray(base, skia.ColorType.kRGBA_8888_ColorType), 0, 0)

    b = frame // BOIL
    img = atlas()
    lum = under @ np.array([0.299, 0.587, 0.114], np.float32)
    for li, (cell, length, lvar, detail_only) in enumerate(LAYERS):
        pts = _seeds(seed, li)
        rng = np.random.default_rng((seed * 7919 + b * 104729 + li) % (2 ** 32))
        n = len(pts)
        p = pts + rng.normal(0, 0.18 * boil, (n, 2)).astype(np.float32) * cell
        ix = np.clip((p[:, 0] / US).astype(np.int32), 0, UW - 1)
        iy = np.clip((p[:, 1] / US).astype(np.int32), 0, UH - 1)
        keep = np.ones(n, bool)
        if detail_only:
            keep = rng.random(n) < det[iy, ix] * 1.4
        elif li == 1:
            keep = rng.random(n) < 0.45 + 0.55 * det[iy, ix]
        p, ix, iy = p[keep], ix[keep], iy[keep]
        n = len(p)
        if n == 0:
            continue
        a = ang[iy, ix] + rng.normal(0, 0.1 * boil, n)
        a = np.where(np.cos(a) < 0, a + math.pi, a)
        L = length * size * (1 + rng.uniform(-lvar, lvar, n))
        # 弯曲：沿笔触方向前后两点的流场角度差决定弯向
        dx, dy = np.cos(a) * L * 0.5 / US, np.sin(a) * L * 0.5 / US
        fx = np.clip((ix + dx).astype(np.int32), 0, UW - 1)
        fy = np.clip((iy + dy).astype(np.int32), 0, UH - 1)
        bx = np.clip((ix - dx).astype(np.int32), 0, UW - 1)
        by = np.clip((iy - dy).astype(np.int32), 0, UH - 1)
        da = np.angle(np.exp(2j * (ang[fy, fx] - ang[by, bx]))) / 2
        bend = np.where(da > 0.12, 2, np.where(da < -0.12, 0, 1))
        sprite = bend * N_BRISTLE + rng.integers(0, N_BRISTLE, n)

        col = under[iy, ix]
        l = lum[iy, ix][:, None]
        col = l + (col - l) * vivid
        col = col * (1 + rng.normal(0, 0.09, (n, 3))) * (1 + rng.normal(0, 0.08, (n, 1)))
        col = np.clip(col * 1.12 * 255, 0, 255).astype(np.uint32)
        argb = (0xFF000000 | (col[:, 0] << 16) | (col[:, 1] << 8) | col[:, 2]).astype(np.int64)

        s = L / SW
        cs, sn = s * np.cos(a), s * np.sin(a)
        tx = p[:, 0] - (cs * SW / 2 - sn * SH / 2)
        ty = p[:, 1] - (sn * SW / 2 + cs * SH / 2)
        xf = list(map(skia.RSXform, cs.tolist(), sn.tolist(), tx.tolist(), ty.tolist()))
        tex = [_RECTS[k] for k in sprite.tolist()]
        c.drawAtlas(img, xf, tex, argb.tolist(), skia.BlendMode.kModulate,
                    skia.SamplingOptions(skia.FilterMode.kLinear))


_RECTS = [skia.Rect.MakeXYWH(0, k * SH, SW, SH) for k in range(N_BEND * N_BRISTLE)]


def finish(buf: np.ndarray):
    """就地施加画布纹理与暗角（buf 为 H×W×4 uint8）。"""
    tex = canvas_texture()
    rgb = buf[:, :, :3].astype(np.float32) * tex[:, :, None]
    buf[:, :, :3] = np.clip(rgb, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- 底稿画布

class Under:
    """底稿画布：在 UW×UH 的 skia 表面上用成片坐标（W×H）作画，to_array 输出 float32 RGB。"""

    def __init__(self):
        self.buf = np.zeros((UH, UW, 4), np.uint8)
        self.surf = skia.Surface(self.buf)
        self.c = self.surf.getCanvas()

    def begin(self) -> skia.Canvas:
        self.c.restoreToCount(1)
        self.c.save()
        self.c.scale(1 / US, 1 / US)
        self.c.clear(0xFF000000)
        return self.c

    def to_array(self) -> np.ndarray:
        self.c.restoreToCount(1)
        self.surf.flushAndSubmit()
        return self.buf[:, :, :3].astype(np.float32) / 255.0
