"""背景音乐：加载项目内置 BGM、节拍网格分析（BPM / 强拍 / drop）、与视频时间轴对齐的卡点工具。

分析全部为确定性计算，同一音频每次得到相同的网格。
"""

import functools
import math
import subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy import signal

from .audio import SR, ROOT

DEFAULT_BGM = ROOT / "music" / "bgm.m4a"
LUFS = -19.0
HOP = 512


@functools.lru_cache(maxsize=4)
def load(path: str | Path = DEFAULT_BGM) -> np.ndarray:
    """用 FFmpeg 解码为 SR 采样率的立体声 float 数组，并把响度标准化到 LUFS；失败时抛出 RuntimeError。"""
    import pyloudnorm

    cmd = ["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"]
    proc = subprocess.run(cmd, capture_output=True)
    if proc.returncode != 0 or not proc.stdout:
        raise RuntimeError(f"cannot decode bgm {path}: {proc.stderr.decode(errors='ignore').strip()}")
    x = np.frombuffer(proc.stdout, np.float32).reshape(-1, 2).astype(np.float64)
    loud = pyloudnorm.Meter(SR).integrated_loudness(x)
    return x * 10 ** ((LUFS - loud) / 20)


@dataclass(frozen=True)
class Grid:
    """音乐节拍网格（音乐自身时间）：首个强拍 t0、拍长 period、每小节拍数、drop（能量跃升最大的小节线）。"""
    t0: float
    period: float
    beats_per_bar: int
    drop: float
    length: float

    @property
    def bpm(self) -> float:
        return 60 / self.period

    @property
    def bar(self) -> float:
        return self.period * self.beats_per_bar


