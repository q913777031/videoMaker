"""手机屏幕叙事：整片就是一部手机，故事在工作群、读书 App 和备忘录里发生；动作落在实测拍点上。

    python3 -m styles.phone --stills    # 8 张小节末单帧
    python3 -m styles.phone             # → out/styles/phone.mp4
"""

import math

import skia

from adler import fx
from engine import gfx
from engine.gfx import clamp01, ease_in, ease_out, ease_out_back, lerp
from styles import seg

W, H = seg.W, seg.H
PX, PY, PW, PH = 60, 50, 960, 1820          # 手机外框
SX, SY, SW, SH = PX + 22, PY + 22, PW - 44, PH - 44   # 屏幕
CX = SX + SW / 2
GREEN = "#95EC69"
ACC = "#2F7A78"
INK = "#1B1D24"
GRAY = "#8A8F98"


def txt(c, s, x, y, size, font="sans", color=INK, alpha=1.0, align="center"):
    return gfx.draw_text(c, s, x, y, size, font, color, alpha, align)


def avatar(c, x, y, r, color, ch, alpha=1.0, scale=1.0):
    if alpha <= 0:
        return
    c.save()
    c.translate(x, y)
    c.scale(scale, scale)
    gfx.rrect(c, 0, 0, 2 * r, 2 * r, r * 0.28, color, alpha)
    txt(c, ch, 0, 0, r * 0.95, "bold", "#FFFFFF", alpha)
    c.restore()


# ---------------------------------------------------------------- 工作群（小节 0–3）

P = {"王总": "#3D4B66", "小李": "#D98E8A", "老陈": "#8C9A6A", "阿梅": "#C98B5A", "小周": "#5E9A8A",
     "小吴": "#7E6FA6", "小郑": "#C0502A", "大刘": "#6E9CC2"}


def _b(i, k):
    return seg.BARS[i]["beats"][k]


def _mid(i, k):
    b = seg.BARS[i]["beats"] + [seg.BARS[i]["t1"]]
    return (b[k] + b[k + 1]) / 2


FEED = [
    (_b(0, 0), "tip", "", "“王总”加入了群聊"),
    (_b(0, 1), "msg", "王总", "大家好，我是新来的负责人"),
    (_b(0, 2), "msg", "王总", "咱们重新出发！@party_popper"),
    (_b(1, 0), "tip", "", "“小李”退出了群聊"),
    (_b(1, 1), "tip", "", "“小周”加入了群聊"),
    (_b(1, 2), "tip", "", "“老陈”退出了群聊"),
    (_b(1, 3), "tip", "", "“小吴”加入了群聊"),
    (_b(2, 0), "msg", "小周", "冲！"),
    (_mid(2, 0), "msg", "小吴", "收到！"),
    (_b(2, 1), "msg", "小郑", "冲冲冲！"),
    (_mid(2, 1), "msg", "大刘", "这次一定行！"),
    (_b(2, 2), "msg", "阿梅", "全力以赴@fire"),
    (_b(3, 0), "divider", "", "三个月后"),
    (_b(3, 1), "msg", "王总", "在吗？"),
    (_b(3, 2), "msg", "王总", "这个……谁负责？"),
]

OLD = ["小李", "老陈", "阿梅", "大刘", "王总", "小李", "老陈", "阿梅"]
NEW = {0: "小周", 2: "小吴", 5: "小郑", 6: "大刘"}


def _item_h(kind):
    return {"tip": 74, "divider": 120, "msg": 150}[kind]


def _msg(c, y, who, text, k, dim):
    a = clamp01(k * 4) * (1 - 0.45 * dim)
    s = 0.6 + 0.4 * ease_out_back(clamp01(k), 2.4)
    emo = None
    if "@" in text:
        text, emo = text.split("@")
    size = 42
    tw = gfx.text_width(text, size, "sans") + (64 if emo else 0)
    bw, bh = tw + 56, 92
    ax = SX + 70
    c.save()
    c.translate(ax, y - 20)
    c.scale(s, s)
    avatar(c, 0, 0, 40, P[who], who[-1], a)
    txt(c, who, 64, -34, 28, "sans", GRAY, a, "left")
    bx = 64 + bw / 2
    gfx.rrect(c, bx, 30, bw, bh, 18, "#FFFFFF", a)
    p = skia.Path()
    p.moveTo(64, 14)
    p.lineTo(52, 26)
    p.lineTo(64, 38)
    c.drawPath(p, skia.Paint(AntiAlias=True, Color=gfx.col("#FFFFFF", a)))
    txt(c, text, 92, 30, size, "sans", INK, a, "left")
    if emo:
        gfx.draw_emoji(c, emo, 92 + gfx.text_width(text, size, "sans") + 36, 28, 56, a, shadow=0)
    c.restore()


