"""《一把伞的雪夜》（夜色像素风）：时间表与混音。

画面在 weilanx-claude-videos 工程里用 Remotion 渲染（src/episodes/ep52-umbrella/），这里负责两件事：
1. 用 engine/bgm.py 的 detect() 测 music/bgm.m4a 的实测拍点，把每个画面节点吸附到最近的拍点上，写出 timeline.json；
2. 渲染完成后，用 engine/perc.py 合成打击乐音效（峰值对齐撞击帧），与配乐混音、统一响度、限真峰值，封装成片。

用法：
    python3 -m nightpixel.umbrella --plan <episode目录>          # 写 timeline.json
    python3 -m nightpixel.umbrella --mix <无声成片.mp4> <输出目录>   # 混音 + 封装 + 卡点表 + 核验
"""

import csv
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy import signal

from engine import audio, bgm, perc

FPS = 30
END = 89.0
DET = bgm.detect()
BT = [b["t"] for b in DET["beats"]]

LEVEL = {"wood_high": 0.3, "wood_low": 0.34, "rim": 0.3, "shaker": 0.24, "clap": 0.32, "kick": 0.5, "kick_light": 0.45,
         "cymbal": 0.26, "tom": 0.42}

cues: dict[str, int] = {}
events: list[dict] = []


def bidx(t: float) -> int:
    return int(np.argmin([abs(b - t) for b in BT]))


def cue(name: str, t: float, sfx: str | None = None, gain: float = 1.0, note: str = "") -> float:
    """把目标时刻 t 吸附到最近的实测拍点，记下帧号；sfx 不为空时在该拍放一个打击乐音效。"""
    i = bidx(t)
    tt = BT[i]
    cues[name] = int(round(tt * FPS))
    if sfx:
        b = DET["beats"][i]
        if sfx == "kick" and b["low"] >= 0.7:
            sfx = "kick_light"
        events.append(dict(t=tt, frame=cues[name], beat=i, bar_pos=b["bar_pos"], sfx=sfx, gain=gain, note=note or name))
    return tt


def plan() -> dict:
    # 1 开场聊天窗（第 1 段 0–8.6 秒）
    cue("s1", 0.0)
    cue("chat_b1", 1.18, "wood_high", 0.9, "气泡：门口有把旧伞")
    cue("cap1", 1.7)
    cue("chat_b2", 3.85, "wood_high", 0.8, "气泡：用完放哪")
    cue("chat_b3", 5.98, "wood_high", 0.8, "气泡：放回来就行")
    cue("typing", 6.9)
    # 2 伞柄上的卡（第 2 段起 8.6 秒）
    cue("s2", 8.63, "tom", 0.6, "信笺糊化进入")
    cue("card1_write", 9.2)
    cue("cap2", 12.9)
    # 3 drop：街景，学生把伞递给骑手
    cue("s3", 17.14, "kick", 1.0, "音乐 drop：硬切到雪夜街景")
    cue("rider_in", 18.2)
    cue("pass1", 20.2)
    cue("pass1_end", 20.9, "wood_high", 0.9, "伞递到骑手手里")
    cue("cap3b", 21.4)
    # 4 骑手写卡、红笔批改、重写、盖章
    cue("s4", 23.7, "wood_low", 0.8, "信笺糊化进入")
    cue("card2_write", 24.3)
    cue("card2_mark", 26.4, "rim", 0.8, "红圈：明早就还")
    cue("card2_note", 27.4, "wood_low", 0.7, "红字批注")
    cue("card2_strike", 27.9, "rim", 0.7, "划掉")
    cue("card2_redo", 28.95)
    cue("card2_stamp", 30.55, "clap", 0.9, "通过章：接力")
    cue("cap4", 31.0)
    # 5 接力加速硬切：6 刀，4/4/3/3/2/2 拍，结束于高潮前 2 拍
    hit = bidx(42.64)
    lens = [4, 4, 3, 3, 2, 2]
    start = hit - 2 - sum(lens)
    relay = []
    k = start
    for j, n in enumerate(lens):
        f0, f1 = int(round(BT[k] * FPS)), int(round(BT[k + n] * FPS))
        relay.append(dict(at=f0, len=f1 - f0))
        b = DET["beats"][k]
        events.append(dict(t=BT[k], frame=f0, beat=k, bar_pos=b["bar_pos"], sfx="rim" if j == 0 else "shaker", gain=0.8,
                           note=f"接力硬切 {j + 1}"))
        k += n
    cues["s5"] = relay[0]["at"]
    # 6 高潮：雪落在「还」字上，变成「传」
    cue("s6", BT[hit - 2])
    cue("swap", BT[hit], "kick", 1.0, "高潮：雪落改字 还→传")
    cue("swap_cym", BT[hit], "cymbal", 0.8, "高潮吊镲")
    cue("cap6", 44.3)
    # 7 伞继续往前走
    cue("s7", 47.5, "tom", 0.5, "街景远景")
    # 8 第二天早上（第 51.2 秒段落）
    cue("s8", 51.15, "tom", 0.7, "暖光店里")
    cue("cap8", 52.0)
    # 9 卡的背面：三行
    cue("s9", 59.6, "wood_low", 0.8, "卡的背面 1")
    cue("cap9", 60.6)
    cue("s9b", 63.8, "wood_low", 0.7, "卡的背面 2")
    cue("s9c", 68.1, "wood_low", 0.7, "卡的背面 3")
    # 10 收尾聊天窗（第 72.4 秒段落）
    cue("s10", 72.41, "tom", 0.6, "收尾聊天窗")
    cue("end_b1", 73.5, "wood_high", 0.8, "气泡：那把伞还没回来")
    cue("end_b2", 76.2, "wood_high", 0.8, "气泡：在我这，雪还没停")
    cue("end_b3", 78.9, "wood_high", 0.9, "气泡：那就别还了")
    cue("cap10", 80.9)
    # 11 片尾题字（第 85.1 秒段落）
    cue("s11", 85.15, "cymbal", 0.5, "片尾题字")
    return dict(fps=FPS, end=int(round(END * FPS)), cues=cues, relay=relay,
                sfx=sorted(events, key=lambda e: e["t"]))


