"""《为什么一到晚上，就觉得自己的人生不行了》15 个镜头的场景绘制。

每个函数签名 (c, t, D, cue, view)：c 为已映射到舞台单位的画布；t 为镜头内时间；D 为镜头时长；
cue 为本镜事件时刻表（键 → 镜头内秒），撞击动作一律读 cue，保证音效校准后画面同步移动；view 为可见舞台范围。
"""

import math

import numpy as np
import skia

from kepu import draw as d
from kepu.config import GOLD, WHITE
from kepu.props import (
    C1, C2, DOOR, F, FIG9, LOOP, PERIOD, REC, RING, THUMBS, bedroom, book, cell, city, desk, doc_on_desk,
    door, event_icon, inlet, lap_shade, loop_floor, mark_pos_on_doc, paragraph, problem_card, ring_card,
    ring_floor, sheet, vague_label, walker, window,
)


def shot01(c, t, D, cue, view):
    s = 2.4 + 0.75 * d.ease_out(d.prog(t, cue["surge"] - F, 0.3)) + 0.08 * t / D
    c.save()
    k = 1 + 0.03 * t / D
    c.translate(500, 560)
    c.scale(k, k)
    c.translate(-500, -560)
    j, pos = bedroom(c, t, view, s, city=1.0, card_rot=-8 - 4 * d.ease_out(d.prog(t, cue["surge"] - F, 0.3)))
    d.glow(c, pos[0], pos[1], 90, GOLD, 0.25 * d.pulse(t, cue["surge"], 0.6))
    c.restore()


def shot02(c, t, D, cue, view):
    desk(c, view)
    grow = d.ease_out(d.prog(t, 0, 0.6))
    scale = 0.45 + 0.55 * grow
    doc_on_desk(c, scale=scale, frame_k=d.prog(t, cue["frame"] - F, 0.35),
                tick_k=d.prog(t, cue["frame"] + 0.5, 1.2))
    if t > cue["frame"]:
        x, y = mark_pos_on_doc()
        d.glow(c, x, y, 120, GOLD, 0.22 * d.pulse(t, cue["frame"], 0.6))


def shot03(c, t, D, cue, view):
    desk(c, view)
    pull = d.ease_io(d.prog(t, cue["pull"], D - 0.4 - cue["pull"]))
    zoom = 1 - 0.55 * pull
    c.save()
    c.translate(500, 480)
    c.scale(zoom, zoom)
    c.translate(-500, -480 - 260 * pull)
    # 其余工作记录：小卡片 + 正常勾选
    grow = d.ease_in(d.prog(t, 0.3, cue["cover"] - 0.3))
    mx, my = 500, 485
    R = 60 + grow * 820
    for i, (x, y) in enumerate(REC):
        dist = math.hypot(x - mx, y - my)
        covered = d.clamp01((R * 0.62 - dist + 60) / 60)
        if covered >= 1:
            continue
        d.paper(c, x, y, 150, 110, rot=(i * 37 % 9) - 4, lines=3, ticks=3, lift=0.5, line_seed=i,
                a=1 - covered * 0.6)
    # 膨胀的修改卡
    scale = 1 + grow * 6.2
    d.mark_card(c, mx, my, w=130 * scale, h=88 * scale, rot=-3 * (1 - grow), lift=1 + grow * 3,
                shade=0.35 * grow)
    c.restore()
    # 后退后显露的卡片城市（楼宇由叠放的纸卡构成）
    if pull > 0:
        city(c, view, pull)
    d.glow(c, 500, 560, 260, GOLD, 0.15 * d.pulse(t, cue["cover"], 0.5))


def shot04(c, t, D, cue, view):
    d.backdrop(c, view)
    laps = [cue["lap"], cue["lap"] + PERIOD, cue["lap"] + 2 * PERIOD]
    tt = t - cue["lap"]
    ang = math.pi / 2 + 2 * math.pi * tt / PERIOD
    shade = lap_shade(t, laps)
    inlet(c, 900, 360)
    ring_floor(c, glow_k=max(d.pulse(t, la, 0.4) for la in laps))
    # 拖影：前若干时刻的位置，颜色同当前
    for k in range(5, 0, -1):
        a2 = ang - k * 0.16
        cx, cy, rx, ry = RING
        c.drawCircle(cx + rx * math.cos(a2), cy + ry * math.sin(a2) - 60, 4, d.fill(GOLD, 0.08 * (6 - k)))
    behind = math.sin(ang) < 0
    if behind:
        ring_card(c, ang, shade)
        c.drawPath(d.ellipse_path(*RING[:2], RING[2] * 0.25, RING[3] * 0.25), d.fill("#141519"))
    else:
        ring_card(c, ang, shade)
    x, y = RING[0], RING[1] + RING[3]
    d.glow(c, x, y - 60, 120, GOLD, 0.25 * max(d.pulse(t, la, 0.5) for la in laps))


