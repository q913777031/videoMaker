"""混音：音效按事件帧放置、按局部音乐电平定增益、平滑避让、响度与真峰值测量，导出三条 24 bit WAV。

响度目标 -16 LUFS-I、真峰值 ≤ -1 dBTP 只是起始目标：若达到 -16 会让真峰值超标，则降低整体增益，
不使用削波或限幅器，并在报告中写明实测值。
"""

import numpy as np
import pyloudnorm as pyln
import soundfile as sf
from scipy import signal

from . import sfx as S
from .story import FPS

SR = S.SR
SPF = SR // FPS  # 每帧 1600 个采样


def true_peak_db(x: np.ndarray) -> float:
    """4 倍过采样估计真峰值（dBTP）。"""
    up = signal.resample_poly(x, 4, 1, axis=0)
    return float(20 * np.log10(np.max(np.abs(up)) + 1e-12))


def _local(x: np.ndarray, i: int, half: float, f=None) -> float:
    a, b = max(0, i - int(half * SR)), min(len(x), i + int(half * SR))
    seg = x[a:b].mean(axis=1)
    if f is not None:
        seg = signal.sosfilt(signal.butter(2, f, "lowpass", fs=SR, output="sos"), seg)
    return float(np.sqrt(np.mean(seg ** 2)) + 1e-9)


def _duck_env(n: int, hits: list[tuple[int, float]]) -> np.ndarray:
    """以余弦曲线平滑的避让包络：起音前 10 ms 开始下压、保持 80 ms、300 ms 回升，避免抽吸感。"""
    g = np.zeros(n)
    att, hold, rel = int(0.010 * SR), int(0.080 * SR), int(0.300 * SR)
    shape = np.concatenate([0.5 - 0.5 * np.cos(np.linspace(0, np.pi, att)), np.ones(hold),
                            0.5 + 0.5 * np.cos(np.linspace(0, np.pi, rel))])
    for i, db in hits:
        a = i - att
        seg = shape[max(0, -a):]
        a = max(a, 0)
        b = min(n, a + len(seg))
        g[a:b] = np.maximum(g[a:b], seg[:b - a] * db)
    return 10 ** (-g / 20)


def music_segment(x: np.ndarray, seg: dict, song_dur: float, n: int) -> tuple[np.ndarray, str]:
    """截取选定片段并做首尾包络，返回 (音轨, 收尾说明)。
    非曲首起点加 30 ms 淡入。只有「片段终点 = 曲尾」且曲尾 0.5 秒已比全片中位电平低 20 dB 以上（原曲自带淡出）时，
    才保留自然尾韵只做 0.3 秒收尾；否则做 3 秒余弦淡出，避免突然截断。"""
    a = int(round(seg["start"] * SR))
    m = x[a:a + n].copy()
    if len(m) < n:
        m = np.pad(m, ((0, n - len(m)), (0, 0)))
    if a > 0:
        k = int(0.03 * SR)
        m[:k] *= np.linspace(0, 1, k)[:, None]
    mono = m.mean(axis=1)
    blk = int(0.5 * SR)
    levels = [np.sqrt(np.mean(mono[i:i + blk] ** 2)) + 1e-9 for i in range(0, len(mono) - blk, blk)]
    tail_db = 20 * np.log10(np.sqrt(np.mean(mono[-blk:] ** 2)) + 1e-9)
    med_db = 20 * np.log10(float(np.median(levels)))
    natural = abs(seg["end"] - song_dur) < 0.5 and tail_db < med_db - 20
    fade = 0.3 if natural else 3.0
    k = int(fade * SR)
    m[-k:] *= (0.5 + 0.5 * np.cos(np.linspace(0, np.pi, k)))[:, None]
    note = (f"原曲自带淡出（曲尾 {tail_db:.1f} dB，中位 {med_db:.1f} dB），保留自然尾韵，仅 0.3 秒收尾" if natural else
            f"片段末 0.5 秒仍为 {tail_db:.1f} dB（全片中位 {med_db:.1f} dB），原曲未自带淡出，做 3 秒余弦淡出避免截断")
    return m, note


