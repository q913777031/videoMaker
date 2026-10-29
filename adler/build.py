"""阿德勒心理学 10 讲：命令行入口。

用法：
    python3 -m adler.build                    # 渲染全部 10 期（成片、封面、分轨、卡点表、文案与出处）
    python3 -m adler.build 01 05              # 只渲染指定期
    python3 -m adler.build 01 --no-video      # 只出音频分轨、封面与文档
    python3 -m adler.build 01 --sheet         # 导出逐镜联系表（每镜头取画面完整时刻），用于检查
    python3 -m adler.build 01 --still 17.5    # 导出单帧
    python3 -m adler.build --verify           # 核验已渲染成片（时长、编码、响度、真峰值、音画偏差），写 out/adler/核验.md
    python3 -m adler.build --publish          # 交付成片、封面、标题与话题到 videos/adler/（配置了取景镜头的讲另出单讲 1080×1080 横屏封面；多讲另出合集图与 1080×1080 封面）
    python3 -m adler.build --square           # 只重出单讲 1080×1080 横屏封面（需配置 SQUARE / 分镜模块 SQUARE_SHOT）
输出目录：out/adler/epXX/
"""

import csv
import importlib
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import skia

from . import core

ROOT = Path(__file__).resolve().parent.parent
PKG = "adler"                       # 其他系列复用本入口时覆盖 PKG / OUT / MODS
OUT = ROOT / "out" / "adler"
MODS = {
    "01": "ep01_teleology", "02": "ep02_inferiority", "03": "ep03_complex", "04": "ep04_competition",
    "05": "ep05_life_tasks", "06": "ep06_tasks", "07": "ep07_encouragement", "08": "ep08_memories",
    "09": "ep09_birth_order", "10": "ep10_community",
}


SQUARE: dict = {}                   # 每讲 1080×1080 横屏封面的取景镜头 {期号: 镜头序号}；分镜模块里的 SQUARE_SHOT 优先


def load(key: str) -> core.Episode:
    return importlib.import_module(f"{PKG}.{MODS[key]}").build()


def square_shot(key: str) -> int | None:
    """该讲横屏封面取景的镜头序号；未配置时返回 None（不出单讲横屏封面，旧系列保持原样）。"""
    mod = importlib.import_module(f"{PKG}.{MODS[key]}")
    return getattr(mod, "SQUARE_SHOT", SQUARE.get(key))


