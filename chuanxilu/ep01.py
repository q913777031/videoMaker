"""第 01 讲 · 心即理：道理都懂，为什么还是过不好？（第七版分镜：提出困扰 → 解释原因 → 当下实例 → 升华前行）

每个场景对应文案若干句；画面锚定到“读到某个词”的时刻，打击乐与撞击帧对齐。
配乐：音乐 drop 落在故事开场；第 4 节“扎心”段闷音，读到“别等准备好了”瞬间全开。
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
CALLI = "知道这么多道理却依然过不好这一生心即理出发知行合一根你不是不努力"


def backdrop(c, t, a, shift=0.0, far=0.28, near=0.45, y=560):
    """远山两层 + 云雾（古代场景通用）。"""
    ink.mountains(c, y, 360, 3, alpha=far * a, blur=6, shift=shift * 0.4 + t * 2)
    ink.mist(c, t, y + 280, 0.5 * a, seed=1)
    ink.mountains(c, y + 140, 380, 5, alpha=near * a, shift=shift * 0.8 + t * 4)
    ink.mist(c, t, y + 420, 0.45 * a, seed=2)


def night(c, a, y0=320, y1=1300, tone=(70, 84, 98), alpha=0.22):
    """今人深夜：冷灰淡墨夜色块。"""
    c.drawRoundRect(skia.Rect.MakeLTRB(70, y0, gfx.W - 70, y1), 30, 30, ink.paint(tone, alpha * a, blur=24))


def bamboo_grove(c, x0, y, t, a, n=6, h=560, seed=0, grow=1.0):
    for k in range(n):
        art.bamboo(c, x0 + k * 52 + (k % 2) * 14, y + (k % 3) * 10, h - (k % 3) * 60, seed + k, t,
                   a * (0.6 + 0.4 * (k % 2)), width=18 + (k % 2) * 6, grow=grow)


def pop_text(c, text, x, y, size, t0, t, tone=ink.INK, a=1.0, name="serif_black"):
    """文字从 1.3 倍压到原大落定（配合打击乐的“砸字”）。"""
    k = P(t, t0, 0.18)
    if k <= 0:
        return
    sc = 1.3 - 0.3 * EO(k)
    c.save()
    c.translate(x, y)
    c.scale(sc, sc)
    ink.label(c, text, 0, 0, size, tone=tone, alpha=a * k, name=name)
    c.restore()


def strike(c, x, y, w, t0, t, a, tone=ink.CINNABAR):
    """朱砂一笔划掉。"""
    if t >= t0:
        ink.brush_path(c, [(x - w / 2, y + 6), (x + w / 2, y - 6)], 12, p=P(t, t0, 0.15), tone=tone, alpha=a)


def rays(c, x, y, t, t0, a, n=14, tone=(255, 200, 120), r0=60, r1=280, spread=0.9):
    """顿悟 / 晨光放射：从 (x, y) 向上半圈放射的光笔，随时间衰减。"""
    if t < t0:
        return
    k = math.exp(-(t - t0) * 1.2)
    for r in range(n):
        ang = math.pi * (1 + (1 - spread) / 2 + spread * r / (n - 1))
        ln = r1 + 80 * math.sin(r * 2.3)
        ink.brush_path(c, [(x + math.cos(ang) * r0, y + math.sin(ang) * r0), (x + math.cos(ang) * ln, y + math.sin(ang) * ln)],
                       10, p=P(t, t0, 0.25), tone=tone, alpha=0.55 * k * a)


# ================================================================ 第 1 节 · 提出困扰

def d_hook(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    night(c, a * (1 - P(t, 1.2, 0.6)))
    inner = art.phone(c, 540, 820, 0.7, a * (1 - P(t, 1.0, 0.5)), glow=0.6)
    n = int(300 * EO(P(t, 0, 1.0)))
    ink.label(c, f"收藏 {n}", inner.centerX(), inner.top() + 40, 32, alpha=a * (1 - P(t, 1.0, 0.5)))
    for k in range(6):
        art.fav_card(c, inner.centerX(), inner.top() + 110 + k * 62, inner.width() - 26, "干货",
                     alpha=a * P(t, k * 0.1, 0.2) * (1 - P(t, 1.0, 0.5)))
    t1, t2 = word(ctx, 0, "知道"), word(ctx, 0, "却依然")
    ink.label(c, "为什么", 540, 470, 64, alpha=a * P(t, 1.0, 0.3), name="serif_black")
    hanzi.write(c, "知道这么多道理", 540, 680, 118, hanzi.progress(t, max(1.0, t1), max(0.8, t2 - t1)), alpha=a)
    hanzi.write(c, "却依然过不好这一生", 540, 920, 96, hanzi.progress(t, t2, ctx.end(0) - t2 + 0.3), color=ink.CINNABAR,
                alpha=a)


# ================================================================ 第 2 节 · 解释原因

def d_bamboo(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    backdrop(c, t, a * 0.5, y=480)
    bamboo_grove(c, 560, 1260, t, a, n=7, h=620, seed=6, grow=EO(P(t, 0, 1.2)))
    ink.label(c, "王阳明", 300, 470, 70, alpha=a * P(t, word(ctx, 0, "王阳明"), 0.3), name="serif_black")
    t7, tb = word(ctx, 1, "七天"), word(ctx, 2, "病倒")
    pop_text(c, "7 天", 790, 520, 120, t7, t, tone=ink.CINNABAR, a=a)
    k = P(t, tb, 0.4)
    art.scholar_standing(c, 380, 1260, 0.8, a * (1 - k))
    art.figure_fallen(c, 380, 1265, 0.75, a * k)
    pop_text(c, "圣贤做不得", 380, 760, 54, word(ctx, 3, "圣贤"), t, a=a)


def d_exile(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    k_m = P(t, ctx.cue(1), 1.0)
    backdrop(c, t, a * (0.3 + 0.5 * k_m), y=520, near=0.6)
    for yy in (900, 1050, 1180):
        ink.mist(c, t * 1.5, yy, 0.6 * a * k_m, seed=yy)
    tl, tz = word(ctx, 0, "刘瑾"), word(ctx, 0, "四十廷杖")
    pop_text(c, "刘瑾", 300, 430, 64, tl, t, a=a * (1 - P(t, ctx.cue(1), 0.3)))
    pop_text(c, "廷杖四十", 760, 430, 64, tz, t, tone=ink.CINNABAR, a=a * (1 - P(t, ctx.cue(1), 0.3)))
    pop_text(c, "贬 · 贵州龙场", 540, 560, 56, word(ctx, 0, "贵州龙场"), t, a=a)
    pop_text(c, "瘴气弥漫", 540, 680, 46, word(ctx, 1, "瘴气"), t, tone=ink.OCHRE, a=a * (1 - P(t, ctx.cue(2), 0.3)),
             name="serif_medium")
    for k, (txt, w) in enumerate((("官", "官没了"), ("名", "名没了"), ("书", "书也没了"))):
        tk = word(ctx, 2, w)
        x = 300 + k * 240
        pop_text(c, txt, x, 820, 130, tk - 0.15, t, a=a)
        strike(c, x, 820, 150, tk + 0.25, t, a)
    pop_text(c, "连命都可能保不住", 540, 1040, 50, word(ctx, 2, "连命"), t, tone=ink.CINNABAR, a=a)


def d_coffin(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    backdrop(c, t, a * 0.6, y=380, far=0.32, near=0.5)
    art.cave(c, 360, 1210, 200, 360, a)
    ink.lamp(c, 470, 1200, t, 0.7, alpha=a)
    art.scholar_seated(c, 360, 1212, 0.62, a, tone=(70, 62, 54), t=t)
    pop_text(c, "荣辱 · 看开", 760, 520, 50, word(ctx, 1, "荣辱"), t, a=a)
    pop_text(c, "生死 · 未破", 760, 600, 50, word(ctx, 1, "生死"), t, tone=ink.CINNABAR, a=a)
    tc = word(ctx, 2, "石棺")
    k = P(t, tc - 0.2, 0.5)
    art.coffin(c, 790, 1240, 0.9, a * k)
    ink.label(c, "《年谱》：吾惟俟命而已", 790, 1310, 30, tone=ink.OCHRE, alpha=a * k, name="serif_medium")


def d_care(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    backdrop(c, t, a * 0.35, y=380, far=0.22, near=0.32)
    art.figure_fallen(c, 250, 1150, 0.6, a * 0.75)
    art.figure_fallen(c, 820, 1160, 0.6, a * 0.75)
    art.congee_pot(c, 560, 1170, 0.9, t, a * P(t, word(ctx, 0, "熬粥") - 0.3, 0.4))
    art.scholar_standing(c, 420, 1170, 0.75, a, bow=0.3)
    for k, (txt, w) in enumerate((("砍柴", "砍柴"), ("挑水", "挑水"), ("熬粥", "熬粥"))):
        pop_text(c, txt, 300 + k * 240, 520, 56, word(ctx, 0, w), t, a=a * (1 - P(t, ctx.cue(1), 0.3)))
    pop_text(c, "唱歌 · 讲笑话", 540, 620, 44, word(ctx, 0, "唱歌"), t, tone=ink.OCHRE, a=a * (1 - P(t, ctx.cue(1), 0.3)),
             name="serif_medium")
    tq = ctx.cue(1)
    ink.seal(c, "？", 540, 560, 150, t - (tq + 0.2), round_=True)
    pop_text(c, "圣人到了这一步，会怎么办？", 540, 720, 46, tq + 0.4, t, a=a)


def d_wake(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    tj = word(ctx, 0, "跳起来")
    t1, t2 = ctx.cue(1), ctx.cue(2)
    out = P(t, t1, 0.4)
    backdrop(c, t, a * 0.6 * (1 - out), y=380)
    art.cave(c, 540, 1230, 220, 400, a * (1 - out))
    flare = 1 + 1.6 * math.exp(-max(0.0, t - tj) * 2.5) * (t >= tj)
    ink.lamp(c, 680, 1220, t, 0.8, alpha=a * (1 - out), glow=flare)
    jump = math.sin(math.pi * P(t, tj, 0.45)) * 60
    art.scholar_seated(c, 540, 1232 - jump, 0.7, a * (1 - out), tone=(70, 62, 54), t=t)
    rays(c, 680, 1200, t, tj, a * (1 - out))
    if t >= t1:
        for k, txt in enumerate(("官", "名", "书")):
            x = 300 + k * 240
            ink.label(c, txt, x, 520, 90, alpha=a * 0.35 * (1 - P(t, t1 + 0.5 + k * 0.3, 0.6)))
            strike(c, x, 520, 110, t1, t, a * 0.6 * (1 - P(t, t1 + 0.5 + k * 0.3, 0.6)))
        th = word(ctx, 1, "善意")
        ink.bloom(c, 540, 860, 160, P(t, th, 1.0), seed=7, tone=ink.CINNABAR, alpha=0.6 * a)
        hanzi.write(c, "心", 540, 860, 180, hanzi.progress(t, th, 0.6), color=ink.PAPER, alpha=a)
        pop_text(c, "善意，一点没少", 540, 1100, 56, th + 0.3, t, tone=ink.CINNABAR, a=a * (1 - P(t, t2, 0.3)))
    if t >= t2:
        ink.text_card(c, ["圣人之道", "吾性自足"], 540, 1130, P(t, t2, 1.2), size=58, source="《年谱》", alpha=a)


def d_gold(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    ink.bloom(c, 540, 820, 520, P(t, 0, 1.0), seed=9, alpha=0.1 * a)
    ink.label(c, "道理从来不在竹子上", 540, 520, 58, alpha=a * P(t, 0.0, 0.3), name="serif_black")
    pop_text(c, "就在自己心里", 540, 620, 64, word(ctx, 0, "就在"), t, tone=ink.CINNABAR, a=a)
    tx = word(ctx, 1, "心即理")
    hanzi.write(c, "心即理", 540, 900, 250, hanzi.progress(t, tx - 0.2, 1.1), alpha=a)
    ink.seal(c, "心即理", 860, 1140, 150, t - (tx + 1.0))


def d_why(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    t0, t1 = ctx.cue(0), ctx.cue(1)
    pop_text(c, "不是懂得太少", 540, 470, 58, word(ctx, 0, "不是懂得太少"), t, a=a)
    rng = np.random.default_rng(5)
    ko = EO(P(t, word(ctx, 1, "往外找"), 1.2))
    for k in range(10):
        ang = rng.uniform(0, 2 * math.pi)
        d = 80 + ko * rng.uniform(220, 420)
        art.fav_card(c, 540 + math.cos(ang) * d, 820 + math.sin(ang) * d * 0.7, 160, "干货", alpha=a * (1 - 0.7 * ko),
                     rot=rng.uniform(-30, 30))
    pop_text(c, "往外找 ×", 300, 1150, 54, word(ctx, 1, "往外找"), t, tone=ink.INK, a=a)
    tg = word(ctx, 1, "扎根")
    pop_text(c, "在心里扎根 √", 770, 1150, 54, tg, t, tone=ink.CINNABAR, a=a)
    art.tree(c, 540, 820, 0.5, EO(P(t, tg, 1.0)), 0.0, 0.0, a * 0.8)


# ================================================================ 第 3 节 · 当下实例

def d_root(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    tg, tz = word(ctx, 0, "真心是根"), word(ctx, 0, "枝叶")
    art.tree(c, 540, 1010, 0.8, EO(P(t, tg, 1.0)), EO(P(t, tz, 1.0)), P(t, tz + 0.6, 0.8), a)
    pop_text(c, "做法 ＝ 枝叶", 540, 420, 58, tz, t, a=a)
    pop_text(c, "真心 ＝ 根", 540, 1320, 58, tg, t, tone=ink.CINNABAR, a=a)


def d_wang(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    night(c, a * 0.6, 360, 1320, tone=(120, 110, 90), alpha=0.15)
    art.courier(c, 540, 1250, 1.3, a, t=t)
    pop_text(c, "王计兵 · 外卖员", 540, 440, 60, word(ctx, 0, "王计兵"), t, a=a)
    for k, (txt, w, x, y) in enumerate((("初中没念完", "初中", 280, 600), ("木工", "木工", 820, 600),
                                        ("摆地摊", "地摊", 250, 760), ("捡破烂", "破烂", 830, 760))):
        pop_text(c, txt, x, y, 46, word(ctx, 1, w), t, tone=ink.OCHRE, a=a, name="serif_black")
    pop_text(c, "心里一直有话想说", 540, 1340, 50, word(ctx, 2, "心里"), t, tone=ink.CINNABAR, a=a)


def d_stairs(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    t0, t1 = ctx.cue(0), ctx.end(0)
    climb = P(t, t0, t1 - t0)
    art.stairs(c, 140, 1250, 1.0, 9, a * 0.8)
    cx = 180 + climb * 560
    cy = 1250 - climb * 400
    art.courier(c, cx, cy, 0.7, a, climb=1.0 if climb < 1 else 0.0, t=t)
    floor = 1 + int(17 * climb)
    pop_text(c, f"{floor} 层", 820, 470, 110, t0, t, tone=ink.CINNABAR if floor == 18 else ink.INK, a=a)
    tf = word(ctx, 0, "罚了款")
    ink.seal(c, "罚款", 880, 900, 130, t - (tf + 0.1))
    art.cig_box(c, 300, 600, 0.9, 5, P(t, ctx.cue(1), ctx.end(1) - ctx.cue(1) + 0.5), a * P(t, ctx.cue(1) - 0.2, 0.3))


def d_book(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    tb = word(ctx, 1, "2023年")
    k = P(t, tb, 0.5)
    rng = np.random.default_rng(2)
    for i in range(7):
        q = P(t, i * 0.35, 0.3)
        x, y = 540 + rng.uniform(-300, 300) * (1 - k), 800 + rng.uniform(-260, 260) * (1 - k)
        if i % 2:
            art.cig_box(c, x, y, 0.55, 4, 1.0, a * q * (1 - k), rot=rng.uniform(-20, 20), seed=i)
        else:
            c.save()
            c.translate(x, y)
            c.rotate(rng.uniform(-15, 15))
            c.drawRect(skia.Rect.MakeXYWH(-150, -100, 300, 200), ink.paint((222, 214, 196), a * q * (1 - k)))
            for j in range(5):
                c.drawLine(-130, -70 + j * 34, 130, -70 + j * 34, ink.paint(ink.INK, 0.25 * a * q * (1 - k), stroke=4))
            c.restore()
    ink.label(c, "烟盒 · 废报纸", 540, 470, 50, tone=ink.OCHRE, alpha=a * P(t, word(ctx, 0, "烟盒"), 0.3) * (1 - k),
              name="serif_medium")
    art.book_cover(c, 540, 860, 1.1, "赶时间的人", "一个外卖员的诗", a * k)
    pop_text(c, "2023 · 第一本诗集", 540, 1180, 50, tb, t, tone=ink.CINNABAR, a=a)


def d_heart(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    tx, tj = word(ctx, 1, "想写的那颗心"), word(ctx, 1, "技巧")
    art.tree(c, 540, 1010, 0.8, EO(P(t, tx, 1.0)), EO(P(t, tj, 1.5)), P(t, tj + 1.0, 0.8), a)
    pop_text(c, "先学技巧？", 540, 420, 54, ctx.cue(0), t, a=a * (1 - P(t, ctx.cue(1), 0.3)))
    strike(c, 540, 420, 280, ctx.cue(1), t, a * (1 - P(t, ctx.cue(1) + 0.6, 0.3)))
    pop_text(c, "技巧慢慢长出来", 540, 420, 54, tj, t, a=a)
    pop_text(c, "先有想写的心", 540, 1320, 56, tx, t, tone=ink.CINNABAR, a=a)


# ================================================================ 第 4 节 · 升华前行

def d_compare(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    t2 = ctx.cue(2)
    k = P(t, t2, 0.5)
    art.cave(c, 300, 900, 120, 220, a * (1 - k))
    art.scholar_seated(c, 300, 902, 0.42, a * (1 - k), tone=(70, 62, 54), t=t)
    art.stairs(c, 620, 900, 0.6, 5, a * 0.8 * (1 - k))
    art.courier(c, 700, 860, 0.55, a * (1 - k), t=t)
    pop_text(c, "根扎得很深", 540, 1120, 56, word(ctx, 1, "根"), t, tone=ink.CINNABAR, a=a * (1 - k))
    if t >= t2:
        night(c, a * k)
        art.modern_bed_phone(c, 420, 1180, 1.15, a * k, glow=1.0, t=t)
        pop_text(c, "手里什么都有", 540, 470, 60, word(ctx, 2, "手里"), t, a=a)
        pop_text(c, "心里空落落", 540, 570, 60, word(ctx, 2, "心里"), t, tone=ink.CINNABAR, a=a)


def d_life(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    t1, t2 = ctx.cue(1), ctx.cue(2)
    k1, k2 = P(t, t1, 0.3), P(t, t2, 0.3)
    art.subway(c, 540, 1250, 1.0, a * (1 - k1), t=t)
    ts = word(ctx, 0, "收藏")
    if t >= ts:
        ink.seal(c, "收藏", 760, 860, 110, t - ts)
    if t >= t1:
        art.progress_bar(c, 540, 600, 520, 1 / 30, "第 1 节 / 共 30 节", a * k1 * (1 - k2))
        art.books(c, 540, 1100, 1.2, n=4, alpha=a * k1 * (1 - k2))
        pop_text(c, "塑封未拆", 540, 1180, 50, word(ctx, 1, "塑封"), t, tone=ink.CINNABAR, a=a * (1 - k2))
    if t >= t2:
        night(c, a * k2)
        art.modern_bed_phone(c, 420, 1180, 1.15, a * k2, glow=0.3, t=t)
        tm = word(ctx, 2, "明天一定改")
        pop_text(c, "明天一定改", 540, 500, 70, tm, t, a=a)
        tz = word(ctx, 2, "一切照旧")
        strike(c, 540, 500, 380, tz, t, a)
        pop_text(c, "一切照旧", 540, 620, 50, tz + 0.2, t, tone=ink.OCHRE, a=a, name="serif_medium")


def d_hug(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    t1, t2 = ctx.cue(1), ctx.cue(2)
    warm = P(t, 0, 0.8) * (1 - P(t, t1, 0.4))
    c.drawCircle(540, 820, 520, ink.paint((255, 220, 170), 0.35 * warm * a, blur=120))
    hanzi.write(c, "你不是不努力", 540, 760, 130, hanzi.progress(t, 0.1, ctx.end(0) * 0.55), alpha=a * (1 - P(t, t1, 0.3)))
    pop_text(c, "只是太累了，又太怕落后", 540, 960, 50, word(ctx, 0, "太累"), t, tone=ink.CINNABAR, a=a * (1 - P(t, t1, 0.3)))
    tw = word(ctx, 3, "你到底")
    if t >= t1:
        k = P(t, t1, 0.3) * (1 - P(t, tw - 0.3, 0.3))
        art.pot(c, 540, 1100, 1.2, a * k)
        rng = np.random.default_rng(3)
        n = int(14 * EO(P(t, word(ctx, 1, "塞道理"), 1.2)))
        for i in range(n):
            art.fav_card(c, 540 + rng.uniform(-140, 140), 1050 - rng.uniform(40, 340), 170, "道理", alpha=a * k,
                         rot=rng.uniform(-40, 40))
        pop_text(c, "往空花盆里插枝叶", 540, 470, 54, word(ctx, 1, "空花盆"), t, a=a * k * (1 - P(t, t2, 0.25)))
    if t >= t2:
        pop_text(c, "先别急着再装了", 540, 470, 54, t2 + 0.25, t, tone=ink.OCHRE, a=a * (1 - P(t, tw - 0.3, 0.3)),
                 name="serif_medium")
    if t >= tw - 0.3:
        ink.bloom(c, 540, 820, 160, P(t, tw - 0.3, 1.0), seed=4, tone=ink.CINNABAR, alpha=0.55 * a)
        pop_text(c, "你到底想要什么？", 540, 1080, 64, tw, t, a=a)


def d_task(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx)
    ink.seal(c, "今日功课", 230, 480, 160, t - (ctx.cue(0) + 0.1))
    inner = art.phone(c, 760, 900, 0.7, a, glow=0.4)
    tsel = word(ctx, 0, "挑一条")
    left = 300 - int(299 * EO(P(t, tsel, 0.8)))
    ink.label(c, f"收藏 {left}", inner.centerX(), inner.top() + 40, 32, alpha=a)
    shown = 5 if t < tsel else max(1, 5 - int(5 * P(t, tsel, 0.6)))
    for k in range(shown):
        art.fav_card(c, inner.centerX(), inner.top() + 110 + k * 62, inner.width() - 26, "干货" if k else "我最想做到的",
                     alpha=a)
    tw = word(ctx, 0, "我为什么想要它")
    ink.label(c, "我为什么想要它？", 300, 900, 46, alpha=a * P(t, tw, 0.4), name="serif_black")
    pop_text(c, "做一小步", 300, 1060, 64, word(ctx, 1, "一小步"), t, tone=ink.CINNABAR, a=a)


def d_fire1(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx, fade_in=0.1, fade_out=0.15)
    t1, t2 = ctx.cue(1), ctx.cue(2)
    if t < t1:
        pop_text(c, "别等准备好", 540, 640, 96, 0.0, t, a=a)
        pop_text(c, "别等道理攒够", 540, 820, 96, word(ctx, 0, "别等道理"), t, tone=ink.CINNABAR, a=a)
    elif t < t2:
        backdrop(c, t, a * 0.7, y=380)
        art.cave(c, 540, 1230, 220, 400, a)
        tf = word(ctx, 1, "翻过来")
        jump = math.sin(math.pi * P(t, tf, 0.45)) * 80
        art.scholar_standing(c, 540, 1232 - jump, 0.75, a, tone=(70, 62, 54))
        rays(c, 540, 1000, t, tf, a, r1=420)
        pop_text(c, "把命运翻过来", 540, 470, 70, tf, t, tone=ink.CINNABAR, a=a)
    else:
        tk = word(ctx, 2, "多得多")
        art.window(c, 540, 900, 1.15, EO(P(t, t2, 0.6)), a, light=P(t, t2 + 0.2, 0.6))
        pop_text(c, "比他多得多！", 540, 460, 84, tk, t, tone=ink.CINNABAR, a=a)


def d_fire2(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx, fade_in=0.1)
    t1, t2 = ctx.cue(1), ctx.cue(2)
    sun = P(t, t1, 0.6)
    c.drawCircle(540, 760, 700, ink.paint((255, 214, 150), 0.45 * sun * a, blur=160))
    if t < t2:
        art.tree(c, 540, 820, 1.0, EO(P(t, 0, 1.0)), EO(P(t, 0.4, 1.0)), 1.0, a * (1 - 0.5 * sun))
        pop_text(c, "根扎下了，路就在脚下", 540, 1180, 56, 0.0, t, a=a * (1 - sun))
        rays(c, 540, 820, t, t1, a, n=18, r1=600, spread=1.0)
        pop_text(c, "心亮起来，人就站起来！", 540, 1180, 60, word(ctx, 1, "心亮起来"), t, tone=ink.CINNABAR, a=a)
    else:
        tg = word(ctx, 2, "出发")
        hanzi.write(c, "出发", 540, 820, 330, hanzi.progress(t, tg - 0.15, 0.7), alpha=a)
        ink.seal(c, "心即理", 860, 1110, 170, t - (tg + 0.7))
        ink.brush_path(c, ink.smooth([(200, 1300), (540, 1250), (880, 1180)], 30), 22, p=P(t, tg + 0.3, 0.5),
                       tone=ink.CINNABAR, alpha=a)


def d_next(ctx):
    c, t, a = ctx.c, ctx.t, env(ctx, fade_out=1.0)
    dawn = P(t, 0, 1.5)
    c.drawRect(skia.Rect.MakeLTRB(0, 300, gfx.W, 1350), ink.paint((255, 236, 200), 0.2 * dawn * a, blur=60))
    backdrop(c, t, a * 0.8, y=420)
    tk = word(ctx, 0, "知行合一")
    ink.label(c, "下一讲", 540, 520, 44, tone=ink.OCHRE, alpha=a * P(t, 0.1, 0.3), name="serif_medium")
    ink.label(c, "知道却做不到，怎么办？", 540, 610, 50, alpha=a * P(t, 0.2, 0.3), name="serif_black")
    hanzi.write(c, "知行合一", 540, 820, 170, hanzi.progress(t, tk, 1.1), alpha=a)


def scenes():
    hanzi.prepare(CALLI)
    S = E.scene
    return [
        S("hook", 1, [0], d_hook, [("dagu", 0, "却依然", 0.0)], marks={0: ("过不好这一生",)}),
        S("bamboo", 2, [0, 1, 2, 3], d_bamboo, [("tanggu", 1, "七天", 0.0), ("dagu", 2, "病倒", 0.0)], marks={2: ("病倒",)}),
        S("exile", 2, [4, 5, 6], d_exile,
          [("daluo", 0, "四十廷杖", 0.0), ("muyu", 2, "官没了", -0.15), ("muyu", 2, "名没了", -0.15),
           ("muyu", 2, "书也没了", -0.15)], marks={0: ("四十廷杖",)}),
        S("coffin", 2, [7, 8, 9], d_coffin, [("tanggu", 2, "石棺", -0.2)], marks={2: ("石棺",)}),
        S("care", 2, [10, 11, 12], d_care, [("bangzi", 1, None, 0.2)], marks={2: ("还能怎么办",)}),
        S("wake", 2, [13, 14, 15], d_wake, [("bangzi", 0, "跳起来", 0.0), ("bianzhong", 1, "善意", 0.0)],
          marks={1: ("善意",)}),
        S("gold", 2, [16, 17], d_gold, [("dagu", 1, "心即理", -0.2)], marks={0: ("自己心里",), 1: ("心即理",)}),
        S("why", 2, [18, 19], d_why, [("tanggu", 1, "扎根", 0.0)], marks={1: ("扎根",)}),
        S("root", 3, [0, 1], d_root, [("muyu", 0, "真心是根", 0.0)], marks={0: ("真心是根",)}),
        S("wang", 3, [2, 3, 4], d_wang, [("bangzi", 0, "王计兵", 0.0)], marks={0: ("王计兵",)}),
        S("stairs", 3, [5, 6], d_stairs, [("daluo", 0, "罚了款", 0.1)], marks={0: ("十八层",)}),
        S("book", 3, [7, 8], d_book, [("dagu", 1, "2023年", 0.0)], marks={1: ("赶时间的人",)}),
        S("heart", 3, [9, 10], d_heart, [("tanggu", 1, "想写的那颗心", 0.0)], marks={1: ("想写的那颗心",)}),
        S("compare", 4, [0, 1, 2], d_compare, [("dagu", 2, "手里", 0.0)], marks={2: ("心里却空落落",)}),
        S("life", 4, [3, 4, 5], d_life, [("muyu", 0, "收藏", 0.0), ("muyu", 2, "一切照旧", 0.0)],
          marks={2: ("一切照旧",)}),
        S("hug", 4, [6, 7, 8, 9], d_hug, [("bianzhong", 0, None, 0.1)], marks={0: ("你不是不努力",), 3: ("你到底想要什么",)}),
        S("task", 4, [10, 11], d_task, [("daluo", 0, None, 0.1)], marks={0: ("我为什么想要它",)}),
        S("fire1", 4, [12, 13, 14], d_fire1,
          [("dagu", 0, None, 0.0), ("dagu", 0, "别等道理", 0.0), ("dagu", 1, "翻过来", 0.0), ("dagu", 2, "多得多", 0.0)],
          marks={0: ("别等准备好了",), 2: ("比他多得多",)}),
        S("fire2", 4, [15, 16, 17], d_fire2,
          [("dagu", 0, None, 0.0), ("dagu", 1, "心亮起来", 0.0), ("daluo", 2, "出发", -0.15)],
          marks={1: ("人就站起来",), 2: ("现在，就出发",)}),
        S("next", 4, [18], d_next, [("bianzhong", 0, "知行合一", 0.0)], marks={0: ("知行合一",)}, tail=2.0),
    ]


MUSIC = [("compare", 2, "low", "可我们呢"), ("fire1", 0, "full")]


def video() -> InkVideo:
    return InkVideo(scenes(), HEADER, drop_at="bamboo", music=MUSIC)
