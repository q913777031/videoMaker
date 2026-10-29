"""频道片尾：@Vibe哥 关注卡动画（约 4.3 秒，1080×1920、30fps），接在每个视频末尾。

画面（参考常见爆款结尾）：黑底蓝色微光 → 霓虹圆环扫一圈画出、头像弹入并伴随光粒 → “@Vibe哥”砸下（轻抖）→
红色“+ 点个关注”按钮从下方弹起并呼吸 → 手指点按，按钮变灰“✓ 已关注”，爱心飞出 → “下期见”逐字出现 → 淡出。
配乐：music/bgm.m4a 在 drop 处（17.14 秒起）截 2 小节，所有动作与音效落在该段的实测拍点上，响度对齐 -14 LUFS。

用法：python3 -m brand.outro [--stills]   → brand/outro.mp4（以及 out/brand/ 下的单帧）
"""

import math
import subprocess
import sys
import tempfile
from multiprocessing import get_context
from pathlib import Path

import numpy as np
import skia
import soundfile as sf

from adler import core
from adler import fx
from adler import kit as K
from engine import audio, perc
from engine.gfx import clamp01, ease_in_out, ease_out, ease_out_back, lerp

ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
W, H, FPS = 1080, 1920, 30
SRC_T0 = 17.14                       # 原曲 drop 处
NAME = "@Vibe哥"
BLUE = "#3FA9FF"
RED = "#F2394A"


def _beats():
    """从 SRC_T0 起 8 个实测拍点（相对片尾起点的秒数）与片尾总长。"""
    i0 = next(i for i, b in enumerate(core.BEATS) if b["t"] >= SRC_T0 - 0.05 and b["bar_pos"] == 0)
    bs = [core.BEATS[i0 + k]["t"] - core.BEATS[i0]["t"] for k in range(9)]
    return bs[:8], bs[8] + 0.05, core.BEATS[i0]["t"]


BEATS, TOTAL, START = _beats()
CX, CY, R = W / 2, 690, 300                      # 头像圆心与半径


def since(k: float, t: float) -> float:
    i = int(k)
    f = k - i
    a = BEATS[min(i, 7)]
    b = BEATS[i + 1] if i + 1 < 8 else TOTAL
    return t - (a + (b - a) * f)


_AV = {}


def avatar() -> skia.Image:
    if "img" not in _AV:
        _AV["img"] = skia.Image.open(str(HERE / "avatar.png"))
    return _AV["img"]


def _ring(c, t):
    """霓虹圆环：第 0 拍起 0.4 秒扫一圈画出，之后一道高光沿环转动，随拍呼吸。"""
    k = ease_out(clamp01(since(0, t) / 0.4))
    if k <= 0:
        return
    pulse = 0.0
    for i in range(8):
        dt = since(i, t)
        if dt >= 0:
            pulse = math.exp(-dt * 6)
    rr = R + 16
    rect = skia.Rect.MakeXYWH(CX - rr, CY - rr, 2 * rr, 2 * rr)
    for width, alpha, blur in ((34, 0.35 + 0.25 * pulse, 22), (16, 0.6, 6), (7, 1.0, 0)):
        p = K.paint(BLUE if blur else "#BFE6FF", alpha, width, blur=blur)
        path = skia.Path()
        path.addArc(rect, -90, 360 * k)
        c.drawPath(path, p)
    if k >= 1:
        ang = (t * 160) % 360
        path = skia.Path()
        path.addArc(rect, ang, 70)
        c.drawPath(path, K.paint("#FFFFFF", 0.8, 9, blur=3))
        path = skia.Path()
        path.addArc(rect, ang + 180, 40)
        c.drawPath(path, K.paint("#9FDBFF", 0.6, 7, blur=3))


def _avatar(c, t):
    dt = since(0, t) - 0.08
    if dt < 0:
        return
    s = ease_out_back(clamp01(dt / 0.45), 1.9) * (1 + 0.012 * math.sin(t * 2.2))
    a = clamp01(dt / 0.2)
    with K.at(c, CX, CY, 0, s):
        c.save()
        clip = skia.Path()
        clip.addCircle(0, 0, R)
        c.clipPath(clip, doAntiAlias=True)
        img = avatar()
        c.drawImageRect(img, skia.Rect.MakeXYWH(-R, -R, 2 * R, 2 * R), skia.SamplingOptions(skia.CubicResampler.Mitchell()),
                        skia.Paint(Alphaf=a))
        sweep = since(0, t) - 0.25
        if 0 <= sweep < 0.6:                      # 一道扫光
            x = lerp(-R * 1.6, R * 1.6, sweep / 0.6)
            c.drawRect(skia.Rect.MakeXYWH(x - 50, -R, 100, 2 * R), K.paint("#FFFFFF", 0.35, blur=20))
        c.restore()


