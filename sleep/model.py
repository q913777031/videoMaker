"""睡眠双过程模型（Daan, Beersma & Borbély 1984）的数值模拟，供片中曲线逐帧取值。

参数取自 Skeldon, Dijk & Derks 2014（arXiv:1311.1734）图 1 图注（注明沿用 Daan 1984）：
上升时间常数 18.2 h、下降 4.2 h、下阈值均值 0.17、昼夜幅度 0.10、上渐近线 1；
C(t) 用 Borbély & Achermann 1999 的五次谐波。上阈值均值与相位按“23 点入睡、7 点醒来”的自由作息标定（见 calibrate）。
全部为确定性纯计算；时间单位为小时，t=0 为第 1 天 0 点。
"""

import functools
import math

import numpy as np

TAU_W = 18.2
TAU_S = 4.2
MU = 1.0
H0_LOW = 0.17
AMP = 0.10
HARMONICS = (0.97, 0.22, 0.007, 0.03, 0.001)
DT = 1 / 60

# calibrate() 的结果（23:00 入睡、7:00 醒来）
H0_HIGH = 0.645
ALPHA = 9.25


def circadian(t, alpha: float = ALPHA):
    """生物钟过程 C(t)，约在 [-1.2, 1.2]；值越大清醒信号越强（阈值越高）。"""
    x = 2 * math.pi / 24 * (np.asarray(t) - alpha)
    return sum(a * np.sin((k + 1) * x) for k, a in enumerate(HARMONICS))


def upper(t, h0: float = H0_HIGH, alpha: float = ALPHA):
    """入睡阈值：睡眠压力 S 碰到它就会睡着。"""
    return h0 + AMP * circadian(t, alpha)


def lower(t, alpha: float = ALPHA):
    """醒来阈值：睡眠中 S 降到它就会醒。"""
    return H0_LOW + AMP * circadian(t, alpha)


def forced(sleeps: list[tuple[float, float]], hours: float, s0: float = 0.25) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """按给定作息（[(入睡, 醒来), ...]，单位小时）积分 S，返回 (t, S, 是否在睡)；不受阈值约束，用于“被迫熬夜”等场景。"""
    t = np.arange(0, hours + DT / 2, DT)
    asleep = np.zeros(len(t), bool)
    for a, b in sleeps:
        asleep |= (t >= a) & (t < b)
    s = np.empty(len(t))
    s[0] = s0
    kw, ks = math.exp(-DT / TAU_W), math.exp(-DT / TAU_S)
    for i in range(1, len(t)):
        s[i] = s[i - 1] * ks if asleep[i - 1] else MU - (MU - s[i - 1]) * kw
    return t, s, asleep


def free(hours: float, h0: float = H0_HIGH, alpha: float = ALPHA, s0: float = 0.25):
    """无外界约束的自由作息：S 碰上阈值入睡，降到下阈值醒来。返回 (t, S, 是否在睡, [(入睡, 醒来), ...])。"""
    t = np.arange(0, hours + DT / 2, DT)
    hi, lo = upper(t, h0, alpha), lower(t, alpha)
    s = np.empty(len(t))
    asleep = np.zeros(len(t), bool)
    s[0], state, start, spans = s0, False, 0.0, []
    kw, ks = math.exp(-DT / TAU_W), math.exp(-DT / TAU_S)
    for i in range(1, len(t)):
        s[i] = s[i - 1] * ks if state else MU - (MU - s[i - 1]) * kw
        if not state and s[i] >= hi[i]:
            state, start = True, t[i]
        elif state and s[i] <= lo[i]:
            state = False
            spans.append((start, t[i]))
        asleep[i] = state
    return t, s, asleep, spans


def calibrate(onset: float = 23.0, wake: float = 7.0) -> tuple[float, float]:
    """网格搜索上阈值均值与相位（对全部参数组合并行积分），使自由作息第 8–10 天稳定在 onset 入睡、wake 醒来；返回 (h0, alpha)。"""
    h, a = (g.ravel() for g in np.meshgrid(np.arange(0.50, 0.80, 0.005), np.arange(0, 24, 0.25), indexing="ij"))
    s, state = np.full(h.shape, 0.25), np.zeros(h.shape, bool)
    err, cnt = np.zeros(h.shape), np.zeros(h.shape)
    kw, ks = math.exp(-DT / TAU_W), math.exp(-DT / TAU_S)
    for i in range(1, int(round(240 / DT)) + 1):
        t = i * DT
        s = np.where(state, s * ks, MU - (MU - s) * kw)
        c = AMP * circadian(t, a)
        go, up = ~state & (s >= h + c), state & (s <= H0_LOW + c)
        if t > 168:
            err[go] += ((t % 24 - onset + 12) % 24 - 12) ** 2
            err[up] += ((t % 24 - wake + 12) % 24 - 12) ** 2
            cnt += go | up
        state = np.where(go, True, np.where(up, False, state))
    k = int(np.argmin(np.where(cnt >= 4, err, np.inf)))
    return round(float(h[k]), 3), round(float(a[k]), 2)


def sleepiness(t, s, h0: float = H0_HIGH, alpha: float = ALPHA):
    """困意：S 在“醒来阈值—入睡阈值”之间的相对位置，0 为刚醒、1 为到了该睡的点，超过 1 表示硬撑。"""
    lo, hi = lower(t, alpha), upper(t, h0, alpha)
    return (s - lo) / (hi - lo)


@functools.lru_cache(maxsize=None)
def scenario(name: str):
    """片中用到的作息场景：先用正常作息（23 点睡、7 点起）跑 6 天进入稳态，再接场景本身；返回从场景首日 0 点起算的 (t, S, 是否在睡)。

    normal：每天照常；allnighter：首日通宵，次日 9–16 点补睡；weekend：首日熬到 3 点、睡到 12 点。
    """
    warm = [(d * 24 - 1, d * 24 + 7) for d in range(1, 7)]
    base = 6 * 24
    plans = {
        "normal": [(base + d * 24 - 1, base + d * 24 + 7) for d in range(1, 4)],
        "allnighter": [(base + 24 + 9, base + 24 + 16), (base + 48 - 1, base + 48 + 7)],
        "weekend": [(base + 27, base + 36), (base + 48 - 1, base + 48 + 7)],
    }
    t, s, asleep = forced(warm + plans[name], base + 72)
    k = int(round(base / DT))
    return t[k:] - base, s[k:], asleep[k:]


if __name__ == "__main__":
    print("calibrated (h0, alpha):", calibrate())
