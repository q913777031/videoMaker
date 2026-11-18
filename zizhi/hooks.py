"""《资治通鉴》每讲的开场钩子（第 0 屏，黄金 3 秒）：本讲痛点画面 + 大字逐字砸下（只留砸字音效，不混配音）。

做法与接口同 fengtian/hooks.py：钩子函数 hook(H, j, cx, cy, acc) 前 3 拍画面动作（每拍一个，配打击乐），
随后 fengtian.hooks._finish 让大字按配音的顿读节奏逐字砸下，再弹出系列小字。本模块在导入时把钩子注册进
fengtian.hooks（HOOKS / HOOK_TEXT / HOOK_PINYIN），并把系列小字换成本系列的（只影响本进程）。
"""
from fengtian import hooks as FH

FH.SERIES_SUB = "资治通鉴 · 打工人的识人做事课"

HOOK_TEXT = dict(zz_credit="功劳全归他", zz_unread="没人当真", zz_slides="一做就砸", zz_blush="下不来台", zz_rules="没人看", zz_tall="压不住", zz_toss="全推翻？", zz_shots="翻旧账", zz_knock="又被拒了")
HOOK_PINYIN = dict(zz_unread=[("当真", "[d][àng]真")])
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