def sheet(ep: core.Episode, path: Path, cols: int = 4):
    """逐镜联系表：每个镜头取退场前的完整画面，缩到 1/4 拼图。"""
    tw, th = core.W // 4, core.H // 4
    n = len(ep.shots)
    rows = (n + cols - 1) // cols
    surf = skia.Surface.MakeRaster(skia.ImageInfo.Make(tw * cols, th * rows, skia.kRGBA_8888_ColorType,
                                                       skia.kPremul_AlphaType))
    c = surf.getCanvas()
    c.clear(skia.ColorWHITE)
    big = skia.Surface.MakeRaster(skia.ImageInfo.Make(core.W, core.H, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType))
    for i, s in enumerate(ep.shots):
        T = max(s.t0 + 0.5, s.t1 - core.EXIT - 0.12)
        core.draw_frame(big.getCanvas(), ep, T)
        img = big.makeImageSnapshot()
        c.drawImageRect(img, skia.Rect.MakeXYWH((i % cols) * tw, (i // cols) * th, tw, th),
                        skia.SamplingOptions(skia.FilterMode.kLinear))
    path.parent.mkdir(parents=True, exist_ok=True)
    surf.makeImageSnapshot().save(str(path), skia.kPNG)


def _video(k: str, ep: core.Episode) -> Path:
    return OUT / f"ep{k}" / f"{core.SERIES['prefix']}{ep.no:02d}_{ep.concept}.mp4"


def verify(keys: list[str]) -> bool:
    """逐期核验成片；任一项不合格返回 False。"""
    rows, ok_all = [], True
    for k in keys:
        ep = load(k)
        mp4 = _video(k, ep)
        if not mp4.exists():
            rows.append(f"| {k} | 缺失 | | | | | | ✗ |")
            ok_all = False
            continue
        info = json.loads(subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "stream=codec_name,width,height,r_frame_rate,pix_fmt,sample_rate",
             "-show_entries", "format=duration", "-of", "json", str(mp4)], capture_output=True, text=True).stdout)
        v = next(s for s in info["streams"] if s["codec_name"] == "h264")
        a = next(s for s in info["streams"] if s["codec_name"] == "aac")
        dur = float(info["format"]["duration"])
        err = subprocess.run(["ffmpeg", "-nostats", "-i", str(mp4), "-af", "ebur128=peak=true", "-f", "null", "-"],
                             capture_output=True, text=True).stderr
        lufs = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1])
        tp = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", err)[-1])
        with open(OUT / f"ep{k}" / "cue_sheet.csv", encoding="utf-8") as f:
            cues = list(csv.DictReader(f))
        worst = max(abs(float(r["音画偏差(帧)"])) for r in cues)
        ok = (v["width"], v["height"]) == (1080, 1920) and v["r_frame_rate"] == "30/1" and v["pix_fmt"] == "yuv420p" \
            and abs(dur - core.END) < 0.05 and worst <= 1.0 and tp <= -0.5
        ok_all &= ok
        rows.append(f"| {k} | {ep.concept} | {dur:.2f}s | {v['width']}×{v['height']} {v['r_frame_rate']} {v['pix_fmt']} | "
                    f"{a['sample_rate']} Hz | {lufs:.1f} LUFS / {tp:.1f} dBTP | {len(cues)} 个，最大 {worst:.2f} 帧 | "
                    f"{'✓' if ok else '✗'} |")
    text = "\n".join([f"# {core.SERIES['name']} {core.SERIES['count']}成片核验", "",
                      f"标准：1080×1920、30fps、yuv420p、时长 {core.END:.2f}s（±0.05）、音效峰值与画面撞击帧偏差 ≤1 帧、真峰值 ≤ -0.5 dBTP。", "",
                      "| 期 | 概念 | 时长 | 视频 | 音频 | 响度 / 真峰值 | 音效卡点 | 结果 |",
                      "|----|------|------|------|------|---------------|----------|------|"] + rows) + "\n"
    (OUT / "核验.md").write_text(text, encoding="utf-8")
    print(text)
    return ok_all


BRAND = "Vibe知识大赏"              # 发布标题统一为「Vibe知识大赏｜片名」


def publish(keys: list[str]):
    """交付到 videos/<PKG>/XX_概念/：只放成片、封面与“标题与话题.txt”（卡点表与出处留在 out/ 内部核验用）。
    系列多于 1 讲且本次交付全部讲时，另出系列合集图与 1080×1080 横屏封面。"""
    eps = []
    for k in keys:
        ep = load(k)
        eps.append((k, ep))
        src = OUT / f"ep{k}"
        dst = ROOT / "videos" / PKG / f"{k}_{ep.concept}"
        if dst.exists():
            shutil.rmtree(dst)
        dst.mkdir(parents=True)
        shutil.copy2(_video(k, ep), dst / _video(k, ep).name)
        shutil.copy2(src / "cover.png", dst / "cover.png")
        (dst / "标题与话题.txt").write_text(f"{BRAND}｜{ep.title}\n{ep.hashtags}\n", encoding="utf-8")
        if square_shot(k) is not None:
            episode_square(k, dst / "横屏封面_1080x1080.png")
        print(dst)
    from engine import wording

    for k, ep in eps:
        for w in wording.episode_warnings(ep) + [f"话题含 AI 腔用语：{h}" for h in wording.check(ep.hashtags)]:
            print(f"  文案警告 ep{k}：{w}")
    intro = ROOT / "videos" / PKG / "合集简介.txt"
    if intro.exists():
        for h in wording.check(intro.read_text(encoding="utf-8")):
            print(f"  文案警告 合集简介：含 AI 腔用语：{h}")
    if len(MODS) > 1 and set(keys) == set(MODS):
        d = ROOT / "videos" / PKG
        collage(eps, d / "合集.png")
        square_cover(eps, d / "横屏封面_1080x1080.png")
        print(d / "合集.png")
        print(d / "横屏封面_1080x1080.png")


