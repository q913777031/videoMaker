"""《百年孤独》每讲的开场钩子（第 0 屏，黄金 3 秒）：今天生活里的痛点画面 + 大字逐字砸下（只留砸字音效，不混配音）。

做法与接口同 fengtian/hooks.py、zizhi/hooks.py：钩子函数 hook(H, j, cx, cy, acc) 前 3 拍画面动作（每拍一个，配打击乐），
随后 fengtian.hooks._finish 让大字按配音的顿读节奏逐字砸下，再弹出系列小字。本模块在导入时把钩子注册进
fengtian.hooks（HOOKS / HOOK_TEXT / HOOK_PINYIN），并把系列小字换成本系列的（只影响本进程）。
"""
from fengtian import hooks as FH

FH.SERIES_SUB = "百年孤独 · 写给今天的我们"

HOOK_TEXT = dict(bn_pigtail="怕生出猪尾巴", bn_unfinished="都没做完", bn_forget="转头就忘", bn_push="又推开了", bn_crowd="没人可说", bn_again="又是这样",
                 bn_fog="看不清路", bn_control="为你好", bn_eyes="别人怎么看", bn_nothing="没发生过", bn_written="早就写好了")
HOOK_PINYIN = dict()
FH.HOOK_TEXT.update(HOOK_TEXT)
FH.HOOK_PINYIN.update(HOOK_PINYIN)


# ---------------------------------------------------------------- 绘制

import math  # noqa: E402

import skia  # noqa: E402

from adler import kit as K  # noqa: E402
from engine.gfx import clamp01, ease_out, lerp  # noqa: E402
from fengtian.common import BLACK, RED, draw_li, pop_scale  # noqa: E402
from whiteboard import engine as wb  # noqa: E402


def _card(c, x, y, w, h, label, frac, a=1.0):
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h), 22, 22, K.paint("#FFFFFF", a))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h), 22, 22, wb.marker(BLACK, 7, a))
    K.text(c, label, x - w / 2 + 40, y - 24, 56, "hand", BLACK, a, "left")
    bw = w - 230
    bx = x - w / 2 + 40
    c.drawRoundRect(skia.Rect.MakeXYWH(bx, y + 22, bw, 28), 14, 14, K.paint("#EEEEEE", a))
    c.drawRoundRect(skia.Rect.MakeXYWH(bx, y + 22, max(28, bw * frac), 28), 14, 14, K.paint(RED, a))
    c.drawRoundRect(skia.Rect.MakeXYWH(bx, y + 22, bw, 28), 14, 14, wb.marker(BLACK, 4, a))
    K.text(c, f"{int(frac * 100)}%", x + w / 2 - 95, y + 36, 50, "hand", RED, a)


def bn_unfinished(H, j, cx, cy, acc):
    """01 冰块：三张卡片逐拍弹出——剪视频课、健身卡、副业计划，进度条都卡在个位数；小李挠头；大字“都没做完”。"""
    rows = [("剪视频课", 0.08, cy - 540), ("健身卡", 0.03, cy - 350), ("副业计划", 0.1, cy - 160)]
    H.note(*(r[0] for r in rows), "8%", "3%", "10%")
    X = cx - 140

    def scene(c, kk, T):
        for i, (s, f, y) in enumerate(rows):
            t0 = H.tb(j, i)
            sc = pop_scale(T - t0)
            if sc <= 0:
                continue
            grow = ease_out(clamp01((T - t0 - 0.15) / 0.35))
            with K.at(c, X, y, 0, sc):
                _card(c, 0, 0, 720, 150, s, f * grow)
        sc = pop_scale(T - H.tb(j, 0))
        if sc > 0:
            lx, ly = cx + 400, cy + 120
            with K.at(c, lx, ly, 0, sc):
                c.translate(-lx, -ly)
                hy = ly - 290 * 0.85
                draw_li(c, lx, ly, 0.85, "sad" if T >= H.tb(j, 2) else "flat",
                        rh=(lx + 40, hy - 50) if T >= H.tb(j, 1) else None)
        return None
    H.b.custom(j, 0, 0.3, scene, sfx="pop", gain=0.7)
    H.b.hit(j, 1, "pop", 0.7, "健身卡")
    H.b.hit(j, 2, "rim", 0.8, "副业计划")
    FH._finish(H, j, cx, cy, HOOK_TEXT["bn_unfinished"], acc, text_sfx="kick")