def shot05(c, t, D, cue, view):
    d.backdrop(c, view)
    # 承接镜头 04 结尾位置，0.5 秒内减速停下
    t4 = cue["_t4"]                          # 镜头 04 结束时距其首圈的时间，由渲染器注入
    halt = cue["halt"]
    tau = min(t, halt) - (min(t, halt) ** 2) / (2 * halt)
    ang = math.pi / 2 + 2 * math.pi * (t4 + tau) / PERIOD
    shift = d.ease_io(d.prog(t, halt, 0.8))
    ring = (500 - 230 * shift, 560, 330 * (1 - 0.32 * shift), 118 * (1 - 0.32 * shift))
    ring_floor(c, ring=ring)
    ring_card(c, ang, 0.9 - 0.0 * shift, ring=ring, size=1 - 0.25 * shift)
    # 通向桌面的短路径
    k = d.ease_out(d.prog(t, halt + 0.4, 1.2))
    if k > 0:
        x0, y0 = ring[0] + ring[2] + 20, 560
        x1 = x0 + (790 - x0) * k
        c.drawLine(x0, y0, x1, y0, d.stroke(GOLD, 3, 0.85, dash=((16, 10), 0)))
        if k > 0.95:
            c.drawLine(x1 - 16, y0 - 12, x1, y0, d.stroke(GOLD, 3))
            c.drawLine(x1 - 16, y0 + 12, x1, y0, d.stroke(GOLD, 3))
        a = d.prog(t, halt + 1.2, 0.6)
        if a > 0:
            c.drawRect(skia.Rect.MakeLTRB(800, 590, 960, 606), d.fill("#2A2824", a))
            c.drawLine(800, 590, 960, 590, d.stroke(GOLD, 1.5, 0.5 * a))
            c.drawRect(skia.Rect.MakeLTRB(815, 606, 825, 690), d.fill("#1F1E1B", a))
            c.drawRect(skia.Rect.MakeLTRB(935, 606, 945, 690), d.fill("#1F1E1B", a))
            d.paper(c, 880, 560, 92, 60, rot=-4, lines=3, lift=0.3, a=a, line_seed=2)


def shot06(c, t, D, cue, view):
    d.backdrop(c, view)
    m = cue["merge"]
    for i, (x, y, rot, depth, delay) in enumerate(THUMBS):
        k = d.ease_in(d.prog(t, 0.2 + delay, m - 0.2 - delay))
        if k >= 1:
            continue
        px, py = d.lerp(x, 500, k), d.lerp(y, 520, k)
        s = depth * (1 - 0.3 * k)
        blur_far = depth < 0.85
        c.save()
        if blur_far:
            c.saveLayerAlpha(None, 200)
        d.paper(c, px, py + 8 * math.sin(t * 1.3 + i), 110 * s, 145 * s, rot=rot * (1 - k), lines=6,
                lift=0.6 * s, line_seed=i)
        if blur_far:
            c.restore()
        c.restore()
    if t >= m - 1e-6:
        pop = d.ease_out(d.prog(t, m, 0.35))
        book(c, 500, 520, s=1.12 - 0.12 * pop)
        d.sparks(c, 500, 520, t, m, n=18, r=260, seed=6)
        d.glow(c, 500, 520, 340, GOLD, 0.6 * d.pulse(t, m, 0.7))


def shot07(c, t, D, cue, view):
    d.room(c, view, floor_y=600)
    loop_floor(c)
    door(c, *DOOR, glint=d.pulse(t, cue["door"], 0.6))
    ang, behind, paint = walker(c, t, cue["walk"], cue["door"])
    if behind:
        paint()
        problem_card(c)
    else:
        problem_card(c)
        paint()


