"""《梦的解析》09 典型的梦：为什么总梦见没穿衣服、从高处掉下来？（白板手绘 + AI 旁白，竖屏 2:3）

经典问答：先摆出三种人人都做过的梦（没穿鞋、踩空往下掉、会飞），再一个个问“书里怎么说”。
- 开场：楼顶边缘、小李一脚踩空、往下掉的速度线，配音“一脚踩空”逐字砸下；
- 痛点：梦里公司走廊，小李只穿袜子、拿文件夹挡着，急得冒汗；同事背过身，没反应；
- 身边的例子（drop 在第 2 屏）：梦里从楼顶踩空往下掉 → 床上的小李猛地一抽；会飞、越飞越高；
- 书中：弗洛伊德与“典型的梦”；没穿衣服的梦——别人不在乎，只有自己臊得慌，像小时候满屋跑；皇帝的新装；
  飞和掉连着小时候被大人举高、抛起来、假装松手的游戏；同样的梦，每个人连着的事各不相同；
- 现在怎么看：最近的压力、怕出丑；那一下踩空多半是刚睡着时身体抽了一下；
- 三步：看场合（公司 / 学校 / 家）、看旁人（同事都在看自己的手机）、提前准备（发言稿多读两遍）；梦变成演练；评论区与下一讲。
文案与出处见 mengjie/PLAN.md「### 09」。小李为虚构人物，例子是示意。
"""

import math

import skia

from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from fengtian.common import BLACK, BLUE, GREEN, ORANGE, RED, YELLOW, draw_boss, draw_li, pop_scale
from mengjie import art as A
from mengjie.art import (GRAY, NIGHT, NOTE_FILL, PAPER_W, WOOD, at_pop, bed, box, draw_freud, dream_cloud, moon,
                         sleeper, sparkle, star)
from whiteboard import engine as wb
from whiteboard.engine import P, check, cross

BLUSH = "#F6A5A0"
RED_FILL = "#F6C3BE"


# ---------------------------------------------------------------- 本讲画面元件

def socks(c, x, y, s, alpha=1.0):
    """只穿袜子的两只脚：(x, y) 为人物脚底中心。"""
    for sg in (-1, 1):
        fx = x + sg * 55 * s
        r = skia.Rect.MakeXYWH(fx - 30 * s + sg * 10 * s, y - 16 * s, 60 * s, 32 * s)
        c.drawRoundRect(r, 14 * s, 14 * s, K.paint(PAPER_W, alpha))
        c.drawRoundRect(r, 14 * s, 14 * s, wb.marker(BLUE, 5, alpha))
        C.line(c, (fx - 18 * s + sg * 10 * s, y - 2 * s), (fx + 18 * s + sg * 10 * s, y - 2 * s), RED, 4, alpha)


def blush(c, hx, hy, s, alpha=1.0):
    for sg in (-1, 1):
        c.drawOval(skia.Rect.MakeXYWH(hx + sg * 26 * s - 13 * s, hy + 8 * s, 26 * s, 14 * s), K.paint(BLUSH, alpha))


def li_hide(c, x, y, s, T=0.0, folder=True, sweat=False, t0=0.0, red=False):
    """小李只穿袜子、拿蓝色文件夹挡在身前；sweat=True 时头边冒汗。(x, y) 为脚底。"""
    hy = y - 290 * s
    if folder:
        draw_li(c, x, y, s, "sad", lh=(x - 70 * s, y - 160 * s), rh=(x + 70 * s, y - 160 * s))
    else:
        draw_li(c, x, y, s, "flat")
    socks(c, x, y, s)
    if folder:
        with K.at(c, x, y - 150 * s, -4):
            box(c, 0, 0, 170 * s, 170 * s, "#CFE0F5", BLUE, 6, 10)
            C.line(c, (-60 * s, -50 * s), (60 * s, -50 * s), BLUE, 4)
    if red:
        blush(c, x, hy, s)
    if sweat and T >= t0:
        for n in range(2):
            ph = ((T - t0) * 1.3 + n * 0.5) % 1.0
            A._sweat(c, x + (-75 if n else 75) * s, hy - 30 * s + ph * 70 * s, s, 1 - ph)


def corridor(c, cx, gy, w=1100, alpha=1.0):
    """公司走廊：地面线 + 两扇门 + 墙上一条腰线。gy 为地面。"""
    C.line(c, (cx - w / 2, gy), (cx + w / 2, gy), BLACK, 7, alpha)
    C.line(c, (cx - w / 2, gy - 520), (cx + w / 2, gy - 520), GRAY, 5, alpha)
    for dx in (-w / 2 + 110, w / 2 - 110):
        c.drawRect(skia.Rect.MakeXYWH(cx + dx - 80, gy - 400, 160, 400), K.paint("#F1E3CB", alpha))
        c.drawRect(skia.Rect.MakeXYWH(cx + dx - 80, gy - 400, 160, 400), wb.marker("#A9773E", 7, alpha))
        c.drawCircle(cx + dx + 50 * (1 if dx < 0 else -1), gy - 200, 9, K.paint("#A9773E", alpha))


def toddler(c, x, y, s, mood="smile", arms_up=True, alpha=1.0):
    """小娃娃：大头、短身子、尿布。(x, y) 为脚底。"""
    hy = y - 200 * s
    for sg in (-1, 1):
        C.line(c, (x, y - 70 * s), (x + sg * 30 * s, y), BLACK, 9, alpha)
        hand = (x + sg * 70 * s, hy + (10 if arms_up else 120) * s)
        C.line(c, (x, hy + 70 * s), hand, BLACK, 9, alpha)
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 34 * s, hy + 50 * s, 68 * s, 70 * s), 20 * s, 20 * s, K.paint(PAPER_W, alpha))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 34 * s, hy + 50 * s, 68 * s, 70 * s), 20 * s, 20 * s, wb.marker(BLACK, 6, alpha))
    diaper = P((x - 36 * s, hy + 100 * s), (x + 36 * s, hy + 100 * s), (x + 20 * s, hy + 140 * s), (x - 20 * s, hy + 140 * s),
               close=True)
    c.drawPath(diaper, K.paint("#CFE0F5", alpha))
    c.drawPath(diaper, wb.marker(BLUE, 5, alpha))
    c.drawCircle(x, hy, 52 * s, K.paint(PAPER_W, alpha))
    c.drawCircle(x, hy, 52 * s, wb.marker(BLACK, 8, alpha))
    c.drawPath(P((x - 6 * s, hy - 52 * s), (x + 4 * s, hy - 70 * s), (x + 10 * s, hy - 50 * s)), wb.marker(BLACK, 5, alpha))
    for dx in (-17, 17):
        c.drawCircle(x + dx * s, hy - 4 * s, 5 * s, K.paint(BLACK, alpha))
    m = skia.Path()
    if mood == "smile":
        m.addArc(skia.Rect.MakeXYWH(x - 16 * s, hy + 6 * s, 32 * s, 24 * s), 20, 140)
    else:
        m.addCircle(x, hy + 22 * s, 8 * s)
    c.drawPath(m, wb.marker(BLACK, 5, alpha))
    blush(c, x, hy, s * 0.9, alpha)


