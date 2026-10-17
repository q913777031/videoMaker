"""逐帧场景（深夜卧室版，竖屏）：由（版式, 时间轴, 帧号）唯一确定一帧画面。

卡点机制：
- 镜头切点全部在小节强拍，主卡在切点上 0.22 秒内落版，之后完全静止；
- 每一拍：传送带步进、轨道卡片步进、信息流滚动一条、时钟冒号闪烁、主卡金色节点亮起；
- 每个小节强拍：舞台镜头轻推（只作用于舞台层，不影响文字）；
- 关键动作与音效从同一个事件帧开始（事件已吸附到原曲实测起音）。
"""

import bisect
import math

import numpy as np
import skia

from engine import gfx
from engine.gfx import clamp01, ease_in_out, ease_out, ease_out_back, lerp, prog

from . import draw as D
from . import story
from .story import FPS, GOLD, INK, WHITE
from .timeline import EXIT, Timeline

U, F = D.UPPER, D.FORE
WIDE = (0.88, 492, 600)
RESEARCH_CAM = (1.0, 546, 500)
CAMS = {1: (0.92, 480, 610), 2: (0.96, 470, 615), 3: (0.88, 492, 560), 4: (0.9, 500, 560), 5: (0.88, 492, 560),
        6: WIDE, 11: (0.98, 470, 600), 12: WIDE, 13: (0.96, 430, 600), 14: (0.92, 470, 570), 15: (0.94, 450, 590),
        16: WIDE, 17: (0.92, 480, 610), 18: (0.92, 480, 610)}
BELT_X = (230, 800)
BELT_STEP = {1: 34, 2: 30, 3: 34, 4: 38, 5: 70, 6: 46, 11: 50, 12: 40, 13: 34, 14: 30, 15: 22}

LIE = dict(hip=(560, 612), lean=90, neck=-12, sh_n=160, el_n=140, sh_f=92, el_f=88,
           th_n=92, kn_n=88, th_f=92, kn_f=88, leg_scale=0.72)
SIT = dict(hip=(440, 612), lean=48, neck=8, sh_n=20, el_n=70, sh_f=20, el_f=60,
           th_n=92, kn_n=90, th_f=92, kn_f=90, leg_scale=0.72)
REST_HAND = (470, 584)
RAISED_HAND = (400, 470)
LAMP_SWITCH = (196, 470)
STACK = (148, D.STAND_Y - 4)
CUP_STAND = (120, D.STAND_Y - 12)
BOX = (790, 430)


def ik(shoulder, target, reach=0.97, bend=-1):
    """近侧手臂两段 IK：返回 (sh_n, el_n)；超出臂长时伸直指向目标。bend 选择肘部弯向哪一侧。"""
    dx, dy = target[0] - shoulder[0], target[1] - shoulder[1]
    dist = math.hypot(dx, dy)
    d = min(dist, (U + F) * reach)
    base = math.degrees(math.atan2(dx, dy))
    if dist > d or d <= 1e-6:
        return base, base
    cos_a = max(-1.0, min(1.0, (U * U + d * d - F * F) / (2 * U * d)))
    sh = base + bend * math.degrees(math.acos(cos_a))
    r = math.radians(sh)
    el = (shoulder[0] + U * math.sin(r), shoulder[1] + U * math.cos(r))
    return sh, math.degrees(math.atan2(target[0] - el[0], target[1] - el[1]))


def with_arm(P: dict, target) -> dict:
    """躺姿（lean > 70）肘部朝床面弯，坐姿朝后下方弯。"""
    sh, el = ik(D.joints(P)["sh"], target, bend=1 if P["lean"] > 70 else -1)
    return dict(P, sh_n=sh, el_n=el)


def move(a, b, k):
    return (lerp(a[0], b[0], k), lerp(a[1], b[1], k))


