"""《资治通鉴》每讲的开场钩子（第 0 屏，黄金 3 秒）：本讲痛点画面 + 大字逐字砸下（只留砸字音效，不混配音）。

做法与接口同 fengtian/hooks.py：钩子函数 hook(H, j, cx, cy, acc) 前 3 拍画面动作（每拍一个，配打击乐），
随后 fengtian.hooks._finish 让大字按配音的顿读节奏逐字砸下，再弹出系列小字。本模块在导入时把钩子注册进
fengtian.hooks（HOOKS / HOOK_TEXT / HOOK_PINYIN），并把系列小字换成本系列的（只影响本进程）。
"""
from fengtian import hooks as FH

FH.SERIES_SUB = "资治通鉴 · 打工人的识人做事课"

HOOK_TEXT = dict(zz_credit="功劳全归他", zz_unread="没人当真", zz_slides="一做就砸", zz_blush="下不来台", zz_rules="没人看", zz_tall="压不住", zz_toss="全推翻？", zz_shots="翻旧账", zz_knock="又被拒了",
                 zz_dust="没空学", zz_nope="都说不行", zz_crash="稳赢的局", zz_resume="没人可用", zz_ear="听一边",
                 zz_mirror="都说好")
HOOK_PINYIN = dict(zz_unread=[("当真", "[d][àng]真")], zz_dust=[("没空", "没[k][òng]")])
FH.HOOK_TEXT.update(HOOK_TEXT)
FH.HOOK_PINYIN.update(HOOK_PINYIN)


# ---------------------------------------------------------------- 绘制

import skia  # noqa: E402

from adler import kit as K  # noqa: E402
from engine.gfx import clamp01, lerp  # noqa: E402
from fengtian.common import BLACK, RED, pop_scale  # noqa: E402
from whiteboard import engine as wb  # noqa: E402
from whiteboard.engine import P, rect  # noqa: E402


def zz_credit(H, j, cx, cy, acc):
    """01 才与德：项目汇报单上的署名逐拍被红笔划掉，最后圈出“他”，能人同事冒出来得意一笑；大字“功劳全归他”。"""
    from zizhi.lesson import draw_ace
    b = H.b
    x, top, w, h = cx - 90, cy - 600, 600, 560
    H.note("项目汇报", "小王", "小李", "他")
    b.path(j, 0, 0.6, rect(x, top + h / 2, w, h, 22), BLACK, 9, sfx="wood_high")
    b.text(j, 0.2, 0.6, "项目汇报", x, top + 80, 64, BLACK, font="sans_medium")
    b.path(j, 0.3, 0.6, P((x - 230, top + 140), (x + 230, top + 140)), BLACK, 6)
    rows = [("小王", top + 250), ("小李", top + 360), ("他", top + 470)]
    for s, y in rows:
        b.text(j, 0.5, 0.9, s, x, y, 76, BLACK)
    for k, (s, y) in zip((1, 2), rows[:2]):
        b.path(j, k, k + 0.25, P((x - 110, y + 4), (x + 110, y - 10)), RED, 13, sfx="rim", gain=0.8)
    yh = rows[2][1]
    ring = skia.Path()
    ring.addOval(skia.Rect.MakeXYWH(x - 90, yh - 70, 180, 140))
    b.path(j, 3, 3.3, ring, RED, 10, sfx="tom", gain=0.8)

    def ace(c, kk, T):
        sc = pop_scale(T - H.tb(j, 3))
        if sc <= 0:
            return None
        ax, ay, s = cx + 400, cy + 40, 0.78
        with K.at(c, ax, ay, 0, sc):
            c.translate(-ax, -ay)
            hy = ay - 290 * s
            draw_ace(c, ax, ay, s, mood="smug", lh=(ax - 120 * s, hy + 60 * s), chin=1)
        return None
    b.custom(j, 3, 3.3, ace)
    FH._finish(H, j, cx, cy, HOOK_TEXT["zz_credit"], acc, text_sfx="kick")


FH.HOOKS.update(zz_credit=zz_credit)


