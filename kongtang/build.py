"""控糖革命 12 讲：命令行入口（与 adler.build 相同的子命令）。

用法：
    python3 -m kongtang.build                    # 渲染全部 12 期（成片、封面、分轨、卡点表、文案与出处）
    python3 -m kongtang.build 01 05              # 只渲染指定期
    python3 -m kongtang.build 01 --no-video      # 只出音频分轨、封面与文档
    python3 -m kongtang.build 01 --sheet         # 导出逐镜联系表（每镜头取画面完整时刻），用于检查
    python3 -m kongtang.build 01 --still 17.5    # 导出单帧
    python3 -m kongtang.build --verify           # 核验已渲染成片（时长、编码、响度、真峰值、音画偏差），写 out/kongtang/核验.md
    python3 -m kongtang.build --publish          # 把成片、封面、卡点表、文案与出处复制到 videos/kongtang/
输出目录：out/kongtang/epXX/
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


from adler import core
from adler.build import sheet

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out" / "kongtang"
MODS = {f"{i:02d}": f"ep{i:02d}" for i in range(1, 13)}


def load(key: str) -> core.Episode:
    return importlib.import_module(f"kongtang.{MODS[key]}").build()


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
    text = "\n".join(["# 控糖革命 12 讲成片核验", "",
                      f"标准：1080×1920、30fps、yuv420p、时长 {core.END:.2f}s（±0.05）、音效峰值与画面撞击帧偏差 ≤1 帧、真峰值 ≤ -0.5 dBTP。", "",
                      "| 期 | 概念 | 时长 | 视频 | 音频 | 响度 / 真峰值 | 音效卡点 | 结果 |",
                      "|----|------|------|------|------|---------------|----------|------|"] + rows) + "\n"
    (OUT / "核验.md").write_text(text, encoding="utf-8")
    print(text)
    return ok_all


def publish(keys: list[str]):
    """复制交付物到 videos/kongtang/XX_概念/。"""
    for k in keys:
        ep = load(k)
        src = OUT / f"ep{k}"
        dst = ROOT / "videos" / "kongtang" / f"{k}_{ep.concept}"
        dst.mkdir(parents=True, exist_ok=True)
        shutil.copy2(_video(k, ep), dst / _video(k, ep).name)
        for name in ("cover.png", "cue_sheet.csv", "文案与出处.md"):
            shutil.copy2(src / name, dst / name)
        print(dst)


def main():
    args = sys.argv[1:]
    skip = {args.index("--still") + 1} if "--still" in args else set()     # --still 后面的时间不是期号
    keys = [a for i, a in enumerate(args) if a in MODS and i not in skip] or list(MODS)
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
