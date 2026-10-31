"""《丰田模式》样片 v3：角色可辨 + 动效卡点（约 26 秒），不接频道片尾。

在 v2（慢速讲解、4 屏、拉绳 = 音乐 drop）基础上：
- 读音：结尾问句改成“停线这么狠，返工反倒少了？”（避开“少返工”被读成 shào）；
- 角色一眼可辨：第 1 屏“小李 · 打工人”（衬衫领带）；员工“小王”黄安全帽 + 蓝工装 + 胸前“员工”工牌；
  组长“老张”红帽 + 红袖章“组长” + 手拿夹板，个子更高、线条黑色；名字标签写在脚下；
- 旁白说到谁就让谁动：员工头顶冒“!”并指向那辆车 → 伸手抓绳、拉直、黄灯亮（drop）→ 组长从右侧跑进来（脚步卡拍）
  → 摇头、“修”被划掉 → 车辆刹停（停止线 + 回弹）、转红灯 → “停！”砸字；
- 每个画面事件都在实测拍点上并配打击乐，音效峰值与撞击帧同帧或相邻帧；返工圈按拍转，每转一圈一声；
- 慢切换照旧：每屏 ≥5.8 秒，画完讲完后停 ≥1.5 秒；第 2 屏只留线、车、员工、灯、绳（书缩小放左上角）；第 3 屏构图收回画面内。

书中观点为转述：Jeffrey K. Liker, The Toyota Way（2004）原则 5——发现问题就停下来解决，一次做对；
丰田生产线上工人发现异常可以拉安灯绳：先亮灯叫组长来处理，当场处理不好，整条线才停下。
人物、名字、“返工第三遍”均为示意。

用法：python3 -m fengtian.sample_v3 [--sheet] [--asr 模型目录]   → out/fengtian/sample_v3.mp4
"""

import math
import subprocess
import sys
import tempfile
from multiprocessing import get_context
from pathlib import Path

import numpy as np
import skia
import soundfile as sf
from scipy.ndimage import minimum_filter1d, uniform_filter1d

from adler import core, fx
from adler import kit as K
from engine import audio, bgm, gfx, perc, wording
from engine.gfx import clamp01, ease_in_out, ease_out, ease_out_back, lerp
from whiteboard import engine as wb
from whiteboard.engine import BLACK, BLUE, GREEN, RED, Board, P, arrow, book, check, circle, cross, desk, doc, join, rect

# ---------------------------------------------------------------- 旁白音色（换音色只改这里）
NARRATOR = {"voice": "zv_yunjian", "prompt_speed": 0.95}   # audio.Narrator(**NARRATOR)
GENERATE = {"speed": 1.0, "num_steps": 8}                   # narrator.generate(text, **GENERATE)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out" / "fengtian"
COMMA, PERIOD = 0.25, 0.5
ACC = "#C8102E"
YELLOW, HAT, SUIT, BOARD_C = "#E0A21B", "#F2B705", "#CFE0F5", "#C89B63"
SCREENS = [(10, 22), (22, 36), (36, 48), (48, 59)]   # 每屏 [起拍, 止拍)（实测拍序号，均为半小节线）
S = core.BEATS[SCREENS[0][0]]["t"] - 0.15
DROP = 32
SPIN0 = SCREENS[0][0] + 4                            # 返工圈开始转的拍；每 4 拍转一圈
MUSIC_DB, DUCK, SFX_DB = -12.5, 0.45, -9.0

core.SERIES.update(name="丰田模式", count="样片", prefix="丰田")

LINES = [
    ("同一个问题，返工第三遍了。", ["同一个问题", "【返工】第三遍了"]),
    ("补了又坏，坏了又补。", ["补了又坏，坏了又补"]),
    ("丰田偏偏反着来：", ["丰田偏偏【反着来】"]),
    ("工人看到毛病，就拉一下绳。", ["工人看到毛病", "就【拉】一下绳"]),
    ("组长马上赶来，当场修不好，整条线就停下。", ["组长马上赶来", "当场修不好", "整条线就【停下】"]),
    ("停线这么狠，返工反倒少了？", ["停线这么狠", "返工反倒【少了】？"]),
    ("往下看。", ["往下看"]),
]

# ---------------------------------------------------------------- 白板与布局

b = Board(size=(2400, 3400))
VA = (1100, 800, 0.85)            # 屏 1：小李的工位 + 返工圈
VB = (1100, 1750, 0.8)            # 屏 2：流水线（线、车、员工、灯、绳）
VB2 = (1240, 1880, 0.66)          # 屏 3：拉宽，书、整条线、员工、组长都在画面内
VC = (1200, 1250, 0.55)           # 屏 4：拉远，返工圈与流水线同框

LC, LR = (1350, 820), 230
WK = (1530, 2150, 0.9)            # 员工小王（脚底, 缩放）
LD = (1850, 2150, 1.0)            # 组长老张停下的位置
CORD_X, RAIL_Y, HANDLE_Y = 1610, 1470, 1840
LAMP = (1000, 1565, 50)
BELT = (470, 1380, 2000)
STOP_X = 1365                     # 停止线
CAR_X = [650, 950, 1250]          # 刹停时三辆车的位置
CAR_V = 40.0


def tb(j, k):
    return b.t_of(j, k)


def beat_pos(T):
    """全局小数拍位置（按实测拍点插值）。"""
    bt_ = core._BEAT_T
    i = int(np.clip(np.searchsorted(bt_, T, side="right") - 1, 0, len(bt_) - 2))
    return i + (T - bt_[i]) / (bt_[i + 1] - bt_[i])


