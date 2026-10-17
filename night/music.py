"""原曲 bgm.m4a 的读取、信号分析、片段选择、卡点校准与混音母带。

分析只基于信号（谱通量起音、短时能量、局部自相关速度候选），不能替代人工试听；
所有结论在卡点表中标注检测方式与置信度。原曲缺失时不生成任何替代配乐。
"""

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pyloudnorm as pyln
from scipy import signal
from scipy.ndimage import maximum_filter1d, median_filter, minimum_filter1d

from .config import BASE_TOTAL, SR

HOP = 480                       # 10 ms
TARGET_LUFS = -16.0
TP_LIMIT = -1.0


@dataclass
class Analysis:
    path: str
    duration: float
    sample_rate: int
    channels: int
    codec: str
    seg_start: float = 0.0
    seg_end: float = 0.0
    total: float = BASE_TOTAL
    notes: list[str] = field(default_factory=list)
    env_t: np.ndarray | None = None      # 片段内起音包络时间轴（视频时间）
    env: np.ndarray | None = None        # 归一化起音强度 0–1
    peaks: list[tuple[float, float]] = field(default_factory=list)   # (视频时间, 强度)
    low_ratio: np.ndarray | None = None  # 每个包络帧的 40–150 Hz 能量占比
    tempo: list[tuple[float, float]] = field(default_factory=list)   # (窗口中心视频时间, BPM 候选)
    audio: np.ndarray | None = None      # 片段音频（48 kHz 立体声浮点）


def probe(path: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {out.stderr.strip()}")
    return json.loads(out.stdout)


def decode(path: Path) -> np.ndarray:
    """用 FFmpeg 解码为 48 kHz 立体声 float32（单声道复制为双声道）。"""
    out = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                         capture_output=True)
    if out.returncode != 0:
        raise RuntimeError(f"ffmpeg decode failed: {out.stderr.decode(errors='replace').strip()}")
    return np.frombuffer(out.stdout, np.float32).reshape(-1, 2).astype(np.float64)


