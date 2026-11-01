"""《丰田模式》10 反省：每天都很忙，为什么还在原地？（白板手绘 + AI 旁白，竖屏 2:3；系列收尾）

自测：三道题，符合记一分。第 2–5 屏右上角一直挂着计分卡（三个格子 + “N分”），每答完一题，“+1”飞进格子。
- 0–3 秒：系列开场“丰田模式”四字，缓推到挂历一页页翻到十二月，小李在跑步机上满头大汗，“原地”砸下；一张“小测试”卷子；
- 第一题（drop）：小李一次次跳进同一个坑，“×3”；drop 时第一格填上；
- 第二题：小李把文件扔进文件筐，背过身走掉，文件上冒出问号；第二格；
- 第三题：小王指着文件说“这里不对”，小李双手摆个不停；第三格；计分卡放大，“两分以上”，一只大手拍拍小李的肩，
  旁边一排小人也都举着分数牌；
- 书中做法：“反省”“改善”两张字卡；会议室门牌“反省会”，奖杯放在桌角；白板列“没做好的地方”，说“没问题”的员工被组长追问；
  大野耐一和“没有问题，就是最大的问题”；矮台阶一级一级往上，镜头拉远，一年后已经很高；
- 为什么：左边圆圈跑道上转圈（重复），右边停下回头看，脚下长出往上的路（学）；一本“一年经验”复印十遍叠成“十年经验？”；
- 说回我们：两个季度的汇报卡在同一处；和对象为洗碗吵三次；做饭咸了怪锅，放大镜里是半勺盐；照镜子难为情，大复盘打叉，
  五分钟沙漏，“三步”；三步做法（便签“下次更好”、只圈一行明天改、先说谢谢再解释）；
- 收尾：回头看，身后一条长路插着十面小旗（十讲的概念）；十讲小卡片排成两排，“第一季 完”，第一讲“停线”亮起，评论框。
办公室里的同事小王用本模块的 draw_wang（短发、白衬衫、蓝工牌，不戴安全帽，与第 06、07 讲同一造型）；
安全帽造型（common.draw_worker）只用于车间员工（第 6、7 屏丰田的项目组）；组长 common.draw_leader，大野耐一 common.draw_ohno。
文案见 fengtian/PLAN.md「### 10 反省」；时间轴、配乐、相机、人物见 fengtian/common.py。
"""

import math
from contextlib import contextmanager

import skia

from adler import core
from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from fengtian.common import (BLACK, BLUE, GREEN, ORANGE, RED, YELLOW, draw_leader, draw_li, draw_ohno, draw_worker,
                             pop_scale, rest_hands, walk)
from whiteboard import engine as wb
from whiteboard.engine import P, check, cross, rect

# 每屏：(旁白句序号, 页眉标签, 白板区块)
SCREENS = [
    ([], "开场", 0),
    ([0, 1], "打工人日常", 1),
    ([2], "自测 · 第一题", 2),
    ([3], "自测 · 第二题", 3),
    ([4], "自测 · 第三题", 4),
    ([5], "自测 · 算一算", 5),
    ([6, 7], "丰田模式 · 书中做法", 6),
    ([8, 9], "丰田模式 · 书中做法", 7),
    ([10], "书中观点", 8),
    ([11, 12], "丰田模式 · 书中做法", 9),
    ([13, 14], "为什么光忙没用", 10),
    ([15], "为什么光忙没用", 11),
    ([16, 17], "说回我们自己", 12),
    ([18], "说回我们自己", 13),
    ([19], "说回我们自己", 14),
    ([20, 21], "说回我们自己", 15),
    ([22], "做法一 · 示意", 16),
    ([23], "做法二 · 示意", 17),
    ([24], "做法三 · 示意", 18),
    ([25], "回头看", 19),
    ([26, 27, 28], "系列收尾", 20),
]

L = C.Lesson("10", SCREENS, drop_screen=2, board_size=(5000, 12800))
b = L.b
tb, kb, wt = L.tb, L.kb, L.wt

# 各屏在白板上的区块中心（相邻屏相距 1600，蛇形排列）
_COLS = (900, 2500, 4100)
R = [(2600, 800), (900, 900)] + [(_COLS[i % 3] if (i // 3) % 2 == 0 else _COLS[2 - i % 3], 2500 + 1600 * (i // 3))
                                 for i in range(19)]
Z = 0.72

NOTES = [
    "书目：Jeffrey K. Liker, The Toyota Way（中译本《丰田模式：精益制造的14项管理原则》，机械工业出版社）。",
    "本讲依据：原则 14——通过不断反省（hansei）与持续改善（kaizen）成为学习型组织。书中讲丰田项目即使成功也要开反省会，"
    "专找没做好的地方；“没有问题就是最大的问题”常见归于大野耐一。",
    "自测题、楼梯、跑道、复印本均为示意；小李、小王、组长为虚构人物。",
]

GRAY, GRAY_FILL, GREEN_FILL, RED_FILL, BLUE_FILL = "#8A8F99", "#ECEEF1", "#D3EDDC", "#F6C3BE", "#D5E3F7"
WOOD, NOTE_FILL, SKY, GOLD = "#E3C9A0", "#FFF1A8", "#E4EEF8", "#E0A21B"
CONCEPTS = ["停线", "拉动", "均衡", "单件流", "标准化", "目视化", "现地现物", "五问", "共识", "反省"]


def nbeats(j):
    return L.BOUNDS[j][1] - L.BOUNDS[j][0]


def kq(j, t_local, lo=0):
    """kb，但 lo 超出本屏时夹到最后一拍（排期变短时不报错）。"""
    return kb(j, t_local, lo=min(lo, nbeats(j) - 1))


def klast(j, tail=0.35):
    """本屏最后一个能放画面事件的拍：事件做完（tail 秒）后到切屏至少还停 1.6 秒。"""
    b0, b1 = L.BOUNDS[j]
    return max(k for k in range(b1 - b0) if core.bt(b0 + k) + tail <= core.bt(b1) - 1.6)


def cap(j, k, tail=0.35):
    return min(k, klast(j, tail))


def nx(j, t_local, prev, gap=1):
    """离 t_local 最近、且至少在 prev 之后 gap 拍的拍号。"""
    return max(kq(j, t_local, prev + gap), prev + gap)


# ================================================================ 小工具

def pop_fn(j, k, draw, dur=0.32):
    """第 j 屏第 k 拍弹出：draw(c, sc, T)。"""
    def fn(c, kk, T):
        sc = pop_scale(T - tb(j, k), dur)
        if sc > 0:
            draw(c, sc, T)
        return None
    return fn


@contextmanager
def at_pop(c, x, y, sc):
    c.save()
    c.translate(x, y)
    c.scale(sc, sc)
    c.translate(-x, -y)
    try:
        yield
    finally:
        c.restore()


def ev(j, k, fn, sfx=None, gain=0.8, dur=0.3):
    b.custom(j, k, k + dur, fn, sfx=sfx, gain=gain)


def box(c, x, y, w, h, fill, line, width=6, r=14, alpha=1.0):
    rr = skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h)
    c.drawRoundRect(rr, r, r, K.paint(fill, alpha))
    c.drawRoundRect(rr, r, r, wb.marker(line, width, alpha))


def dashed(c, a, z, color, width, alpha=1.0, on=18, off=12):
    p = K.paint(color, alpha, width)
    p.setPathEffect(skia.DashPathEffect.Make([on, off], 0))
    c.drawLine(a[0], a[1], z[0], z[1], p)


def dashed_path(c, path, color, width, alpha=1.0, on=22, off=16):
    p = K.paint(color, alpha, width)
    p.setPathEffect(skia.DashPathEffect.Make([on, off], 0))
    c.drawPath(path, p)


def head_of(x, y, s):
    return x, y - 290 * s


def sparkle(c, x, y, dt, color=YELLOW, n=8, r0=40, r1=130):
    """放射短线（亮了 / 挺直），dt 为距触发的秒数。"""
    if dt < 0 or dt > 0.9:
        return
    f = ease_out(clamp01(dt / 0.5))
    a = 1 - clamp01((dt - 0.5) / 0.4)
    for i in range(n):
        ang = 2 * math.pi * i / n
        r_a, r_b = lerp(r0, r1 * 0.7, f), lerp(r0 + 20, r1, f)
        C.line(c, (x + math.cos(ang) * r_a, y + math.sin(ang) * r_a), (x + math.cos(ang) * r_b, y + math.sin(ang) * r_b),
               color, 7, a)


def bubble_box(c, x, y, w, h, tail=-1, alpha=1.0, fill="#FFFFFF"):
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h), 40, 40, K.paint(fill, alpha))
    c.drawPath(wb.bubble(x, y, w, h, tail), wb.marker(BLACK, 7, alpha))


def sweat(c, x, y, s=1.0, alpha=1.0):
    """一滴汗：(x, y) 为水滴中心。"""
    p = skia.Path()
    p.moveTo(x, y - 22 * s)
    p.quadTo(x + 16 * s, y + 2 * s, x, y + 12 * s)
    p.quadTo(x - 16 * s, y + 2 * s, x, y - 22 * s)
    c.drawPath(p, K.paint("#BFDDF7", alpha))
    c.drawPath(p, wb.marker(BLUE, 4, alpha))


def doc_card(c, x, y, w=200, h=250, color=BLACK, rows=4, fill="#FFFFFF", rot=0.0):
    """一页文件：(x, y) 为中心，几行灰线。"""
    with K.at(c, x, y, rot):
        box(c, 0, 0, w, h, fill, color, 6, 8)
        for r in range(rows):
            yy = -h / 2 + 50 + r * (h - 80) / max(1, rows - 1)
            C.line(c, (-w / 2 + 30, yy), (w / 2 - 30 - (r % 2) * 40, yy), GRAY, 6)


def trophy(c, x, y, s=1.0):
    """奖杯：(x, y) 为底座底边中点。"""
    cup_ = skia.Path()
    cup_.moveTo(x - 60 * s, y - 210 * s)
    cup_.lineTo(x + 60 * s, y - 210 * s)
    cup_.quadTo(x + 58 * s, y - 120 * s, x, y - 105 * s)
    cup_.quadTo(x - 58 * s, y - 120 * s, x - 60 * s, y - 210 * s)
    cup_.close()
    for sgn in (-1, 1):
        h = skia.Path()
        h.addArc(skia.Rect.MakeXYWH(x + sgn * 62 * s - 26 * s, y - 200 * s, 52 * s, 60 * s), -90 if sgn > 0 else 90, 180)
        c.drawPath(h, wb.marker(GOLD, 8))
    c.drawPath(cup_, K.paint("#FFE39A"))
    c.drawPath(cup_, wb.marker(GOLD, 7))
    C.line(c, (x, y - 105 * s), (x, y - 50 * s), GOLD, 10)
    box(c, x, y - 25 * s, 110 * s, 50 * s, "#C9A227", "#A9842A", 5, 6)
    K.text(c, "★", x, y - 165 * s, 50 * s, "black", "#FFFFFF")


def big_hand(c, x, y, s=1.0, rot=0.0, color=ORANGE):
    """一只大手（手掌朝下）：(x, y) 为掌心。"""
    with K.at(c, x, y, rot, s):
        palm = skia.Rect.MakeXYWH(-55, -50, 110, 100)
        c.drawRoundRect(palm, 36, 36, K.paint("#FBE3CF"))
        for i, (dx, ln) in enumerate(((-42, 70), (-14, 82), (14, 80), (42, 68))):
            f = skia.Rect.MakeXYWH(dx - 13, 30, 26, ln)
            c.drawRoundRect(f, 13, 13, K.paint("#FBE3CF"))
            c.drawRoundRect(f, 13, 13, wb.marker(color, 5))
        th = skia.Rect.MakeXYWH(-95, -10, 60, 26)
        c.drawRoundRect(th, 13, 13, K.paint("#FBE3CF"))
        c.drawRoundRect(th, 13, 13, wb.marker(color, 5))
        c.drawRoundRect(palm, 36, 36, wb.marker(color, 6))
        c.drawRect(skia.Rect.MakeXYWH(-50, -130, 100, 80), K.paint("#FFFFFF"))
        C.line(c, (-50, -130), (-50, -48), color, 6)
        C.line(c, (50, -130), (50, -48), color, 6)


# ================================================================ 本讲人物

WANG_SHIRT, HAIR = "#FFFFFF", "#2E2A28"


def draw_wang(c, x, y, s, lh=None, rh=None, mood="flat", head_dx=0.0, alpha=1.0):
    """同事小王（办公室）：齐耳短发 + 橙色发卡、白衬衫蓝描边、蓝工牌、蓝色四肢；不戴安全帽（与第 06、07 讲同一造型）。"""
    d_lh, d_rh = rest_hands(x, y, s)
    lh, rh = lh or d_lh, rh or d_rh
    hy = y - 290 * s
    sh = (x, hy + 80 * s)
    hip = (x, y - 120 * s)
    for ft in ((x - 50 * s, y), (x + 50 * s, y)):
        C.line(c, hip, ft, BLUE, 10, alpha)
    C.line(c, sh, lh, BLUE, 10, alpha)
    C.line(c, sh, rh, BLUE, 10, alpha)
    torso = skia.Rect.MakeLTRB(x - 42 * s, hy + 55 * s, x + 42 * s, y - 105 * s)
    c.drawRoundRect(torso, 18 * s, 18 * s, K.paint(WANG_SHIRT, alpha))
    c.drawRoundRect(torso, 18 * s, 18 * s, wb.marker(BLUE, 7, alpha))
    c.drawPath(P((x - 16 * s, hy + 58 * s), (x, hy + 82 * s), (x + 16 * s, hy + 58 * s)), wb.marker(BLUE, 5, alpha))
    badge = skia.Rect.MakeXYWH(x - 20 * s, hy + 110 * s, 40 * s, 30 * s)
    c.drawRoundRect(badge, 4, 4, K.paint("#DCE8F7", alpha))
    c.drawRoundRect(badge, 4, 4, wb.marker(BLUE, 4, alpha))
    hx = x + head_dx
    back = skia.Rect.MakeLTRB(hx - 54 * s, hy - 46 * s, hx + 54 * s, hy + 40 * s)
    c.drawRoundRect(back, 26 * s, 26 * s, K.paint(HAIR, alpha))
    c.drawCircle(hx, hy, 45 * s, K.paint("#FFFFFF", alpha))
    c.drawCircle(hx, hy, 45 * s, wb.marker(BLACK, 9, alpha))
    fringe = skia.Path()
    fringe.addArc(skia.Rect.MakeXYWH(hx - 50 * s, hy - 52 * s, 100 * s, 72 * s), 180, 180)
    fringe.close()
    c.drawPath(fringe, K.paint(HAIR, alpha))
    c.drawCircle(hx + 36 * s, hy - 24 * s, 9 * s, K.paint(ORANGE, alpha))
    C._eyes_mouth(c, hx, hy + 4 * s, s, mood, alpha)