def _tip(c, y, text, k, dim):
    a = clamp01(k * 4) * (1 - 0.45 * dim)
    w = gfx.text_width(text, 30, "sans") + 40
    gfx.rrect(c, CX, y, w, 50, 10, "#DADADA", a)
    txt(c, text, CX, y, 30, "sans", "#666A70", a)


def _divider(c, y, text, k):
    a = clamp01(k * 3)
    s = 0.5 + 0.5 * ease_out_back(clamp01(k), 2.0)
    c.save()
    c.translate(CX, y)
    c.scale(s, s)
    gfx.rrect(c, 0, 0, 470, 96, 48, "#3D4B66", a)
    gfx.draw_emoji(c, "spiral_calendar", -170, 0, 64, a, rot=(1 - ease_out(clamp01(k))) * 360, shadow=0)
    txt(c, text, 30, 0, 48, "black", "#FFFFFF", a)
    c.restore()


def chat(c, t):
    gfx.rrect(c, CX, SY + SH / 2, SW, SH, 0, "#EDEDED")
    # 顶栏
    gfx.rrect(c, CX, SY + 190, SW, 120, 0, "#F7F7F7")
    txt(c, "‹", SX + 50, SY + 190, 64, "sans", INK)
    n = 12
    txt(c, f"项目组（{n}）", CX, SY + 190, 44, "bold", INK)
    txt(c, "···", SX + SW - 60, SY + 182, 48, "bold", INK)
    # 成员头像条
    gfx.rrect(c, CX, SY + 330, SW, 160, 0, "#FFFFFF")
    for i, name in enumerate(OLD):
        x = SX + 70 + i * 111
        nm = name
        sc = 1.0
        if i in NEW:
            j = list(NEW).index(i)
            tb = seg.BARS[1]["beats"][j]
            dt = t - tb
            if dt >= 0:
                nm = NEW[i]
                sc = 0.4 + 0.6 * ease_out_back(clamp01(dt / 0.3), 2.5)
            elif dt > -0.15:
                sc = clamp01(-dt / 0.15)
        avatar(c, x, SY + 315, 40, P[nm], nm[-1], 1, sc)
        txt(c, nm, x, SY + 380, 24, "sans", GRAY)
    # 消息流：从输入栏往上堆叠，新消息把旧消息推上去
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(SX, SY + 410, SX + SW, SY + SH - 150))
    y = SY + SH - 230
    dim = clamp01((t - _b(3, 0)) / 0.4)
    for tm, kind, who, text in reversed(FEED):
        dt = t - tm
        if dt < 0:
            continue
        k = clamp01(dt / 0.28)
        h = _item_h(kind) * ease_out(clamp01(dt / 0.18))
        cy = y - h / 2 + 10
        old = 1.0 if tm < _b(3, 0) else 0.0
        if kind == "msg":
            _msg(c, cy, who, text, k, dim * old)
        elif kind == "tip":
            _tip(c, cy, text, k, dim)
        else:
            _divider(c, cy, text, k)
        y -= h
    c.restore()
    # 点赞特效
    dt = t - _b(2, 3)
    if 0 <= dt < 1.2:
        for i in range(7):
            k = clamp01((dt - i * 0.06) / 0.9)
            if k <= 0:
                continue
            x = SX + SW - 120 - 40 * math.sin(i * 1.7 + k * 4)
            gfx.draw_emoji(c, "thumbs_up", x, SY + SH - 260 - k * 900, 90, 1 - k, shadow=0)
        fx.sparks(c, SX + SW - 120, SY + SH - 260, dt, ["#FFD23F", "#FF7A59", "#FFFFFF"], n=18, reach=220)
    # 输入栏
    gfx.rrect(c, CX, SY + SH - 90, SW, 140, 0, "#F7F7F7")
    gfx.rrect(c, CX - 40, SY + SH - 95, SW - 230, 80, 14, "#FFFFFF")
    txt(c, "+", SX + SW - 70, SY + SH - 98, 70, "sans", INK)


# ---------------------------------------------------------------- 全屏通知（小节 4）

def drop_card(c, t, bar):
    d0 = seg.since(bar, 0, t)
    d1 = seg.since(bar, 1, t)
    k0 = ease_in(clamp01((d0 + 0.18) / 0.18))
    cy = lerp(SY - 900, SY + SH / 2, k0)
    c.drawRect(skia.Rect.MakeXYWH(SX, SY, SW, SH), skia.Paint(Color=gfx.col("#000000", 0.55 * k0)))
    gfx.rrect(c, CX, cy, SW - 60, 1100, 56, "#14161C", 1, shadow=0.5)
    gfx.rrect(c, CX, cy - 430, 300, 60, 30, ACC)
    txt(c, "系统之美 · 书中观点", CX, cy - 430, 30, "bold", "#FFFFFF")
    txt(c, "不是人的问题", CX, cy - 150, 118, "black", "#FFFFFF")
    if d1 >= -0.05:
        s = 1.6 - 0.6 * ease_out(clamp01((d1 + 0.05) / 0.2))
        c.save()
        c.translate(CX, cy + 120)
        c.scale(s, s)
        gfx.rrect(c, 0, 0, 560, 200, 30, ACC, clamp01((d1 + 0.05) / 0.1))
        txt(c, "是结构", 0, 0, 150, "black", "#FFFFFF", clamp01((d1 + 0.05) / 0.1))
        c.restore()
        fx.sparks(c, CX, cy + 120, seg.since(bar, 2, t), ["#FFD23F", "#7FE0D8", "#FFFFFF"], n=20, reach=420)
    txt(c, "现在", CX, cy + 420, 30, "sans", GRAY)


