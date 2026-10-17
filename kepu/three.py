"""3D 画面层的桥接：把校准后的时间轴切成卡拍子镜头，导出给 kepu3d/（Remotion + three.js）渲染，并在解码后的成片上核验。

分工：时间轴、卡点、音效、混音与核验仍由 Python 负责；kepu3d/ 只按 timeline.json 逐帧画画面与字幕，
不做任何节拍判断。子镜头切点只取原曲节拍（优先小节重拍，其次第 3 拍），撞击前后留出预备与余韵，不在撞击帧上切。
"""

import json
import shutil
import subprocess
from pathlib import Path

import cv2
import numpy as np

from .config import FPS, Layout

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "kepu3d"
BROWSER = "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell"
FONTS = ("NotoSerifCJKsc-Bold.otf", "NotoSerifCJKsc-SemiBold.otf", "NotoSansCJKsc-Medium.otf")

SUB_MIN, SUB_MAX, SUB_LONG = 1.5, 2.6, 3.3     # 子镜头目标时长（秒）；首镜（钩子）下限 1.0 秒，节奏更快
PRE, POST = 0.9, 0.45            # 撞击前至少留 0.9 秒预备、撞击后至少 0.45 秒余韵，期间不切
EDGE = 0.9                       # 切点离镜头首尾至少 0.9 秒


def _fr(t: float) -> float:
    return round(t * FPS) / FPS


def subshots(tl, an) -> list[dict]:
    """每个镜头内按拍切子镜头：在 [上一切点 + SUB_MIN, 上一切点 + SUB_MAX] 内依次找小节重拍、第 3 拍、任意拍，
    避开撞击保护区；找不到就不切。返回 [{shot, k, start, end, why}]（视频绝对秒）。"""
    out = []
    for s in tl.shots:
        hits = [s.start + v for k, v in tl.cues[s.no].items() if not k.startswith("_")]
        ok = lambda x: (s.start + EDGE <= x <= s.start + s.dur - EDGE
                        and all(not (h - PRE <= x <= h + POST) for h in hits))
        cuts, last = [], s.start
        lo = 1.0 if s.no == tl.shots[0].no else SUB_MIN
        while an is not None:
            pick = None
            for pos, why, hi in (({1}, "小节重拍", SUB_MAX), ({3}, "第3拍", SUB_MAX), (None, "最近拍", SUB_MAX),
                                 ({1, 3}, "撞击保护区后的重拍/第3拍", SUB_LONG)):
                cand = [b for b in an.beats if (pos is None or b.pos in pos)
                        and last + lo <= b.t <= last + hi and ok(b.t)]
                if cand:
                    pick = (min(cand, key=lambda b: b.t) if pos in ({1}, {1, 3}) else min(cand, key=lambda b: abs(b.t - last - 1.8)), why)
                    break
            if pick is None:
                break
            cuts.append((_fr(pick[0].t), pick[1]))
            last = pick[0].t
        edges = [(s.start, "镜头切换")] + cuts + [(s.start + s.dur, "")]
        for k, ((a, why), (b, _)) in enumerate(zip(edges, edges[1:])):
            out.append({"shot": s.no, "k": k, "start": round(a, 4), "end": round(b, 4), "why": why})
    return out


def props(tl, an, L: Layout, topic, subs: list[dict], audio: str, cover: bool = False) -> dict:
    """Remotion 输入：画幅与排版、镜头（字幕、角标、镜头内 cue）、子镜头、需要画面撞击的事件、音频路径。"""
    return {
        "slug": topic.slug, "fps": FPS, "total": round(tl.total, 4), "width": L.w, "height": L.h,
        "layout": {k: getattr(L, k) for k in ("name", "text_size", "text_line_gap", "text_x", "text_y", "text_align",
                                               "ref_size", "tag_size", "tag_x", "tag_y")},
        "shots": [{"no": s.no, "start": round(s.start, 4), "dur": round(s.dur, 4), "lines": s.lines, "tag": s.tag,
                   "credit": s.credit, "cue": {k: round(v, 4) for k, v in tl.cues[s.no].items()}} for s in tl.shots],
        "subshots": subs,
        "hits": [{"shot": e["shot"], "key": e["key"], "t": round(e["t"], 4),
                  "soft": e.get("orig_sound", e["sound"]) in ("", "shaker")} for e in tl.events],
        "audio": audio,
        "cover": {"title": list(topic.cover_title), "subtitle": topic.cover_subtitle} if cover else None,
    }


