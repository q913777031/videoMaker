"""黑金科普短片构建入口：读取原曲 → 节拍网格 → 校准时间轴 → 合成音效与混音 → 渲染横竖屏双版本 → 媒体核验。

用法：
    python3 -m kepu.build --topic night                  # 依次查找 ./bgm.m4a、./music/bgm.m4a、./assets/bgm.m4a
    python3 -m kepu.build --topic night --bgm 路径/bgm.m4a
    python3 -m kepu.build --topic night --stills 1,9,33  # 只出抽帧拼图（叙事基准时间轴），用于画面检查
    python3 -m kepu.build --topic night --covers-only
原曲缺失时只输出“待配乐预览”（音轨仅含合成音效），不生成任何替代配乐。
"""

import argparse
import csv
import json
import subprocess
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import soundfile as sf

from . import config, music, render, sfx
from .config import FPS, SR, SOUNDS
from .topic import Topic, load

ROOT = Path(__file__).resolve().parent.parent


def tc(sec: float) -> str:
    f = int(round(sec * FPS))
    return f"{f // (3600 * FPS):02d}:{f // (60 * FPS) % 60:02d}:{f // FPS % 60:02d}:{f % FPS:02d}"


def write_wav(path: Path, x: np.ndarray):
    sf.write(str(path), x.astype(np.float32), SR, subtype="PCM_24")


# ---------------------------------------------------------------- 文本交付物

def reading_table(tl) -> list[dict]:
    """逐镜阅读窗口与预算核算：预算 = max(2, 汉字数 / 4.5) 秒，含数字或为来源卡时另加余量。"""
    rows = []
    for k, s in enumerate(tl.shots):
        a = s.start + (0.2 if k == 0 else render.TEXT_IN)
        b = s.start + s.dur - render.TEXT_OUT
        budget, need = s.budget, s.need
        rows.append({"shot": s.no, "text": s.text, "han": s.han, "start": a, "end": b, "window": b - a,
                     "budget": budget, "need": need, "ok": b - a >= need, "tag": s.tag})
    return rows


def write_captions(path: Path, tl, rows, topic: Topic):
    out = [f"{topic.title}逐屏文案", "",
           "说明：“／”为主字幕换行；稳定窗口不含入场、退场；预算 = max(2, 汉字数/4.5) 秒（排版预算，不是心理学定律）。",
           f"时间轴状态：{'已按原曲校准' if tl.calibrated else '叙事基准（原曲缺失，未按音乐校准）'}；总长 {tl.total:.2f} 秒。", ""]
    for r in rows:
        out.append(f"镜头{r['shot']:02d}｜{tc(r['start'])}–{tc(r['end'])}｜角标：{r['tag']}")
        out.append(f"  主字幕：{r['text']}")
        out.append(f"  汉字 {r['han']} 字｜稳定 {r['window']:.2f} 秒｜预算 {r['budget']:.2f} 秒｜"
                   f"含余量需求 {r['need']:.2f} 秒｜{'满足' if r['ok'] else '不满足'}")
        out.append("")
    total_han = sum(r["han"] for r in rows)
    out.append(f"{len(rows)} 张主卡汉字合计：{total_han}（数字、英文、标点另计；角标不计入）。")
    out += ["", "封面", f"  主标题：{''.join(topic.cover_title)}", f"  副标题：{topic.cover_subtitle}",
            f"发布标题：{topic.publish_title}", f"话题：{topic.hashtags}"]
    path.write_text("\n".join(out) + "\n", encoding="utf-8")