def zz_unread(H, j, cx, cy, acc):
    """02 立信：群聊里一条“收到请回复”，已读人数逐拍往上跳，回复一条没有；大字“没人当真”。"""
    b = H.b
    x, top, w, h = cx - 40, cy - 610, 720, 600
    H.note("项目群", "收到请回复", "已读 3", "已读 12", "已读 28", "无人回复")
    b.path(j, 0, 0.6, rect(x, top + h / 2, w, h, 30), BLACK, 9, sfx="wood_high")
    b.text(j, 0.2, 0.6, "项目群", x, top + 60, 52, BLACK, font="sans_medium")
    b.path(j, 0.3, 0.6, P((x - w / 2, top + 110), (x + w / 2, top + 110)), BLACK, 5)

    def msg(c, kk, T):
        g = pop_scale(T - H.tb(j, 0) - 0.3)
        if g <= 0:
            return None
        with K.at(c, x + 90, top + 230, 0, g):
            c.drawRoundRect(skia.Rect.MakeXYWH(-230, -60, 460, 120), 30, 30, K.paint("#D7ECD0"))
            c.drawRoundRect(skia.Rect.MakeXYWH(-230, -60, 460, 120), 30, 30, wb.marker("#3E8A4A", 5))
            K.text(c, "收到请回复", 0, 2, 58, "hand", BLACK)
        n = 0
        for k_, v in ((1, 3), (2, 12), (3, 28)):
            if T >= H.tb(j, k_):
                n = v
        if n:
            kk_ = max(k_ for k_ in (1, 2, 3) if T >= H.tb(j, k_))
            sc = 1 + 0.35 * max(0.0, 1 - (T - H.tb(j, kk_)) / 0.25)
            with K.at(c, x + 170, top + 335, 0, sc):
                K.text(c, f"已读 {n}", 0, 0, 64, "sans_medium", RED)
        if T >= H.tb(j, 3):
            a = clamp01((T - H.tb(j, 3)) / 0.3)
            K.text(c, "无人回复", x - 100, top + 480, 72, "hand", "#8A8F99", a)
        return None
    b.custom(j, 0.3, 0.6, msg)
    for k_, sfx in ((1, "pop"), (2, "pop"), (3, "tom")):
        b.hit(j, k_, sfx, 0.75, "已读人数上涨")
    FH._finish(H, j, cx, cy, HOOK_TEXT["zz_unread"], acc, text_sfx="kick")


FH.HOOKS.update(zz_unread=zz_unread)


def zz_slides(H, j, cx, cy, acc):
    """03 纸上谈兵：方案幻灯片上的曲线一路往上，按下“上线”，曲线变红一头栽下；大字“一做就砸”。"""
    from fengtian.common import GREEN
    b = H.b
    x, top, w, h = cx - 30, cy - 610, 760, 560
    H.note("方案", "上线")
    b.path(j, 0, 0.6, rect(x, top + h / 2, w, h, 20), BLACK, 9, sfx="wood_high")
    b.text(j, 0.2, 0.6, "方案", x - 260, top + 70, 56, BLACK, font="sans_medium")
    x0, y0 = x - 300, top + h - 70
    b.path(j, 0.3, 0.6, P((x0, top + 120), (x0, y0), (x + 330, y0)), BLACK, 6)
    up = [(x0 + 20 + i * 70, y0 - 40 - i * 40 - (i % 2) * 18) for i in range(9)]
    b.path(j, 1, 1.8, P(*up), GREEN, 12, sfx="shaker", gain=0.7)

    def btn(c, kk, T):
        g = pop_scale(T - H.tb(j, 2))
        if g <= 0:
            return None
        press = 0.9 if H.tb(j, 2) + 0.1 < T < H.tb(j, 2) + 0.25 else 1.0
        with K.at(c, x + 230, top + 110, 0, g * press):
            c.drawRoundRect(skia.Rect.MakeXYWH(-90, -38, 180, 76), 38, 38, K.paint(RED))
            K.text(c, "上线", 0, 2, 44, "sans_medium", "#FFFFFF")
        return None
    b.custom(j, 2, 2.3, btn, sfx="pop", gain=0.75)

    def crash(c, kk, T):
        t3 = H.tb(j, 3)
        if T < t3:
            return None
        f = clamp01((T - t3) / 0.35)
        last = up[-1]
        p = P(last, (last[0] + 50, last[1] + 10), (last[0] + 60, last[1] + (y0 - 20 - last[1]) * f))
        c.drawPath(p, wb.marker(RED, 13))
        if f >= 1:
            K.text(c, "×", last[0] + 60, y0 - 50, 90, "hand", RED)
        return None
    b.custom(j, 3, 3.3, crash, sfx="tom", gain=0.8)
    FH._finish(H, j, cx, cy, HOOK_TEXT["zz_slides"], acc, text_sfx="kick")


FH.HOOKS.update(zz_slides=zz_slides)