# ---------------------------------------------------------------- 读书 App（小节 5–6）

def slinky_art(c, x, y, t, bar5, bar6, t_now):
    tap = seg.since(bar6, 1, t_now) if bar6 else -1
    top = y - 250
    if tap >= 0:
        L = 330 + 170 * math.sin(tap * 7.0) * math.exp(-tap * 1.0)
    else:
        L = 330
    for i in range(20):
        yy = top + L * i / 19
        c.drawOval(skia.Rect.MakeXYWH(x - 80, yy - 14, 160, 28),
                   skia.Paint(AntiAlias=True, Color=gfx.col("#3E8A6E" if i % 2 else "#2F7A78"), Style=skia.Paint.kStroke_Style,
                              StrokeWidth=9))
    a = 1.0 if tap < 0 else 1 - clamp01(tap / 0.3)
    hy = top - 60 - (220 * ease_out(clamp01(tap / 0.35)) if tap >= 0 else 0)
    if a > 0:
        gfx.rrect(c, x, hy, 120, 64, 28, "#F2D6BA", a)
        gfx.rrect(c, x, hy - 70, 84, 100, 18, "#6E9CC2", a)


def book(c, t, bar):
    i = bar["i"]
    d = seg.since(seg.BARS[5], 0, t)
    k = ease_out(clamp01((d + 0.02) / 0.35))
    off = (1 - k) * SW
    c.save()
    c.translate(off, 0)
    gfx.rrect(c, CX, SY + SH / 2, SW, SH, 0, "#F6F0E3")
    txt(c, "‹ 书架", SX + 40, SY + 180, 36, "sans", GRAY, 1, "left")
    txt(c, "Aa", SX + SW - 60, SY + 180, 38, "bold", GRAY)
    txt(c, "系统之美", CX, SY + 300, 64, "serif_black", INK)
    txt(c, "第一章 · 书中例子：弹簧玩具", CX, SY + 390, 36, "sans", "#7A6A55")
    for j in range(4):
        gfx.rrect(c, CX - (60 if j == 3 else 0), SY + 480 + j * 56, SW - 160 - (120 if j == 3 else 0), 18, 9, "#DCD2C2")
    # 插图框
    gfx.rrect(c, CX, SY + 1030, SW - 160, 760, 24, "#FFFFFF", 1, stroke=("#E3D9C6", 4))
    slinky_art(c, CX, SY + 1150, t, seg.BARS[5], seg.BARS[6] if i >= 6 else None, t)
    hl = seg.since(seg.BARS[5], 2, t)
    if hl >= 0:
        w = (SW - 260) * ease_out(clamp01(hl / 0.3))
        gfx.rrect(c, SX + 130 + w / 2, SY + 1480, w, 70, 12, "#FFE58A", 0.9)
    txt(c, "手一松，它自己弹" if i >= 6 else "把弹簧提在手里……", CX, SY + 1480, 52, "black", INK,
        1 if hl >= 0 else 0.0)
    if i >= 6:
        tap = seg.since(bar, 1, t)
        if -0.4 < tap < 0.8:
            fx_ = clamp01((tap + 0.4) / 0.4)
            fy = SY + 820
            gfx.circle(c, CX + 160, fy + 120 * (1 - fx_), 46, "#F2D6BA", 0.9 if tap < 0.3 else 0.9 * (1 - (tap - 0.3) / 0.5))
            if tap >= 0:
                r = 40 + 200 * ease_out(clamp01(tap / 0.5))
                c.drawCircle(CX + 160, fy, r, skia.Paint(AntiAlias=True, Color=gfx.col(ACC, 1 - clamp01(tap / 0.5)),
                                                         Style=skia.Paint.kStroke_Style, StrokeWidth=8))
        for kk in (2, 3):
            dt = seg.since(bar, kk, t)
            if 0 <= dt < 0.5:
                txt(c, "弹！", CX + 260, SY + 900 + (kk - 2) * 200, 64, "black", ACC, 1 - dt / 0.5)
    c.restore()