def stage_assets(slug: str, wav: Path | None):
    """把字体与混音复制进 kepu3d/public（目录已被 .gitignore 排除）。"""
    fd = APP / "public" / "fonts"
    fd.mkdir(parents=True, exist_ok=True)
    for f in FONTS:
        if not (fd / f).exists():
            shutil.copy(ROOT / "assets" / "fonts" / f, fd / f)
    if wav is not None:
        td = APP / "public" / slug
        td.mkdir(parents=True, exist_ok=True)
        shutil.copy(wav, td / "mix.wav")


def _npx(args: list[str], workers: int):
    cmd = ["npx", "remotion", *args, f"--browser-executable={BROWSER}", "--gl=swangle",
           f"--concurrency={workers}", "--log=error"]
    r = subprocess.run(cmd, cwd=APP)
    if r.returncode != 0:
        raise RuntimeError(f"remotion exited with code {r.returncode}: {' '.join(args[:3])}")


def render(p: dict, out_mp4: Path, props_path: Path, workers: int = 4):
    """整片渲染：H.264 yuv420p 30fps（参数见 kepu3d/remotion.config.ts），音频 AAC 48 kHz。"""
    props_path.write_text(json.dumps(p, ensure_ascii=False), encoding="utf-8")
    out_mp4, props_path = out_mp4.resolve(), props_path.resolve()
    raw = out_mp4.with_name(out_mp4.stem + "_raw.mp4")
    _npx(["render", "src/index.ts", "Kepu", str(raw), f"--props={props_path}",
          "--audio-codec=aac", "--audio-bitrate=192k"], workers)
    to_tv_range(raw, out_mp4)
    raw.unlink()


def to_tv_range(src: Path, dst: Path):
    """Remotion 的 JPEG 帧会产出全幅 yuvj420p；转成通用的有限幅 yuv420p（音频直接复制）。"""
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vf", "scale=in_range=full:out_range=tv",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
                    "-c:a", "copy", "-movflags", "+faststart", str(dst)], check=True)


def stills(p: dict, frames: list[int], out_dir: Path, props_path: Path, comp: str = "Kepu") -> list[Path]:
    """批量抽帧（只打包一次）：返回 PNG 路径列表，顺序与 frames 一致。"""
    props_path.write_text(json.dumps(p, ensure_ascii=False), encoding="utf-8")
    props_path, out_dir = props_path.resolve(), out_dir.resolve()
    r = subprocess.run(["node", "stills.mjs", str(props_path), str(out_dir), ",".join(map(str, frames)), comp], cwd=APP)
    if r.returncode != 0:
        raise RuntimeError(f"stills.mjs exited with code {r.returncode}")
    return [out_dir / f"f{f:05d}.png" for f in frames]


# ---------------------------------------------------------------- 成片核验（解码后的帧）

def decode_gray(mp4: Path, w: int = 270) -> np.ndarray:
    """解码全片为缩小的灰度帧 [N, h, w]，用于帧差统计。"""
    info = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                      "stream=width,height", "-of", "json", str(mp4)],
                                     capture_output=True, text=True).stdout)["streams"][0]
    h = int(round(info["height"] * w / info["width"] / 2)) * 2
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(mp4), "-vf", f"scale={w}:{h}:flags=area",
                          "-pix_fmt", "gray", "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w)


