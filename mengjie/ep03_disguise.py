"""《梦的解析》03 伪装：梦里的事，为什么总拐着弯说？（白板手绘 + AI 旁白，竖屏 2:3）

误区对照：很多人以为“梦是反着来的”，书里说梦是化了妆的心里话。
- 开场：梦泡泡里一个问号、一副面具罩上去、一把钥匙晃出来，配音“梦在打哑谜”逐字砸下；
- 痛点：小李梦见礼物被打叉、梦里一堆加班文件，醒来坐起一脸问号；
- 身边的例子（drop 在第 2 屏）：同事背后藏着一摞文件，心里想“帮我”，开口砸下“忙不忙？”；
  妈妈心里想着空着的饭桌，电话里只说“家里一切都好”；
- 书中：弗洛伊德与拐弯的箭头；病人来“反驳”；她的梦：一点熏鲑鱼、店关门、电话打不通 → “落空”；
  瘦朋友想长胖、丈夫欣赏朋友 → 请不成客 → “愿望满足了”；看门的拦住心思，愿望戴上面具混过去；
  上司底下写文章，批评改成拐弯的话；两层：化完妆的样子 / 底下的心里话；
- 现在怎么看：有的梦有暗号，有的梦是白天回放；
- 误区对照“梦反着来”打叉 → 三步：吃亏/得好处的天平、梦里的人对照身边的人、写下没说出口的话；摘下面具；评论区与下一讲。
文案与出处见 mengjie/PLAN.md「### 03」。小李为虚构人物，例子是示意。
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

PURPLE, PURPLE_FILL = "#7A3E9D", "#E3CFF0"


# ================================================================ 本讲小元件

def woman(c, x, y, s, fill="#F6C3BE", line=RED, mood="flat", thin=False, hair="#5A3A2A", lh=None, rh=None, apron=False):
    """成年女性：盘发、连衣裙。(x, y) 为脚底；thin=True 画得很瘦。"""
    hy = y - 290 * s
    w = (36 if thin else 72) * s
    for sg in (-1, 1):
        C.line(c, (x + sg * 14 * s, y - 100 * s), (x + sg * 34 * s, y), BLACK, 9)
    sh = (x, hy + 75 * s)
    C.line(c, sh, lh or (x - 70 * s, hy + 175 * s), BLACK, 9)
    C.line(c, sh, rh or (x + 70 * s, hy + 175 * s), BLACK, 9)
    dress = P((x - 24 * s, hy + 52 * s), (x + 24 * s, hy + 52 * s), (x + w, y - 90 * s), (x - w, y - 90 * s), close=True)
    c.drawPath(dress, K.paint(fill))
    c.drawPath(dress, wb.marker(line, 6))
    if apron:
        box(c, x, y - 150 * s, 60 * s, 80 * s, PAPER_W, GRAY, 4, 8)
    c.drawCircle(x, hy - 50 * s, 24 * s, K.paint(hair))
    c.drawCircle(x, hy - 6 * s, 50 * s, K.paint(hair))
    c.drawCircle(x, hy, 45 * s, K.paint(PAPER_W))
    c.drawCircle(x, hy, 45 * s, wb.marker(BLACK, 8))
    C._eyes_mouth(c, x, hy, s, mood, 1.0)


def colleague(c, x, y, s, mood="flat", lh=None, rh=None):
    """同事：小人 + 圆眼镜 + 发髻。"""
    hy = y - 290 * s
    c.drawCircle(x, hy - 50 * s, 20 * s, K.paint(BLACK))
    draw_li(c, x, y, s, mood, lh=lh, rh=rh)
    for sg in (-1, 1):
        c.drawCircle(x + sg * 16 * s, hy - 4 * s, 13 * s, wb.marker(BLUE, 4))


def phone(c, x, y, s=1.0, rot=0.0):
    with K.at(c, x, y, rot, s):
        box(c, 0, 0, 70, 120, "#2E2A28", BLACK, 4, 12)
        box(c, 0, -4, 56, 90, "#CFE0F5", BLUE, 2, 6)


def mask(c, x, y, s=1.0, rot=0.0, alpha=1.0, stick=True):
    """化装舞会面具（紫色，两只眼洞，一根小棍）。"""
    with K.at(c, x, y, rot, s):
        p = skia.Path()
        p.moveTo(-120, -20)
        p.cubicTo(-90, -70, -30, -50, 0, -30)
        p.cubicTo(30, -50, 90, -70, 120, -20)
        p.cubicTo(110, 40, 40, 50, 0, 20)
        p.cubicTo(-40, 50, -110, 40, -120, -20)
        p.close()
        c.drawPath(p, K.paint(PURPLE_FILL, alpha))
        c.drawPath(p, wb.marker(PURPLE, 7, alpha))
        for sg in (-1, 1):
            c.drawOval(skia.Rect.MakeXYWH(sg * 55 - 28, -22, 56, 30), K.paint(BLACK, alpha))
        for sg in (-1, 1):
            star(c, sg * 95, -45, 14, alpha=alpha)
        if stick:
            C.line(c, (110, 10), (170, 140), "#A9773E", 10, alpha)


def fish(c, x, y, s=1.0):
    """一小片熏鲑鱼（橙色鱼片）。"""
    with K.at(c, x, y, 0, s):
        p = skia.Path()
        p.moveTo(-60, 0)
        p.quadTo(-10, -40, 50, -8)
        p.lineTo(80, -30)
        p.lineTo(74, 22)
        p.lineTo(50, 8)
        p.quadTo(-10, 40, -60, 0)
        p.close()
        c.drawPath(p, K.paint("#F4A07A"))
        c.drawPath(p, wb.marker(ORANGE, 5))
        for i in range(3):
            C.line(c, (-30 + i * 22, -14), (-38 + i * 22, 14), PAPER_W, 4)


def files(c, x, y, n=5, w=150):
    """一摞文件，(x, y) 为底部中心。"""
    for i in range(n):
        box(c, x + (i % 2) * 8 - 4, y - 18 - i * 26, w, 26, PAPER_W, GRAY, 4, 4)


def gift(c, x, y, s=1.0):
    with K.at(c, x, y, 0, s):
        box(c, 0, 0, 160, 130, "#F6C3BE", RED, 6, 8)
        C.line(c, (0, -65), (0, 65), RED, 9)
        C.line(c, (-80, 0), (80, 0), RED, 9)
        for sg in (-1, 1):
            c.drawOval(skia.Rect.MakeXYWH(-4 + sg * 30 - 26, -96, 52, 34), wb.marker(RED, 6))


def _hook(H, j, cx, cy, acc):
    """开场：梦泡泡里一个问号 → 面具罩上去 → 钥匙晃出来；随后“梦在打哑谜”逐字砸下。"""
    b = H.b
    H.note("？")
    CLx, CLy = cx, cy - 250

    def cl(c, kk, T):
        sc = pop_scale(T - H.tb(j, 0))
        if not dream_cloud(c, CLx, CLy, 760, 440, sc):
            return None
        hidden = T >= H.tb(j, 1)
        with at_pop(c, CLx, CLy, sc):
            if not hidden:
                K.text(c, "？", CLx, CLy + 10, 220, "hand", NIGHT)
        return None
    b.custom(j, 0, 0.3, cl, sfx="wood_low", gain=0.7)

    def mk(c, kk, T):
        dt = T - H.tb(j, 1)
        if dt < 0:
            return None
        f = ease_out(clamp01(dt / 0.3))
        mask(c, CLx - 40, lerp(CLy - 300, CLy, f), 1.6, -6, stick=False)
        return None
    b.custom(j, 1, 1.3, mk, sfx="tom", gain=0.75)

    def key(c, kk, T):
        dt = T - H.tb(j, 2)
        if dt < 0:
            return None
        sw = 12 * math.exp(-dt * 3) * math.sin(dt * 10)
        with K.at(c, CLx + 330, CLy + 120, 30 + sw, pop_scale(dt)):
            c.drawCircle(0, -60, 34, K.paint("#FFE39A"))
            c.drawCircle(0, -60, 34, wb.marker(YELLOW, 8))
            c.drawCircle(0, -60, 12, K.paint(PAPER_W))
            C.line(c, (0, -26), (0, 70), YELLOW, 12)
            C.line(c, (0, 40), (24, 40), YELLOW, 10)
            C.line(c, (0, 62), (20, 62), YELLOW, 10)
        sparkle(c, CLx + 330, CLy + 100, dt, YELLOW, 8, 70, 140)
        return None
    b.custom(j, 2, 2.3, key, sfx="ding", gain=0.75)
    A.finish_hook(H, j, cx, cy, acc)


L, R, Z = A.setup("03", _hook)
b = L.b
KT = A.Kit(L)
tb, wt, nx, kq, cap, ev, pop_fn = KT.tb, KT.wt, KT.nx, KT.kq, KT.cap, KT.ev, KT.pop_fn

NOTES = [
    "书目：Sigmund Freud, Die Traumdeutung（1899；中译本《梦的解析》）第四章“梦的伪装”。",
    "书中例子：“聪明的屠夫之妻”的梦（只剩一点熏鲑鱼、店关门、电话打不通），她的瘦朋友想来吃饭长胖，丈夫欣赏这位朋友；"
    "政治作家在当权者面前要伪装措辞的比方；结论“梦是被压抑愿望的伪装的满足”。",
    "现在的研究不认为每个梦都有隐藏含义；片中交代为书里的看法。小李为虚构人物，例子均为示意。",
]

# ================================================================ 屏 0：开场
j = L.scene(0, L.intro_view(*R[0]))
L.intro(j, *R[0])

# ================================================================ 屏 1：梦里礼物被打叉、一摞加班文件；醒来一脸问号
cx, cy = R[1]
j = L.scene(1, (cx, cy + 10, Z))
k_bed = 0
k_cl = nx(j, wt(0, 0, 0.6), k_bed)
k_wake = nx(j, wt(0, 1, 0.4), k_cl)
k_no = nx(j, wt(1, 0, 0.5), k_wake)
k_bad = nx(j, wt(1, 1, 0.5), k_no)
BED1 = (cx - 380, cy + 330)
HIP1 = (BED1[0] + 230, BED1[1] - 20)
CL1 = (cx + 100, cy - 270)
L.note("想要的", "不想要的", "？")


def scene1(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(1, k_bed))
    if sc <= 0:
        return None
    with at_pop(c, cx, BED1[1], sc):
        bed(c, *BED1, 560)
        hx, hy = sleeper(c, *HIP1, 0.8, T, tb(1, k_wake), "o" if T >= tb(1, k_wake) else "smile")
        if T >= tb(1, k_wake):
            g = pop_scale(T - tb(1, k_wake))
            with K.at(c, hx + 120, hy - 60, 10, g):
                K.text(c, "？", 0, 0, 110, "hand", RED)
    return None


ev(j, k_bed, scene1, "wood_low", 0.7)


def cloud1(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(1, k_cl))
    if not dream_cloud(c, CL1[0], CL1[1], 820, 520, sc, tail_to=(HIP1[0] - 300, HIP1[1] - 120)):
        return None
    with at_pop(c, CL1[0], CL1[1], sc):
        x1, x2, y = CL1[0] - 190, CL1[0] + 190, CL1[1] + 20
        K.text(c, "想要的", x1, y - 160, 50, "hand", GREEN)
        gift(c, x1, y + 30, 0.9)
        if T >= tb(1, k_no):
            g = pop_scale(T - tb(1, k_no))
            with K.at(c, x1, y + 30, 0, g):
                c.drawPath(cross(0, 0, 90), wb.marker(RED, 12))
        if T >= tb(1, k_bad):
            g = pop_scale(T - tb(1, k_bad))
            with at_pop(c, x2, y + 100, g):
                K.text(c, "不想要的", x2, y - 160, 50, "hand", RED)
                files(c, x2, y + 110, 6, 170)
    return None


ev(j, k_cl, cloud1, "pop", 0.75)
b.hit(j, k_wake, "kick", 0.85, "醒来一脸问号")
b.shots[j].shake = [(k_wake, 7.0)]
b.hit(j, k_no, "rim", 0.8, "想要的打叉")
b.hit(j, k_bad, "wood_high", 0.75, "梦见一摞文件")

# ================================================================ 屏 2：同事想让你帮忙 → drop：“你最近忙不忙？”
cx, cy = R[2]
j = L.scene(2, (cx, cy + 10, Z))
KD = L.drop_k()
b.shots[j].shake, b.shots[j].flashes = [(KD, 16.0)], [(KD, 0.45)]
k_li2 = 1
k_col = max(k_li2 + 1, min(kq(j, wt(3, 0, 0.4), k_li2 + 1), KD - 2))
k_th = max(k_col + 1, KD - 1) if KD - 1 > k_col else k_col
GY2 = cy + 440
COL = (cx - 300, GY2)
L.note("帮帮我")


def li2(c, sc, T, cx=cx, cy=cy):
    x = cx + 300
    with at_pop(c, x, GY2, sc):
        c.drawRect(skia.Rect.MakeXYWH(x - 120, GY2 - 160, 360, 30), K.paint(WOOD))
        c.drawRect(skia.Rect.MakeXYWH(x - 120, GY2 - 160, 360, 30), wb.marker("#A9773E", 6))
        for lx in (x - 100, x + 220):
            C.line(c, (lx, GY2 - 130), (lx, GY2), "#A9773E", 8)
        box(c, x + 120, GY2 - 240, 170, 130, "#2E2A28", BLACK, 5, 8)
        draw_li(c, x - 20, GY2, 0.85, "o" if T >= tb(2, KD) else "flat", lh=(x - 80, GY2 - 160), rh=(x + 40, GY2 - 165))
    return None


ev(j, k_li2, pop_fn(j, k_li2, li2), "wood_low", 0.7)


def col2(c, sc, T, cx=cx, cy=cy):
    x, y = COL
    with at_pop(c, x, y, sc):
        files(c, x - 130, y - 110, 5, 130)
        colleague(c, x, y, 0.85, "smile", lh=(x - 80, y - 170), rh=(x + 60, y - 140))
    return None


ev(j, k_col, pop_fn(j, k_col, col2), "wood_high", 0.7)
TH2 = (cx - 280, cy - 300)


def th2(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(2, k_th))
    if not dream_cloud(c, *TH2, 440, 300, sc, tail_to=(COL[0] + 10, COL[1] - 330)):
        return None
    with at_pop(c, *TH2, sc):
        K.text(c, "帮帮我", TH2[0], TH2[1] - 50, 64, "hand", NIGHT)
        files(c, TH2[0], TH2[1] + 100, 3, 110)
    return None


ev(j, k_th, th2, "pop", 0.7)
ev(j, KD, L.slam_text("忙不忙？", cx + 220, cy - 120, 140, RED, j, KD, rot=-5), "kick", 0.95)

# ================================================================ 屏 3：妈妈想你回家，电话里只说“家里一切都好”
cx, cy = R[3]
j = L.scene(3, (cx, cy + 10, Z))
k_mom = kq(j, wt(4, 0, 0.3), 0)
k_th3 = nx(j, wt(4, 0, 0.8), k_mom)
k_call = nx(j, wt(4, 1, 0.2), k_th3)
k_say = nx(j, wt(4, 1, 0.75), k_call)
GY3 = cy + 440
MOM = (cx - 330, GY3)
L.note("回家")


def mom3(c, sc, T, cx=cx, cy=cy):
    x, y = MOM
    with at_pop(c, x, y, sc):
        roof = P((x - 220, y - 420), (x, y - 560), (x + 220, y - 420), close=True)
        c.drawPath(roof, K.paint("#F6C3BE"))
        c.drawPath(roof, wb.marker(RED, 7))
        c.drawRect(skia.Rect.MakeXYWH(x - 190, y - 420, 380, 420), wb.marker("#A9773E", 7))
        talk = T >= tb(3, k_call)
        woman(c, x, y, 0.85, "#FFE39A", ORANGE, "smile", rh=(x + 50, y - 330) if talk else None, apron=True)
        if talk:
            phone(c, x + 50, y - 300, 0.6, 10)
    return None


ev(j, k_mom, pop_fn(j, k_mom, mom3), "wood_low", 0.7)
TH3 = (cx - 160, cy - 300)


def th3(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(3, k_th3))
    if not dream_cloud(c, *TH3, 520, 340, sc, tail_to=(MOM[0] + 20, MOM[1] - 470)):
        return None
    with at_pop(c, *TH3, sc):
        x, y = TH3[0], TH3[1] + 40
        c.drawRect(skia.Rect.MakeXYWH(x - 150, y - 10, 300, 24), K.paint(WOOD))
        c.drawRect(skia.Rect.MakeXYWH(x - 150, y - 10, 300, 24), wb.marker("#A9773E", 5))
        for sg in (-1, 1):
            c.drawPath(P((x + sg * 190, y + 80), (x + sg * 190, y - 70)), wb.marker(GRAY, 6))
            c.drawPath(P((x + sg * 190, y + 20), (x + sg * 150, y + 20), (x + sg * 150, y + 80)), wb.marker(GRAY, 6))
        for i, dx in enumerate((-80, 0, 80)):
            c.drawOval(skia.Rect.MakeXYWH(x + dx - 34, y - 34, 68, 26), K.paint(PAPER_W))
            c.drawOval(skia.Rect.MakeXYWH(x + dx - 34, y - 34, 68, 26), wb.marker(BLACK, 4))
        K.text(c, "回家", x + 140, y - 110, 54, "hand", RED)
    return None


ev(j, k_th3, th3, "pop", 0.7)


def li3(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(3, k_call))
    if sc <= 0:
        return None
    x, y = cx + 360, GY3
    with at_pop(c, x, y, sc):
        for i, (dx, h) in enumerate(((-150, 300), (130, 380))):
            box(c, x + dx, y - h / 2, 110, h, "#DCE6F2", BLUE, 5, 4)
        draw_li(c, x, y, 0.8, "smile", rh=(x - 50, y - 300))
        phone(c, x - 50, y - 280, 0.6, -10)
        for i in range(3):
            ph = ((T - tb(3, k_call)) * 1.2 + i / 3) % 1
            r = 40 + ph * 80
            p = skia.Path()
            p.addArc(skia.Rect.MakeXYWH(x - 150 - r, y - 300 - r, 2 * r, 2 * r), 150, 60)
            c.drawPath(p, wb.marker(GRAY, 5, 1 - ph))
    return None


ev(j, k_call, li3, "shaker", 0.7)
ev(j, k_say, L.pop_bubble("一切都好", cx + 170, cy - 40, j, k_say, 64, BLACK, tail=-1), "pop", 0.75)

# ================================================================ 屏 4：弗洛伊德：梦也拐着弯说话；病人做梦来“反驳”
cx, cy = R[4]
j = L.scene(4, (cx, cy + 10, Z))
k_fr = kq(j, wt(5, 0, 0.3), 0)
k_curve = nx(j, wt(5, 1, 0.5), k_fr)
k_lady = nx(j, wt(6, 0, 0.6), k_curve)
k_rb = nx(j, wt(6, 1, 0.6), k_lady)
L.note("心里话", "梦", "拐着弯")


def fr4(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 330, cy + 440
    with at_pop(c, x, y, sc):
        draw_freud(c, x, y, 1.0, "smile")
    return None


ev(j, k_fr, pop_fn(j, k_fr, fr4), "wood_low", 0.7)


def curve4(c, kk, T, cx=cx, cy=cy):
    t0 = tb(4, k_curve)
    if T < t0:
        return None
    f = ease_out(clamp01((T - t0) / 0.6))
    a = (cx - 380, cy - 330)
    p = skia.Path()
    p.moveTo(*a)
    p.cubicTo(cx - 240, cy - 560, cx - 60, cy - 560, cx, cy - 400)
    p.cubicTo(cx + 60, cy - 240, cx + 240, cy - 240, cx + 300, cy - 330)
    c.drawPath(wb.partial(p, f)[0], wb.marker(PURPLE, 9))
    g = pop_scale(T - t0)
    with K.at(c, a[0] - 60, a[1] + 60, 0, g):
        c.drawPath(C.heart_path(0, 0, 60), K.paint("#F6C3BE"))
        c.drawPath(C.heart_path(0, 0, 60), wb.marker(RED, 6))
        K.text(c, "心里话", 0, 110, 44, "hand", RED)
    if f >= 1:
        dream_cloud(c, cx + 420, cy - 300, 220, 150, pop_scale(T - t0 - 0.6))
        K.text(c, "梦", cx + 420, cy - 296, 60, "hand", NIGHT, clamp01((T - t0 - 0.6) / 0.2))
        K.text(c, "拐着弯", cx, cy - 190, 64, "hand", PURPLE, clamp01((T - t0 - 0.4) / 0.2))
    return None


ev(j, k_curve, curve4, "wood_high", 0.75)


def lady4(c, sc, T, cx=cx, cy=cy):
    x, y = cx + 250, cy + 440
    with at_pop(c, x, y, sc):
        woman(c, x, y, 1.0, "#CFE0F5", BLUE, "flat", lh=(x - 110, y - 220), rh=(x + 70, y - 110))
    return None


ev(j, k_lady, pop_fn(j, k_lady, lady4), "pop", 0.7)
ev(j, k_rb, L.stamp("反驳", cx + 60, cy + 10, 80, j, k_rb, rot=-8), "rim", 0.85)
b.shots[j].shake = [(k_rb, 6.0)]

# ================================================================ 屏 5：她的梦：一点熏鲑鱼、店关门、电话打不通 → “落空”
cx, cy = R[5]
j = L.scene(5, (cx, cy + 10, Z))
k_cl5 = kq(j, wt(7, 0, 0.4), 0)
k_fish = nx(j, wt(7, 1, 0.6), k_cl5)
k_shop = nx(j, wt(7, 2, 0.4), k_fish)
k_tel = nx(j, wt(7, 3, 0.4), k_shop)
k_fail = nx(j, wt(8, 1, 0.5), k_tel)
CL5 = (cx + 40, cy - 230)
LADY5 = (cx - 380, cy + 450)
L.note("关门")


def lady5(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(5, k_cl5))
    if sc <= 0:
        return None
    x, y = LADY5
    sad = T >= tb(5, k_fail)
    with at_pop(c, x, y, sc):
        woman(c, x, y, 0.9, "#CFE0F5", BLUE, "sad" if sad else "smile",
              lh=(x - 90, y - 300) if sad else None, rh=(x + 90, y - 300) if sad else None)
    return None


ev(j, k_cl5, lady5, "wood_low", 0.7)


def cloud5(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(5, k_cl5))
    if not dream_cloud(c, CL5[0], CL5[1], 960, 600, sc, tail_to=(LADY5[0] + 10, LADY5[1] - 480)):
        return None
    with at_pop(c, CL5[0], CL5[1], sc):
        x0, y = CL5[0], CL5[1] + 20
        if T >= tb(5, k_fish):
            g = pop_scale(T - tb(5, k_fish))
            with K.at(c, x0 - 270, y + 40, 0, g):
                c.drawOval(skia.Rect.MakeXYWH(-140, 0, 280, 80), K.paint(PAPER_W))
                c.drawOval(skia.Rect.MakeXYWH(-140, 0, 280, 80), wb.marker(BLACK, 6))
                fish(c, 0, 20, 1.1)
        if T >= tb(5, k_shop):
            g = pop_scale(T - tb(5, k_shop))
            with K.at(c, x0, y, 0, g):
                c.drawPath(P((-130, -60), (0, -140), (130, -60), close=True), K.paint("#F6C3BE"))
                c.drawPath(P((-130, -60), (0, -140), (130, -60), close=True), wb.marker(RED, 6))
                c.drawRect(skia.Rect.MakeXYWH(-110, -60, 220, 180), K.paint(PAPER_W))
                c.drawRect(skia.Rect.MakeXYWH(-110, -60, 220, 180), wb.marker(BLACK, 6))
                with K.at(c, 0, 40, -8):
                    box(c, 0, 0, 150, 70, "#FFE39A", RED, 5, 6)
                    K.text(c, "关门", 0, 2, 46, "hand", RED)
        if T >= tb(5, k_tel):
            g = pop_scale(T - tb(5, k_tel))
            with K.at(c, x0 + 270, y + 20, 0, g):
                phone(c, 0, 0, 1.3)
                c.drawPath(cross(0, 0, 50), wb.marker(RED, 10))
    return None


ev(j, k_cl5, cloud5, "pop", 0.75)
b.hit(j, k_fish, "pop", 0.7, "只剩一点熏鲑鱼")
b.hit(j, k_shop, "wood_high", 0.75, "店都关了")
b.hit(j, k_tel, "rim", 0.75, "电话打不通")
ev(j, k_fail, L.stamp("落空", cx + 200, cy + 300, 100, j, k_fail, rot=-6), "kick", 0.9)
b.shots[j].shake = [(k_fail, 8.0)]

# ================================================================ 屏 6：瘦朋友想来吃饭长胖；丈夫欣赏朋友；请不成客 → 愿望满足了
cx, cy = R[6]
j = L.scene(6, (cx, cy + 10, Z))
k_fri = kq(j, wt(9, 1, 0.4), 0)
k_fat = nx(j, wt(9, 3, 0.3), k_fri)
k_hus = nx(j, wt(10, 1, 0.3), k_fat)
k_noparty = nx(j, wt(11, 0, 0.5), k_hus)
k_ok = nx(j, wt(11, 2, 0.4), k_noparty)
GY6 = cy + 440
FRI = (cx - 320, GY6)
HUS = (cx + 330, GY6)
L.note("朋友", "长胖", "丈夫", "请客")


def fri6(c, sc, T, cx=cx, cy=cy):
    x, y = FRI
    with at_pop(c, x, y, sc):
        woman(c, x, y, 0.95, "#D3EDDC", GREEN, "smile", thin=True)
        K.text(c, "朋友", x, y + 50, 46, "sans_medium", GREEN)
    return None


ev(j, k_fri, pop_fn(j, k_fri, fri6), "wood_low", 0.7)
TH6 = (cx - 330, cy - 280)


def th6(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(6, k_fat))
    if not dream_cloud(c, *TH6, 380, 260, sc, tail_to=(FRI[0], FRI[1] - 340)):
        return None
    with at_pop(c, *TH6, sc):
        x, y = TH6
        c.drawOval(skia.Rect.MakeXYWH(x - 120, y + 10, 140, 50), K.paint(PAPER_W))
        c.drawOval(skia.Rect.MakeXYWH(x - 120, y + 10, 140, 50), wb.marker(BLACK, 5))
        c.drawCircle(x - 50, y + 10, 30, K.paint("#E0A21B"))
        K.text(c, "长胖", x + 80, y + 10, 56, "hand", ORANGE)
    return None


ev(j, k_fat, th6, "pop", 0.7)


def hus6(c, sc, T, cx=cx, cy=cy):
    x, y = HUS
    with at_pop(c, x, y, sc):
        draw_li(c, x, y, 0.95, "smile")
        box(c, x, y - 150, 90, 110, PAPER_W, GRAY, 4, 8)
        K.text(c, "丈夫", x, y + 50, 46, "sans_medium", BLUE)
        for i in range(2):
            ph = ((T - tb(6, k_hus)) * 0.8 + i / 2) % 1
            hx, hy = lerp(x - 100, FRI[0] + 160, ph), y - 330 - 40 * math.sin(ph * math.pi)
            with K.at(c, hx, hy, 0, 0.5):
                c.drawPath(C.heart_path(0, 0, 50), K.paint("#F6C3BE", 1 - ph * 0.6))
                c.drawPath(C.heart_path(0, 0, 50), wb.marker(RED, 6, 1 - ph * 0.6))
    return None


ev(j, k_hus, pop_fn(j, k_hus, hus6), "ding", 0.7)


def party6(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(6, k_noparty))
    if sc <= 0:
        return None
    x, y = cx + 220, cy - 300
    with at_pop(c, x, y, sc):
        box(c, x, y, 360, 200, PAPER_W, ORANGE, 6, 12)
        K.text(c, "请客", x, y - 30, 70, "hand", ORANGE)
        C.line(c, (x - 100, y + 50), (x + 100, y + 50), GRAY, 6)
        c.drawPath(cross(x, y, 110), wb.marker(RED, 12))
    return None


ev(j, k_noparty, party6, "rim", 0.8)
ev(j, k_ok, L.stamp("愿望满足了", cx + 60, cy - 40, 76, j, k_ok, color=GREEN, rot=-5), "kick", 0.9)
b.shots[j].shake = [(k_ok, 7.0)]

# ================================================================ 屏 7：梦里有个看门的；说不出口的愿望化了妆再出来
cx, cy = R[7]
j = L.scene(7, (cx, cy + 10, Z))
k_gate = kq(j, wt(12, 0, 0.5), 0)
k_stop = nx(j, wt(12, 1, 0.5), k_gate)
k_mask = nx(j, wt(13, 1, 0.3), k_stop)
k_pass = nx(j, wt(13, 1, 0.8), k_mask)
GY7 = cy + 420
DOORX = cx + 120
L.note("看门的", "露面", "想要")


def gate7(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, DOORX, GY7, sc):
        c.drawRect(skia.Rect.MakeXYWH(DOORX - 110, GY7 - 520, 220, 520), K.paint("#F1E3CB"))
        c.drawRect(skia.Rect.MakeXYWH(DOORX - 110, GY7 - 520, 220, 520), wb.marker("#A9773E", 9))
        K.text(c, "露面", DOORX, GY7 - 580, 50, "hand", "#A9773E")
        x = DOORX + 250
        draw_boss(c, x, GY7, 0.85, mood="flat", lh=(x - 100, GY7 - 200))
        hy = GY7 - 290 * 0.85
        c.drawPath(P((x - 50, hy - 30), (x + 50, hy - 30), (x + 40, hy - 70), (x - 40, hy - 70), close=True), K.paint(NIGHT))
        C.line(c, (x - 70, hy - 30), (x + 60, hy - 30), NIGHT, 10)
        K.text(c, "看门的", x, GY7 + 50, 46, "sans_medium", NIGHT)
    return None


ev(j, k_gate, pop_fn(j, k_gate, gate7), "wood_low", 0.7)


def wish7(c, kk, T, cx=cx, cy=cy):
    t0 = tb(7, k_stop)
    if T < t0:
        return None
    g = pop_scale(T - t0)
    masked = T >= tb(7, k_mask)
    go = ease_in_out(clamp01((T - tb(7, k_pass)) / 0.6)) if T >= tb(7, k_pass) else 0.0
    bounce = 0 if masked else -18 * abs(math.sin((T - t0) * 6)) * math.exp(-(T - t0) * 1.5)
    x, y = lerp(cx - 330, DOORX, go), cy + 120 + bounce
    with K.at(c, x, y, 0, g):
        c.drawPath(C.heart_path(0, 0, 90), K.paint("#F6C3BE"))
        c.drawPath(C.heart_path(0, 0, 90), wb.marker(RED, 7))
        for sg in (-1, 1):
            c.drawCircle(sg * 26, -10, 7, K.paint(BLACK))
        if not masked:
            K.text(c, "想要", 0, 130, 46, "hand", RED)
        else:
            mask(c, 0, -10, 0.55, 0, stick=False)
    if not masked:
        with K.at(c, cx - 140, cy + 100, 0, pop_scale(T - t0 - 0.1)):
            c.drawPath(cross(0, 0, 60), wb.marker(RED, 12))
    else:
        sparkle(c, cx - 330, cy + 100, T - tb(7, k_mask), PURPLE, 8, 100, 170)
    return None


ev(j, k_stop, wish7, "rim", 0.8)
b.hit(j, k_mask, "ding", 0.8, "戴上面具")
ev(j, k_pass, L.slam_text("化了妆", cx - 220, cy - 320, 110, PURPLE, j, k_pass, rot=-4), "kick", 0.85)

# ================================================================ 屏 8：严厉上司底下写文章，批评写得拐弯抹角；两层：化完妆的样子 / 心里话
cx, cy = R[8]
j = L.scene(8, (cx, cy + 10, Z))
k_desk8 = kq(j, wt(14, 0, 0.5), 0)
k_x8 = nx(j, wt(14, 1, 0.3), k_desk8)
k_soft = nx(j, wt(14, 1, 0.8), k_x8)
k_layer = nx(j, wt(15, 1, 0.3), k_soft)
k_heart = nx(j, wt(15, 2, 0.3), k_layer)
L.note("你错了", "再想想？", "醒来记得的", "心里话")


def desk8(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 250, cy + 440
    with at_pop(c, x, y, sc):
        draw_boss(c, x - 180, y, 1.0, mood="sad", lh=(x - 290, y - 230))
        c.drawRect(skia.Rect.MakeXYWH(x - 30, y - 160, 330, 30), K.paint(WOOD))
        c.drawRect(skia.Rect.MakeXYWH(x - 30, y - 160, 330, 30), wb.marker("#A9773E", 6))
        for lx in (x - 10, x + 280):
            C.line(c, (lx, y - 130), (lx, y), "#A9773E", 8)
        draw_li(c, x + 140, y, 0.7, "sad" if T < tb(8, k_soft) else "flat", lh=(x + 80, y - 165), rh=(x + 200, y - 170))
        A.pen(c, x + 210, y - 190, -40, 0.6)
    return None


ev(j, k_desk8, pop_fn(j, k_desk8, desk8), "wood_low", 0.7)


def paper8(c, kk, T, cx=cx, cy=cy):
    t0 = tb(8, k_x8)
    if T < t0:
        return None
    x, y = cx - 200, cy - 180
    with K.at(c, x, y, -3, pop_scale(T - t0)):
        box(c, 0, 0, 420, 300, PAPER_W, BLACK, 6, 6)
        K.text(c, "你错了", 0, -60, 70, "hand", BLACK)
        f = clamp01((T - t0 - 0.15) / 0.3)
        if f > 0:
            C.line(c, (-120, -60), (-120 + 240 * f, -60), RED, 10)
        if T >= tb(8, k_soft):
            K.text(c, "再想想？", 0, 60, 70, "hand", BLUE, clamp01((T - tb(8, k_soft)) / 0.2))
    return None


ev(j, k_x8, paper8, "rim", 0.8)
b.hit(j, k_soft, "pop", 0.7, "改成拐弯的话")


def layer8(c, kk, T, cx=cx, cy=cy):
    t0 = tb(8, k_layer)
    if T < t0:
        return None
    x, y = cx + 330, cy - 120
    with at_pop(c, x, y, pop_scale(T - t0)):
        box(c, x, y - 120, 360, 200, PURPLE_FILL, PURPLE, 7, 14)
        mask(c, x, y - 140, 0.75, 0, stick=False)
        K.text(c, "醒来记得的", x, y - 290, 46, "hand", PURPLE)
        c.drawPath(wb.arrow((x, y - 10), (x, y + 70), 0.0, 26), wb.marker(GRAY, 6))
        if T >= tb(8, k_heart):
            g = pop_scale(T - tb(8, k_heart))
            with K.at(c, x, y + 180, 0, g):
                box(c, 0, 0, 360, 200, "#FFF4D6", RED, 7, 14)
                c.drawPath(C.heart_path(0, 0, 60), K.paint("#F6C3BE"))
                c.drawPath(C.heart_path(0, 0, 60), wb.marker(RED, 6))
    return None


ev(j, k_layer, layer8, "wood_high", 0.75)
ev(j, k_heart, L.slam_text("心里话", cx + 330, cy + 400, 90, RED, j, k_heart, rot=-3), "kick", 0.85)

# ================================================================ 屏 9：现在怎么看——有的梦有暗号，有的梦是白天在回放
cx, cy = R[9]
j = L.scene(9, (cx, cy + 10, Z))
k_bk9 = kq(j, wt(16, 0, 0.5), 0)
k_code = nx(j, wt(16, 1, 0.5), k_bk9)
k_play = nx(j, wt(16, 2, 0.5), k_code)
L.note("书里的看法", "研究", "暗号", "回放", "不一定")


def bk9(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, cy - 380, sc):
        box(c, cx - 300, cy - 380, 220, 280, NIGHT, BLACK, 6, 10)
        K.text(c, "梦的", cx - 300, cy - 420, 50, "serif_black", "#FFE39A")
        K.text(c, "解析", cx - 300, cy - 360, 50, "serif_black", "#FFE39A")
        K.text(c, "书里的看法", cx - 300, cy - 190, 44, "hand", NIGHT)
        A.brain(c, cx + 280, cy - 380, 100)
        K.text(c, "研究", cx + 280, cy - 230, 46, "hand", BLUE)
        K.text(c, "不一定", cx, cy - 380, 56, "hand", ORANGE)
    return None


ev(j, k_bk9, pop_fn(j, k_bk9, bk9), "wood_low", 0.7)


def code9(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(9, k_code))
    x, y = cx - 270, cy + 170
    if not dream_cloud(c, x, y, 480, 380, sc):
        return None
    with at_pop(c, x, y, sc):
        mask(c, x, y - 20, 0.9, -6, stick=False)
        K.text(c, "暗号", x, y + 100, 56, "hand", PURPLE)
    return None


ev(j, k_code, code9, "pop", 0.75)


def play9(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(9, k_play))
    x, y = cx + 270, cy + 170
    if not dream_cloud(c, x, y, 480, 380, sc):
        return None
    with at_pop(c, x, y, sc):
        box(c, x, y - 20, 240, 160, "#DCE6F2", BLUE, 6, 12)
        c.drawPath(P((x - 30, y - 70), (x - 30, y + 30), (x + 50, y - 20), close=True), K.paint(BLUE))
        K.text(c, "回放", x, y + 100, 56, "hand", BLUE)
    return None


ev(j, k_play, play9, "ding", 0.75)

# ================================================================ 屏 10：别急着说“梦反着来”（打叉）→ 三步
cx, cy = R[10]
j = L.scene(10, (cx, cy + 10, Z))
k_li10 = kq(j, wt(17, 0, 0.5), 0)
k_myth = nx(j, wt(17, 1, 0.3), k_li10)
k_x10 = nx(j, wt(17, 1, 0.8), k_myth)
k_3 = nx(j, wt(17, 2, 0.5), k_x10)
GY10 = cy + 420
L.note("梦反着来", "三步")


def li10(c, sc, T, cx=cx, cy=cy):
    x = cx - 280
    with at_pop(c, x, GY10, sc):
        C.line(c, (x - 260, GY10), (x + 260, GY10), BLACK, 7)
        draw_li(c, x, GY10, 0.9, "o")
        K.text(c, "？", x + 120, GY10 - 340, 90, "hand", RED)
    return None


ev(j, k_li10, pop_fn(j, k_li10, li10), "wood_low", 0.7)


def myth10(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(10, k_myth))
    if sc <= 0:
        return None
    x, y = cx - 120, cy - 330
    with K.at(c, x, y, -4, sc):
        box(c, 0, 0, 520, 180, NOTE_FILL, ORANGE, 7, 12)
        K.text(c, "梦反着来", 0, 4, 90, "hand", BLACK)
        if T >= tb(10, k_x10):
            g = pop_scale(T - tb(10, k_x10))
            with K.at(c, 0, 0, 0, g):
                c.drawPath(cross(0, 0, 110), wb.marker(RED, 16))
    return None


ev(j, k_myth, myth10, "wood_high", 0.75)
b.hit(j, k_x10, "rim", 0.85, "打叉")


def three10(c, kk, T, cx=cx, cy=cy):
    sc = C.slam_scale(T - tb(10, k_3))
    if sc <= 0:
        return None
    with K.at(c, cx + 270, cy + 60, -4, sc):
        c.drawCircle(0, 0, 190, K.paint("#FFF4D6"))
        c.drawCircle(0, 0, 190, wb.marker(L.ACC, 10))
        K.text(c, "三步", 0, 6, 130, "hand", L.ACC)
    return None


ev(j, k_3, three10, "kick", 0.85)
b.shots[j].shake = [(k_3, 7.0)]

# ================================================================ 屏 11：第一——谁吃了亏，谁得了好处（天平）
cx, cy = R[11]
j = L.scene(11, (cx, cy + 10, Z))
k_h11 = kq(j, wt(18, 0, 0.3), 0)
k_sc11 = nx(j, wt(18, 1, 0.3), k_h11)
k_loss = nx(j, wt(18, 1, 0.8), k_sc11)
k_gain = nx(j, wt(18, 2, 0.6), k_loss)
L.note("第一", "谁吃亏 谁得好处", "吃亏", "得好处")


def h11(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, cy - 500, sc):
        K.text(c, "第一", cx - 380, cy - 500, 70, "hand", L.ACC)
        K.text(c, "谁吃亏 谁得好处", cx + 40, cy - 500, 56, "hand", BLACK)
    return None


ev(j, k_h11, pop_fn(j, k_h11, h11), "wood_low", 0.6)


def scale11(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(11, k_sc11))
    if sc <= 0:
        return None
    tilt = 0.0
    if T >= tb(11, k_gain):
        tilt = -12 * ease_out(clamp01((T - tb(11, k_gain)) / 0.4))
    x, y = cx, cy - 120
    with at_pop(c, x, cy + 300, sc):
        c.drawPath(P((x - 120, cy + 380), (x, cy + 300), (x + 120, cy + 380), close=True), K.paint(WOOD))
        C.line(c, (x, cy + 300), (x, y), "#A9773E", 14)
        a = math.radians(tilt)
        ends = []
        for sg in (-1, 1):
            ex, ey = x + sg * 330 * math.cos(a), y + sg * 330 * math.sin(a)
            ends.append((ex, ey))
        C.line(c, ends[0], ends[1], "#A9773E", 12)
        c.drawCircle(x, y, 18, K.paint("#A9773E"))
        for i, (ex, ey) in enumerate(ends):
            for sg in (-1, 1):
                C.line(c, (ex, ey), (ex + sg * 100, ey + 160), GRAY, 4)
            c.drawPath(P((ex - 120, ey + 160), (ex + 120, ey + 160), (ex + 90, ey + 200), (ex - 90, ey + 200), close=True),
                       K.paint(PAPER_W))
            c.drawPath(P((ex - 120, ey + 160), (ex + 120, ey + 160), (ex + 90, ey + 200), (ex - 90, ey + 200), close=True),
                       wb.marker(BLACK, 5))
            if i == 0 and T >= tb(11, k_loss):
                g = pop_scale(T - tb(11, k_loss))
                with K.at(c, ex, ey + 160, 0, g):
                    woman(c, 0, 0, 0.6, "#D3EDDC", GREEN, "sad", thin=True)
                    K.text(c, "吃亏", 0, 80, 56, "hand", RED)
            if i == 1 and T >= tb(11, k_gain):
                g = pop_scale(T - tb(11, k_gain))
                with K.at(c, ex, ey + 160, 0, g):
                    woman(c, 0, 0, 0.6, "#CFE0F5", BLUE, "smile")
                    K.text(c, "得好处", 0, 80, 56, "hand", GREEN)
    return None


ev(j, k_sc11, scale11, "wood_high", 0.7)
b.hit(j, k_loss, "pop", 0.7, "吃亏的一边")
b.hit(j, k_gain, "ding", 0.8, "得好处的一边")

# ================================================================ 屏 12：第二——梦里的人换成身边的人，看看像谁
cx, cy = R[12]
j = L.scene(12, (cx, cy + 10, Z))
k_h12 = kq(j, wt(19, 0, 0.3), 0)
k_who = nx(j, wt(19, 1, 0.3), k_h12)
k_ph = nx(j, wt(19, 1, 0.8), k_who)
k_hit = nx(j, wt(19, 2, 0.5), k_ph)
L.note("第二", "看看像谁", "梦里的人", "像她")


def h12(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, cy - 500, sc):
        K.text(c, "第二", cx - 380, cy - 500, 70, "hand", L.ACC)
        K.text(c, "看看像谁", cx - 60, cy - 500, 56, "hand", BLACK)
    return None


ev(j, k_h12, pop_fn(j, k_h12, h12), "wood_low", 0.6)


def who12(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(12, k_who))
    x, y = cx, cy - 210
    if not dream_cloud(c, x, y, 520, 400, sc):
        return None
    with at_pop(c, x, y, sc):
        hy = y - 70
        c.drawCircle(x, hy, 50, K.paint(GRAY))
        c.drawPath(P((x - 80, y + 130), (x - 50, hy + 60), (x + 50, hy + 60), (x + 80, y + 130), close=True), K.paint(GRAY))
        K.text(c, "？", x, hy + 6, 70, "hand", PAPER_W)
        K.text(c, "梦里的人", x, y + 160, 44, "hand", NIGHT)
    return None


ev(j, k_who, who12, "pop", 0.7)
FR12 = [(cx - 360, cy + 300), (cx, cy + 300), (cx + 360, cy + 300)]


def frames12(c, kk, T, cx=cx, cy=cy):
    for i, (x, y) in enumerate(FR12):
        g = pop_scale(T - tb(12, k_ph) - i * 0.15)
        if g <= 0:
            continue
        with K.at(c, x, y, (-4, 2, 5)[i], g):
            box(c, 0, 0, 260, 300, PAPER_W, BLACK, 7, 8)
            if i == 0:
                draw_boss(c, 0, 130, 0.75, mood="flat")
            elif i == 1:
                woman(c, 0, 130, 0.75, "#FFE39A", ORANGE, "smile", apron=True)
            else:
                colleague(c, 0, 130, 0.75, "smile")
    if T >= tb(12, k_hit):
        g = pop_scale(T - tb(12, k_hit))
        x, y = FR12[1]
        with K.at(c, x, y, 0, g):
            c.drawOval(skia.Rect.MakeXYWH(-170, -190, 340, 380), wb.marker(RED, 10))
            K.text(c, "像她", 0, 240, 60, "hand", RED)
    for i, (x, y) in enumerate(FR12):
        a = clamp01((T - tb(12, k_ph) - i * 0.15) / 0.3)
        if a > 0:
            c.drawPath(wb.arrow((cx + (i - 1) * 60, cy - 10), (x, y - 170), 0.1, 22), wb.marker(GRAY, 5, a))
    return None


ev(j, k_ph, frames12, "wood_high", 0.7)
b.hit(j, k_hit, "ding", 0.8, "圈出像谁")

# ================================================================ 屏 13：第三——找一句白天没说出口的话，写下来
cx, cy = R[13]
j = L.scene(13, (cx, cy + 10, Z))
k_h13 = kq(j, wt(20, 0, 0.3), 0)
k_zip = nx(j, wt(20, 1, 0.4), k_h13)
k_nb = nx(j, wt(20, 2, 0.2), k_zip)
k_wr = nx(j, wt(20, 2, 0.8), k_nb)
L.note("第三", "没说出口的话", "我想回家吃饭")


def h13(c, sc, T, cx=cx, cy=cy):
    with at_pop(c, cx, cy - 500, sc):
        K.text(c, "第三", cx - 380, cy - 500, 70, "hand", L.ACC)
        K.text(c, "没说出口的话", cx, cy - 500, 56, "hand", BLACK)
    return None


ev(j, k_h13, pop_fn(j, k_h13, h13), "wood_low", 0.6)


def li13(c, sc, T, cx=cx, cy=cy):
    x, y = cx - 330, cy + 440
    with at_pop(c, x, y, sc):
        writing = T >= tb(13, k_wr)
        draw_li(c, x, y, 0.95, "flat", rh=(x + 110, y - 200) if writing else None)
        hy = y - 290 * 0.95
        if not writing:
            C.line(c, (x - 26, hy + 20), (x + 26, hy + 20), GRAY, 12)
            for i in range(5):
                C.line(c, (x - 20 + i * 10, hy + 12), (x - 20 + i * 10, hy + 28), BLACK, 3)
        dream_cloud(c, x + 40, hy - 170, 200, 120, 1.0, tail_to=(x + 10, hy - 50))
        c.drawPath(C.heart_path(x + 40, hy - 170, 30), K.paint("#F6C3BE"))
        c.drawPath(C.heart_path(x + 40, hy - 170, 30), wb.marker(RED, 5))
    return None


ev(j, k_zip, pop_fn(j, k_zip, li13), "wood_high", 0.7)


def nb13(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(13, k_nb))
    if sc <= 0:
        return None
    x, y = cx + 170, cy - 30
    with K.at(c, x, y, 3, sc):
        box(c, 0, 0, 560, 480, NOTE_FILL, ORANGE, 7, 10)
        for r in range(4):
            C.line(c, (-230, -120 + r * 90), (230, -120 + r * 90), "#E8CF7A", 4)
        if T >= tb(13, k_wr):
            s_ = "我想回家吃饭"
            g = clamp01((T - tb(13, k_wr)) / 0.8)
            n = max(1, int(math.ceil(len(s_) * g)))
            K.text(c, s_[:n], -230, -30, 70, "hand", RED, 1.0, "left")
            if g >= 1:
                A.pen(c, 200, 80, -40, 1.0)
    return None


ev(j, k_nb, nb13, "pop", 0.7)
b.hit(j, k_wr, "shaker", 0.7, "写下来")

# ================================================================ 屏 14：说出口的心里话，用不着在梦里化妆——面具掉下来
cx, cy = R[14]
j = L.scene(14, (cx, cy + 10, Z))
k_li14 = 0
k_drop = nx(j, wt(21, 0, 0.6), k_li14)
k_say14 = nx(j, wt(21, 1, 0.4), k_drop)
GY14 = cy + 440
L.note("心里话")


def li14(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(14, k_li14))
    if sc <= 0:
        return None
    x = cx - 200
    hy = GY14 - 290 * 1.1
    with at_pop(c, x, GY14, sc):
        off = T >= tb(14, k_drop)
        draw_li(c, x, GY14, 1.1, "smile" if off else "flat",
                rh=(x + 120, hy + 60) if not off else (x + 130, hy + 20))
        if not off:
            mask(c, x, hy - 6, 0.6, 0)
        else:
            f = ease_in_out(clamp01((T - tb(14, k_drop)) / 0.5))
            mask(c, lerp(x, x - 240, f), lerp(hy - 6, GY14 - 40, f), 0.6, lerp(0, -70, f))
    return None


ev(j, k_li14, li14, "wood_low", 0.7)
b.hit(j, k_drop, "clap", 0.85, "面具掉下来")
b.shots[j].shake = [(k_drop, 5.0)]


def say14(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(14, k_say14))
    if sc <= 0:
        return None
    x, y = cx + 230, cy - 230
    with K.at(c, x, y, 0, sc):
        c.drawRoundRect(skia.Rect.MakeXYWH(-260, -150, 520, 300), 60, 60, K.paint(PAPER_W))
        c.drawPath(wb.bubble(0, 0, 520, 300, -1), wb.marker(BLACK, 8))
        c.drawPath(C.heart_path(0, -30, 60), K.paint("#F6C3BE"))
        c.drawPath(C.heart_path(0, -30, 60), wb.marker(RED, 6))
        K.text(c, "心里话", 0, 80, 64, "hand", RED)
    sparkle(c, x, y, T - tb(14, k_say14), YELLOW, 10, 180, 280)
    return None


ev(j, k_say14, say14, "ding", 0.85)

# ================================================================ 屏 15：评论区——“梦见请客没请成”；睡得轻松；下一讲预告
cx, cy = R[15]
j = L.scene(15, (cx, cy + 10, Z))
k_box = kq(j, wt(22, 0, 0.4), 0)
k_type = nx(j, wt(23, 0, 0.5), k_box)
k_likes = nx(j, wt(23, 1, 0.5), k_type)
k_rest = nx(j, wt(24, 1, 0.3), k_likes)
k_n = nx(j, wt(25, 0, 0.1), k_rest)
L.note("评论区", "梦见请客没请成", "发送", "我来猜", "睡得轻松")


def input15(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(15, k_box))
    if sc <= 0:
        return None
    x, y, w = cx, cy - 420, 860
    with at_pop(c, x, y, sc):
        box(c, x, y, w, 150, PAPER_W, BLACK, 6, 30)
        K.text(c, "评论区", x - w / 2 + 90, y - 110, 44, "sans_medium", GRAY)
        if T >= tb(15, k_type):
            s_ = "梦见请客没请成"
            g = clamp01((T - tb(15, k_type)) / 0.8)
            n = max(1, int(math.ceil(len(s_) * g)))
            K.text(c, s_[:n], x - w / 2 + 40, y + 2, 58, "hand", BLACK, 1.0, "left")
        K.rr(c, x + w / 2 - 85, y, 130, 80, 20, L.ACC)
        K.text(c, "发送", x + w / 2 - 85, y, 42, "sans_medium", "#FFFFFF")
        for i in range(4):
            g = pop_scale(T - tb(15, k_likes) - i * 0.15)
            if g > 0:
                with K.at(c, x - 300 + i * 200, y + 140, 0, g):
                    K.rr(c, 0, 0, 170, 64, 30, "#FFF4D6")
                    K.text(c, "我来猜", 0, 2, 40, "hand", L.ACC)
    return None


ev(j, k_box, input15, "wood_high", 0.7)
b.hit(j, k_type, "pop", 0.6, "打字")
b.hit(j, k_likes, "clap", 0.75, "大家来猜")


def rest15(c, kk, T, cx=cx, cy=cy):
    sc = pop_scale(T - tb(15, k_rest))
    if sc <= 0:
        return None
    x, y = cx - 260, cy + 260
    with at_pop(c, x + 260, y, sc):
        bed(c, x, y, 520)
        sleeper(c, x + 230, y - 20, 0.75, T, None, "smile")
        moon(c, x + 600, y - 280, 60)
        for i in range(3):
            f = ((T - tb(15, k_rest)) * 0.7 + i / 3) % 1
            K.text(c, "Z", x + 40 + f * 60, y - 150 - f * 160, 50 + i * 10, "hand", NIGHT, 1 - f)
        K.text(c, "睡得轻松", x + 260, y - 260, 64, "hand", GREEN)
    return None


L.note("Z")
ev(j, k_rest, rest15, "ding", 0.8)
b.move(j, k_n, (cx, cy + 420, Z), dur=1.0)
KT.next_card(j, k_n + 1, "怎么会梦见八百年没想起的人？", cx, cy + 860)

# ================================================================ 收尾
L.finish(cover_shot=2, square_shot=5, notes=NOTES)
L.export(globals())