def shot08(c, t, D, cue, view):
    d.room(c, view, floor_y=600)
    fade = d.ease_io(d.prog(t, 0, 0.8))
    loop = (LOOP[0] - 170 * fade, LOOP[1], LOOP[2] * (1 - 0.45 * fade), LOOP[3] * (1 - 0.45 * fade))
    loop_floor(c, ring=loop, a=1 - 0.4 * fade)
    problem_card(c, x=loop[0], y=loop[1], a=1 - 0.5 * fade)
    # 分叉的另一条路径
    k = d.ease_out(d.prog(t, 0.4, cue["fact"] - 0.6))
    x0, y0 = loop[0] + loop[2], loop[1]
    x1 = 640
    c.drawLine(x0, y0, d.lerp(x0, x1, k), d.lerp(y0, 470, k), d.stroke(GOLD, 3, 0.9))
    if k > 0:
        c.drawCircle(d.lerp(x0, x1, k), d.lerp(y0, 470, k), 6, d.fill(GOLD))
    # 文件分成事实格与行动格（只用图形）
    fk = d.ease_back(d.prog(t, cue["fact"], 0.4), 1.6)
    ak = d.ease_back(d.prog(t, cue["act"], 0.4), 1.6)
    base_a = d.prog(t, 0.6, 0.5)
    if fk <= 0:
        d.paper(c, 790, 470, 230, 300, lines=8, lift=0.8, a=base_a, line_seed=8)
    else:
        lx = d.lerp(790, 700, fk)
        cell(c, lx, 470, "fact", a=1.0)
        if ak <= 0:
            d.paper(c, d.lerp(790, 860, fk), 470, 140, 220, lines=5, lift=0.6, line_seed=9)
        else:
            cell(c, d.lerp(860, 880, ak), 470, "act", a=1.0)
        d.glow(c, 700, 470, 120, GOLD, 0.25 * d.pulse(t, cue["fact"], 0.5))
        d.glow(c, 880, 470, 120, GOLD, 0.25 * d.pulse(t, cue["act"], 0.5))


def shot09(c, t, D, cue, view):
    d.room(c, view, floor_y=760)
    f = d.ease_in(d.prog(t, 0.1, cue["fold"] - 0.1))
    # 手风琴式折叠：面板数 4 → 1，宽高同时收拢，颜色由暗转亮
    W0, H0 = 1100, 900
    W1, H1 = 300, 400
    w, h = d.lerp(W0, W1, f), d.lerp(H0, H1, f)
    cx, cy = d.lerp(500, 400, f), d.lerp(470, 470, f)
    shade = 0.85 * (1 - f)
    panels = 4
    d.soft_shadow(c, cx, cy, w, h, lift=1.5, a=0.7)
    for i in range(panels):
        y0 = cy - h / 2 + i * h / panels
        tone = d.mix(d.mix(WHITE, d.PAPER_DIM, shade), "#000000", (0.18 if i % 2 else 0.0) * math.sin(f * math.pi))
        c.drawRect(skia.Rect.MakeLTRB(cx - w / 2, y0, cx + w / 2, y0 + h / panels + 1), d.fill(tone))
    c.drawRect(skia.Rect.MakeLTRB(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), d.stroke(GOLD, 2, 0.5))
    if f < 1:
        path = d.skyline_path(cx - w / 2, cy + h / 2, w, h * 0.55, seed=7)
        c.drawPath(path, d.fill("#000000", 0.5 * (1 - f)))
    else:
        for i in range(7):
            yy = cy - h / 2 + 60 + i * 44
            c.drawLine(cx - w * 0.36, yy, cx + w * (0.2 if i % 3 == 2 else 0.34), yy, d.stroke("#9A948A", 4))
    d.glow(c, cx, cy, 240, GOLD, 0.25 * d.pulse(t, cue["fold"], 0.5))
    # 人物从右侧伸手，抽出真实修改标记
    pk = d.ease_io(d.prog(t, cue["pick"] - 0.5, 0.9))
    pose = d.blend(d.HOLD, d.REACH, d.prog(t, cue["pick"] - 0.9, 0.5)) if t < cue["pick"] + 0.6 else \
        d.blend(d.REACH, d.HOLD, d.prog(t, cue["pick"] + 0.6, 0.6))
    a_fig = d.prog(t, 0.6, 0.5)
    d.floor_shadow(c, FIG9[0], 770, 160, 0.5 * a_fig)
    j = d.figure(c, FIG9[0], FIG9[1] - (d.SEG["th"] + d.SEG["sh"]) + 140, pose, facing=-1, a=a_fig)
    if f >= 1:
        sx, sy = cx - 10, cy + 10
        hx, hy = j["hand_f"]
        mx, my = d.lerp(sx, hx - 50, pk), d.lerp(sy, hy - 20, pk)
        d.mark_card(c, mx, my, w=120, h=80, rot=-6 * pk, lift=0.4 + 0.8 * pk)


