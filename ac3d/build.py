"""国风 3D 科普短片构建：分镜（story.py）→ 实测拍点时间轴 → 配乐 + 中国打击乐音效 → 3D 逐帧渲染 → 混流与核验。

用法：
    python3 -m ac3d.build                 # 完整成片 out/ac3d/
    python3 -m ac3d.build --timeline      # 只生成 web/timeline.json（检查画面前先运行）
    python3 -m ac3d.build --stills 3.2,17.5   # 生成时间轴并导出静帧到 out/ac3d/stills/
    python3 -m ac3d.build --stills 3.2 --only hook   # 只构建指定镜头，启动更快
    python3 -m ac3d.build --audio         # 只出音频分轨与卡点表
    python3 -m ac3d.build --verify        # 核验已渲染成片

时间轴规则与阿德勒系列一致：镜头以小节（4 个实测拍点）为单位，带音效的动作必须落在整数拍（实测拍点），
音效按起音峰值提前放置，峰值与画面撞击帧同帧或相邻帧。
"""

import csv
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal

from adler import core as A          # 复用：实测拍点缓存、原曲配乐（含尾音混响）、拍点插值
from engine import audio, perc

from . import story as S

ROOT = Path(__file__).resolve().parent.parent
WEB = Path(__file__).resolve().parent / "web"
OUT = ROOT / "out" / "ac3d"
FPS = 30
END = A.END

SFX_LEVEL = {"tanggu": 0.55, "dagu": 0.6, "daluo": 0.42, "xiaoluo": 0.32, "naobo": 0.3, "bangzi": 0.34, "muyu": 0.34,
             "bianzhong": 0.3, "kick": 0.5, "kick_light": 0.5, "wood_high": 0.3, "shaker": 0.22}
DUCK_DEPTH = {"tanggu": 0.2, "dagu": 0.24, "daluo": 0.2, "xiaoluo": 0.08, "naobo": 0.12, "bianzhong": 0.1, "kick": 0.2}


# ---------------------------------------------------------------- 时间轴

def timeline() -> dict:
    """把分镜换算成全片时间：镜头起止取实测强拍，动作与字幕取镜头内第 k 个实测拍点。"""
    shots, cues, caps, events = [], {}, [], []
    b = 0
    for i, s in enumerate(S.SHOTS):
        t0 = 0.0 if i == 0 else A.bt(b)
        b1 = b + 4 * s.bars
        t1 = A.bt(b1) if b1 < A.N_BEATS else END
        for name, k in s.cues.items():
            cues[f"{s.name}.{name}"] = round(A.bt(b + k), 4)
        for name, sfx, gain, note in s.sfx:
            k = s.cues[name]
            if abs(k - round(k)) > 1e-9:
                raise ValueError(f"{s.name}.{name}: sfx on fractional beat {k}")
            gi = b + int(round(k))
            events.append(dict(shot=i + 1, name=f"{s.name}.{name}", beat=gi, t=A.BEATS[gi]["t"], b=A.BEATS[gi], sfx=sfx,
                               gain=gain, note=note))
        for c in s.caps:
            c0 = A.bt(b + c.at)
            c1 = A.bt(b + c.out) if c.out is not None else (t1 if b1 < A.N_BEATS else END - 1.4)
            caps.append(dict(t0=round(c0, 4), t1=round(c1 - 0.02, 4), text=c.text, note=c.note, shot=i + 1))
        shots.append(dict(name=s.name, t0=round(t0, 4), t1=round(t1, 4), tag=s.tag, transition=s.transition, bars=s.bars,
                          note=s.note))
        b = b1
    if b != A.LAST_BAR * 4:
        raise ValueError(f"story covers {b // 4} bars, music has {A.LAST_BAR}")
    shots[-1]["t1"] = END
    events.sort(key=lambda e: e["t"])
    return dict(series=S.SERIES, title_short=S.TITLE_SHORT, title=S.TITLE, refs=S.REFS_SHORT, end=END, music_end=A.MUSIC_END,
                beats=[x["t"] for x in A.BEATS], shots=shots, cues=cues, captions=caps, _events=events)