def zz_blush(H, j, cx, cy, acc):
    """04 将相和：会议桌对面飞来一句“这也叫方案？”，小李的脸一格格变红；大字“下不来台”。"""
    from zizhi.lesson import draw_ace, draw_li
    b = H.b
    GY = cy + 80
    H.note("这也叫方案？")
    b.path(j, 0, 0.5, rect(cx, GY - 170, 900, 50, 10), "#8B6B43", 8, sfx="wood_low")

    def people(c, kk, T):
        g = pop_scale(T - H.tb(j, 0) - 0.1)
        if g <= 0:
            return None
        red = 0.0
        for k_ in (2, 3):
            if T >= H.tb(j, k_):
                red = 0.5 if k_ == 2 else 1.0
        lx = cx - 330
        with K.at(c, lx, GY, 0, g):
            c.translate(-lx, -GY)
            draw_li(c, lx, GY, 1.05, "sad" if red else "flat")
            if red:
                hy = GY - 290 * 1.05
                c.drawCircle(lx, hy, 46, K.paint(RED, 0.35 * red))
                for sg in (-1, 1):
                    c.drawOval(skia.Rect.MakeXYWH(lx + sg * 22 - 12, hy + 4, 24, 14), K.paint(RED, 0.7 * red))
        ax = cx + 330
        with K.at(c, ax, GY, 0, g):
            c.translate(-ax, -GY)
            draw_ace(c, ax, GY, 1.05, mood="laugh" if T >= H.tb(j, 1) else "smug", rh=(ax - 150, GY - 400))
        t1 = H.tb(j, 1)
        if T >= t1:
            f = clamp01((T - t1) / 0.35)
            x = cx + 150 - 260 * f
            with K.at(c, x, cy - 470 + 60 * f, 0, 1.15):
                c.drawRoundRect(skia.Rect.MakeXYWH(-230, -60, 460, 120), 40, 40, K.paint("#FFFFFF"))
                c.drawPath(wb.bubble(0, 0, 460, 120, 1), wb.marker(BLACK, 6))
                K.text(c, "这也叫方案？", 0, 2, 54, "hand", RED)
        return None
    b.custom(j, 0, 0.3, people)
    b.hit(j, 1, "rim", 0.8, "一句话飞过来")
    b.hit(j, 2, "wood_high", 0.7, "脸变红")
    b.hit(j, 3, "tom", 0.75, "红到耳根")
    FH._finish(H, j, cx, cy, HOOK_TEXT["zz_blush"], acc, text_sfx="kick")


FH.HOOKS.update(zz_blush=zz_blush)


