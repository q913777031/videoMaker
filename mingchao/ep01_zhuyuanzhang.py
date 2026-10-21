"""01 朱元璋：一个连父母都埋不起的穷孩子，怎么当上了皇帝？

开头用问题钩子（穷孩子 → 皇帝？），中段按《明史·太祖本纪》的时间线走，结尾两镜是高光：1368 年称帝，回扣 24 年前的那块坟地。
"""

import math

import skia

from engine.gfx import clamp01, ease_in_out, ease_out, lerp

from adler import kit as K
from adler.core import Big, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot
from adler.ep06_tasks import joints

ACC = "#A8322A"          # 朱红
GOLD = "#C9A04A"
ROBE = "#D8A62E"         # 龙袍黄
RAG = "#8C7A62"          # 粗布
GROUND = 1130
SERIES = dict(series="明朝皇帝", series_count=16, file_prefix="明朝")
REFS = ["《明史·太祖本纪》（张廷玉等，清）",
        "当年明月《明朝那些事儿》第一部（叙事参考，非引用）"]


def ground(g):
    K.ground(g.c, GROUND)


# ---------------------------------------------------------------- 人物与道具

def hat(c, hx, hy, s, color=K.INK):
    """翼善冠（简化）：圆顶乌纱 + 脑后两只上翘的“翼”。hx, hy 为头心。"""
    r = 0.15 * s
    for sgn in (-1, 1):
        K.rr(c, hx + sgn * r * 0.9, hy - r * 1.05, r * 0.7, r * 0.42, r * 0.2, color)
    p = skia.Path()
    p.addArc(skia.Rect.MakeLTRB(hx - r * 1.02, hy - r * 1.55, hx + r * 1.02, hy + r * 0.3), 180, 180)
    p.close()
    c.drawPath(p, K.paint(color))
    K.rr(c, hx, hy - r * 0.62, r * 2.1, r * 0.28, r * 0.1, color)


def emperor(c, x, y, s, pose="stand", face=1, mood="calm", alpha=1.0):
    K.figure(c, x, y, s, pose, ROBE, alpha=alpha, face=face, mood=mood)
    j = joints(s, pose, face)
    hat(c, x + j["head"][0], y + j["head"][1], s)


def throne(c, x, y, s, alpha=1.0, glow=0.0):
    """宝座：(x, y) 为底边中点。"""
    if glow > 0:
        K.spotlight(c, x, y - s * 0.6, s * 1.2, GOLD, 0.5 * glow)
    with K.fade(c, alpha):
        with K.paper(c, 1, 0.9):
            K.rr(c, x, y - s * 0.75, s * 0.9, s * 0.8, s * 0.08, K.shade(ACC, 0.1))
            K.rr(c, x, y - s * 0.32, s * 1.1, s * 0.16, s * 0.05, K.shade(ACC, 0.25))
            for sgn in (-1, 1):
                K.rr(c, x + sgn * s * 0.48, y - s * 0.12, s * 0.1, s * 0.26, s * 0.03, K.shade(ACC, 0.3))
        K.rr(c, x, y - s * 0.75, s * 0.6, s * 0.55, s * 0.05, GOLD)
        K.dot(c, x, y - s * 0.78, s * 0.17, K.shade(GOLD, 0.15))
        K.ring(c, x, y - s * 0.78, s * 0.17, ACC, max(2, s * 0.015))
        K.text(c, "龙", x, y - s * 0.775, s * 0.17, "serif_black", ACC)


def tablet(c, x, y, s, text, alpha=1.0):
    """牌位。"""
    with K.fade(c, alpha):
        with K.paper(c, 1, 0.8):
            K.rr(c, x, y + s * 0.42, s * 0.62, s * 0.16, s * 0.04, K.DARK)
            K.rr(c, x, y, s * 0.42, s * 0.8, s * 0.12, "#3B2A22")
        K.rr(c, x, y, s * 0.3, s * 0.64, s * 0.08, "#F2E6CC")
        K.text(c, text, x, y, s * 0.24, "serif_black", "#3B2A22")