def write_cue_csv(path: Path, tl, an, onset_check: dict):
    cols = ["视频时间码HH:MM:SS:FF", "帧号", "原曲时间", "事件类型", "相对重音强度0-1", "归一化口径", "检测/复核方式",
            "置信度", "镜头号", "视觉撞击动作", "字幕", "音效类型", "音效起音帧", "混音调整"]
    norm = "片段内谱通量减局部中值÷片段第99百分位，截断0–1" if an else "未确认"
    rows = []
    for k, s in enumerate(tl.shots):
        if k == 0:
            continue
        info = tl.boundaries[k] if tl.boundaries else None
        if info:
            bt, why = info
            rows.append([tc(s.start), int(round(s.start * FPS)), f"{an.seg_start + bt.t:.3f}",
                         f"镜头切换｜{render.POS_NAME[bt.pos]}｜{why}", round(bt.strength, 3), norm,
                         f"节拍网格 {an.grid_info['bpm']} BPM；自动分析，未人工试听", "高" if bt.pos == 1 else "中",
                         s.no, "场景层0.3s匹配转场", s.text, "", "", ""])
        else:
            rows.append([tc(s.start), int(round(s.start * FPS)), "未确认" if not an else f"{an.seg_start + s.start:.3f}",
                         "镜头切换", "未确认", norm, "叙事基准边界" if not an else "附近无合适拍点，保持叙事位置",
                         "未确认", s.no, "场景层0.3s匹配转场", s.text, "", "", ""])
    for e in tl.events:
        s = tl.shots[e["shot"] - 1]
        f = int(round(e["t"] * FPS))
        snd = SOUNDS.get(e["sound"], "") if e["sound"] else "无新增音效"
        on = onset_check.get((e["shot"], e["key"]))
        bt = e.get("beat")
        kind = render.POS_NAME[bt.pos] if bt else ("柔和动作（未贴拍）" if an else "候选事件")
        kind = ("撞击｜" if e["sound"] and e["sound"] != "shaker" else "移动/动作｜") + kind
        rows.append([tc(e["t"]), f, f"{an.seg_start + e['music_t']:.3f}" if an and e["music_t"] is not None else "未确认",
                     kind, e["strength"] if e["strength"] is not None else "未确认", norm,
                     e["method"], e["conf"], e["shot"], e["action"], s.text, snd,
                     on if on is not None else "", e["mix"] or (f"增益 {e['gain']:.2f}" if e["sound"] else "")])
    rows.sort(key=lambda r: r[1])
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        w.writerows(rows)


def write_beat_csv(path: Path, an):
    """完整节拍网格，供人工试听复核。"""
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["视频时间码HH:MM:SS:FF", "帧号", "原曲时间", "小节", "拍位", "相对重音强度0-1", "是否段落起点"])
        bar = 0
        for b in an.beats:
            if b.pos == 1:
                bar += 1
            w.writerow([tc(b.t), int(round(b.t * FPS)), f"{an.seg_start + b.t:.3f}", bar, b.pos,
                        round(b.strength, 3), "是" if any(abs(b.t - x) < 1e-6 for x in an.sections) else ""])


# ---------------------------------------------------------------- 核验

def measure_onsets(track: np.ndarray, tl) -> tuple[dict, list]:
    """在音效轨上实测每个事件的起音帧：窗口 [t-0.1, t+0.15] 内包络首次超过窗口峰值 10% 的位置。"""
    env = np.abs(track).max(axis=1)
    res, rows = {}, []
    for e in tl.events:
        if not e["sound"]:
            continue
        a, b = int((e["sfx_t"] - 0.1) * SR), int((e["sfx_t"] + 0.15) * SR)
        w = env[max(0, a):b]
        i = int(np.argmax(w > 0.1 * w.max()))
        on = (max(0, a) + i) / SR
        fr = int(round(on * FPS))
        res[(e["shot"], e["key"])] = fr
        rows.append({"shot": e["shot"], "key": e["key"], "cue_frame": int(round(e["t"] * FPS)), "onset_frame": fr,
                     "onset_s": round(on, 4), "diff_frames": fr - int(round(e["t"] * FPS)),
                     "vs_beat_ms": round((on - e["music_t"]) * 1000, 1) if e.get("music_t") is not None else None})
    return res, rows


def visual_hits(tl, L, events) -> list:
    """在渲染帧上实测视觉撞击：事件前后 ±4 帧内相邻帧差（画面变化量）最大的一帧。"""
    out = []
    for e in events:
        if not e["sound"] or e["sound"] == "shaker":
            continue
        f0 = int(round(e["t"] * FPS))
        frames = {f: cv2.cvtColor(render.still(tl, L, f), cv2.COLOR_RGBA2GRAY).astype(np.int16)
                  for f in range(f0 - 5, f0 + 5)}
        diffs = {f: float(np.abs(frames[f] - frames[f - 1]).mean()) for f in range(f0 - 4, f0 + 5)}
        peak = max(diffs, key=diffs.get)
        out.append({"shot": e["shot"], "key": e["key"], "cue_frame": f0, "visual_peak_frame": peak,
                    "diff_frames": peak - f0})
    return out


