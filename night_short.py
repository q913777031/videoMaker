"""《为什么一到晚上，就觉得自己的人生不行了》：横竖屏双版本渲染、音效合成、原曲校准与交付核验。

用法：
    python3 night_short.py                    # 自动查找 ./bgm.m4a 或 ./assets/bgm.m4a
    python3 night_short.py --bgm 路径/bgm.m4a
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

from night import config, music, render, sfx
from night.config import FPS, SR, SOUNDS

ROOT = Path(__file__).resolve().parent


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
        budget = max(2.0, s.han / 4.5)
        extra = 0.0
        if any(ch.isdigit() for ch in s.text):
            extra += 0.8
        if s.no in (6, 15):
            extra += 1.0
        need = max(budget + extra, 3.0 if s.no != 15 else 5.0)
        rows.append({"shot": s.no, "text": s.text, "han": s.han, "start": a, "end": b, "window": b - a,
                     "budget": budget, "need": need, "ok": b - a >= need, "tag": s.tag})
    return rows


def write_captions(path: Path, tl, rows):
    out = ["《为什么一到晚上，就觉得自己的人生不行了》逐屏文案", "",
           "说明：“／”为主字幕换行；稳定窗口不含入场、退场；预算 = max(2, 汉字数/4.5) 秒（排版预算，不是心理学定律）。",
           f"时间轴状态：{'已按原曲校准' if tl.calibrated else '叙事基准（原曲缺失，未按音乐校准）'}；总长 {tl.total:.2f} 秒。", ""]
    for r in rows:
        out.append(f"镜头{r['shot']:02d}｜{tc(r['start'])}–{tc(r['end'])}｜角标：{r['tag']}")
        out.append(f"  主字幕：{r['text']}")
        out.append(f"  汉字 {r['han']} 字｜稳定 {r['window']:.2f} 秒｜预算 {r['budget']:.2f} 秒｜"
                   f"含余量需求 {r['need']:.2f} 秒｜{'满足' if r['ok'] else '不满足'}")
        out.append("")
    total_han = sum(r["han"] for r in rows)
    out.append(f"15 张主卡汉字合计：{total_han}（数字、英文、标点另计；角标不计入）。")
    out += ["", "封面", "  主标题：一到晚上，就否定人生？", "  副标题：一件小事，怎么变成全部",
            "发布标题：《白天还能上班，晚上却觉得整个人生都不行？》",
            "话题：#知识科普 #心理学 #反刍思维 #自我评价 #上班族"]
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


REFERENCES = """参考资料

Susan Nolen-Hoeksema, Blair E. Wisco, Sonja Lyubomirsky (2008).
Rethinking Rumination. Perspectives on Psychological Science, 3(5), 400–424.
DOI: 10.1111/j.1745-6924.2008.00088.x
期刊学会页面：https://www.psychologicalscience.org/journals/perspectives/j.1745-6924.2008.00088.x
论文摘要：https://pubmed.ncbi.nlm.nih.gov/26158958/

核验范围
- 本片依据制作提示词所附的书目信息与摘要范围制作。
- 制作环境的网络策略拒绝访问 PubMed、Crossref 等文献站点，本次未能在线复核摘要原文，也未查阅全文，
  未补充任何实验程序、样本或数据细节。