def draw_partner(c, x, y, s, lh=None, rh=None, mood="flat", alpha=1.0):
    """小李的对象：高马尾 + 绿色连衣裙。(x, y) 为脚底，身高约 320·s。"""
    d_lh, d_rh = rest_hands(x, y, s)
    lh, rh = lh or d_lh, rh or d_rh
    hy = y - 285 * s
    sh = (x, hy + 80 * s)
    for ft in ((x - 35 * s, y), (x + 35 * s, y)):
        C.line(c, (ft[0] * 0.6 + x * 0.4, y - 90 * s), ft, BLACK, 9, alpha)
    dress = P((x - 32 * s, hy + 55 * s), (x + 32 * s, hy + 55 * s), (x + 72 * s, y - 80 * s), (x - 72 * s, y - 80 * s),
              close=True)
    c.drawPath(dress, K.paint(GREEN_FILL, alpha))
    c.drawPath(dress, wb.marker(GREEN, 7, alpha))
    C.line(c, sh, lh, BLACK, 9, alpha)
    C.line(c, sh, rh, BLACK, 9, alpha)
    tail = skia.Path()
    tail.moveTo(x + 30 * s, hy - 40 * s)
    tail.quadTo(x + 110 * s, hy - 60 * s, x + 95 * s, hy + 40 * s)
    tail.quadTo(x + 80 * s, hy - 10 * s, x + 30 * s, hy - 20 * s)
    tail.close()
    c.drawPath(tail, K.paint(HAIR, alpha))
    c.drawCircle(x, hy, 44 * s, K.paint("#FFFFFF", alpha))
    c.drawCircle(x, hy, 44 * s, wb.marker(BLACK, 8, alpha))
    fringe = skia.Path()
    fringe.addArc(skia.Rect.MakeXYWH(x - 48 * s, hy - 50 * s, 96 * s, 60 * s), 180, 180)
    fringe.close()
    c.drawPath(fringe, K.paint(HAIR, alpha))
    c.drawCircle(x + 34 * s, hy - 40 * s, 9 * s, K.paint(RED, alpha))
    C._eyes_mouth(c, x, hy + 6 * s, s, mood, alpha)


def draw_runner(c, x, y, s, T, mood="flat", speed=9.0):
    """跑步的小李：手脚前后摆、身体上下颠（腿自己画，draw_li 的腿盖不住，所以整个人用线画）。"""
    ph = T * speed
    bob = -abs(math.sin(ph)) * 14 * s
    y0 = y + bob
    hy = y0 - 290 * s
    hip = (x, y0 - 120 * s)
    sh = (x, hy + 80 * s)
    sw = math.sin(ph)
    for sgn in (1, -1):
        knee = (x + sgn * sw * 45 * s, y0 - 60 * s)
        ft = (x + sgn * sw * 75 * s - 10 * s, y - 4 * s if sgn * sw < 0 else y - 30 * s)
        C.line(c, hip, knee, BLACK, 10)
        C.line(c, knee, ft, BLACK, 10)
        hand = (x - sgn * sw * 70 * s, hy + 140 * s - abs(sw) * 20 * s)
        C.line(c, sh, hand, BLACK, 10)
    C.line(c, (x, hy + 45 * s), hip, BLACK, 10)
    c.drawPath(wb.circle(x, hy, 45 * s), wb.marker(BLACK, 10))
    c.drawPath(P((x - 45 * s, hy - 5 * s), (x - 30 * s, hy - 45 * s), (x + 30 * s, hy - 45 * s), (x + 50 * s, hy + 10 * s)),
               wb.marker(BLACK, 10))
    c.drawPath(P((x, hy + 50 * s), (x - 12 * s, hy + 100 * s), (x, hy + 120 * s), (x + 12 * s, hy + 100 * s), close=True),
               wb.marker(BLACK, 10))
    c.drawPath(wb.face(x, y0, s, mood), wb.marker(BLACK, 7))


# ================================================================ 自测：题卡、计分卡、+1

def qcard(j, n, s, k=0):
    """左上角题卡：红底“第n题” + 题眼。"""
    x, y = R[j][0] - 250, R[j][1] - 470
    head = f"第{n}题"
    L.note(head, s)

    def fn(c, kk, T):
        sc = C.slam_scale(T - tb(j, k))
        if sc <= 0:
            return None
        with K.at(c, x, y, -2, sc):
            box(c, 0, 0, 640, 150, "#FFFFFF", BLACK, 7, 22)
            K.rr(c, -205, 0, 190, 100, 20, RED)
            K.text(c, head, -205, 2, 60, "hand", "#FFFFFF")
            K.text(c, s, 100, 2, 66, "hand", BLACK)
        return None
    b.custom(j, k, k + 0.3, fn, sfx="rim", gain=0.75)


SCORE_W, SCORE_H = 380, 170
L.note("计分", "0分", "1分", "2分", "3分", "+1")


def score_xy(j):
    return R[j][0] + 390, R[j][1] - 470


def scorecard(j, n0, k_add=None, k0=0, xy=None, big=1.0, sfx="wood_high"):
    """计分卡：三个格子，前 n0 个已填；k_add 拍第 n0+1 格填上（红底白勾，砸一下）。"""
    x, y = xy or score_xy(j)

    def fn(c, kk, T):
        sc = pop_scale(T - tb(j, k0))
        if sc <= 0:
            return None
        n, dt = n0, 9.0
        if k_add is not None and T >= tb(j, k_add):
            n, dt = n0 + 1, T - tb(j, k_add)
        with K.at(c, x, y, 0, sc * big):
            box(c, 0, 0, SCORE_W, SCORE_H, "#FFFDF4", BLACK, 7, 20)
            K.text(c, "计分", -105, -42, 50, "hand", BLACK)
            g = C.slam_scale(dt) if dt < 1 else 1.0
            with K.at(c, 95, -42, 0, g):
                K.text(c, f"{n}分", 0, 0, 64, "hand", RED)
            for i in range(3):
                sx, sy = -110 + i * 110, 38
                if i < n:
                    gg = C.slam_scale(dt) if i == n0 and dt < 1 else 1.0
                    with K.at(c, sx, sy, 0, gg):
                        c.drawCircle(0, 0, 38, K.paint(RED))
                        c.drawPath(check(0, 2, 20), wb.marker("#FFFFFF", 8))
                else:
                    c.drawCircle(sx, sy, 38, K.paint("#FFFFFF"))
                    c.drawCircle(sx, sy, 38, wb.marker(GRAY, 5))
        return None
    b.custom(j, k0, k0 + 0.3, fn, sfx=sfx if k0 == 0 or k0 != k_add else None, gain=0.55)
    if k_add is not None:
        b.hit(j, k_add, "kick" if j == L.drop_screen else "ding", 0.9, f"计分卡第 {n0 + 1} 格填上")


def plus_one(j, k_from, k_to, src, n0):
    """“+1”在 k_from 拍从 src 弹出，飞到计分卡第 n0+1 格，k_to 拍落进去。"""
    dst = (score_xy(j)[0] - 110 + n0 * 110, score_xy(j)[1] + 38)

    def fn(c, kk, T):
        t0, t1 = tb(j, k_from), tb(j, k_to)
        if T < t0 or T >= t1:
            return None
        f = ease_in_out(clamp01((T - t0 - 0.25) / max(0.1, t1 - t0 - 0.25)))
        x = lerp(src[0], dst[0], f)
        y = lerp(src[1], dst[1], f) - math.sin(f * math.pi) * 120
        with K.at(c, x, y, 0, pop_scale(T - t0) * lerp(1.0, 0.6, f)):
            c.drawCircle(0, 0, 58, K.paint(RED))
            K.text(c, "+1", 0, 3, 62, "black", "#FFFFFF")
        return None
    b.custom(j, k_from, k_from + 0.3, fn, sfx="pop", gain=0.7)


def steps_row(jj, active, k0=0, kq0=None, sfx="wood_high"):
    """右上角三个步骤圆点：第 active 个（0 起）在 k0 拍变红放大。kq0 为圆点出现的拍（默认 0）。"""
    x0, y0 = R[jj][0] + 60, R[jj][1] - 470
    kq0 = 0 if kq0 is None else kq0

    def fn(c, kk, T):
        for i in range(3):
            sc = pop_scale(T - tb(jj, kq0) - i * 0.1)
            if sc <= 0:
                continue
            on = i == active and T >= tb(jj, k0)
            g = 1 + 0.25 * pop_scale(T - tb(jj, k0)) if on else 1.0
            x = x0 + 120 + i * 140
            with K.at(c, x, y0, 0, sc * g):
                c.drawCircle(0, 0, 50, K.paint(RED if on else "#FFFFFF"))
                c.drawCircle(0, 0, 50, wb.marker(RED if on else GRAY, 7))
                K.text(c, str(i + 1), 0, 4, 60, "hand", "#FFFFFF" if on else GRAY)
        return None
    b.custom(jj, min(k0, kq0), min(k0, kq0) + 0.3, fn, sfx=sfx, gain=0.7)
    if k0 != kq0:
        b.hit(jj, k0, "clap", 0.7, f"第 {active + 1} 步亮起")


L.note("1", "2", "3")

# ================================================================ 屏 0：系列开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])

# ================================================================ 屏 1：挂历翻到十二月，小李在跑步机上满头大汗，“原地”；一张“小测试”卷子
cx, cy = R[1]
j = L.scene(1, (cx, cy + 10, Z))
k_cal = 0
k_run = 1
k_fl = [nx(j, wt(0, 0, 0.6), k_run)]
k_fl += [k_fl[0] + 1, k_fl[0] + 2, k_fl[0] + 3]
k_yd = nx(j, wt(0, 2, 0.55), k_fl[3])
k_test = nx(j, wt(1, 0, 0.4), k_yd)
k_rows = nx(j, wt(1, 1, 0.2), k_test)
k_pt = nx(j, wt(1, 2, 0.6), k_rows + 1)
MONTHS = ["一月", "四月", "八月", "十二月"]
L.note(*MONTHS, "原地", "小测试", "+1分")
CAL = (cx - 300, cy - 300)
TM = (cx + 230, cy + 390)              # 跑步机：底边中点


def cal1(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(1, k_cal))
    if sc <= 0:
        return None
    x, y = CAL
    n = sum(1 for k_ in k_fl if T >= tb(1, k_))
    with K.at(c, x, y, 0, sc):
        box(c, 0, 20, 330, 340, "#FFFFFF", BLACK, 8, 14)
        c.drawRect(skia.Rect.MakeXYWH(-165, -150, 330, 80), K.paint(RED))
        for dx in (-90, 0, 90):
            c.drawCircle(dx, -150, 12, K.paint(BLACK))
        for r in range(3):
            for q in range(5):
                c.drawCircle(-120 + q * 60, 60 + r * 50, 8, K.paint(GRAY))
        name = MONTHS[max(0, n - 1)] if n else "一月"
        K.text(c, name, 0, -20, 74 if len(name) < 3 else 66, "hand", RED if n == 4 else BLACK)
        if n:
            dt = T - tb(1, k_fl[n - 1])
            if dt < 0.3:                       # 上一页翻起来
                f = dt / 0.3
                with K.at(c, 0, -110, 0, 1.0, max(0.02, 1 - f)):
                    c.drawRect(skia.Rect.MakeXYWH(-160, 0, 320, 300), K.paint("#FFFFFF", 1 - f * 0.5))
                    c.drawRect(skia.Rect.MakeXYWH(-160, 0, 320, 300), wb.marker(GRAY, 4, 1 - f * 0.5))
        K.text(c, "×12", 230, 120, 60, "hand", GRAY, clamp01((T - tb(1, k_fl[3])) / 0.2))
    return None


L.note("×12")
ev(j, k_cal, cal1, "wood_high", 0.6)
for i, k_ in enumerate(k_fl):
    b.hit(j, k_, "rim" if i == 3 else "wood_high", 0.75 if i == 3 else 0.6, f"挂历翻到{MONTHS[i]}")


