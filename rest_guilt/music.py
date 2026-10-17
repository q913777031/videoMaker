"""原曲读取与信号分析：解码、起音候选、局部速度、节拍候选、段落新颖度、片段选择。

全部为信号分析结果，是"候选"而不是"已试听确认"。本模块不做循环、变速、拉伸，也不替换曲目；
原曲不足 87 秒时抛出 MusicTooShort，由调用方报告差额并停止出成片。
"""

import json
import subprocess

import numpy as np
from scipy import signal
from scipy.ndimage import median_filter

SR = 48000
HOP = 480  # 10 ms
NFFT = 2048
METHOD = "谱通量起音检测 + 局部自相关速度 + 动态规划节拍候选（信号分析，未经人工试听复核）"


class MusicTooShort(Exception):
    pass


def probe(path: str) -> dict:
    """ffprobe 读取实际容器 / 流信息；文件不可解码时抛出 RuntimeError。"""
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration:stream=codec_name,sample_rate,channels,codec_type",
                        "-of", "json", path], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {r.stderr.strip()}")
    d = json.loads(r.stdout)
    a = [s for s in d.get("streams", []) if s.get("codec_type") == "audio"]
    if not a:
        raise RuntimeError("no audio stream")
    return {"duration": float(d["format"]["duration"]), "codec": a[0]["codec_name"],
            "sample_rate": int(a[0]["sample_rate"]), "channels": int(a[0]["channels"])}


def decode(path: str) -> np.ndarray:
    """解码为 48 kHz 立体声 float32，形状 (n, 2)。"""
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-acodec", "pcm_f32le",
                        "-ac", "2", "-ar", str(SR), "-"], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg decode failed: {r.stderr.decode(errors='replace').strip()}")
    x = np.frombuffer(r.stdout, np.float32).reshape(-1, 2)
    if len(x) == 0:
        raise RuntimeError("decoded audio is empty")
    return x.astype(np.float64)


def _bands(mono: np.ndarray):
    """STFT → 48 条对数间隔频带能量（30 Hz—16 kHz），帧率 100 Hz。"""
    f, t, z = signal.stft(mono, fs=SR, nperseg=NFFT, noverlap=NFFT - HOP, boundary="even", padded=True)
    mag = np.abs(z)
    edges = np.geomspace(30, 16000, 49)
    idx = np.digitize(f, edges) - 1
    B = np.zeros((48, mag.shape[1]))
    for b in range(48):
        sel = idx == b
        if sel.any():
            B[b] = mag[sel].sum(axis=0)
    return t, B, edges


def _refine(mono: np.ndarray, t: float) -> float:
    """精确起音：在 [t-40ms, t+60ms] 内用 512 点（10.7 ms）短窗、2 ms 步长的对数谱通量取最大帧中心。
    谱通量只响应频谱变化，对持续音的拍频纹波不敏感；粗检所用 2048 点居中 STFT 的峰可能比真实起音早约半窗，
    因此窗口向后多看。"""
    a, b = int((t - 0.040) * SR) - 256, int((t + 0.060) * SR) + 256
    a, b = max(a, 0), min(b, len(mono))
    if b - a < 1024:
        return t
    _, tt, z = signal.stft(mono[a:b], fs=SR, nperseg=512, noverlap=512 - 96, boundary=None, padded=False)
    lg = np.log1p(1000 * np.abs(z) / (np.abs(z).max() + 1e-12))
    fl = np.maximum(np.diff(lg, axis=1), 0).sum(axis=0)
    if not len(fl):
        return t
    k = int(np.argmax(fl)) + 1
    return a / SR + float(tt[k])


def _local_tempo(env: np.ndarray, fr: float = 100.0) -> list[dict]:
    """8 秒窗、4 秒步长的起音包络自相关，60—180 BPM；返回每窗速度与峰值清晰度（0—1）。"""
    out = []
    w, h = int(8 * fr), int(4 * fr)
    lo, hi = int(fr * 60 / 180), int(fr * 60 / 60)
    for s in range(0, max(1, len(env) - w), h):
        e = env[s:s + w] - env[s:s + w].mean()
        ac = np.correlate(e, e, "full")[len(e) - 1:]
        if ac[0] <= 0:
            continue
        ac = ac / ac[0]
        lag = lo + int(np.argmax(ac[lo:hi]))
        out.append({"t": s / fr, "bpm": round(60 * fr / lag, 1), "clarity": round(float(ac[lag]), 3)})
    return out


def _beats(env: np.ndarray, tempi: list[dict], fr: float = 100.0) -> list[float]:
    """Ellis 动态规划节拍跟踪，周期取局部速度（允许速度变化）。结果仅作普通拍点候选。"""
    if not tempi:
        return []
    tt = np.array([d["t"] + 4 for d in tempi])
    period = np.interp(np.arange(len(env)) / fr, tt, [60 * fr / d["bpm"] for d in tempi])
    score = env / (env.std() + 1e-9)
    cum = score.copy()
    back = -np.ones(len(env), int)
    for i in range(len(env)):
        P = period[i]
        lo, hi = int(i - 2 * P), int(i - P / 2)
        if hi <= 0:
            continue
        lo = max(lo, 0)
        cand = np.arange(lo, hi)
        pen = -2.0 * np.log((i - cand) / P) ** 2
        j = int(np.argmax(cum[cand] + pen))
        cum[i] = score[i] + cum[cand][j] + pen[j]
        back[i] = cand[j]
    i = int(np.argmax(cum[-int(2 * period[-1]):])) + len(env) - int(2 * period[-1])
    path = []
    while i >= 0:
        path.append(i / fr)
        i = back[i]
    return path[::-1]


