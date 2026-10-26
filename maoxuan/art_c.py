"""《毛选》05–07 讲专用元件：三幕戏舞台、平台期曲线、远山目标、打卡格、力量对比、草原火势、
桅杆航船、日出、波浪式扩大、根据地与流动、关系图、半圆占比。坐标以元素中心为原点。"""

import math

import skia

from adler import fx
from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from xingzuo.art import fire

GRASS = "#B9A35A"
SEA = "#5B8DB8"
SUN = "#F2B441"


# ---------------------------------------------------------------- 论持久战：三幕戏

def stage3(c, g, el_t, d):
    """三幕戏舞台：幕布在 open 拍拉开，三块幕牌 acts 依次在 b0 起每拍亮起；hi 指定的那一幕在 hi_at 拍放大发光。"""
    w, h = 900, 620
    K.rr(c, 0, -h / 2 - 20, w + 40, 60, 10, "#7A2E26")
    K.rr(c, 0, h / 2 + 10, w + 40, 50, 8, "#6B4A33")
    K.rr(c, 0, 0, w, h, 6, "#3B2E2A")
    acts = d.get("acts", ())
    hi, hi_at = d.get("hi"), d.get("hi_at", 99)
    for i, (title, sub) in enumerate(acts):
        x = (i - 1) * 290
        st = fx.word_pop(g.since(d.get("b0", 1) + i))
        if st is None:
            continue
        a, s_, _ = st
        big = hi == i and g.since(hi_at) >= 0
        k = ease_out(clamp01(g.since(hi_at) / 0.3)) if big else 0
        if big:
            fx.glow(c, x, 0, 260, K.GOLD, 0.5 * k)
        with K.at(c, x, 0, 0, s_ * (1 + 0.18 * k)):
            K.card(c, 0, 0, 250, 380, K.GOLD if big else K.PAPER, a, r=16)
            K.text(c, title, 0, -110, 52, "serif_black", K.PAPER if big else g.acc, a)
            for j, line in enumerate(sub.split("|")):
                K.text(c, line, 0, 10 + j * 64, 44, "serif_black", K.PAPER if big else K.INK, a)
    k = ease_in_out(clamp01(g.since(d.get("open", 0)) / 0.6))
    cw = (w / 2) * (1 - k) + 40
    for sx in (-1, 1):
        x0 = sx * w / 2
        K.rr(c, x0 - sx * cw / 2, 0, cw, h, 4, "#A8342B")
        for j in range(4):
            xx = x0 - sx * cw * (j + 0.5) / 4
            K.seg(c, xx, -h / 2, xx, h / 2, K.shade("#A8342B", 0.25), 4)


def plateau(c, g, el_t, d):
    """进度曲线：先升、中段长长一段平台、再陡升；小人沿曲线从 b0 走到 b1；label_at 拍在平台处弹出标签。"""
    w, h = 860, 520
    K.seg(c, -w / 2, h / 2, w / 2, h / 2, K.INK2, 6)
    K.seg(c, -w / 2, h / 2, -w / 2, -h / 2, K.INK2, 6)

    def f(u):
        if u < 0.25:
            return 0.35 * ease_out(u / 0.25)
        if u < 0.72:
            return 0.35 + 0.06 * (u - 0.25) / 0.47
        return 0.41 + 0.55 * ((u - 0.72) / 0.28) ** 1.6

    k = g.span(d.get("b0", 0), d.get("b1", 3), ease=lambda x: x)
    p = skia.Path()
    for i in range(81):
        u = i / 80
        (p.moveTo if i == 0 else p.lineTo)(-w / 2 + u * w, h / 2 - f(u) * h)
    c.drawPath(p, K.paint(K.LINE, 1, 12))
    q = skia.Path()
    n = max(1, int(80 * k))
    for i in range(n + 1):
        u = k * i / n
        (q.moveTo if i == 0 else q.lineTo)(-w / 2 + u * w, h / 2 - f(u) * h)
    c.drawPath(q, K.paint(g.acc, 1, 12))
    x, y = -w / 2 + k * w, h / 2 - f(k) * h
    K.dot(c, x, y, 22, g.acc)
    fx.glow(c, x, y, 80, K.GOLD, 0.4)
    la = d.get("label_at")
    if la is not None:
        st = fx.word_pop(g.since(la))
        if st:
            a, s_, _ = st
            with K.at(c, -w / 2 + 0.48 * w, h / 2 - 0.38 * h - 110, 0, s_):
                K.pill(c, 0, 0, d.get("label", "最困难 · 转折点"), 44, K.RED, K.PAPER, a)
    if d.get("goal"):
        K.icon(c, "flag", w / 2 - 40, -h / 2 - 20, 110, K.GOLD, 1, 0.5)