def _diff(fr: np.ndarray) -> np.ndarray:
    """d[i] = 第 i 帧与第 i-1 帧的灰度平均绝对差（d[0] = 0）。"""
    d = np.abs(fr[1:].astype(np.int16) - fr[:-1].astype(np.int16)).mean(axis=(1, 2))
    return np.concatenate([[0.0], d])


def visual_hits(fr: np.ndarray, events: list[dict]) -> list:
    """撞击事件前后 ±4 帧内帧差最大的一帧（在解码成片上实测）。"""
    d, out = _diff(fr), []
    for e in events:
        if e.get("orig_sound", e["sound"]) in ("", "shaker"):
            continue
        f0 = int(round(e["t"] * FPS))
        win = range(max(1, f0 - 4), min(len(d), f0 + 5))
        peak = max(win, key=lambda f: d[f])
        out.append({"shot": e["shot"], "key": e["key"], "cue_frame": f0, "visual_peak_frame": peak,
                    "diff_frames": peak - f0, "peak_diff": round(float(d[peak]), 2)})
    return out


def cut_check(fr: np.ndarray, subs: list[dict]) -> dict:
    """每个子镜头切点（含镜头切换）在解码成片上的帧差：切点帧应是 ±4 帧内的最大值。"""
    d, rows = _diff(fr), []
    for s in subs[1:]:
        f0 = int(round(s["start"] * FPS))
        win = range(max(1, f0 - 4), min(len(d), f0 + 5))
        peak = max(win, key=lambda f: d[f])
        rows.append({"t": s["start"], "frame": f0, "peak": peak, "diff": round(float(d[f0]), 2)})
    bad = [r for r in rows if r["peak"] != r["frame"]]
    return {"cuts": len(rows), "peak_on_cut": len(rows) - len(bad), "min_cut_diff": min(r["diff"] for r in rows),
            "off": bad}


def change_3s(fr: np.ndarray, step: float = 0.5, gap: float = 3.0) -> dict:
    """与 kepu.build.change_3s 同口径，但在解码成片上计算。"""
    n = len(fr)
    idx = lambda sec: min(n - 1, int(round(sec * FPS)))
    g = lambda sec: fr[idx(sec)].astype(np.int16)
    times = np.arange(0.0, n / FPS - gap - 0.4, step)
    diffs = [(float(np.abs(g(x) - g(x + gap)).mean()), float(x)) for x in times]
    run, best = 0.0, 0.0
    for x in times:
        if float(np.abs(g(x) - g(x + step)).mean()) < 1.0:
            run += step
            best = max(best, run)
        else:
            run = 0.0
    m = min(diffs)
    return {"min_diff_3s": round(m[0], 2), "at": round(m[1], 2), "longest_static_s": round(best, 2)}


def event_gap(tl, subs: list[dict]) -> dict:
    """画面事件（切镜、子镜头切点、撞击）之间的最大间隔。"""
    times = sorted({0.0, tl.total} | {s["start"] for s in subs}
                   | {e["t"] for e in tl.events if e.get("orig_sound", e["sound"])})
    g, at = max((b - a, a) for a, b in zip(times, times[1:]))
    return {"max_gap_s": round(g, 2), "from": round(at, 2), "ok": g <= 3.0}


def contact_sheet(pngs: list[tuple[float, Path]], path: Path, k: float = 0.3):
    ims = []
    for t, p in pngs:
        im = cv2.imread(str(p))
        im = cv2.resize(im, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
        cv2.putText(im, f"{t:g}s", (8, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        ims.append(im)
    rows = [np.hstack(ims[i:i + 6]) for i in range(0, len(ims), 6)]
    w = max(r.shape[1] for r in rows)
    cv2.imwrite(str(path), np.vstack([cv2.copyMakeBorder(r, 0, 6, 0, w - r.shape[1], cv2.BORDER_CONSTANT) for r in rows]))