def _novelty(B: np.ndarray, fr: float = 100.0, block: float = 0.5, half: int = 8):
    """0.5 秒块的对数频带特征自相似矩阵 + 棋盘核新颖度（左右各 4 秒），用于段落 / 乐句转折候选。"""
    n = int(block * fr)
    m = B.shape[1] // n
    F = np.log1p(B[:, :m * n].reshape(48, m, n).mean(axis=2) * 100)
    F = (F - F.mean(axis=1, keepdims=True))
    F /= np.linalg.norm(F, axis=0, keepdims=True) + 1e-9
    S = F.T @ F
    k = np.ones((2 * half, 2 * half))
    k[:half, half:] = k[half:, :half] = -1
    g = np.outer(signal.windows.gaussian(2 * half, half / 2), signal.windows.gaussian(2 * half, half / 2))
    k *= g
    nov = np.zeros(m)
    for i in range(half, m - half):
        nov[i] = (S[i - half:i + half, i - half:i + half] * k).sum()
    nov = np.maximum(nov, 0)
    nov /= nov.max() + 1e-9
    return np.arange(m) * block, nov


def analyze(x: np.ndarray, info: dict, target: float = 90.0, lo: float = 87.0, hi: float = 93.0) -> dict:
    """完整分析并选定约 90 秒的连续片段；返回片段内（时间以片段起点为 0）的起音、节拍与摘要。"""
    mono = x.mean(axis=1)
    dur = len(mono) / SR
    if dur < lo:
        raise MusicTooShort(f"原曲实测 {dur:.2f} 秒，短于下限 {lo:.0f} 秒，差 {lo - dur:.2f} 秒（距 90 秒差 {target - dur:.2f} 秒）")
    t, B, edges = _bands(mono)
    fr = SR / HOP
    logB = np.log1p(1000 * B / (B.max() + 1e-12))
    flux = np.maximum(np.diff(logB, axis=1, prepend=logB[:, :1]), 0)
    env = flux.sum(axis=0)
    low_env = flux[edges[:-1] < 160].sum(axis=0)
    base = median_filter(env, size=101) + 0.5 * env.std()
    peaks, _ = signal.find_peaks(env, height=base[:len(env)], distance=int(0.1 * fr))
    tempi = _local_tempo(env, fr)
    beats = _beats(env, tempi, fr)
    bt, nov = _novelty(B, fr)

    # 片段选择
    if dur <= hi:
        seg_start, seg_len, why = 0.0, dur, "原曲时长在 87—93 秒内，整首使用"
    else:
        nb = signal.find_peaks(nov, height=0.25, distance=8)[0]
        starts = sorted({0.0, *[float(bt[i]) for i in nb]})
        best = None
        for s in starts:
            if s + lo > dur:
                continue
            for L in np.arange(lo, min(hi, dur - s) + 1e-6, 1 / 30):
                e = s + L
                ni = min(int(e / 0.5), len(nov) - 1)
                end_nov = nov[max(ni - 1, 0):ni + 2].max()
                natural_end = 1.0 if abs(e - dur) < 0.5 else 0.0
                si = min(int(s / 0.5), len(nov) - 1)
                score = (1.0 if s == 0 else nov[si]) + max(end_nov, natural_end) - 0.15 * abs(L - target)
                if best is None or score > best[0]:
                    best = (score, s, float(L))
        _, seg_start, seg_len = best
        why = "按段落新颖度选择起止点（起点与终点贴近乐句转折），并偏好接近 90 秒"
    seg_len = round(seg_len * 30) / 30
    a, b = seg_start, seg_start + seg_len

    times = peaks / fr - 0.5 / fr
    in_seg = (times >= a) & (times < b)
    vals = env[peaks][in_seg]
    norm = float(np.percentile(vals, 99)) if len(vals) else 1.0
    onsets = []
    for p, tm in zip(peaks[in_seg], times[in_seg]):
        tr = _refine(mono, float(tm))
        onsets.append({"t": round(tr - a, 4), "strength": round(min(1.0, env[p] / norm), 3),
                       "low": round(float(low_env[p] / (low_env.max() + 1e-9)), 3)})
    bpm = [d["bpm"] for d in tempi if a - 4 <= d["t"] <= b]
    summary = {
        **info, "decoded_duration": round(dur, 3),
        "segment": f"{a:.3f}—{b:.3f} 秒（长 {seg_len:.3f} 秒）", "segment_reason": why,
        "tempo_median_bpm": float(np.median(bpm)) if bpm else None,
        "tempo_range_bpm": [float(min(bpm)), float(max(bpm))] if bpm else None,
        "n_onsets": len(onsets),
        "strength_norm": "相对重音强度 = 该起音处全频带谱通量 / 片段内全部起音谱通量 99 分位，截断到 0—1",
        "method": METHOD,
        "limits": "未实际试听；自动起音会把部分非节拍音量变化当作候选；未判定原曲是否含人声，需人工试听确认。",
    }
    return {
        "summary": summary, "method": METHOD,
        "segment": {"start": a, "end": b, "length": seg_len},
        "onsets": onsets,
        "beats": [round(x - a, 4) for x in beats if a <= x < b],
        "tempi": tempi,
        "novelty": [{"t": round(float(tt_ - a), 2), "v": round(float(v), 3)} for tt_, v in zip(bt, nov) if a <= tt_ < b],
    }
