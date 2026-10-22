"""第 01 讲 · 心即理：道理都懂，为什么还是过不好？（分镜）

每个场景对应文案若干句；画面锚定到“读到某个词”的时刻，打击乐与撞击帧对齐。
"""

import math

import numpy as np
import skia

from engine import gfx

from . import art, hanzi, ink
from .video import Ep, InkVideo, env, word

E = Ep("ep01")
TITLE = "道理都懂，为什么还是过不好？"
HEADER = "第一讲 · 心即理"
P = gfx.prog
EO = gfx.ease_out
CALLI = "道理都懂为什么还是过不好格物你缺的不是心即理反从心出发根知行合一今日功课我为什么想要它"


def _fade(a, x):
    return max(0.0, min(1.0, a)) * x


def backdrop(c, t, a, shift=0.0, far=0.28, near=0.45, y=560):
    """远山两层 + 云雾（古代场景通用）。"""
    ink.mountains(c, y, 360, 3, alpha=far * a, blur=6, shift=shift * 0.4 + t * 2)
    ink.mist(c, t, y + 280, 0.5 * a, seed=1)
    ink.mountains(c, y + 140, 380, 5, alpha=near * a, shift=shift * 0.8 + t * 4)
    ink.mist(c, t, y + 420, 0.45 * a, seed=2)


def night(c, a, y0=320, y1=1300, tone=(70, 84, 98), alpha=0.22):
    """今人深夜：冷灰淡墨夜色块。"""
    c.drawRoundRect(skia.Rect.MakeLTRB(70, y0, gfx.W - 70, y1), 30, 30, ink.paint(tone, alpha * a, blur=24))


def divider(c, y, a, p=1.0):
    ink.brush_path(c, [(120, y), (gfx.W - 120, y + 6)], 7, p=p, alpha=0.6 * a)
    ink.label(c, "今", 92, y - 40, 34, tone=ink.CINNABAR, alpha=a * 0.9)
    ink.label(c, "古", 92, y + 52, 34, tone=ink.CINNABAR, alpha=a * 0.9)


def bamboo_grove(c, x0, y, t, a, n=6, h=560, seed=0, grow=1.0):
    for k in range(n):
        art.bamboo(c, x0 + k * 52 + (k % 2) * 14, y + (k % 3) * 10, h - (k % 3) * 60, seed + k, t, a * (0.6 + 0.4 * (k % 2)),
                   width=18 + (k % 2) * 6, grow=grow)


def counter_text(c, text, x, y, size, t0, t, tone=ink.INK, a=1.0):
    k = P(t, t0, 0.18)
    if k <= 0:
        return
    sc = 1.3 - 0.3 * EO(k)
    c.save()
    c.translate(x, y)
    c.scale(sc, sc)
    ink.label(c, text, 0, 0, size, tone=tone, alpha=a * k)
    c.restore()


# ================================================================ 第 1 节 · 钩子