def run1(c, sc, T, cx=cx, cy=cy):
    x, y = TM
    with at_pop(c, x, y, sc):
        belt = skia.Rect.MakeXYWH(x - 230, y - 40, 460, 44)
        c.drawRoundRect(belt, 22, 22, K.paint("#3A3F48"))
        off = (T * 260) % 60
        for i in range(9):
            xx = x - 220 + ((i * 60 - off) % 440)
            C.line(c, (xx, y - 30), (xx - 14, y - 8), GRAY, 4)
        C.line(c, (x + 200, y - 40), (x + 240, y - 300), BLACK, 10)
        box(c, x + 240, y - 320, 110, 50, "#C9D6E8", BLUE, 6, 10)
        for dx in (-140, 140):
            c.drawCircle(x + dx, y - 18, 16, K.paint("#FFFFFF"))
        draw_runner(c, x - 20, y - 44, 0.85, T, "sad" if T >= tb(1, k_yd) else "flat")
        hx, hy = x - 20, y - 44 - 290 * 0.85
        for n in range(3):
            ph = (T * 1.6 + n * 0.33) % 1.0
            sweat(c, hx + (-70 if n % 2 else 70) - (n - 1) * 10, hy - 30 + ph * 90, 1.0, 1 - ph)
        for n in range(3):
            C.line(c, (x - 300 - n * 10, hy + 110 + n * 50), (x - 380 - n * 10, hy + 110 + n * 50), GRAY, 6)
    return None


ev(j, k_run, pop_fn(j, k_run, run1), "wood_low", 0.7)


def pin1(c, kk, T, cx=cx, cy=cy):
    t0 = tb(1, k_yd)
    if T < t0:
        return None
    x, y = TM[0] - 20, TM[1] + 20
    g = pop_scale(T - t0)
    with K.at(c, x, y, 0, g):
        c.drawOval(skia.Rect.MakeXYWH(-120, -18, 240, 36), K.paint(RED_FILL))
        c.drawOval(skia.Rect.MakeXYWH(-120, -18, 240, 36), wb.marker(RED, 6))
    return None


b.custom(j, k_yd, k_yd + 0.3, pin1)
ev(j, k_yd, L.stamp("原地", cx + 260, cy - 150, 110, j, k_yd, rot=-7), "kick", 0.9)
b.shots[j].shake = [(k_yd, 9.0)]


def test1(c, kk, T, cx=cx, cy=cy):
    t0 = tb(1, k_test)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    x, y = cx - 300, cy + 200
    with K.at(c, x, y, -4, sc):
        box(c, 0, 0, 380, 420, "#FFFFFF", BLACK, 7, 10)
        K.text(c, "小测试", 0, -150, 70, "hand", BLUE)
        C.line(c, (-140, -100), (140, -100), BLUE, 5)
        for r in range(3):
            g = pop_scale(T - tb(1, k_rows) - r * 0.18)
            if g <= 0:
                continue
            yy = -40 + r * 95
            with K.at(c, 0, yy, 0, g):
                K.text(c, str(r + 1), -140, 0, 50, "hand", BLACK)
                C.line(c, (-100, 12), (80, 12), GRAY, 6)
                c.drawRect(skia.Rect.MakeXYWH(105, -24, 46, 46), K.paint("#FFFFFF"))
                c.drawRect(skia.Rect.MakeXYWH(105, -24, 46, 46), wb.marker(BLACK, 5))
        if T >= tb(1, k_pt):
            g = pop_scale(T - tb(1, k_pt))
            with K.at(c, 120, 260, 0, g):
                K.rr(c, 0, 0, 170, 76, 38, RED)
                K.text(c, "+1分", 0, 2, 50, "hand", "#FFFFFF")
    return None


ev(j, k_test, test1, "wood_low", 0.7)
b.hit(j, k_rows, "pop", 0.6, "卷子上三道题")
b.hit(j, k_pt, "ding", 0.75, "记一分")

# ================================================================ 屏 2：第一题——小李一次次跳进同一个坑，“×3”；drop 时第一格填上
cx, cy = R[2]
j = L.scene(2, (cx, cy + 10, Z))
KD = L.drop_k()
b.shots[j].shake, b.shots[j].flashes = [(KD, 16.0)], [(KD, 0.45)]
qcard(j, 1, "同一个坑")
scorecard(j, 0, KD, k0=1)
k_pit = 2
k_f2 = [max(k_pit + 2, KD - 7), max(k_pit + 4, KD - 5), max(k_pit + 6, KD - 3)]
k_f2 = [min(k_, KD - 3 + 2 * (i - 2)) for i, k_ in enumerate(k_f2)]
k_p2 = KD - 1
GY2 = cy + 420
PIT2 = (cx + 60, GY2)
LI2X = cx - 330
L.note("坑", "×1", "×2", "×3", "今年")


def ground2(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, PIT2[0], GY2, sc):
        C.line(c, (cx - 560, GY2), (cx + 560, GY2), BLACK, 8)
        c.drawOval(skia.Rect.MakeXYWH(PIT2[0] - 170, GY2 - 30, 340, 70), K.paint("#3A3F48"))
        c.drawOval(skia.Rect.MakeXYWH(PIT2[0] - 170, GY2 - 30, 340, 70), wb.marker(BLACK, 6))
        with K.at(c, PIT2[0] + 290, GY2 - 170, 0, 1):
            C.line(c, (0, 0), (0, 160), "#A9773E", 9)
            box(c, 0, -30, 150, 80, "#FFFFFF", ORANGE, 6, 8)
            K.text(c, "坑", 0, -28, 56, "hand", ORANGE)
    return None


ev(j, k_pit, pop_fn(j, k_pit, ground2), "wood_low", 0.7)


def li2(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(2, k_pit))
    if sc <= 0:
        return None
    s = 0.85
    x, y, mood, inpit = LI2X, GY2, "flat", False
    for i, k_ in enumerate(k_f2):
        tf = tb(2, k_)
        if tf - 0.32 <= T < tf:                       # 跳过去
            f = (T - tf + 0.32) / 0.32
            x = lerp(LI2X, PIT2[0], f)
            y = GY2 - math.sin(f * math.pi) * 110
        elif tf <= T < tf + 0.5:                      # 掉在坑里
            x, inpit = PIT2[0], True
            y = GY2 + min(1.0, (T - tf) / 0.08) * 170
            mood = "sad"
        elif tf + 0.5 <= T < tf + 0.8:                # 爬回来
            f = (T - tf - 0.5) / 0.3
            x = lerp(PIT2[0], LI2X, f)
            y = GY2 + 170 * (1 - f) - math.sin(f * math.pi) * 60
            mood = "sad"
        elif T >= tf + 0.8:
            mood = "sad"
    with at_pop(c, LI2X, GY2, sc):
        if inpit:
            c.save()
            c.clipRect(skia.Rect.MakeLTRB(x - 300, y - 600, x + 300, GY2 + 5))
        draw_li(c, x, y, s, mood)
        if inpit:
            c.restore()
            c.drawOval(skia.Rect.MakeXYWH(PIT2[0] - 170, GY2 - 30, 340, 70), wb.marker(BLACK, 6))
    return None


b.custom(j, k_pit, k_pit + 0.3, li2)


def count2(c, kk, T, cx=cx, cy=cy):
    n = sum(1 for k_ in k_f2 if T >= tb(2, k_))
    if n == 0:
        return None
    dt = T - tb(2, k_f2[n - 1])
    with K.at(c, PIT2[0] + 20, cy - 60, -4, C.slam_scale(dt)):
        K.text(c, f"×{n}", 0, 0, 130, "hand", RED)
    with K.at(c, PIT2[0] - 150, cy - 60, 0, pop_scale(T - tb(2, k_f2[0]))):
        K.text(c, "今年", 0, 0, 64, "hand", GRAY)
    return None


ev(j, k_f2[0], count2, "tom", 0.8)
b.hit(j, k_f2[1], "tom", 0.8, "第二次掉进坑")
b.hit(j, k_f2[2], "rim", 0.85, "第三次掉进坑")
plus_one(j, k_p2, KD, (PIT2[0] + 200, cy - 60), 0)

# ================================================================ 屏 3：第二题——文件扔进筐，小李背过身走掉，文件上冒问号；第二格
cx, cy = R[3]
j = L.scene(3, (cx, cy + 10, Z))
qcard(j, 2, "做完就走")
k_s3 = 1
k_put = kq(j, wt(3, 0, 0.6), 2)
k_go = nx(j, wt(3, 1, 0.2), k_put)
k_q3 = nx(j, wt(3, 2, 0.3), k_go + 1)
k_a3 = cap(j, nx(j, wt(3, 2, 0.9), k_q3) + 1)
k_p3 = k_a3 - 1
scorecard(j, 1, k_a3, k0=k_s3)
GY3 = cy + 440
DESK3 = (cx - 260, GY3)
L.note("？", "哪里能更好")


def desk3(c, sc, T, cx=cx, cy=cy):
    x, y = DESK3
    with at_pop(c, x, y, sc):
        top = skia.Rect.MakeXYWH(x - 220, y - 200, 440, 30)
        c.drawRoundRect(top, 8, 8, K.paint(WOOD))
        c.drawRoundRect(top, 8, 8, wb.marker("#A9773E", 6))
        for dx in (-190, 190):
            C.line(c, (x + dx, y - 170), (x + dx, y), "#A9773E", 9)
        tray = P((x - 130, y - 270), (x - 110, y - 200), (x + 110, y - 200), (x + 130, y - 270))
        c.drawPath(tray, wb.marker(BLUE, 8))
    return None


ev(j, 0, pop_fn(j, 0, desk3), "wood_low", 0.7)
DOC3 = (DESK3[0], DESK3[1] - 390)


def doc3(c, kk, T, cx=cx, cy=cy):
    t0 = tb(3, k_put)
    if T < tb(3, 0):
        return None
    if T < t0 - 0.3:
        return None
    f = ease_out(clamp01((T - t0 + 0.3) / 0.3))
    x, y = DOC3[0], lerp(DOC3[1] - 80, DOC3[1], f)
    with K.at(c, x, y, lerp(-12, 0, f), 1):
        doc_card(c, 0, 0, 220, 270)
        if T >= tb(3, k_q3):
            g = pop_scale(T - tb(3, k_q3))
            c.drawOval(skia.Rect.MakeXYWH(-95, -15, 190, 60), wb.marker(RED, 6, clamp01(g)))
            with K.at(c, 150, -110, 0, g):
                K.text(c, "？", 0, 0, 150, "hand", RED)
    return None


b.custom(j, k_put, k_put + 0.3, doc3, sfx="wood_high", gain=0.7)
b.hit(j, k_q3, "pop", 0.8, "文件上冒出问号")


def li3(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(3, 0))
    if sc <= 0:
        return None
    s = 0.85
    t_go = tb(3, k_go)
    x0 = DESK3[0] + 240
    x, dy, moving = walk(T, t_go, tb(3, k_go + 3) - t_go, x0, cx + 470, 12, 3.2)
    hx, hy = head_of(x0, GY3, s)
    back = T >= t_go - 0.1
    rh = (x0 - 140 * s, hy + 60 * s) if T < tb(3, k_put) + 0.2 else None
    with at_pop(c, x0, GY3, sc):
        draw_li(c, x, GY3 + dy, s, "flat", back=back, rh=rh)
        if back:
            for n in range(3):
                C.line(c, (x - 90 - n * 6, GY3 - 260 + n * 50), (x - 150 - n * 6, GY3 - 260 + n * 50), GRAY, 6,
                       1.0 if moving else 0.0)
    return None


b.custom(j, 0, 0.3, li3)
b.hit(j, k_go, "shaker", 0.6, "小李背过身走掉")
ev(j, k_go + 1, L.pop_text("头也不回", cx + 300, cy - 150, 62, GRAY, j, k_go + 1), "wood_high", 0.5)
plus_one(j, k_p3, k_a3, (DOC3[0] + 150, DOC3[1] - 110), 1)

# ================================================================ 屏 4：第三题——小王指出一处，小李双手摆个不停；第三格
cx, cy = R[4]
j = L.scene(4, (cx, cy + 10, Z))
qcard(j, 3, "先解释")
k_s4 = 1
k_wang4 = kq(j, wt(4, 0, 0.3), 1)
k_say4 = nx(j, wt(4, 0, 0.75), k_wang4)
k_wave = nx(j, wt(4, 1, 0.5), k_say4)
k_a4 = cap(j, nx(j, wt(4, 1, 1.0), k_wave) + 1)
k_p4 = k_a4 - 1
scorecard(j, 2, k_a4, k0=k_s4)
GY4 = cy + 450
LI4 = (cx - 300, GY4, 0.9)
WG4 = (cx + 330, GY4, 0.9)
L.note("这里不对", "因为……", "所以……", "解释")


def wang4(c, sc, T, cx=cx, cy=cy):
    x, y, s = WG4
    hx, hy = head_of(x, y, s)
    point = T >= tb(4, k_say4)
    with at_pop(c, x, y, sc):
        draw_wang(c, x, y, s, lh=(x - 150 * s, hy + 40 * s) if point else None, head_dx=-6 if point else 0)
        doc_card(c, x - 30, hy + 150 * s, 150, 190, BLACK, 3, rot=6)
        if point:
            g = pop_scale(T - tb(4, k_say4))
            c.drawCircle(x - 50, hy + 160 * s, 46 * g, wb.marker(RED, 6))
    return None


ev(j, k_wang4, pop_fn(j, k_wang4, wang4), "pop", 0.6)
ev(j, k_say4, L.pop_bubble("这里不对", cx + 280, cy - 150, j, k_say4, 64, RED, tail=1), "pop", 0.7)


def li4(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(4, 0))
    if sc <= 0:
        return None
    x, y, s = LI4
    hx, hy = head_of(x, y, s)
    t0 = tb(4, k_wave)
    with at_pop(c, x, y, sc):
        if T >= t0:
            a = math.sin((T - t0) * 22)
            lh = (x - 60 * s + 40 * s * a, hy + 20 * s)
            rh = (x + 110 * s - 40 * s * a, hy + 10 * s)
            draw_li(c, x, y, s, "sad", lh=lh, rh=rh)
            for sgn, hp in ((-1, lh), (1, rh)):
                for n in range(2):
                    C.line(c, (hp[0] + sgn * (30 + n * 18), hp[1] - 30 + n * 30),
                           (hp[0] + sgn * (55 + n * 18), hp[1] - 40 + n * 30), GRAY, 5)
            sweat(c, hx + 60, hy - 30, 1.1)
        else:
            draw_li(c, x, y, s, "flat")
    return None