def pop_scale(dt, dur=0.32):
    """弹出：0 → 1 带回弹；dt < 0 时为 0。"""
    if dt < 0:
        return 0.0
    return ease_out_back(clamp01(dt / dur))


def slam_scale(dt):
    """砸字：从 1.9 倍砸到 1，落地后小幅回弹。"""
    if dt < 0:
        return 0.0
    if dt < 0.1:
        return lerp(1.9, 1.0, ease_out(dt / 0.1))
    return 1.0 + 0.07 * math.exp(-(dt - 0.1) * 9) * math.sin((dt - 0.1) * 30)


def t_drop():
    return core.BEATS[DROP]["t"]


def t_stop():
    return tb(2, 7)


# ---------------------------------------------------------------- 角色

def _line(c, a, z, color, w, alpha=1.0):
    c.drawLine(a[0], a[1], z[0], z[1], wb.marker(color, w, alpha))


def _reveal(c, x, top, h, p):
    """描出效果：从上往下逐渐露出，返回笔尖。"""
    c.clipRect(skia.Rect.MakeLTRB(x - 400, top - 10, x + 400, top + h * p))
    return (x + 70, top + h * p) if p < 1 else None


def draw_worker(c, x, y, s, lh, rh, head_dx=0.0, alpha=1.0):
    """员工小王：黄安全帽、蓝工装、胸前工牌“员工”。lh / rh 为左右手位置。"""
    hy = y - 290 * s
    sh = (x, hy + 80 * s)
    hip = (x, y - 120 * s)
    torso = skia.Rect.MakeLTRB(x - 42 * s, hy + 55 * s, x + 42 * s, y - 105 * s)
    c.drawRoundRect(torso, 18 * s, 18 * s, K.paint(SUIT, alpha))
    c.drawRoundRect(torso, 18 * s, 18 * s, wb.marker(BLUE, 8, alpha))
    for foot in ((x - 55 * s, y), (x + 55 * s, y)):
        _line(c, hip, foot, BLUE, 10, alpha)
    _line(c, sh, lh, BLUE, 10, alpha)
    _line(c, sh, rh, BLUE, 10, alpha)
    hx = x + head_dx
    c.drawCircle(hx, hy, 45 * s, K.paint("#FFFFFF", alpha))
    c.drawCircle(hx, hy, 45 * s, wb.marker(BLACK, 9, alpha))
    for dx in (-15, 15):
        c.drawCircle(hx + dx * s, hy - 4 * s, 4 * s, K.paint(BLACK, alpha))
    _line(c, (hx - 14 * s, hy + 20 * s), (hx + 14 * s, hy + 20 * s), BLACK, 6, alpha)
    dome = skia.Path()
    dome.addArc(skia.Rect.MakeXYWH(hx - 50 * s, hy - 82 * s, 100 * s, 90 * s), 180, 180)
    dome.close()
    c.drawPath(dome, K.paint(HAT, alpha))
    c.drawPath(dome, wb.marker(BLACK, 7, alpha))
    _line(c, (hx - 66 * s, hy - 37 * s), (hx + 66 * s, hy - 37 * s), BLACK, 9, alpha)
    badge = skia.Rect.MakeXYWH(x - 30 * s, hy + 85 * s, 60 * s, 34 * s)
    c.drawRoundRect(badge, 5, 5, K.paint("#FFFFFF", alpha))
    c.drawRoundRect(badge, 5, 5, wb.marker(BLUE, 4, alpha))
    K.text(c, "员工", x, hy + 102 * s, 22 * s, "sans_medium", BLUE, alpha)


def draw_leader(c, x, y, s, phase, run, head_dx=0.0, alpha=1.0):
    """组长老张：红帽、红袖章“组长”、左手夹板；phase 为跑步相位（0–1 一步），run 为跑动强度 0–1。"""
    bob = -abs(math.sin(math.pi * phase)) * 16 * run
    y0 = y + bob
    hy = y0 - 290 * s
    sh = (x, hy + 80 * s)
    hip = (x, y0 - 120 * s)
    sw = math.sin(2 * math.pi * phase) * run
    _line(c, (x, hy + 45 * s), hip, BLACK, 11, alpha)
    for sgn in (1, -1):
        stand = (x + sgn * 55 * s, y)
        runp = (x + sgn * 75 * s * sw, y0 - 22 * s * max(0.0, -sgn * sw))
        _line(c, hip, (lerp(stand[0], runp[0], run), lerp(stand[1], runp[1], run)), BLACK, 11, alpha)
    # 左手夹板（在身前），右手随跑步摆动
    clip_c = (x - 80 * s, hy + 150 * s)
    _line(c, sh, (clip_c[0] + 10 * s, clip_c[1]), BLACK, 11, alpha)
    rh = (x + 70 * s - 30 * sw * s, hy + 170 * s - 25 * abs(sw) * s)
    _line(c, sh, rh, BLACK, 11, alpha)
    clip = skia.Rect.MakeXYWH(clip_c[0] - 40 * s, clip_c[1] - 55 * s, 80 * s, 105 * s)
    c.drawRoundRect(clip, 6, 6, K.paint(BOARD_C, alpha))
    c.drawRoundRect(clip, 6, 6, wb.marker(BLACK, 6, alpha))
    for i in range(3):
        _line(c, (clip_c[0] - 25 * s, clip_c[1] - 20 * s + i * 22 * s), (clip_c[0] + 25 * s, clip_c[1] - 20 * s + i * 22 * s),
              BLACK, 4, alpha)
    # 红袖章
    ax, ay = lerp(sh[0], rh[0], 0.4), lerp(sh[1], rh[1], 0.4)
    band = skia.Rect.MakeXYWH(ax - 36 * s, ay - 17 * s, 72 * s, 34 * s)
    c.drawRoundRect(band, 6, 6, K.paint(RED, alpha))
    K.text(c, "组长", ax, ay, 22 * s, "sans_medium", "#FFFFFF", alpha)
    hx = x + head_dx
    c.drawCircle(hx, hy, 45 * s, K.paint("#FFFFFF", alpha))
    c.drawCircle(hx, hy, 45 * s, wb.marker(BLACK, 9, alpha))
    for dx in (-15, 15):
        c.drawCircle(hx + dx * s, hy - 4 * s, 4 * s, K.paint(BLACK, alpha))
    m = skia.Path()
    m.addArc(skia.Rect.MakeXYWH(hx - 16 * s, hy + 12 * s, 32 * s, 18 * s), 200, 140)
    c.drawPath(m, wb.marker(BLACK, 6, alpha))
    cap = skia.Path()
    cap.addArc(skia.Rect.MakeXYWH(hx - 47 * s, hy - 70 * s, 94 * s, 70 * s), 180, 180)
    cap.close()
    c.drawPath(cap, K.paint(RED, alpha))
    c.drawPath(cap, wb.marker(BLACK, 6, alpha))
    _line(c, (hx - 10 * s, hy - 35 * s), (hx - 80 * s, hy - 30 * s), BLACK, 10, alpha)   # 帽檐朝左（面向流水线）