def shot10(c, t, D, cue, view):
    desk(c, view)
    sheet(c)
    # 图标先在格子上方淡入悬停，事件帧落入第一格，格子金框同时点亮
    appear = d.ease_out(d.prog(t, cue["place"] - 0.9, 0.5))
    drop = d.ease_in(d.prog(t, cue["place"] - 3 * F, 3 * F))
    event_icon(c, C1[0], C1[1] - 46 * (1 - drop) - 20 * (1 - appear), s=1.08 - 0.08 * drop, a=appear)
    lit = d.pulse(t, cue["place"], 1.2)
    if lit > 0:
        c.drawRRect(d.rrect(*C1, 310, 380, 12), d.stroke(GOLD, 4, 0.9 * lit))
    d.glow(c, *C1, 200, GOLD, 0.35 * lit)
    s = d.ease_io(d.prog(t, cue["slide"] - 0.5, 0.9))
    vague_label(c, d.lerp(500, 820, s), d.lerp(470, 740, s), rot=d.lerp(-4, 9, s), a=d.lerp(0.95, 0.75, s))


def shot11(c, t, D, cue, view):
    desk(c, view)
    sheet(c)
    event_icon(c, *C1)
    vague_label(c, 820, 740, rot=9, a=0.75)
    a = d.prog(t, 0.2, 0.5)
    paragraph(c, C2[0], C2[1], hi=d.prog(t, cue["point"], 0.3),
              cursor=a * (1 if (t * 2) % 2 < 1.2 else 0.15) if t > cue["point"] else 0)
    # 箭头：从事实格出发，只指向一个段落
    k = d.ease_io(d.prog(t, cue["point"] - 0.9, 0.9))
    if k > 0:
        p = skia.Path()
        p.moveTo(C1[0] + 70, C1[1] - 100)
        p.quadTo(500, 300, C2[0] - 140, C2[1])
        meas = skia.PathMeasure(p, False)
        L = meas.getLength()
        seg = skia.Path()
        meas.getSegment(0, L * k, seg, True)
        c.drawPath(seg, d.stroke(GOLD, 4))
        if k >= 1:
            pos, tan = meas.getPosTan(L)
            ex, ey = pos.x(), pos.y()
            ang = math.atan2(tan.y(), tan.x())
            for s in (-1, 1):
                c.drawLine(ex, ey, ex - 22 * math.cos(ang + s * 0.5), ey - 22 * math.sin(ang + s * 0.5),
                           d.stroke(GOLD, 4))
    d.glow(c, C2[0] - 4, C2[1], 140, GOLD, 0.22 * d.pulse(t, cue["point"], 0.5))


def shot12(c, t, D, cue, view):
    d.room(c, view, floor_y=760, warm=(760, 420, 0.6))
    # 背后的环形轨道淡出
    ra = 1 - d.ease_io(d.prog(t, cue["down"], 2.5))
    if ra > 0:
        ring_floor(c, ring=(470, 800, 360, 70), a=ra)
    # 小桌
    c.drawRect(skia.Rect.MakeLTRB(560, 600, 820, 618), d.fill("#2A2824"))
    c.drawLine(560, 600, 820, 600, d.stroke(GOLD, 1.5, 0.5))
    c.drawRect(skia.Rect.MakeLTRB(580, 618, 594, 760), d.fill("#1D1C19"))
    c.drawRect(skia.Rect.MakeLTRB(786, 618, 800, 760), d.fill("#1D1C19"))
    k = d.ease_io(d.prog(t, cue["down"], 1.2))
    relax = d.ease_io(d.prog(t, cue["down"] + 1.4, 1.2))
    pose = d.blend(d.HOLD, d.LOWER, k) if k < 1 else d.blend(d.LOWER, d.STAND, relax)
    d.floor_shadow(c, 430, 770, 170, 0.5)
    j = d.figure(c, 430, 760 - (d.SEG["th"] + d.SEG["sh"]), pose, facing=1)
    hx, hy = (j["hand_f"][0] + j["hand_b"][0]) / 2, (j["hand_f"][1] + j["hand_b"][1]) / 2
    px, py = d.lerp(hx + 40, 690, k), d.lerp(hy - 40, 590, k)
    d.paper(c, px, py, 150, 110, rot=d.lerp(-6, 0, k), lines=4, mark=(1, 1.0), lift=d.lerp(0.8, 0.15, k),
            line_seed=5)


