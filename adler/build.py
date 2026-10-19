"""阿德勒心理学 10 讲：命令行入口。

用法：
    python3 -m adler.build                    # 渲染全部 10 期（成片、封面、分轨、卡点表、文案与出处）
    python3 -m adler.build 01 05              # 只渲染指定期
    python3 -m adler.build 01 --no-video      # 只出音频分轨、封面与文档
    python3 -m adler.build 01 --sheet         # 导出逐镜联系表（每镜头取画面完整时刻），用于检查
    python3 -m adler.build 01 --still 17.5    # 导出单帧
    python3 -m adler.build --verify           # 核验已渲染成片（时长、编码、响度、真峰值、音画偏差），写 out/adler/核验.md
    python3 -m adler.build --publish          # 把成片、封面、卡点表、文案与出处复制到 videos/adler/
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
OUT = ROOT / "out" / "adler"
MODS = {
    "01": "ep01_teleology", "02": "ep02_inferiority", "03": "ep03_complex", "04": "ep04_competition",
    "05": "ep05_life_tasks", "06": "ep06_tasks", "07": "ep07_encouragement", "08": "ep08_memories",
    "09": "ep09_birth_order", "10": "ep10_community",
}


def load(key: str) -> core.Episode:
    return importlib.import_module(f"adler.{MODS[key]}").build()


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
    return OUT / f"ep{k}" / f"{ep.file_prefix}{ep.no:02d}_{ep.concept}.mp4"


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
    text = "\n".join(["# 阿德勒 10 讲成片核验", "",
                      f"标准：1080×1920、30fps、yuv420p、时长 {core.END:.2f}s（±0.05）、音效峰值与画面撞击帧偏差 ≤1 帧、真峰值 ≤ -0.5 dBTP。", "",
                      "| 期 | 概念 | 时长 | 视频 | 音频 | 响度 / 真峰值 | 音效卡点 | 结果 |",
                      "|----|------|------|------|------|---------------|----------|------|"] + rows) + "\n"
    (OUT / "核验.md").write_text(text, encoding="utf-8")
    print(text)
    return ok_all


def publish(keys: list[str]):
    """复制交付物到 videos/adler/XX_概念/。"""
    for k in keys:
        ep = load(k)
        src = OUT / f"ep{k}"
        dst = ROOT / "videos" / "adler" / f"{k}_{ep.concept}"
        dst.mkdir(parents=True, exist_ok=True)
        shutil.copy2(_video(k, ep), dst / _video(k, ep).name)
        for name in ("cover.png", "cue_sheet.csv", "文案与出处.md"):
            shutil.copy2(src / name, dst / name)
        print(dst)


def main():
    args = sys.argv[1:]
    keys = [a for a in args if a in MODS] or list(MODS)
    if "--verify" in args:
        sys.exit(0 if verify(keys) else 1)
    if "--publish" in args:
        publish(keys)
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
    main()