FH.HOOKS.update(bn_unfinished=bn_unfinished)


def bn_forget(H, j, cx, cy, acc):
    """02 标签：冰箱门上贴满便利贴，逐拍一张张掉下来，最后手机提醒弹满屏；大字“转头就忘”。"""
    from fengtian.common import ORANGE
    H.note("回消息", "交电费", "取快递", "提醒")
    FX, FY, FW, FH_ = cx - 120, cy - 330, 460, 640
    notes = [("回消息", FX - 90, FY - 170), ("交电费", FX + 100, FY - 30), ("取快递", FX - 60, FY + 130)]

    def scene(c, kk, T):
        sc = pop_scale(T - H.tb(j, 0))
        if sc <= 0:
            return None
        with K.at(c, FX, FY, 0, sc):
            c.drawRoundRect(skia.Rect.MakeXYWH(-FW / 2, -FH_ / 2, FW, FH_), 30, 30, K.paint("#F4F6F8"))
            c.drawRoundRect(skia.Rect.MakeXYWH(-FW / 2, -FH_ / 2, FW, FH_), 30, 30, wb.marker(BLACK, 8))
            c.drawLine(-FW / 2, -FH_ / 2 + 220, FW / 2, -FH_ / 2 + 220, wb.marker(BLACK, 6))
            c.drawLine(FW / 2 - 50, -FH_ / 2 + 60, FW / 2 - 50, -FH_ / 2 + 170, wb.marker(BLACK, 10))
        for i, (s, x, y) in enumerate(notes):
            t_fall = H.tb(j, i + 0.5)
            f = clamp01((T - t_fall) / 0.45)
            yy = y + 700 * f * f
            rot = (i - 1) * 4 + 50 * f
            a = 1 - clamp01((T - t_fall - 0.3) / 0.2)
            if a <= 0:
                continue
            with K.at(c, x, yy, rot, sc):
                c.drawRect(skia.Rect.MakeXYWH(-110, -60, 220, 120), K.paint("#FFF1A8", a))
                c.drawRect(skia.Rect.MakeXYWH(-110, -60, 220, 120), wb.marker(ORANGE, 4, a))
                K.text(c, s, 0, 0, 46, "hand", BLACK, a)
        t2 = H.tb(j, 2)
        if T >= t2:
            PX, PY = cx + 380, cy - 300
            with K.at(c, PX, PY, 6, pop_scale(T - t2)):
                c.drawRoundRect(skia.Rect.MakeXYWH(-110, -190, 220, 380), 26, 26, K.paint("#FFFFFF"))
                c.drawRoundRect(skia.Rect.MakeXYWH(-110, -190, 220, 380), 26, 26, wb.marker(BLACK, 7))
                for q in range(4):
                    g = pop_scale(T - t2 - q * 0.07, 0.2)
                    if g > 0:
                        with K.at(c, 0, -120 + q * 80, 0, g):
                            c.drawRoundRect(skia.Rect.MakeXYWH(-90, -30, 180, 60), 14, 14, K.paint("#FDE2DE"))
                            K.text(c, "提醒", -20, 0, 34, "sans_medium", RED)
                            c.drawCircle(70, 0, 14, K.paint(RED))
        return None
    H.b.custom(j, 0, 0.3, scene, sfx="wood_high", gain=0.65)
    H.b.hit(j, 1, "pop", 0.7, "便利贴掉下来")
    H.b.hit(j, 2, "rim", 0.8, "提醒弹满屏")
    FH._finish(H, j, cx, cy, HOOK_TEXT["bn_forget"], acc, text_sfx="kick")