def write_timeline(tl: dict) -> Path:
    p = WEB / "timeline.json"
    p.write_text(json.dumps({k: v for k, v in tl.items() if not k.startswith("_")}, ensure_ascii=False))
    return p


_HAN = re.compile(r"[一-鿿]")


def read_check(tl: dict) -> list[str]:
    """字幕阅读窗：稳定显示 ≥ max(2 秒, 汉字数 / 4.5)，含数字或英文另加 1 秒。"""
    out = []
    for c in tl["captions"]:
        n = len(_HAN.findall(c["text"]))
        need = max(2.0, n / 4.5) + (1.0 if re.search(r"[0-9A-Za-z%]", c["text"]) else 0.0)
        stable = (c["t1"] - c["t0"]) - 0.38 - 0.28
        if stable < need:
            out.append(f"镜头{c['shot']}「{c['text']}」稳定 {stable:.2f}s < 预算 {need:.2f}s")
        if len(c["text"].split("|")) > 2:
            out.append(f"镜头{c['shot']}「{c['text']}」超过 2 行")
    return out


# ---------------------------------------------------------------- 音频

def build_audio(tl: dict):
    """返回 (混音, 配乐分轨, 音效分轨, 音效清单)；两条分轨乘同一个总增益，相加即限幅前混音。"""
    import pyloudnorm

    sr = audio.SR
    n = int(END * sr)
    music = A.music_track()
    sfx = np.zeros((n, 2))
    duck = np.zeros(n)
    rel = np.exp(-np.arange(int(0.45 * sr)) / sr / 0.16)
    att = int(0.012 * sr)
    events = []
    for e in tl["_events"]:
        name = e["sfx"]
        if name == "kick" and e["b"]["low"] >= 0.7:
            name = "kick_light"
        clip = perc.sound(name) * SFX_LEVEL[name] * e["gain"]
        lead = perc.attack_ms(name) / 1000
        i = int(round((e["t"] - lead) * sr))
        seg = sfx[i: i + len(clip)]
        seg += audio.pan(clip[: len(seg)], 0)
        d = DUCK_DEPTH.get(name, 0.05) * e["gain"]
        a0 = max(0, i - att)
        duck[a0:i] = np.maximum(duck[a0:i], np.linspace(0, d, i - a0))
        tail = duck[i: i + len(rel)]
        duck[i: i + len(rel)] = np.maximum(tail, d * rel[: len(tail)])
        frame = int(round(e["t"] * FPS))
        events.append(dict(e, sfx=name, frame=frame, frame_err=round((i / sr + lead) * FPS - frame, 2)))
    duck = signal.lfilter([0.02], [1, -0.98], duck)
    music_d = music * (1 - np.clip(duck, 0, 0.3))[:, None]
    meter = pyloudnorm.Meter(sr)
    mix = music_d + sfx
    g = 10 ** ((-14.0 - meter.integrated_loudness(mix)) / 20)
    music_d, sfx = music_d * g, sfx * g
    mix = music_d + sfx
    a = np.abs(mix)
    knee, ceil = 0.6, 0.84
    over = a > knee
    mix[over] = np.sign(mix[over]) * (knee + (ceil - knee) * np.tanh((a[over] - knee) / (ceil - knee)))
    return mix.astype(np.float32), music_d.astype(np.float32), sfx.astype(np.float32), events


# ---------------------------------------------------------------- 文档

def tc(t: float) -> str:
    f = int(round(t * FPS))
    return f"{f // FPS // 60:02d}:{f // FPS % 60:02d}:{f % FPS:02d}"