b.custom(j, 0, 0.3, li4)
ev(j, k_wave, L.pop_bubble("因为……", cx - 300, cy - 210, j, k_wave, 60, BLACK, tail=-1), "wood_high", 0.7)
ev(j, k_wave + 1, L.pop_bubble("所以……", cx - 110, cy - 60, j, k_wave + 1, 60, BLACK, tail=-1), "wood_high", 0.7)
plus_one(j, k_p4, k_a4, (cx - 300, cy - 210), 2)

# ================================================================ 屏 5：算一算——计分卡放大“两分以上”，大手拍拍小李的肩；一排小人都举着分数牌
cx, cy = R[5]
j = L.scene(5, (cx, cy + 10, Z))
k_two = kq(j, wt(5, 0, 0.5), 0)
k_pat = nx(j, wt(5, 1, 0.3), k_two)
k_ok5 = nx(j, wt(5, 2, 0.4), k_pat + 1)
k_crowd = nx(j, wt(5, 3, 0.1), k_ok5)
GY5 = cy + 450
LI5 = (cx - 330, GY5, 0.95)
L.note("两分以上？", "很正常")


scorecard(j, 3, None, k0=0, xy=(cx - 160, cy - 400), big=1.25)
ev(j, k_two, L.slam_text("两分以上？", cx + 300, cy - 400, 80, RED, j, k_two, rot=-4), "kick", 0.85)
b.shots[j].shake = [(k_two, 8.0)]


def li5(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(5, 0))
    if sc <= 0:
        return None
    x, y, s = LI5
    t_ok = tb(5, k_ok5)
    sq = 0.92 if T < t_ok else lerp(0.92, 1.0, ease_out(clamp01((T - t_ok) / 0.3)))
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, s, "smile" if T >= t_ok else "sad", squash=sq)
    return None


b.custom(j, 0, 0.3, li5, sfx="pop", gain=0.5)


def hand5(c, kk, T, cx=cx, cy=cy):
    t0 = tb(5, k_pat)
    if T < t0 - 0.3:
        return None
    x, y, s = LI5
    shx, shy = x + 40 * s, y - 290 * s * 0.92 + 70 * s
    come = ease_out(clamp01((T - t0 + 0.3) / 0.3))
    dt = T - t0
    pat = 0.0
    for n in range(2):
        d = dt - n * (tb(5, k_pat + 1) - t0)
        if 0 <= d < 0.4:
            pat = max(pat, math.sin(d / 0.4 * math.pi))
    hx = lerp(shx + 330, shx + 95, come)
    hy = lerp(shy - 300, shy - 85, come) + pat * 40
    big_hand(c, hx, hy, 0.85, -25)
    return None


b.custom(j, k_pat, k_pat + 0.3, hand5, sfx="wood_high", gain=0.75)
b.hit(j, k_pat + 1, "wood_high", 0.75, "再拍一下肩")
ev(j, k_ok5, L.pop_text("很正常", cx - 330, cy - 120, 70, GREEN, j, k_ok5), "ding", 0.7)
CROWD = [(cx + 60, "2分"), (cx + 190, "3分"), (cx + 320, "2分"), (cx + 450, "3分")]
L.note(*{c_[1] for c_ in CROWD})


def crowd5(i):
    x, s_ = CROWD[i]
    k_ = k_crowd + i // 2

    def fn(c, kk, T):
        sc = pop_scale(T - tb(5, k_) - (i % 2) * 0.18)
        if sc <= 0:
            return None
        y, s = GY5, 0.55
        hx, hy = head_of(x, y, s)
        with at_pop(c, x, y, sc):
            c.drawPath(wb.stick(x, y, s, "up"), wb.marker(GRAY, 8))
            c.drawPath(wb.face(x, y, s, "smile"), wb.marker(GRAY, 5))
            box(c, x, hy - 70, 100, 64, "#FFFFFF", RED, 5, 8)
            K.text(c, s_, x, hy - 68, 40, "hand", RED)
        return None
    return fn