def mountain_goal(c, g, el_t, d):
    """远山目标：一座山，山顶旗子；山脚小人；zoom 拍起山被“拉远”变小（目标太远）。"""
    k = ease_out(clamp01(g.since(d.get("zoom", 99)) / 0.5))
    s = 1 - 0.45 * k
    with K.at(c, 0, -80 * k, 0, s):
        K.poly(c, [(-430, 260), (-60, -360), (60, -260), (180, -330), (470, 260)], "#8FA3A8")
        K.poly(c, [(-130, -240), (-60, -360), (10, -280), (-40, -250)], K.PAPER)
        K.icon(c, "flag", -60, -420, 120, K.RED, 1, 0.5)
    K.pill(c, 280, -380, d.get("goal", "目标"), 50, g.acc, K.PAPER)
    K.figure(c, -330, 300, 220, "stand", K.HERO, mood="worried" if k > 0 else "calm", hair="short", role="worker")


def tally(c, g, el_t, d):
    """打卡格：n 天，b0 起每 step 拍打一个勾；quit 拍之后的格子打叉（半途放弃）。"""
    n, cols = d.get("n", 14), 7
    quit_ = d.get("quit")
    cw = 110
    h = (n // cols) * cw + 160
    K.card(c, 0, 0, cols * cw + 60, h, K.PAPER, 1, r=24, accent=g.acc)
    K.text(c, d.get("title", "打卡"), 0, -h / 2 + 62, 46, "serif_black", K.INK)
    for i in range(n):
        x = -cols * cw / 2 + cw / 2 + (i % cols) * cw
        y = -(n // cols) * cw / 2 + cw / 2 + 30 + (i // cols) * cw
        K.rr_stroke(c, x, y, cw - 18, cw - 18, 12, K.LINE, 4)
        bad = quit_ is not None and i >= d.get("quit_n", 3)
        b = (quit_ if bad else d.get("b0", 0) + i * d.get("step", 0.5))
        st = fx.word_pop(g.since(b))
        if st:
            a, s_, _ = st
            with K.at(c, x, y, 0, s_):
                K.icon(c, "cross" if bad else "check", 0, 0, 70, K.RED if bad else K.GREEN, a, 0.3)


def power(c, g, el_t, d):
    """力量对比：左“我的力量”柱、右“难度”柱；grow 拍起左柱变高超过右柱，越线时金光。"""
    k = ease_out(clamp01(g.since(d.get("grow", 1)) / 0.9))
    me = lerp(d.get("me0", 0.3), d.get("me1", 0.95), k)
    them = lerp(d.get("them0", 0.8), d.get("them1", 0.6), k)
    for x, v, col, lab in ((-180, me, g.acc, d.get("left", "自己的力量")), (180, them, K.INK2, d.get("right", "困难"))):
        h = 520 * v
        K.rr(c, x, 260 - h / 2, 200, h, 18, col)
        K.text(c, lab, x, 330, 44, "serif_black", K.INK)
    if me > them:
        fx.glow(c, -180, 260 - 520 * me, 160, K.GOLD, 0.5)
        K.icon(c, "crown", -180, 200 - 520 * me, 110, K.GOLD, 1, 0.4)
    K.seg(c, -340, 260, 340, 260, K.INK2, 6)


# ---------------------------------------------------------------- 星星之火

def prairie(c, g, el_t, d):
    """草原：一排枯草；spark 拍一粒火星落下，之后火势从中间向两边蔓延，b1 拍烧满（燎原）。"""
    w = 960
    n = 15
    sp = d.get("spark", 0)
    k = g.span(sp + 0.5, d.get("b1", 3), ease=lambda x: x) if g.since(sp + 0.5) >= 0 else 0
    for i in range(n):
        x = -w / 2 + w * (i + 0.5) / n
        K.poly(c, [(x - 26, 200), (x - 8, 80), (x, 190), (x + 10, 60), (x + 26, 200)], GRASS)
    K.rr(c, 0, 210, w, 30, 8, K.shade(GRASS, 0.3))
    ds = g.since(sp)
    if ds >= 0:
        y = lerp(-420, 120, clamp01(ds / 0.4))
        if ds < 0.4:
            K.star(c, 0, y, 26, K.GOLD)
        else:
            reach = k * (w / 2 + 40)
            for i in range(n):
                x = -w / 2 + w * (i + 0.5) / n
                if abs(x) <= reach + 1e-6 or (i == n // 2):
                    s = 120 + 110 * clamp01((reach - abs(x)) / 200 + 0.3)
                    fire(c, x, 110 - s * 0.2, s, g.t + i * 0.37, 1.0, glow=i % 3 == 0)


def ship_mast(c, g, el_t, d):
    """海平线：一只航船从海平线下 b0→b1 拍升起，先露桅杆尖头，再露船身。"""
    K.rr(c, 0, 160, 960, 360, 10, K.tint(SEA, 0.35))
    K.seg(c, -480, -20, 480, -20, SEA, 6)
    k = g.span(d.get("b0", 0), d.get("b1", 3))
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(-480, -480, 480, -20))
    y = lerp(260, -40, k)
    K.seg(c, 0, y, 0, y - 300, K.INK2, 10)
    K.poly(c, [(8, y - 290), (150, y - 120), (8, y - 110)], K.PAPER)
    K.poly(c, [(-8, y - 260), (-120, y - 110), (-8, y - 100)], K.tint(K.PAPER, 0.2))
    K.rr(c, 0, y - 300, 40, 20, 4, K.RED)
    K.poly(c, [(-180, y - 40), (180, y - 40), (130, y + 40), (-130, y + 40)], "#7A5A3A")
    c.restore()
    if k > 0.15:
        K.pill(c, 260, -340, d.get("label", "桅杆尖头"), 44, g.acc, K.PAPER, clamp01((k - 0.15) / 0.2))
    K.figure(c, -360, 120, 200, "point", None, hair="short", mood="happy", role=d.get("role", "youth"))


def sunrise(c, g, el_t, d):
    """山巅日出：太阳从山后 b0→b1 拍升起，光芒四射。"""
    k = g.span(d.get("b0", 0), d.get("b1", 3))
    y = lerp(240, -170, k)
    fx.rays(c, 0, y, 700, SUN, g.t, 16, 0.25 * k)
    fx.glow(c, 0, y, 360, SUN, 0.55 * k)
    K.dot(c, 0, y, 130, SUN)
    K.poly(c, [(-520, 330), (-200, 20), (-40, 150), (140, -20), (520, 330)], "#6E7F5A")
    K.poly(c, [(-520, 330), (-330, 170), (-150, 260), (520, 330)], K.shade("#6E7F5A", 0.25))
    if d.get("watcher"):
        K.figure(c, -200, 30, 170, "point", None, mood="happy", face=1, role=d["watcher"])


def waves(c, g, el_t, d):
    """波浪式扩大：中心一块根据地，b0 起每拍向外扩一圈（实心填色），每圈像一道浪推出去。"""
    n = d.get("n", 4)
    for i in reversed(range(n)):
        dt = g.since(d.get("b0", 0) + i)
        if dt < 0:
            continue
        k = ease_out(clamp01(dt / 0.45))
        r = (90 + i * 95) * k
        c.drawCircle(0, 0, r, K.paint(K.tint(g.acc, 0.25 + 0.17 * i)))
        K.ripple(c, 0, 0, dt, g.acc, r + 60, 5)
    K.dot(c, 0, 0, 70, g.acc)
    K.text(c, d.get("core", "根据地"), 0, 0, 40, "serif_black", K.PAPER)


def base_vs_roam(c, g, el_t, d):
    """左：东一点西一点的流动小点（opacity 闪烁，留不住）；右：一块越来越实的方块（根据地）。b 拍打叉/打勾。"""
    for i in range(7):
        a = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(g.t * 5 + i * 1.7))
        x, y = -260 + math.sin(i * 2.3) * 140, math.cos(i * 1.9) * 200
        K.dot(c, x, y, 26, K.INK2, a)
    K.text(c, "到处跑", -260, 290, 44, "serif_black", K.INK)
    k = ease_out(clamp01(g.since(d.get("grow", 1)) / 0.6))
    K.rr(c, 260, 0, 120 + 160 * k, 120 + 160 * k, 20, g.acc)
    K.text(c, "扎根", 260, 0, 54, "serif_black", K.PAPER)
    K.text(c, "一块地方", 260, 290, 44, "serif_black", K.INK)
    b = d.get("b", 2)
    st = fx.word_pop(g.since(b))
    if st:
        a, s_, _ = st
        with K.at(c, -260, -300, 0, s_):
            K.icon(c, "cross", 0, 0, 100, K.RED, a, 0.3)
        with K.at(c, 260, -300, 0, s_):
            K.icon(c, "check", 0, 0, 100, K.GREEN, a, 0.3)


def magnify_split(c, g, el_t, d):
    """一时的小挫折被放大：左边小小一块乌云，grow 拍被放大镜放大成满屏乌云（扩大化）。"""
    k = ease_out(clamp01(g.since(d.get("grow", 1)) / 0.5))
    s = lerp(0.5, 1.9, k)
    K.icon(c, "cloud", 0, -60, 220 * s, K.INK2, 1, 0.6)
    K.pill(c, 0, 240, d.get("label", "一次挫折"), 44, K.INK, K.PAPER)
    if k > 0:
        K.text(c, "全完了", 0, -60, 70 * s * 0.6, "serif_black", K.PAPER, k)


# ---------------------------------------------------------------- 谁是朋友

def relation_map(c, g, el_t, d):
    """关系图：中心“我”，周围 people [(标签, 立场, 角度)]，第 i 人在 b0 + i*step 拍出现；
    shown 拍起按立场染色（支持=绿 / 中立=金 / 阻力=灰红），并连线；pull 拍起中立者向中心靠拢。"""
    col = {"支持": K.GREEN, "中立": K.GOLD, "阻力": "#A35A4E", "?": K.INK3}
    shown = g.since(d.get("shown", 99)) >= 0
    pk = ease_out(clamp01(g.since(d.get("pull", 99)) / 0.6))
    people = d["people"]
    R = d.get("r", 330)
    for i, (lab, side, ang) in enumerate(people):
        st = fx.word_pop(g.since(d.get("b0", 0) + i * d.get("step", 0.5)))
        if st is None:
            continue
        a, s_, _ = st
        r = R * (1 - 0.35 * pk if side == "中立" else 1)
        x, y = math.cos(math.radians(ang)) * r, math.sin(math.radians(ang)) * r * 0.85
        cc = col[side] if shown else col["?"]
        if shown and side != "阻力":
            K.seg(c, 0, 0, x, y, cc, 6, 0.6)
        with K.at(c, x, y, 0, s_):
            K.dot(c, 0, 0, 62, cc, a)
            K.text(c, lab, 0, 0, 34, "serif_black", K.PAPER, a)
    fx.glow(c, 0, 0, 140, K.GOLD, 0.3)
    K.dot(c, 0, 0, 78, K.HERO)
    K.text(c, "我", 0, 0, 56, "serif_black", K.PAPER)
    if shown and d.get("legend", True):
        for j, side in enumerate(("支持", "中立", "阻力")):
            K.pill(c, -260 + j * 260, 430, side, 36, col[side], K.PAPER)


def half_pie(c, g, el_t, d):
    """占比饼：一个圆，fill 拍起金色扇区扫到一半，中间“一半”。"""
    k = ease_out(clamp01(g.since(d.get("fill", 1)) / 0.6))
    K.dot(c, 0, 0, 260, K.LINE)
    p = skia.Path()
    p.moveTo(0, 0)
    p.arcTo(skia.Rect.MakeXYWH(-260, -260, 520, 520), -90, 180 * k, False)
    p.close()
    c.drawPath(p, K.paint(K.GOLD))
    K.dot(c, 0, 0, 140, K.PAPER)
    K.text(c, d.get("text", "一半"), 0, 0, 70, "serif_black", K.INK, k)
    if d.get("sub"):
        K.text(c, d["sub"], 0, 330, 44, "serif_black", K.INK2)


def three_groups(c, g, el_t, d):
    """三组人：左（右翼）、中（中立，人最多）、右（左翼），b0 起每拍出现一组；sun 拍日出光，三组都朝光的方向转身。"""
    sun = g.since(d.get("sun", 99)) >= 0
    k = ease_out(clamp01(g.since(d.get("sun", 99)) / 0.5))
    if sun:
        fx.rays(c, 0, -360, 600, SUN, g.t, 14, 0.25 * k)
        K.dot(c, 0, -360, 90, SUN, k)
    groups = d.get("groups", (("观望", 2, -360), ("中立", 4, 0), ("支持", 2, 360)))
    cols = (K.OTHER, K.GOLD, K.GREEN)
    roles = d.get("roles")
    for i, (lab, n, x0) in enumerate(groups):
        st = fx.word_pop(g.since(d.get("b0", 0) + i))
        if st is None:
            continue
        a, s_, _ = st
        for j in range(n):
            x = x0 + (j - (n - 1) / 2) * 92
            mood = "happy" if sun else "calm"
            pose = "cheer" if sun and i > 0 else "stand"
            K.figure(c, x + (-x0 * 0.15 * k), 260, 210, pose, cols[i], alpha=a, mood=mood,
                     hair=("short", "bun", "long")[j % 3], face=1 if x < 0 else -1,
                     role=roles[i] if roles else ("worker", "worker_f")[j % 2])
        K.pill(c, x0, 340, lab, 40, cols[i], K.PAPER, a)


def crowd_roles(c, g, el_t, d):
    """一排古今人物：roles 依次循环取造型，spread 内均匀排开，轻微呼吸起伏，都朝向中心。"""
    roles = d.get("roles", ("farmer", "scholar", "woman", "merchant", "youth", "soldier"))
    n, s, spread = d.get("n", 6), d.get("s", 250), d.get("spread", 820)
    moods = d.get("moods", ("calm", "smile", "flat", "open"))
    for i in range(n):
        x = -spread / 2 + spread * i / max(1, n - 1)
        bob = 0.006 * math.sin(g.t * 2.4 + i)
        K.figure(c, x, 0, s * (0.94 + 0.06 * (i % 2)), d.get("pose", "stand"), None, mood=moods[i % len(moods)],
                 face=1 if x < 0 else -1, bob=bob, role=roles[i % len(roles)])
