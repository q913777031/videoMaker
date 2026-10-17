"""打击乐音效合成：低音鼓、军鼓边击、木块、沙锤、框鼓、低音通鼓、邦戈鼓、拍手、轻柔吊镲。

设计取向：
- 每种音色都带 1–5 kHz 的起音成分，手机扬声器（低频截止约 200 Hz）上也能分辨；
- 起音峰值在开头 5 ms 内，便于与画面撞击帧对齐；
- 尾音短、高频经低通柔化，不刺耳、不拖进下一镜头；
- 全部为确定性合成（固定随机种子），同一参数每次输出相同波形。
"""

import functools

import numpy as np

from .audio import SR, _fade, _noise, bandpass, highpass, lowpass


def _t(dur: float) -> np.ndarray:
    return np.arange(int(dur * SR)) / SR


def _env(t: np.ndarray, attack: float, decay: float) -> np.ndarray:
    return np.minimum(1, t / max(attack, 1e-4)) * np.exp(-t / decay)


def _modes(t: np.ndarray, freqs, amps, decays, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    y = np.zeros(len(t))
    for f, a, d in zip(freqs, amps, decays):
        y += a * np.sin(2 * np.pi * f * t + rng.random() * 0.3) * np.exp(-t / d)
    return y


def _peak(y: np.ndarray, level: float) -> np.ndarray:
    return y / (np.max(np.abs(y)) + 1e-9) * level


def kick(light: bool = False) -> np.ndarray:
    """低音鼓：120→48 Hz 下滑正弦 + 3 kHz 击槌声。light 时高通 90 Hz、缩短尾音，用于音乐自身已有重底鼓的拍点。"""
    t = _t(0.45)
    f = 48 + 75 * np.exp(-t * 28)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (0.12 if light else 0.2))
    click = bandpass(_noise(len(t), 101), 1800, 5000) * np.exp(-t / 0.006) * 0.5
    knock = np.sin(2 * np.pi * 230 * t) * np.exp(-t / 0.035) * 0.7
    beater = bandpass(_noise(len(t), 112), 350, 1400) * np.exp(-t / 0.02) * 2.6
    y = np.tanh(1.4 * (body + knock)) + click + beater
    if light:
        y = highpass(y, 90, 2)
    return _peak(_fade(y, 0.0, 0.05), 0.9 if not light else 0.75)


def rim() -> np.ndarray:
    """军鼓边击（cross-stick）：1.7 kHz 木质共鸣 + 480 Hz 鼓体 + 极短噪声咔嗒。"""
    t = _t(0.16)
    tone = _modes(t, (1720, 480, 3150), (1.0, 0.55, 0.35), (0.018, 0.035, 0.009), 7)
    click = bandpass(_noise(len(t), 102), 2500, 7000) * np.exp(-t / 0.004) * 0.9
    return _peak(_fade(tone + click, 0.0, 0.03), 0.8)


def woodblock(pitch: str = "high") -> np.ndarray:
    """木块：两个非谐振模态的快速衰减；high 约 1.2 kHz（信息节点），low 约 760 Hz（十二宫节点）。"""
    base = 1220 if pitch == "high" else 760
    t = _t(0.12)
    y = _modes(t, (base, base * 2.68, base * 4.1), (1.0, 0.4, 0.12), (0.03, 0.012, 0.006), 9)
    y += bandpass(_noise(len(t), 103), 2000, 6000) * np.exp(-t / 0.002) * 0.3
    return _peak(_fade(y, 0.0, 0.02), 0.7)


def shaker() -> np.ndarray:
    """沙锤：两次 4–9 kHz 颗粒噪声（前短后长），软起音，经 9 kHz 低通去刺。"""
    t = _t(0.2)
    n = bandpass(_noise(len(t), 104), 3800, 9000, 2)
    e = 0.55 * np.minimum(1, t / 0.008) * np.exp(-t / 0.03)
    t2 = np.clip(t - 0.07, 0, None)
    e += np.where(t >= 0.07, np.minimum(1, t2 / 0.012) * np.exp(-t2 / 0.045), 0)
    y = lowpass(n * e, 9000)
    return _peak(_fade(y, 0.0, 0.03), 0.42)


def frame_drum() -> np.ndarray:
    """框鼓：85 Hz 起的膜振动模态（轻微下滑）+ 900 Hz 掌击噪声，尾音约 0.5 秒，低沉而不轰。"""
    t = _t(0.7)
    f0 = 85 * (1 + 0.08 * np.exp(-t * 20))
    ph = 2 * np.pi * np.cumsum(f0) / SR
    y = np.sin(ph) * np.exp(-t / 0.22) + 0.45 * np.sin(1.59 * ph) * np.exp(-t / 0.12)
    y += 0.3 * np.sin(2.14 * ph) * np.exp(-t / 0.08)
    y += bandpass(_noise(len(t), 105), 500, 1800) * np.exp(-t / 0.035) * 3.6
    y += np.sin(3.1 * ph) * np.exp(-t / 0.05) * 0.35 + np.sin(4.6 * ph) * np.exp(-t / 0.035) * 0.25
    y += bandpass(_noise(len(t), 106), 2500, 5000) * np.exp(-t / 0.004) * 0.25
    return _peak(_fade(y, 0.0, 0.08), 0.8)