def _surface(w: int, h: int):
    return skia.Surface.MakeRaster(skia.ImageInfo.Make(w, h, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType))


def _paper(c, ep, w, h):
    bg = core.bg_image(ep.accent)
    c.drawImageRect(bg, skia.Rect.MakeXYWH(0, (core.H - core.W * h / w) / 2, core.W, core.W * h / w),
                    skia.Rect.MakeWH(w, h), skia.SamplingOptions(skia.FilterMode.kLinear))


MAX_IMG_BYTES = 5 * 1024 * 1024       # 系列图片（合集图、方形封面）上限 5MB


def _save_capped(img: skia.Image, path: Path):
    """存 PNG；超过 5MB 时降为 256 色调色板 PNG（仍超则逐步减色），保证不超过上限。"""
    img.save(str(path), skia.kPNG)
    if path.stat().st_size <= MAX_IMG_BYTES:
        return
    from PIL import Image

    src = Image.open(path).convert("RGB")
    for colors in (256, 192, 128, 64):
        src.quantize(colors=colors, method=Image.Quantize.MEDIANCUT).save(path, optimize=True)
        if path.stat().st_size <= MAX_IMG_BYTES:
            return
    raise RuntimeError(f"{path} 仍超过 5MB")


def collage(eps, path: Path):
    """系列合集图（1080×1080，≤5MB）：顶部系列名与卖点，下方网格排列各讲封面（每张下方标期号与概念）。"""
    from . import kit as K

    S, head, gap, lab = 1080, 230, 18, 52
    n = len(eps)
    best = None
    for cols in range(2, n + 1):                 # 选能让封面最大的列数
        rows = (n + cols - 1) // cols
        tw = min((S - (cols + 1) * gap) / cols, ((S - head - gap) / rows - lab - gap) * 9 / 16)
        if best is None or tw > best[0]:
            best = (tw, cols, rows)
    tw, cols, rows = best
    th = tw * 16 / 9
    surf = _surface(S, S)
    c = surf.getCanvas()
    _paper(c, eps[0][1], S, S)
    K.text(c, BRAND, S / 2, 58, 34, "sans_medium", K.INK2)
    title = f"{core.SERIES['name']} · {core.SERIES['count']}"
    K.text(c, title, S / 2, 128, min(80.0, 80 * 960 / K.text_w(title, 80, "serif_black")), "serif_black", eps[0][1].accent)
    if core.SERIES.get("tagline"):
        K.text(c, core.SERIES["tagline"], S / 2, 194, 36, "sans_medium", K.INK)
    grid_h = rows * (th + lab + gap) - gap
    y0 = head + (S - head - grid_h) / 2
    for i, (k, ep) in enumerate(eps):
        r, j = divmod(i, cols)
        in_row = min(cols, n - r * cols)
        x = S / 2 - (in_row * tw + (in_row - 1) * gap) / 2 + j * (tw + gap)
        y = y0 + r * (th + lab + gap)
        img = skia.Image.open(str(OUT / f"ep{k}" / "cover.png"))
        K.card(c, x + tw / 2, y + th / 2, tw, th, K.PAPER, 1, r=12)
        c.save()
        c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, tw, th), 12, 12), doAntiAlias=True)
        c.drawImageRect(img, skia.Rect.MakeXYWH(x, y, tw, th), skia.SamplingOptions(skia.FilterMode.kLinear))
        c.restore()
        label = f"{ep.no:02d} {ep.concept}"
        size = min(30.0, 30 * (tw - 8) / K.text_w(label, 30, "serif_black"))
        K.text(c, label, x + tw / 2, y + th + lab / 2 + 2, size, "serif_black", K.INK)
    _save_capped(surf.makeImageSnapshot(), path)