# ---------------------------------------------------------------- 混音

def music_track(n: int) -> np.ndarray:
    y = bgm.load()[:n].astype(np.float64)
    fade = int(1.5 * audio.SR)
    y[-fade:] *= np.linspace(1, 0, fade)[:, None]
    return y


def mix(tl: dict):
    import pyloudnorm

    sr = audio.SR
    n = int(END * sr)
    music = music_track(n)
    sfx = np.zeros((n, 2))
    out = []
    for e in tl["sfx"]:
        clip = perc.sound(e["sfx"]) * LEVEL[e["sfx"]] * e["gain"]
        lead = perc.attack_ms(e["sfx"]) / 1000
        i = int(round((e["frame"] / FPS - lead) * sr))
        seg = sfx[i: i + len(clip)]
        seg += audio.pan(clip[: len(seg)], 0)
        out.append(dict(e, frame_err=round((i / sr + lead) * FPS - e["frame"], 2)))
    meter = pyloudnorm.Meter(sr)
    m = music + sfx
    g = 10 ** ((-14.0 - meter.integrated_loudness(m)) / 20)
    m = m * g
    tp = np.abs(signal.resample_poly(m, 4, 1, axis=0)).max()
    if tp > 10 ** (-2.0 / 20):
        m *= 10 ** (-2.0 / 20) / tp
    return m.astype(np.float32), out


def finish(silent: Path, out_dir: Path, ep: Path):
    tl = json.loads((ep / "timeline.json").read_text(encoding="utf-8"))
    out_dir.mkdir(parents=True, exist_ok=True)
    m, evs = mix(tl)
    wav = out_dir / "mix.wav"
    audio.write_wav(str(wav), m) if hasattr(audio, "write_wav") else _write(wav, m)
    mp4 = out_dir / "一把伞的雪夜.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(silent), "-i", str(wav), "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-pix_fmt", "yuv420p", "-color_range", "tv", "-movflags", "+faststart",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", str(mp4)], check=True)
    wav.unlink()
    with open(out_dir / "cue_sheet.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["时间", "帧", "实测拍序号", "小节内位置", "动作", "音色", "音画偏差(帧)"])
        for e in evs:
            w.writerow([f"{e['t']:.3f}", e["frame"], e["beat"], e["bar_pos"], e["note"], perc.TIMBRES[e["sfx"]], e["frame_err"]])
    info = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_name,width,height,r_frame_rate,pix_fmt",
                                      "-show_entries", "format=duration", "-of", "json", str(mp4)], capture_output=True, text=True).stdout)
    v = next(s for s in info["streams"] if s["codec_name"] == "h264")
    err = subprocess.run(["ffmpeg", "-nostats", "-i", str(mp4), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    lufs = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1])
    tp = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", err)[-1])
    worst = max(abs(e["frame_err"]) for e in evs)
    dur = float(info["format"]["duration"])
    ok = abs(dur - END) < 0.1 and worst <= 1 and tp <= -0.5 and v["pix_fmt"] == "yuv420p"
    line = (f"{'✓' if ok else '✗'} {dur:.2f}s，{v['width']}×{v['height']} {v['r_frame_rate']} {v['pix_fmt']}，{lufs:.1f} LUFS / {tp:.1f} dBTP，"
            f"{len(evs)} 个音效，最大音画偏差 {worst:.2f} 帧")
    (out_dir / "核验.txt").write_text(line + "\n", encoding="utf-8")
    print(line)


def _write(path: Path, m: np.ndarray):
    import wave
    x = (np.clip(m, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(audio.SR)
        w.writeframes(x.tobytes())


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "--plan":
        ep = Path(a[1])
        tl = plan()
        (ep / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"写入 {ep / 'timeline.json'}：{len(tl['cues'])} 个节点、{len(tl['sfx'])} 个音效，接力 {[r['len'] for r in tl['relay']]} 帧")
    elif a and a[0] == "--mix":
        plan()
        finish(Path(a[1]), Path(a[2]), Path(a[3]) if len(a) > 3 else Path("."))
    else:
        print(__doc__)