def shot13(c, t, D, cue, view):
    l, t_, r, b = view
    c.drawRect(skia.Rect.MakeLTRB(l, t_, r, b), d.fill("#08090B"))
    # 夜色中的两栋楼：左边是主角的房间，右边是邻近的一扇窗
    c.drawRect(skia.Rect.MakeLTRB(l, 260, 470, b), d.fill("#111216"))
    c.drawRect(skia.Rect.MakeLTRB(560, 300, r, b), d.fill("#111216"))
    on = d.ease_out(d.prog(t, cue["lamp"], 0.5))
    window(c, 90, 380, 400, 700, 0.35)
    window(c, 620, 400, 900, 700, on)
    # 左窗：主角坐在小灯旁；右窗：一个中性剪影
    d.figure(c, 230, 690 - 40, d.SIT_EASE, facing=1, scale=0.62, rim=0.8)
    if on > 0:
        c.saveLayerAlpha(None, int(255 * on))
        d.figure(c, 800, 690 - 40, d.SIT_EASE, facing=-1, scale=0.6, rim=1.0)
        c.restore()
        d.glow(c, 700, 520, 90, "#FFF1D2", 0.5 * on)
    # 两扇窗之间的光桥
    br = d.ease_out(d.prog(t, cue["lamp"] + 0.4, 1.4))
    if br > 0:
        g = skia.GradientShader.MakeLinear([(400, 0), (620, 0)], [d.col("#E8C987", 0.0), d.col("#E8C987", 0.28 * br),
                                                                  d.col("#E8C987", 0.0)], [0, 0.5, 1])
        c.drawRect(skia.Rect.MakeLTRB(400, 560, 620, 700), skia.Paint(Shader=g, MaskFilter=skia.MaskFilter.MakeBlur(
            skia.kNormal_BlurStyle, 20)))
    rng = np.random.default_rng(13)
    for i in range(16):        # 灯下少量浮尘，仅局部
        x = 640 + rng.uniform(0, 240)
        y = 420 + ((rng.uniform(0, 260) - t * rng.uniform(6, 14)) % 260)
        c.drawCircle(x, y, rng.uniform(1.2, 2.4), d.fill("#F6E2B5", 0.35 * on * rng.uniform(0.4, 1)))


def shot14(c, t, D, cue, view):
    # 事件帧瞬间收回：城市阴影换成卡片的真实影子，随后轻微回弹落定
    after = t >= cue["settle"] - 1e-6
    city = 0.0 if after else 1.0
    s = 1.0 + 0.15 * (1 - d.ease_out(d.prog(t, cue["settle"], 0.4))) if after else 2.6
    bedroom(c, t, view, s, city=city, card_rot=-6, pose=d.blend(d.SIT, d.SIT_EASE, d.prog(t, cue["settle"], 1.6)),
            city_alpha=0.75)


def shot15(c, t, D, cue, view):
    c.save()
    bedroom(c, 6.0, view, 1.0, city=0.0, card_rot=-6, pose=d.SIT_EASE)
    c.restore()
    l, t_, r, b = view
    c.drawRect(skia.Rect.MakeLTRB(l, t_, r, b), d.fill("#000000", 0.62 * d.ease_out(d.prog(t, 0, 0.4))))


SCENES = {1: shot01, 2: shot02, 3: shot03, 4: shot04, 5: shot05, 6: shot06, 7: shot07, 8: shot08,
          9: shot09, 10: shot10, 11: shot11, 12: shot12, 13: shot13, 14: shot14, 15: shot15}