def square_cover(eps, path: Path):
    """系列横屏封面（1080×1080，≤5MB）：光束 + 系列名 + 一句话卖点 + 各讲概念纸片。"""
    from . import fx
    from . import kit as K

    S = 1080
    surf = _surface(S, S)
    c = surf.getCanvas()
    acc = eps[0][1].accent
    _paper(c, eps[0][1], S, S)
    fx.rays(c, S / 2, 380, 900, K.GOLD, 0, 18, 0.2)
    fx.glow(c, S / 2, 380, 520, K.GOLD, 0.35)
    K.text(c, BRAND, S / 2, 120, 40, "sans_medium", K.INK2)
    name = core.SERIES["name"]
    ts = min(230.0, 230 * 900 / K.text_w(name, 230, "serif_black"))
    K.text(c, name, S / 2, 330, ts, "serif_black", acc, shadow=(8, 12, 12, K.SHADOW))
    sub = core.SERIES.get("tagline") or core.SERIES["count"]
    line = f"{sub} · {core.SERIES['count']}"
    K.text(c, line, S / 2, 520, min(50.0, 50 * 940 / K.text_w(line, 50, "serif_black")), "serif_black", K.INK)
    n = len(eps)
    cols = 4 if n > 4 else n
    rows = (n + cols - 1) // cols
    pw, gx = 225, 20
    ph = 96 if rows <= 2 else 84
    gy = 26 if rows <= 2 else 18
    top, bottom = 600, 1040
    y0 = (top + bottom) / 2 - (rows * ph + (rows - 1) * gy) / 2 + ph / 2
    for i, (k, ep) in enumerate(eps):
        r, j = divmod(i, cols)
        in_row = min(cols, n - r * cols)
        x = S / 2 - (in_row * pw + (in_row - 1) * gx) / 2 + pw / 2 + j * (pw + gx)
        y = y0 + r * (ph + gy)
        label = f"{ep.no:02d} {ep.concept}"
        K.card(c, x, y, pw, ph, ep.accent, 1, r=24, rot=(-2, 1.5, -1, 2)[i % 4])
        K.text(c, label, x, y, min(36.0, 36 * (pw - 30) / K.text_w(label, 36, "serif_black")), "serif_black", K.PAPER)
    _save_capped(surf.makeImageSnapshot(), path)