def ffprobe(path: Path) -> dict:
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json",
                                   str(path)], capture_output=True, text=True).stdout)
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    a = next((s for s in j["streams"] if s["codec_type"] == "audio"), None)
    return {"file": path.name, "size_mb": round(int(j["format"]["size"]) / 1e6, 2),
            "duration": float(j["format"]["duration"]), "video": f"{v['codec_name']} {v['width']}x{v['height']} "
            f"{v['pix_fmt']} {v['r_frame_rate']} frames={v.get('nb_frames')}",
            "audio": f"{a['codec_name']} {a['sample_rate']}Hz ch={a['channels']}" if a else "无"}


def blackdetect(path: Path) -> str:
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", str(path), "-vf", "blackdetect=d=0.1:pix_th=0.02",
                        "-an", "-f", "null", "-"], capture_output=True, text=True)
    return "; ".join(l.split("] ")[-1] for l in r.stderr.splitlines() if "black_start" in l) or "无"


def ebur128(path: Path) -> str:
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True)
    tail = r.stderr[r.stderr.rfind("Summary:"):]
    vals = {}
    for key in ("I:", "Peak:", "LRA:"):
        k = tail.find(key)
        if k >= 0:
            vals[key.rstrip(":")] = tail[k:].split("\n")[0].split(":", 1)[1].strip()
    return json.dumps(vals, ensure_ascii=False)


def extract_frames(mp4: Path, out_dir: Path, times: dict):
    for name, t in times.items():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(mp4), "-frames:v", "1",
                        str(out_dir / f"{mp4.stem}_{name}.png")], check=True)


# ---------------------------------------------------------------- 主流程

