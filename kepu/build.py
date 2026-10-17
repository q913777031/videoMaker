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

from . import config, music, render, sfx, three
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


def layout_check(tl) -> list[str]:
    """主字幕与来源卡是否超出各画幅的关键内容安全区；返回问题列表（空表示通过）。"""
    from . import draw as d
    bad = []
    for L in config.LAYOUTS.values():
        l, _, r, _ = L.safe
        for s in tl.shots:
            size = L.ref_size if s.credit else L.text_size
            for ln in s.lines:
                w = d.text_width(ln, "serif", size)
                if s.credit:
                    w += L.ref_size * 2.4
                    x0 = L.w / 2 - w / 2
                elif L.text_align == "center":
                    x0 = L.text_x - w / 2
                else:
                    x0 = L.text_x
                if x0 < l or x0 + w > r:
                    bad.append(f"{L.name} 镜头{s.no:02d}「{ln}」宽 {w:.0f}px，超出安全区 x {l}–{r}")
    return bad


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
        hit = e.get("orig_sound") and e["orig_sound"] != "shaker"
        kind = ("撞击｜" if hit else "移动/动作｜") + kind
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
        if e.get("orig_sound", e["sound"]) in ("", "shaker"):
            continue
        f0 = int(round(e["t"] * FPS))
        frames = {f: cv2.cvtColor(render.still(tl, L, f), cv2.COLOR_RGBA2GRAY).astype(np.int16)
                  for f in range(f0 - 5, f0 + 5)}
        diffs = {f: float(np.abs(frames[f] - frames[f - 1]).mean()) for f in range(f0 - 4, f0 + 5)}
        peak = max(diffs, key=diffs.get)
        out.append({"shot": e["shot"], "key": e["key"], "cue_frame": f0, "visual_peak_frame": peak,
                    "diff_frames": peak - f0})
    return out


def event_gap(tl) -> dict:
    """画面事件（切镜、撞击、二次构图）之间的最大间隔；motion=max 时要求 ≤ 3 秒。"""
    times = sorted({0.0, tl.total} | {s.start for s in tl.shots}
                   | {e["t"] for e in tl.events if e.get("orig_sound", e["sound"]) or e["key"].startswith("reframe")})
    g, at = max((b - a, a) for a, b in zip(times, times[1:]))
    return {"max_gap_s": round(g, 2), "from": round(at, 2), "ok": g <= 3.0}


def change_3s(tl, L, step: float = 0.5, gap: float = 3.0) -> dict:
    """“3 秒内画面不重复”检查：每隔 step 秒取一帧，与 gap 秒后的帧比较灰度平均绝对差（0–255），
    报告最小值及其位置；同时报告各镜头内最长的“无明显变化”时长（相邻 0.5 秒帧差 < 1.0 连续累计）。"""
    def gray(sec):
        return cv2.cvtColor(render.still(tl, L, int(round(sec * FPS))), cv2.COLOR_RGBA2GRAY).astype(np.int16)
    times = np.arange(0.0, tl.total - gap - 0.4, step)
    cache = {}
    g = lambda sec: cache.setdefault(round(sec, 3), gray(sec))
    diffs = [(float(np.abs(g(x) - g(x + gap)).mean()), float(x)) for x in times]
    still_run, best = 0.0, 0.0
    for x in times:
        if float(np.abs(g(x) - g(x + step)).mean()) < 1.0:
            still_run += step
            best = max(best, still_run)
        else:
            still_run = 0.0
    m = min(diffs)
    return {"min_diff_3s": round(m[0], 2), "at": round(m[1], 2), "longest_static_s": round(best, 2)}


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