def _name(c, t):
    dt = since(1, t)
    if dt < 0:
        return
    k = clamp01(dt / 0.18)
    s = lerp(1.7, 1.0, ease_out(k))
    a = clamp01(dt / 0.08)
    shake = 10 * math.exp(-dt * 16) * math.sin(dt * 80) if dt < 0.4 else 0
    with K.at(c, CX + shake, 1160, 0, s):
        K.text(c, NAME, 0, 0, 150, "black", "#000000", a * 0.5, shadow=(0, 8, 16, "#000000"))
        K.text(c, NAME, 0, 0, 150, "black", "#FFFFFF", a)
    if 0 <= dt < 0.25:
        fx.flash(c, 0.25 * (1 - dt / 0.25), "#FFFFFF")


def _button(c, t):
    dt = since(2, t)
    if dt < 0:
        return
    y = lerp(1500, 1340, ease_out_back(clamp01(dt / 0.4), 2.2))
    a = clamp01(dt / 0.15)
    tap = since(4, t)
    s = 1.0
    if tap < 0:
        breathe = since(3, t)
        if breathe >= 0:
            s = 1 + 0.06 * math.sin(clamp01(breathe / 0.5) * math.pi)
    else:
        s = 1 - 0.08 * math.sin(clamp01(tap / 0.18) * math.pi)
    followed = tap >= 0.09
    w, h = 660, 160
    with K.at(c, CX, y, 0, s):
        if not followed:
            K.rr(c, 0, 8, w, h, h / 2, "#000000", 0.35 * a)
            K.rr(c, 0, 0, w, h, h / 2, RED, a)
            K.rr(c, 0, -h * 0.22, w - 40, h * 0.36, h * 0.2, "#FFFFFF", 0.12 * a)
            K.text(c, "+ 点个关注", 0, 0, 84, "black", "#FFFFFF", a)
        else:
            K.rr(c, 0, 0, w, h, h / 2, "#3A3A40", a)
            K.text(c, "✓ 已关注", 0, 0, 80, "black", "#D8D8DE", a)
    if tap >= 0:
        for i in range(10):
            rng = np.random.default_rng(i)
            ang = -math.pi / 2 + (rng.random() - 0.5) * 2.2
            d = ease_out(clamp01(tap / 0.9)) * (180 + 120 * rng.random())
            hx, hy = CX + 200 + math.cos(ang) * d, 1340 + math.sin(ang) * d - 40 * tap
            al = 1 - clamp01((tap - 0.4) / 0.6)
            if al > 0:
                K.heart(c, hx, hy, 36 + 16 * rng.random(), ("#FF4D6A", "#FF8FA3", "#FFFFFF")[i % 3], al)


def _finger(c, t):
    """手指从右下角滑入，在第 4 拍点按按钮。"""
    k0 = since(3, t)
    if k0 < 0:
        return
    tap = since(4, t)
    approach = ease_in_out(clamp01(k0 / max(0.01, BEATS[4] - BEATS[3])))
    x = lerp(1150, CX + 210, approach)
    y = lerp(1900, 1395, approach)
    press = 0.0
    if tap >= 0:
        press = math.sin(clamp01(tap / 0.18) * math.pi)
        x += ease_in_out(clamp01((tap - 0.3) / 0.4)) * 400
        y += ease_in_out(clamp01((tap - 0.3) / 0.4)) * 500
    with K.at(c, x, y + press * 10, -20, 1 - 0.06 * press):
        if tap >= 0 and tap < 0.4:
            K.ripple(c, 0, -20, tap, "#FFFFFF", 120, 6)
        K.rr(c, 0, 70, 70, 180, 35, "#F3D2B5")
        K.rr(c, 50, 170, 150, 150, 60, "#F3D2B5")
        c.drawRoundRect(skia.Rect.MakeXYWH(-35, -20, 70, 180), 35, 35, K.paint("#8A6A55", 1, 4))
        K.rr(c, 0, 5, 44, 40, 18, "#FBE7DA")