# ---------------------------------------------------------------- 第 1 屏

def loop_fn(c, k, T):
    """返工圈：第 2 拍描出；第 4 拍起按实测拍转（4 拍一圈），屏 4 剪断那一拍停转变淡。"""
    t0, t1 = tb(0, 2), tb(0, 2.9)
    tc = tb(3, 5)
    p = clamp01((T - t0) / (t1 - t0))
    spin = 0.0
    if T > core.bt(SPIN0):
        spin = 360 * (beat_pos(min(T, tc)) - SPIN0) / 4
    alpha = 1.0 - 0.55 * ease_out(clamp01((T - tc) / 0.25))
    x, y = LC
    tip = None
    for i in range(2):
        a0 = -90 + i * 180 + spin + 12
        sweep = 150 * p
        pa = skia.Path()
        pa.addArc(skia.Rect.MakeXYWH(x - LR, y - LR, 2 * LR, 2 * LR), a0, sweep)
        c.drawPath(pa, wb.marker(RED, 12, alpha))
        ae = math.radians(a0 + sweep)
        ex, ey = x + LR * math.cos(ae), y + LR * math.sin(ae)
        if p >= 1:
            tx, ty = -math.sin(ae), math.cos(ae)
            for d in (0.55, -0.55):
                hx = ex - 46 * (tx * math.cos(d) - ty * math.sin(d))
                hy = ey - 46 * (tx * math.sin(d) + ty * math.cos(d))
                c.drawLine(ex, ey, hx, hy, wb.marker(RED, 12, alpha))
        elif i == 1 or tip is None:
            tip = (ex, ey)
    # 每转一圈（4 拍）在 12 点方向闪一下
    if p >= 1 and core.bt(SPIN0) <= T < tc:
        dt = T - core.bt(SPIN0 + 4 * int((beat_pos(T) - SPIN0) // 4))
        if dt < 0.35:
            K.ripple(c, x, y - LR, dt, RED, 70, 6, 0.7, 0.35)
    return tip if p < 1 else None


def slam_text(s, x, y, size, color, j, k, font="hand"):
    def fn(c, kk, T):
        sc = slam_scale(T - tb(j, k))
        if sc > 0:
            with K.at(c, x, y, 0, sc):
                K.text(c, s, 0, 0, size, font, color, clamp01((T - tb(j, k)) / 0.06))
        return None
    return fn


def pop_text(s, x, y, size, color, j, k, font="hand"):
    def fn(c, kk, T):
        sc = pop_scale(T - tb(j, k))
        if sc > 0:
            with K.at(c, x, y, 0, sc):
                K.text(c, s, 0, 0, size, font, color, clamp01(sc * 2))
        return None
    return fn


# ---------------------------------------------------------------- 第 2–3 屏：车、员工、绳、灯、组长

def car_path(x, y, s=1.0) -> skia.Path:
    return join(P((x - 85 * s, y - 20 * s), (x - 85 * s, y - 55 * s), (x - 45 * s, y - 60 * s), (x - 25 * s, y - 95 * s),
                  (x + 35 * s, y - 95 * s), (x + 55 * s, y - 60 * s), (x + 85 * s, y - 52 * s), (x + 85 * s, y - 20 * s),
                  close=True),
                circle(x - 48 * s, y - 16 * s, 17 * s), circle(x + 48 * s, y - 16 * s, 17 * s))


def car_offset(T):
    """车相对刹停位置的偏移：刹停前匀速前进，刹停那一拍停住并带回弹（先冲过一点再弹回）。"""
    ts = t_stop()
    if T < ts:
        return -CAR_V * (ts - T)
    dt = T - ts
    return 16 * math.exp(-dt * 7) * math.sin(dt * 22)


def cars_fn(c, k, T):
    t_in, t_mark = tb(1, 3), tb(1, 7)
    a = ease_out(clamp01((T - t_in) / 0.3))
    x0, x1, y = BELT
    off = car_offset(T)
    tilt = -4 * math.exp(-(T - t_stop()) * 7) * math.sin((T - t_stop()) * 22) if T >= t_stop() else 0.0
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(x0, y - 300, x1 + 120, y + 40))
    for i, xs in enumerate(CAR_X):
        cx = xs + off
        with K.at(c, cx, y - 25, tilt):
            pth = car_path(0, 0)
            if i == 1 and T >= t_mark:                         # 员工指着的那辆车：红色描边 + 底色
                m = ease_out(clamp01((T - t_mark) / 0.2))
                c.drawPath(pth, K.paint(RED, 0.2 * m))
                c.drawPath(pth, wb.marker(RED, 12, m))
            c.drawPath(pth, wb.marker(BLACK, 8, a))
    c.restore()
    if T >= t_stop():                                         # 停止线：刹停那一拍砸下
        dt = T - t_stop()
        h = 170 * ease_out(clamp01(dt / 0.12))
        c.drawLine(STOP_X, y + 30, STOP_X, y + 30 - h, wb.marker(RED, 16))
        for i in range(4):
            c.drawLine(STOP_X + 18, y + 10 - i * 40, STOP_X + 18, y - 10 - i * 40, wb.marker(RED, 6, 0.6))
    return None


def worker_hands(T):
    x, y, s = WK
    hy = y - 290 * s
    lh_rest = (x - 70 * s, hy + 170 * s)
    rh_rest = (x + 70 * s, hy + 170 * s)
    car_mid = (CAR_X[1] + car_offset(T), BELT[2] - 80)
    t_pt, t_reach = tb(1, 7), tb(1, 9)
    # 左手：第 7 拍指向那辆车，抓绳后放下
    k_pt = ease_out(clamp01((T - t_pt) / 0.18)) * (1 - ease_in_out(clamp01((T - t_reach) / 0.3)))
    d = (car_mid[0] - x, car_mid[1] - (hy + 80 * s))
    n = math.hypot(*d)
    point = (x + d[0] / n * 160 * s, hy + 80 * s + d[1] / n * 160 * s)
    lh = (lerp(lh_rest[0], point[0], k_pt), lerp(lh_rest[1], point[1], k_pt))
    # 右手：第 9 拍伸手抓绳，drop 那一帧拉到底
    handle = (CORD_X, HANDLE_Y + 30 + pull_dy(T))
    k_r = ease_out(clamp01((T - t_reach) / 0.25))
    rh = (lerp(rh_rest[0], handle[0], k_r), lerp(rh_rest[1], handle[1], k_r))
    return lh, rh


def pull_dy(T):
    return 60 * ease_in_out(clamp01((T - (t_drop() - 0.12)) / 0.12))


def worker_fn(c, k, T):
    x, y, s = WK
    t0 = tb(1, 5)
    p = clamp01((T - t0) / (tb(1, 5.8) - t0))
    c.save()
    tip = _reveal(c, x, y - 380 * s, 400 * s, p)
    lh, rh = worker_hands(T)
    shake = 6 * math.sin((T - t_drop()) * 40) * math.exp(-(T - t_drop()) * 8) if T > t_drop() else 0.0
    draw_worker(c, x, y, s, lh, rh, shake)
    c.restore()
    # 头顶冒“!”（第 6 拍弹出，带回弹）
    sc = pop_scale(T - tb(1, 6))
    if sc > 0:
        with K.at(c, x + 40, y - 290 * s - 150, 0, sc):
            c.drawCircle(0, 0, 46, K.paint("#FFFFFF"))
            c.drawCircle(0, 0, 46, wb.marker(RED, 7))
            c.drawLine(0, -26, 0, 8, wb.marker(RED, 12))
            c.drawCircle(0, 24, 6, K.paint(RED))
    return tip


def cord_fn(c, k, T):
    """安灯绳：松着时微微下垂（弯），拉的那一帧绷直。"""
    dy = pull_dy(T)
    yb = RAIL_Y + (HANDLE_Y + dy - RAIL_Y) * clamp01(k)
    slack = 22 * (1 - dy / 60)
    p = skia.Path()
    p.moveTo(CORD_X, RAIL_Y)
    p.quadTo(CORD_X + slack, (RAIL_Y + yb) / 2, CORD_X, yb)
    c.drawPath(p, wb.marker(ACC, 7))
    if k >= 1:
        c.drawPath(rect(CORD_X, HANDLE_Y + 25 + dy, 34, 56, 10), wb.marker(ACC, 9))
        return None
    return CORD_X, yb


def lamp_fn(c, k, T):
    """安灯：拉绳那一帧亮黄灯（叫组长，带一圈波纹），整条线停下那一拍转红灯。"""
    if T < t_drop():
        return None
    red = T >= t_stop()
    col = RED if red else YELLOW
    t_on = t_stop() if red else t_drop()
    x, y, r = LAMP
    dt = T - t_on
    blink = 0.75 + 0.25 * math.cos((T - t_drop()) * 2 * math.pi / 1.07)
    c.drawCircle(x, y, r * 3.2, K.paint(col, 0.3 * blink, blur=40))
    c.drawCircle(x, y, r - 4, K.paint(col, 0.9 * blink))
    for i in range(8):
        ang = i / 8 * 2 * math.pi
        L = 30 + 18 * ease_out(clamp01(dt / 0.25))
        c.drawLine(x + math.cos(ang) * (r + 18), y + math.sin(ang) * (r + 18),
                   x + math.cos(ang) * (r + 18 + L), y + math.sin(ang) * (r + 18 + L), wb.marker(col, 7, blink))
    if dt < 0.6:
        K.ripple(c, x, y, dt, col, 230, 8, 0.8, 0.6)
    return None


LEAD_STEPS = [2230, 2050, LD[0]]          # 组长在屏 3 第 0、1、2 拍脚落地的位置


def leader_fn(c, k, T):
    """组长：屏 3 第 0–2 拍从右侧跑进来（每拍一步），第 5–6 拍摇头。"""
    x, y, s = LD
    bp = beat_pos(T) - SCREENS[2][0]          # 屏 3 内的小数拍
    if bp < 2:
        i = int(max(0, math.floor(bp)))
        f = bp - i
        xx = lerp(LEAD_STEPS[i], LEAD_STEPS[min(i + 1, 2)], ease_in_out(f))
        run, phase = 1.0, f
    else:
        settle = clamp01((bp - 2) / 0.5)
        xx, run, phase = x, 1 - settle, 0.5 * (1 - settle)
    hd = 0.0
    if tb(2, 5) <= T < tb(2, 6.5):
        dt = T - tb(2, 5)
        hd = 14 * math.sin(dt * 2 * math.pi * 3.2) * (1 - clamp01(dt / 0.8))
    draw_leader(c, xx, y, s, phase % 1.0, run, hd)
    if run > 0.05:                                     # 速度线
        for i in range(3):
            yy = y - 230 + i * 50
            c.drawLine(xx + 90, yy, xx + 90 + 90 * run - i * 18, yy, wb.marker(BLACK, 7, 0.7 * run))
    for i in range(3):                                 # 每步落脚扬一点土
        dt = T - tb(2, i)
        if 0 <= dt < 0.3:
            K.ripple(c, LEAD_STEPS[i], y + 4, dt, "#8A8F99", 60, 5, 0.6, 0.3)
    return None


def bubble_fn(c, k, T):
    """组长头顶的“修”气泡：第 4 拍弹出。"""
    sc = pop_scale(T - tb(2, 4))
    if sc <= 0:
        return None
    x, y = LD[0] - 20, 1640
    with K.at(c, x, y, 0, sc):
        c.drawRoundRect(skia.Rect.MakeXYWH(-85, -70, 170, 140), 40, 40, K.paint("#FFFFFF"))
        c.drawPath(wb.bubble(0, 0, 170, 140, -1), wb.marker(BLACK, 7))
        K.text(c, "修", 0, 0, 96, "hand", BLACK)
    return None


# ---------------------------------------------------------------- 分镜

x0, x1, by = BELT

# 屏 1（12 拍）：小李返工第三遍
j = b.shot("", "打工人日常", view=VA, bars=4)
b.path(j, 0, 0.8, join(desk(780, 990, 380), wb.stick(600, 1140, 0.85, "hold", tie=True, hair=True)), sfx="wood_high")
b.path(j, 0.8, 0.95, wb.face(600, 1140, 0.85, "sad"))
b.custom(j, 1, 1.3, pop_text("小李 · 打工人", 720, 790, 54, BLACK, j, 1, "sans_medium"), sfx="pop")
b.path(j, 1.3, 1.9, doc(*LC, 150, 190), BLACK, 9)
b.custom(j, 2, 2.9, loop_fn, sfx="wood_high")
b.custom(j, 3, 3.3, slam_text("第3遍", LC[0], 520, 96, RED, j, 3), sfx="rim")
b.hit(j, 4, "shaker", 0.6, "返工圈开始按拍转")
b.custom(j, 6, 6.3, pop_text("补", 1030, 700, 80, GREEN, j, 6), sfx="pop")
b.path(j, 6.3, 6.8, check(1030, 830, 42), GREEN, 11)
b.custom(j, 7, 7.3, pop_text("坏", 1680, 700, 80, RED, j, 7), sfx="rim", gain=0.7)
b.path(j, 7.3, 7.8, cross(1680, 830, 38), RED, 11)
b.hit(j, 8, "wood_low", 0.8, "返工圈转满一圈")

# 屏 2（14 拍）：员工看到毛病，拉绳（drop）
KD = DROP - SCREENS[1][0]
j = b.shot("", "丰田模式 · 书中做法", view=VB, bars=4, shake=[(KD, 16.0)], flashes=[(KD, 0.45)])
b.path(j, 0, 0.7, book(540, 1310, 150, 100), GREEN, 7, sfx="wood_low")
b.text(j, 1, 1.8, "丰田模式", 760, 1310, 60, GREEN, sfx="pop")
b.path(j, 2, 2.8, join(rect((x0 + x1) / 2, by + 12, x1 - x0 + 40, 46, 20),
                       *[circle(xx, by + 12, 13) for xx in range(x0 + 40, x1, 110)]), sfx="wood_high")
b.custom(j, 3, 3.3, cars_fn, sfx="pop")
b.custom(j, 5, 5.8, worker_fn, sfx="wood_high")
b.text(j, 5.8, 5.95, "员工", WK[0], 2220, 60, BLUE)
b.text(j, 5.95, 6.0, "小王", WK[0], 2290, 48, BLUE)
b.hit(j, 6, "pop", 0.9, "员工头顶冒“!”")
b.hit(j, 7, "rim", 0.8, "员工指向那辆车，车身标红")
b.path(j, 8, 8.5, join(P((x0, RAIL_Y), (1760, RAIL_Y)), P((LAMP[0], RAIL_Y), (LAMP[0], LAMP[1] - LAMP[2])),
                       circle(*LAMP)), BLACK, 9, sfx="wood_high")
b.custom(j, 8.5, 8.9, cord_fn)
b.hit(j, 9, "shaker", 0.7, "员工伸手抓住安灯绳")
b.custom(j, KD, KD + 1, lamp_fn, sfx="kick", gain=0.9)          # drop：拉直绳子，黄灯亮

# 屏 3（12 拍）：组长跑来，修不好，整条线刹停
j = b.shot("", "丰田模式 · 书中做法", view=VB2, bars=4, shake=[(7, 10.0), (8, 18.0)])
b.custom(j, 0, 0.1, leader_fn, sfx="bongo_low", gain=0.9)
b.hit(j, 1, "bongo_low", 0.9, "组长脚步")
b.hit(j, 2, "bongo_low", 0.9, "组长脚步（站定）")
b.text(j, 2.4, 2.75, "组长", LD[0], 2220, 60, RED)
b.text(j, 2.75, 3.0, "老张", LD[0], 2290, 48, RED)
b.custom(j, 4, 4.3, bubble_fn, sfx="pop")
b.path(j, 5, 5.35, cross(LD[0] - 20, 1640, 75), RED, 13, sfx="rim")
b.hit(j, 7, "tom", 0.9, "车辆刹停 + 停止线 + 转红灯")
b.custom(j, 8, 8.3, slam_text("停！", 860, 1760, 150, RED, j, 8), sfx="kick", gain=0.85)

# 屏 4（11 拍）：拉远，剪断返工圈
j = b.shot("", "接下来", view=VC, bars=4, shake=[(5, 12.0)])
b.path(j, 1, 1.8, arrow((1680, 1430), (1530, 1040), 0.18, 44), GREEN, 11, sfx="wood_high")
b.hit(j, 2, "wood_low", 0.8, "返工圈转满一圈")
b.custom(j, 3, 3.3, pop_text("？", 2060, 1180, 280, RED, j, 3), sfx="pop")
b.path(j, 5, 5.2, P((1080, 560), (1640, 1100)), RED, 22, sfx="frame", gain=0.9)
b.path(j, 7, 7.3, arrow((2060, 1350), (2060, 1520), 0.0, 44), RED, 12, sfx="pop", gain=0.6)

ep = core.Episode(1, "sample", "停线", "丰田模式样片", ACC, b.shots, refs=[])
for s, (k0, k1) in zip(b.shots, SCREENS):
    s.b0, s.t0, s.t1 = k0, core.bt(k0), core.bt(k1)
b.shots[0].t0 = S
b.attach(ep)
END = core.bt(SCREENS[-1][1]) - S

# ---------------------------------------------------------------- 旁白


def stretch(x, text):
    """逗号处补停顿到约 COMMA 秒（预期位置 ±12% 内最安静的 30ms 切开）。返回 (音频, 各逗号后分句起点秒)。"""
    clauses = text.rstrip("。：？！").split("，")
    hz = [sum(1 for ch in cl if ch not in "。：？！") for cl in clauses]
    total = sum(hz)
    hop = int(0.01 * audio.SR)
    starts, added, acc = [], 0, 0
    for ci in range(len(clauses) - 1):
        acc += hz[ci]
        n = len(x) // hop
        r = np.sqrt(np.mean(x[: n * hop].reshape(n, hop) ** 2, 1))
        r3 = np.convolve(r, np.ones(3) / 3, "same")
        orig_n = (len(x) - added) // hop
        center = int(acc / total * orig_n) + added // hop
        lo, hi = max(1, center - int(0.12 * orig_n)), min(n - 1, center + int(0.12 * orig_n))
        i = lo + int(np.argmin(r3[lo:hi]))
        quiet = r3 < r.max() * 10 ** (-32 / 20)
        a = i
        while a > 0 and quiet[a - 1]:
            a -= 1
        e = i
        while e < n and quiet[e]:
            e += 1
        have = (e - a) / 100 if quiet[i] else 0.0
        add = int(max(0.0, COMMA - have) * audio.SR)
        cut = i * hop
        f = int(0.008 * audio.SR)
        left, right = x[:cut].copy(), x[cut:].copy()
        left[-f:] *= np.linspace(1, 0, f)
        right[:f] *= np.linspace(0, 1, f)
        x = np.concatenate([left, np.zeros(add), right])
        added += add
        starts.append((cut + add) / audio.SR - min(0.05, have / 2))
    return x, starts


def narration():
    nar = audio.Narrator(**NARRATOR)
    raw = [nar.generate(t, **GENERATE) for t, _ in LINES]
    clips, inner = zip(*[stretch(x, t) for x, (t, _) in zip(raw, LINES)])
    d = [len(x) / audio.SR for x in clips]
    loc = lambda T: T - S
    st = [0.25, None, loc(b.shots[1].t0) + 0.45, loc(t_drop()) - d[3] - 0.03, loc(b.shots[2].t0) + 0.3,
          loc(b.shots[3].t0) + 0.3, None]
    st[1] = st[0] + d[0] + PERIOD
    st[6] = st[5] + d[5] + 0.4
    for i in range(1, len(st)):
        if st[i] < st[i - 1] + d[i - 1] + 0.3:
            raise ValueError(f"第 {i + 1} 句与上一句太近：{st[i]:.2f}s")
    caps, table = [], []
    for (text, pieces), s0, du, cuts in zip(LINES, st, d, inner):
        if len(pieces) not in (1, len(cuts) + 1):
            raise ValueError(f"字幕条数与逗号不符：{text}")
        bounds = [s0] + ([s0 + c_ for c_ in cuts] if len(pieces) > 1 else [])
        for t_, cap in zip(bounds, pieces):
            caps.append([t_, None, cap])
        table.append((text, s0, du))
    for i, cp in enumerate(caps):
        cp[1] = caps[i + 1][0] if i + 1 < len(caps) else None
    return list(zip(st, clips)), caps, table, raw


# ---------------------------------------------------------------- 画面

CAPS: list = []
DUR = END
_DUMMY = skia.Surface(8, 8).getCanvas()
REST = [(1850, 1450), (1760, 2380), (2080, 2500), (2190, 1760)]     # 每屏手的停放处（画面右下角外沿）


def draw_caption(c, t):
    for t0, t1, cap in CAPS:
        if t0 <= t and (t1 is None or t < t1):
            break
    else:
        return
    k = clamp01((t - t0) / 0.2)
    size = 70
    segs = gfx.parse_marks(cap)
    total = sum(K.text_w(s, size, "serif") for s, _ in segs)
    x = core.W / 2 - total / 2
    y = core.CAP_Y + 8 * (1 - ease_out(k))
    for s, hi in segs:
        w = K.text_w(s, size, "serif")
        if hi:
            c.drawRoundRect(skia.Rect.MakeXYWH(x - 6, y + size * 0.08, w + 12, size * 0.38), 8, 8,
                            K.paint(K.tint(ACC, 0.6), 0.85 * k))
        x += K.text(c, s, x, y, size, "serif", K.INK, k, "left")


def idle_tip(T):
    """手的停放：最近画完的那一笔终点；空闲 0.4 秒后慢慢挪到本屏右下角，让出画面。逐帧独立求值。"""
    best, tip = -1.0, None
    for it in b.items:
        t1 = b.t_of(it["j"], it["k1"])
        if t1 > T or t1 < best:
            continue
        if it["kind"] == "path":
            p = wb.partial(it["path"], 0.999)[1]
        elif it["kind"] == "text":
            p = (it["x"] + K.text_w(it["s"], it["size"], it["font"]) / 2, it["y"])
        else:
            p = it["fn"](_DUMMY, 0.999, t1 - 1e-3)
            if p is None:
                continue
        best, tip = t1, p
    j = ep.shot_at(T)
    rest = REST[j]
    if tip is None or best < ep.shots[j].t0:
        return rest
    m = ease_in_out(clamp01((T - best - 0.4) / 0.6))
    return lerp(tip[0], rest[0], m), lerp(tip[1], rest[1], m)


def frame(c, t):
    T = S + t
    b._last_tip = idle_tip(T)
    s = ep.shots[ep.shot_at(T)]
    g = core.G(c, ep, s, T - s.t0)
    wb.render_board(c, b, T)
    for kb, pk in s.flashes:
        a = fx.flash_alpha(g.since(kb), pk)
        if a > 0:
            c.drawPaint(K.paint("#FFFFFF", a))
    c.drawRect(skia.Rect.MakeLTRB(0, wb.CAP_TOP, core.W, wb.CAP_BOTTOM), K.paint("#FFFFFF", 0.82, blur=8))
    draw_caption(c, t)
    c.drawRect(skia.Rect.MakeLTRB(0, 0, core.W, 318), K.paint("#FBFBF9", 1.0, blur=6))
    core.draw_header(c, ep, s, T, g)
    y, xa, xb = 300, 72, core.W - 72
    K.seg(c, xa, y, xb, y, K.LINE, 4)
    K.seg(c, xa, y, xa + (xb - xa) * clamp01(t / DUR), y, ACC, 4)


def _render(i):
    surf = skia.Surface.MakeRaster(skia.ImageInfo.Make(core.W, core.H, skia.kRGBA_8888_ColorType,
                                                       skia.kPremul_AlphaType))
    frame(surf.getCanvas(), i / core.FPS)
    return surf.makeImageSnapshot().tobytes()


def still(t, path):
    surf = skia.Surface.MakeRaster(skia.ImageInfo.Make(core.W, core.H, skia.kRGBA_8888_ColorType,
                                                       skia.kPremul_AlphaType))
    frame(surf.getCanvas(), t)
    surf.makeImageSnapshot().save(path, skia.kPNG)


# ---------------------------------------------------------------- 混音

def _lufs(x):
    import pyloudnorm
    return pyloudnorm.Meter(audio.SR).integrated_loudness(x)


def limiter(x, ceil_db=-2.0, look=0.004):
    ceil = 10 ** (ceil_db / 20)
    need = np.minimum(1.0, ceil / np.maximum(np.max(np.abs(x), axis=1), 1e-9))
    w = 2 * max(3, int(look * audio.SR)) + 1
    g = uniform_filter1d(minimum_filter1d(need, w), w)
    return x * np.minimum(g, minimum_filter1d(need, 3))[:, None]


def build_audio(voice_clips):
    n = int(DUR * audio.SR)
    v = np.zeros(n)
    for st, x in voice_clips:
        audio.place(v, x, st)
    v = audio.process_voice(v)
    voice = audio.pan(v, 0) * 1.41
    m0 = int(round(S * audio.SR))
    music = bgm.load()[m0: m0 + n].copy()
    fi, fo = int(0.3 * audio.SR), int(0.8 * audio.SR)
    music[:fi] *= np.linspace(0, 1, fi)[:, None]
    music[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5
    sfx = np.zeros((n, 2))
    events = []
    for k, s in enumerate(ep.shots):
        for beat, name, gain, note in s.all_hits():
            gi = s.b0 + int(round(beat))
            bt_ = core.BEATS[gi]
            name = core.resolve_sfx(name, bt_)
            clip = perc.sound(name) * core.SFX_LEVEL.get(name, 0.3) * gain
            lead = perc.attack_ms(name) / 1000
            t = bt_["t"] - S
            audio.place(sfx, audio.pan(clip, 0), t - lead)
            fr = int(round(t * core.FPS))
            events.append(dict(shot=k + 1, kb=int(round(beat)), beat=gi, t=t, sfx=name, note=note, frame=fr,
                               frame_err=round(t * core.FPS - fr, 2)))
    lv = _lufs(voice)
    music *= 10 ** ((lv + MUSIC_DB - _lufs(music)) / 20)
    sfx *= 10 ** ((lv + SFX_DB - _lufs(sfx)) / 20)
    music_d = music * (1 - DUCK * audio.duck_envelope(v))[:, None]
    mix = voice + music_d + sfx
    gain = 10 ** ((-14.0 - _lufs(mix)) / 20)
    stems = {"voice": voice * gain, "music": music_d * gain, "sfx": sfx * gain}
    mix = limiter(mix * gain)
    mix = limiter(mix * 10 ** ((-14.0 - _lufs(mix)) / 20))
    return mix.astype(np.float32), stems, sorted(events, key=lambda e: e["t"])


# ---------------------------------------------------------------- 检查与输出

def wording_warnings():
    texts = [("旁白", t) for t, _ in LINES] + [("字幕", c_) for _, ps in LINES for c_ in ps]
    texts += [(f"屏{it['j'] + 1}白板字", it["s"]) for it in b.items if it["kind"] == "text"]
    texts += [("画面字", s) for s in ("小李 · 打工人", "第3遍", "补", "坏", "员工", "组长", "修", "停！", "？")]
    texts += [(f"屏{i + 1}标签", s.tag) for i, s in enumerate(b.shots)]
    out = []
    for where, s in texts:
        hits = wording.check(wording.gfx_plain(s))
        if hits:
            out.append(f"{where}“{s}”：{'、'.join(hits)}")
        if where == "字幕" and core.han(s) > 10:
            out.append(f"字幕“{s}”超过 10 字")
    return out


def screen_table(table):
    rows = []
    for j, s in enumerate(b.shots):
        a, z = (0.0 if j == 0 else s.t0 - S), s.t1 - S
        ends = [b.t_of(it["j"], it["k1"]) - S for it in b.items if it["j"] == j]
        ends += [e - S for e in (core.bt(s.b0 + h[0]) for h in s.hits)]
        last_event = max(ends)
        last_voice = max((st + du for _, st, du in table if a - 0.01 <= st < z), default=a)
        rows.append((j + 1, a, z, z - a, last_event, last_voice, z - max(last_event, last_voice)))
    return rows


def main():
    global CAPS
    OUT.mkdir(parents=True, exist_ok=True)
    for w in wording_warnings():
        print("文案警告：", w, file=sys.stderr)
    clips, CAPS, table, raw = narration()
    print(f"音色 {NARRATOR} {GENERATE}；时长 {DUR:.2f}s，配乐 {S:.2f}–{S + DUR:.2f}s（drop 在 {t_drop() - S:.2f}s）")
    for text, st, du in table:
        print(f"  旁白 {st:5.2f}–{st + du:5.2f}s  {du:.2f}s {core.han(text) / du:.2f}字/秒  {text}")
    for t0, t1, cap in CAPS:
        print(f"  字幕 {t0:5.2f}–{(t1 if t1 is not None else DUR):5.2f}s  {cap}")
    hz12 = core.han(LINES[0][0]) + core.han(LINES[1][0])
    print(f"  前两句（含句间停顿）{hz12 / (table[1][1] + table[1][2] - table[0][1]):.2f} 字/秒")
    for r in screen_table(table):
        print(f"  屏{r[0]} {r[1]:5.2f}–{r[2]:5.2f}s 停留 {r[3]:.2f}s，最后画面事件 {r[4]:.2f}s，旁白止 {r[5]:.2f}s，"
              f"之后停 {r[6]:.2f}s")
    if "--asr" in sys.argv:
        from fengtian.voice_audition import asr_check, edit
        res = asr_check(sys.argv[sys.argv.index("--asr") + 1], raw)
        for (t, _), a in zip(LINES, res):
            ref = "".join(ch for ch in t if ch not in "，。：？")
            print(f"  ASR {a}（原文 {ref}，差 {edit(ref, a)} 字）")
    if "--sheet" in sys.argv:
        for t in (4.9, 10.0, 12.6, 15.2, 16.9, 18.6, 23.4):
            still(t, str(OUT / f"v3_sheet_{t:05.2f}.png"))
        return
    mix, stems, events = build_audio(clips)
    for e in events:
        print(f"  事件 屏{e['shot']} 第{e['kb']}拍 {e['t']:5.2f}s 帧{e['frame']:3d}（偏差 {e['frame_err']:+.2f}） "
              f"{e['sfx']:10s} {e['note']}")
    for k, x in stems.items():
        sf.write(OUT / f"v3_{k}.wav", x.astype(np.float32), audio.SR, subtype="PCM_16")
    hop = int(0.05 * audio.SR)
    vr = np.sqrt(np.maximum(uniform_filter1d(stems["voice"][:, 0] ** 2, hop), 0))
    on = vr > 0.1 * vr.max()
    db = lambda x, m: 10 * np.log10(np.mean(x[m] ** 2) + 1e-12)
    print(f"  人声段：人声 {db(stems['voice'], on):.1f} dB，配乐 {db(stems['music'], on):.1f} dB；"
          f"无人声段配乐 {db(stems['music'], ~on):.1f} dB；积分响度 人声 {_lufs(stems['voice']):.1f} / "
          f"配乐 {_lufs(stems['music']):.1f} / 音效 {_lufs(stems['sfx']):.1f} LUFS")
    out = OUT / "sample_v3.mp4"
    n = int(round(DUR * core.FPS))
    with tempfile.TemporaryDirectory() as tmp:
        wav = str(Path(tmp) / "mix.wav")
        sf.write(wav, mix, audio.SR)
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s",
               f"{core.W}x{core.H}", "-r", str(core.FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset",
               "medium", "-crf", "20", "-tune", "animation", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
               "-shortest", "-movflags", "+faststart", str(out)]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        with get_context("fork").Pool(4) as pool:
            for buf in pool.imap(_render, range(n), chunksize=8):
                proc.stdin.write(buf)
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError("ffmpeg failed")
    print(out)


if __name__ == "__main__":
    main()