def candle(c, x, y, s, lit=1.0, t=0.0):
    K.rr(c, x, y, s * 0.18, s * 0.5, s * 0.04, "#F4ECDD")
    if lit > 0:
        f = 1 + 0.08 * math.sin(t * 12 + x)
        K.spotlight(c, x, y - s * 0.38, s * 0.5 * lit, "#FFC66B", 0.4 * lit)
        K.dot(c, x, y - s * 0.36, s * 0.08 * f * lit, "#F29A3A", lit)


def seal(c, x, y, s, text="洪武", k=1.0, rot=-6):
    """朱红方印：k 为盖下进度（1.6 倍 → 1 倍）。"""
    if k <= 0:
        return
    sc = 1 + 0.6 * (1 - ease_out(clamp01(k)))
    a = clamp01(k * 3)
    with K.at(c, x, y, rot, sc):
        K.rr(c, 0, 0, s, s, s * 0.08, ACC, a)
        K.rr_stroke(c, 0, 0, s * 0.86, s * 0.86, s * 0.05, "#F6E7D6", s * 0.03, a)
        for i, ch in enumerate(text):
            K.text(c, ch, 0, (i - (len(text) - 1) / 2) * s * 0.36, s * 0.32, "serif_black", "#F6E7D6", a)


def mound(c, x, y, s, alpha=1.0):
    """小坟包。"""
    with K.fade(c, alpha):
        p = skia.Path()
        p.addArc(skia.Rect.MakeLTRB(x - s, y - s * 0.7, x + s, y + s * 0.7), 180, 180)
        p.close()
        c.drawPath(p, K.paint("#9C8A6A"))
        K.rr(c, x, y - s * 0.5, s * 0.22, s * 0.5, s * 0.04, "#6B5A44")


# ---------------------------------------------------------------- 1 钩子

def hook(c, g, t, d):
    """左：破衣少年站在小坟包旁；右：宝座。第 6 拍宝座发光，中间问号。"""
    mound(c, -260, 330, 90)
    K.figure(c, -380, 330, 300, "sad", RAG, mood="sad", hair="short", lift=0.8)
    k = clamp01(g.since(3) / 0.5)
    throne(c, 290, 330, 360, k, clamp01(g.since(6) / 0.4))
    kk = clamp01(g.since(8) / 0.3)
    if kk > 0:
        K.text(c, "？", 0, 60, 150, "serif_black", ACC, kk)


# ---------------------------------------------------------------- 2 四级台阶

STEPS = ["放牛", "出家", "讨饭", "皇帝"]