def crown(c, x, y, w=90, alpha=1.0):
    """王冠：(x, y) 为底边中心。"""
    p = P((x - w / 2, y), (x - w / 2, y - w * 0.55), (x - w / 4, y - w * 0.25), (x, y - w * 0.65), (x + w / 4, y - w * 0.25),
          (x + w / 2, y - w * 0.55), (x + w / 2, y), close=True)
    c.drawPath(p, K.paint("#FFD27A", alpha))
    c.drawPath(p, wb.marker(ORANGE, 6, alpha))


def building(c, x, y, w, h, alpha=1.0):
    """楼：(x, y) 为楼底中心。"""
    box(c, x, y - h / 2, w, h, "#DCE6F2", BLUE, 6, 6, alpha)
    for r in range(int(h // 70)):
        for q in range(max(1, int(w // 70))):
            wx = x - w / 2 + 35 + q * 70 + (w - 70 * max(1, int(w // 70))) / 2
            c.drawRect(skia.Rect.MakeXYWH(wx - 14, y - h + 30 + r * 70, 28, 34), K.paint(PAPER_W, alpha))


def falling_li(c, x, y, s, rot, T):
    """往下掉的小李：手脚乱划，头顶上方三条速度线。"""
    ph = math.sin(T * 18)
    with K.at(c, x, y, rot):
        hy = -290 * s
        draw_li(c, 0, 0, s, "o", lh=(-90 * s, hy + 20 * s + ph * 20 * s), rh=(90 * s, hy + 20 * s - ph * 20 * s))
    for i in range(3):
        C.line(c, (x - 50 + i * 50, y - 330 * s - 40), (x - 50 + i * 50, y - 330 * s - 120), GRAY, 5)


def flyer(c, x, y, s, T):
    """飞着的小李：身体横过来，双手向前，脚后跟有风线。(x, y) 为身体中心。"""
    with K.at(c, x, y, -80):
        draw_li(c, 0, 150 * s, s, "smile", lh=(-30 * s, -250 * s), rh=(30 * s, -250 * s))
    for i in range(3):
        ph = (T * 1.5 + i / 3) % 1
        C.line(c, (x - 200 * s - ph * 60, y - 20 + i * 30), (x - 260 * s - ph * 60, y - 20 + i * 30), GRAY, 5, 1 - ph)


def phone_hold(c, x, y, s):
    """低头看手机的同事：右手举着手机到脸前。"""
    hy = y - 290 * s
    draw_li(c, x, y, s, "flat", rh=(x + 50 * s, hy + 70 * s))
    box(c, x + 52 * s, hy + 50 * s, 40 * s, 66 * s, "#2E2A28", BLACK, 4, 8)


# ---------------------------------------------------------------- 开场

def _hook(H, j, cx, cy, acc):
    """开场：楼顶边缘 → 小李一脚踩空 → 往下掉的速度线；随后“一脚踩空”逐字砸下。"""
    b = H.b

    def roof(c, kk, T):
        sc = pop_scale(T - H.tb(j, 0))
        if sc > 0:
            with at_pop(c, cx - 250, cy + 100, sc):
                building(c, cx - 300, cy + 110, 300, 420)
        return None
    b.custom(j, 0, 0.3, roof, sfx="wood_low", gain=0.7)

    def step(c, kk, T):
        dt = T - H.tb(j, 1)
        if dt < 0:
            return None
        drop = 0.0 if T < H.tb(j, 2) else ease_in_out(clamp01((T - H.tb(j, 2)) / 0.5))
        x, y = cx - 80 + 120 * drop, cy - 310 + 340 * drop
        with at_pop(c, x, y, pop_scale(dt)):
            if drop <= 0:
                hy = y - 290 * 0.8
                draw_li(c, x, y, 0.8, "o", lh=(x - 90, hy + 40), rh=(x + 90, hy + 40))
            else:
                falling_li(c, x, y - 120, 0.8, 20 * drop, T)
        return None
    b.custom(j, 1, 1.3, step, sfx="tom", gain=0.75)

    def whoosh(c, kk, T):
        dt = T - H.tb(j, 2)
        if dt < 0:
            return None
        a = clamp01(dt / 0.2)
        for i in range(4):
            C.line(c, (cx + 160 + i * 70, cy - 470 + i * 30), (cx + 160 + i * 70, cy - 230 + i * 30), GRAY, 7, a)
        K.text(c, "!", cx + 280, cy - 560, 110, "hand", RED, a)
        return None
    H.note("!")
    b.custom(j, 2, 2.3, whoosh, sfx="ding", gain=0.75)
    A.finish_hook(H, j, cx, cy, acc)


L, R, Z = A.setup("09", _hook)
b = L.b
KT = A.Kit(L)
tb, wt, nx, kq, cap, ev, pop_fn = KT.tb, KT.wt, KT.nx, KT.kq, KT.cap, KT.ev, KT.pop_fn

NOTES = [
    "书目：Sigmund Freud, Die Traumdeutung（1899；中译本《梦的解析》）第五章 D“典型的梦”。",
    "书中说法：没穿衣服的尴尬梦里旁人无动于衷；这类梦连着童年不害臊的光身时期，并提到安徒生《皇帝的新装》；"
    "飞和坠落的梦连着童年被大人举高、抛起的游戏。",
    "入睡抽动（刚睡着时身体抽一下）是今天的生理解释；现在的研究不按固定意思解读这类梦。小李为虚构人物，例子均为示意。",
]

# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])

# ================================================================ 屏 1：梦里公司走廊，小李只穿袜子、文件夹挡着；同事没反应
cx, cy = R[1]
j = L.scene(1, (cx, cy + 10, Z))
GY1 = cy + 420
X1 = cx - 220
k_cor1 = 0
k_li1 = nx(j, wt(0, 0, 0.7), k_cor1)
k_sock1 = nx(j, wt(0, 1, 0.5), k_li1)
k_hide1 = nx(j, wt(0, 2, 0.4), k_sock1)
k_col1 = nx(j, wt(1, 1, 0.2), k_hide1)
k_no1 = nx(j, wt(1, 1, 0.8), k_col1)
L.note("梦里", "没穿鞋", "没反应")


def cor1(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(1, k_cor1))
    if sc <= 0:
        return None
    with at_pop(c, cx, GY1, sc):
        corridor(c, cx, GY1)
        dream_cloud(c, cx - 380, cy - 420, 230, 120, 1.0)
        K.text(c, "梦里", cx - 380, cy - 418, 50, "hand", NIGHT)
    return None


ev(j, k_cor1, cor1, "wood_low", 0.7)


def li1(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(1, k_li1))
    if sc <= 0:
        return None
    hide = T >= tb(1, k_hide1)
    with at_pop(c, X1, GY1, sc):
        li_hide(c, X1, GY1, 0.9, T, folder=hide, sweat=hide, t0=tb(1, k_hide1), red=hide)
    return None


ev(j, k_li1, li1, "pop", 0.7)


def sock1(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(1, k_sock1))
    if sc <= 0:
        return None
    with at_pop(c, X1, GY1, sc):
        c.drawOval(skia.Rect.MakeXYWH(X1 - 130, GY1 - 50, 260, 90), wb.marker(RED, 7))
    with K.at(c, X1 - 50, GY1 - 650, -6, C.slam_scale(T - tb(1, k_sock1))):
        box(c, 0, 0, 260, 100, PAPER_W, RED, 7, 14)
        K.text(c, "没穿鞋", 0, 2, 64, "hand", RED)
    return None


ev(j, k_sock1, sock1, "rim", 0.8)
b.hit(j, k_hide1, "pop", 0.7, "文件夹挡住")


def col1(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(1, k_col1))
    if sc <= 0:
        return None
    with at_pop(c, cx + 300, GY1, sc):
        draw_li(c, cx + 200, GY1, 0.75, back=True)
        phone_hold(c, cx + 400, GY1, 0.75)
    return None


ev(j, k_col1, col1, "wood_high", 0.7)


def no1(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(1, k_no1))
    if sc <= 0:
        return None
    with K.at(c, cx + 300, cy - 30, 0, sc):
        box(c, 0, 0, 280, 100, PAPER_W, GRAY, 5, 40)
        K.text(c, "没反应", 0, 2, 58, "hand", GRAY)
        for i in range(3):
            c.drawCircle(-40 + i * 40, 90, 9, K.paint(GRAY))
    return None


ev(j, k_no1, no1, "ding", 0.7)

# ================================================================ 屏 2：drop——梦里从楼顶踩空往下掉，床上的小李猛地一抽
cx, cy = R[2]
j = L.scene(2, (cx, cy + 10, Z))
KD = L.drop_k()
b.shots[j].shake, b.shots[j].flashes = [(KD, 16.0)], [(KD, 0.45)]
k_bed2 = 0
k_cl2 = max(1, min(kq(j, wt(2, 1, 0.5), 1), KD - 2))
k_step2 = max(k_cl2 + 1, min(kq(j, wt(3, 0, 0.4), k_cl2 + 1), KD - 1))
k_up2 = nx(j, wt(3, 3, 0.4), KD)
BED2 = (cx - 400, cy + 380)
HIP2 = (BED2[0] + 230, BED2[1] - 20)
CL2 = (cx + 90, cy - 250)
L.note("猛地一抽", "醒了")


def bed2(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(2, k_bed2))
    if sc <= 0:
        return None
    with at_pop(c, cx, BED2[1], sc):
        bed(c, *BED2, 560)
        sleeper(c, *HIP2, 0.8, T, tb(2, KD), "o" if T >= tb(2, KD) else "flat", sweat=True)
    return None


ev(j, k_bed2, bed2, "wood_low", 0.7)


def cloud2(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(2, k_cl2))
    if not dream_cloud(c, CL2[0], CL2[1], 860, 600, sc, tail_to=(HIP2[0] - 280, HIP2[1] - 90)):
        return None
    with at_pop(c, CL2[0], CL2[1], sc):
        bx, by = CL2[0] - 200, CL2[1] + 230
        building(c, bx, by, 220, 330)
        roof_y = by - 330
        if T < tb(2, k_step2):
            draw_li(c, bx + 40, roof_y, 0.5, "flat")
        else:
            f = ease_in_out(clamp01((T - tb(2, k_step2)) / max(0.3, tb(2, KD) - tb(2, k_step2))))
            x = lerp(bx + 140, CL2[0] + 200, f)
            y = lerp(roof_y + 20, CL2[1] + 230, f)
            falling_li(c, x, y, 0.5, 30 * f, T)
    return None


ev(j, k_cl2, cloud2, "pop", 0.7)
b.hit(j, k_step2, "tom", 0.75, "一脚踩空")
ev(j, KD, L.slam_text("猛地一抽", cx + 230, cy + 160, 120, RED, j, KD, rot=-6), "kick", 0.95)
ev(j, k_up2, L.pop_text("醒了", cx + 320, cy + 330, 80, NIGHT, j, k_up2), "wood_high", 0.7)

# ================================================================ 屏 3：也有人梦见会飞，越飞越高
cx, cy = R[3]
j = L.scene(3, (cx, cy + 10, Z))
k_bed3 = 0
k_cl3 = nx(j, wt(4, 0, 0.5), k_bed3)
k_go3 = nx(j, wt(4, 1, 0.1), k_cl3)
k_hi3 = nx(j, wt(4, 1, 0.8), k_go3)
BED3 = (cx - 400, cy + 380)
HIP3 = (BED3[0] + 230, BED3[1] - 20)
CL3 = (cx + 80, cy - 230)
L.note("越飞越高")


def bed3(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(3, k_bed3))
    if sc <= 0:
        return None
    with at_pop(c, cx, BED3[1], sc):
        bed(c, *BED3, 560)
        sleeper(c, *HIP3, 0.8, T, None, "smile")
        moon(c, cx - 450, cy + 120, 50)
    return None


ev(j, k_bed3, bed3, "wood_low", 0.7)


def cloud3(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(3, k_cl3))
    if not dream_cloud(c, CL3[0], CL3[1], 860, 620, sc, tail_to=(HIP3[0] - 280, HIP3[1] - 90)):
        return None
    with at_pop(c, CL3[0], CL3[1], sc):
        base = CL3[1] + 250
        for i, (dx, h) in enumerate(((-260, 150), (-130, 220), (20, 120), (150, 190), (270, 140))):
            building(c, CL3[0] + dx, base, 100, h)
        up = ease_out(clamp01((T - tb(3, k_go3)) / 1.6)) if T >= tb(3, k_go3) else 0.0
        fx, fy = CL3[0] - 160 + 220 * up, CL3[1] + 60 - 130 * up
        flyer(c, fx, fy, 0.45, T)
        if up > 0:
            for i in range(2):
                bx_ = CL3[0] + 200 + i * 90
                by_ = CL3[1] - 10 + i * 40
                c.drawPath(P((bx_ - 18, by_), (bx_, by_ + 12), (bx_ + 18, by_)), wb.marker(BLACK, 4, up))
    return None


ev(j, k_cl3, cloud3, "pop", 0.7)
b.hit(j, k_go3, "shaker", 0.7, "飞起来")
ev(j, k_hi3, L.slam_text("越飞越高", cx + 250, cy + 170, 110, BLUE, j, k_hi3, rot=-5), "kick", 0.85)
b.shots[j].shake = [(k_hi3, 7.0)]

# ================================================================ 屏 4：弗洛伊德与书；“典型的梦”：好多人做，内容差不多
cx, cy = R[4]
j = L.scene(4, (cx, cy + 10, Z))
k_fr4 = kq(j, wt(5, 0, 0.2), 0)
k_bk4 = nx(j, wt(5, 0, 0.5), k_fr4)
k_st4 = nx(j, wt(5, 0, 0.7), k_bk4)
k_crowd4 = nx(j, wt(5, 0, 0.95), k_st4)
k_same4 = nx(j, wt(5, 1, 0.6), k_crowd4)
L.note("梦的解析", "典型的梦", "好多人做", "内容差不多")


def fr4(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx - 360, cy + 40, sc):
        draw_freud(c, cx - 360, cy + 40, 0.85, "smile")
    return None


ev(j, k_fr4, pop_fn(j, k_fr4, fr4), "wood_low", 0.7)


def bk4(c, kk, T, cx=cx, cy=cy):
    sc = C.slam_scale(T - tb(4, k_bk4))
    if sc <= 0:
        return None
    with K.at(c, cx - 140, cy - 330, 6, sc):
        box(c, 0, 0, 200, 270, NIGHT, BLACK, 6, 10)
        K.text(c, "梦的", 0, -50, 50, "serif_black", "#FFE39A")
        K.text(c, "解析", 0, 14, 50, "serif_black", "#FFE39A")
        moon(c, 0, 90, 26)
    return None


ev(j, k_bk4, bk4, "ding", 0.75)
ev(j, k_st4, L.stamp("典型的梦", cx + 270, cy - 360, 84, j, k_st4, color=RED, rot=-5), "kick", 0.9)
b.shots[j].shake = [(k_st4, 7.0)]
ICONS4 = ("sock", "fall", "fly", "fall")


def mini_icon(c, kind, x, y, r=1.0, T=0.0):
    if kind == "sock":
        socks(c, x, y + 20 * r, 0.6 * r)
    elif kind == "fall":
        c.drawPath(wb.arrow((x, y - 34 * r), (x, y + 34 * r), 0.0, 22 * r), wb.marker(RED, 6))
    else:
        c.drawPath(wb.arrow((x - 30 * r, y + 26 * r), (x + 30 * r, y - 26 * r), 0.0, 22 * r), wb.marker(BLUE, 6))


def crowd4(c, kk, T, cx=cx, cy=cy):
    gy = cy + 470
    for i, x in enumerate((cx - 130, cx + 60, cx + 250, cx + 440)):
        g = pop_scale(T - tb(4, k_crowd4) - i * 0.12)
        if g <= 0:
            continue
        with at_pop(c, x, gy, g):
            draw_li(c, x, gy, 0.55, "o" if i % 2 else "flat")
            dream_cloud(c, x, gy - 270, 160, 110, 1.0)
            same = T >= tb(4, k_same4)
            mini_icon(c, ICONS4[0] if not same else ICONS4[1], x, gy - 270, 1.0, T)
    if T >= tb(4, k_crowd4):
        g = pop_scale(T - tb(4, k_crowd4))
        with K.at(c, cx + 160, cy - 150, 0, g):
            K.text(c, "好多人做", 0, 0, 72, "hand", BLACK)
    return None


ev(j, k_crowd4, crowd4, "wood_high", 0.7)
ev(j, k_same4, L.pop_text("内容差不多", cx + 160, cy - 30, 72, ORANGE, j, k_same4), "ding", 0.75)

# ================================================================ 屏 5：没穿衣服的梦——别人不在乎，自己臊得慌；像小时候满屋跑，不害臊
cx, cy = R[5]
j = L.scene(5, (cx, cy + 10, Z))
k_li5 = kq(j, wt(6, 0, 0.4), 0)
k_care5 = nx(j, wt(6, 1, 0.5), k_li5)
k_sao5 = nx(j, wt(6, 2, 0.5), k_care5)
k_kid5 = nx(j, wt(7, 1, 0.4), k_sao5)
k_ok5 = nx(j, wt(7, 3, 0.3), k_kid5)
GY5 = cy - 20
GK5 = cy + 470
L.note("不在乎", "臊得慌", "小时候", "不害臊")


def li5(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx - 360, GY5, sc):
        C.line(c, (cx - 560, GY5), (cx + 560, GY5), BLACK, 6)
        li_hide(c, cx - 360, GY5, 0.8, T, folder=True, sweat=True, t0=tb(5, k_li5), red=T >= tb(5, k_sao5))
    return None


ev(j, k_li5, pop_fn(j, k_li5, li5), "wood_low", 0.7)


def care5(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(5, k_care5))
    if sc <= 0:
        return None
    with at_pop(c, cx + 200, GY5, sc):
        phone_hold(c, cx + 80, GY5, 0.7)
        phone_hold(c, cx + 330, GY5, 0.7)
        K.text(c, "不在乎", cx + 205, GY5 - 300, 56, "hand", GRAY)
    return None


ev(j, k_care5, care5, "pop", 0.7)
ev(j, k_sao5, L.slam_text("臊得慌", cx - 360, cy - 460, 84, RED, j, k_sao5, rot=-6), "rim", 0.85)


def kid5(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(5, k_kid5))
    if sc <= 0:
        return None
    with at_pop(c, cx, GK5, sc):
        C.line(c, (cx - 560, GK5), (cx + 560, GK5), BLACK, 6)
        box(c, cx - 420, GK5 - 300, 170, 110, "#FFF4D6", "#A9773E", 5, 10)
        K.text(c, "小时候", cx - 420, GK5 - 298, 44, "hand", "#A9773E")
        run = ((T - tb(5, k_kid5)) * 0.35) % 1.0
        x = lerp(cx - 200, cx + 380, ease_in_out(abs(run * 2 - 1)))
        hop = -abs(math.sin((T - tb(5, k_kid5)) * 9)) * 18
        toddler(c, x, GK5 + hop, 0.85, "smile")
        for i in range(3):
            C.line(c, (x - 110 - i * 10, GK5 - 140 + i * 30), (x - 160 - i * 10, GK5 - 140 + i * 30), GRAY, 5)
    return None


ev(j, k_kid5, kid5, "wood_high", 0.7)


def arrow5(c, kk, T, cx=cx, cy=cy):
    t0 = tb(5, k_kid5)
    if T < t0:
        return None
    f = ease_out(clamp01((T - t0) / 0.4))
    a, z = (cx - 360, cy + 60), (cx - 420, cy + 130)
    c.drawPath(wb.arrow(a, (lerp(a[0], z[0], f), lerp(a[1], z[1], f)), 0.0, 26), wb.marker(GRAY, 6))
    return None


b.custom(j, k_kid5, k_kid5 + 0.3, arrow5)
ev(j, k_ok5, L.stamp("不害臊", cx + 330, cy + 180, 64, j, k_ok5, color=GREEN, rot=6), "ding", 0.8)

# ================================================================ 屏 6：皇帝的新装——大家都看见了，都装作没看见
cx, cy = R[6]
j = L.scene(6, (cx, cy + 10, Z))
k_bk6 = kq(j, wt(8, 0, 0.3), 0)
k_emp6 = nx(j, wt(8, 0, 0.6), k_bk6)
k_crowd6 = nx(j, wt(8, 0, 0.9), k_emp6)
k_st6 = nx(j, wt(8, 1, 0.6), k_crowd6)
GY6 = cy + 440
L.note("皇帝的新装", "没看见")


def bk6(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, cy - 440, sc):
        with K.at(c, cx, cy - 440, -2):
            box(c, 0, 0, 640, 140, "#FFF4D6", ORANGE, 8, 16)
            K.text(c, "皇帝的新装", 0, 4, 80, "hand", ORANGE)
    return None


ev(j, k_bk6, pop_fn(j, k_bk6, bk6), "wood_low", 0.7)


def emp6(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(6, k_emp6))
    if sc <= 0:
        return None
    dt = T - tb(6, k_emp6)
    x = cx - 40 + 30 * math.sin(dt * 1.2)
    bob = -abs(math.sin(dt * 4)) * 10
    s = 1.0
    with at_pop(c, x, GY6, sc):
        hy = GY6 + bob - 290 * s
        robe = P((x - 120, hy + 60), (x + 120, hy + 60), (x + 150, GY6 - 30), (x - 150, GY6 - 30), close=True)
        dash = wb.marker(GRAY, 5, 0.8)
        dash.setPathEffect(skia.DashPathEffect.Make([18, 16], 0))
        c.drawPath(robe, dash)
        draw_li(c, x, GY6 + bob, s, "smile", lh=(x - 80, hy + 170), rh=(x + 80, hy + 170))
        crown(c, x, hy - 40, 100)
    return None


ev(j, k_emp6, emp6, "tom", 0.75)


def watcher(c, x, y, s, side, T):
    """围观的人：背过身去，头顶三个点。"""
    hy = y - 290 * s
    draw_li(c, x, y, s, back=True)
    for i in range(3):
        c.drawCircle(x - 24 * s + i * 24 * s, hy - 80 * s, 6 * s, K.paint(GRAY))


def crowd6(c, kk, T, cx=cx, cy=cy):
    for i, (x, sd) in enumerate(((cx - 440, 1), (cx - 290, 1), (cx + 250, -1), (cx + 410, -1))):
        g = pop_scale(T - tb(6, k_crowd6) - i * 0.1)
        if g <= 0:
            continue
        with at_pop(c, x, GY6, g):
            watcher(c, x, GY6, 0.7, sd, T)
    return None


ev(j, k_crowd6, crowd6, "pop", 0.7)
ev(j, k_st6, L.stamp("装作没看见", cx, cy - 230, 76, j, k_st6, color=RED, rot=-4), "kick", 0.9)
L.note("装作没看见")
b.shots[j].shake = [(k_st6, 7.0)]

# ================================================================ 屏 7：飞和掉——大人把你举高、抛起来、假装松手；又怕又爱，长大又找上门
cx, cy = R[7]
j = L.scene(7, (cx, cy + 10, Z))
k_dad7 = kq(j, wt(9, 0, 0.4), 0)
k_l7 = [nx(j, wt(9, 1, 0.25), k_dad7)]
k_l7.append(nx(j, wt(9, 1, 0.55), k_l7[0]))
k_l7.append(nx(j, wt(9, 1, 0.85), k_l7[1]))
k_love7 = nx(j, wt(10, 0, 0.5), k_l7[2])
k_grow7 = nx(j, wt(10, 2, 0.3), k_love7)
LAB7 = ["举高", "抛起来", "假装松手"]
GY7 = cy + 450
DX7 = cx - 280
L.note(*LAB7, "又怕又爱", "长大以后")


def dad7(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(7, k_dad7))
    if sc <= 0:
        return None
    s = 0.95
    hy = GY7 - 290 * s
    t1, t2 = tb(7, k_l7[1]), tb(7, k_l7[2])
    if T < t1:
        ky = hy - 40
    else:
        ph = ((T - t1) * 1.1) % 1.0
        ky = hy - 40 - 300 * math.sin(math.pi * ph)
    hands_y = min(hy - 30, ky + 60) if T < t2 else min(hy - 30, ky + 120)
    with at_pop(c, DX7, GY7, sc):
        C.line(c, (cx - 560, GY7), (cx + 100, GY7), BLACK, 6)
        draw_li(c, DX7, GY7, s, "smile", lh=(DX7 - 60, hands_y), rh=(DX7 + 60, hands_y))
        toddler(c, DX7, ky + 30, 0.6, "o" if T >= t2 and math.sin(math.pi * (((T - t1) * 1.1) % 1.0)) > 0.6 else "smile")
        if T >= t1:
            arc = skia.Path()
            arc.addArc(skia.Rect.MakeXYWH(DX7 - 180, hy - 420, 360, 300), 200, 140)
            c.drawPath(arc, wb.marker(GRAY, 5, 0.8))
    return None


ev(j, k_dad7, dad7, "wood_low", 0.7)


def labels7(c, kk, T, cx=cx, cy=cy):
    for i, s_ in enumerate(LAB7):
        g = pop_scale(T - tb(7, k_l7[i]))
        if g <= 0:
            continue
        with K.at(c, cx + 270, cy - 430 + i * 130, 0, g):
            box(c, 0, 0, 300, 100, PAPER_W, (BLUE, ORANGE, RED)[i], 6, 40)
            K.text(c, s_, 0, 2, 56, "hand", (BLUE, ORANGE, RED)[i])
    return None


ev(j, k_l7[0], labels7, "pop", 0.7)
b.hit(j, k_l7[1], "tom", 0.75, "抛起来")
b.hit(j, k_l7[2], "rim", 0.8, "假装松手")


def love7(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(7, k_love7))
    if sc <= 0:
        return None
    x, y = cx + 270, cy - 20
    with at_pop(c, x, y, sc):
        c.drawPath(C.heart_path(x - 150, y, 50), K.paint("#F6C3BE"))
        c.drawPath(C.heart_path(x - 150, y, 50), wb.marker(RED, 6))
        K.text(c, "又怕又爱", x + 50, y, 60, "hand", RED)
        A._sweat(c, x - 90, y - 50, 1.0)
    return None


ev(j, k_love7, love7, "ding", 0.75)


def grow7(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(7, k_grow7))
    x, y = cx + 270, cy + 320
    if not dream_cloud(c, x, y, 470, 300, sc):
        return None
    with at_pop(c, x, y, sc):
        building(c, x - 110, y + 110, 110, 200)
        f = ((T - tb(7, k_grow7)) * 0.5) % 1.0
        falling_li(c, x + 60, y - 20 + 90 * f, 0.32, 20, T)
        K.text(c, "长大以后", x, y - 175, 48, "hand", NIGHT)
    return None


ev(j, k_grow7, grow7, "pop", 0.7)

# ================================================================ 屏 8：典型的梦看着一样，每个人连着的事各不相同
cx, cy = R[8]
j = L.scene(8, (cx, cy + 10, Z))
k_cl8 = kq(j, wt(11, 0, 0.5), 0)
k_ln8 = nx(j, wt(11, 1, 0.3), k_cl8)
k_it8 = nx(j, wt(11, 1, 0.8), k_ln8)
k_st8 = nx(j, wt(11, 2, 0.5), k_it8)
XS8 = (cx - 350, cx, cx + 350)
ITEMS8 = ["考试", "汇报", "相亲"]
L.note("看着一样", *ITEMS8, "各不相同")


def cl8(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(8, k_cl8))
    if sc <= 0:
        return None
    K.text(c, "看着一样", cx, cy - 520, 60, "hand", NIGHT, clamp01(sc * 2))
    for x in XS8:
        dream_cloud(c, x, cy - 330, 300, 220, sc)
        with at_pop(c, x, cy - 330, sc):
            building(c, x - 50, cy - 250, 70, 120)
            falling_li(c, x + 50, cy - 270, 0.25, 20, T)
    return None


ev(j, k_cl8, cl8, "pop", 0.75)


def ln8(c, kk, T, cx=cx, cy=cy):
    t0 = tb(8, k_ln8)
    if T < t0:
        return None
    f = ease_out(clamp01((T - t0) / 0.4))
    for x in XS8:
        c.drawPath(wb.arrow((x, cy - 200), (x, lerp(cy - 200, cy - 80, f)), 0.0, 26), wb.marker(GRAY, 6))
    return None


ev(j, k_ln8, ln8, "wood_high", 0.7)


def it8(c, kk, T, cx=cx, cy=cy):
    for i, x in enumerate(XS8):
        g = pop_scale(T - tb(8, k_it8) - i * 0.15)
        if g <= 0:
            continue
        with K.at(c, x, cy + 70, (-4, 3, -2)[i], g):
            box(c, 0, 0, 260, 220, PAPER_W, (RED, BLUE, ORANGE)[i], 6, 14)
            if i == 0:
                A.exam_paper(c, 0, -25, 110, 120, 0, "", None)
            elif i == 1:
                box(c, 0, -20, 160, 100, "#DCE6F2", BLUE, 5, 6)
                c.drawPath(P((-50, 0), (-10, -30), (20, -10), (60, -50)), wb.marker(RED, 5))
            else:
                c.drawPath(C.heart_path(0, -20, 48), K.paint("#F6C3BE"))
                c.drawPath(C.heart_path(0, -20, 48), wb.marker(RED, 5))
            K.text(c, ITEMS8[i], 0, 78, 48, "hand", BLACK)
    return None


ev(j, k_it8, it8, "pop", 0.7)
ev(j, k_st8, L.slam_text("各不相同", cx, cy + 380, 120, L.ACC, j, k_st8, rot=-3), "kick", 0.9)
b.shots[j].shake = [(k_st8, 7.0)]

# ================================================================ 屏 9：现在怎么看——压力、怕出丑；踩空多半是刚睡着时身体抽了一下
cx, cy = R[9]
j = L.scene(9, (cx, cy + 10, Z))
k_br9 = kq(j, wt(12, 0, 0.4), 0)
k_tag9 = nx(j, wt(12, 1, 0.4), k_br9)
k_bed9 = nx(j, wt(13, 0, 0.5), k_tag9)
k_moon9 = nx(j, wt(13, 1, 0.4), k_bed9)
k_jerk9 = nx(j, wt(13, 2, 0.5), k_moon9)
TAGS9 = ["最近的压力", "怕出丑"]
L.note("研究", *TAGS9, "刚睡着", "抽了一下")


def br9(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 300, cy - 330
    with at_pop(c, x, y, sc):
        A.brain(c, x, y, 110)
        K.text(c, "研究", x, y - 160, 54, "hand", BLUE)
    return None


ev(j, k_br9, pop_fn(j, k_br9, br9), "wood_low", 0.7)


def tag9(c, kk, T, cx=cx, cy=cy):
    for i, s_ in enumerate(TAGS9):
        g = pop_scale(T - tb(9, k_tag9) - i * 0.18)
        if g <= 0:
            continue
        x, y = cx + 250, cy - 420 + i * 150
        C.line(c, (cx - 140, cy - 330), (x - 170, y), GRAY, 5, g)
        with K.at(c, x, y, (-3, 3)[i], g):
            box(c, 0, 0, 340, 110, PAPER_W, (ORANGE, RED)[i], 6, 40)
            K.text(c, s_, 0, 2, 54, "hand", (ORANGE, RED)[i])
    return None


ev(j, k_tag9, tag9, "pop", 0.7)
BED9 = (cx - 330, cy + 330)
HIP9 = (BED9[0] + 230, BED9[1] - 20)


def bed9(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, BED9[1], sc):
        bed(c, *BED9, 560)
        t0 = tb(9, k_jerk9)
        jump = 0.0
        if T >= t0:
            jump = -40 * math.exp(-(T - t0) * 6) * abs(math.cos((T - t0) * 18))
        with K.at(c, 0, jump, 0):
            sleeper(c, *HIP9, 0.8, T, None, "o" if T >= t0 else "smile")
        if T >= t0:
            a = 1 - clamp01((T - t0 - 0.6) / 0.6)
            for i in range(3):
                C.line(c, (HIP9[0] - 40 + i * 70, HIP9[1] - 90), (HIP9[0] - 30 + i * 70, HIP9[1] - 140), RED, 6, a)
    return None


ev(j, k_bed9, pop_fn(j, k_bed9, bed9), "wood_high", 0.7)


def moon9(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(9, k_moon9))
    if sc <= 0:
        return None
    x, y = cx + 380, cy + 40
    with at_pop(c, x, y, sc):
        moon(c, x - 40, y, 50)
        box(c, x - 20, y + 120, 240, 90, PAPER_W, NIGHT, 5, 40)
        K.text(c, "刚睡着", x - 20, y + 122, 50, "hand", NIGHT)
    return None


ev(j, k_moon9, moon9, "ding", 0.7)
ev(j, k_jerk9, L.slam_text("抽了一下", cx + 220, cy - 80, 100, RED, j, k_jerk9, rot=-5), "kick", 0.9)
b.shots[j].shake = [(k_jerk9, 8.0)]

# ================================================================ 屏 10：说回我们自己——别急着担心；“三步”
cx, cy = R[10]
j = L.scene(10, (cx, cy + 10, Z))
k_li10 = kq(j, wt(14, 0, 0.5), 0)
k_bb10 = nx(j, wt(14, 1, 0.5), k_li10)
k_3 = nx(j, wt(14, 2, 0.5), k_bb10)
GY10 = cy + 420
L.note("三步")


def li10(c, sc, T, cx=cx, cy=cy):
    x = cx - 220
    with at_pop(c, x, GY10, sc):
        C.line(c, (x - 300, GY10), (x + 300, GY10), BLACK, 7)
        draw_li(c, x, GY10, 0.9, "smile")
        dream_cloud(c, x - 120, cy - 310, 300, 220, 1.0)
        building(c, x - 170, cy - 240, 70, 120)
        falling_li(c, x - 70, cy - 260, 0.25, 20, T)
    return None


ev(j, k_li10, pop_fn(j, k_li10, li10), "wood_low", 0.7)
ev(j, k_bb10, L.pop_bubble("别急着担心", cx - 80, cy - 70, j, k_bb10, 54, GREEN, tail=-1), "pop", 0.7)


def three10(c, kk, T, cx=cx, cy=cy):
    sc = C.slam_scale(T - tb(10, k_3))
    if sc <= 0:
        return None
    with K.at(c, cx + 300, cy - 330, -4, sc):
        c.drawCircle(0, 0, 180, K.paint("#FFF4D6"))
        c.drawCircle(0, 0, 180, wb.marker(L.ACC, 10))
        K.text(c, "三步", 0, 6, 120, "hand", L.ACC)
    return None


ev(j, k_3, three10, "kick", 0.85)
b.shots[j].shake = [(k_3, 7.0)]

# ================================================================ 屏 11：做法一——看场合：公司、学校、还是家
cx, cy = R[11]
j = L.scene(11, (cx, cy + 10, Z))
k_h11 = kq(j, wt(15, 0, 0.3), 0)
k_pl11 = [nx(j, wt(15, 1, 0.6), k_h11)]
k_pl11.append(nx(j, wt(15, 2, 0.4), k_pl11[0]))
k_pl11.append(nx(j, wt(15, 3, 0.5), k_pl11[1]))
PL11 = ["公司", "学校", "家"]
L.note("第一", "看场合", *PL11, "梦里在哪")


def h11(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, cy - 500, sc):
        K.text(c, "第一", cx - 380, cy - 500, 70, "hand", L.ACC)
        K.text(c, "看场合", cx - 120, cy - 500, 60, "hand", BLACK)
    return None


ev(j, k_h11, pop_fn(j, k_h11, h11), "wood_low", 0.6)


def house(c, x, y, w=150, school=False):
    box(c, x, y + 30, w, w * 0.7, "#FFF4D6" if not school else "#F6E0C8", "#A9773E", 6, 6)
    c.drawPath(P((x - w * 0.62, y - w * 0.05), (x, y - w * 0.55), (x + w * 0.62, y - w * 0.05), close=True), K.paint(RED_FILL))
    c.drawPath(P((x - w * 0.62, y - w * 0.05), (x, y - w * 0.55), (x + w * 0.62, y - w * 0.05), close=True), wb.marker(RED, 6))
    c.drawRect(skia.Rect.MakeXYWH(x - 20, y + 20, 40, 60), K.paint("#A9773E"))
    if school:
        C.line(c, (x, y - w * 0.55), (x, y - w * 0.95), BLACK, 5)
        c.drawPath(P((x, y - w * 0.95), (x + 50, y - w * 0.85), (x, y - w * 0.75), close=True), K.paint(RED))


def pl11(c, kk, T, cx=cx, cy=cy):
    for i, s_ in enumerate(PL11):
        g = pop_scale(T - tb(11, k_pl11[i]))
        if g <= 0:
            continue
        x, y = cx - 350 + i * 350, cy - 140
        with K.at(c, x, y, (-3, 2, -2)[i], g):
            box(c, 0, 0, 300, 330, PAPER_W, BLACK, 6, 16)
            if i == 0:
                building(c, 0, 70, 150, 220)
            elif i == 1:
                house(c, 0, 0, 160, True)
            else:
                house(c, 0, 0, 160)
            K.text(c, s_, 0, 125, 52, "hand", BLACK)
    return None


ev(j, k_pl11[0], pl11, "pop", 0.7)
b.hit(j, k_pl11[1], "pop", 0.7, "学校")
b.hit(j, k_pl11[2], "pop", 0.7, "家")


def li11(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(11, k_pl11[0]) - 0.4)
    if sc <= 0:
        return None
    x, gy = cx - 160, cy + 480
    with at_pop(c, x, gy, sc):
        draw_li(c, x, gy, 0.75, "flat", rh=(x + 40, gy - 290 * 0.75 + 40))
        dream_cloud(c, x + 300, gy - 240, 320, 160, 1.0, tail_to=(x + 60, gy - 250))
        K.text(c, "梦里在哪", x + 300, gy - 238, 48, "hand", NIGHT)
    return None


b.custom(j, k_pl11[0], k_pl11[0] + 0.3, li11)

# ================================================================ 屏 12：做法二——看旁人：同事都在看自己的手机，只有你在意
cx, cy = R[12]
j = L.scene(12, (cx, cy + 10, Z))
k_h12 = kq(j, wt(16, 0, 0.3), 0)
k_col12 = nx(j, wt(16, 1, 0.2), k_h12)
k_q12 = nx(j, wt(16, 1, 0.45), k_col12)
k_mag12 = nx(j, wt(16, 1, 0.75), k_q12)
GY12 = cy + 300
L.note("第二", "看旁人", "真在笑你吗", "在看手机")


def h12(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, cy - 500, sc):
        K.text(c, "第二", cx - 380, cy - 500, 70, "hand", L.ACC)
        K.text(c, "看旁人", cx - 120, cy - 500, 60, "hand", BLACK)
        C.line(c, (cx - 560, GY12), (cx + 560, GY12), BLACK, 6)
        li_hide(c, cx - 400, GY12, 0.8, T, folder=True, sweat=False, red=True)
    return None


ev(j, k_h12, pop_fn(j, k_h12, h12), "wood_low", 0.6)


def col12(c, kk, T, cx=cx, cy=cy):
    for i, x in enumerate((cx - 60, cx + 170, cx + 400)):
        g = pop_scale(T - tb(12, k_col12) - i * 0.12)
        if g <= 0:
            continue
        with at_pop(c, x, GY12, g):
            phone_hold(c, x, GY12, 0.72)
    return None


ev(j, k_col12, col12, "wood_high", 0.7)
ev(j, k_q12, L.pop_bubble("真在笑你吗", cx + 50, cy - 300, j, k_q12, 54, BLACK, tail=-1), "pop", 0.7)


def mag12(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(12, k_mag12))
    if sc <= 0:
        return None
    s_ = 0.72
    px, py = cx + 170 + 52 * s_, GY12 - 290 * s_ + 50 * s_
    with K.at(c, px, py, 0, sc):
        C.line(c, (60, 60), (130, 130), "#A9773E", 18)
        c.drawCircle(0, 0, 80, wb.marker(BLACK, 8))
    with K.at(c, cx + 170, GY12 + 120, 0, sc):
        box(c, 0, 0, 300, 90, PAPER_W, GREEN, 6, 40)
        K.text(c, "在看手机", 0, 2, 52, "hand", GREEN)
    return None


ev(j, k_mag12, mag12, "ding", 0.8)

# ================================================================ 屏 13：做法三——找一件怕出丑的事，提前准备：发言稿多读两遍
cx, cy = R[13]
j = L.scene(13, (cx, cy + 10, Z))
k_h13 = kq(j, wt(17, 0, 0.3), 0)
k_cal13 = nx(j, wt(17, 1, 0.5), k_h13)
k_li13 = nx(j, wt(17, 2, 0.3), k_cal13)
k_x13 = nx(j, wt(17, 2, 0.8), k_li13)
GY13 = cy + 450
L.note("第三", "提前准备", "周五", "发言", "发言稿", "多读两遍")


def h13(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, cy - 500, sc):
        K.text(c, "第三", cx - 380, cy - 500, 70, "hand", L.ACC)
        K.text(c, "提前准备", cx - 90, cy - 500, 60, "hand", BLACK)
    return None


ev(j, k_h13, pop_fn(j, k_h13, h13), "wood_low", 0.6)


def cal13(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(13, k_cal13))
    if sc <= 0:
        return None
    with K.at(c, cx + 300, cy - 250, 4, sc):
        box(c, 0, 0, 300, 280, PAPER_W, BLACK, 7, 12)
        c.drawRect(skia.Rect.MakeXYWH(-150, -140, 300, 80), K.paint(RED))
        K.text(c, "周五", 0, -100, 50, "hand", "#FFFFFF")
        K.text(c, "发言", 0, 30, 80, "hand", RED)
    return None


ev(j, k_cal13, cal13, "pop", 0.7)


def li13(c, sc, T, cx=cx, cy=cy):
    x = cx - 200
    with at_pop(c, x, GY13, sc):
        C.line(c, (cx - 560, GY13), (cx + 560, GY13), BLACK, 6)
        hy = GY13 - 290 * 0.95
        draw_li(c, x, GY13, 0.95, "smile", lh=(x + 40, hy + 140), rh=(x + 150, hy + 120))
        with K.at(c, x + 140, hy + 70, 8):
            box(c, 0, 0, 160, 200, PAPER_W, BLACK, 5, 6)
            K.text(c, "发言稿", 0, -60, 34, "hand", BLUE)
            for r in range(3):
                C.line(c, (-55, -10 + r * 36), (55 - r * 15, -10 + r * 36), GRAY, 4)
    return None


ev(j, k_li13, pop_fn(j, k_li13, li13), "wood_high", 0.7)
ev(j, k_x13, L.stamp("多读两遍", cx + 260, cy + 120, 70, j, k_x13, color=GREEN, rot=-5), "kick", 0.85)

# ================================================================ 屏 14：这样看梦——走廊的梦变成一次提前演练
cx, cy = R[14]
j = L.scene(14, (cx, cy + 10, Z))
k_cl14 = 0
k_turn14 = nx(j, wt(18, 1, 0.5), k_cl14)
k_txt14 = nx(j, wt(18, 2, 0.6), k_turn14)
CL14 = (cx, cy - 140)
L.note("提前演练", "加油")


def cl14(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(14, k_cl14))
    if not dream_cloud(c, CL14[0], CL14[1], 900, 700, sc):
        return None
    m = ease_in_out(clamp01((T - tb(14, k_turn14)) / 0.45)) if T >= tb(14, k_turn14) else 0.0
    gy = CL14[1] + 230
    with at_pop(c, CL14[0], CL14[1], sc):
        if m < 1:
            li_hide(c, CL14[0], gy, 0.75, T, folder=True, red=True)
            C.line(c, (CL14[0] - 300, gy), (CL14[0] + 300, gy), BLACK, 6, 1 - m)
        if m > 0:
            c.drawPath(P((CL14[0] - 60, CL14[1] - 260), (CL14[0] - 230, gy), (CL14[0] + 230, gy), (CL14[0] + 60, CL14[1] - 260),
                         close=True), K.paint("#FFF1A8", 0.7 * m))
            c.drawRect(skia.Rect.MakeXYWH(CL14[0] - 330, gy, 660, 50), K.paint(WOOD, m))
            c.drawRect(skia.Rect.MakeXYWH(CL14[0] - 330, gy, 660, 50), wb.marker("#A9773E", 6, m))
            with at_pop(c, CL14[0], gy, m):
                hy = gy - 290 * 0.75
                draw_li(c, CL14[0], gy, 0.75, "smile", rh=(CL14[0] + 110, hy - 20))
    if m > 0:
        sparkle(c, CL14[0], CL14[1] - 120, T - tb(14, k_turn14), YELLOW, 10, 150, 260)
    return None


ev(j, k_cl14, cl14, "pop", 0.7)
b.hit(j, k_turn14, "clap", 0.8, "走廊变舞台")
ev(j, k_txt14, L.slam_text("提前演练", cx, cy + 380, 130, L.ACC, j, k_txt14, rot=-3), "kick", 0.9)
b.shots[j].shake = [(k_txt14, 7.0)]

# ================================================================ 屏 15：评论区——“梦里一脚踩空”；同事都在看自己的事，放轻松；下一讲预告
cx, cy = R[15]
j = L.scene(15, (cx, cy + 10, Z))
k_box15 = kq(j, wt(19, 0, 0.4), 0)
k_type15 = nx(j, wt(20, 0, 0.5), k_box15)
k_likes15 = nx(j, wt(20, 1, 0.5), k_type15)
k_relax15 = nx(j, wt(21, 1, 0.5), k_likes15)
k_n = nx(j, wt(22, 0, 0.1), k_relax15)
L.note("评论区", "梦里一脚踩空", "发送", "+1", "放轻松")


def input15(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(15, k_box15))
    if sc <= 0:
        return None
    x, y, w = cx, cy - 420, 860
    with at_pop(c, x, y, sc):
        box(c, x, y, w, 150, PAPER_W, BLACK, 6, 30)
        K.text(c, "评论区", x - w / 2 + 90, y - 110, 44, "sans_medium", GRAY)
        if T >= tb(15, k_type15):
            s_ = "梦里一脚踩空"
            g = clamp01((T - tb(15, k_type15)) / 0.8)
            n = max(1, int(math.ceil(len(s_) * g)))
            K.text(c, s_[:n], x - w / 2 + 40, y + 2, 58, "hand", BLACK, 1.0, "left")
        K.rr(c, x + w / 2 - 85, y, 130, 80, 20, L.ACC)
        K.text(c, "发送", x + w / 2 - 85, y, 42, "sans_medium", "#FFFFFF")
        for i in range(6):
            g = pop_scale(T - tb(15, k_likes15) - i * 0.15)
            if g > 0:
                with K.at(c, x - 330 + i * 120, y + 140, 0, g):
                    K.rr(c, 0, 0, 100, 60, 30, "#FFF4D6")
                    K.text(c, "+1", 0, 2, 40, "hand", L.ACC)
    return None


ev(j, k_box15, input15, "wood_high", 0.7)
b.hit(j, k_type15, "pop", 0.6, "打字")
b.hit(j, k_likes15, "clap", 0.75, "好多人加一")


def relax15(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(15, k_relax15))
    if sc <= 0:
        return None
    gy = cy + 400
    with at_pop(c, cx, gy, sc):
        C.line(c, (cx - 520, gy), (cx + 520, gy), BLACK, 6)
        hy = gy - 290 * 0.9
        draw_li(c, cx - 250, gy, 0.9, "smile", lh=(cx - 340, hy - 40), rh=(cx - 160, hy - 40))
        for i, x in enumerate((cx + 40, cx + 220, cx + 400)):
            phone_hold(c, x, gy, 0.6)
        K.text(c, "放轻松", cx - 250, hy - 140, 64, "hand", GREEN)
    sparkle(c, cx - 250, gy - 300, T - tb(15, k_relax15), YELLOW, 10, 110, 200)
    return None


ev(j, k_relax15, relax15, "ding", 0.8)
b.move(j, k_n, (cx, cy + 420, Z), dur=1.0)
KT.next_card(j, k_n + 1, "闹钟响了，为什么梦里先变成了别的声音？", cx, cy + 860)

# ================================================================ 收尾
L.finish(cover_shot=2, square_shot=4, notes=NOTES)
L.export(globals())