def bn_push(H, j, cx, cy, acc):
    """03 黑纱布：手机输入框里“我没事”打出来、删掉、又打出来，发出去；对面的人影转身走远；大字“又推开了”。"""
    H.note("我没事", "发送")
    PX, PY = cx - 120, cy - 300

    def scene(c, kk, T):
        sc = pop_scale(T - H.tb(j, 0))
        if sc <= 0:
            return None
        with K.at(c, PX, PY, 0, sc):
            c.drawRoundRect(skia.Rect.MakeXYWH(-260, -330, 520, 660), 40, 40, K.paint("#FFFFFF"))
            c.drawRoundRect(skia.Rect.MakeXYWH(-260, -330, 520, 660), 40, 40, wb.marker(BLACK, 8))
            c.drawRoundRect(skia.Rect.MakeXYWH(-220, -280, 300, 90), 30, 30, K.paint("#E9EEF4"))
            K.text(c, "在吗？还好吗？", -70, -235, 36, "sans_medium", BLACK)
            c.drawRoundRect(skia.Rect.MakeXYWH(-230, 200, 340, 90), 20, 20, wb.marker(BLACK, 5))
            c.drawRoundRect(skia.Rect.MakeXYWH(130, 205, 100, 80), 20, 20, K.paint(RED))
            K.text(c, "发送", 180, 245, 32, "sans_medium", "#FFFFFF")
            t1, t2 = H.tb(j, 1), H.tb(j, 2)
            if T < t1:
                n = min(3, int((T - H.tb(j, 0)) / 0.12) + 1)
                K.text(c, "我没事"[:n], -200, 245, 50, "hand", BLACK, 1, "left")
            elif T < t2:
                n = max(0, 3 - int((T - t1) / 0.1) - 1)
                K.text(c, "我没事"[:n], -200, 245, 50, "hand", BLACK, 1, "left")
            else:
                f = clamp01((T - t2) / 0.3)
                y = lerp(245, 0, ease_out(f))
                with K.at(c, lerp(-60, 60, f), y, 0, 1):
                    c.drawRoundRect(skia.Rect.MakeXYWH(-120, -45, 240, 90), 30, 30, K.paint("#D3EDDC"))
                    K.text(c, "我没事", 0, 0, 50, "hand", BLACK)
        t2 = H.tb(j, 2)
        if T >= t2:
            f = ease_out(clamp01((T - t2) / 0.8))
            x = lerp(cx + 330, cx + 520, f)
            draw_li(c, x, cy + 120, 0.75, "flat", back=True, alpha=1 - 0.5 * f)
        return None
    H.b.custom(j, 0, 0.3, scene, sfx="wood_high", gain=0.65)
    H.b.hit(j, 1, "shaker", 0.7, "删掉")
    H.b.hit(j, 2, "rim", 0.8, "又发了我没事")
    FH._finish(H, j, cx, cy, HOOK_TEXT["bn_push"], acc, text_sfx="kick")


FH.HOOKS.update(bn_forget=bn_forget, bn_push=bn_push)