def _onset_envelope(mono: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """返回 (全频谱通量, 低频 <150Hz 通量)，帧率 SR / HOP。"""
    _, _, z = signal.stft(mono, SR, nperseg=2048, noverlap=2048 - HOP, boundary=None)
    mag = np.log1p(100 * np.abs(z))
    flux = np.maximum(0, np.diff(mag, axis=1, prepend=mag[:, :1]))
    freqs = np.fft.rfftfreq(2048, 1 / SR)
    return flux.sum(axis=0), flux[freqs < 150].sum(axis=0)


@functools.lru_cache(maxsize=4)
def analyze(path: str | Path = DEFAULT_BGM, beats_per_bar: int = 4) -> Grid:
    """估计恒定速度的节拍网格：自相关求速度 → 梳状打分精修拍长与相位 → 低频能量定强拍 → 小节能量跃升定 drop。"""
    x = load(path)
    mono = x.mean(axis=1)
    env, low = _onset_envelope(mono)
    env = env - signal.medfilt(env, 31)
    env = np.maximum(env, 0)
    fps = SR / HOP

    ac = np.correlate(env, env, "full")[len(env) - 1:]
    lags = np.arange(len(ac)) / fps
    ok = (lags > 60 / 180) & (lags < 60 / 70)
    prior = np.exp(-0.5 * (np.log2(lags[ok] * 2) / 0.9) ** 2)   # 偏向 120 BPM 附近，避免倍速/半速
    coarse = lags[ok][np.argmax(ac[ok] * prior)]

    def comb(period: float, phase: float) -> float:
        idx = np.round((phase + np.arange(0, len(env) / fps - phase, period)) * fps).astype(int)
        return env[idx[idx < len(env)]].sum()

    best = (-1.0, coarse, 0.0)
    for period in np.linspace(coarse * 0.98, coarse * 1.02, 81):
        for phase in np.arange(0, period, 1 / fps):
            score = comb(period, phase)
            if score > best[0]:
                best = (score, period, phase)
    _, period, phase = best

    n_beats = int((len(env) / fps - phase) / period)
    beat_idx = np.round((phase + np.arange(n_beats) * period) * fps).astype(int)
    win = int(0.05 * fps)
    strength = np.array([low[max(0, i - win): i + win + 1].max() for i in beat_idx])
    down = max(range(beats_per_bar), key=lambda k: strength[k::beats_per_bar].mean())
    t0 = phase + down * period + 1024 / SR   # STFT 帧以窗口起点计时，加半窗换算到窗口中心

    bar = period * beats_per_bar
    frame_db = 10 * np.log10(np.convolve(mono ** 2, np.ones(HOP) / HOP, "valid")[::HOP] + 1e-12)
    bars = int((len(mono) / SR - t0) / bar)
    level = np.array([frame_db[int((t0 + b * bar) * fps): int((t0 + (b + 1) * bar) * fps)].mean()
                      for b in range(bars)])
    jump = [level[b: b + 2].mean() - level[max(0, b - 2): b].mean() for b in range(2, bars - 1)]
    drop = t0 + (2 + int(np.argmax(jump))) * bar
    return Grid(t0, period, beats_per_bar, drop, len(mono) / SR)


class Sync:
    """视频时间轴上的节拍网格：视频第 0 秒对应音乐的 offset 秒；offset 取强拍，故视频强拍落在小节长度的整数倍上。"""

    def __init__(self, path: str | Path = DEFAULT_BGM, offset_bars: int = 0):
        self.path = path
        self.g = analyze(path)
        self.offset = self.g.t0 + offset_bars * self.g.bar

    def snap(self, t: float, unit: float, lo: float = 0.0, hi: float = math.inf) -> float:
        """把 t 吸附到间隔 unit 的网格点，只在 [t-lo, t+hi] 窗口内取最近点；窗口内无网格点时原样返回。"""
        cands = [k * unit for k in range(math.ceil((t - lo) / unit - 1e-9), math.floor((t + hi) / unit + 1e-9) + 1)]
        return min(cands, key=lambda c: (abs(c - t), c)) if cands else t

    def next_on(self, t: float, unit: float) -> float:
        """t 之后（含）第一个间隔 unit 的网格点。"""
        return math.ceil(t / unit - 1e-9) * unit

    def downbeats(self, total: float) -> list[float]:
        return [k * self.g.bar for k in range(int(total / self.g.bar) + 1)]

    def track(self, total: float, fade_out: float = 1.5) -> np.ndarray:
        """返回与视频等长的立体声配乐：从 offset 播放；音乐不够长时在小节线处接回 drop 小节循环（交叉淡化半拍），结尾淡出。"""
        x = load(self.path)
        g = self.g
        n = int(total * SR)
        xf = int(g.period / 2 * SR)
        ramp = np.linspace(0, 1, xf)[:, None]
        whole = math.floor((g.length - self.offset) / g.bar) * g.bar
        out = x[int(self.offset * SR): int((self.offset + whole) * SR) + xf].copy()
        loop = x[int(g.drop * SR): int((g.drop + math.floor((g.length - g.drop) / g.bar) * g.bar) * SR) + xf]
        while len(out) - xf < n:
            seg = loop.copy()
            seg[:xf] = out[-xf:] * (1 - ramp) + seg[:xf] * ramp
            out = np.concatenate([out[:-xf], seg])
        out = out[:n]
        f = min(n, int(fade_out * SR))
        out[n - f:] *= np.linspace(1, 0, f)[:, None] ** 2
        return out


# ---------------------------------------------------------------- 逐拍检测（不假设恒定速度）

ANALYSIS_SR = 22050
ANALYSIS_HOP = 256


def _norm(v: np.ndarray) -> np.ndarray:
    lo, hi = np.percentile(v, 5), np.percentile(v, 99.7)
    return np.clip((v - lo) / (hi - lo + 1e-9), 0, 1)


@functools.lru_cache(maxsize=4)
def detect(path: str | Path = DEFAULT_BGM) -> dict:
    """用 librosa 动态规划节拍跟踪检测实际拍点（拍长可变），并给出每拍的重音特征、强起音与段落边界。

    返回 dict：
    - beats：[{t, strength, low, high, db, bar_pos}]，strength 为全频起音强度，low/high 为低频（底鼓）与中高频（军鼓/拍手）起音，均归一到 0–1；
      bar_pos 为小节内位置（0 为强拍，按低频起音最强的相位估计）
    - onsets：[{t, strength}] 全部检测到的起音（含反拍）
    - sections：段落边界时刻（按节拍同步的音色/和声特征做层次聚类）
    - energy：[(t, dB)] 每 0.5 秒的响度曲线
    """
    import librosa

    sr, hop = ANALYSIS_SR, ANALYSIS_HOP
    y = librosa.resample(load(path).mean(axis=1).astype(np.float32), orig_sr=SR, target_sr=sr)
    env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop, aggregate=np.median)
    _, beat_f = librosa.beat.beat_track(onset_envelope=env, sr=sr, hop_length=hop, tightness=60)
    times = librosa.frames_to_time(np.arange(len(env)), sr=sr, hop_length=hop)
    mel = librosa.feature.melspectrogram(y=y, sr=sr, hop_length=hop, n_mels=64, fmax=11000)
    mf = librosa.mel_frequencies(n_mels=64, fmax=11000)
    lm = librosa.power_to_db(mel)
    flux = np.maximum(0, np.diff(lm, axis=1, prepend=lm[:, :1]))
    low, high = flux[mf < 160].mean(axis=0), flux[mf > 1500].mean(axis=0)
    rms_db = 20 * np.log10(librosa.feature.rms(y=y, hop_length=hop)[0] + 1e-6)

    win = int(0.04 * sr / hop)

    def peak(v, f):
        return float(v[max(0, f - win): f + win + 1].max())

    s_env, s_low, s_high = _norm(env), _norm(low), _norm(high)
    feats = [(peak(s_env, f), peak(s_low, f), peak(s_high, f)) for f in beat_f]
    phase = max(range(4), key=lambda k: np.mean([x[1] for x in feats[k::4]]))
    beats = []
    for i, (f, (st, lo, hi)) in enumerate(zip(beat_f, feats)):
        seg = rms_db[f: beat_f[i + 1] if i + 1 < len(beat_f) else len(rms_db)]
        beats.append(dict(t=round(float(times[f]), 4), strength=round(st, 3), low=round(lo, 3), high=round(hi, 3),
                          db=round(float(seg.mean()) if len(seg) else float(rms_db[f]), 1), bar_pos=(i - phase) % 4))
    on_f = librosa.onset.onset_detect(onset_envelope=env, sr=sr, hop_length=hop)
    onsets = [dict(t=round(float(times[f]), 4), strength=round(float(s_env[f]), 3)) for f in on_f]

    chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=512)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, hop_length=512, n_mfcc=13)
    feat = np.vstack([librosa.util.normalize(chroma, axis=0), mfcc / (np.abs(mfcc).max() + 1e-9)])
    bf512 = librosa.time_to_frames(times[beat_f], sr=sr, hop_length=512)
    sync_f = librosa.util.sync(feat, bf512, aggregate=np.median)
    bounds = librosa.segment.agglomerative(sync_f, 10)
    bt = [float(times[beat_f[min(max(b - 1, 0), len(beat_f) - 1)]]) for b in bounds[1:]]
    energy = [(round(a, 1), round(float(rms_db[(times >= a) & (times < a + 0.5)].mean()), 1))
              for a in np.arange(0, times[-1], 0.5)]
    return dict(beats=beats, onsets=onsets, sections=[0.0] + [round(b, 4) for b in bt], energy=energy,
                duration=round(len(y) / sr, 3))