def stairs_up(c, g, t, d):
    sw, sh = 210, 110
    x0, y0 = -440, 330
    for i, lab in enumerate(STEPS):
        k = clamp01(g.since(i * 2) / 0.35)
        if k <= 0:
            continue
        x = x0 + i * sw
        top = y0 - (i + 1) * sh
        with K.paper(c, k, 0.8):
            K.rr(c, x + sw / 2, (top + y0) / 2, sw - 6, y0 - top, 10, K.mix(ACC if i == 3 else RAG, K.PAPER, 0.55))
        K.text(c, lab, x + sw / 2, top + 40, 40, "serif_black", ACC if i == 3 else K.INK, k)
    step = min(3, int(max(0, g.since(0)) // (g.b(2) - g.b(0)))) if g.since(0) >= 0 else 0
    u = clamp01((g.since(step * 2)) / 0.45)
    prev = max(0, step - 1)
    fx = lerp(x0 + prev * sw + sw / 2, x0 + step * sw + sw / 2, ease_in_out(u))
    fy = lerp(y0 - (prev + 1) * sh, y0 - (step + 1) * sh, ease_in_out(u))
    if step == 3 and u > 0.5:
        emperor(c, fx, fy, 200, "cheer", 1, "happy")
    else:
        K.figure(c, fx, fy, 200, K.walk(u * 3, 1.0) if u < 1 else "stand", RAG, mood="smile", hair="short")


# ---------------------------------------------------------------- 4 drop

def drop_seal(c, g, t, d):
    seal(c, 0, 0, 230, "洪武", clamp01(g.since(6) / 0.25))


# ---------------------------------------------------------------- 5 天灾

def disaster(c, g, t, d):
    """龟裂的土地 + 烈日 + 蝗虫群；第 8 拍“疫”字压下。"""
    with K.paper(c, 1, 0.8):
        K.rr(c, 0, 220, 900, 260, 20, "#C9A97A")
    rng = [(-380, 140, -260, 300), (-200, 120, -120, 310), (-20, 140, 60, 300), (150, 120, 260, 310), (300, 140, 400, 290)]
    for a, b, cc, dd in rng:
        p = skia.Path()
        p.moveTo(a, b)
        p.lineTo((a + cc) / 2 + 20, (b + dd) / 2)
        p.lineTo(cc, dd)
        c.drawPath(p, K.paint("#8C6A44", 1, 6))
    K.icon(c, "sun", -280, -230, 180, K.RED, 1, 0.5, g.t * 10, 1, 1, K.GOLD)
    k = clamp01(g.since(4) / 0.4)
    for i in range(26):
        u = (g.t * 0.35 + i / 26) % 1
        x = lerp(500, -500, u) + 40 * math.sin(i * 1.7 + g.t * 3)
        y = -160 + 120 * math.sin(i * 2.3) + 18 * math.sin(g.t * 6 + i)
        K.rr(c, x, y, 26, 10, 5, "#4A4A2E", k)
    kk = clamp01(g.since(8) / 0.25)
    if kk > 0:
        with K.at(c, 260, -180, -8, 1 + 0.5 * (1 - ease_out(kk))):
            K.text(c, "疫", 0, 0, 180, "serif_black", ACC, kk)


# ---------------------------------------------------------------- 6 三块牌位

def tablets(c, g, t, d):
    for i, (who, b) in enumerate((("父", 2), ("兄", 5), ("母", 8))):
        k = clamp01(g.since(b) / 0.35)
        x = -260 + i * 260
        if k > 0:
            tablet(c, x, 0, 260, who, k)
        candle(c, x, 230, 120, clamp01(g.since(b) / 0.3), g.t)
    kk = clamp01(g.since(10) / 0.4)
    if kk > 0:
        K.text(c, "半月之间", 0, -260, 44, "serif_black", K.INK2, kk)


# ---------------------------------------------------------------- 7 一块地

def land(c, g, t, d):
    k = clamp01(g.since(4) / 0.5)
    if k > 0:
        p = skia.Path()
        p.addRect(skia.Rect.MakeXYWH(-130, 250, 260 * k, 70))
        c.drawPath(p, K.paint("#B89A6A", 0.9))
        dash = K.paint(ACC, 1, 5)
        dash.setPathEffect(skia.DashPathEffect.Make([14, 10], 0))
        c.drawRect(skia.Rect.MakeXYWH(-130, 250, 260 * k, 70), dash)
    mk = clamp01(g.since(8) / 0.4)
    if mk > 0:
        mound(c, 0, 285, 80, mk)


# ---------------------------------------------------------------- 8 皇觉寺

def temple(c, g, t, d):
    with K.paper(c, 1, 0.9):
        K.rr(c, 0, 80, 560, 300, 8, "#B7493B")
        K.poly(c, [(-360, -60), (360, -60), (300, -150), (-300, -150)], "#3B3F4E")
        K.poly(c, [(-400, -60), (-360, -40), (360, -40), (400, -60)], "#3B3F4E")
    K.rr(c, 0, 140, 160, 180, 6, "#5A2A22")
    K.rr(c, 0, -100, 220, 56, 6, GOLD)
    K.text(c, "皇觉寺", 0, -100, 34, "serif_black", "#5A2A22")


# ---------------------------------------------------------------- 9 讨饭路

# 按经纬度大致换算的相对位置（x = (经度 − 115) × 170，y = −(纬度 − 32.5) × 170），起点为濠州钟离
START = ("濠州", 425, -68)
PLACES = [("合肥", 393, 119), ("光州", 0, 68), ("固始", 119, 51), ("汝州", -374, -289), ("颍州", 136, -68)]


def begging(c, g, t, d):
    pts = [START[1:]] + [(x, y) for _, x, y in PLACES]
    K.dot(c, START[1], START[2], 14, K.INK)
    K.text(c, START[0], START[1] - 20, START[2] - 34, 32, "serif_black", K.INK2, 1, "right")
    K.text(c, "路线示意", -420, 300, 26, "sans_medium", K.INK3, 1, "left")
    p = skia.Path()
    p.moveTo(*pts[0])
    for a, b in zip(pts, pts[1:]):
        p.quadTo(a[0] + 60, (a[1] + b[1]) / 2 + 40, b[0], b[1])
    dash = K.paint(K.INK3, 1, 6)
    dash.setPathEffect(skia.DashPathEffect.Make([16, 12], 0))
    c.drawPath(p, dash)
    for i, (name, x, y) in enumerate(PLACES):
        k = clamp01(g.since(1 + i * 1.5) / 0.3)
        if k > 0:
            K.dot(c, x, y, 12, ACC, k)
            K.text(c, name, x + 22, y - 26, 32, "serif_black", K.INK, k, "left")
    K.text(c, "约三年", -300, 180, 44, "serif_black", ACC, clamp01(g.since(8) / 0.3))


# ---------------------------------------------------------------- 10 红巾军

def banners(c, g, t, d):
    for i in range(5):
        x = -360 + i * 180
        wave = 10 * math.sin(g.t * 4 + i)
        k = clamp01(g.since(i * 0.5) / 0.3)
        if k <= 0:
            continue
        K.seg(c, x, 330, x, -60, "#6B4A2E", 10, k)
        p = skia.Path()
        p.moveTo(x, -60)
        p.cubicTo(x + 60, -80 + wave, x + 110, -40 - wave, x + 150, -60 + wave)
        p.lineTo(x + 150, 30 + wave)
        p.cubicTo(x + 110, 50 - wave, x + 60, 10 + wave, x, 30)
        p.close()
        c.drawPath(p, K.paint("#C8322A", k))
    K.crowd(c, 0, 330, 7, 230, g.t, (RAG, "#7A6A55", "#9C8A6A", "#6E5E48"), 1, 780, 7)


# ---------------------------------------------------------------- 12 鄱阳湖

def poyang(c, g, t, d):
    """湖面上两支船队；第 4 拍起火船冲向敌阵，第 10 拍敌方主舰中箭、标签变灰。"""
    with K.paper(c, 1, 0.6):
        K.rr(c, 0, 60, 940, 520, 200, "#9EC3D6")
    for i in range(5):
        y = -120 + i * 90
        K.seg(c, -420, y, 420, y, "#B9D6E4", 4)

    def boat(x, y, col, s=1.0, fire=0.0):
        K.poly(c, [(x - 60 * s, y), (x + 60 * s, y), (x + 40 * s, y + 26 * s), (x - 40 * s, y + 26 * s)], col)
        K.seg(c, x, y, x, y - 70 * s, "#5A4632", 5)
        K.poly(c, [(x, y - 66 * s), (x + 40 * s, y - 36 * s), (x, y - 20 * s)], "#F2E6CC")
        if fire > 0:
            for j in range(3):
                fy = y - 30 * s - 30 * fire * (1 + 0.3 * math.sin(g.t * 10 + j))
                K.dot(c, x - 20 * s + j * 20 * s, fy, 18 * s * fire, "#F29A3A", 0.9)
                K.dot(c, x - 20 * s + j * 20 * s, fy + 6, 10 * s * fire, "#F6D34A", 0.9)

    burn = clamp01(g.since(7) / 0.6)
    for i in range(4):
        boat(240 + (i % 2) * 100, -80 + i * 90, "#6E6E6E", 0.9, burn if i < 3 else 0)
    adv = ease_in_out(clamp01(g.since(4) / max(0.1, g.b(7) - g.b(4))))
    for i in range(3):
        boat(lerp(-300, 120, adv) + (i % 2) * 40, -40 + i * 110, "#5A2A22", 0.8, 1.0)
    for i in range(3):
        boat(-380, -60 + i * 110, ACC, 0.9)
    K.text(c, "朱元璋", -380, 300, 32, "serif_black", ACC)
    k = clamp01(g.since(10) / 0.4)
    K.text(c, "陈友谅", 300, 300, 32, "serif_black", K.mix(K.INK, K.INK3, k))
    if k > 0:
        K.arrow(c, (40, -260), (280, -110), K.INK, 6, 1, k, 0.1, 22)


# ---------------------------------------------------------------- 13 高光：称帝

def coronation(c, g, t, d):
    k = clamp01(g.since(0) / 0.5)
    for i in range(16):
        a = math.radians(i * 22.5 + g.t * 6)
        K.seg(c, 0, -60, 700 * math.cos(a), -60 + 700 * math.sin(a), K.tint(GOLD, 0.5), 18, 0.35 * k)
    throne(c, 0, 330, 420, 1, 0.8 + 0.2 * math.sin(g.t * 3))
    emperor(c, 0, 330 - 4, 330, "sit", 1, "calm")
    seal(c, 330, -230, 170, "大明", clamp01(g.since(4) / 0.25))
    K.confetti(c, 0, -100, g.since(4), (GOLD, ACC, "#F6D34A"), 40, 5, 1.4)
    kk = clamp01(g.since(8) / 0.4)
    if kk > 0:
        K.pill(c, -300, -230, "洪武元年", 40, ACC, K.PAPER, kk)


# ---------------------------------------------------------------- 14 高光：回扣

def contrast(c, g, t, d):
    """左：1344 年，少年与小坟包（灰）；右：1368 年，皇帝与宝座（金）；中间箭头写“24 年”。"""
    a = clamp01(g.since(0) / 0.4)
    with K.fade(c, a):
        K.rr(c, -250, 60, 420, 560, 30, "#E3DDD2")
        mound(c, -200, 260, 70)
        K.figure(c, -320, 260, 220, "sad", "#8F8F8F", mood="sad", hair="short", lift=0.6)
        K.text(c, "1344", -250, -150, 56, "serif_black", K.INK3)
    b = clamp01(g.since(2) / 0.4)
    if b > 0:
        with K.fade(c, b):
            K.spotlight(c, 250, 60, 320, GOLD, 0.45)
            K.rr(c, 250, 60, 420, 560, 30, K.tint(GOLD, 0.65))
            throne(c, 250, 280, 260, 1, 0.5)
            emperor(c, 250, 276, 210, "sit")
            K.text(c, "1368", 250, -150, 56, "serif_black", ACC)
    k = clamp01(g.since(4) / 0.4)
    if k > 0:
        K.arrow(c, (-30, 60), (40, 60), ACC, 10, k, k, 0, 26)
        K.pill(c, 5, -10, "24 年", 34, ACC, K.PAPER, k)


def build() -> Episode:
    shots = [
        Shot(3, "一个连父母都埋不起的穷孩子，|后来当上了皇帝？", "情境演绎", [
            Custom(hook, x=540, y=800, at=0, enter="none"),
        ], draw=ground, hits=[(0, "wood_low", 0.7, "少年与坟包"), (3, "wood_high", 0.7, "宝座出现"),
                              (6, "rim", 0.9, "宝座发光"), (8, "bongo_high", 0.8, "大问号")],
            note="左边破衣少年站在小坟包旁，右边宝座浮现、发光，中间一个朱红大问号"),
        Shot(3, "放牛、出家、讨饭，|最后坐上了皇位。", "情境演绎", [
            Custom(stairs_up, x=540, y=800, at=0, enter="none"),
        ], hits=[(0, "wood_low", 0.7, "放牛"), (2, "wood_high", 0.7, "出家"), (4, "bongo_low", 0.7, "讨饭"),
                 (6, "rim", 0.9, "皇帝：换上龙袍")],
            note="四级台阶“放牛、出家、讨饭、皇帝”，少年一级级往上走，最后一级换上黄袍和乌纱"),
        Shot(2, "他到底是怎么做到的？", "情境演绎", [
            Fig(540, GROUND, 360, at=0, enter="none", pose="shrug", mood="surprised", hair="short", color=RAG),
            Icon("question", 760, 640, 150, color=ACC, at=2, enter="pop", sfx="bongo_low", note="大问号"),
        ], draw=ground, note="少年摊手，头顶弹出问号"),
        Shot(3, "明朝第一位皇帝：|朱元璋。", "人物", [
            Big("朱元璋", 540, 520, 160, at=0, sfx="kick", sub="明太祖 · 1328–1398", note="名字落版（音乐 drop）"),
            Custom(drop_seal, x=540, y=930, at=0, enter="none"),
        ], hits=[(6, "frame", 0.9, "“洪武”朱印盖下")], note="drop 处“朱元璋”砸下；第 6 拍“洪武”朱红方印盖下"),
        Shot(3, "1344 年，淮河一带|旱灾、蝗灾、瘟疫接连来。", "史料记载", [
            Custom(disaster, x=540, y=780, at=0, enter="fade"),
        ], hits=[(4, "shaker", 0.8, "蝗虫飞过"), (8, "tom", 0.9, "“疫”字压下")],
            note="龟裂的土地、烈日，蝗虫群飞过，第 8 拍朱红“疫”字压下"),
        Shot(3, "半个月里，父亲、大哥、|母亲相继去世。", "史料记载", [
            Custom(tablets, x=540, y=760, at=0, enter="none"),
        ], hits=[(2, "wood_low", 0.7, "父"), (5, "wood_low", 0.7, "兄"), (8, "wood_low", 0.7, "母")],
            note="三块牌位“父、兄、母”按拍立起，前面的蜡烛一支支点亮"),
        Shot(3, "穷得没有地下葬，|邻居刘继祖给了一块地。", "史料记载", [
            Fig(330, GROUND, 330, at=0, pose="crouch", mood="sad", hair="short", color=RAG),
            Fig(780, GROUND, 340, at=1, mood="calm", color=K.OTHER, face=-1,
                moves=[(3, dict(pose="give", sfx="wood_high", note="刘继祖伸手指向一块地"))]),
            Label("刘继祖", 780, 680, 32, at=2, fill=K.INK2),
            Custom(land, x=540, y=800, at=0, enter="none"),
        ], draw=ground, hits=[(8, "tom", 0.7, "坟包隆起")],
            note="少年蹲着，邻居刘继祖指出一块地，虚线圈出地块，第 8 拍坟包隆起"),
        Shot(2, "十七岁，他进皇觉寺|当了小和尚。", "史料记载", [
            Custom(temple, x=540, y=760, at=0, enter="pop", sfx="wood_low", note="皇觉寺"),
            Fig(540, GROUND, 260, at=1, mood="calm", color="#8A6A3A", sfx="wood_high", note="小和尚"),
        ], draw=ground, text_beat=0, note="皇觉寺门前站着剃了头的小和尚"),
        Shot(2, "寺里也断了粮，|他四处讨饭约三年。", "史料记载", [
            Custom(begging, x=540, y=760, at=0, enter="fade"),
        ], hits=[(1, "wood_high", 0.6, "合肥"), (4, "wood_low", 0.6, "固始"), (7, "bongo_high", 0.6, "颍州")],
            text_beat=0, note="虚线路线从濠州出发，依次经过合肥、光州、固始、汝州、颍州（按经纬度大致定位，示意），标“约三年”"),
        Shot(3, "1352 年，他投奔|郭子兴的红巾军。", "史料记载", [
            Custom(banners, x=540, y=800, at=0, enter="none"),
            Label("郭子兴", 540, 520, 34, at=4, fill=ACC, sfx="wood_high", note="郭子兴"),
        ], hits=[(0, "wood_low", 0.6, "第一面红旗"), (2, "wood_low", 0.6, "红旗林立")],
            note="一排红旗按拍竖起、飘动，下方一队士兵（红巾军）"),
        Shot(3, "他听进了九个字：|高筑墙，广积粮，缓称王。", "史料记载", [
            Card("高筑墙", 230, 800, 56, at=2, enter="drop", sfx="tom", note="高筑墙", accent=ACC),
            Card("广积粮", 540, 800, 56, at=5, enter="drop", sfx="tom", note="广积粮", accent=ACC),
            Card("缓称王", 850, 800, 56, at=8, enter="drop", sfx="tom", note="缓称王", accent=ACC),
            Txt("谋士朱升献策", 540, 1000, 34, at=10, font="sans_medium", color=K.INK2),
        ], note="三张字卡按拍落下：高筑墙、广积粮、缓称王"),
        Shot(4, "1363 年鄱阳湖大战，|劲敌陈友谅中箭身亡。", "史料记载", [
            Custom(poyang, x=540, y=780, at=0, enter="fade"),
        ], hits=[(4, "shaker", 0.8, "火船冲出"), (7, "frame", 0.9, "敌船起火"), (10, "rim", 0.9, "陈友谅中箭")],
            note="湖面两支船队：朱元璋的火船冲入陈友谅船阵，敌船起火；第 10 拍箭矢飞向“陈友谅”，名字变灰"),
        Shot(4, "1368 年正月，他在应天称帝，|国号大明。", "高光时刻", [
            Custom(coronation, x=540, y=780, at=0, enter="fade"),
        ], hits=[(0, "cymbal", 0.6, "金光铺开"), (4, "kick", 0.8, "“大明”印盖下"), (8, "wood_high", 0.8, "“洪武元年”")],
            note="金色光芒中，身穿黄袍、头戴乌纱的朱元璋坐上宝座；第 4 拍“大明”朱印盖下、彩纸飞散"),
        Shot(2, "二十四年前，|他连埋父母的地都没有。", "高光时刻", [
            Custom(contrast, x=540, y=780, at=0, enter="none"),
        ], hits=[(0, "wood_low", 0.7, "1344：坟包与少年"), (2, "rim", 0.9, "1368：宝座与皇帝"), (4, "clap", 0.8, "24 年")],
            text_beat=0, note="左右对照：1344 年灰色画面里的少年与小坟包，1368 年金色画面里的皇帝与宝座，中间“24 年”"),
        end_shot(REFS, "02 建文帝：一位皇帝，怎么会下落不明？"),
    ]
    return Episode(1, "zhuyuanzhang", "朱元璋", "一个连父母都埋不起的穷孩子，怎么当上了皇帝？", ACC, shots, refs=REFS,
                   publish_title="放牛娃、和尚、乞丐，怎么当上了皇帝？｜明朝皇帝01 朱元璋",
                   hashtags="#朱元璋 #明朝 #明朝那些事儿 #历史 #洪武",
                   cover_title="放牛娃、和尚、乞丐，|怎么当上了【皇帝】？", cover_sub="明朝皇帝 · 朱元璋",
                   cover_shot=12, cover_t=5.0,
                   notes=[
                       "《明史·太祖本纪》：“至正四年，旱蝗，大饥疫。太祖时年十七，父母兄相继殁，贫不克葬。里人刘继祖与之地，乃克葬。"
                       "孤无所依，乃入皇觉寺为僧。逾月，游食合肥。道病……历光、固、汝、颍诸州三年，复还寺。”"
                       "片中 1344 年即至正四年；也有资料记为 1343 年。“十七岁”为虚岁。",
                       "父亲、长兄、母亲在半个月左右相继去世，见《明太祖实录》及朱元璋《御制皇陵碑》的追述。",
                       "至正十二年（1352）投郭子兴；至正十六年（1356）克集庆，改应天府；朱升“高筑墙，广积粮，缓称王”之策约在 1358 年前后。",
                       "至正二十三年（1363）鄱阳湖之战，陈友谅中流矢而死（《明史》）；火攻、船队画面为示意，不表示实际兵力与阵形。",
                       "洪武元年（1368）正月初四在应天即皇帝位，国号大明；同年八月徐达攻入大都，元顺帝北走。",
                       "叙事节奏参考当年明月《明朝那些事儿》，史实以《明史》为准，未引用原书文字。",
                       "人物服饰、宝座、印章为简化示意。",
                   ], **SERIES).build()