- 片中使用的结论仅限：该综述讨论反刍与负面思考、问题解决等的关系，并区分反刍与更有适应性的自我反思。
- 该综述不是专门验证“夜晚人生崩溃”的实验；片中“夜晚”只是故事场景，不主张夜间自我否定均由反刍造成。
- 年份 2008 为文献发表年份，不代表现象首次出现的年份。
- 片中的“写下事实 / 下一步”属于改编的反思练习工具，不是验证理论的正式实验，也不替代专业帮助。
"""


def write_cue_csv(path: Path, tl, an, onset_check: dict):
    cols = ["视频时间码HH:MM:SS:FF", "帧号", "原曲时间", "事件类型", "相对重音强度0-1", "归一化口径", "检测/复核方式",
            "置信度", "镜头号", "视觉撞击动作", "字幕", "音效类型", "音效起音帧", "混音调整"]
    norm = "片段内谱通量减局部中值÷片段第99百分位，截断0–1" if an else "未确认"
    rows = []
    for k, s in enumerate(tl.shots):
        if k > 0:
            rows.append([tc(s.start), int(round(s.start * FPS)),
                         f"{an.seg_start + s.start:.3f}" if an else "未确认", "镜头切换", "未确认", norm,
                         "叙事基准边界" if not an else "边界±0.3s内贴强起音（自动）", "未确认", s.no,
                         "场景层0.3s匹配转场", s.text, "", "", ""])
    for e in tl.events:
        s = tl.shots[e["shot"] - 1]
        f = int(round(e["t"] * FPS))
        snd = SOUNDS.get(e["sound"], "") if e["sound"] else "无新增音效"
        on = onset_check.get((e["shot"], e["key"]))
        rows.append([tc(e["t"]), f, f"{an.seg_start + e['t']:.3f}" if an else "未确认",
                     "候选重音事件" if e["sound"] else "柔和动作（不追重音）",
                     e["strength"] if e["strength"] is not None else "未确认", norm,
                     e["method"], e["conf"], e["shot"], e["action"], s.text, snd,
                     on if on is not None else "", e["mix"] or (f"增益 {e['gain']:.2f}" if e["sound"] else "")])
    rows.sort(key=lambda r: r[1])
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        w.writerows(rows)


# ---------------------------------------------------------------- 核验

def measure_onsets(track: np.ndarray, tl) -> tuple[dict, list]:
    """在音效轨上实测每个事件的起音帧：窗口 [t-0.1, t+0.15] 内包络首次超过窗口峰值 10% 的位置。"""
    env = np.abs(track).max(axis=1)
    res, rows = {}, []
    for e in tl.events:
        if not e["sound"]:
            continue
        a, b = int((e["t"] - 0.1) * SR), int((e["t"] + 0.15) * SR)
        w = env[max(0, a):b]
        i = int(np.argmax(w > 0.1 * w.max()))
        on = (max(0, a) + i) / SR
        fr = int(round(on * FPS))
        res[(e["shot"], e["key"])] = fr
        rows.append({"shot": e["shot"], "key": e["key"], "cue_frame": int(round(e["t"] * FPS)), "onset_frame": fr,
                     "onset_s": round(on, 4), "diff_frames": fr - int(round(e["t"] * FPS))})
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

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bgm", default=None)
    ap.add_argument("--out", default=str(ROOT / "out" / "night"))
    ap.add_argument("--only", choices=["vertical", "horizontal"], default=None)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--covers-only", action="store_true")
    args = ap.parse_args()
    out = Path(args.out)
    if args.covers_only:
        out.mkdir(parents=True, exist_ok=True)
        for name, L in config.LAYOUTS.items():
            cv2.imwrite(str(out / f"cover_{name}.png"), cv2.cvtColor(render.cover(L), cv2.COLOR_RGBA2BGR))
        return
    (out / "sfx_samples").mkdir(parents=True, exist_ok=True)
    (out / "check").mkdir(exist_ok=True)
    report = {"generated": time.strftime("%Y-%m-%d %H:%M:%S")}

    bgm = Path(args.bgm) if args.bgm else next((p for p in (ROOT / "bgm.m4a", ROOT / "assets" / "bgm.m4a")
                                               if p.exists()), None)
    an = None
    if bgm is not None and bgm.exists():
        an = music.analyze(bgm)
        report["music"] = {"path": str(bgm), "duration": round(an.duration, 3), "sample_rate": an.sample_rate,
                           "channels": an.channels, "codec": an.codec, "segment": [round(an.seg_start, 3),
                           round(an.seg_end, 3)], "tempo_candidates": an.tempo, "notes": an.notes}
    else:
        report["music"] = {"status": "缺失", "searched": [str(ROOT / "bgm.m4a"), str(ROOT / "assets" / "bgm.m4a")]}
        print("bgm.m4a not found: rendering PREVIEW without music (no substitute score).", file=sys.stderr)

    tl = render.build_timeline(an)
    total = tl.total

    # 音效：样本与音效轨
    for name, fn in sfx.BANK.items():
        write_wav(out / "sfx_samples" / f"{name}.wav", np.repeat(fn()[:, None], 2, axis=1))
    events = [(e["t"], e["sound"], e["gain"]) for e in tl.events if e["sound"]]
    sfx_track = sfx.render_track(events, total)

    if an is not None:
        mus = music.fade_tail(an.audio[: len(sfx_track)])
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
    rows = reading_table(tl)
    report["reading"] = rows
    write_captions(out / "captions.txt", tl, rows)
    (out / "references.txt").write_text(REFERENCES, encoding="utf-8")

    for name in ([args.only] if args.only else ["vertical", "horizontal"]):
        L = config.LAYOUTS[name]
        cv2.imwrite(str(out / f"cover_{name}.png"), cv2.cvtColor(render.cover(L), cv2.COLOR_RGBA2BGR))
        mp4 = out / f"night_{name}{suffix}.mp4"
        t0 = time.time()
        render.render(tl, L, str(mp4), str(audio_for_video), workers=args.workers)
        report.setdefault("render_seconds", {})[name] = round(time.time() - t0, 1)
        report.setdefault("ffprobe", {})[name] = ffprobe(mp4)
        report.setdefault("blackdetect", {})[name] = blackdetect(mp4)
        report.setdefault("loudness_ffmpeg", {})[name] = ebur128(mp4)
        extract_frames(mp4, out / "check", {"first": 0.0, "research": 33.0, "reflection": 57.0, "ending": 87.0})
        report.setdefault("visual_hits", {})[name] = visual_hits(tl, L, tl.events)

    (out / "verify_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1, default=str),
                                            encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("ffprobe", "blackdetect", "loudness_ffmpeg") if k in report},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