def contact_sheet(tl, times: list[float], path: Path):
    """横竖屏各一行抽帧拼图（左上角标时间），用于快速检查画面与排版。"""
    rows = []
    for L in config.LAYOUTS.values():
        k = 0.3 if L.name == "vertical" else 0.25
        ims = []
        for t in times:
            im = cv2.cvtColor(render.still(tl, L, int(round(t * FPS))), cv2.COLOR_RGBA2BGR)
            im = cv2.resize(im, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
            cv2.putText(im, f"{t:g}s", (8, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            ims.append(im)
        rows.append(np.hstack(ims))
    w = max(r.shape[1] for r in rows)
    cv2.imwrite(str(path), np.vstack([cv2.copyMakeBorder(r, 0, 6, 0, w - r.shape[1], cv2.BORDER_CONSTANT)
                                      for r in rows]))


def check_times(tl) -> dict:
    """解码抽检时刻：首帧，以及约 1/3、2/3 处镜头和最后一镜的稳定窗口中点。"""
    sh = tl.shots
    pick = {"first": 0.0}
    for i in (len(sh) // 3, 2 * len(sh) // 3, len(sh) - 1):
        pick[f"s{sh[i].no:02d}"] = round(sh[i].start + sh[i].dur / 2, 3)
    return pick


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", required=True, help="topics/<slug> 的目录名")
    ap.add_argument("--bgm", default=None)
    ap.add_argument("--out", default=None, help="默认 out/<slug>")
    ap.add_argument("--only", choices=["vertical", "horizontal"], default=None)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--covers-only", action="store_true")
    ap.add_argument("--stills", default=None, help="逗号分隔的秒数：只输出抽帧拼图 stills.png")
    args = ap.parse_args()
    topic = load(args.topic)
    out = Path(args.out) if args.out else ROOT / "out" / topic.slug
    out.mkdir(parents=True, exist_ok=True)
    if args.stills:
        contact_sheet(render.build_timeline(topic), [float(x) for x in args.stills.split(",")], out / "stills.png")
        print(out / "stills.png")
        return
    if args.covers_only:
        for name, L in config.LAYOUTS.items():
            cv2.imwrite(str(out / f"cover_{name}.png"), cv2.cvtColor(render.cover(L, topic), cv2.COLOR_RGBA2BGR))
        return
    (out / "sfx_samples").mkdir(parents=True, exist_ok=True)
    (out / "check").mkdir(exist_ok=True)
    report = {"generated": time.strftime("%Y-%m-%d %H:%M:%S")}

    search = (ROOT / "bgm.m4a", ROOT / "music" / "bgm.m4a", ROOT / "assets" / "bgm.m4a")
    bgm = Path(args.bgm) if args.bgm else next((p for p in search if p.exists()), None)
    an = None
    if bgm is not None and bgm.exists():
        base = topic.shots()
        an = music.analyze(bgm, base[-1].start + base[-1].dur)
        report["music"] = {"path": str(bgm), "duration": round(an.duration, 3), "sample_rate": an.sample_rate,
                           "channels": an.channels, "codec": an.codec, "segment": [round(an.seg_start, 3),
                           round(an.seg_end, 3)], "tempo_candidates": an.tempo, "grid": an.grid_info,
                           "notes": an.notes}
    else:
        report["music"] = {"status": "缺失", "searched": [str(p) for p in search]}
        print("bgm.m4a not found: rendering PREVIEW without music (no substitute score).", file=sys.stderr)

    tl = render.build_timeline(topic, an)
    total = tl.total

    # 音效：样本与音效轨
    for name, fn in sfx.BANK.items():
        write_wav(out / "sfx_samples" / f"{name}.wav", np.repeat(fn()[:, None], 2, axis=1))
    events = [(e["sfx_t"], e["sound"], e["gain"]) for e in tl.events if e["sound"]]
    sfx_track = sfx.render_track(events, total)

    if an is not None:
        src = an.audio[: len(sfx_track)]
        src = np.pad(src, ((0, len(sfx_track) - len(src)), (0, 0)))
        # 原曲在片尾仍是满电平：从最后 2–3.5 秒内的小节重拍起做余弦淡出，避免突然截断
        fade_from = next((b.t for b in an.beats if b.pos == 1 and total - 3.5 <= b.t <= total - 2.0), total - 3.0)
        mus = music.fade_tail(src, total - fade_from)
        report["music"]["fade_out"] = [round(fade_from, 3), round(total, 3)]
        mus, sfx_track, mix, stats = music.master(mus, sfx_track)
        write_wav(out / "bgm.wav", mus)
        write_wav(out / "mix.wav", mix)
        audio_for_video = out / "mix.wav"
        report["mix_measured"] = stats
        suffix = ""
    else:
        audio_for_video = out / "sfx.wav"
        suffix = "_PREVIEW_noBGM"
    write_wav(out / "sfx.wav", sfx_track)

    onset_map, onset_rows = measure_onsets(sfx_track, tl)
    report["sfx_onset_check"] = onset_rows
    write_cue_csv(out / "cue_table.csv", tl, an, onset_map)
    if an is not None:
        write_beat_csv(out / "beat_grid.csv", an)
        report["boundaries"] = [None] + [
            {"shot": tl.shots[k].no, "start": round(tl.shots[k].start, 3), "dur": round(tl.shots[k].dur, 3),
             "beat_pos": tl.boundaries[k][0].pos if tl.boundaries[k] else None,
             "why": tl.boundaries[k][1] if tl.boundaries[k] else "保持"} for k in range(1, len(tl.shots))]
    rows = reading_table(tl)
    report["reading"] = rows
    write_captions(out / "captions.txt", tl, rows, topic)
    (out / "references.txt").write_text(topic.references, encoding="utf-8")

    for name in ([args.only] if args.only else ["vertical", "horizontal"]):
        L = config.LAYOUTS[name]
        cv2.imwrite(str(out / f"cover_{name}.png"), cv2.cvtColor(render.cover(L, topic), cv2.COLOR_RGBA2BGR))
        mp4 = out / f"{topic.slug}_{name}{suffix}.mp4"
        t0 = time.time()
        render.render(tl, L, str(mp4), str(audio_for_video), workers=args.workers)
        report.setdefault("render_seconds", {})[name] = round(time.time() - t0, 1)
        report.setdefault("ffprobe", {})[name] = ffprobe(mp4)
        report.setdefault("blackdetect", {})[name] = blackdetect(mp4)
        report.setdefault("loudness_ffmpeg", {})[name] = ebur128(mp4)
        extract_frames(mp4, out / "check", check_times(tl))
        report.setdefault("visual_hits", {})[name] = visual_hits(tl, L, tl.events)

    (out / "verify_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1, default=str),
                                            encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("ffprobe", "blackdetect", "loudness_ffmpeg") if k in report},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