def d_hook_fav(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    night(c, a)
    art.modern_bed_phone(c, 400, 1180, 1.25, a, glow=1.0, t=t)
    inner = art.phone(c, 820, 700, 0.62, a, glow=0.6)
    t300 = word(ctx, 0, "三百篇")
    n = int(300 * EO(P(t, ctx.cue(0), max(0.3, t300 - ctx.cue(0) + 0.3))))
    ink.label(c, f"收藏 {n}", inner.centerX(), inner.top() + 40, 30, alpha=a)
    for k in range(5):
        art.fav_card(c, inner.centerX(), inner.top() + 110 + k * 62, inner.width() - 26,
                     ["自律的十个方法", "高效人士的7个习惯", "早起改变人生", "30天读完50本书", "一张表管好时间"][k],
                     alpha=a * P(t, ctx.cue(0) + k * 0.15, 0.25), star=True)
    t50 = word(ctx, 0, "五十本")
    counter_text(c, "书单 50 本", 820, 1020, 40, t50, t, tone=ink.OCHRE, a=a)
    t12 = ctx.cue(1)
    counter_text(c, "00:00", 300, 520, 72, t12, t, a=a * (1 - P(t, ctx.cue(2), 0.2)))
    t7 = ctx.cue(2)
    if t >= t7:
        counter_text(c, "07:00", 300, 520, 72, t7, t, a=a)
        tx = word(ctx, 2, "按掉")
        ink.brush_path(c, [(200, 470), (400, 570)], 16, p=P(t, tx, 0.15), tone=ink.CINNABAR, alpha=a)
        ink.brush_path(c, [(400, 470), (200, 570)], 16, p=P(t, tx + 0.12, 0.15), tone=ink.CINNABAR, alpha=a)


def d_hook_title(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    ink.bloom(c, 540, 700, 420, P(t, 0, 1.2), seed=3, alpha=0.12 * a)
    t1 = word(ctx, 0, "为什么")
    hanzi.write(c, "道理都懂", 540, 600, 190, hanzi.progress(t, 0.0, max(0.6, t1 - 0.1)), alpha=a)
    ink.label(c, "为什么还是", 540, 880, 70, alpha=a * P(t, t1, 0.3), name="serif_black")
    t2 = word(ctx, 0, "过不好")
    hanzi.write(c, "过不好", 540, 1060, 200, hanzi.progress(t, t2, 0.9), color=ink.CINNABAR, alpha=a)


def d_hook_bamboo(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    t_out = word(ctx, 0, "病倒")
    off = 1 - P(t, t_out, 0.35)
    night(c, a, 330, 790)
    art.modern_bed_phone(c, 520, 760, 0.95, a, glow=off, t=t)
    divider(c, 830, a, P(t, 0, 0.5))
    bamboo_grove(c, 560, 1330, t, a * 0.9, n=6, h=480, seed=2)
    ink.lamp(c, 430, 1290, t, 0.9, alpha=a * off + a * 0.15, glow=off)
    k = P(t, t_out, 0.4)
    art.scholar_seated(c, 260, 1330, 0.85, a * (1 - k), t=t)
    art.figure_fallen(c, 270, 1330, 0.8, a * k)
    ink.label(c, "21 岁", 860, 960, 46, tone=ink.CINNABAR, alpha=a * P(t, word(ctx, 0, "二十一岁"), 0.3))


# ================================================================ 第 2 节 · 开放回路

def d_loop_gewu(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    backdrop(c, t, a * 0.6)
    art.books(c, 540, 1300, 1.2, n=int(2 + 4 * P(t, 0, 1.5)), alpha=a)
    ink.label(c, "当时最权威的说法", 540, 420, 46, tone=ink.OCHRE, alpha=a * P(t, 0.2, 0.4), name="serif_medium")
    tg = word(ctx, 1, "格")
    hanzi.write(c, "格物", 540, 700, 230, hanzi.progress(t, tg - 0.3, 1.0), alpha=a)
    tq = word(ctx, 1, "穷究")
    ink.label(c, "格 ＝ 穷究", 540, 920, 52, tone=ink.CINNABAR, alpha=a * P(t, tq, 0.3))


def d_loop_bamboo(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    backdrop(c, t, a * 0.5, y=480)
    art.pavilion(c, 300, 1250, 0.75, a * 0.85)
    bamboo_grove(c, 620, 1260, t, a, n=7, h=620, seed=6, grow=EO(P(t, 0, 1.2)))
    t3, t7 = word(ctx, 2, "三天"), word(ctx, 2, "第七天")
    k1, k2 = P(t, t3 + 0.3, 0.4), P(t, t7 + 0.4, 0.4)
    art.scholar_standing(c, 480, 1250, 0.6, a * (1 - k1), flip=False)
    art.figure_fallen(c, 470, 1250, 0.5, a * k1)
    art.scholar_standing(c, 560, 1250, 0.66, a * (1 - k2))
    art.figure_fallen(c, 570, 1255, 0.55, a * k2)
    counter_text(c, "3 天", 300, 640, 88, t3, t, a=a)
    counter_text(c, "7 天", 760, 640, 110, t7, t, tone=ink.CINNABAR, a=a)
    tq = ctx.cue(3)
    ink.seal(c, "？", 540, 470, 120, t - (tq + 0.4), round_=True)


def d_loop_longchang(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    pan = EO(P(t, 0, ctx.dur)) * 900
    c.save()
    c.translate(-pan * 0.3, 0)
    bamboo_grove(c, 160 - pan * 0.7, 1300, t, a * (1 - P(t, 0.5, 1.5)), n=5, h=520, seed=6)
    c.restore()
    backdrop(c, t, a, shift=pan, far=0.32, near=0.55)
    art.cave(c, 1380 - pan, 1250, 120, 210, a)
    glow = P(t, ctx.dur - 1.5, 1.0)
    c.drawCircle(1380 - pan, 1160, 70, ink.paint((255, 205, 120), 0.5 * glow * a, blur=40))
    t16 = word(ctx, 0, "十六年后")
    counter_text(c, "十六年后", 540, 460, 76, t16, t, a=a)
    tg = word(ctx, 0, "贵州龙场")
    counter_text(c, "贵州 · 龙场", 540, 560, 52, tg, t, tone=ink.CINNABAR, a=a)


def d_loop_promise(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    t1 = word(ctx, 0, "你缺的")
    hanzi.write(c, "你缺的", 540, 640, 150, hanzi.progress(t, t1, 0.8), alpha=a)
    t2 = word(ctx, 0, "不是")
    hanzi.write(c, "不是道理", 540, 860, 170, hanzi.progress(t, t2, 1.2), alpha=a)
    ta = word(ctx, 1, "答案")
    ink.seal(c, "？", 840, 1080, 150, t - (ta + 0.2), round_=True)
    ink.label(c, "答案在最后", 540, 1110, 50, tone=ink.OCHRE, alpha=a * P(t, ta, 0.3), name="serif_medium")


# ================================================================ 第 3 节 · 原典登场

def d_src_cave(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    backdrop(c, t, a, far=0.35, near=0.6, y=420)
    art.cave(c, 540, 1260, 230, 420, a)
    tj = word(ctx, 3, "跳起来")
    jump = math.sin(math.pi * P(t, tj, 0.45)) * 60
    flare = 1 + 1.6 * math.exp(-max(0.0, t - tj) * 2.5) * (t >= tj)
    ink.lamp(c, 690, 1250, t, 0.8, alpha=a, glow=flare)
    art.scholar_seated(c, 540, 1262 - jump, 0.72, a * 0.95, tone=(70, 62, 54), t=t)
    if t >= tj:
        k = math.exp(-(t - tj) * 1.8)
        for r in range(14):
            ang = math.pi * (1.05 + 0.9 * r / 13)
            ln = 260 + 120 * math.sin(r * 2.3)
            ink.brush_path(c, [(690 + math.cos(ang) * 60, 1220 + math.sin(ang) * 60),
                               (690 + math.cos(ang) * ln, 1220 + math.sin(ang) * ln)], 10, p=P(t, tj, 0.25),
                           tone=(255, 200, 120), alpha=0.55 * k * a, taper=True)
    k = P(t, tj + 0.25, 0.3)
    for k_, x in enumerate((180, 900)):
        art.scholar_standing(c, x, 1300, 0.42, a * 0.75, flip=(x > 540), bow=0.6 * k)
    tq = ctx.cue(2)
    ink.label(c, "？", 540, 760, 110, tone=ink.CINNABAR, alpha=a * P(t, tq, 0.3) * (1 - P(t, tj, 0.3)))
    ink.label(c, "龙场 · 今贵州修文", 540, 380, 40, tone=ink.OCHRE, alpha=a * P(t, 0.3, 0.5), name="serif_medium")


def d_src_card1(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    backdrop(c, t, a * 0.35, y=420)
    t0, t1 = ctx.cue(1), ctx.end(1)
    p = P(t, t0 - 0.3, (t1 - t0) + 0.3)
    up = EO(P(t, ctx.cue(2), 0.6))
    ink.text_card(c, ["圣人之道", "吾性自足", "向之求理", "于事物者", "误也"], 540, 860 - up * 60, max(0.02, p),
                  size=66, source="《年谱》· 正德三年（非《传习录》正文）", alpha=a)


def d_src_xuai(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    backdrop(c, t, a * 0.4, y=300, far=0.25, near=0.35)
    art.scholar_seated(c, 730, 780, 0.75, a, t=t)
    art.scholar_standing(c, 330, 790, 0.72, a, bow=EO(P(t, ctx.cue(0), 0.6)))
    ink.label(c, "徐爱", 330, 380, 40, tone=ink.CINNABAR, alpha=a * P(t, word(ctx, 0, "徐爱"), 0.3))
    divider(c, 860, a)
    night(c, a, 900, 1330)
    art.modern_desk(c, 470, 1290, 0.95, a, glow=1.0)
    q = "找得全吗？"
    tq = ctx.cue(1)
    n = int(len(q) * P(t, tq, ctx.end(1) - tq))
    ink.label(c, q[:n], 640, 1030, 40, alpha=a, name="serif_black")


def d_src_card2(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    t0, t1 = ctx.cue(1), ctx.end(1)
    p = P(t, t0 - 0.3, (t1 - t0) + 0.3)
    dim = P(t, ctx.cue(3), 0.5)
    ink.text_card(c, ["心即理也", "天下又有", "心外之事", "心外之理乎"], 540, 820, max(0.02, p), size=70,
                  source="《传习录·上》· 徐爱录", alpha=a * (1 - 0.5 * dim))
    ink.seal(c, "心即理", 800, 1180, 170, t - (word(ctx, 2, "心的理") + 0.3))
    ink.label(c, "最不玄的一句", 540, 1290, 46, tone=ink.CINNABAR, alpha=a * P(t, word(ctx, 3, "最不玄"), 0.3),
              name="serif_black")


# ================================================================ 第 4 节 · 深讲

def d_deep_zhuxi(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    ink.label(c, "朱熹", 540, 400, 64, alpha=a * P(t, 0.1, 0.3))
    ink.label(c, "《大学章句》", 540, 470, 32, tone=ink.OCHRE, alpha=a * P(t, 0.2, 0.3), name="serif_medium")
    stack = int(1 + 7 * EO(P(t, ctx.cue(1), ctx.end(1) - ctx.cue(1))))
    art.books(c, 330, 1180, 1.0, n=stack, alpha=a)
    th = word(ctx, 1, "豁然贯通")
    ink.label(c, "豁然贯通", 330, 700, 60, tone=ink.CINNABAR, alpha=a * P(t, th, 0.3))
    inner = art.phone(c, 790, 880, 0.62, a * P(t, ctx.cue(2), 0.3), glow=0.4)
    tp = ctx.cue(2)
    n = int(300 * EO(P(t, tp, ctx.end(2) - tp)))
    if t >= tp:
        ink.label(c, f"收藏 {n}", inner.centerX(), inner.top() + 40, 30, alpha=a)
        for k in range(6):
            art.fav_card(c, inner.centerX(), inner.top() + 110 + k * 62, inner.width() - 26, "干货", alpha=a * P(t, tp + k * 0.12, 0.2))


def d_deep_reverse(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    tf = word(ctx, 0, "方向反了")
    hanzi.write(c, "反", 540, 800, 420, hanzi.progress(t, tf, 0.7), alpha=a)
    k = EO(P(t, tf + 0.4, 0.5))
    ink.brush_path(c, ink.smooth([(260, 1180), (540, 1100 - 120 * k), (820, 1180)], 30), 18, p=k, tone=ink.CINNABAR,
                   alpha=a)


def d_deep_xiao(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    backdrop(c, t, a * 0.3, y=420, far=0.2, near=0.3)
    art.scholar_seated(c, 720, 1100, 0.85, a * 0.8, tone=(80, 72, 64), t=t)
    art.scholar_standing(c, 360, 1110, 0.8, a, bow=0.7)
    tf = word(ctx, 0, "父亲身上")
    ink.label(c, "孝的道理 · 在父亲身上？", 540, 430, 44, alpha=a * P(t, tf, 0.3) * (1 - P(t, ctx.cue(1), 0.3)),
              name="serif_black")
    th = word(ctx, 1, "心里")
    ink.bloom(c, 390, 860, 90, P(t, th, 0.8), seed=6, tone=ink.CINNABAR, alpha=0.6 * a)
    hanzi.write(c, "心", 390, 860, 120, hanzi.progress(t, th, 0.6), color=ink.PAPER, alpha=a)
    tw, ts = word(ctx, 2, "冬天"), word(ctx, 2, "夏天")
    counter_text(c, "冬 · 怕冷", 300, 430, 50, tw, t, a=a)
    counter_text(c, "夏 · 怕热", 780, 430, 50, ts, t, a=a)


def d_deep_tree(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    tg = word(ctx, 0, "根")
    tz = word(ctx, 0, "枝叶")
    t1 = ctx.cue(1)
    roots = EO(P(t, tg - 0.2, 1.0)) if t < t1 else 1.0
    br = EO(P(t, tz, 1.0)) if t < t1 else EO(P(t, word(ctx, 1, "才有枝叶"), 1.0))
    if t < t1:
        br = min(br, 0.35)
    art.tree(c, 540, 1060, 1.1, roots, max(br, 0.0), P(t, word(ctx, 1, "才有枝叶") + 0.6, 0.8), a)
    ink.label(c, "根", 360, 1220, 56, tone=ink.CINNABAR, alpha=a * P(t, tg, 0.3))
    ink.label(c, "枝叶", 780, 520, 56, tone=ink.CINNABAR, alpha=a * P(t, tz, 0.3))
    ink.text_card(c, ["这诚孝的心", "便是根", "许多条件", "便是枝叶"], 840, 1180, P(t, tg - 0.2, 1.2), size=34,
                  source="《传习录·上》", alpha=a * 0.95)


def d_deep_drop(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    ink.bloom(c, 540, 820, 520, P(t, 0, 1.0), seed=9, alpha=0.1 * a)
    tx = word(ctx, 0, "心即理")
    hanzi.write(c, "心即理", 540, 820, 270, hanzi.progress(t, tx - 0.25, 1.3), alpha=a)
    ink.seal(c, "阳明", 860, 1050, 130, t - (tx + 1.1))


def d_deep_pot(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    tw = word(ctx, 1, "活不了")
    wither = P(t, tw, 1.0)
    art.pot(c, 540, 1120, 1.3, a)
    ink.label(c, "300", 540, 1230, 64, tone=ink.PAPER, alpha=a * 0.9)
    rng = np.random.default_rng(3)
    t300 = word(ctx, 0, "三百片")
    n = int(16 * EO(P(t, ctx.cue(0), t300 - ctx.cue(0) + 0.5)))
    for k in range(n):
        ang = rng.uniform(-40, 40)
        droop = wither * rng.uniform(20, 55) * (1 if ang > 0 else -1)
        x = 540 + rng.uniform(-150, 150)
        y = 1060 - rng.uniform(40, 360) + wither * 80
        art.fav_card(c, x, y, 190, "干货", alpha=a * (1 - 0.65 * wither), rot=ang + droop,
                     tone=gfx.mix(ink.INK, (150, 140, 120), wither))
    ink.label(c, "根没种下", 540, 470, 64, tone=ink.CINNABAR, alpha=a * P(t, ctx.cue(1), 0.3), name="serif_black")


# ================================================================ 第 5 节 · 现代对照

def d_mod_lab(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    ink.label(c, "1971 · 心理学家 德西（Deci）", 540, 400, 40, tone=ink.OCHRE, alpha=a * P(t, ctx.cue(1), 0.3),
              name="serif_medium")
    tm = word(ctx, 2, "给钱")
    to = word(ctx, 3, "离开房间")
    tr = ctx.cue(4)
    stop = P(t, tr, 0.5)
    art.student_at_table(c, 330, 1150, 0.9, a, playing=1 - stop, t=t, coin=P(t, tm, 0.3))
    art.student_at_table(c, 780, 1150, 0.9, a, playing=1.0, t=t)
    ink.label(c, "有钱组", 330, 1230, 38, alpha=a * P(t, tm, 0.3))
    ink.label(c, "无钱组", 780, 1230, 38, alpha=a * P(t, word(ctx, 2, "另一组"), 0.3))
    art.door(c, 980, 800, 0.6, P(t, to, 0.4), a * P(t, ctx.cue(3) - 0.3, 0.3))
    ink.label(c, "没人要求的时候", 540, 560, 50, tone=ink.CINNABAR, alpha=a * P(t, word(ctx, 3, "没人要求"), 0.3) * (1 - stop),
              name="serif_black")
    ink.label(c, "玩得更少", 330, 560, 56, tone=ink.CINNABAR, alpha=a * P(t, word(ctx, 4, "更少"), 0.3), name="serif_black")


def d_mod_meta(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    tn = word(ctx, 0, "一百二十八")
    n = int(128 * EO(P(t, tn - 0.3, 0.8)))
    ink.label(c, f"{n}", 540, 720, 200, alpha=a * P(t, tn - 0.3, 0.2))
    ink.label(c, "项研究汇总", 540, 880, 50, alpha=a * P(t, tn, 0.3), name="serif_black")
    ink.label(c, "Deci, Koestner & Ryan, 1999", 540, 960, 30, tone=ink.OCHRE, alpha=a * P(t, tn, 0.3),
              name="serif_medium")
    tc = ctx.cue(1)
    ink.label(c, "反方：Cameron & Pierce, 1994", 540, 1130, 36, tone=ink.CINNABAR, alpha=a * P(t, tc, 0.3),
              name="serif_medium")
    ink.label(c, "争论至今", 540, 1200, 44, alpha=a * P(t, word(ctx, 1, "争论"), 0.3), name="serif_black")


def d_mod_root(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    tz, tg = word(ctx, 0, "枝叶"), word(ctx, 0, "根")
    art.tree(c, 540, 980, 0.9, EO(P(t, tg, 0.8)), 1.0, 1.0, a)
    ink.label(c, "外面的奖励 ＝ 枝叶", 540, 450, 54, alpha=a * P(t, tz, 0.3), name="serif_black")
    ink.label(c, "自己想做的心 ＝ 根", 540, 1250, 54, tone=ink.CINNABAR, alpha=a * P(t, tg, 0.3), name="serif_black")


# ================================================================ 第 6 节 · 误读与边界

def d_mis_dust(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    ink.seal(c, "误读", 540, 470, 150, t - (ctx.cue(0) + 0.3))
    tno = ctx.cue(2)
    dust = P(t, ctx.cue(1), 0.8) * (1 - P(t, tno + 0.3, 0.5))
    art.scholar_seated(c, 360, 1150, 0.85, a, t=t)
    art.books(c, 760, 1150, 0.9, n=4, alpha=a, dust=dust, t=t)
    ink.label(c, "凭感觉？", 360, 700, 54, alpha=a * P(t, word(ctx, 1, "凭感觉"), 0.3) * (1 - P(t, tno, 0.2)),
              name="serif_black")
    if t >= tno:
        ink.brush_path(c, [(250, 640), (470, 760)], 16, p=P(t, tno, 0.15), tone=ink.CINNABAR, alpha=a)
        ink.brush_path(c, [(470, 640), (250, 760)], 16, p=P(t, tno + 0.1, 0.15), tone=ink.CINNABAR, alpha=a)
    tr = ctx.cue(3)
    ink.label(c, "只学枝叶、不种根", 540, 1290, 50, tone=ink.CINNABAR, alpha=a * P(t, tr, 0.3), name="serif_black")


def d_mis_life(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    t1, t2, t3 = word(ctx, 0, "读书"), word(ctx, 0, "讲学"), word(ctx, 0, "带兵")
    k1, k2, k3 = P(t, t1, 0.25), P(t, t2, 0.25), P(t, t3, 0.25)
    art.books(c, 270, 900, 0.8, n=3, alpha=a * k1)
    ink.label(c, "读书", 270, 1000, 50, alpha=a * k1, name="serif_black")
    art.lectern(c, 560, 860, 0.45, a * k2)
    ink.label(c, "讲学", 560, 1060, 50, alpha=a * k2, name="serif_black")
    art.banner(c, 780, 1150, 0.55, t, a * k3, char="兵")
    ink.label(c, "带兵", 880, 1220, 50, tone=ink.CINNABAR, alpha=a * k3, name="serif_black")


def d_mis_gu(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    k = P(t, ctx.cue(2), 0.6)
    for x in (330, 750):
        art.scholar_seated(c, x, 1150, 0.7, a * (1 - 0.6 * k), t=t)
    ink.label(c, "空谈", 540, 760, 70, alpha=a * P(t, word(ctx, 0, "空谈"), 0.3) * (1 - k), name="serif_black")
    ink.label(c, "顾炎武", 540, 420, 52, alpha=a * P(t, word(ctx, 1, "顾炎武"), 0.3))
    ink.text_card(c, ["以明心见性之空言", "代修己治人之实学"], 540, 880, P(t, ctx.cue(2) - 0.2, 1.0), size=48,
                  source="顾炎武《日知录》", alpha=a * k)


def d_mis_gold(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    tx = word(ctx, 0, "从心出发")
    ink.label(c, "不是停在心里", 540, 560, 54, alpha=a * P(t, word(ctx, 0, "停在心里"), 0.3), name="serif_black")
    hanzi.write(c, "从心出发", 540, 860, 190, hanzi.progress(t, tx - 0.1, 1.2), alpha=a)
    ink.seal(c, "心即理", 840, 1110, 120, t - (tx + 1.2))


# ================================================================ 第 7 节 · 今日功课

def d_hw_answer(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    ink.label(c, "你缺的，是什么？", 540, 460, 60, alpha=a * P(t, 0.0, 0.3) * (1 - 0.5 * P(t, ctx.cue(1), 0.3)),
              name="serif_black")
    tg = word(ctx, 1, "一条根")
    hanzi.write(c, "根", 540, 780, 300, hanzi.progress(t, tg, 0.8), color=ink.CINNABAR, alpha=a)
    art.tree(c, 540, 1080, 0.6, EO(P(t, tg + 0.5, 1.2)), 0.0, 0.0, a * 0.8)
    ink.label(c, "你自己真心想要的那件事", 540, 1250, 46, alpha=a * P(t, word(ctx, 1, "真心想要"), 0.3), name="serif_black")


def d_hw_task(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    ink.seal(c, "今日功课", 230, 470, 160, t - (ctx.cue(0) + 0.2))
    ink.label(c, "五分钟", 230, 620, 44, tone=ink.CINNABAR, alpha=a * P(t, word(ctx, 0, "五分钟"), 0.3), name="serif_black")
    steps = ["① 打开收藏夹", "② 只挑一篇", "③ 写一句：我为什么想要它"]
    times = [ctx.cue(1), word(ctx, 1, "只挑一篇"), ctx.cue(2)]
    for k, (txt, tk) in enumerate(zip(steps, times)):
        ink.label(c, txt, 110, 760 + k * 80, 38, alpha=a * P(t, tk, 0.3), name="serif_black", align="left")
    inner = art.phone(c, 790, 1000, 0.62, a, glow=0.4)
    tsel = word(ctx, 1, "只挑一篇")
    left = 300 - int(299 * EO(P(t, tsel, 1.0)))
    ink.label(c, f"收藏 {left}", inner.centerX(), inner.top() + 40, 30, alpha=a)
    shown = 5 if t < tsel else max(1, 5 - int(5 * P(t, tsel, 0.8)))
    for k in range(shown):
        art.fav_card(c, inner.centerX(), inner.top() + 110 + k * 62, inner.width() - 26, "干货" if k else "我最想做到的",
                     alpha=a)
    tw = ctx.cue(2)
    if t >= tw:
        hanzi.write(c, "我为什么想要它", inner.centerX(), inner.top() + 220, 26, hanzi.progress(t, tw, 1.6), alpha=a)
    tok = ctx.cue(3)
    ink.label(c, "写得出来 → 根种下了", 540, 1300, 42, tone=ink.CINNABAR, alpha=a * P(t, tok, 0.3), name="serif_black")


def d_hw_next(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx, fade_out=1.0)
    dawn = P(t, 0, 2.0)
    c.drawRect(skia.Rect.MakeLTRB(0, 300, gfx.W, 1350), ink.paint((255, 236, 200), 0.18 * dawn * a, blur=60))
    backdrop(c, t, a * 0.8, y=420)
    art.cave(c, 880, 1300, 70, 130, a * 0.8)
    tk = word(ctx, 1, "知行合一")
    ink.label(c, "下一讲", 540, 560, 44, tone=ink.OCHRE, alpha=a * P(t, ctx.cue(1), 0.3), name="serif_medium")
    hanzi.write(c, "知行合一", 540, 760, 170, hanzi.progress(t, tk, 1.2), alpha=a)
    ink.label(c, "知道却不去做，就是还不知道", 540, 1000, 42, alpha=a * P(t, ctx.cue(2), 0.4), name="serif_black")
    ink.seal(c, "心即理", 200, 1180, 170, t - (word(ctx, 2, "还不知道") + 0.6))


def scenes():
    hanzi.prepare(CALLI)
    S = E.scene
    return [
        S("hook_fav", 1, [0, 1, 2], d_hook_fav, [("ding", 0, "三百篇", 0.0), ("muyu", 2, "按掉", 0.0)],
          marks={0: ("三百篇",)}),
        S("hook_title", 1, [3], d_hook_title, [("dagu", 0, None, 0.0)], marks={0: ("过不好",)}),
        S("hook_bamboo", 1, [4], d_hook_bamboo, [("tanggu", 0, "病倒", 0.0)], marks={0: ("病倒",)}),
        S("loop_gewu", 2, [0, 1], d_loop_gewu, [("bangzi", 1, "格", 0.0)], marks={1: ("穷究",)}),
        S("loop_bamboo", 2, [2, 3, 4, 5], d_loop_bamboo,
          [("tanggu", 2, "三天", 0.3), ("dagu", 2, "第七天", 0.4)], marks={1: ("日夜苦想",)}),
        S("loop_longchang", 2, [6], d_loop_longchang, [("daluo", 0, "贵州龙场", 0.0)]),
        S("loop_promise", 2, [7, 8], d_loop_promise, [("dagu", 1, "答案", 0.2)], marks={0: ("更多的道理",)}),
        S("src_cave", 3, [0, 1, 2, 3], d_src_cave, [("bangzi", 3, "跳起来", 0.0)]),
        S("src_card1", 3, [4, 5, 6], d_src_card1, [("muyu", 1, None, -0.3)], marks={2: ("找错了",)}),
        S("src_xuai", 3, [7, 8], d_src_xuai, [], marks={1: ("找得全吗",)}),
        S("src_card2", 3, [9, 10, 11, 12], d_src_card2, [("muyu", 1, None, -0.3), ("dagu", 2, "心的理", 0.3)],
          marks={2: ("就在心里",)}),
        S("deep_zhuxi", 4, [0, 1, 2], d_deep_zhuxi, [], marks={1: ("豁然贯通",)}),
        S("deep_reverse", 4, [3], d_deep_reverse, [("daluo", 0, "方向反了", 0.0)], marks={0: ("方向反了",)}),
        S("deep_xiao", 4, [4, 5, 6], d_deep_xiao, [("bianzhong", 1, "心里", 0.0)], marks={1: ("想对爸妈好的心",)}),
        S("deep_tree", 4, [7, 8], d_deep_tree, [("tanggu", 0, "根", 0.0)], marks={0: ("真心是根",)}),
        S("deep_drop", 4, [9], d_deep_drop, [("dagu", 0, "心即理", 0.0)], marks={0: ("心即理",)}),
        S("deep_pot", 4, [10, 11], d_deep_pot, [("tanggu", 1, "活不了", 0.0)], marks={1: ("活不了",)}),
        S("mod_lab", 5, [0, 1, 2, 3, 4], d_mod_lab, [("muyu", 3, "离开房间", 0.0), ("tanggu", 4, "更少", 0.0)],
          marks={4: ("更少",)}),
        S("mod_meta", 5, [5, 6], d_mod_meta, [("dagu", 0, "一百二十八", 0.0)], marks={1: ("被夸大",)}),
        S("mod_root", 5, [7], d_mod_root, [("bianzhong", 0, "根", 0.0)], marks={0: ("才是根",)}),
        S("mis_dust", 6, [0, 1, 2, 3], d_mis_dust, [("daluo", 0, None, 0.3), ("bangzi", 2, None, 0.0)],
          marks={3: ("只学枝叶",)}),
        S("mis_life", 6, [4], d_mis_life, [("muyu", 0, "读书", 0.0), ("muyu", 0, "讲学", 0.0), ("tanggu", 0, "带兵", 0.0)]),
        S("mis_gu", 6, [5, 6, 7], d_mis_gu, [("daluo", 2, None, -0.2)], marks={2: ("空话",)}),
        S("mis_gold", 6, [8], d_mis_gold, [("dagu", 0, "从心出发", 0.0)], marks={0: ("从心出发",)}),
        S("hw_answer", 7, [0, 1], d_hw_answer, [("dagu", 1, "一条根", 0.0)], marks={1: ("真心想要",)}),
        S("hw_task", 7, [2, 3, 4, 5], d_hw_task, [("daluo", 0, None, 0.2)], marks={2: ("我为什么想要它",)}),
        S("hw_next", 7, [6, 7, 8], d_hw_next, [("bianzhong", 1, "知行合一", 0.0), ("bianzhong", 2, "还不知道", 0.6)],
          marks={1: ("知行合一",)}, tail=2.0),
    ]


def video() -> InkVideo:
    return InkVideo(scenes(), HEADER, drop_at="hook_title")