def bn_crowd(H, j, cx, cy, acc):
    """04 粉笔圈：群聊红点跳到 999+，通讯录一路往下滑，名字一个个变灰；大字“没人可说”。"""
    H.note("999+", "群聊", "通讯录")
    PX, PY = cx - 60, cy - 300
    NAMES = ["阿杰", "表姐", "老同学", "房东", "王经理", "健身教练", "快递", "前同事", "小张", "大刘", "物业", "阿梅"]

    def scene(c, kk, T):
        sc = pop_scale(T - H.tb(j, 0))
        if sc <= 0:
            return None
        t1, t2 = H.tb(j, 1), H.tb(j, 2)
        with K.at(c, PX, PY, 0, sc):
            c.drawRoundRect(skia.Rect.MakeXYWH(-300, -340, 600, 680), 40, 40, K.paint("#FFFFFF"))
            c.drawRoundRect(skia.Rect.MakeXYWH(-300, -340, 600, 680), 40, 40, wb.marker(BLACK, 8))
            if T < t1:
                K.text(c, "群聊", -120, -250, 48, "sans_medium", BLACK)
                n = min(999, int(30 * 2 ** ((T - H.tb(j, 0)) * 9)))
                with K.at(c, 120, -250, 0, 1):
                    c.drawRoundRect(skia.Rect.MakeXYWH(-90, -36, 180, 72), 36, 36, K.paint(RED))
                    K.text(c, "999+" if n >= 999 else str(n), 0, 2, 44, "sans_medium", "#FFFFFF")
                for q in range(4):
                    c.drawRoundRect(skia.Rect.MakeXYWH(-250, -150 + q * 110, 500, 80), 20, 20, K.paint("#E9EEF4"))
            else:
                K.text(c, "通讯录", 0, -270, 46, "sans_medium", BLACK)
                c.save()
                c.clipRect(skia.Rect.MakeXYWH(-290, -220, 580, 540))
                off = min(1.0, (T - t1) / 0.8) * 700
                for q, nm in enumerate(NAMES):
                    y = -170 + q * 100 - off
                    gray = T >= t2 + q * 0.03 - 0.2
                    c.drawCircle(-220, y, 30, K.paint("#C9CCD2" if gray else "#9FB1C6"))
                    K.text(c, nm, -160, y, 44, "hand", "#A0A4AC" if gray else BLACK, 1, "left")
                c.restore()
        return None
    H.b.custom(j, 0, 0.3, scene, sfx="pop", gain=0.7)
    H.b.hit(j, 1, "shaker", 0.7, "通讯录往下滑")
    H.b.hit(j, 2, "rim", 0.8, "名字都变灰")
    FH._finish(H, j, cx, cy, HOOK_TEXT["bn_crowd"], acc, text_sfx="kick")


FH.HOOKS.update(bn_crowd=bn_crowd)


def _stone(c, x, y, a=1.0):
    c.drawOval(skia.Rect.MakeXYWH(x - 70, y - 44, 140, 60), K.paint("#9AA0A8", a))
    c.drawOval(skia.Rect.MakeXYWH(x - 70, y - 44, 140, 60), wb.marker(BLACK, 6, a))


def bn_again(H, j, cx, cy, acc):
    """05 名字：小李走路，每拍被同一块石头绊倒一次（三次），头顶冒出“3”；大字“又是这样”。"""
    H.note("1", "2", "3")
    GY = cy + 120
    SX = cx + 60

    def scene(c, kk, T):
        sc = pop_scale(T - H.tb(j, 0))
        if sc <= 0:
            return None
        c.drawLine(cx - 560, GY + 6, cx + 560, GY + 6, wb.marker(BLACK, 6))
        _stone(c, SX, GY, sc)
        k = H.beat_at(j, T)
        n = min(3, int(math.floor(k)) + 1)
        u = k - math.floor(k)
        if k >= 2.45:
            x, fall = SX - 70, clamp01((k - 2) / 0.2)
        elif u < 0.45:
            x, fall = SX - 70, clamp01(u / 0.2)
        else:
            x, fall = lerp(cx - 420, SX - 70, ease_out(clamp01((u - 0.45) / 0.5))), 0.0
        with K.at(c, x, GY, 75 * fall, 1):
            draw_li(c, 0, 0, 0.8, "o" if fall > 0.5 else "flat")
        for i in range(n):
            K.text(c, str(i + 1), SX + 140 + i * 90, cy - 320 - i * 30, 90, "hand", RED, clamp01((k - i) / 0.2))
        return None
    H.b.custom(j, 0, 0.3, scene, sfx="tom", gain=0.6)
    H.b.hit(j, 1, "tom", 0.7, "又绊倒")
    H.b.hit(j, 2, "tom", 0.8, "第三次")
    FH._finish(H, j, cx, cy, HOOK_TEXT["bn_again"], acc, text_sfx="kick")