def low_tom() -> np.ndarray:
    """低音通鼓轻击：130→105 Hz 下滑 + 1.1 kHz 鼓皮起音，尾音约 0.35 秒。"""
    t = _t(0.5)
    f = 105 + 25 * np.exp(-t * 18)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.16)
    y += 0.3 * np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR) * np.exp(-t / 0.07)
    y += 0.8 * np.sin(2 * np.pi * np.cumsum(f * 2.3) / SR) * np.exp(-t / 0.06)
    y += bandpass(_noise(len(t), 107), 600, 3000) * np.exp(-t / 0.02) * 3.2
    return _peak(_fade(np.tanh(1.2 * y), 0.0, 0.06), 0.7)


def bongo(pitch: str = "high") -> np.ndarray:
    """邦戈鼓：high 约 420 Hz、low 约 290 Hz，带 1.5 倍泛音与指击噪声，尾音约 0.15 秒。"""
    f0 = 420 if pitch == "high" else 290
    t = _t(0.25)
    f = f0 * (1 + 0.12 * np.exp(-t * 60))
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) * np.exp(-t / 0.07) + 0.35 * np.sin(1.51 * ph) * np.exp(-t / 0.04)
    y += bandpass(_noise(len(t), 108 + (pitch == "low")), 1500, 5000) * np.exp(-t / 0.005) * 0.4
    return _peak(_fade(y, 0.0, 0.03), 0.6)


def clap() -> np.ndarray:
    """短促拍手：三次 10 ms 间隔的 1–3.5 kHz 噪声脉冲 + 60 ms 尾音。"""
    t = _t(0.18)
    n = bandpass(_noise(len(t), 109), 1000, 3500, 2)
    e = 0.5 * np.exp(-t / 0.05)
    for d, a in ((0.0, 1.0), (0.01, 0.8), (0.021, 0.65)):
        e += np.where(t >= d, a * np.exp(-np.clip(t - d, 0, None) / 0.004), 0)
    return _peak(_fade(n * e, 0.0, 0.03), 0.7)


def cymbal(dur: float = 2.6) -> np.ndarray:
    """轻柔吊镲：毡头槌轻击，非谐振金属模态 + 噪声，经 7.5 kHz 低通柔化，尾音 dur 秒内衰减到静音。"""
    t = _t(dur)
    rng = np.random.default_rng(110)
    freqs = 520 * np.array([1.0, 1.47, 1.98, 2.43, 2.91, 3.62, 4.27, 5.11, 6.03, 7.17])
    y = np.zeros(len(t))
    for k, f in enumerate(freqs):
        y += np.sin(2 * np.pi * f * (1 + 0.002 * rng.standard_normal()) * t + rng.random() * 6) / (1 + 0.25 * k)
    y = y * 0.25 + bandpass(_noise(len(t), 111), 3000, 7500) * 0.6
    env = np.minimum(1, t / 0.012) * np.exp(-t / (dur / 4.5))
    y = lowpass(y * env, 7500, 2)
    return _peak(_fade(y, 0.0, 0.3), 0.35)


@functools.lru_cache(maxsize=32)
def sound(name: str) -> np.ndarray:
    """按名称取音效（单声道）。名称见 TIMBRES。"""
    table = {
        "kick": lambda: kick(False), "kick_light": lambda: kick(True), "rim": rim,
        "wood_high": lambda: woodblock("high"), "wood_low": lambda: woodblock("low"), "shaker": shaker,
        "frame": frame_drum, "tom": low_tom, "bongo_high": lambda: bongo("high"),
        "bongo_low": lambda: bongo("low"), "clap": clap, "cymbal": cymbal,
    }
    return table[name]()


TIMBRES = {
    "kick": "低音鼓", "kick_light": "低音鼓（高通 90 Hz，避让音乐底鼓）", "rim": "军鼓边击",
    "wood_high": "木块（高）", "wood_low": "木块（低）", "shaker": "沙锤", "frame": "框鼓",
    "tom": "低音通鼓", "bongo_high": "邦戈鼓（高）", "bongo_low": "邦戈鼓（低）", "clap": "拍手",
    "cymbal": "轻柔吊镲",
}


def attack_ms(name: str) -> float:
    """音效起音峰值相对开头的毫秒数（用于核对与画面帧的对齐）。"""
    y = np.abs(sound(name))
    return float(np.argmax(y[: int(0.05 * SR)]) / SR * 1000)


def tail_s(name: str, thr_db: float = -50.0) -> float:
    """音效衰减到峰值以下 thr_db 的时长（秒）。"""
    y = np.abs(sound(name))
    above = np.nonzero(y > np.max(y) * 10 ** (thr_db / 20))[0]
    return float(above[-1] / SR) if len(above) else 0.0

