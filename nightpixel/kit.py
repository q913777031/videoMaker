"""夜色像素风各期共用的时间表与混音工具。

- `Plan`：用 engine/bgm.py 的 detect() 实测拍点，把每个画面节点吸附到最近的拍点上（cue），接力加速硬切按拍数排（relay），
  导出 timeline.json 给 Remotion 读。
- `finish`：渲染出无声成片后，用 engine/perc.py 合成打击乐（起音峰值对齐撞击帧），与 music/bgm.m4a 混音、
  归一到 -14 LUFS、限真峰值 -2 dBTP，重编码为 yuv420p，写卡点表与核验。
"""

import csv
import json
import re
import subprocess
import wave
from pathlib import Path

import numpy as np
from scipy import signal

from engine import audio, bgm, perc

FPS = 30
DET = bgm.detect()
BT = [b["t"] for b in DET["beats"]]
LEVEL = {"wood_high": 0.3, "wood_low": 0.34, "rim": 0.3, "shaker": 0.24, "clap": 0.32, "kick": 0.5, "kick_light": 0.45,
         "cymbal": 0.26, "tom": 0.42}


def bidx(t: float) -> int:
    return int(np.argmin([abs(b - t) for b in BT]))


class Plan:
    def __init__(self, end: float):
        self.end = end
        self.cues: dict[str, int] = {}
        self.events: list[dict] = []
        self.relay: list[dict] = []

    def cue(self, name: str, t: float, sfx: str | None = None, gain: float = 1.0, note: str = "") -> float:
        """把目标时刻 t 吸附到最近的实测拍点，记下帧号；sfx 不为空时在该拍放一个打击乐音效。"""
        i = bidx(t)
        self.cues[name] = int(round(BT[i] * FPS))
        if sfx:
            self._event(i, sfx, gain, note or name)
        return BT[i]

    def _event(self, i: int, sfx: str, gain: float, note: str):
        b = DET["beats"][i]
        if sfx == "kick" and b["low"] >= 0.7:
            sfx = "kick_light"
        self.events.append(dict(t=BT[i], frame=int(round(BT[i] * FPS)), beat=i, bar_pos=b["bar_pos"], sfx=sfx, gain=gain, note=note))

    def relay_cuts(self, end_t: float, lens: list[int], name: str = "接力硬切"):
        """以 end_t 附近的拍为终点，往前排一串硬切（每段的拍数见 lens），每刀一个音效。返回起点拍序号。"""
        k = bidx(end_t) - sum(lens)
        start = k
        for j, n in enumerate(lens):
            f0, f1 = int(round(BT[k] * FPS)), int(round(BT[k + n] * FPS))
            self.relay.append(dict(at=f0, len=f1 - f0))
            self._event(k, "rim" if j == 0 else "shaker", 0.8, f"{name} {j + 1}")
            k += n
        return start

    def dump(self, ep: Path):
        tl = dict(fps=FPS, end=int(round(self.end * FPS)), cues=self.cues, relay=self.relay, sfx=sorted(self.events, key=lambda e: e["t"]))
        (ep / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"写入 {ep / 'timeline.json'}：{len(self.cues)} 个节点、{len(self.events)} 个音效，接力 {[r['len'] for r in self.relay]} 帧")
        return tl


def _mix(tl: dict, end: float):
    import pyloudnorm

    sr = audio.SR
    n = int(end * sr)
    music = bgm.load()[:n].astype(np.float64)
    fade = int(1.5 * sr)
    music[-fade:] *= np.linspace(1, 0, fade)[:, None]
    sfx = np.zeros((n, 2))
    out = []
    for e in tl["sfx"]:
        clip = perc.sound(e["sfx"]) * LEVEL[e["sfx"]] * e["gain"]
        lead = perc.attack_ms(e["sfx"]) / 1000
        i = int(round((e["frame"] / FPS - lead) * sr))
        seg = sfx[i: i + len(clip)]
        seg += audio.pan(clip[: len(seg)], 0)
        out.append(dict(e, frame_err=round((i / sr + lead) * FPS - e["frame"], 2)))
    m = music + sfx
    m *= 10 ** ((-14.0 - pyloudnorm.Meter(sr).integrated_loudness(m)) / 20)
    tp = np.abs(signal.resample_poly(m, 4, 1, axis=0)).max()
    if tp > 10 ** (-2.0 / 20):
        m *= 10 ** (-2.0 / 20) / tp
    return m.astype(np.float32), out


def finish(silent: Path, out_dir: Path, ep: Path, name: str):
    tl = json.loads((ep / "timeline.json").read_text(encoding="utf-8"))
    end = tl["end"] / FPS
    out_dir.mkdir(parents=True, exist_ok=True)
    m, evs = _mix(tl, end)
    wav = out_dir / "mix.wav"
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(audio.SR)
        w.writeframes((np.clip(m, -1, 1) * 32767).astype("<i2").tobytes())
    mp4 = out_dir / f"{name}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(silent), "-i", str(wav), "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
                    "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-color_range", "tv", "-movflags", "+faststart",
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
    ok = abs(dur - end) < 0.1 and worst <= 1 and tp <= -0.5 and v["pix_fmt"] == "yuv420p"
    line = (f"{'✓' if ok else '✗'} {dur:.2f}s，{v['width']}×{v['height']} {v['r_frame_rate']} {v['pix_fmt']}，{lufs:.1f} LUFS / {tp:.1f} dBTP，"
            f"{len(evs)} 个音效，最大音画偏差 {worst:.2f} 帧")
    (out_dir / "核验.txt").write_text(line + "\n", encoding="utf-8")
    print(line)