FH.HOOKS.update(bn_again=bn_again)


def bn_fog(H, j, cx, cy, acc):
    """06 眼睛：路口一根路标杆挂三块牌子，雾一拍吞掉一块；小李站在路口张望；大字“看不清路”。"""
    H.note("东", "西", "北")
    PX, GY = cx - 60, cy + 120
    SIGNS = [("东", 1, cy - 470), ("西", -1, cy - 340), ("北", 1, cy - 210)]

    def scene(c, kk, T):
        sc = pop_scale(T - H.tb(j, 0))
        if sc <= 0:
            return None
        c.drawLine(PX, GY, PX, cy - 540, wb.marker("#6E4E22", 14, sc))
        for i, (s, d, y) in enumerate(SIGNS):
            gone = clamp01((T - H.tb(j, i + 0.4)) / 0.4)
            a = sc * (1 - gone)
            if a <= 0:
                continue
            x = PX + d * 150
            pts = [(PX, y - 45), (PX + d * 260, y - 45), (PX + d * 310, y), (PX + d * 260, y + 45), (PX, y + 45)]
            path = skia.Path()
            path.addPoly([skia.Point(*p) for p in pts], True)
            c.drawPath(path, K.paint("#FFFFFF", a))
            c.drawPath(path, wb.marker(BLACK, 6, a))
            K.text(c, s, x, y, 56, "hand", BLACK, a)
        for q in range(9):
            t0 = H.tb(j, q / 3)
            f = ease_out(clamp01((T - t0) / 0.8))
            if f <= 0:
                continue
            fx = cx - 520 + (q % 3) * 520 + 60 * math.sin(T + q)
            fy = cy - 520 + (q // 3) * 170
            c.drawOval(skia.Rect.MakeXYWH(fx - 260 * f, fy - 70 * f, 520 * f, 140 * f), K.paint("#D9DCE1", 0.55 * f))
        with K.at(c, cx + 330, GY, 0, sc):
            draw_li(c, 0, 0, 0.8, "o" if T >= H.tb(j, 2) else "flat", rh=(40, -300))
        return None
    H.b.custom(j, 0, 0.3, scene, sfx="wood_low", gain=0.6)
    H.b.hit(j, 1, "shaker", 0.7, "雾吞掉路牌")
    H.b.hit(j, 2, "rim", 0.8, "全看不见了")
    FH._finish(H, j, cx, cy, HOOK_TEXT["bn_fog"], acc, text_sfx="kick")


FH.HOOKS.update(bn_fog=bn_fog)


def bn_control(H, j, cx, cy, acc):
    """07 黄蝴蝶：一个小人站在中间，手机定位、门禁、日程表三样东西逐拍落下把他围住；大字“为你好”。"""
    from fengtian.common import BLUE, ORANGE
    H.note("定位", "门禁 22:00", "日程表")
    PX, GY = cx, cy + 80

    def scene(c, kk, T):
        sc = pop_scale(T - H.tb(j, 0))
        if sc <= 0:
            return None
        with K.at(c, PX, GY, 0, sc):
            draw_li(c, 0, 0, 0.8, "sad" if T >= H.tb(j, 2) else "flat")
        items = [(-330, cy - 420, "定位"), (330, cy - 420, "门禁 22:00"), (0, cy - 560, "日程表")]
        for i, (dx, y, s) in enumerate(items):
            t0 = H.tb(j, i)
            if T < t0:
                continue
            f = ease_out(clamp01((T - t0) / 0.3))
            x = PX + dx
            yy = lerp(y - 200, y, f)
            with K.at(c, x, yy, 0, pop_scale(T - t0)):
                c.drawRoundRect(skia.Rect.MakeXYWH(-150, -60, 300, 120), 24, 24, K.paint("#FFFFFF"))
                c.drawRoundRect(skia.Rect.MakeXYWH(-150, -60, 300, 120), 24, 24, wb.marker((RED, BLUE, ORANGE)[i], 7))
                K.text(c, s, 0, 0, 46 if len(s) < 5 else 40, "hand", BLACK)
            c.drawLine(x, yy + 60, PX + dx * 0.25, GY - 250, wb.marker((RED, BLUE, ORANGE)[i], 4, 0.6 * f))
        if T >= H.tb(j, 2):
            ring = skia.Path()
            ring.addOval(skia.Rect.MakeXYWH(PX - 220, GY - 330, 440, 380))
            c.drawPath(wb.partial(ring, ease_out(clamp01((T - H.tb(j, 2)) / 0.4)))[0], wb.marker(RED, 8))
        return None
    H.b.custom(j, 0, 0.3, scene, sfx="wood_high", gain=0.65)
    H.b.hit(j, 1, "wood_high", 0.7, "门禁")
    H.b.hit(j, 2, "rim", 0.8, "日程表围住")
    FH._finish(H, j, cx, cy, HOOK_TEXT["bn_control"], acc, text_sfx="kick")


def bn_eyes(H, j, cx, cy, acc):
    """08 床单：镜子前一件件衣服飞出去，镜框四周冒出一只只眼睛；大字“别人怎么看”。"""
    from fengtian.common import BLUE, ORANGE
    MX, MY = cx - 80, cy - 300

    def eye(c, x, y, s, a=1.0):
        with K.at(c, x, y, 0, s):
            c.drawOval(skia.Rect.MakeXYWH(-50, -26, 100, 52), K.paint("#FFFFFF", a))
            c.drawOval(skia.Rect.MakeXYWH(-50, -26, 100, 52), wb.marker(BLACK, 5, a))
            c.drawCircle(0, 0, 16, K.paint(BLACK, a))

    def scene(c, kk, T):
        sc = pop_scale(T - H.tb(j, 0))
        if sc <= 0:
            return None
        with K.at(c, MX, MY, 0, sc):
            c.drawRoundRect(skia.Rect.MakeXYWH(-200, -300, 400, 600), 190, 190, K.paint("#E8EEF8"))
            c.drawRoundRect(skia.Rect.MakeXYWH(-200, -300, 400, 600), 190, 190, wb.marker("#8A6A3A", 12))
        for i in range(3):
            t0 = H.tb(j, i + 0.1)
            if T < t0:
                continue
            f = clamp01((T - t0) / 0.6)
            x = lerp(MX, MX + (-450, 420, -380)[i], f)
            y = lerp(MY + 100, MY - 250 + i * 180, f) - 200 * math.sin(f * math.pi)
            with K.at(c, x, y, 200 * f * (1 if i % 2 else -1), 1):
                p = skia.Path()
                p.addPoly([skia.Point(*q) for q in ((-60, -60), (-25, -70), (25, -70), (60, -60), (80, 0), (45, 10),
                                                    (45, 70), (-45, 70), (-45, 10), (-80, 0))], True)
                c.drawPath(p, K.paint((RED, BLUE, ORANGE)[i]))
                c.drawPath(p, wb.marker(BLACK, 5))
        for q in range(8):
            t0 = H.tb(j, 1 + q * 0.2)
            if T < t0:
                continue
            a = q / 8 * 2 * math.pi
            eye(c, MX + 290 * math.cos(a), MY + 380 * math.sin(a), pop_scale(T - t0))
        return None
    H.b.custom(j, 0, 0.3, scene, sfx="pop", gain=0.65)
    H.b.hit(j, 1, "pop", 0.7, "眼睛冒出来")
    H.b.hit(j, 2, "rim", 0.8, "满是眼睛")
    FH._finish(H, j, cx, cy, HOOK_TEXT["bn_eyes"], acc, text_sfx="kick")


def bn_nothing(H, j, cx, cy, acc):
    """09 大雨：会议桌上一张红色报表，一只只手逐拍伸过来把它盖住；大字“没发生过”。"""
    H.note("报表", "-38%")
    RX, RY = cx - 40, cy - 300

    def hand(c, x, y, rot, a=1.0):
        with K.at(c, x, y, rot, 1):
            c.drawRoundRect(skia.Rect.MakeXYWH(-70, -60, 140, 120), 40, 40, K.paint("#FFFFFF", a))
            c.drawRoundRect(skia.Rect.MakeXYWH(-70, -60, 140, 120), 40, 40, wb.marker(BLACK, 6, a))
            c.drawLine(70, 0, 260, 0, wb.marker(BLACK, 30, a))
            c.drawLine(70, 0, 260, 0, wb.marker("#FFFFFF", 18, a))

    def scene(c, kk, T):
        sc = pop_scale(T - H.tb(j, 0))
        if sc <= 0:
            return None
        c.drawRect(skia.Rect.MakeXYWH(cx - 560, cy - 80, 1120, 40), K.paint("#E7D6BA"))
        with K.at(c, RX, RY, -4, sc):
            c.drawRect(skia.Rect.MakeXYWH(-230, -270, 460, 540), K.paint("#FFFFFF"))
            c.drawRect(skia.Rect.MakeXYWH(-230, -270, 460, 540), wb.marker(BLACK, 7))
            K.text(c, "报表", 0, -200, 54, "hand", BLACK)
            c.drawLine(-160, 100, -60, 0, wb.marker(RED, 10))
            c.drawLine(-60, 0, 40, 60, wb.marker(RED, 10))
            c.drawLine(40, 60, 160, 180, wb.marker(RED, 10))
            K.text(c, "-38%", 60, -90, 70, "hand", RED)
        for i, (dx, dy, rot) in enumerate(((-200, -80, -150), (220, -120, -20), (0, 120, 90))):
            t0 = H.tb(j, i + 0.6)
            if T < t0:
                continue
            f = ease_out(clamp01((T - t0) / 0.3))
            ang = math.radians(rot)
            x = RX + dx + math.cos(ang) * 400 * (1 - f)
            y = RY + dy + math.sin(ang) * 400 * (1 - f)
            hand(c, x, y, rot)
        return None
    H.b.custom(j, 0, 0.3, scene, sfx="wood_high", gain=0.65)
    H.b.hit(j, 1, "wood_low", 0.7, "一只手盖住")
    H.b.hit(j, 2, "rim", 0.8, "全盖住")
    FH._finish(H, j, cx, cy, HOOK_TEXT["bn_nothing"], acc, text_sfx="kick")


def bn_written(H, j, cx, cy, acc):
    """10 羊皮卷：一卷羊皮卷从上往下展开，上面一行行写着“小李明天会……”；大字“早就写好了”。"""
    H.note("小李", "明天会着急", "会吼孩子", "会后悔")
    PX, PY = cx - 40, cy - 330
    ROWS = ["小李", "明天会着急", "会吼孩子", "会后悔"]

    def scene(c, kk, T):
        sc = pop_scale(T - H.tb(j, 0))
        if sc <= 0:
            return None
        f = ease_out(clamp01((T - H.tb(j, 0)) / 0.6))
        h = 620 * f
        top = PY - 310
        c.drawRect(skia.Rect.MakeXYWH(PX - 300, top, 600, h), K.paint("#F3E3C0"))
        c.drawRect(skia.Rect.MakeXYWH(PX - 300, top, 600, h), wb.marker("#8A6A3A", 6))
        for yy in (top, top + h):
            c.drawRoundRect(skia.Rect.MakeXYWH(PX - 330, yy - 18, 660, 36), 16, 16, K.paint("#C9A46A"))
            c.drawRoundRect(skia.Rect.MakeXYWH(PX - 330, yy - 18, 660, 36), 16, 16, wb.marker("#8A6A3A", 4))
        for i, s in enumerate(ROWS):
            t0 = H.tb(j, 0.5 + i * 0.6)
            if T < t0:
                continue
            K.text(c, s, PX, top + 90 + i * 130, 60 if i else 66, "hand", RED if i == 0 else BLACK, clamp01((T - t0) / 0.25))
        return None
    H.b.custom(j, 0, 0.3, scene, sfx="wood_low", gain=0.65)
    H.b.hit(j, 1, "pop", 0.7, "一行行写着")
    H.b.hit(j, 2, "rim", 0.8, "全写好了")
    FH._finish(H, j, cx, cy, HOOK_TEXT["bn_written"], acc, text_sfx="kick")


FH.HOOKS.update(bn_control=bn_control, bn_eyes=bn_eyes, bn_nothing=bn_nothing, bn_written=bn_written)


def pig_tail(c, x, y, s=1.0, a=1.0, f=1.0, color="#E58FA0"):
    """一条卷卷的猪尾巴（螺旋线），f 为画出的比例。"""
    p = skia.Path()
    n = 60
    pts = []
    for i in range(n + 1):
        u = i / n
        ang = u * 3.2 * math.pi
        r = (10 + 60 * u) * s
        pts.append((x + r * math.cos(ang) + 140 * s * u, y + r * math.sin(ang)))
    p.moveTo(*pts[0])
    for q in pts[1: max(2, int(len(pts) * f))]:
        p.lineTo(*q)
    c.drawPath(p, wb.marker(color, 16 * s, a))
    c.drawPath(p, wb.marker("#9C4A5A", 4 * s, 0.7 * a))


def bn_pigtail(H, j, cx, cy, acc):
    """01 冰块（故事体）：羊皮卷上浮出一个襁褓，一条卷卷的猪尾巴一拍一拍画出来，问号弹出；大字“怕生出猪尾巴”。"""
    PX, PY = cx - 40, cy - 330

    def scene(c, kk, T):
        sc = pop_scale(T - H.tb(j, 0))
        if sc <= 0:
            return None
        with K.at(c, PX, PY, 0, sc):
            c.drawRoundRect(skia.Rect.MakeXYWH(-380, -300, 760, 600), 24, 24, K.paint("#F3E3C0"))
            c.drawRoundRect(skia.Rect.MakeXYWH(-380, -300, 760, 600), 24, 24, wb.marker("#8A6A3A", 7))
            c.drawOval(skia.Rect.MakeXYWH(-230, -90, 300, 180), K.paint("#FFFFFF"))
            c.drawOval(skia.Rect.MakeXYWH(-230, -90, 300, 180), wb.marker(BLACK, 6))
            c.drawCircle(-170, -10, 55, K.paint("#FFFFFF"))
            c.drawCircle(-170, -10, 55, wb.marker(BLACK, 6))
            for sg in (-1, 1):
                c.drawCircle(-170 + sg * 18, -18, 5, K.paint(BLACK))
        f = clamp01((T - H.tb(j, 1)) / 0.8)
        if f > 0:
            pig_tail(c, PX + 70, PY + 20, 1.1, 1.0, f)
        if T >= H.tb(j, 2):
            with K.at(c, PX + 290, PY - 170, 0, pop_scale(T - H.tb(j, 2))):
                K.text(c, "？", 0, 0, 170, "hand", RED)
        return None
    H.b.custom(j, 0, 0.3, scene, sfx="wood_low", gain=0.6)
    H.b.hit(j, 1, "shaker", 0.7, "猪尾巴卷出来")
    H.b.hit(j, 2, "rim", 0.85, "问号")
    FH._finish(H, j, cx, cy, HOOK_TEXT["bn_pigtail"], acc, text_sfx="kick")


FH.HOOKS.update(bn_pigtail=bn_pigtail)