def _bye(c, t):
    dt = since(5, t)
    if dt < 0:
        return
    s = "下期见"
    for i, ch in enumerate(s):
        st = fx.word_pop(dt - i * 0.12)
        if st:
            a, sc, _ = st
            with K.at(c, CX - 90 + i * 90, 1530, 0, sc):
                K.text(c, ch, 0, 0, 68, "sans_medium", "#C9CDD6", a)


def _bg(c, t):
    c.drawColor(skia.ColorBLACK)
    pulse = 0.0
    for i in range(8):
        dt = since(i, t)
        if dt >= 0:
            pulse = math.exp(-dt * 5)
    fx.glow(c, CX, CY, 760, "#1C4E8A", 0.35 + 0.15 * pulse)
    rng = np.random.default_rng(3)
    for i in range(60):
        x = rng.random() * W
        y0 = rng.random() * H
        sp = 40 + rng.random() * 80
        y = (y0 - t * sp) % H
        K.dot(c, x, y, 1.5 + rng.random() * 2.5, "#6FB8FF", 0.2 + 0.4 * rng.random())


def draw(c, t: float):
    _bg(c, t)
    sp = since(0, t)
    if 0 <= sp < 0.9:
        fx.sparks(c, CX, CY, sp, ["#9FDBFF", "#FFFFFF", BLUE], 26, 7, 520, 18)
    _ring(c, t)
    _avatar(c, t)
    _name(c, t)
    _button(c, t)
    _bye(c, t)
    _finger(c, t)
    fade = clamp01((t - (TOTAL - 0.35)) / 0.35)
    if fade > 0:
        c.drawPaint(K.paint("#000000", fade))


# 音效：(拍, 音色, 增益)
HITS = [(0, "pop", 0.9), (1, "kick", 1.0), (2, "pop", 0.8), (4, "rim", 0.8), (4, "ding", 0.9), (5, "pop", 0.6),
        (6, "pop", 0.5)]


def audio_track() -> np.ndarray:
    import pyloudnorm

    sr = audio.SR
    from engine import bgm

    x = bgm.load()
    a = int(START * sr)
    n = int(TOTAL * sr)
    mus = x[a:a + n].copy()
    fi, fo = int(0.03 * sr), int(0.45 * sr)
    mus[:fi] *= np.linspace(0, 1, fi)[:, None]
    mus[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.4
    sfx = np.zeros_like(mus)
    for k, name, gain in HITS:
        clip = perc.sound(name) * core.SFX_LEVEL.get(name, 0.3) * gain
        lead = int(perc.attack_ms(name) / 1000 * sr)
        i = max(0, int(BEATS[k] * sr) - lead)
        m = min(len(clip), len(sfx) - i)
        if m > 0:
            sfx[i:i + m] += clip[:m, None] if clip.ndim == 1 else clip[:m]
    mix = mus + sfx
    meter = pyloudnorm.Meter(sr)
    mix *= 10 ** ((-14.0 - meter.integrated_loudness(mix)) / 20)
    peak = np.abs(mix).max()
    if peak > 0.84:
        mix *= 0.84 / peak
    return mix.astype(np.float32)


def _frame(t: float) -> bytes:
    surf = skia.Surface.MakeRaster(skia.ImageInfo.Make(W, H, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType))
    draw(surf.getCanvas(), t)
    return surf.makeImageSnapshot().tobytes()


def main():
    out_dir = ROOT / "out" / "brand"
    out_dir.mkdir(parents=True, exist_ok=True)
    if "--stills" in sys.argv:
        for i, t in enumerate((BEATS[0] + 0.5, BEATS[1] + 0.3, BEATS[3] + 0.2, BEATS[4] + 0.25, BEATS[6], TOTAL - 0.5)):
            surf = skia.Surface.MakeRaster(skia.ImageInfo.Make(W, H, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType))
            draw(surf.getCanvas(), t)
            surf.makeImageSnapshot().save(str(out_dir / f"outro_{i}.png"), skia.kPNG)
        print(out_dir / "outro_*.png")
        return
    mp4 = HERE / "outro.mp4"
    n = int(round(TOTAL * FPS))
    with tempfile.TemporaryDirectory() as tmp:
        wav = str(Path(tmp) / "a.wav")
        sf.write(wav, audio_track(), audio.SR)
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS),
               "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-shortest", "-movflags", "+faststart", str(mp4)]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        with get_context("fork").Pool(4) as pool:
            for buf in pool.imap(_frame, [k / FPS for k in range(n)], chunksize=4):
                proc.stdin.write(buf)
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError("ffmpeg failed")
    print(mp4, f"{TOTAL:.2f}s")


if __name__ == "__main__":
    main()
