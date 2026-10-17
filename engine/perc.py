"""打击乐音效合成：低音鼓、军鼓边击、木块、沙锤、框鼓、低音通鼓、邦戈鼓、拍手、轻柔吊镲；
以及中国打击乐：堂鼓、大鼓、大锣、小锣、铙钹、梆子、木鱼、编钟。

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


# ---------------------------------------------------------------- 中国打击乐

def tanggu() -> np.ndarray:
    """堂鼓：牛皮鼓面、鼓槌击中心，约 175 Hz 起音后轻微下滑，带 1.59 / 2.14 倍膜振动泛音与 2–5 kHz 槌击声，尾音约 0.45 秒。"""
    t = _t(0.7)
    f0 = 168 * (1 + 0.12 * np.exp(-t * 35))
    ph = 2 * np.pi * np.cumsum(f0) / SR
    y = np.sin(ph) * np.exp(-t / 0.16) + 0.55 * np.sin(1.59 * ph) * np.exp(-t / 0.09)
    y += 0.35 * np.sin(2.14 * ph) * np.exp(-t / 0.06) + 0.2 * np.sin(2.65 * ph) * np.exp(-t / 0.045)
    y += bandpass(_noise(len(t), 121), 900, 3200) * np.exp(-t / 0.025) * 2.4
    y += bandpass(_noise(len(t), 122), 2000, 6000) * np.exp(-t / 0.004) * 0.9
    return _peak(_fade(np.tanh(1.3 * y), 0.0, 0.08), 0.85)


def dagu() -> np.ndarray:
    """大鼓：大面积鼓皮，约 78 Hz 基频、低频饱满，起音带 1.2 kHz 槌声保证手机上可辨，尾音约 0.8 秒。"""
    t = _t(1.1)
    f0 = 74 * (1 + 0.18 * np.exp(-t * 18))
    ph = 2 * np.pi * np.cumsum(f0) / SR
    y = np.sin(ph) * np.exp(-t / 0.32) + 0.5 * np.sin(1.5 * ph) * np.exp(-t / 0.15)
    y += 0.35 * np.sin(2.3 * ph) * np.exp(-t / 0.08)
    y += bandpass(_noise(len(t), 123), 500, 1800) * np.exp(-t / 0.03) * 3.0
    y += bandpass(_noise(len(t), 124), 1800, 4500) * np.exp(-t / 0.005) * 0.7
    return _peak(_fade(np.tanh(1.6 * y), 0.0, 0.12), 0.9)


def _metal(t, freqs, amps, decays, bend=0.0, bend_t=0.15, seed=0, shimmer=0.0):
    """锣钹类金属体：非谐振分音之和，可带整体音高滑动（bend 为相对变化量）与缓慢拍频（shimmer）。"""
    rng = np.random.default_rng(seed)
    k = 1 + bend * (1 - np.exp(-t / bend_t))
    y = np.zeros(len(t))
    for f, a, d in zip(freqs, amps, decays):
        ph = 2 * np.pi * np.cumsum(f * k) / SR + rng.random() * 6.28
        am = 1 + shimmer * np.sin(2 * np.pi * (0.7 + 2.3 * rng.random()) * t + rng.random() * 6.28)
        y += a * np.sin(ph) * np.exp(-t / d) * am
    return y


def daluo() -> np.ndarray:
    """大锣：约 210 Hz 的深沉锣声，起音后音高略降，泛音缓慢拍动，尾音约 2.5 秒；起音带槌击噪声。"""
    t = _t(3.0)
    base = 210
    ratios = (1.0, 1.52, 2.03, 2.48, 2.97, 3.61, 4.4, 5.3)
    y = _metal(t, [base * r for r in ratios], (1, .7, .55, .45, .35, .25, .18, .12),
               (1.1, .8, .65, .5, .4, .3, .22, .16), bend=-0.035, bend_t=0.4, seed=131, shimmer=0.25)
    y += bandpass(_noise(len(t), 132), 400, 2500) * np.exp(-t / 0.02) * 1.6
    y = lowpass(y, 6500)
    return _peak(_fade(y, 0.0, 0.4), 0.8)


def xiaoluo() -> np.ndarray:
    """小锣（京剧“台”）：约 760 Hz 起音后音高上扬约 9%，明亮短促，尾音约 0.9 秒。"""
    t = _t(1.2)
    base = 760
    y = _metal(t, [base, base * 1.48, base * 2.1, base * 2.9], (1, .45, .25, .12), (.35, .2, .12, .07),
               bend=0.09, bend_t=0.12, seed=133)
    y += bandpass(_noise(len(t), 134), 2000, 7000) * np.exp(-t / 0.006) * 0.6
    return _peak(_fade(y, 0.0, 0.15), 0.7)


def naobo() -> np.ndarray:
    """铙钹：两片对击的“嚓”声，3–9 kHz 噪声爆发 + 金属分音，经 9 kHz 低通去刺，尾音约 1.2 秒。"""
    t = _t(1.5)
    n = bandpass(_noise(len(t), 135), 2800, 9000, 2)
    env = np.minimum(1, t / 0.002) * (0.65 * np.exp(-t / 0.05) + 0.35 * np.exp(-t / 0.45))
    y = n * env + bandpass(_noise(len(t), 143), 1500, 6000) * np.exp(-t / 0.003) * 2.5
    y += 0.35 * _metal(t, [430 * r for r in (1, 1.71, 2.53, 3.37, 4.6, 5.9)], (1, .8, .7, .5, .4, .3),
                       (.5, .4, .32, .25, .2, .15), seed=136)
    y = lowpass(y, 9000)
    return _peak(_fade(y, 0.0, 0.3), 0.6)


def bangzi() -> np.ndarray:
    """梆子：硬木对击，约 2.1 kHz 主共振、极短（约 70 ms），起音清脆。"""
    t = _t(0.1)
    y = _modes(t, (2100, 3400, 5200), (1.0, 0.35, 0.15), (0.022, 0.009, 0.005), 137)
    y += bandpass(_noise(len(t), 138), 3000, 8000) * np.exp(-t / 0.0018) * 0.5
    return _peak(_fade(y, 0.0, 0.015), 0.7)


def muyu() -> np.ndarray:
    """木鱼：空腔木器“笃”声，约 620 Hz 空腔共振 + 1.9 kHz 木质泛音，尾音约 0.12 秒。"""
    t = _t(0.18)
    y = _modes(t, (620, 1880, 2950), (1.0, 0.5, 0.18), (0.045, 0.014, 0.007), 139)
    y += bandpass(_noise(len(t), 140), 1500, 5000) * np.exp(-t / 0.002) * 0.35
    return _peak(_fade(y, 0.0, 0.03), 0.7)


def bianzhong() -> np.ndarray:
    """编钟：青铜钟“一钟双音”，正鼓音约 523 Hz、侧鼓音约 659 Hz，加钟体高次分音，尾音约 2 秒。"""
    t = _t(2.4)
    y = _metal(t, (523, 659, 1210, 1580, 2470, 3300), (1, .6, .35, .25, .12, .06), (1.0, .8, .4, .3, .16, .1),
               seed=141, shimmer=0.08)
    y += bandpass(_noise(len(t), 142), 1500, 5000) * np.exp(-t / 0.004) * 0.4
    return _peak(_fade(y, 0.0, 0.35), 0.65)


@functools.lru_cache(maxsize=32)
def sound(name: str) -> np.ndarray:
    """按名称取音效（单声道）。名称见 TIMBRES。"""
    table = {
        "kick": lambda: kick(False), "kick_light": lambda: kick(True), "rim": rim,
        "wood_high": lambda: woodblock("high"), "wood_low": lambda: woodblock("low"), "shaker": shaker,
        "frame": frame_drum, "tom": low_tom, "bongo_high": lambda: bongo("high"),
        "bongo_low": lambda: bongo("low"), "clap": clap, "cymbal": cymbal,
        "tanggu": tanggu, "dagu": dagu, "daluo": daluo, "xiaoluo": xiaoluo, "naobo": naobo,
        "bangzi": bangzi, "muyu": muyu, "bianzhong": bianzhong,
    }
    return table[name]()


TIMBRES = {
    "kick": "低音鼓", "kick_light": "低音鼓（高通 90 Hz，避让音乐底鼓）", "rim": "军鼓边击",
    "wood_high": "木块（高）", "wood_low": "木块（低）", "shaker": "沙锤", "frame": "框鼓",
    "tom": "低音通鼓", "bongo_high": "邦戈鼓（高）", "bongo_low": "邦戈鼓（低）", "clap": "拍手",
    "cymbal": "轻柔吊镲",
    "tanggu": "堂鼓", "dagu": "大鼓", "daluo": "大锣", "xiaoluo": "小锣", "naobo": "铙钹", "bangzi": "梆子",
    "muyu": "木鱼", "bianzhong": "编钟",
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