def build(music: np.ndarray, timeline, target_lufs: float = -16.0, tp_limit: float = -1.0) -> dict:
    """返回 {bgm, sfx, mix, report}；三条音轨同起点、同长度（= 总帧数 × 1600 采样）。"""
    n = timeline.total_frames * SPF
    bank = S.bank()
    fx = np.zeros((n, 2))
    hits = []
    lows = [_local(music, i, 0.05, 120) for i in range(SR // 2, n - SR // 2, SR // 10)]
    music_low_ref = float(np.percentile(lows, 90)) if lows else 1e-3
    for e in timeline.events:
        if not e.sfx:
            continue
        i = e.frame * SPF
        clip = bank[e.sfx]
        gain_db = e.gain_db
        if e.sfx == "low_drum":
            ratio = _local(music, i, 0.05, 120) / music_low_ref
            if ratio > 1.5:
                e.mix_note = (e.mix_note + "；" if e.mix_note else "") + f"原曲此处低频已强（{ratio:.2f}× 片段 90 分位），取消低鼓叠加"
                e.sfx = None
                continue
            if ratio > 0.8:
                gain_db -= 6.0
                e.mix_note = (e.mix_note + "；" if e.mix_note else "") + f"原曲此处低频较强（{ratio:.2f}× 片段 90 分位），低鼓降 6 dB"
        ref = max(_local(music, i, 0.2), 0.02)
        lift = 2.0 if e.mode == "strong" else 0.0
        amp = ref * 1.4 * 10 ** ((gain_db + lift - 3.0) / 20) / S.PEAK
        b = min(n, i + len(clip))
        fx[i:b] += clip[:b - i] * amp
        if e.mode == "strong" or e.sfx in ("low_drum", "snare_rim"):
            hits.append((i, 2.0))
            e.mix_note = (e.mix_note + "；" if e.mix_note else "") + "音乐平滑避让 2 dB（10/80/300 ms）"
        e.mix_note = e.mix_note or "按局部音乐电平 -3 dB 放置"
    duck = _duck_env(n, hits)[:, None]
    bgm = music * duck
    mix = bgm + fx

    meter = pyln.Meter(SR)
    lufs = meter.integrated_loudness(mix)
    g = target_lufs - lufs
    tp = true_peak_db(mix) + g
    if tp > tp_limit:
        g -= tp - tp_limit
    G = 10 ** (g / 20)
    bgm, fx, mix = bgm * G, fx * G, mix * G
    report = {"mix_lufs_i": round(meter.integrated_loudness(mix), 2), "mix_true_peak_dbtp": round(true_peak_db(mix), 2),
              "bgm_lufs_i": round(meter.integrated_loudness(bgm), 2),
              "sfx_peak_dbfs": round(float(20 * np.log10(np.max(np.abs(fx)) + 1e-12)), 2),
              "gain_applied_db": round(g, 2), "target": f"{target_lufs} LUFS-I / ≤ {tp_limit} dBTP（起始目标）",
              "limiter": "未使用限幅或削波"}
    if report["mix_lufs_i"] < target_lufs - 0.5:
        report["note"] = "为满足真峰值上限，整体响度低于 -16 LUFS 目标"
    return {"bgm": bgm, "sfx": fx, "mix": mix, "report": report}


def write24(path, x: np.ndarray):
    sf.write(path, x.astype(np.float32), SR, subtype="PCM_24")


def onset_frames(x: np.ndarray, thresh_db: float = -45.0) -> list[int]:
    """在独立音效轨上检测实际起音帧（静音后首次越过阈值），用于核对音画偏差。"""
    m = np.abs(x).max(axis=1)
    k = int(0.001 * SR)
    env = np.maximum.reduceat(m, np.arange(0, len(m), k))
    th = 10 ** (thresh_db / 20)
    out, quiet = [], True
    for j, v in enumerate(env):
        if quiet and v > th:
            out.append(int(j * k / SPF))
            quiet = False
        elif not quiet and v < th * 0.3:
            quiet = env[j:j + 30].max() < th * 0.3 if j + 30 < len(env) else True
    return out