# ---------------------------------------------------------------- 备忘录（小节 7）

WORDS = [("行为", False), ("藏在", False), ("结构", True), ("里", False)]


def memo(c, t, bar):
    d = seg.since(bar, 0, t)
    k = ease_out(clamp01((d + 0.05) / 0.3))
    c.save()
    c.translate(0, (1 - k) * 400)
    gfx.rrect(c, CX, SY + SH / 2, SW, SH, 0, "#FFFFFF", k)
    txt(c, "‹ 备忘录", SX + 40, SY + 180, 36, "sans", "#D9A21F", k, "left")
    txt(c, "完成", SX + SW - 70, SY + 180, 36, "bold", "#D9A21F", k)
    txt(c, "读书笔记 · 系统之美", SX + 60, SY + 330, 56, "black", INK, k, "left")
    txt(c, "今天 09:41", SX + 60, SY + 410, 30, "sans", GRAY, k, "left")
    x = SX + 60
    y = SY + 640
    for j, (w, hi) in enumerate(WORDS):
        dt = seg.since(bar, j, t)
        if dt < 0:
            break
        size = 120
        ww = gfx.text_width(w, size, "black")
        st = fx.word_pop(dt)
        if st:
            a, s_, _ = st
            if hi:
                mk = ease_out(clamp01(dt / 0.3))
                gfx.rrect(c, x + ww * mk / 2, y + 20, ww * mk + 20, 90, 10, "#FFE58A")
            c.save()
            c.translate(x + ww / 2, y)
            c.scale(s_, s_)
            txt(c, w, 0, 0, size, "black", ACC if hi else INK, a)
            c.restore()
            if hi:
                fx.sparks(c, x + ww / 2, y, dt, ["#FFD23F", "#7FE0D8", "#FFFFFF"], n=16, reach=240)
        x += ww + 20
        if x > SX + SW - 280:
            x, y = SX + 60, y + 170
    if (t * 2) % 1 < 0.5:
        gfx.rrect(c, x + 6, y, 6, 110, 3, "#D9A21F", k)
    # 键盘
    gfx.rrect(c, CX, SY + SH - 330, SW, 660, 0, "#D3D6DC", k)
    rows = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
    pressed = None
    for j in range(4):
        dt = seg.since(bar, j, t)
        if 0 <= dt < 0.12:
            pressed = j * 3 % 10
    for r, row in enumerate(rows):
        for q, ch in enumerate(row):
            kx = SX + 50 + q * 90 + r * 45
            ky = SY + SH - 560 + r * 130
            on = pressed is not None and r == 0 and q == pressed
            gfx.rrect(c, kx + 30, ky, 76, 108, 12, "#FFFFFF" if not on else "#9FB3D1", k)
            txt(c, ch, kx + 30, ky, 40, "sans", INK, k)
    c.restore()


# ---------------------------------------------------------------- 外框

def phone_frame(c, t):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeLinear([(0, 0), (W, H)], [gfx.col("#DDE6F5"), gfx.col("#F5E3EC")]))
    c.drawRect(skia.Rect.MakeWH(W, H), p)
    gfx.circle(c, 150, 300, 260, "#FFFFFF", 0.35, blur=60)
    gfx.circle(c, 950, 1650, 300, "#FFFFFF", 0.3, blur=70)


def draw(c, t):
    phone_frame(c, t)
    bar, _ = seg.bar_at(t)
    dx = dy = 0.0
    if bar["i"] == 4:
        for k in (0, 1):
            ox, oy = fx.shake_offset(seg.since(bar, k, t), 22, 0.35, seed=k)
            dx += ox
            dy += oy
    c.save()
    c.translate(dx, dy)
    gfx.rrect(c, PX + PW / 2, PY + PH / 2, PW, PH, 120, "#15171D", 1, shadow=0.45)
    c.save()
    c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(SX, SY, SW, SH), 98, 98), doAntiAlias=True)
    i = bar["i"]
    if i <= 4:
        chat(c, t)
    if i == 4:
        drop_card(c, t, bar)
    if i in (5, 6):
        book(c, t, bar)
    if i == 7:
        book(c, t, seg.BARS[6])
        memo(c, t, bar)
    # 状态栏与灵动岛
    dark = i == 4 and seg.since(bar, 0, t) > -0.1
    col = "#FFFFFF" if dark else INK
    txt(c, "9:41", SX + 110, SY + 56, 36, "bold", col)
    gfx.battery(c, SX + SW - 110, SY + 56, 64, 30, 0.8, 1.0)
    gfx.rrect(c, CX, SY + 52, 250, 70, 35, "#000000")
    c.restore()
    c.restore()
    if i == 4:
        for k in (0, 1):
            fx.flash(c, fx.flash_alpha(seg.since(bar, k, t), 0.5))


if __name__ == "__main__":
    seg.main("phone", draw)