def write_docs(tl: dict, events: list[dict], out: Path):
    with open(out / "cue_sheet.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["时间", "帧", "实测拍序号", "小节内位置", "重音值", "镜头", "动作", "音色", "音画偏差(帧)"])
        for e in events:
            w.writerow([f"{e['t']:.3f}", e["frame"], e["beat"], e["b"]["bar_pos"], f"{A.accent(e['b']):.2f}", e["shot"],
                        e["note"], perc.TIMBRES[e["sfx"]], e["frame_err"]])
    lines = [f"# {S.TITLE}", "", f"- 发布标题：{S.PUBLISH_TITLE}", f"- 话题：{S.HASHTAGS}",
             f"- 时长：{END:.1f} 秒（1080×1920，30fps；配乐 music/bgm.m4a，镜头边界与音效落在实测拍点上）", "",
             "## 逐屏文案", "", "| # | 时间（分:秒:帧） | 角标 | 屏幕文字 | 画面 |", "|---|------|------|----------|------|"]
    for i, s in enumerate(tl["shots"]):
        caps = "；".join(c["text"].replace("|", "／") + (f"（小字：{c['note']}）" if c["note"] else "")
                        for c in tl["captions"] if c["shot"] == i + 1) or "—"
        lines.append(f"| {i + 1} | {tc(s['t0'])}–{tc(s['t1'])} | {s['tag']} | {caps} | {s['note']} |")
    lines += ["", "## 依据与出处", ""] + [f"- {r}" for r in S.REFS]
    if S.NOTES:
        lines += ["", "## 事实核查与表述说明", ""] + [f"- {n}" for n in S.NOTES]
    (out / "文案与出处.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- 渲染与核验

def node(*args):
    subprocess.run(["node", str(Path(__file__).resolve().parent / "render.cjs"), *args], check=True)


def verify(mp4: Path, events: list[dict]) -> str:
    info = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                      "stream=codec_name,width,height,r_frame_rate,pix_fmt,sample_rate",
                                      "-show_entries", "format=duration", "-of", "json", str(mp4)],
                                     capture_output=True, text=True).stdout)
    v = next(s for s in info["streams"] if s["codec_name"] == "h264")
    err = subprocess.run(["ffmpeg", "-nostats", "-i", str(mp4), "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    lufs = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1])
    tp = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", err)[-1])
    dur = float(info["format"]["duration"])
    worst = max(abs(e["frame_err"]) for e in events)
    ok = (v["width"], v["height"]) == (1080, 1920) and v["r_frame_rate"] == "30/1" and abs(dur - END) < 0.05 \
        and worst <= 1.0 and tp <= -0.5
    return (f"{'✓' if ok else '✗'} {dur:.2f}s，{v['width']}×{v['height']} {v['r_frame_rate']} {v['pix_fmt']}，"
            f"{lufs:.1f} LUFS / {tp:.1f} dBTP，{len(events)} 个音效，最大音画偏差 {worst:.2f} 帧")


def main():
    args = sys.argv[1:]
    tl = timeline()
    write_timeline(tl)
    for w in read_check(tl):
        print("  阅读窗警告：" + w, file=sys.stderr)
    if "--timeline" in args:
        print(WEB / "timeline.json")
        return
    if "--stills" in args:
        times = args[args.index("--stills") + 1]
        extra = ["--only", args[args.index("--only") + 1]] if "--only" in args else []
        node("--stills", str(OUT / "stills"), times, *extra)
        return
    OUT.mkdir(parents=True, exist_ok=True)
    mix, music, sfx, events = build_audio(tl)
    sf.write(OUT / "bgm_track.wav", music, audio.SR, subtype="PCM_16")
    sf.write(OUT / "sfx_track.wav", sfx, audio.SR, subtype="PCM_16")
    write_docs(tl, events, OUT)
    print(f"音效 {len(events)} 个，最大音画偏差 {max(abs(e['frame_err']) for e in events):.2f} 帧")
    if "--audio" in args:
        return
    final = OUT / f"{S.FILE_NAME}.mp4"
    if "--verify" not in args:
        with tempfile.TemporaryDirectory() as tmp:
            silent = Path(tmp) / "silent.mp4"
            wav = Path(tmp) / "mix.wav"
            sf.write(wav, mix, audio.SR)
            node("--video", str(silent), "--workers", "4")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-i", str(wav), "-map", "0:v", "-map", "1:a",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-maxrate", "8M", "-bufsize", "16M",
                            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
                            str(final)], check=True)
    report = verify(final, events)
    (OUT / "核验.txt").write_text(report + "\n", encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