for i in range(len(CROWD)):
    b.custom(j, k_crowd + i // 2, k_crowd + i // 2 + 0.3, crowd5(i), sfx="pop" if i % 2 == 0 else None, gain=0.6)

# ================================================================ 屏 6：“反省”“改善”两张字卡；会议室门牌“反省会”，奖杯放在桌角
cx, cy = R[6]
j = L.scene(6, (cx, cy + 10, Z))
k_two6 = kq(j, wt(6, 0, 0.5), 0)
k_hs = nx(j, wt(6, 1, 0.85), k_two6)
k_kz = nx(j, wt(6, 2, 0.5), k_hs)
k_room = nx(j, wt(7, 0, 0.5), k_kz)
k_tro = nx(j, wt(7, 1, 0.6), k_room)
k_plate = nx(j, wt(7, 2, 0.7), k_tro)
L.note("两个词", "反省", "改善", "hansei", "kaizen", "反省会", "做成了")


def word6(s_, sub, x, col, k_, cx=cx, cy=cy):
    def fn(c, kk, T):
        sc = C.slam_scale(T - tb(6, k_))
        if sc <= 0:
            return None
        with K.at(c, x, cy - 340, -3 if x < cx else 3, sc):
            box(c, 0, 0, 400, 250, "#FFFFFF", col, 9, 24)
            K.text(c, s_, 0, -20, 130, "hand", col)
            K.text(c, sub, 0, 80, 44, "sans_medium", GRAY)
        return None
    return fn


ev(j, k_two6, L.pop_text("两个词", cx, cy - 530, 60, GRAY, j, k_two6), "wood_high", 0.6)
ev(j, k_hs, word6("反省", "hansei", cx - 250, RED, k_hs), "kick", 0.85)
ev(j, k_kz, word6("改善", "kaizen", cx + 250, BLUE, k_kz), "kick", 0.85)
b.shots[j].shake = [(k_hs, 7.0), (k_kz, 7.0)]
GY6 = cy + 470


def room6(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, GY6, sc):
        door = skia.Rect.MakeXYWH(cx - 520, GY6 - 420, 220, 420)
        c.drawRect(door, K.paint("#F1E3CB"))
        c.drawRect(door, wb.marker("#A9773E", 8))
        c.drawCircle(cx - 330, GY6 - 200, 12, K.paint("#A9773E"))
        for i, x in enumerate((cx - 60, cx + 130)):
            draw_worker(c, x, GY6 - 60, 0.6, mood="flat")
        tab = skia.Rect.MakeXYWH(cx - 220, GY6 - 150, 560, 110)
        c.drawOval(tab, K.paint(WOOD))
        c.drawOval(tab, wb.marker("#A9773E", 8))
    return None


ev(j, k_room, pop_fn(j, k_room, room6), "wood_low", 0.7)


def tro6(c, sc, T, cx=cx, cy=cy):
    x, y = cx + 300, GY6 - 110
    with at_pop(c, x, y, sc):
        trophy(c, x, y, 0.85)
        sparkle(c, x, y - 140, T - tb(6, k_tro), YELLOW, 8, 70, 150)
        K.text(c, "做成了", x + 10, y - 260, 54, "hand", GOLD)
    return None


ev(j, k_tro, pop_fn(j, k_tro, tro6), "clap", 0.75)
ev(j, k_plate, L.stamp("反省会", cx - 410, GY6 - 520, 64, j, k_plate, rot=-3), "rim", 0.85)

# ================================================================ 屏 7：奖杯打叉“不表功”；白板列“没做好的地方”；说“没问题”的员工被组长追问
cx, cy = R[7]
j = L.scene(7, (cx, cy + 10, Z))
k_tro7 = 0
k_x7 = kq(j, wt(8, 0, 0.7), 1)
k_wb7 = nx(j, wt(8, 1, 0.2), k_x7)
k_rows7 = [nx(j, wt(8, 1, 0.6), k_wb7)]
k_rows7 += [k_rows7[0] + 1, k_rows7[0] + 2]
k_ok7 = nx(j, wt(9, 0, 0.5), k_rows7[2])
k_ask = [nx(j, wt(9, 1, 0.3), k_ok7)]
k_ask += [k_ask[0] + 1, k_ask[0] + 2]
GY7 = cy + 460
L.note("表功", "没做好的地方", "没问题")


def tro7(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 380, cy - 140
    with at_pop(c, x, y, sc):
        trophy(c, x, y, 0.75)
        K.text(c, "表功", x, y + 60, 56, "hand", GOLD)
    return None


ev(j, k_tro7, pop_fn(j, k_tro7, tro7), "wood_high", 0.6)
b.path(j, k_x7, k_x7 + 0.4, cross(cx - 380, cy - 230, 130), RED, 14, sfx="rim", gain=0.85)
WB7 = (cx + 190, cy - 230)


def wb7(c, sc, T, cx=cx, cy=cy):
    x, y = WB7
    with at_pop(c, x, y, sc):
        box(c, x, y, 620, 440, "#FFFFFF", BLACK, 8, 12)
        K.text(c, "没做好的地方", x, y - 160, 62, "hand", RED)
        C.line(c, (x - 220, y - 115), (x + 220, y - 115), RED, 5)
        for i, k_ in enumerate(k_rows7):
            f = clamp01((T - tb(7, k_)) / 0.35)
            if f <= 0:
                continue
            yy = y - 50 + i * 85
            K.text(c, str(i + 1), x - 240, yy, 52, "hand", BLACK)
            C.line(c, (x - 190, yy + 8), (x - 190 + (380 - (i % 2) * 90) * f, yy + 8), BLUE, 8)
    return None


ev(j, k_wb7, pop_fn(j, k_wb7, wb7), "wood_low", 0.7)
for i, k_ in enumerate(k_rows7):
    b.hit(j, k_, "wood_high", 0.6, f"白板写下第 {i + 1} 条")
WK7 = (cx - 330, GY7, 0.8)
LD7 = (cx + 200, GY7, 0.85)


def wk7(c, sc, T, cx=cx, cy=cy):
    x, y, s = WK7
    hx, hy = head_of(x, y, s)
    asked = T >= tb(7, k_ask[0])
    with at_pop(c, x, y, sc):
        draw_worker(c, x, y, s, rh=(x + 100 * s, hy + 60 * s) if not asked else None, mood="sad" if asked else "smile")
        if asked:
            sweat(c, hx + 60, hy - 40, 1.0)
    return None


ev(j, k_tro7, pop_fn(j, k_tro7, wk7), None)
ev(j, k_ok7, L.pop_bubble("没问题", cx - 240, cy + 40, j, k_ok7, 60, BLACK, tail=-1, until=(7, k_ask[0])), "pop", 0.7)


def ld7(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(7, k_ok7))
    if sc <= 0:
        return None
    x, y, s = LD7
    hx, hy = head_of(x, y, s)
    lean = -14 * ease_out(clamp01((T - tb(7, k_ask[0])) / 0.3)) if T >= tb(7, k_ask[0]) else 0
    with at_pop(c, x, y, sc):
        draw_leader(c, x, y, s, head_dx=lean)
        for n, k_ in enumerate(k_ask):
            g = C.slam_scale(T - tb(7, k_))
            if g > 0:
                with K.at(c, hx + 90 + n * 90, hy - 110 - (n % 2) * 40, -8 + n * 8, g):
                    K.text(c, "？", 0, 0, 110 - n * 10, "hand", RED)
    return None


b.custom(j, k_ok7, k_ok7 + 0.3, ld7)
for n, k_ in enumerate(k_ask):
    b.hit(j, k_, ("rim", "rim", "kick")[n], 0.75, f"组长追问 {n + 1}")
L.note("？")

# ================================================================ 屏 8：大野耐一 + “没有问题，就是最大的问题”；空着的问题清单冒出红色感叹号
cx, cy = R[8]
j = L.scene(8, (cx, cy + 10, Z))
OH8 = (cx - 340, cy + 460, 1.0)
k_oh = 0
k_q1 = kq(j, wt(10, 0, 0.75), 1)
k_q2 = nx(j, wt(10, 1, 0.75), k_q1)
k_list = 1 if k_q1 > 2 else k_q1
k_bang = k_q2 + 1 if k_q2 + 1 < nbeats(j) - 3 else k_q2
L.note("大野耐一", "没有问题", "就是最大的问题", "问题清单", "!")


def oh8(c, sc, T, cx=cx, cy=cy):
    x, y, s = OH8
    hx, hy = head_of(x, y, s)
    up = T >= tb(8, k_q1)
    with at_pop(c, x, y, sc):
        draw_ohno(c, x, y, s, rh=(x + 130 * s, hy - 40 * s) if up else None, mood="flat")
        K.text(c, "大野耐一", x, y + 60, 54, "hand", GRAY)
    return None


ev(j, k_oh, pop_fn(j, k_oh, oh8), "wood_low", 0.6)


def quote8(c, kk, T, cx=cx, cy=cy):
    t1, t2 = tb(8, k_q1), tb(8, k_q2)
    if T < t1:
        return None
    x, y = cx + 40, cy - 330
    with K.at(c, x, y, 0, pop_scale(T - t1)):
        box(c, 0, 0, 960, 340, "#FFFFFF", BLACK, 8, 26)
        K.text(c, "“", -430, -110, 120, "serif_black", RED)
        K.text(c, "没有问题", 0, -70, 92, "hand", BLACK)
    if T >= t2:
        with K.at(c, x, y + 75, 0, C.slam_scale(T - t2)):
            gx = K.text_w("就是最大的", 96, "hand")
            gw = K.text_w("问题", 96, "hand")
            K.text(c, "就是最大的", -gw / 2, 0, 96, "hand", BLACK)
            K.text(c, "问题", gx / 2, 0, 96, "hand", RED)
    return None


ev(j, k_q1, quote8, "wood_high", 0.7)
b.hit(j, k_q2, "kick", 0.85, "“就是最大的问题”砸下")
b.shots[j].shake = [(k_q2, 9.0)]


def list8(c, sc, T, cx=cx, cy=cy):
    x, y = cx + 250, cy + 230
    with at_pop(c, x, y, sc):
        c.drawRoundRect(skia.Rect.MakeXYWH(x - 170, y - 200, 340, 400), 12, 12, K.paint(C.BOARD_C))
        c.drawRoundRect(skia.Rect.MakeXYWH(x - 170, y - 200, 340, 400), 12, 12, wb.marker(BLACK, 7))
        box(c, x, y + 20, 290, 330, "#FFFFFF", GRAY, 4, 4)
        box(c, x, y - 200, 120, 40, GRAY, BLACK, 4, 8)
        K.text(c, "问题清单", x, y - 110, 50, "hand", BLACK)
        for r in range(3):
            dashed(c, (x - 110, y - 30 + r * 70), (x + 110, y - 30 + r * 70), GRAY, 4)
        if T >= tb(8, k_bang):
            g = C.slam_scale(T - tb(8, k_bang))
            with K.at(c, x + 150, y - 190, 8, g):
                c.drawCircle(0, 0, 62, K.paint(RED))
                K.text(c, "!", 0, 4, 90, "black", "#FFFFFF")
    return None


ev(j, k_list, pop_fn(j, k_list, list8), "wood_high", 0.6)
if k_bang != k_q2:
    b.hit(j, k_bang, "rim", 0.8, "空清单冒出感叹号")

# ================================================================ 屏 9：矮台阶一级一级往上（镜头近）；“一年下来”拉远，台阶已经很高
cx, cy = R[9]
NSTEP, SW, SH = 14, 70, 52
ST0 = (cx - 540, cy + 470)                    # 第一级左下角
k_s1 = kq(j := L.scene(9, (cx - 300, cy + 220, 1.05)), wt(11, 1, 0.3), 0)
k_st = [k_s1 + i for i in range(4)]
k_day = k_st[0]
k_tiny = nx(j, wt(12, 0, 0.6), k_st[3])
k_pull = nx(j, wt(12, 1, 0.75), k_tiny)
k_big = nx(j, wt(12, 2, 0.6), k_pull + 1)
b.move(j, k_pull, (cx, cy + 10, Z), 1.0)
L.note("改善", "第1天", "第2天", "第3天", "第4天", "一点点", "一年后", "原地", "差别大了")


def step_xy(i):
    return ST0[0] + i * SW, ST0[1] - (i + 1) * SH


def stair9(c, kk, T, cx=cx, cy=cy):
    """前 4 级逐拍画出；拉远时其余 10 级一口气长出来。"""
    t_pull = tb(9, k_pull)
    for i in range(NSTEP):
        if i < 4:
            f = clamp01((T - tb(9, k_st[i])) / 0.2)
        else:
            f = clamp01((T - t_pull - 0.25 - (i - 4) * 0.06) / 0.15)
        if f <= 0:
            continue
        x, y = step_xy(i)
        r = skia.Rect.MakeXYWH(x, y, SW, (i + 1) * SH * f)
        c.drawRect(r, K.paint(BLUE_FILL if i < NSTEP - 1 else "#FDE3C8"))
        c.drawRect(r, wb.marker(BLUE, 5))
    C.line(c, (ST0[0] - 60, ST0[1]), (cx + 560, ST0[1]), BLACK, 8)
    return None


b.custom(j, 0, 0.3, stair9)
for i, k_ in enumerate(k_st):
    b.hit(j, k_, ("wood_high", "wood_low")[i % 2], 0.65, f"画出第 {i + 1} 级台阶")
b.hit(j, k_pull + 1, "shaker", 0.7, "其余台阶一口气长出来")


def li9(c, kk, T, cx=cx, cy=cy):
    s = 0.55
    n = sum(1 for k_ in k_st if T >= tb(9, k_))
    pos = n - 1
    t_pull = tb(9, k_pull)
    if T >= t_pull + 0.25:
        f = clamp01((T - t_pull - 0.25) / (NSTEP * 0.06 + 0.3))
        pos = lerp(3, NSTEP - 1, ease_in_out(f))
    if pos < 0:
        x, y = ST0[0] - 40, ST0[1]
    else:
        i = int(pos)
        fr = pos - i
        x0, y0 = step_xy(i)
        x1, y1 = step_xy(min(NSTEP - 1, i + 1))
        x = lerp(x0, x1, fr) + SW / 2
        y = lerp(y0, y1, fr) - math.sin(fr * math.pi) * 20
    if n >= 1 and T < t_pull + 0.25:
        dt = T - tb(9, k_st[n - 1])
        y -= math.sin(clamp01(dt / 0.25) * math.pi) * 30
    top = T >= tb(9, k_big)
    draw_li(c, x, y, s, "smile" if top else "flat", rh=(x + 60 * s, y - 290 * s - 80 * s) if top else None)
    return None


b.custom(j, 0, 0.3, li9, sfx="pop", gain=0.5)


def day9(c, kk, T, cx=cx, cy=cy):
    n = sum(1 for k_ in k_st if T >= tb(9, k_))
    if n == 0 or T >= tb(9, k_pull):
        return None
    x, y = step_xy(n - 1)
    with K.at(c, x + SW / 2, y - 250, 0, pop_scale(T - tb(9, k_st[n - 1]), 0.22)):
        K.text(c, f"第{n}天", 0, 0, 44, "hand", BLUE)
    return None


b.custom(j, k_day, k_day + 0.3, day9)


def tiny9(c, kk, T, cx=cx, cy=cy):
    t0 = tb(9, k_tiny)
    if T < t0 or T >= tb(9, k_pull):
        return None
    x, y = step_xy(1)
    g = pop_scale(T - t0)
    with K.at(c, x + SW + 40, y + SH / 2, 0, g):
        C.line(c, (0, -SH / 2), (0, SH / 2), RED, 5)
        C.line(c, (-14, -SH / 2), (14, -SH / 2), RED, 5)
        C.line(c, (-14, SH / 2), (14, SH / 2), RED, 5)
        K.text(c, "一点点", 110, 0, 46, "hand", RED)
    return None


b.custom(j, k_tiny, k_tiny + 0.3, tiny9, sfx="pop", gain=0.65)


def flat9(c, kk, T, cx=cx, cy=cy):
    t0 = tb(9, k_pull) + 0.6
    if T < t0:
        return None
    x, y = cx + 420, ST0[1]
    with at_pop(c, x, y, pop_scale(T - t0)):
        c.drawPath(wb.stick(x, y, 0.55, "down", hair=True), wb.marker(GRAY, 8))
        c.drawPath(wb.face(x, y, 0.55, "flat"), wb.marker(GRAY, 5))
        K.text(c, "原地", x, y - 230, 48, "hand", GRAY)
    return None


b.custom(j, k_pull + 1, k_pull + 1.3, flat9)


def big9(c, kk, T, cx=cx, cy=cy):
    t0 = tb(9, k_big)
    if T < t0:
        return None
    xa = cx + 300
    ytop = step_xy(NSTEP - 1)[1]
    f = ease_out(clamp01((T - t0) / 0.3))
    C.line(c, (xa, ST0[1] - 10), (xa, lerp(ST0[1] - 10, ytop, f)), RED, 9)
    if f >= 1:
        c.drawPath(P((xa - 26, ytop + 34), (xa, ytop), (xa + 26, ytop + 34)), wb.marker(RED, 9))
    with K.at(c, cx - 160, cy - 470, -4, C.slam_scale(T - t0)):
        K.text(c, "差别大了", 0, 0, 100, "hand", RED)
    K.text(c, "一年后", cx - 160, cy - 360, 52, "hand", GRAY, clamp01((T - tb(9, k_pull)) / 0.3))
    return None


ev(j, k_big, big9, "kick", 0.85)
b.shots[j].shake = [(k_big, 8.0)]

# ================================================================ 屏 10：左：圆圈跑道上转圈（重复）；右：停下回头看，脚下长出往上的路（学）
cx, cy = R[10]
j = L.scene(10, (cx, cy + 10, Z))
k_div = 0
k_loop = 1
k_qq = kq(j, wt(13, 1, 0.6), 2)
k_rep = nx(j, wt(14, 0, 0.8), k_qq)
k_back = nx(j, wt(14, 1, 0.4), k_rep)
k_path = nx(j, wt(14, 2, 0.2), k_back)
k_xue = nx(j, wt(14, 2, 0.9), k_path)
TR10 = (cx - 290, cy + 120)
L.note("光忙", "变强？", "重复", "回头看", "学")
b.path(j, k_div, k_div + 0.6, P((cx, cy - 330), (cx, cy + 540)), GRAY, 6, sfx="wood_high", gain=0.5)
ev(j, k_div, L.pop_text("光忙", cx - 290, cy - 440, 70, BLACK, j, k_div), None)


def loop10(c, sc, T, cx=cx, cy=cy):
    x, y = TR10
    rep = T >= tb(10, k_rep)
    with at_pop(c, x, y, sc):
        rr = skia.Rect.MakeXYWH(x - 240, y - 170, 480, 340)
        c.drawOval(rr, wb.marker(RED if rep else BLACK, 9))
        c.drawOval(skia.Rect.MakeXYWH(x - 170, y - 110, 340, 220), wb.marker(GRAY, 4))
        for a in (0.2, 1.8, 3.4, 5.0):
            px, py = x + math.cos(a) * 205, y + math.sin(a) * 140
            tx, ty = -math.sin(a), math.cos(a) * 0.7
            c.drawPath(P((px - tx * 30 - ty * 18, py - ty * 30 + tx * 18), (px, py),
                         (px - tx * 30 + ty * 18, py - ty * 30 - tx * 18)), wb.marker(RED if rep else GRAY, 6))
        ang = (T - tb(10, k_loop)) * 2.6
        lx, ly = x + math.cos(ang) * 205, y + math.sin(ang) * 140 + 80
        draw_runner(c, lx, ly, 0.45, T, "sad", 12)
    return None


ev(j, k_loop, pop_fn(j, k_loop, loop10), "shaker", 0.7)


def qq10(c, kk, T, cx=cx, cy=cy):
    t0 = tb(10, k_qq)
    if T < t0:
        return None
    with K.at(c, cx + 290, cy - 440, 0, pop_scale(T - t0)):
        K.text(c, "变强？", 0, 0, 70, "hand", BLUE)
    return None


ev(j, k_qq, qq10, "pop", 0.7)
ev(j, k_rep, L.stamp("重复", cx - 290, cy - 260, 72, j, k_rep, rot=-6), "rim", 0.85)
LI10 = (cx + 200, cy + 400, 0.75)
FEET10 = [(cx + 120 - n * 70, cy + 405 + (n % 2) * 18) for n in range(1, 5)]


def li10(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(10, k_loop) - 0.4)
    if sc <= 0:
        return None
    x, y, s = LI10
    hx, hy = head_of(x, y, s)
    back = T >= tb(10, k_back)
    with at_pop(c, x, y, sc):
        for n, (fx, fy) in enumerate(FEET10):
            with K.at(c, fx, fy, 90):
                c.drawOval(skia.Rect.MakeXYWH(-12, -16, 24, 34), K.paint(GRAY, 0.8))
        draw_li(c, x, y, s, "smile" if T >= tb(10, k_xue) else "flat", rh=(x - 110 * s, hy - 10 * s) if back else None)
        if back:
            g = pop_scale(T - tb(10, k_back))
            with K.at(c, hx - 120, hy - 60, 0, g):
                c.drawPath(wb.arrow((60, 0), (-120, 30), -0.35, 30), wb.marker(BLUE, 7))
            K.text(c, "回头看", hx - 110, hy - 140, 52, "hand", BLUE, clamp01(g))
    return None


b.custom(j, k_loop, k_loop + 0.3, li10)
b.hit(j, k_back, "wood_high", 0.7, "小李停下回头看")
PATH10 = skia.Path()
PATH10.moveTo(cx + 120, cy + 420)
PATH10.cubicTo(cx + 260, cy + 400, cx + 300, cy + 200, cx + 360, cy + 60)
PATH10.cubicTo(cx + 400, cy - 40, cx + 450, cy - 120, cx + 480, cy - 200)
b.path(j, k_path, k_path + 1.2, PATH10, GREEN, 16, sfx="wood_low", gain=0.7)


def xue10(c, kk, T, cx=cx, cy=cy):
    t0 = tb(10, k_xue)
    if T < t0:
        return None
    with K.at(c, cx + 380, cy - 230, 0, C.slam_scale(T - t0)):
        c.drawCircle(0, 0, 80, K.paint(GREEN))
        K.text(c, "学", 0, 4, 100, "hand", "#FFFFFF")
    return None


ev(j, k_xue, xue10, "kick", 0.85)

# ================================================================ 屏 11：一本“一年经验”复印十遍叠起来；“十年经验？”
cx, cy = R[11]
j = L.scene(11, (cx, cy + 10, Z))
k_bk = kq(j, wt(15, 0, 0.3), 0)
k_tag11 = nx(j, wt(15, 1, 0.5), k_bk)
k_cp0 = nx(j, wt(15, 2, 0.15), k_tag11)
k_cps = [k_cp0 + i // 2 for i in range(10)]
k_x10 = cap(j, k_cps[-1] + 1)
BK11 = (cx - 330, cy + 120)
STK11 = (cx + 230, cy + 460)
L.note("一年经验", "十年经验？", "×10")


def book(c, x, y, w=260, h=60, rot=0.0, label=True):
    with K.at(c, x, y, rot):
        box(c, 0, 0, w, h, "#FDE3C8", ORANGE, 6, 8)
        C.line(c, (-w / 2 + 18, -h / 2 + 6), (-w / 2 + 18, h / 2 - 6), ORANGE, 5)
        if label:
            K.text(c, "一年经验", 14, 2, 36, "hand", ORANGE)


def bk11(c, sc, T, cx=cx, cy=cy):
    x, y = BK11
    with at_pop(c, x, y, sc):
        box(c, x, y, 300, 380, "#FDE3C8", ORANGE, 8, 14)
        C.line(c, (x - 120, y - 180), (x - 120, y + 180), ORANGE, 7)
        K.text(c, "一年", x + 20, y - 60, 84, "hand", ORANGE)
        K.text(c, "经验", x + 20, y + 40, 84, "hand", ORANGE)
        draw_li(c, x - 210, cy + 470, 0.6, "flat", rh=(x - 150, cy + 470 - 290 * 0.6 + 60))
    return None


ev(j, k_bk, pop_fn(j, k_bk, bk11), "wood_low", 0.7)


def stack11(c, kk, T, cx=cx, cy=cy):
    x, y = STK11
    t_tag = tb(11, k_tag11)
    if T < t_tag:
        return None
    a = pop_scale(T - t_tag)
    with K.at(c, x, y - 330, 0, a):
        dashed(c, (-150, -320), (150, -320), GRAY, 5)
        dashed(c, (-150, -320), (-150, 330), GRAY, 5)
        dashed(c, (150, -320), (150, 330), GRAY, 5)
    for i, k_ in enumerate(k_cps):
        t0 = tb(11, k_) + (i % 2) * 0.27
        if T < t0:
            continue
        f = ease_out(clamp01((T - t0) / 0.25))
        yy = y - 32 - i * 64
        bx = lerp(BK11[0], x, f)
        by = lerp(BK11[1], yy, f)
        book(c, bx, by, 270, 60, (i % 3 - 1) * 2.0)
    return None


b.custom(j, k_tag11, k_tag11 + 0.3, stack11)
for k_ in sorted(set(k_cps)):
    b.hit(j, k_, "wood_high", 0.55, "复印一本叠上去")


def tag11(c, kk, T, cx=cx, cy=cy):
    t0 = tb(11, k_tag11)
    if T < t0:
        return None
    x, y = STK11[0] - 10, cy - 450
    with K.at(c, x, y, 3, pop_scale(T - t0)):
        box(c, 0, 0, 360, 110, "#FFFFFF", BLACK, 6, 16)
        K.text(c, "十年经验", -30, 2, 64, "hand", BLACK)
        K.text(c, "？", 140, 2, 80, "hand", RED, clamp01((T - tb(11, k_x10)) / 0.1))
    return None


ev(j, k_tag11, tag11, "pop", 0.7)
ev(j, k_x10, L.slam_text("×10", cx - 320, cy - 230, 120, RED, j, k_x10, rot=-5), "kick", 0.85)
b.shots[j].shake = [(k_x10, 8.0)]

# ================================================================ 屏 12：一季度汇报交了松口气；二季度同一页同一处又亮红
cx, cy = R[12]
j = L.scene(12, (cx, cy + 10, Z))
LI12 = (cx - 400, cy + 460, 0.85)
k_li12 = 0
k_r1 = kq(j, wt(17, 0, 0.5), 1)
k_ok12 = k_r1 + 1
k_sigh = nx(j, wt(17, 1, 0.4), k_ok12)
k_r2 = nx(j, wt(17, 2, 0.4), k_sigh)
k_red = nx(j, wt(17, 3, 0.6), k_r2)
k_link = k_red + 1
SL1, SL2 = (cx - 190, cy - 300), (cx + 290, cy - 300)
L.note("一季度汇报", "二季度汇报", "交了", "呼", "又卡住")


def slide(c, x, y, title, T, red_from=None, j_=12):
    box(c, x, y, 420, 300, "#FFFFFF", BLACK, 7, 10)
    c.drawRect(skia.Rect.MakeXYWH(x - 210, y - 150, 420, 60), K.paint(BLUE_FILL))
    K.text(c, title, x, y - 118, 44, "hand", BLUE)
    for n, hgt in enumerate((60, 100, 80, 120)):
        c.drawRect(skia.Rect.MakeXYWH(x - 170 + n * 50, y + 110 - hgt, 34, hgt), K.paint("#C9D6E8"))
    for r in range(3):
        C.line(c, (x + 50, y - 40 + r * 50), (x + 170, y - 40 + r * 50), GRAY, 6)
    if red_from is not None and T >= red_from:
        g = pop_scale(T - red_from)
        on = 0.6 + 0.4 * math.sin((T - red_from) * 9)
        c.drawRoundRect(skia.Rect.MakeXYWH(x + 30, y + 10 - 4, 160, 70), 10, 10, K.paint(RED_FILL, on * clamp01(g)))
        c.drawRoundRect(skia.Rect.MakeXYWH(x + 30, y + 10 - 4, 160, 70), 10, 10, wb.marker(RED, 7, clamp01(g)))


def li12(c, sc, T):
    x, y, s = LI12
    hx, hy = head_of(x, y, s)
    sighed = T >= tb(12, k_sigh)
    stuck = T >= tb(12, k_red)
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, s, "sad" if stuck else ("smile" if sighed else "flat"),
                lh=(x - 50 * s, hy - 15 * s) if stuck else None, rh=(x + 50 * s, hy - 15 * s) if stuck else None)
        if sighed and not stuck:
            d = T - tb(12, k_sigh)
            g = clamp01(d / 0.3) * (1 - clamp01((d - 1.2) / 0.4))
            c.drawOval(skia.Rect.MakeXYWH(hx + 60 + d * 30, hy - 10, 120, 70), K.paint("#EEF4FB", g))
            c.drawOval(skia.Rect.MakeXYWH(hx + 60 + d * 30, hy - 10, 120, 70), wb.marker(BLUE, 5, g))
            K.text(c, "呼", hx + 120 + d * 30, hy + 25, 44, "hand", BLUE, g)
    return None


ev(j, k_li12, pop_fn(j, k_li12, li12), "pop", 0.55)
b.hit(j, k_sigh, "shaker", 0.6, "松一口气")


def r1_12(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(12, k_r1))
    if sc <= 0:
        return None
    with at_pop(c, SL1[0], SL1[1], sc):
        slide(c, SL1[0], SL1[1], "一季度汇报", T, tb(12, k_red))
        if T >= tb(12, k_ok12):
            with K.at(c, SL1[0] - 150, SL1[1] + 210, -6, C.slam_scale(T - tb(12, k_ok12))):
                K.rr(c, 0, 0, 150, 70, 14, GREEN)
                K.text(c, "交了", 0, 2, 48, "hand", "#FFFFFF")
    return None


ev(j, k_r1, r1_12, "wood_low", 0.7)
b.hit(j, k_ok12, "clap", 0.7, "一季度汇报交了")


def r2_12(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(12, k_r2))
    if sc <= 0:
        return None
    x, y = SL2[0], SL2[1] + 330
    with at_pop(c, x, y, sc):
        slide(c, x, y, "二季度汇报", T, tb(12, k_red))
    return None


ev(j, k_r2, r2_12, "wood_high", 0.7)
b.hit(j, k_red, "rim", 0.85, "两页同一处亮红")


def link12(c, kk, T, cx=cx, cy=cy):
    t0 = tb(12, k_link)
    if T < t0:
        return None
    a = (SL1[0] + 190, SL1[1] + 80)
    z = (SL2[0] + 30, SL2[1] + 330 + 45)
    f = ease_out(clamp01((T - t0) / 0.4))
    dashed(c, a, (lerp(a[0], z[0], f), lerp(a[1], z[1], f)), RED, 7)
    with K.at(c, cx + 290, cy + 300, -3, C.slam_scale(T - t0)):
        K.text(c, "又卡住", 0, 0, 80, "hand", RED)
    return None


ev(j, k_link, link12, "kick", 0.8)

# ================================================================ 屏 13：和对象吵架（锯齿气泡），吵完各自转身；日历上“洗碗”被圈了三次
cx, cy = R[13]
j = L.scene(13, (cx, cy + 10, Z))
GY13 = cy + 470
LI13, PT13 = (cx - 260, GY13, 0.85), (cx + 240, GY13, 0.85)
k_ppl13 = 0
k_zig = kq(j, wt(18, 0, 0.5), 1)
k_turn = nx(j, wt(18, 1, 0.5), k_zig)
k_cal13 = nx(j, wt(18, 2, 0.1), k_turn)
k_c13 = [k_cal13 + 1, k_cal13 + 2, k_cal13 + 3]
CAL13 = (cx, cy - 330)
CIRC13 = [(0, 0), (2, 1), (4, 2)]          # (列, 行)
L.note("洗碗", "同一件事")


def ppl13(c, sc, T, cx=cx, cy=cy):
    turned = tb(13, k_turn) <= T
    angry = tb(13, k_zig) <= T
    with at_pop(c, cx, GY13, sc):
        x, y, s = LI13
        hx, hy = head_of(x, y, s)
        if turned:
            draw_li(c, x - 30, y, s, "sad", back=True)
        else:
            shake = math.sin(T * 30) * 6 if angry else 0
            draw_li(c, x + shake, y, s, "sad" if angry else "flat",
                    rh=(x + 130 * s, hy + 30 * s + shake) if angry else None)
        x, y, s = PT13
        hx, hy = head_of(x, y, s)
        if turned:
            draw_partner(c, x + 30, y, s, mood="sad")
            K.text(c, "哼", x + 140, hy - 40, 56, "hand", GRAY)
        else:
            shake = math.sin(T * 30 + 1) * 6 if angry else 0
            draw_partner(c, x + shake, y, s, lh=(x - 130 * s, hy + 30 * s - shake) if angry else None,
                         mood="sad" if angry else "flat")
    return None


L.note("哼")
ev(j, k_ppl13, pop_fn(j, k_ppl13, ppl13), "pop", 0.6)


def zig13(c, kk, T, cx=cx, cy=cy):
    t0, t1 = tb(13, k_zig), tb(13, k_turn)
    if T < t0 or T >= t1 + 0.25:
        return None
    g = pop_scale(T - t0) * (1 - clamp01((T - t1) / 0.25))
    x, y = cx, GY13 - 380
    with K.at(c, x, y, math.sin(T * 25) * 3, g):
        pts = []
        for i in range(16):
            a = 2 * math.pi * i / 16
            r = 130 if i % 2 == 0 else 85
            pts.append((math.cos(a) * r * 1.3, math.sin(a) * r * 0.9))
        z = P(*pts, close=True)
        c.drawPath(z, K.paint("#FFE2DE"))
        c.drawPath(z, wb.marker(RED, 7))
        c.drawPath(P((-50, -40), (0, -5), (-20, 10), (40, 45)), wb.marker(RED, 9))
    return None


ev(j, k_zig, zig13, "kick", 0.85)
b.shots[j].shake = [(k_zig, 9.0)]
b.hit(j, k_turn, "wood_low", 0.7, "吵完各自转身")


def cal13(c, kk, T, cx=cx, cy=cy):
    t0 = tb(13, k_cal13)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    x, y = CAL13
    with K.at(c, x, y, 0, sc):
        box(c, 0, 0, 780, 360, "#FFFFFF", BLACK, 8, 14)
        c.drawRect(skia.Rect.MakeXYWH(-390, -180, 780, 60), K.paint(RED))
        for r in range(3):
            for q in range(7):
                gx, gy = -330 + q * 110, -70 + r * 90
                C.line(c, (gx - 40, gy + 30), (gx + 40, gy + 30), GRAY_FILL, 4)
        for n, (q, r) in enumerate(CIRC13):
            gx, gy = -330 + q * 110, -70 + r * 90
            K.text(c, "洗碗", gx, gy, 38, "hand", BLACK)
            g = clamp01((T - tb(13, k_c13[n])) / 0.25)
            if g > 0:
                part, _ = wb.partial(wb.circle(gx, gy, 52), max(0.001, g))
                c.drawPath(part, wb.marker(RED, 7))
    return None


ev(j, k_cal13, cal13, "wood_high", 0.7)
for n, k_ in enumerate(k_c13):
    b.hit(j, k_, ("rim", "rim", "kick")[n], 0.75, f"日历上第 {n + 1} 次圈洗碗")

# ================================================================ 屏 14：锅冒烟，小李尝一口“咸！”指着锅“这锅不行”；放大镜里半勺盐
cx, cy = R[14]
j = L.scene(14, (cx, cy + 10, Z))
GY14 = cy + 470
LI14 = (cx - 380, GY14, 0.9)
k_pan = 0
k_salty = kq(j, wt(19, 0, 0.6), 1)
k_blame = nx(j, wt(19, 1, 0.5), k_salty)
k_mag = nx(j, wt(19, 2, 0.3), k_blame)
k_half = nx(j, wt(19, 2, 0.85), k_mag)
STOVE = (cx + 60, GY14)
L.note("咸！", "这锅不行", "半勺", "少放")


def stove14(c, sc, T, cx=cx, cy=cy):
    x, y = STOVE
    with at_pop(c, x, y, sc):
        box(c, x, y - 90, 420, 180, GRAY_FILL, BLACK, 7, 10)
        for dx in (-110, 110):
            c.drawCircle(x + dx, y - 45, 20, K.paint(BLACK))
        pan = skia.Path()
        pan.moveTo(x - 150, y - 210)
        pan.lineTo(x + 150, y - 210)
        pan.quadTo(x + 140, y - 180, x + 110, y - 180)
        pan.lineTo(x - 110, y - 180)
        pan.quadTo(x - 140, y - 180, x - 150, y - 210)
        c.drawPath(pan, K.paint("#3A3F48"))
        C.line(c, (x + 150, y - 205), (x + 300, y - 230), BLACK, 14)
        for n in range(3):
            ph = (T * 0.9 + n * 0.33) % 1.0
            sx = x - 70 + n * 70 + math.sin(T * 3 + n) * 12
            sy = y - 240 - ph * 160
            c.drawCircle(sx, sy, 22 + ph * 18, K.paint(GRAY, 0.35 * (1 - ph)))
    return None


ev(j, k_pan, pop_fn(j, k_pan, stove14), "wood_low", 0.7)


def li14(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(14, 0))
    if sc <= 0:
        return None
    x, y, s = LI14
    hx, hy = head_of(x, y, s)
    salty, blame = T >= tb(14, k_salty), T >= tb(14, k_blame)
    if blame:
        rh = (x + 180 * s, hy + 40 * s + 6 * math.sin(T * 14))
    elif salty:
        rh = (x + 40 * s, hy + 30 * s)
    else:
        rh = (x + 60 * s, hy + 60 * s)
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, s, "sad" if salty else "flat", rh=rh)
        if not blame:
            C.line(c, rh, (rh[0] + 20, rh[1] - 60), "#A9773E", 7)
            c.drawOval(skia.Rect.MakeXYWH(rh[0] + 10, rh[1] - 90, 30, 40), K.paint("#A9773E"))
    return None


b.custom(j, 0, 0.3, li14)
ev(j, k_salty, L.slam_text("咸！", cx - 380, cy - 150, 110, RED, j, k_salty, rot=-6), "rim", 0.85)
ev(j, k_blame, L.pop_bubble("这锅不行", cx + 30, cy - 120, j, k_blame, 60, BLACK, tail=-1), "pop", 0.7)


def mag14(c, kk, T, cx=cx, cy=cy):
    t0 = tb(14, k_mag)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    x, y = cx + 250, cy - 400
    with K.at(c, x, y, 0, sc):
        C.line(c, (-110, 110), (-200, 200), "#A9773E", 22)
        c.drawCircle(0, 0, 150, K.paint("#FFFFFF"))
        c.drawCircle(0, 0, 150, wb.marker(BLACK, 10))
        spoon = skia.Rect.MakeXYWH(-70, -40, 100, 70)
        c.drawOval(spoon, K.paint("#E9EDF2"))
        c.drawOval(spoon, wb.marker(GRAY, 5))
        C.line(c, (30, -5), (110, -40), GRAY, 9)
        half = skia.Path()
        half.addArc(skia.Rect.MakeXYWH(-60, -30, 80, 50), 0, 180)
        half.close()
        c.drawPath(half, K.paint("#FFFFFF"))
        c.drawPath(half, wb.marker(BLUE, 4))
        if T >= tb(14, k_half):
            g = C.slam_scale(T - tb(14, k_half))
            with K.at(c, 0, 80, 0, g):
                K.text(c, "半勺", 0, 0, 56, "hand", BLUE)
            with K.at(c, -250, 30, -4, g):
                K.text(c, "少放", 0, 0, 60, "hand", GREEN)
    return None


ev(j, k_mag, mag14, "wood_high", 0.7)
b.hit(j, k_half, "ding", 0.8, "半勺盐")

# ================================================================ 屏 15：照镜子难为情；大复盘打叉；五分钟沙漏；“三步”
cx, cy = R[15]
j = L.scene(15, (cx, cy + 10, Z))
GY15 = cy + 470
k_mir = 0
k_blush = kq(j, wt(20, 2, 0.3), 1)
k_bind = nx(j, wt(21, 0, 0.4), k_blush)
k_xb = nx(j, wt(21, 0, 0.9), k_bind)
k_hg = nx(j, wt(21, 1, 0.5), k_xb)
k_three = nx(j, wt(21, 2, 0.7), k_hg)
L.note("大复盘", "五分钟", "三步")
MIR = (cx - 200, GY15)


def mir15(c, sc, T, cx=cx, cy=cy):
    x, y = MIR
    blush = T >= tb(15, k_blush)
    with at_pop(c, x, y, sc):
        fr = skia.Rect.MakeXYWH(x - 50, y - 420, 230, 360)
        c.drawOval(fr, K.paint("#EEF4FB"))
        c.drawOval(fr, wb.marker("#A9773E", 10))
        C.line(c, (x + 65, y - 60), (x + 65, y), "#A9773E", 10)
        C.line(c, (x + 10, y), (x + 120, y), "#A9773E", 10)
        for n in range(2):
            C.line(c, (x + 10 + n * 40, y - 360 + n * 20), (x + 40 + n * 40, y - 390 + n * 20), "#FFFFFF", 7)
        c.save()
        c.clipRect(fr)
        draw_li(c, x + 65, y + 40, 0.75, "sad" if blush else "flat", back=False, alpha=0.45)
        c.restore()
        lx, ly, s = x - 230, y, 0.9
        hx, hy = head_of(lx, ly, s)
        draw_li(c, lx, ly, s, "sad" if blush else "flat", back=True,
                rh=(lx + 60 * s, hy + 10 * s) if blush else None)
        if blush:
            g = clamp01((T - tb(15, k_blush)) / 0.3)
            sweat(c, hx - 60, hy - 50, 1.1, g)
    return None


ev(j, k_mir, pop_fn(j, k_mir, mir15), "wood_low", 0.6)
b.hit(j, k_blush, "pop", 0.6, "难为情冒汗")


def bind15(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 260, cy - 330
    with at_pop(c, x, y, sc):
        for n in range(4):
            box(c, x - 30 + n * 14, y + 70 - n * 12, 300, 70, "#FFFFFF", GRAY, 4, 6)
        box(c, x + 30, y - 20, 300, 190, BLUE_FILL, BLUE, 7, 10)
        K.text(c, "大复盘", x + 30, y - 20, 64, "hand", BLUE)
    return None


ev(j, k_bind, pop_fn(j, k_bind, bind15), "wood_low", 0.7)
b.path(j, k_xb, k_xb + 0.4, cross(cx - 230, cy - 320, 150), RED, 14, sfx="rim", gain=0.85)


def hg15(c, sc, T, cx=cx, cy=cy):
    x, y = cx + 300, cy - 300
    t0 = tb(15, k_hg)
    f = clamp01((T - t0) / 6.0)
    with at_pop(c, x, y, sc):
        C.line(c, (x - 90, y - 150), (x + 90, y - 150), "#A9773E", 12)
        C.line(c, (x - 90, y + 150), (x + 90, y + 150), "#A9773E", 12)
        glass = P((x - 70, y - 140), (x + 70, y - 140), (x + 10, y), (x + 70, y + 140), (x - 70, y + 140), (x - 10, y),
                  close=True)
        c.drawPath(glass, K.paint("#FFFFFF"))
        top = P((x - 60 * (1 - f), y - 120 + 110 * f), (x + 60 * (1 - f), y - 120 + 110 * f), (x, y - 5), close=True)
        c.drawPath(top, K.paint(GOLD))
        bot = P((x - 60 * f - 5, y + 140), (x + 60 * f + 5, y + 140), (x, y + 140 - 100 * f - 10), close=True)
        c.drawPath(bot, K.paint(GOLD))
        C.line(c, (x, y), (x, y + 130), GOLD, 4)
        c.drawPath(glass, wb.marker(BLACK, 7))
        K.text(c, "五分钟", x, y + 220, 62, "hand", ORANGE)
    return None


ev(j, k_hg, pop_fn(j, k_hg, hg15), "wood_high", 0.7)
ev(j, k_three, L.slam_text("三步", cx + 300, cy + 60, 130, RED, j, k_three, rot=-5), "kick", 0.9)
b.shots[j].shake = [(k_three, 10.0)]

# ================================================================ 屏 16：做法一——下班前（挂钟六点），小李在便签上写“下次更好”
cx, cy = R[16]
j = L.scene(16, (cx, cy + 10, Z))
steps_row(j, 0)
GY16 = cy + 470
k_clk = kq(j, wt(22, 1, 0.1), 1)
k_desk = 0
k_wr = nx(j, wt(22, 2, 0.1), k_clk)
k_st16 = nx(j, wt(22, 2, 0.9), k_wr + 1)
L.note("下班前", "今天", "下次更好")


def clock16(c, kk, T, cx=cx, cy=cy):
    t0 = tb(16, k_clk)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    x, y = cx - 330, cy - 330
    f = ease_out(clamp01((T - t0) / 0.6))
    with K.at(c, x, y, 0, sc):
        c.drawCircle(0, 0, 130, K.paint("#FFFFFF"))
        c.drawCircle(0, 0, 130, wb.marker(BLACK, 9))
        for i in range(12):
            a = i * math.pi / 6
            C.line(c, (math.cos(a) * 108, math.sin(a) * 108), (math.cos(a) * 122, math.sin(a) * 122), BLACK, 5)
        am = math.radians(-90 + lerp(270, 360, f))
        C.line(c, (0, 0), (math.cos(am) * 95, math.sin(am) * 95), BLACK, 7)
        C.line(c, (0, 0), (0, 70), RED, 10)
        K.text(c, "下班前", 0, 190, 58, "hand", RED)
    return None


ev(j, k_clk, clock16, "wood_high", 0.7)


def desk16(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 20, GY16
    with at_pop(c, x, y, sc):
        writing = T >= tb(16, k_wr)
        lx, s = x - 140, 0.85
        hx, hy = head_of(lx, y, s)
        rh = (lx + 120 * s + 8 * math.sin(T * 16), y - 205) if writing else None
        draw_li(c, lx, y, s, "flat", rh=rh)
        top = skia.Rect.MakeXYWH(x - 300, y - 200, 600, 30)
        c.drawRoundRect(top, 8, 8, K.paint(WOOD))
        c.drawRoundRect(top, 8, 8, wb.marker("#A9773E", 6))
        for dx in (-270, 270):
            C.line(c, (x + dx, y - 170), (x + dx, y), "#A9773E", 9)
        box(c, x + 170, y - 280, 200, 140, "#3A3F48", BLACK, 6, 8)
        C.line(c, (x + 170, y - 210), (x + 170, y - 200), BLACK, 8)
        box(c, lx + 110, y - 208, 90, 16, NOTE_FILL, "#C9A227", 3, 3)
    return None


ev(j, k_desk, pop_fn(j, k_desk, desk16), None)


def note16(c, kk, T, cx=cx, cy=cy):
    t0 = tb(16, k_wr)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    x, y = cx + 220, cy - 200
    with K.at(c, x, y, 4, sc):
        box(c, 0, 0, 380, 300, NOTE_FILL, "#C9A227", 6, 6)
        K.text(c, "今天", 0, -80, 56, "hand", BLACK)
        c.save()
        f = clamp01((T - t0 - 0.2) / 0.8)
        c.clipRect(skia.Rect.MakeXYWH(-180, -10, 360 * f, 120))
        K.text(c, "下次更好", 0, 50, 70, "hand", BLUE)
        c.restore()
        if T >= tb(16, k_st16):
            with K.at(c, 150, 120, 0, C.slam_scale(T - tb(16, k_st16))):
                c.drawCircle(0, 0, 40, K.paint(GREEN))
                c.drawPath(check(0, 2, 22), wb.marker("#FFFFFF", 8))
    return None


ev(j, k_wr, note16, "wood_low", 0.7)
b.hit(j, k_wr + 1, "shaker", 0.55, "便签上写字")
b.hit(j, k_st16, "ding", 0.75, "便签打勾")

# ================================================================ 屏 17：做法二——清单只圈一行；明天（日历翻页）改完打勾；本子上记一笔
cx, cy = R[17]
j = L.scene(17, (cx, cy + 10, Z))
steps_row(j, 1)
k_list17 = 0
k_pick = kq(j, wt(23, 1, 0.5), 1)
k_tmr = nx(j, wt(23, 2, 0.3), k_pick)
k_tick = k_tmr + 1
k_log = nx(j, wt(23, 3, 0.5), k_tick)
LST17 = (cx - 230, cy - 120)
L.note("明天", "改善本", "正")


def list17(c, sc, T, cx=cx, cy=cy):
    x, y = LST17
    with at_pop(c, x, y, sc):
        box(c, x, y, 480, 440, "#FFFFFF", BLACK, 7, 12)
        for r in range(4):
            yy = y - 140 + r * 95
            sel = r == 1
            col = BLACK if sel or T < tb(17, k_pick) else GRAY_FILL
            c.drawRect(skia.Rect.MakeXYWH(x - 200, yy - 22, 44, 44), wb.marker(col if sel else GRAY, 5))
            C.line(c, (x - 130, yy), (x + 180 - (r % 2) * 60, yy), BLUE if sel else GRAY, 8 if sel else 6,
                   1.0 if sel or T < tb(17, k_pick) else 0.35)
        if T >= tb(17, k_pick):
            f = clamp01((T - tb(17, k_pick)) / 0.3)
            part, _ = wb.partial(rect(x, y - 45, 460, 90, 40), max(0.001, f))
            c.drawPath(part, wb.marker(RED, 8))
        if T >= tb(17, k_tick):
            g = C.slam_scale(T - tb(17, k_tick))
            with K.at(c, x - 178, y - 45, 0, g):
                c.drawPath(check(0, 0, 34), wb.marker(GREEN, 11))
    return None


ev(j, k_list17, pop_fn(j, k_list17, list17), "wood_low", 0.6)
b.hit(j, k_pick, "rim", 0.8, "只圈一行")
b.hit(j, k_tick, "ding", 0.8, "改完打勾")


def tmr17(c, kk, T, cx=cx, cy=cy):
    t0 = tb(17, k_tmr)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    x, y = cx + 300, cy - 180
    with K.at(c, x, y, 0, sc):
        box(c, 0, 0, 230, 240, "#FFFFFF", BLACK, 7, 12)
        c.drawRect(skia.Rect.MakeXYWH(-115, -120, 230, 60), K.paint(RED))
        K.text(c, "明天", 0, 30, 70, "hand", RED)
        f = clamp01((T - t0) / 0.35)
        if f < 1:
            with K.at(c, 0, -60, 0, 1.0, max(0.02, 1 - f)):
                c.drawRect(skia.Rect.MakeXYWH(-112, 0, 224, 175), K.paint("#FFFFFF"))
                c.drawRect(skia.Rect.MakeXYWH(-112, 0, 224, 175), wb.marker(GRAY, 4))
    return None


ev(j, k_tmr, tmr17, "wood_high", 0.7)
GY17 = cy + 470


def log17(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(17, 0))
    if sc <= 0:
        return None
    lx, s = cx - 210, 0.75
    hx, hy = head_of(lx, GY17, s)
    t0 = tb(17, k_log)
    w = T >= t0
    with at_pop(c, cx, GY17, sc):
        x, y = cx + 160, cy + 330
        box(c, x, y, 380, 240, "#FFFFFF", ORANGE, 7, 10)
        C.line(c, (x, y - 120), (x, y + 120), ORANGE, 5)
        K.text(c, "改善本", x - 95, y - 70, 46, "hand", ORANGE)
        for n in range(2):
            C.line(c, (x - 170, y + n * 50), (x - 30, y + n * 50), GRAY, 5)
        f = clamp01((T - t0) / 0.5)
        if f > 0:
            C.line(c, (x + 30, y - 60), (x + 30 + 130 * f, y - 60), BLUE, 7)
            K.text(c, "正", x + 100, y + 30, 80, "hand", RED, clamp01((T - t0 - 0.3) / 0.2))
        draw_li(c, lx, GY17, s, "smile" if w else "flat",
                rh=(x - 120 + 8 * math.sin(T * 16), y + 10) if w else None)
    return None


b.custom(j, 0, 0.3, log17)
b.hit(j, k_log, "wood_high", 0.75, "本子上记一笔")

# ================================================================ 屏 18：做法三——小王指出问题，小李先双手合十“谢谢”，再开口
cx, cy = R[18]
j = L.scene(18, (cx, cy + 10, Z))
steps_row(j, 2)
GY18 = cy + 460
LI18, WG18 = (cx - 300, GY18, 0.9), (cx + 330, GY18, 0.9)
k_wg18 = 0
k_pt18 = kq(j, wt(24, 1, 0.6), 1)
k_thx = nx(j, wt(24, 2, 0.5), k_pt18)
k_exp = nx(j, wt(24, 3, 0.5), k_thx)
k_smile = k_exp + 1 if k_exp + 1 < nbeats(j) - 3 else k_exp
L.note("这里有问题", "谢谢", "先", "再", "我是这么想的")


def wg18(c, sc, T, cx=cx, cy=cy):
    x, y, s = WG18
    hx, hy = head_of(x, y, s)
    point = T >= tb(18, k_pt18)
    happy = T >= tb(18, k_smile)
    with at_pop(c, x, y, sc):
        draw_wang(c, x, y, s, lh=(x - 150 * s, hy + 40 * s) if point else None, mood="smile" if happy else "flat")
        doc_card(c, x - 30, hy + 150 * s, 150, 190, BLACK, 3, rot=6)
    return None


ev(j, k_wg18, pop_fn(j, k_wg18, wg18), "pop", 0.6)
ev(j, k_pt18, L.pop_bubble("这里有问题", cx + 260, cy - 180, j, k_pt18, 56, BLACK, tail=1), "pop", 0.7)


def li18(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(18, 0))
    if sc <= 0:
        return None
    x, y, s = LI18
    hx, hy = head_of(x, y, s)
    thx = T >= tb(18, k_thx)
    with at_pop(c, x, y, sc):
        if thx and T < tb(18, k_exp):
            draw_li(c, x, y, s, "smile", lh=(x + 8 * s, hy + 100 * s), rh=(x + 12 * s, hy + 100 * s))
            C.line(c, (x + 10 * s, hy + 70 * s), (x + 10 * s, hy + 112 * s), BLACK, 8)
        elif T >= tb(18, k_exp):
            draw_li(c, x, y, s, "smile", rh=(x + 130 * s, hy + 60 * s))
        else:
            draw_li(c, x, y, s, "flat")
    return None


b.custom(j, 0, 0.3, li18)


def badge_bubble(s_, x, y, k_, badge, col, tail=-1):
    def fn(c, kk, T):
        sc = pop_scale(T - tb(18, k_))
        if sc <= 0:
            return None
        w = K.text_w(s_, 64, "hand") + 100
        with K.at(c, x, y, 0, sc):
            bubble_box(c, 0, 0, w, 140, tail)
            K.text(c, s_, 0, 0, 64, "hand", col)
            with K.at(c, -w / 2 + 10, -70, 0, 1):
                c.drawCircle(0, 0, 40, K.paint(col))
                K.text(c, badge, 0, 3, 48, "hand", "#FFFFFF")
        return None
    return fn


ev(j, k_thx, badge_bubble("谢谢", cx - 360, cy - 250, k_thx, "先", RED), "clap", 0.85)
ev(j, k_exp, badge_bubble("我是这么想的", cx - 130, cy - 40, k_exp, "再", BLUE), "pop", 0.7)
if k_smile != k_exp:
    b.hit(j, k_smile, "wood_high", 0.6, "小王笑了")

# ================================================================ 屏 19：回头看——身后一条长路插着十面小旗（十讲的概念），“很远”
cx, cy = R[19]
j = L.scene(19, (cx, cy + 10, Z))
ROAD = skia.Path()
ROAD.moveTo(cx - 520, cy - 420)
ROAD.cubicTo(cx + 200, cy - 470, cx + 520, cy - 330, cx + 300, cy - 160)
ROAD.cubicTo(cx + 80, cy + 0, cx - 560, cy - 60, cx - 470, cy + 150)
ROAD.cubicTo(cx - 400, cy + 330, cx + 0, cy + 280, cx + 300, cy + 420)
k_road = 0
k_fl0 = kq(j, wt(25, 0, 0.2), 1)
k_flags = [k_fl0 + i // 2 for i in range(10)]
k_lookb = nx(j, wt(25, 1, 0.5), k_flags[-1] - 1)
k_far = nx(j, wt(25, 2, 0.75), max(k_lookb, k_flags[-1]))
L.note(*CONCEPTS, "很远")
b.path(j, k_road, k_road + 1.5, ROAD, "#C9B79A", 30, sfx="wood_low", gain=0.6)
_ROAD_M = skia.PathMeasure(ROAD, False)
_ROAD_LEN = _ROAD_M.getLength()


# 十面小旗在路上的位置（路长比例, 旗面朝右 1 / 朝左 -1）：离线排过，旗面互不重叠、不压路
FLAGS19 = [(0.02, 1), (0.095, 1), (0.17, 1), (0.245, 1), (0.32, 1), (0.395, -1), (0.47, -1), (0.545, -1), (0.62, -1),
           (0.72, 1)]


def flag19(i, cx=cx, cy=cy):
    f, side = FLAGS19[i]
    pos, _ = _ROAD_M.getPosTan(_ROAD_LEN * f)
    x, y = pos.x(), pos.y()
    name = CONCEPTS[i]
    w = K.text_w(name, 40, "hand") + 30
    mx = (4 + w / 2) * side

    def fn(c, kk, T):
        sc = pop_scale(T - tb(19, k_flags[i]) - (i % 2) * 0.27)
        if sc <= 0:
            return None
        with K.at(c, x, y, 0, sc):
            c.drawCircle(0, 0, 8, K.paint("#6B6B6B"))
            C.line(c, (0, 0), (0, -120), "#6B6B6B", 6)
            c.drawPath(rect(mx, -90, w, 56, 8), K.paint(RED if i == 9 else "#FFFFFF"))
            c.drawPath(rect(mx, -90, w, 56, 8), wb.marker(RED, 5))
            K.text(c, name, mx, -88, 40, "hand", "#FFFFFF" if i == 9 else RED)
        return None
    return fn


for i in range(10):
    b.custom(j, k_flags[i], k_flags[i] + 0.3, flag19(i), sfx="pop" if i % 2 == 0 else None, gain=0.55)
LI19 = (cx + 330, cy + 520, 0.7)


def li19(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(19, 0))
    if sc <= 0:
        return None
    x, y, s = LI19
    hx, hy = head_of(x, y, s)
    look = T >= tb(19, k_lookb)
    far = T >= tb(19, k_far)
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, s, "smile" if far else "flat",
                rh=(x + 40 * s, hy - 30 * s) if look else None, lh=(x - 120 * s, hy - 60 * s) if far else None)
        if look:
            g = pop_scale(T - tb(19, k_lookb))
            with K.at(c, hx - 100, hy - 40, 0, g):
                c.drawPath(wb.arrow((40, 0), (-110, -60), 0.3, 28), wb.marker(BLUE, 7))
        sparkle(c, hx, hy - 10, T - tb(19, k_far), YELLOW, 10, 70, 150)
    return None


b.custom(j, 0, 0.3, li19)
b.hit(j, k_lookb, "wood_high", 0.7, "小李回头看")
ev(j, k_far, L.slam_text("很远", cx - 250, cy + 500, 110, RED, j, k_far, rot=-4), "kick", 0.9)
b.shots[j].shake = [(k_far, 9.0)]

# ================================================================ 屏 20：十讲小卡片两排，“第一季 完”；评论框；第一讲“停线”亮起
cx, cy = R[20]
j = L.scene(20, (cx, cy + 10, Z))
k_cd0 = 0
k_cards = [k_cd0 + i // 2 for i in range(10)]
k_end = nx(j, wt(26, 1, 0.5), k_cards[-1])
k_hop = nx(j, wt(27, 1, 0.1), k_end)
k_cmt = nx(j, wt(28, 0, 0.3), k_hop + 2)
k_one = nx(j, wt(28, 1, 0.7), k_cmt)
L.note("第一季", "完", "最想用哪一讲？", "从这里开始")


def card_xy(i, cx=cx, cy=cy):
    return cx - 400 + (i % 5) * 200, cy - 380 + (i // 5) * 220


def cards20(c, kk, T, cx=cx, cy=cy):
    hop0 = tb(20, k_hop)
    for i in range(10):
        sc = pop_scale(T - tb(20, k_cards[i]) - (i % 2) * 0.27)
        if sc <= 0:
            continue
        x, y = card_xy(i)
        lit = i == 0 and T >= tb(20, k_one)
        g = 1 + 0.18 * pop_scale(T - tb(20, k_one)) if lit else 1.0
        hop = 0.0
        if hop0 <= T < hop0 + 2.0:
            idx = int((T - hop0) / 0.25) % 10
            if idx == i:
                hop = -24
        with K.at(c, x, y + hop, 0, sc * g):
            box(c, 0, 0, 180, 190, RED_FILL if lit else "#FFFFFF", RED if lit else BLACK, 8 if lit else 6, 16)
            K.rr(c, 0, -55, 90, 50, 25, RED if lit or i == 9 else GRAY)
            K.text(c, f"{i + 1:02d}", 0, -54, 34, "black", "#FFFFFF")
            nm = CONCEPTS[i]
            K.text(c, nm, 0, 30, 50 if len(nm) <= 2 else (42 if len(nm) == 3 else 38), "hand", RED if lit else BLACK)
    return None


L.note(*[f"{i + 1:02d}" for i in range(10)])
b.custom(j, 0, 0.3, cards20)
for k_ in sorted(set(k_cards)):
    b.hit(j, k_, "wood_high" if k_ % 2 else "pop", 0.55, "十讲卡片依次出现")
ev(j, k_end, L.stamp("第一季 完", cx + 220, cy + 30, 64, j, k_end, rot=-6), "kick", 0.85)
b.hit(j, k_hop, "shaker", 0.6, "卡片挨个跳一下")


def cmt20(c, kk, T, cx=cx, cy=cy):
    t0 = tb(20, k_cmt)
    sc = pop_scale(T - t0)
    if sc <= 0:
        return None
    x, y = cx + 80, cy + 330
    with K.at(c, x, y, 0, sc):
        bubble_box(c, 0, 0, 760, 230, -1)
        K.text(c, "最想用哪一讲？", 0, -40, 66, "hand", RED)
        f = clamp01((T - t0 - 0.3) / 0.8)
        C.line(c, (-280, 50), (-280 + 420 * f, 50), GRAY, 8)
        if f < 1 and int(T * 4) % 2 == 0:
            C.line(c, (-280 + 420 * f + 12, 26), (-280 + 420 * f + 12, 74), BLUE, 6)
    return None


ev(j, k_cmt, cmt20, "pop", 0.75)


def one20(c, kk, T, cx=cx, cy=cy):
    t0 = tb(20, k_one)
    if T < t0:
        return None
    x, y = card_xy(0)
    g = pop_scale(T - t0)
    sparkle(c, x, y, T - t0, YELLOW, 10, 110, 190)
    with K.at(c, x + 30, y - 175, 0, g):
        K.text(c, "从这里开始", 0, 0, 52, "hand", RED)
    return None


ev(j, k_one, one20, "ding", 0.85)


def li20(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(20, k_cmt))
    if sc <= 0:
        return None
    x, y, s = cx - 420, cy + 560, 0.55
    hx, hy = head_of(x, y, s)
    wave = math.sin(T * 8) * 30
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, s, "smile", rh=(x + 80 * s + wave * s, hy - 60 * s))
    return None


b.custom(j, k_cmt, k_cmt + 0.3, li20)

# ================================================================ 收尾
L.finish(cover_shot=1, square_shot=10, notes=NOTES)
L.export(globals())