def episode_square(k: str, path: Path):
    """单讲横屏封面（1080×1080，≤5MB）：上方期号、片名大字（【】高亮），下方装裱的取景镜头画面（不含字幕与界面），右下角概念印章。"""
    from engine import gfx

    from . import fx
    from . import kit as K

    ep = load(k)
    i = square_shot(k)
    shot = ep.shots[i]
    frame = _surface(core.W, core.H)
    fc = frame.getCanvas()
    fc.drawImage(core.bg_image(ep.accent), 0, 0)
    core._draw_shot(fc, ep, i, max(0.5, shot.t1 - shot.t0 - 0.15))
    stage = frame.makeImageSnapshot()

    S = 1080
    surf = _surface(S, S)
    c = surf.getCanvas()
    _paper(c, ep, S, S)
    K.rr(c, 110, 78, 104, 56, 28, ep.accent)
    K.text(c, f"{ep.no:02d}", 110, 78, 36, "black", K.PAPER)
    K.text(c, f"{BRAND} · {core.SERIES['name']}", 180, 78, 34, "sans_medium", K.INK2, 1, "left")
    lines = ep.cover_title.split("|")
    widest = max(K.text_w(gfx.plain(ln), 104, "serif_black") for ln in lines)
    size = min(104.0, 104 * 940 / widest)
    for j, ln in enumerate(lines):
        gfx.draw_rich(c, ln, S / 2, 190 + j * size * 1.18, size, "serif_black", K.INK, ep.accent, 1.0, "center",
                      shadow=(3, 5, 6, K.SHADOW))
    top = 190 + (len(lines) - 1) * size * 1.18 + size * 0.75
    ph = S - top - 70
    pw = min(S - 120, ph * 1080 / 900)
    px, py = S / 2, top + ph / 2 + 10
    fx.glow(c, px, py, 560, ep.accent2, 0.3)
    with K.at(c, px, py, -1.2):
        K.card(c, 0, 0, pw + 26, ph + 26, "#F7F0E2", 1, r=10)
        c.save()
        c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-pw / 2, -ph / 2, pw, ph), 6, 6), doAntiAlias=True)
        sw = 900 * pw / ph if pw / ph < 1080 / 900 else 1080
        sh = sw * ph / pw
        c.drawImageRect(stage, skia.Rect.MakeXYWH((1080 - sw) / 2, 360 + (900 - sh) / 2, sw, sh),
                        skia.Rect.MakeXYWH(-pw / 2, -ph / 2, pw, ph), skia.SamplingOptions(skia.FilterMode.kLinear))
        c.restore()
        K.rr_stroke(c, 0, 0, pw + 10, ph + 10, 8, K.shade("#C9B48E", 0.2), 3)
    lab = ep.concept
    lw = K.text_w(lab, 40, "serif_black") + 56
    with K.at(c, px + pw / 2 - lw / 2 + 10, py + ph / 2 - 6, -3):
        K.rr(c, 0, 0, lw, 70, 12, ep.accent)
        K.rr_stroke(c, 0, 0, lw - 12, 58, 8, K.PAPER, 2, 0.8)
        K.text(c, lab, 0, 0, 40, "serif_black", K.PAPER)
    path.parent.mkdir(parents=True, exist_ok=True)
    _save_capped(surf.makeImageSnapshot(), path)
    return path


def main():
    args = sys.argv[1:]
    keys = [a for a in args if a in MODS] or list(MODS)
    if "--verify" in args:
        sys.exit(0 if verify(keys) else 1)
    if "--publish" in args:
        publish(keys)
        return
    if "--square" in args:
        for k in keys:
            ep = load(k)
            print(episode_square(k, ROOT / "videos" / PKG / f"{k}_{ep.concept}" / "横屏封面_1080x1080.png"))
        return
    if "--still" in args:
        T = float(args[args.index("--still") + 1])
        for k in keys:
            ep = load(k)
            p = OUT / "stills" / f"ep{k}_{T:05.1f}.png"
            p.parent.mkdir(parents=True, exist_ok=True)
            core.still(ep, T, str(p))
            print(p)
        return
    if "--sheet" in args:
        for k in keys:
            ep = load(k)
            p = OUT / "stills" / f"sheet_ep{k}.png"
            sheet(ep, p)
            for w in core.read_check(ep):
                print(f"  阅读窗警告 ep{k}：{w}")
            print(p)
        return
    for k in keys:
        t0 = time.time()
        ep = load(k)
        print(f"[{k}] {ep.concept}｜{ep.title}：{ep.total:.1f}s，{len(ep.shots)} 镜，{len(ep.events)} 个音效")
        out = core.produce(ep, OUT / f"ep{k}", video="--no-video" not in args)
        if out:
            print(f"[{k}] 完成 {out}（{out.stat().st_size / 1e6:.1f}MB，用时 {time.time() - t0:.0f}s）")


if __name__ == "__main__":
    core.RULES.update(core.LEGACY)   # 阿德勒 10 讲为旧系列，保持原节奏
    main()