def zz_rules(H, j, cx, cy, acc):
    """05 约法三章：制度文件一本本砸到桌上越叠越高，桌腿“咔”地压弯；大字“没人看”。"""
    from fengtian.common import BLUE, GREEN
    b = H.b
    GY = cy + 60
    H.note("制度", "流程", "规范", "细则")
    b.path(j, 0, 0.5, rect(cx, GY - 40, 760, 40, 8), "#8B6B43", 8, sfx="wood_low")

    def stack(c, kk, T):
        bend = 0.0
        if T >= H.tb(j, 3):
            bend = clamp01((T - H.tb(j, 3)) / 0.2)
        for sg in (-1, 1):
            x0 = cx + sg * 330
            C_line(c, (x0, GY - 20), (x0 + sg * 40 * bend, GY + 120), "#8B6B43", 10)
        labs = ("制度", "流程", "规范", "细则", "制度", "流程", "规范", "细则")
        for i in range(8):
            k_ = min(3, i // 2 + (i % 2) * 0) if i < 6 else 2 + (i - 6)
            t0 = H.tb(j, [0.3, 1, 1, 2, 2, 2, 3, 3][i]) + (0.12 if i % 2 else 0)
            dt = T - t0
            if dt < 0:
                continue
            drop = (1 - clamp01(dt / 0.18)) * 300
            y = GY - 90 - i * 64 - drop + 16 * bend
            rot = (i * 37 % 9 - 4) + bend * (i % 3 - 1) * 3
            with K.at(c, cx + (i * 53 % 50 - 25), y, rot):
                c.drawRoundRect(skia.Rect.MakeXYWH(-230, -28, 460, 56), 6, 6, K.paint(("#FFFFFF", "#E8EEF8", "#FFF6DA")[i % 3]))
                c.drawRoundRect(skia.Rect.MakeXYWH(-230, -28, 460, 56), 6, 6, wb.marker((BLUE, BLACK, GREEN)[i % 3], 5))
                K.text(c, labs[i], -130, 2, 36, "sans_medium", BLACK)
        return None
    b.custom(j, 0.3, 0.6, stack)
    b.hit(j, 1, "wood_high", 0.8, "又砸下两本")
    b.hit(j, 2, "wood_high", 0.8, "越叠越高")
    b.hit(j, 3, "tom", 0.85, "桌子压弯")
    FH._finish(H, j, cx, cy, HOOK_TEXT["zz_rules"], acc, text_sfx="kick")


def C_line(c, a, z, color, w, alpha=1.0):
    c.drawLine(a[0], a[1], z[0], z[1], wb.marker(color, w, alpha))


FH.HOOKS.update(zz_rules=zz_rules)


def zz_tall(H, j, cx, cy, acc):
    """06 三不如：戴“组长”牌的小李站在三个同事中间，同事一拍一拍变高，小李越缩越小；大字“压不住”。"""
    from zizhi.lesson import draw_ace, draw_li, draw_wang
    from fengtian.common import GREEN, RED as R_
    b = H.b
    GY = cy + 80
    H.note("组长")
    b.path(j, 0, 0.4, P((cx - 560, GY + 4), (cx + 560, GY + 4)), BLACK, 6, sfx="wood_low")

    def people(c, kk, T):
        g = pop_scale(T - H.tb(j, 0) - 0.1)
        if g <= 0:
            return None
        grow = [0.0, 0.0, 0.0]
        for i, k_ in enumerate((1, 2, 3)):
            if T >= H.tb(j, k_):
                grow[i] = clamp01((T - H.tb(j, k_)) / 0.25)
        shrink = 1 - 0.12 * sum(grow)
        for i, (x, fn) in enumerate(((cx - 380, "ace"), (cx + 200, "wang"), (cx + 420, "ace"))):
            s = 0.75 + 0.35 * grow[i]
            with K.at(c, x, GY, 0, g):
                c.translate(-x, -GY)
                if fn == "wang":
                    draw_wang(c, x, GY, s, mood="smile")
                else:
                    draw_ace(c, x, GY, s, mood="smug")
        lx = cx - 90
        s = 0.8 * shrink
        with K.at(c, lx, GY, 0, g):
            c.translate(-lx, -GY)
            draw_li(c, lx, GY, s, "sad" if sum(grow) > 1 else "flat")
            hy = GY - 290 * s
            c.drawRoundRect(skia.Rect.MakeXYWH(lx - 40 * s, hy + 120 * s, 80 * s, 40 * s), 6, 6, K.paint("#F6C3BE"))
            K.text(c, "组长", lx, hy + 141 * s, 28 * s, "sans_medium", R_)
        return None
    b.custom(j, 0, 0.3, people)
    for k_ in (1, 2, 3):
        b.hit(j, k_, "wood_high" if k_ < 3 else "tom", 0.8, "同事变高")
    FH._finish(H, j, cx, cy, HOOK_TEXT["zz_tall"], acc, text_sfx="kick")


FH.HOOKS.update(zz_tall=zz_tall)


def zz_toss(H, j, cx, cy, acc):
    """07 萧规曹随：前任的文件夹被一把扔向垃圾桶，弹了回来；大字“全推翻？”。"""
    import math as _m
    from fengtian.common import BLUE, ORANGE
    b = H.b
    GY = cy + 60
    H.note("前任的项目")
    b.path(j, 0, 0.5, P((cx + 180, GY - 260), (cx + 210, GY), (cx + 430, GY), (cx + 460, GY - 260)), BLACK, 9, sfx="wood_low")

    def folder(c, kk, T):
        t1, t2, t3 = H.tb(j, 1), H.tb(j, 2), H.tb(j, 3)
        g = pop_scale(T - H.tb(j, 0) - 0.2)
        if g <= 0:
            return None
        x, y, rot = cx - 280, cy - 300, 0.0
        if T >= t1:
            f = clamp01((T - t1) / max(0.2, t2 - t1))
            x = lerp(cx - 280, cx + 320, f)
            y = lerp(cy - 300, GY - 180, f) - 260 * _m.sin(_m.pi * f)
            rot = 300 * f
        if T >= t2:
            f2 = clamp01((T - t2) / max(0.2, t3 - t2))
            x = lerp(cx + 320, cx - 60, f2)
            y = lerp(GY - 180, cy - 380, f2) - 160 * _m.sin(_m.pi * f2)
            rot = 300 - 300 * f2
        with K.at(c, x, y, rot, g):
            c.drawRoundRect(skia.Rect.MakeXYWH(-200, -140, 400, 280), 14, 14, K.paint("#F6D98A"))
            c.drawRoundRect(skia.Rect.MakeXYWH(-200, -140, 400, 280), 14, 14, wb.marker(ORANGE, 6))
            c.drawRoundRect(skia.Rect.MakeXYWH(-200, -170, 160, 50), 10, 10, K.paint("#F6D98A"))
            K.text(c, "前任的项目", 0, 0, 52, "hand", BLACK)
        if T >= t2 and T < t2 + 0.4:
            K.burst(c, cx + 320, GY - 240, T - t2, BLUE, 20, 80, 6, 6)
        return None
    b.custom(j, 0.2, 0.5, folder)
    b.hit(j, 1, "shaker", 0.75, "扔出去")
    b.hit(j, 2, "tom", 0.8, "撞到垃圾桶")
    b.hit(j, 3, "pop", 0.75, "弹回来")
    FH._finish(H, j, cx, cy, HOOK_TEXT["zz_toss"], acc, text_sfx="kick")


FH.HOOKS.update(zz_toss=zz_toss)


def zz_shots(H, j, cx, cy, acc):
    """08 不翻旧账：手机里的聊天截图一张张飞出来，叠成一摞；大字“翻旧账”。"""
    from fengtian.common import BLUE, GREEN
    b = H.b
    PX, PY = cx - 330, cy - 200
    H.note("截图")
    b.path(j, 0, 0.5, rect(PX, PY, 220, 400, 30), BLACK, 9, sfx="wood_high")

    def shots(c, kk, T):
        for i in range(5):
            k_ = (1, 1.5, 2, 2.5, 3)[i]
            t0 = H.tb(j, k_)
            if T < t0:
                continue
            f = clamp01((T - t0) / 0.3)
            tx, ty = cx + 220 + (i % 2) * 30 - 15, cy - 420 + i * 70
            x, y = lerp(PX, tx, f), lerp(PY, ty, f) - 120 * (1 - (2 * f - 1) ** 2)
            with K.at(c, x, y, (i * 23 % 13 - 6) * f, lerp(0.4, 1.0, f)):
                c.drawRoundRect(skia.Rect.MakeXYWH(-180, -110, 360, 220), 14, 14, K.paint("#FFFFFF"))
                c.drawRoundRect(skia.Rect.MakeXYWH(-180, -110, 360, 220), 14, 14, wb.marker(BLACK, 5))
                for q in range(2):
                    c.drawRoundRect(skia.Rect.MakeXYWH(-150 + q * 90, -70 + q * 70, 200, 50), 18, 18,
                                    K.paint("#D7ECD0" if q else "#E8EEF8"))
                K.text(c, "截图", 120, 80, 30, "sans_medium", (BLUE, GREEN)[i % 2])
        return None
    b.custom(j, 1, 1.3, shots)
    b.hit(j, 1, "pop", 0.75, "截图飞出")
    b.hit(j, 2, "pop", 0.75, "又一张")
    b.hit(j, 3, "tom", 0.8, "叠成一摞")
    FH._finish(H, j, cx, cy, HOOK_TEXT["zz_shots"], acc, text_sfx="kick")


FH.HOOKS.update(zz_shots=zz_shots)


def zz_knock(H, j, cx, cy, acc):
    """09 三顾：小李发出“在吗？”，三个头像逐拍显示“已读”却没回；大字“又被拒了”。"""
    from fengtian.common import BLUE, GREEN
    b = H.b
    x, top, w, h = cx - 40, cy - 610, 720, 600
    H.note("在吗？", "已读")
    b.path(j, 0, 0.6, rect(x, top + h / 2, w, h, 30), BLACK, 9, sfx="wood_high")

    def msgs(c, kk, T):
        g = pop_scale(T - H.tb(j, 0) - 0.3)
        if g <= 0:
            return None
        with K.at(c, x + 150, top + 110, 0, g):
            c.drawRoundRect(skia.Rect.MakeXYWH(-130, -50, 260, 100), 30, 30, K.paint("#D7ECD0"))
            c.drawRoundRect(skia.Rect.MakeXYWH(-130, -50, 260, 100), 30, 30, wb.marker(GREEN, 5))
            K.text(c, "在吗？", 0, 2, 56, "hand", BLACK)
        for i, k_ in enumerate((1, 2, 3)):
            t0 = H.tb(j, k_)
            gi = pop_scale(T - t0)
            if gi <= 0:
                continue
            yy = top + 240 + i * 120
            with K.at(c, x - 220, yy, 0, gi):
                c.drawCircle(0, 0, 44, K.paint("#E8EEF8"))
                c.drawCircle(0, 0, 44, wb.marker(BLUE, 5))
                K.text(c, "已读", 150, 0, 48, "sans_medium", "#8A8F99")
                K.text(c, "……", 300, -6, 48, "hand", "#8A8F99")
        return None
    b.custom(j, 0.3, 0.6, msgs)
    for k_ in (1, 2, 3):
        b.hit(j, k_, "pop" if k_ < 3 else "tom", 0.75, "已读不回")
    FH._finish(H, j, cx, cy, HOOK_TEXT["zz_knock"], acc, text_sfx="kick")


FH.HOOKS.update(zz_knock=zz_knock)


def zz_dust(H, j, cx, cy, acc):
    """10 劝学：书桌上一本书，外卖盒一层层压上去，书落满灰；大字“没空学”。"""
    from fengtian.common import BLUE, ORANGE
    b = H.b
    GY = cy + 40
    H.note("书")
    b.path(j, 0, 0.5, rect(cx, GY, 900, 40, 8), "#8B6B43", 8, sfx="wood_low")

    def stack(c, kk, T):
        g = pop_scale(T - H.tb(j, 0) - 0.2)
        if g <= 0:
            return None
        with K.at(c, cx - 40, GY - 50, 0, g):
            c.drawRoundRect(skia.Rect.MakeXYWH(-200, -30, 400, 60), 8, 8, K.paint("#D5E3F7"))
            c.drawRoundRect(skia.Rect.MakeXYWH(-200, -30, 400, 60), 8, 8, wb.marker(BLUE, 6))
            K.text(c, "书", 0, 2, 44, "serif_black", BLUE)
        for i in range(5):
            k_ = (1, 1.4, 2, 2.4, 2.8)[i]
            t0 = H.tb(j, k_)
            if T < t0:
                continue
            d = (1 - clamp01((T - t0) / 0.18)) * 260
            y = GY - 130 - i * 80 - d
            with K.at(c, cx - 40 + (i % 2) * 30 - 15, y, (i * 17 % 9) - 4):
                c.drawPath(P((-130, -36), (130, -36), (110, 36), (-110, 36), close=True), K.paint("#FFFFFF"))
                c.drawPath(P((-130, -36), (130, -36), (110, 36), (-110, 36), close=True), wb.marker(ORANGE, 5))
                C_line(c, (-130, -10), (130, -10), ORANGE, 4)
        t3 = H.tb(j, 3)
        if T >= t3:
            a = clamp01((T - t3) / 0.4)
            for q in range(40):
                x = cx - 260 + (q * 53) % 520
                y = GY - 560 + (q * 37) % 520
                c.drawCircle(x, y, 4 + q % 3, K.paint("#8A8F99", 0.5 * a))
            web = skia.Path()
            for r_ in (60, 110, 160):
                web.addArc(skia.Rect.MakeXYWH(cx + 180 - r_, GY - 640 - r_, 2 * r_, 2 * r_), 90, 90)
            c.drawPath(web, wb.marker("#8A8F99", 3, a))
        return None
    b.custom(j, 0.2, 0.5, stack)
    b.hit(j, 1, "wood_high", 0.8, "外卖盒压上去")
    b.hit(j, 2, "wood_high", 0.8, "又压两盒")
    b.hit(j, 3, "tom", 0.8, "落满灰")
    FH._finish(H, j, cx, cy, HOOK_TEXT["zz_dust"], acc, text_sfx="kick")


FH.HOOKS.update(zz_dust=zz_dust)


def zz_nope(H, j, cx, cy, acc):
    """11 有志者：小李举起“我想试试”的牌子，四周一张张嘴冒出“别折腾了”；大字“都说不行”。"""
    from zizhi.lesson import draw_li
    b = H.b
    GY = cy + 60
    H.note("我想试试", "别折腾了")

    def scene(c, kk, T):
        g = pop_scale(T - H.tb(j, 0))
        if g <= 0:
            return None
        lx = cx
        with K.at(c, lx, GY, 0, g):
            c.translate(-lx, -GY)
            n = sum(1 for k_ in (1, 2, 3) if T >= H.tb(j, k_))
            draw_li(c, lx, GY, 0.95 - 0.06 * n, "flat" if n < 2 else "sad", rh=(lx + 110, GY - 420))
            C_line(c, (lx + 110, GY - 420), (lx + 110, GY - 520), "#8B6B43", 8)
            c.drawRoundRect(skia.Rect.MakeXYWH(lx + 10, GY - 640, 260, 120), 12, 12, K.paint("#FFF1A8"))
            c.drawRoundRect(skia.Rect.MakeXYWH(lx + 10, GY - 640, 260, 120), 12, 12, wb.marker(BLACK, 5))
            K.text(c, "我想试试", lx + 140, GY - 580, 48, "hand", BLACK)
        for i, (k_, x, y) in enumerate(((1, cx - 380, cy - 450), (2, cx - 400, cy - 150), (3, cx + 380, cy - 280))):
            t0 = H.tb(j, k_)
            if T < t0:
                continue
            gi = C_slam(T - t0)
            with K.at(c, x, y, (i - 1) * 6, gi):
                c.drawRoundRect(skia.Rect.MakeXYWH(-150, -55, 300, 110), 40, 40, K.paint("#FFFFFF"))
                c.drawPath(wb.bubble(0, 0, 300, 110, 1 if x < cx else -1), wb.marker(BLACK, 5))
                K.text(c, "别折腾了", 0, 0, 48, "hand", RED)
        return None
    b.custom(j, 0, 0.3, scene, sfx="pop", gain=0.6)
    for k_ in (1, 2, 3):
        b.hit(j, k_, "rim" if k_ < 3 else "tom", 0.8, "别折腾了")
    FH._finish(H, j, cx, cy, HOOK_TEXT["zz_nope"], acc, text_sfx="kick")


def C_slam(dt):
    from fengtian.common import slam_scale
    return slam_scale(dt)


FH.HOOKS.update(zz_nope=zz_nope)


def zz_crash(H, j, cx, cy, acc):
    """12 投鞭断流：进度条一路涨到 99%，“啪”地掉到 0；大字“稳赢的局”。"""
    from fengtian.common import GREEN
    b = H.b
    x0, y, w = cx - 380, cy - 330, 760
    H.note("99%", "0%")
    b.path(j, 0, 0.5, rect(cx, y, w, 90, 45), BLACK, 9, sfx="wood_high")

    def bar(c, kk, T):
        t1, t3 = H.tb(j, 1), H.tb(j, 3)
        if T < H.tb(j, 0.3):
            return None
        if T < t3:
            p = 0.2 + 0.79 * ease_out_(clamp01((T - H.tb(j, 0.3)) / max(0.3, H.tb(j, 2.6) - H.tb(j, 0.3))))
            col = GREEN
        else:
            p = 0.99 * (1 - clamp01((T - t3) / 0.15))
            col = RED
        c.drawRoundRect(skia.Rect.MakeXYWH(x0 + 8, y - 37, (w - 16) * p, 74), 37, 37, K.paint(col))
        K.text(c, f"{int(round(p * 100))}%", cx, y - 110, 70, "black", col)
        if T >= t3 and T < t3 + 0.5:
            K.burst(c, x0 + 40, y, T - t3, RED, 20, 90, 7, 7)
        return None
    b.custom(j, 0.3, 0.6, bar)
    b.hit(j, 1, "shaker", 0.7, "进度往上涨")
    b.hit(j, 2, "ding", 0.7, "99%")
    b.hit(j, 3, "tom", 0.85, "掉到 0")
    FH._finish(H, j, cx, cy, HOOK_TEXT["zz_crash"], acc, text_sfx="kick")


def ease_out_(x):
    return 1 - (1 - x) ** 3


FH.HOOKS.update(zz_crash=zz_crash)


def zz_resume(H, j, cx, cy, acc):
    """13 用人如器：简历一张张飞进垃圾桶，最后一张也扔掉；大字“没人可用”。"""
    b = H.b
    BX, BY = cx + 300, cy + 40
    H.note("简历")
    b.path(j, 0, 0.5, P((BX - 150, BY - 260), (BX - 120, BY), (BX + 120, BY), (BX + 150, BY - 260)), BLACK, 9, sfx="wood_low")

    def papers(c, kk, T):
        for i in range(5):
            k_ = (0.5, 1, 1.5, 2, 3)[i]
            t0 = H.tb(j, k_)
            if T < t0:
                continue
            f = clamp01((T - t0) / 0.45)
            x = lerp(cx - 300, BX + (i % 3 - 1) * 30, f)
            y = lerp(cy - 420 + i * 30, BY - 200, f) - 220 * math.sin(math.pi * f)
            with K.at(c, x, y, 260 * f + i * 15, lerp(1, 0.7, f)):
                c.drawRect(skia.Rect.MakeXYWH(-90, -120, 180, 240), K.paint("#FFFFFF"))
                c.drawRect(skia.Rect.MakeXYWH(-90, -120, 180, 240), wb.marker(BLACK, 5))
                c.drawCircle(-40, -70, 26, wb.marker("#8A8F99", 4))
                K.text(c, "简历", 30, -70, 32, "sans_medium", BLACK)
                for q in range(3):
                    C_line(c, (-60, -10 + q * 40), (60, -10 + q * 40), "#8A8F99", 4)
        return None
    b.custom(j, 0.5, 0.8, papers)
    b.hit(j, 1, "shaker", 0.75, "扔一张")
    b.hit(j, 2, "shaker", 0.75, "又扔一张")
    b.hit(j, 3, "tom", 0.8, "最后一张也扔了")
    FH._finish(H, j, cx, cy, HOOK_TEXT["zz_resume"], acc, text_sfx="kick")


import math  # noqa: E402

FH.HOOKS.update(zz_resume=zz_resume)


def zz_ear(H, j, cx, cy, acc):
    """14 兼听：小李的一只耳朵越变越大，另一只缩没了；大字“听一边”。"""
    from zizhi.lesson import draw_li
    b = H.b
    GY = cy + 80

    def scene(c, kk, T):
        g = pop_scale(T - H.tb(j, 0))
        if g <= 0:
            return None
        grow = 0.0
        for k_ in (1, 2, 3):
            if T >= H.tb(j, k_):
                grow = lerp(grow, k_ / 3, clamp01((T - H.tb(j, k_)) / 0.25))
        s = 1.25
        hy = GY - 290 * s
        with K.at(c, cx, GY, 0, g):
            c.translate(-cx, -GY)
            draw_li(c, cx, GY, s, "flat")
            big = 1 + 2.2 * grow
            c.drawOval(skia.Rect.MakeXYWH(cx - 56 * s - 40 * big, hy - 30 * big, 40 * big, 70 * big), K.paint("#FFFFFF"))
            c.drawOval(skia.Rect.MakeXYWH(cx - 56 * s - 40 * big, hy - 30 * big, 40 * big, 70 * big), wb.marker(BLACK, 7))
            small = 1 - grow
            if small > 0.05:
                c.drawOval(skia.Rect.MakeXYWH(cx + 56 * s, hy - 30 * small, 40 * small, 70 * small), wb.marker(BLACK, 7))
        if T >= H.tb(j, 1):
            for q in range(3):
                f = ((T - H.tb(j, 1)) * 1.2 + q * 0.33) % 1
                xx = cx - 520 + 200 * f
                C_line(c, (xx, hy - 40 + q * 40), (xx + 60, hy - 40 + q * 40), "#8A8F99", 5, 1 - f)
        return None
    b.custom(j, 0, 0.3, scene, sfx="wood_low", gain=0.6)
    for k_ in (1, 2, 3):
        b.hit(j, k_, "pop" if k_ < 3 else "tom", 0.8, "耳朵变大")
    FH._finish(H, j, cx, cy, HOOK_TEXT["zz_ear"], acc, text_sfx="kick")


FH.HOOKS.update(zz_ear=zz_ear)


def zz_mirror(H, j, cx, cy, acc):
    """15 以人为镜：小李对着镜子问“怎么样？”，镜子里的人只会点头，一下、两下、三下；大字“都说好”。"""
    from zizhi.lesson import draw_li
    b = H.b
    GY = cy + 80
    MX = cx + 220
    H.note("怎么样？", "好")

    def scene(c, kk, T):
        g = pop_scale(T - H.tb(j, 0))
        if g <= 0:
            return None
        lx = cx - 300
        with K.at(c, lx, GY, 0, g):
            c.translate(-lx, -GY)
            draw_li(c, lx, GY, 1.0, "flat", rh=(lx + 130, GY - 330))
        c.drawRoundRect(skia.Rect.MakeXYWH(MX - 200, cy - 600, 400, 680), 190, 190, K.paint("#E8EEF8"))
        c.drawRoundRect(skia.Rect.MakeXYWH(MX - 200, cy - 600, 400, 680), 190, 190, wb.marker("#8A6A3A", 12))
        nod = 0.0
        for k_ in (1, 2, 3):
            dt = T - H.tb(j, k_)
            if 0 <= dt < 0.35:
                nod = math.sin(dt / 0.35 * math.pi) * 22
        c.save()
        c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(MX - 200, cy - 600, 400, 680), 190, 190))
        c.translate(2 * MX, 0)
        c.scale(-1, 1)
        hy = cy - 40 - 290 * 0.9
        draw_li(c, MX, cy - 40 + nod * 0.3, 0.9, "smile", alpha=0.75)
        c.restore()
        if T >= H.tb(j, 0.5):
            with K.at(c, lx + 90, cy - 420, 0, pop_scale(T - H.tb(j, 0.5))):
                c.drawRoundRect(skia.Rect.MakeXYWH(-130, -50, 260, 100), 40, 40, K.paint("#FFFFFF"))
                c.drawPath(wb.bubble(0, 0, 260, 100, -1), wb.marker(BLACK, 5))
                K.text(c, "怎么样？", 0, 0, 46, "hand", BLACK)
        for i, k_ in enumerate((1, 2, 3)):
            if T >= H.tb(j, k_):
                K.text(c, "好", MX + 150 + i * 10, cy - 520 + i * 90, 50, "hand", "#3E8A4A", clamp01((T - H.tb(j, k_)) / 0.15))
        return None
    b.custom(j, 0, 0.3, scene, sfx="wood_low", gain=0.6)
    for k_ in (1, 2, 3):
        b.hit(j, k_, "pop" if k_ < 3 else "tom", 0.75, "镜子点头")
    FH._finish(H, j, cx, cy, HOOK_TEXT["zz_mirror"], acc, text_sfx="kick")


FH.HOOKS.update(zz_mirror=zz_mirror)