class Film:
    def __init__(self, L: D.Layout, tl: Timeline):
        self.L, self.tl = L, tl
        self.beat_t = [b / FPS for b in tl.beats]
        self.down_t = [b / FPS for b in tl.downbeats]
        n = tl.total_frames
        self.offset = np.zeros(n + 1)
        for f in range(n + 1):
            self.offset[f] = self._belt_offset(f / FPS)

    # ------------------------------------------------------------ 时间与节拍

    def locate(self, f: int):
        b = self.tl.bounds
        i = max(1, min(len(story.SHOTS), bisect.bisect_right(b, f)))
        return i, (f - b[i - 1]) / FPS, (b[i] - b[i - 1]) / FPS

    def T(self, i: int) -> float:
        return self.tl.bounds[i - 1] / FPS

    def E(self, i: int, name: str) -> float:
        return self.T(i) + self.tl.ev(i, name)

    def shot_at(self, gt: float) -> int:
        return self.locate(int(round(gt * FPS)))[0]

    def since_beat(self, gt: float, beats=None) -> tuple[int, float]:
        bt = self.beat_t if beats is None else beats
        k = bisect.bisect_right(bt, gt + 1e-6) - 1
        return k, (gt - bt[k]) if k >= 0 else 99.0

    def beat_count(self, gt: float) -> float:
        """连续的拍计数：每拍前 0.16 秒快速走完一步，其余时间停住（「一拍一顿」）。"""
        k, dt = self.since_beat(gt)
        return k + ease_out(dt / 0.16) if k >= 0 else 0.0

    def _belt_offset(self, gt: float) -> float:
        off = 0.0
        for k, b in enumerate(self.beat_t):
            if b > gt:
                break
            i = self.shot_at(b)
            step = 0.0
            if i in BELT_STEP:
                step = BELT_STEP[i]
                if i == 15:
                    step *= 1 - prog(b, self.E(15, "drawer"), 2.0) * 0.5
            elif i == 16:
                step = 22 * (1 - prog(b, self.E(16, "settle"), 3.0))
            off += step * ease_out(min(1.0, (gt - b) / 0.16))
        return off

    # ------------------------------------------------------------ 镜头

    def cam_shot(self, i: int, t: float) -> tuple:
        s, fx, fy = CAMS.get(i, RESEARCH_CAM)
        if i == 6:
            k = ease_in_out(prog(t, self.tl.ev(6, "pull"), 1.6))
            s, fx, fy = lerp(0.88, 0.6, k), lerp(492, 560, k), lerp(600, 560, k)
        return s, fx, fy

    def camera(self, i: int, t: float, gt: float) -> tuple:
        s, fx, fy = self.cam_shot(i, t)
        if i > 1 and t < 0.5 and i not in (7, 8, 9, 10) and (i - 1) not in (7, 8, 9, 10):
            ps = self.cam_shot(i - 1, 99)
            k = ease_in_out(t / 0.5)
            s, fx, fy = lerp(ps[0], s, k), lerp(ps[1], fx, k), lerp(ps[2], fy, k)
        k, dt = self.since_beat(gt, self.down_t)
        if k >= 0 and i not in (18,):
            s *= 1 + 0.018 * math.exp(-dt / 0.16)
        return s, fx, fy

    # ------------------------------------------------------------ 状态

    def clock_text(self, gt: float) -> str:
        flip = self.E(1, "flip")
        if gt < flip:
            return "23:59"
        return f"00:{min(12, int((gt - flip) / 7.2)):02d}"

    def lamp_level(self, gt: float) -> float:
        if gt < self.T(2):
            return 1.0
        if gt < self.T(13):
            return 1 - ease_out(prog(gt, self.E(2, "lamp"), 0.12)) if gt < self.T(3) else 0.0
        if gt < self.T(17):
            return ease_out(prog(gt, self.T(13), 0.3))
        return 1 - ease_out(prog(gt, self.E(17, "sleep"), 0.6))

    def pose(self, gt: float) -> dict:
        T, E = self.T, self.E
        if gt < T(13):
            P = dict(LIE)
            if gt < T(2):
                P["hip"] = (560, 612 - 6 * math.exp(-gt * 6))
            hand = REST_HAND
            if T(2) <= gt < T(3):
                e = E(2, "lamp")
                k = ease_in_out(prog(gt, e - 0.45, 0.45)) * (1 - ease_in_out(prog(gt, e + 0.3, 0.6)))
                hand = move(REST_HAND, LAMP_SWITCH, k)
            elif T(4) <= gt < T(6):
                hand = move(REST_HAND, RAISED_HAND, ease_out(prog(gt, T(4), 0.25))) if gt < T(5) else RAISED_HAND
                if T(5) <= gt:
                    hand = move(RAISED_HAND, REST_HAND, ease_in_out(prog(gt, T(6) - 0.5, 0.45)))
            elif T(11) <= gt < T(12):
                hand = move(REST_HAND, RAISED_HAND, ease_out(prog(gt, T(11), 0.25)))
            elif T(12) <= gt < T(13):
                r = E(12, "reach")
                hand = move(RAISED_HAND, REST_HAND, ease_in_out(prog(gt, T(12), 0.4)))
                hand = move(hand, (640, 470), 0.85 * ease_out(prog(gt, r, 0.7)))
            return with_arm(P, hand)
        if gt < T(17):
            P = D.pose_mix(LIE, SIT, ease_in_out(prog(gt, T(13), 0.6))) if gt < T(14) else dict(SIT)
            hand = (330, 560)
            if T(13) <= gt < T(14):
                e = E(13, "tidy")
                k = ease_in_out(prog(gt, e - 0.3, 0.4)) * (1 - ease_in_out(prog(gt, e + 1.2, 0.5)))
                sx = 0.5 + 0.5 * math.sin((gt - e) * 6)
                hand = move(hand, (lerp(140, 170, sx), D.STAND_Y - 14), k)
            if gt >= T(15) and self.cup_held(gt):
                hand = (360, 520)
            return with_arm(P, hand)
        k = ease_in_out(prog(gt, E(17, "return") - 0.25, 0.8))
        P = D.pose_mix(SIT, LIE, k)
        P["eyes_closed"] = 1.0 if gt >= E(17, "sleep") else 0.0
        return with_arm(P, REST_HAND)

    def cup_held(self, gt: float) -> bool:
        return self.E(15, "choose") + 0.35 <= gt < self.T(17) + 0.5

    def headphones_on(self, gt: float) -> float:
        if gt < self.T(15):
            return 0.0
        return ease_out(prog(gt, self.E(15, "choose"), 0.35))

    def research(self, i: int, t: float, dur: float) -> float:
        if i in (7, 8, 9, 10):
            return 1.0 if i != 7 else ease_in_out(prog(t, self.tl.ev(7, "roll") + 0.15, 0.4))
        if i == 11:
            return 1 - ease_in_out(prog(t, 0.0, 0.3))
        return 0.0

    # ------------------------------------------------------------ 主绘制

    def frame(self, c: skia.Canvas, f: int):
        L = self.L
        i, t, dur = self.locate(f)
        gt = f / FPS
        cam = self.camera(i, t, gt)
        res = self.research(i, t, dur)
        dark = 0.7 * ease_in_out(prog(t, 0.0, 0.8)) if i == 18 else 0.0
        D.background(c, L, warm=0.6, dark=max(dark, res * 0.7))
        if res < 1:
            lamp = self.lamp_level(gt)
            c.save()
            D.apply_camera(c, L, cam, 0.55)
            D.blur_layer(c, 7 * L.stage_s)
            D.room_far_night(c, gt, light=(1 - res) * (1 - dark * 0.8), lamp=lamp, door=(i == 6))
            c.restore()
            c.restore()
            c.save()
            D.apply_camera(c, L, cam)
            fade = (1 - res) * (1 - dark * 0.6)
            if fade < 1:
                c.saveLayerAlpha(None, int(255 * fade))
            self.bedroom(c, i, t, gt, lamp)
            if fade < 1:
                c.restore()
            if i == 7:
                self.belt_roll(c, t)
            c.restore()
        if res > 0 and i in (7, 8, 9, 10, 11):
            c.save()
            D.apply_camera(c, L, RESEARCH_CAM)
            if res < 1:
                c.saveLayerAlpha(None, int(255 * res))
            {7: self.r_authors, 8: self.r_question, 9: self.r_method, 10: self.r_answer, 11: self.r_answer}[i](c, i, t, gt)
            if res < 1:
                c.restore()
            c.restore()
        self.text_layer(c, i, t, dur, f)
        if i == 18:
            k = prog(t, dur - 0.35, 0.33)
            if k > 0:
                c.drawPaint(D.fill(INK, k))

    # ------------------------------------------------------------ 卧室

    def bedroom(self, c, i, t, gt, lamp):
        T, E = self.T, self.E
        D.floor_line(c, 0.7)
        if gt >= T(16):
            m = ease_in_out(prog(gt, E(16, "settle"), 1.6))
            if m < 1:
                D.line(c, BOX[0], BOX[1] + 70, BOX[0], D.MATTRESS_Y, D.stroke("#4A4034", 5, 1 - m))
            D.checkbox_frame(c, BOX[0], BOX[1], 1.0, 1.0, morph=m)
        elif gt >= T(12):
            g = ease_out_back(prog(gt, E(12, "box"), 0.4), 1.2)
            if g > 0:
                D.line(c, BOX[0], BOX[1] + 70, BOX[0], lerp(D.MATTRESS_Y, BOX[1] + 70, 0) if g > 0 else 0,
                       D.stroke("#4A4034", 5, clamp01(g)))
            D.checkbox_frame(c, BOX[0], BOX[1], g, 0.85 if gt >= T(13) else 1.0)

        if gt < T(17) and i != 7:
            flash = 0.0
            for name, sh in (("flip", 1), ("empty", 6), ("reveal", 11)):
                try:
                    e = E(sh, name)
                except KeyError:
                    continue
                if gt >= e:
                    flash = max(flash, math.exp(-(gt - e) * 3))
            D.belt(c, gt, self.offset[min(int(round(gt * FPS)), len(self.offset) - 1)], 1.0, flash, 0,
                   *BELT_X)
        D.nightstand(c, 1.0, self.drawer(gt))
        k, dt = self.since_beat(gt)
        D.clock(c, self.clock_text(gt), dt < self.tl.beat_len / 2 or k < 0, 1.0,
                glow=math.exp(-max(0, gt - E(1, "flip")) * 2.5) * (gt >= E(1, "flip")))
        D.lamp(c, lamp)
        self.stand_items(c, i, t, gt)
        D.bed_back(c)
        if i in (3, 4, 5) or (i == 6 and t < 1.0):
            self.rail(c, i, t, gt)
        P = self.pose(gt)
        D.person_back(c, P)
        if self.headphones_on(gt) > 0:
            self.headphones(c, P, gt)
        D.blanket(c, P, 1.0, from_hip=P["lean"] < 80)
        self.hand_layer(c, i, t, gt, P)
        if i == 4 or (i == 5 and t < 0.5):
            a = ease_out(prog(t, 0, 0.3)) if i == 4 else 1 - prog(t, 0, 0.4)
            D.phone_feed(c, 560, 150, 250, 400, self.beat_count(gt) - self.beat_count(T(4)), a)

    def drawer(self, gt):
        if not (self.T(15) <= gt < self.T(16)):
            return 0.0
        e = self.E(15, "drawer")
        return ease_out(prog(gt, e - 0.3, 0.3)) * (1 - ease_in_out(prog(gt, e + 0.5, 0.35)))

    def stand_items(self, c, i, t, gt):
        T, E = self.T, self.E
        if gt >= T(13):
            it = E(13, "items")
            k = ease_out_back(prog(gt, it - 0.12, 0.25), 1.0)
            tidy = ease_in_out(prog(gt, E(13, "tidy"), 1.2))
            if k > 0:
                D.icon_bill(c, lerp(130, STACK[0], tidy), lerp(D.STAND_Y - 160, D.STAND_Y - 38, k) - 4 * tidy, 0.85,
                            0.75 if gt >= T(14) else 1.0, rot=lerp(-14, 0, tidy))
                D.icon_notice(c, lerp(175, STACK[0], tidy), lerp(D.STAND_Y - 200, D.STAND_Y - 20, k) - 16 * tidy, 0.85,
                              0.75 if gt >= T(14) else 1.0, rot=lerp(12, 0, tidy))
        if gt >= T(17) + 0.5:
            D.icon_cup(c, *CUP_STAND, 0.9)
            D.steam(c, CUP_STAND[0], CUP_STAND[1] - 20, gt, 0.9 * (1 - 0.6 * (i == 18)))

    def rail(self, c, i, t, gt):
        """床上方的金线轨道：待办卡（第 3 镜）与别人的小人（第 5 镜）按拍步进。"""
        y = 300
        grow = ease_in_out(prog(gt, self.T(3), 0.4))
        a = 1.0 if i != 6 else 1 - t
        D.gold_line(c, [(lerp(500, -700, grow), y), (lerp(500, 1600, grow), y)], 2.2, 0.9 * a, glow=0.3)
        bc = self.beat_count(gt) - self.beat_count(self.T(3))
        for k, name in enumerate(("card1", "card2", "card3")):
            e = self.E(3, name)
            g = ease_out_back(prog(gt, e - 0.1, 0.25), 1.3)
            if g <= 0:
                continue
            x = 700 - k * 230 - max(0.0, bc - (e - self.T(3)) / self.tl.beat_len) * 60
            x = (x + 1400) % 1400 - 300 if i >= 4 else x
            D.line(c, x + 65, y, x + 65, y + 22, D.stroke("#8C7444", 2.4, a))
            D.paper_card(c, x, y + 22 - 30 * (1 - min(g, 1)), 130, 88, a * min(g, 1), r=8, lift=0.7)
            for r in range(3):
                D.line(c, x + 20, y + 46 + r * 18, x + 108 - r * 24, y + 46 + r * 18, D.stroke("#A79A82", 3, a))
        if i == 5:
            D.label(c, "我", 420, y - 58, 30, a, GOLD)
            c.drawCircle(420, y - 18, 16, D.stroke(GOLD, 2.4, a))
            c.drawCircle(420, y - 18, 5, D.fill(GOLD, a))
            b5 = self.beat_count(gt) - self.beat_count(self.T(5))
            for k in range(6):
                x = 980 + k * 170 - b5 * 150
                if -200 < x < 1200:
                    D.runner(c, x, y - 4, b5 * 0.5 + k * 0.3, 1.7, a)

    def headphones(self, c, P, gt):
        j = D.joints(P)
        k = self.headphones_on(gt)
        hx, hy = j["head"]
        sx, sy = move((640, 380), (hx, hy), k)
        up = j["hu"]
        c.save()
        c.translate(sx, sy)
        c.rotate(math.degrees(math.atan2(up[1], up[0])) + 90)
        arc = skia.Path()
        arc.addArc(skia.Rect.MakeLTRB(-48, -50, 48, 42), 215, 110)
        c.drawPath(arc, D.stroke("#5A5246", 7))
        D.rrect(c, -15, -16, 30, 36, 10, D.fill(GOLD))
        c.restore()

    def hand_layer(self, c, i, t, gt, P):
        T, E = self.T, self.E
        item = None
        if gt < T(7) and not (T(2) <= gt < T(3)):
            raised = T(4) <= gt < T(6)

            def item(c, h, raised=raised):
                D.icon_phone(c, h[0] + 6, h[1] - 18, 1.0, -1 if raised else 1, lit=0.9)
                if raised:
                    c.drawCircle(h[0] - 30, h[1] + 30, 60, D.fill("#8FB0D8", 0.18, blur=30))
        elif T(11) <= gt < T(12):
            e = E(11, "reveal")
            g = math.exp(-max(0, gt - e) * 1.6) * (gt >= e) + 0.3

            def item(c, h, g=g):
                D.icon_eval_card(c, h[0] + 6, h[1] - 30, 1.0, 1.0, glow=g, rot=-8)
                self.drive_line(c, (h[0] + 6, h[1] - 6), g, gt)
        elif self.cup_held(gt):
            def item(c, h):
                D.icon_cup(c, h[0] + 8, h[1] - 14, 1.0)
                D.steam(c, h[0] + 8, h[1] - 34, gt, 0.9)
        D.person_front(c, P, hand_item=item)
        if T(12) <= gt < T(16):
            pos, a = (520, 600), 1.0
            if T(15) <= gt:
                e = E(15, "drawer")
                k = ease_in_out(prog(gt, e - 0.3, 0.5))
                pos = move(pos, (110, D.STAND_Y + 48), k)
                a = 1 - prog(gt, e + 0.2, 0.15)
            if a > 0:
                D.icon_eval_card(c, pos[0], pos[1], 0.8, a, glow=0.2, rot=-4)
                if gt < T(15):
                    self.drive_line(c, (pos[0], pos[1] + 18), 0.3, gt)
        if T(14) <= gt < T(16):
            self.options(c, i, t, gt)

    def options(self, c, i, t, gt):
        """第 14 镜：床上方按拍浮现三张选项卡（耳机 / 热水 / 朋友合照）；第 15 镜选中前两项。"""
        icons = (D.icon_headphones, D.icon_cup, D.icon_photo)
        names = ("obj1", "obj2", "obj3")
        xs = (370, 515, 660)
        chosen = ease_out(prog(gt, self.E(15, "choose"), 0.35)) if gt >= self.T(15) else 0.0
        for k in range(3):
            g = ease_out_back(prog(gt, self.E(14, names[k]) - 0.1, 0.28), 1.5)
            if g <= 0:
                continue
            fly = chosen if k < 2 else 0.0
            a = min(1, g) * ((1 - fly) if k < 2 else (1 - 0.5 * chosen))
            if a <= 0.01:
                continue
            x, y = xs[k], 380 - 40 * (1 - min(g, 1))
            D.paper_card(c, x - 60, y - 55, 120, 110, a, dark=True, r=12, lift=0.6)
            icons[k](c, x, y, 1.15, a)

    def drive_line(self, c, p, g, gt):
        q = (BELT_X[1], D.FLOOR_Y + 13)
        path = skia.Path()
        path.moveTo(*p)
        path.cubicTo(p[0] + 160, p[1] - 40, q[0] + 80, q[1] - 220, *q)
        a = clamp01(0.35 + g)
        c.drawPath(path, D.stroke(GOLD, 8, 0.35 * a, blur=6))
        c.drawPath(path, D.stroke(GOLD, 2.2, 0.9 * a))
        meas = skia.PathMeasure(path, False)
        Ln = meas.getLength()
        bc = self.beat_count(gt)
        for k in range(3):
            d = ((bc * 0.33 + k / 3) % 1) * Ln
            pos, _ = meas.getPosTan(d)
            c.drawCircle(pos.x(), pos.y(), 5, D.fill("#FFF2D0", 0.9 * a))

    def belt_roll(self, c, t):
        """第 7 镜：传送带卷起成论文页（舞台坐标中的过渡，随后由研究层接管）。"""
        k = ease_in_out(prog(t, self.tl.ev(7, "roll"), 0.45))
        if k <= 0 or k >= 1:
            return
        x0, y0, w0, h0 = BELT_X[0] - 26, D.FLOOR_Y - 4, BELT_X[1] - BELT_X[0] + 52, 34
        x1, y1, w1, h1 = 200, 100, 600, 260
        c.save()
        x, y, w, h = lerp(x0, x1, k), lerp(y0, y1, k), lerp(w0, w1, k), lerp(h0, h1, k)
        c.translate(x + w / 2, y + h / 2)
        c.rotate(8 * math.sin(math.pi * k))
        D.paper_card(c, -w / 2, -h / 2, w, h, 1.0, dark=k < 0.5, r=lerp(17, 8, k))
        c.restore()

    # ------------------------------------------------------------ 研究层（舞台坐标，可用 x 154—846）

    def r_authors(self, c, i, t, gt):
        D.paper_card(c, 190, 60, 620, 250, 1.0, r=10)
        for k, (txt, sz) in enumerate((("Viewing leisure as wasteful", 34), ("undermines enjoyment", 34),
                                       ("J. Exp. Soc. Psychol., 2021", 30))):
            gfx.draw_text(c, txt, 500, 120 + k * 56, sz, "bold", "#2A2620" if k < 2 else "#6B5E48")
        D.gold_line(c, [(230, 290), (770, 290)], 1.6, 0.8)
        for k, name in enumerate(story.AUTHORS):
            e = self.E(7, f"name{k + 1}")
            g = ease_out_back(prog(gt, e - 0.08, 0.26), 1.4)
            if g <= 0:
                continue
            D.name_plate(c, 190, 350 + k * 94 - 30 * (1 - min(g, 1)), 620, name, min(1, g), 36)

    def r_question(self, c, i, t, gt):
        e0 = self.E(8, "cards")
        g = ease_out_back(prog(gt, e0 - 0.08, 0.3), 1.2)
        for x, kind, lab in ((190, "hourglass", "浪费"), (580, "leisure", "休闲")):
            c.save()
            c.translate(x + 115, 360)
            c.scale(min(g, 1.1), min(g, 1.1))
            D.paper_card(c, -115, -150, 230, 300, 1.0, dark=True, r=14)
            if kind == "hourglass":
                D.hourglass_card(c, 0, -30, 1.25)
            else:
                D.icon_cup(c, -40, -20, 1.6)
                D.icon_headphones(c, 44, -36, 1.3)
            D.label(c, lab, 0, 100, 42, 1.0, GOLD if kind == "hourglass" else WHITE)
            c.restore()
        ask = self.E(8, "ask")
        q = ease_out_back(prog(gt, ask - 0.1, 0.3), 1.8)
        D.gold_line(c, [(420, 360), (580, 360)], 2, 0.8 * min(1, g))
        if q > 0:
            gfx.draw_text(c, "？", 500, 360 - 60 * (1 - min(q, 1)), 130 * min(q, 1.2), "black", GOLD, min(1, q))
        k, dt = self.since_beat(gt)
        if q >= 1:
            c.drawCircle(500, 360, 80, D.fill(GOLD, 0.25 * math.exp(-dt / 0.15), blur=24))

    def _panels(self, c, gt, play_from, covered):
        cov = ease_out_back(prog(gt, self.E(9, "covers") - 0.1, 0.3), 1.2)
        for side, lab in ((0, "其他说法"), (1, "休闲是浪费")):
            py = 40 + side * 400
            D.rrect(c, 160, py, 680, 370, 18, D.fill("#111316"))
            D.rrect(c, 160, py, 680, 370, 18, D.stroke(GOLD, 1.4, 0.4))
            c.save()
            c.translate(265, py + 185)
            c.scale(max(0.05, min(cov, 1.15)), min(cov, 1.15))
            D.paper_card(c, -85, -120, 170, 240, 1.0, dark=side == 1, r=10)
            if side == 0:
                for n in range(3):
                    wave = skia.Path()
                    wave.moveTo(-50, -70 + n * 34)
                    wave.quadTo(-25, -86 + n * 34, 0, -70 + n * 34)
                    wave.quadTo(25, -54 + n * 34, 50, -70 + n * 34)
                    c.drawPath(wave, D.stroke("#8E8066", 3))
            else:
                D.hourglass_card(c, 0, -50, 0.85)
            D.label(c, lab, 0, 78, 30 if side else 32, 1.0, "#2A2620" if side == 0 else GOLD)
            c.restore()
            x, y, w, h = 380, py + 30, 430, 310
            D.rrect(c, x - 6, y - 6, w + 12, h + 12, 12, D.fill("#050506"))
            D.rrect(c, x - 6, y - 6, w + 12, h + 12, 12, D.stroke(GOLD, 1.6, 0.7))
            if gt >= play_from:
                clip_t = (self.beat_count(gt) - self.beat_count(play_from)) * self.tl.beat_len
                D.cat_clip(c, x, y, w, h, clip_t, 1.0)
            else:
                D.rrect(c, x, y, w, h, 6, D.fill("#14171B"))
                D.icon_play(c, x + w / 2, y + h / 2, 1.2, 0.8)
            if side == 1 and covered > 0:
                c.save()
                c.translate(*move((265, py + 185), (x + w * 0.24, y + h * 0.6), min(covered, 1.05)))
                c.rotate(-6 * min(covered, 1))
                D.rrect(c, -90, -70, 180, 140, 10, D.fill("#000000", 0.5, blur=14))
                D.hourglass_card(c, 0, 0, 1.2)
                c.restore()
                c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), D.fill(INK, 0.45 * min(covered, 1)))
            if side == 0 and covered > 0:
                k, dt = self.since_beat(gt)
                D.rrect(c, x - 6, y - 6, w + 12, h + 12, 12, D.stroke(GOLD, 3, 0.4 + 0.5 * math.exp(-dt / 0.2)))

    def r_method(self, c, i, t, gt):
        self._panels(c, gt, self.E(9, "play"), 0.0)

    def r_answer(self, c, i, t, gt):
        cov = ease_out_back(prog(gt, self.E(10, "answer") - 0.1, 0.3), 1.0) if i == 10 else 1.0
        self._panels(c, gt, self.E(9, "play"), cov)

    # ------------------------------------------------------------ 文字层

    def text_alpha(self, i: int, t: float, dur: float) -> tuple:
        if i == 1:
            a, rise = 1.0, 0.0
        else:
            k = ease_out(prog(t, 0.0, 0.22))
            a, rise = k, 30 * (1 - k)
        a *= 1 - ease_in_out(prog(t, dur - EXIT + 0.1, 0.28))
        return a, rise

    def beat_node(self, f: int) -> float:
        k = bisect.bisect_right(self.tl.beats, f) - 1
        if k < 0:
            return 0.0
        return math.exp(-(f - self.tl.beats[k]) / FPS / 0.14)

    def text_layer(self, c, i, t, dur, f):
        shot = story.SHOTS[i - 1]
        a, rise = self.text_alpha(i, t, dur)
        D.main_card(c, self.L, shot.text, shot.hi, a, rise, self.beat_node(f), shot.source)
        ta = 1.0 if i == 1 else ease_out(prog(t, 0.0, 0.2))
        ta *= 1 - prog(t, dur - 0.2, 0.18)
        D.tag(c, self.L, shot.tag, ta)