def write_delivery(out: Path, topic: Topic):
    """根据 verify_report.json 与 cue_table.csv 生成 DELIVERY.md；数值全部来自实测文件，不写目标值。"""
    r = json.loads((out / "verify_report.json").read_text(encoding="utf-8"))
    rows = list(csv.reader((out / "cue_table.csv").open(encoding="utf-8-sig")))[1:]
    final = "mix_measured" in r
    hits = [x for x in rows if x[3].startswith("撞击")]
    off = [x for x in hits if "第1拍" not in x[3]]
    low = [x for x in rows if x[7] == "低"]
    cancel = [x for x in rows if "取消" in x[13]]
    vh = r.get("visual_hits", {})
    worst = max((abs(h["diff_frames"]) for v in vh.values() for h in v), default=None)
    onset = sorted({x["diff_frames"] for x in r.get("sfx_onset_check", [])})
    reading = r.get("reading", [])
    scope = topic.references.split("核验范围", 1)[-1].strip()
    L = [f"# {topic.title}交付说明", "",
         f"**交付状态：{'已配乐成片' if final else '待配乐预览（原曲缺失，未生成替代配乐）'}。** 由 `python3 -m kepu.build --topic {topic.slug}` 生成；"
         f"题材提示词见 `plans/{topic.slug}.md`。", "", "## 已渲染", ""]
    for name, v in r.get("ffprobe", {}).items():
        L.append(f"- `{v['file']}`：{v['video']}，{v['audio']}，{v['duration']:.3f} s")
    L += ["- 两种比例封面 `cover_*.png`；`sfx.wav`" + ("、`bgm.wav`、`mix.wav`（48 kHz 24bit，同起点同长度）" if final else "")
          + "；`cue_table.csv`" + ("、`beat_grid.csv`" if final else "") + "；`captions.txt`、`references.txt`、`verify_report.json`",
          f"- WAV 音轨不提交到仓库（`.gitignore`），可用 `python3 -m kepu.build --topic {topic.slug}` 确定性重新生成，"
          "或在构建所在环境的 `out/` 目录取用。", "",
          "## 已核验（实际运行得到）", ""]
    L.append(f"- blackdetect：{'；'.join(f'{k} {v}' for k, v in r.get('blackdetect', {}).items())}。")
    if final:
        m = r["mix_measured"]
        L.append(f"- 响度：mix.wav 实测 {m['integrated_lufs']} LUFS-I、真峰值 {m['true_peak_dbtp']} dBTP；"
                 f"ffmpeg ebur128 成片实测 {r['loudness_ffmpeg'].get('vertical')}。")
        L.append(f"- 卡点：{len(hits)} 个撞击事件中 {len(hits) - len(off)} 个落在小节重拍。"
                 + ("不在重拍上的：" + "；".join(f"镜头{x[8]} {x[9]}（{x[3].split('｜')[1]}）" for x in off) + "。" if off else ""))
        if cancel:
            L.append("- 原曲在该拍低频已足、按规则取消低音鼓叠加：" + "；".join(f"镜头{x[8]}（{x[13]}）" for x in cancel) + "。画面撞击仍在原拍点。")
    L.append(f"- 音画同步：音效起音帧与事件帧偏差 {onset} 帧；画面撞击峰值与事件帧最大偏差 {worst} 帧（共 {len(vh.get('vertical', []))} 个撞击事件/每版）。")
    L.append(f"- 阅读窗口：{len(reading)} 张主卡{'全部满足' if all(x['ok'] for x in reading) else '存在不满足项'}预算，最短稳定 {min(x['window'] for x in reading):.2f} s；主字幕宽度均在安全区内。")
    for name, v in r.get("change_3s", {}).items():
        L.append(f"- 3 秒画面变化（{name}）：每 0.5 秒取帧与 3 秒后比较，最小灰度平均差 {v['min_diff_3s']}（{v['at']} s 处）；"
                 f"相邻 0.5 秒几乎无变化的最长连续时长 {v['longest_static_s']} s。")
    for name, v in r.get("cut_check", {}).items():
        L.append(f"- 3D 子镜头（{name}）：{len(r.get('subshots', []))} 个镜头画面，切点全部取原曲节拍（小节重拍或第 3 拍）；"
                 f"{v['cuts']} 个切点中 {v['peak_on_cut']} 个在解码成片上是 ±4 帧内帧差最大的一帧，最小切点帧差 {v['min_cut_diff']}。")
    if r.get("subshots"):
        gap = r.get("max_event_gap", {})
        L.append(f"- 切镜与撞击之间的最大间隔 {gap.get('max_gap_s')} s（{gap.get('from')} s 起），"
                 f"{'满足' if gap.get('ok') else '不满足'}“3 秒内画面不重复”。")
    if r.get("reframes"):
        gap = r.get("max_event_gap", {})
        L.append(f"- 镜头内二次构图 {len(r['reframes'])} 处（推近 / 拉开交替，卡在节拍上）；切镜、撞击与构图变化之间的最大间隔 "
                 f"{gap.get('max_gap_s')} s（{gap.get('from')} s 起），{'满足' if gap.get('ok') else '不满足'}“3 秒内不重复”。")
    L.append("- 解码抽帧见 `check/`（首帧与约 1/3、2/3、片尾处）。")
    if low:
        L += ["", "## 需要试听复核", "", "置信度为“低”的事件（网格拍点上原曲起音较弱）：" + "；".join(f"镜头{x[8]} {x[9]}（强度 {x[4]}）" for x in low) + "。"]
    L += ["", "## 核验范围与局限", "", scope, "", "- 没有人工试听，也没有在手机或小扬声器上实听；原曲是否含人声无法确认。"]
    (out / "DELIVERY.md").write_text("\n".join(L) + "\n", encoding="utf-8")


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