def onset_envelope(x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """对数幅度谱通量（正向差分求和）减去局部中值，返回 (时间, 原始强度, 低频占比)。"""
    mono = x.mean(axis=1)
    f, t, z = signal.stft(mono, fs=SR, nperseg=2048, noverlap=2048 - HOP, boundary=None, padded=False)
    mag = np.log1p(100 * np.abs(z))
    flux = np.maximum(0, np.diff(mag, axis=1)).sum(axis=0)
    flux = np.concatenate([[0], flux])
    flux = np.maximum(0, flux - median_filter(flux, 41))
    power = np.abs(z) ** 2
    low = power[(f >= 40) & (f <= 150)].sum(axis=0)
    ratio = low / (power.sum(axis=0) + 1e-12)
    return t, flux, ratio


def pick_peaks(t: np.ndarray, env: np.ndarray, min_gap: float = 0.1, thr: float = 0.12) -> list[tuple[float, float]]:
    """局部极大且高于自适应门限的起音峰。"""
    w = max(1, int(min_gap * SR / HOP))
    loc = env == maximum_filter1d(env, 2 * w + 1)
    adapt = median_filter(env, 151) + thr
    idx = np.where(loc & (env > adapt))[0]
    return [(float(t[i]), float(env[i])) for i in idx]


def local_tempo(t: np.ndarray, env: np.ndarray, win: float = 8.0) -> list[tuple[float, float]]:
    """每 8 秒窗口内包络自相关的最强周期（60–180 BPM），只作候选，不假设全曲恒速。"""
    out = []
    step = int(win * SR / HOP)
    for a in range(0, len(env) - step, step // 2):
        seg = env[a:a + step] - env[a:a + step].mean()
        ac = np.correlate(seg, seg, "full")[len(seg) - 1:]
        lo, hi = int(60 / 180 * SR / HOP), int(60 / 60 * SR / HOP)
        if hi >= len(ac) or ac[0] <= 0:
            continue
        lag = lo + int(np.argmax(ac[lo:hi]))
        conf = ac[lag] / ac[0]
        if conf > 0.2:
            out.append((float(t[a + step // 2]), round(60 * SR / HOP / lag, 1)))
    return out


def choose_segment(x: np.ndarray, notes: list[str]) -> tuple[float, float]:
    """选取约 90 秒的连续片段：起点贴近明显起音、终点处能量处于回落，返回原曲 (起, 止) 秒。"""
    dur = len(x) / SR
    if dur < 87.0:
        raise ValueError(f"bgm too short: {dur:.2f}s < 87s")
    if dur <= 93.0:
        notes.append(f"原曲时长 {dur:.2f}s 位于 87–93s，整曲使用。")
        return 0.0, dur
    t, flux, _ = onset_envelope(x)
    flux = flux / (np.percentile(flux, 99) + 1e-12)
    rms_t = np.arange(0, dur, 0.1)
    mono = x.mean(axis=1)
    rms = np.array([np.sqrt(np.mean(mono[int(a * SR):int((a + 0.4) * SR)] ** 2) + 1e-12) for a in rms_t])
    db = 20 * np.log10(rms)
    best, best_s = -1e9, 0.0
    for s in np.arange(0, dur - 90.0 + 1e-6, 0.1):
        e = s + 90.0
        k0 = np.searchsorted(t, s)
        on = flux[max(0, k0 - 3):k0 + 4].max(initial=0)               # 起点有起音
        pre = db[max(0, int((s - 1) * 10)):int(s * 10) + 1].mean() if s > 0 else -60
        start_db = db[int(s * 10):int((s + 1) * 10)].mean()
        jump = start_db - pre                                           # 起点前更安静（乐句起点）
        ke = int(e * 10)
        fall = db[max(0, ke - 30):ke - 10].mean() - db[ke - 10:min(len(db), ke + 10)].mean()   # 末尾回落
        score = 1.0 * on + 0.08 * jump + 0.12 * fall
        if score > best:
            best, best_s = score, float(s)
    notes.append(f"原曲 {dur:.2f}s，选取 {best_s:.2f}–{best_s + 90:.2f}s（起点起音强度与末尾能量回落的综合打分，"
                 f"属信号启发式，需人工试听复核乐句完整性）。")
    return best_s, best_s + 90.0


def analyze(path: Path) -> Analysis:
    info = probe(path)
    st = next(s for s in info["streams"] if s["codec_type"] == "audio")
    x = decode(path)
    a = Analysis(path=str(path), duration=len(x) / SR, sample_rate=int(st["sample_rate"]),
                 channels=int(st["channels"]), codec=st["codec_name"])
    a.seg_start, a.seg_end = choose_segment(x, a.notes)
    seg = x[int(a.seg_start * SR):int(a.seg_end * SR)]
    a.total = round(len(seg) / SR * 30) / 30
    a.audio = seg
    t, flux, ratio = onset_envelope(seg)
    norm = np.percentile(flux, 99) + 1e-12
    a.env_t, a.env, a.low_ratio = t, np.clip(flux / norm, 0, 1), ratio
    a.peaks = pick_peaks(t, a.env)
    a.tempo = local_tempo(t, a.env)
    a.notes.append("相对重音强度 = 片段内谱通量（减局部中值）÷ 片段第 99 百分位，截断到 0–1。")
    a.notes.append("未进行人工试听；拍点、乐句与情绪判断仅来自信号分析，置信度按强度分级。")
    return a


def snap(a: Analysis, t: float, lo: float, hi: float, min_strength: float = 0.45) -> tuple[float, float, str]:
    """在 [lo, hi] 内寻找最接近 t 的强起音；找不到时保持 t 并标注柔和动作。返回 (时刻, 强度, 置信度)。"""
    cands = [(pt, s) for pt, s in a.peaks if lo <= pt <= hi and s >= min_strength]
    if not cands:
        return t, 0.0, "无合适重音"
    pt, s = max(cands, key=lambda p: p[1] - 0.6 * abs(p[0] - t))
    conf = "高" if s >= 0.75 else "中"
    return pt, s, conf


def low_energy_at(a: Analysis, t: float) -> float:
    k = int(np.clip(np.searchsorted(a.env_t, t), 0, len(a.low_ratio) - 1))
    return float(a.low_ratio[max(0, k - 2):k + 3].mean())


# ---------------------------------------------------------------- 混音

def fade_tail(x: np.ndarray, seconds: float = 3.0) -> np.ndarray:
    """末尾平滑淡出（余弦），保留自然尾韵、避免突然截断。"""
    x = x.copy()
    n = min(len(x), int(seconds * SR))
    x[-n:] *= (0.5 + 0.5 * np.cos(np.linspace(0, np.pi, n)))[:, None]
    m = int(0.01 * SR)
    x[:m] *= np.linspace(0, 1, m)[:, None]
    return x


def duck(music: np.ndarray, sfx: np.ndarray, depth_db: float = 2.0) -> np.ndarray:
    """按音效包络对音乐做小幅平滑避让（最多 depth_db，起 30 ms、释 300 ms），避免抽吸感。"""
    env = np.abs(sfx).max(axis=1)
    env = maximum_filter1d(env, int(0.03 * SR))
    lvl = np.clip(env / 0.3, 0, 1)
    b, a_ = signal.butter(1, 1 / 0.3 / (SR / 2))
    lvl = signal.filtfilt(b, a_, lvl)
    g = 10 ** (-depth_db * np.clip(lvl, 0, 1) / 20)
    return music * g[:, None]


def true_peak_db(x: np.ndarray) -> float:
    up = signal.resample_poly(x, 4, 1, axis=0)
    return 20 * np.log10(np.max(np.abs(up)) + 1e-12)


def limit_gain(x: np.ndarray, ceiling_db: float = TP_LIMIT - 0.2) -> np.ndarray:
    """前瞻式平滑增益限制（非削波）：按 4× 过采样峰值计算所需衰减，最小值滤波后平滑，返回逐样本增益。"""
    ceil = 10 ** (ceiling_db / 20)
    up = np.abs(signal.resample_poly(x, 4, 1, axis=0)).max(axis=1)
    pk = up.reshape(-1, 4).max(axis=1)[: len(x)]
    if len(pk) < len(x):
        pk = np.pad(pk, (0, len(x) - len(pk)))
    need = np.minimum(1.0, ceil / (pk + 1e-12))
    need = minimum_filter1d(need, int(0.005 * SR) * 2 + 1)
    b, a_ = signal.butter(1, 1 / 0.05 / (SR / 2))
    g = np.minimum(need, signal.filtfilt(b, a_, need))
    return minimum_filter1d(g, int(0.002 * SR) * 2 + 1)[:, None]


def master(music: np.ndarray, sfx: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
    """音乐 + 音效 → 混合轨，响度向 -16 LUFS-I 靠拢，真峰值不高于 -1 dBTP。返回同长度三轨与实测值。"""
    n = min(len(music), len(sfx))
    music, sfx = music[:n], sfx[:n]
    meter = pyln.Meter(SR)
    music = duck(music, sfx)
    mix = music + sfx
    for _ in range(4):
        g = 10 ** ((TARGET_LUFS - meter.integrated_loudness(mix)) / 20)
        music, sfx, mix = music * g, sfx * g, mix * g
        if true_peak_db(mix) <= TP_LIMIT:
            break
        g = limit_gain(mix)
        music, sfx, mix = music * g, sfx * g, mix * g
    if true_peak_db(mix) > TP_LIMIT:
        g = 10 ** ((TP_LIMIT - 0.1 - true_peak_db(mix)) / 20)
        music, sfx, mix = music * g, sfx * g, mix * g
    stats = {"integrated_lufs": round(meter.integrated_loudness(mix), 2),
             "true_peak_dbtp": round(true_peak_db(mix), 2),
             "music_lufs": round(meter.integrated_loudness(music), 2)}
    return music, sfx, mix, stats