BGM_SEARCH = (ROOT / "bgm.m4a", ROOT / "music" / "bgm.m4a", ROOT / "assets" / "bgm.m4a")


def _find_bgm(args) -> Path | None:
    return Path(args.bgm) if args.bgm else next((p for p in BGM_SEARCH if p.exists()), None)


def _analysis(topic: Topic, bgm: Path | None):
    if bgm is None or not bgm.exists():
        raise SystemExit("bgm.m4a not found")
    base = topic.shots()
    return music.analyze(bgm, base[-1].start + base[-1].dur)


def stills_three(topic: Topic, args, out: Path):
    """renderer=three 的抽帧检查：按原曲校准时间轴，用 kepu3d/stills.mjs 批量出帧并拼图。"""
    an = _analysis(topic, _find_bgm(args))
    tl = render.build_timeline(topic, an)
    subs = three.subshots(tl, an)
    three.stage_assets(topic.slug, None)
    times = [float(x) for x in args.stills.split(",")]
    for name in ([args.only] if args.only else ["vertical"]):
        p = three.props(tl, an, config.LAYOUTS[name], topic, subs, "")
        pngs = three.stills(p, [int(round(t * FPS)) for t in times], out / f"stills_{name}", out / f"props_{name}.json")
        three.contact_sheet(list(zip(times, pngs)), out / f"stills_{name}.png")
        print(out / f"stills_{name}.png")


def covers_three(topic: Topic, args, out: Path, an):
    """renderer=three 的封面：钩子镜头撞击后的一帧 + 封面主副标题。"""
    tl = render.build_timeline(topic, an)
    subs = three.subshots(tl, an)
    three.stage_assets(topic.slug, None)
    for name in ([args.only] if args.only else ["vertical", "horizontal"]):
        p = three.props(tl, an, config.LAYOUTS[name], topic, subs, "", cover=True)
        p["cover"]["at"] = tl.cues[tl.shots[0].no].get("hook", 0.0) + 0.2
        png = three.stills(p, [0], out / "cover_tmp", out / f"props_cover_{name}.json", comp="Cover")[0]
        png.replace(out / f"cover_{name}.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", required=True, help="topics/<slug> 的目录名")
    ap.add_argument("--bgm", default=None)
    ap.add_argument("--out", default=None, help="默认 out/<slug>")
    ap.add_argument("--only", choices=["vertical", "horizontal"], default=None)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--covers-only", action="store_true")
    ap.add_argument("--stills", default=None, help="逗号分隔的秒数：只输出抽帧拼图 stills.png")
    ap.add_argument("--delivery-only", action="store_true", help="只根据已有核验文件重写 DELIVERY.md")
    args = ap.parse_args()
    topic = load(args.topic)
    out = Path(args.out) if args.out else ROOT / "out" / topic.slug
    out.mkdir(parents=True, exist_ok=True)
    if args.delivery_only:
        write_delivery(out, topic)
        print(out / "DELIVERY.md")
        return
    problems = layout_check(render.build_timeline(topic))
    if problems:
        raise SystemExit("layout check failed:\n  " + "\n  ".join(problems))
    if args.stills and topic.renderer == "three":
        stills_three(topic, args, out)
        return
    if args.stills:
        contact_sheet(render.build_timeline(topic), [float(x) for x in args.stills.split(",")], out / "stills.png")
        print(out / "stills.png")
        return
    if args.covers_only and topic.renderer == "three":
        covers_three(topic, args, out, _analysis(topic, _find_bgm(args)))
        return
    if args.covers_only:
        for name, L in config.LAYOUTS.items():
            cv2.imwrite(str(out / f"cover_{name}.png"), cv2.cvtColor(render.cover(L, topic), cv2.COLOR_RGBA2BGR))
        return
    (out / "sfx_samples").mkdir(parents=True, exist_ok=True)
    (out / "check").mkdir(exist_ok=True)
    report = {"generated": time.strftime("%Y-%m-%d %H:%M:%S")}

    search = BGM_SEARCH
    bgm = _find_bgm(args)
    an = None
    if bgm is not None and bgm.exists():
        an = _analysis(topic, bgm)
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
    if tl.reframes:
        report["reframes"] = [f"镜头{e['shot']} {e['t']:.2f}s（{render.POS_NAME[e['beat'].pos] if e.get('beat') else '空档中点'}）"
                              for e in tl.events if e["key"].startswith("reframe")]
        report["max_event_gap"] = event_gap(tl)
    rows = reading_table(tl)
    report["reading"] = rows
    write_captions(out / "captions.txt", tl, rows, topic)
    (out / "references.txt").write_text(topic.references, encoding="utf-8")

    if topic.renderer == "three":
        if an is None:
            raise SystemExit("renderer=three 需要原曲（music/bgm.m4a）：子镜头切点只取原曲节拍")
        subs = three.subshots(tl, an)
        three.stage_assets(topic.slug, audio_for_video)
        report["subshots"] = subs
        report["max_event_gap"] = three.event_gap(tl, subs)
        for name in ([args.only] if args.only else ["vertical", "horizontal"]):
            L = config.LAYOUTS[name]
            p = three.props(tl, an, L, topic, subs, f"{topic.slug}/mix.wav")
            mp4 = out / f"{topic.slug}_{name}.mp4"
            t0 = time.time()
            three.render(p, mp4, out / f"props_{name}.json", workers=args.workers)
            report.setdefault("render_seconds", {})[name] = round(time.time() - t0, 1)
            report.setdefault("ffprobe", {})[name] = ffprobe(mp4)
            report.setdefault("blackdetect", {})[name] = blackdetect(mp4)
            report.setdefault("loudness_ffmpeg", {})[name] = ebur128(mp4)
            extract_frames(mp4, out / "check", check_times(tl))
            fr = three.decode_gray(mp4)
            report.setdefault("visual_hits", {})[name] = three.visual_hits(fr, tl.events)
            report.setdefault("cut_check", {})[name] = three.cut_check(fr, subs)
            report.setdefault("change_3s", {})[name] = three.change_3s(fr)
        covers_three(topic, args, out, an)
        (out / "verify_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1, default=str),
                                                encoding="utf-8")
        write_delivery(out, topic)
        print(json.dumps({k: report[k] for k in ("ffprobe", "blackdetect", "loudness_ffmpeg") if k in report},
                         ensure_ascii=False, indent=1))
        return

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
        if topic.motion == "max":
            report.setdefault("change_3s", {})[name] = change_3s(tl, L)

    (out / "verify_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1, default=str),
                                            encoding="utf-8")
    write_delivery(out, topic)
    print(json.dumps({k: report[k] for k in ("ffprobe", "blackdetect", "loudness_ffmpeg") if k in report},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
