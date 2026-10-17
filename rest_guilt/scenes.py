"""逐帧场景：由（版式, 时间轴, 帧号）唯一确定一帧画面。

画面状态全部由时间轴事件推导：关键动作在事件帧开始，因此按原曲校准时间轴后，画面撞击与音效起音天然同帧。
主卡在阅读窗口内完全静止（不漂浮、不缩放、不抖动），镜头运动只作用于舞台层。
"""

import math

import numpy as np
import skia

from engine import gfx
from engine.gfx import clamp01, ease_in_out, ease_out, ease_out_back, lerp, prog

from . import draw as D
from . import story
from .story import FPS, GOLD, INK
from .timeline import ENTER, EXIT, Timeline

U, F = D.UPPER, D.FORE

CAMS = {
    1: (1.08, 470, 640), 2: (1.0, 470, 600), 3: (1.12, 450, 580), 4: (0.72, 540, 560),
    5: (0.95, 480, 560), 6: (1.0, 500, 500), 7: (1.0, 500, 500), 8: (1.08, 470, 620),
    9: (0.98, 600, 620), 10: (1.12, 560, 640), 11: (1.12, 580, 650), 12: (1.1, 560, 640),
    13: (1.0, 580, 600), 14: (1.08, 470, 640), 15: (1.08, 470, 640),
}
POSE_TIDY = dict(D.POSE_SIT, lean=-26, neck=14, sh_f=-10, el_f=40)
POSE_HOLD = dict(D.POSE_SIT, sh_n=52, el_n=118)
CARD_LAP = (470, 664)
TABLE_TOP = 606
CUP_ON_TABLE = (634, TABLE_TOP - 8)
PHOTO_ON_TABLE = (694, TABLE_TOP - 12)
STACK_ON_TABLE = (742, TABLE_TOP - 4)
BOX = (850, 540)


def ik(shoulder, target, reach=0.97):
    """近侧手臂两段 IK：返回 (sh_n, el_n) 角度（0 = 竖直向下，正值朝前）；超出臂长时伸直指向目标。"""
    dx, dy = target[0] - shoulder[0], target[1] - shoulder[1]
    d = min(math.hypot(dx, dy), (U + F) * reach)
    base = math.degrees(math.atan2(dx, dy))
    cos_a = clamp01((U * U + d * d - F * F) / (2 * U * d)) if d > 0 else 1
    a = math.degrees(math.acos(cos_a))
    sh = base - a
    el_dir = math.radians(sh)
    el = (shoulder[0] + U * math.sin(el_dir), shoulder[1] + U * math.cos(el_dir))
    fx, fy = target[0] - el[0], target[1] - el[1]
    if math.hypot(dx, dy) > d:
        return base, base
    return sh, math.degrees(math.atan2(fx, fy))


def with_arm(P: dict, target) -> dict:
    j = D.joints(P)
    sh, el = ik(j["sh"], target)
    return dict(P, sh_n=sh, el_n=el)


class Film:
    """一套版式下的全片绘制器。"""

    def __init__(self, L: D.Layout, tl: Timeline):
        self.L, self.tl = L, tl
        n = tl.total_frames
        self.offset = np.zeros(n + 1)
        for f in range(n):
            self.offset[f + 1] = self.offset[f] + self.belt_speed(f / FPS) / FPS

    # ------------------------------------------------------------ 时间工具

    def locate(self, f: int):
        b = self.tl.bounds
        i = max(1, min(len(story.SHOTS), int(np.searchsorted(b, f, side="right"))))
        return i, (f - b[i - 1]) / FPS, (b[i] - b[i - 1]) / FPS

    def T(self, i: int) -> float:
        return self.tl.bounds[i - 1] / FPS

    def E(self, i: int, name: str) -> float:
        """事件的全局秒数。"""
        return self.T(i) + self.tl.ev(i, name)

    def belt_speed(self, gt: float) -> float:
        if gt < self.E(1, "reveal"):
            return 110
        if gt < self.T(5):
            return 170
        if gt < self.T(8):
            return 0
        if gt < self.T(12):
            return 150
        if gt < self.T(13):
            k = prog(gt, self.E(12, "drawer"), 1.2)
            return lerp(150, 70, ease_in_out(k))
        if gt < self.T(14):
            return lerp(70, 0, ease_in_out(prog(gt, self.E(13, "settle"), 3.0)))
        return 0

    # ------------------------------------------------------------ 镜头

    def cam_shot(self, i: int, t: float, dur: float) -> tuple:
        s, fx, fy = CAMS[i]
        if i == 1:
            s = lerp(1.06, 1.08, ease_out(clamp01(t / max(self.tl.ev(1, "reveal"), 0.1))))
        elif i == 3:
            s = lerp(1.12, 1.15, t / dur)
        elif i == 4:
            k = ease_in_out(prog(t, self.tl.ev(4, "pull"), 2.8))
            s, fx, fy = lerp(1.05, 0.72, k), lerp(470, 540, k), lerp(600, 560, k)
        elif i == 9:
            s = lerp(1.05, 0.98, ease_in_out(prog(t, self.tl.ev(9, "reach"), 2.2)))
        elif i in (2, 8, 10, 11, 12, 13):
            s = s * (1 + 0.012 * t / dur)
        return s, fx, fy

    def camera(self, i: int, t: float, dur: float) -> tuple:
        cur = self.cam_shot(i, t, dur)
        if i == 1 or i in (6, 7) or i == 14 or t >= 0.55:
            return cur
        pi = i - 1
        pdur = (self.tl.bounds[pi] - self.tl.bounds[pi - 1]) / FPS
        prev = self.cam_shot(pi, pdur, pdur)
        if pi in (6, 7):
            return cur
        k = ease_in_out(t / 0.55)
        return tuple(lerp(a, b, k) for a, b in zip(prev, cur))

    # ------------------------------------------------------------ 人物与物件状态

    def pose(self, gt: float) -> dict:
        T, E = self.T, self.E
        if gt < T(2):
            P = dict(D.POSE_SIT)
            P["hip"] = (330, 690 - 12 * (1 - ease_out(clamp01(gt / 0.35))))
            return P
        if gt < T(8):
            P = D.pose_mix(D.POSE_SIT, D.POSE_RECLINE, ease_in_out(prog(gt, T(2), 0.7)))
            if T(3) <= gt < T(4):
                ph = E(3, "phone")
                k = ease_in_out(prog(gt, ph - 0.2, 0.5)) * (1 - ease_in_out(prog(gt, ph + 0.7, 0.6)))
                P = with_arm(P, (lerp(D.hand_pos(P)[0], 520, k), lerp(D.hand_pos(P)[1], 586, k))) if k > 0 else P
            return P
        if gt < T(10):
            P = D.pose_mix(D.POSE_RECLINE, POSE_HOLD, ease_in_out(prog(gt, T(8), 0.7)))
            if gt >= T(9):
                P = D.pose_mix(POSE_HOLD, D.POSE_SIT, ease_in_out(prog(gt, T(9), 0.5)))
                r = E(9, "reach")
                k = ease_out(prog(gt, r, 0.9))
                P = D.pose_mix(P, dict(P, lean=-6), k)
                tgt = (lerp(D.hand_pos(P)[0], 600, k), lerp(D.hand_pos(P)[1], 545, k))
                P = with_arm(P, tgt) if k > 0 else P
            return P
        if gt < T(11):
            a = E(10, "tidy")
            k = ease_in_out(prog(gt, a - 0.6, 0.6)) * (1 - ease_in_out(prog(gt, a + 1.6, 0.6)))
            P = D.pose_mix(D.POSE_SIT, POSE_TIDY, k)
            if k > 0.01:
                sx = 0.5 + 0.5 * math.sin((gt - a) * 3.2)
                P = with_arm(P, (lerp(D.hand_pos(P)[0], lerp(700, 744, sx), k), lerp(D.hand_pos(P)[1], TABLE_TOP - 8, k)))
            return P
        if gt < T(12):
            return dict(D.POSE_SIT)
        if gt < T(13):
            dr = E(12, "drawer")
            k1 = ease_in_out(prog(gt, dr - 0.3, 0.4)) * (1 - ease_in_out(prog(gt, dr + 0.6, 0.4)))
            k2 = ease_in_out(prog(gt, dr + 1.1, 0.6))
            P = D.pose_mix(D.POSE_SIT, POSE_TIDY, max(k1 * 0.8, k2))
            if k1 > 0.01:
                P = with_arm(P, (lerp(D.hand_pos(P)[0], 640, k1), lerp(D.hand_pos(P)[1], 640, k1)))
            if k2 > 0.01:
                back = ease_in_out(prog(gt, dr + 1.8, 0.7))
                P = D.pose_mix(P, POSE_HOLD, back)
                tgt = (lerp(CUP_ON_TABLE[0], 470, back), lerp(CUP_ON_TABLE[1] - 4, 600, back))
                P = with_arm(P, (lerp(D.hand_pos(P)[0], tgt[0], k2), lerp(D.hand_pos(P)[1], tgt[1], k2)))
            return P
        P = dict(POSE_HOLD)
        return with_arm(P, (470, 600))

    def cup_held(self, gt: float) -> bool:
        return gt >= self.E(12, "drawer") + 1.1 + 0.6

    # ------------------------------------------------------------ 主绘制

    def frame(self, c: skia.Canvas, f: int):
        L, tl = self.L, self.tl
        i, t, dur = self.locate(f)
        gt = f / FPS
        cam = self.camera(i, t, dur)
        research = self.research_amount(i, t)
        dark = 0.0
        if i == 15:
            dark = 0.72 * ease_in_out(prog(t, 0.0, 0.8))
        D.background(c, L, dark=max(dark, research * 0.6))

        if research < 1:
            c.save()
            D.apply_camera(c, L, cam, 0.55)
            D.blur_layer(c, 7 * L.stage_s)
            D.room_far(c, gt, light=(1 - research) * (1 - dark))
            c.restore()
            c.restore()
            c.save()
            D.apply_camera(c, L, cam)
            if research > 0 or dark > 0:
                c.saveLayerAlpha(None, int(255 * (1 - research) * (1 - dark * 0.6)))
            self.room_near(c, i, t, gt)
            if research > 0 or dark > 0:
                c.restore()
            if i == 5:
                self.paper_roll(c, t)
            c.restore()
        if research > 0 and i in (5, 6, 7, 8):
            c.save()
            D.apply_camera(c, L, (1.0, 500, 500))
            if i in (6, 7, 8):
                self.panels(c, i, t, research)
            c.restore()

        self.text_layer(c, i, t, dur)
        if i == 15:
            k = prog(t, dur - 0.35, 0.33)
            if k > 0:
                c.drawPaint(D.fill(INK, k))

    def research_amount(self, i: int, t: float) -> float:
        if i == 5:
            return 0.85 * ease_in_out(prog(t, self.tl.ev(5, "roll"), 0.7))
        if i in (6, 7):
            return 1.0
        if i == 8:
            return 1 - ease_in_out(prog(t, 0.0, 0.55))
        return 0.0

    # ------------------------------------------------------------ 房间近景

    def room_near(self, c, i: int, t: float, gt: float):
        T, E = self.T, self.E
        D.floor_line(c)
        if gt >= T(13):
            m = ease_in_out(prog(gt, E(13, "settle"), 1.6))
            D.checkbox_frame(c, BOX[0], BOX[1], 1.0, 1.0, morph=m)
            if m < 1:
                self.box_pole(c, 1 - m)
        elif gt >= T(9):
            g = ease_out_back(prog(gt, E(9, "box"), 0.55), 1.2)
            self.box_pole(c, clamp01(g))
            D.checkbox_frame(c, BOX[0], BOX[1], g, 0.85 if gt >= T(10) else 1.0)

        belt_a = 1.0 if gt < T(5) or (T(8) <= gt < T(14)) else 0.0
        if i == 5:
            belt_a = 1.0
        flash = 0.0
        if i == 1:
            flash = math.exp(-max(0, gt - E(1, "reveal")) * 3) * (gt >= E(1, "reveal"))
        if i == 8:
            flash = 0.7 * math.exp(-max(0, gt - E(8, "reveal")) * 2.5) * (gt >= E(8, "reveal"))
        roll = ease_in_out(prog(t, self.tl.ev(5, "roll"), 0.5)) if i == 5 else 0.0
        if belt_a > 0:
            D.belt(c, gt, self.offset[min(int(round(gt * FPS)), len(self.offset) - 1)], belt_a, flash, roll)
        jolt = 0.0
        if i == 1 and gt >= E(1, "reveal"):
            jolt = -5 * math.exp(-(gt - E(1, "reveal")) * 9) * math.sin((gt - E(1, "reveal")) * 40)
        c.save()
        c.translate(jolt, 0)
        D.sofa_back(c)
        if i == 2:
            self.rail(c, t, gt)
        elif i == 3 or (i == 4 and t < 1.0):
            self.rail(c, t + 6, gt, dim=0.45 if i == 3 else 0.45 * (1 - t))
        P = self.pose(gt)
        drawer = 0.0
        if i == 12:
            dr = self.tl.ev(12, "drawer")
            drawer = ease_out(prog(t, dr, 0.4)) * (1 - ease_in_out(prog(t, dr + 0.7, 0.4)))
        if gt >= T(10):
            D.side_table(c, 1.0, drawer)
            self.table_items(c, i, t, gt)
        D.person_back(c, P)
        glow_arm = 0.0
        if i == 1:
            glow_arm = 0.0
        elif i == 2:
            glow_arm = 1 - ease_in_out(prog(t, 0.6, 0.6))
        D.sofa_front(c, top_glow=glow_arm if i == 2 else (ease_in_out(prog(t, 5.3, 0.6)) if i == 1 else 0))
        self.hand_layer(c, i, t, gt, P)
        c.restore()
        if i == 3:
            self.urge_cards(c, t, P)

    def box_pole(self, c, a):
        if a <= 0:
            return
        D.line(c, BOX[0], BOX[1] + 70, BOX[0], D.FLOOR_Y, D.stroke("#4A4034", 5, a))
        D.soft_shadow(c, BOX[0], D.FLOOR_Y, 40, 6, 0.4 * a)

    def rail(self, c, t, gt, dim=1.0):
        """第 2 镜：扶手顶边的金线延展为墙上的轨道，无字任务卡沿轨道快速奔跑。"""
        grow = ease_in_out(prog(t, 0.15, 0.7)) if dim == 1.0 else 1.0
        y = 300
        x0 = lerp(256, -700, grow)
        x1 = lerp(552, 1600, grow)
        yy = lerp(598, y, ease_in_out(prog(t, 0.0, 0.5)) if dim == 1.0 else 1.0)
        D.gold_line(c, [(x0, yy), (x1, yy)], 2.2, 0.9 * dim, glow=0.4)
        try:
            run0 = self.tl.ev(2, "run")
        except KeyError:
            run0 = 0.9
        if t < run0 and dim == 1.0:
            return
        speed = 420
        tt = t - run0
        for k in range(7):
            x = 1500 - ((tt * speed + k * 330) % 2310)
            a = dim * (ease_out(prog(t, run0, 0.3)) if dim == 1.0 else 1.0)
            D.line(c, x + 30, y, x + 30, y + 22, D.stroke("#8C7444", 2, a))
            D.paper_card(c, x, y + 22, 92, 62, a * 0.92, r=6, lift=0.6)
            for r in range(2):
                D.line(c, x + 16, y + 42 + r * 16, x + 74 - r * 18, y + 42 + r * 16, D.stroke("#A79A82", 2.4, a))

    def urge_cards(self, c, t, P):
        """第 3 镜：两张催促卡（书本 / 清单图标，无字）在两个拍点先后贴近人物头部。"""
        head = D.joints(P)["head"]
        for name, icon, start, end in (("card1", D.icon_book, (760, 260), (head[0] + 150, head[1] - 90)),
                                       ("card2", D.icon_checklist, (-200, 300), (head[0] - 150, head[1] - 60))):
            e = self.tl.ev(3, name)
            k = ease_out_back(prog(t, e - 0.25, 0.4), 1.1)
            if k <= 0:
                continue
            x, y = lerp(start[0], end[0], k), lerp(start[1], end[1], k)
            D.paper_card(c, x - 62, y - 50, 124, 100, min(1, k * 1.5), r=10)
            icon(c, x, y, 0.85, min(1, k * 1.5))

    def hand_layer(self, c, i, t, gt, P):
        T, E = self.T, self.E
        item = None
        if gt < T(3) or (i == 3 and t < self.tl.ev(3, "phone") + 0.2):
            face = 1.0
            if i == 3:
                face = math.cos(math.pi * ease_in_out(prog(t, self.tl.ev(3, "phone"), 0.3)))

            def item(c, h, face=face):
                D.icon_phone(c, h[0] + 10, h[1] - 22, 1.0, face, lit=0.9)
        elif T(8) <= gt < T(9):
            e = E(8, "reveal")
            g = math.exp(-max(0, gt - e) * 1.6) * (gt >= e) + 0.25 * (gt >= e)

            def item(c, h, g=g):
                D.icon_eval_card(c, h[0] + 6, h[1] - 30, 1.0, 1.0, glow=g, rot=-8)
                self.drive_line(c, (h[0] + 6, h[1] - 6), g, gt)
        elif i == 13 and self.cup_held(gt) or i in (14, 15) or (i == 12 and self.cup_held(gt)):
            def item(c, h):
                D.icon_cup(c, h[0] + 8, h[1] - 14, 1.0)
                if i in (14, 15):
                    D.steam(c, h[0] + 8, h[1] - 34, gt, 1.0 - 0.5 * (i == 15))
        D.person_front(c, P, hand_item=item)
        # 手机反扣后放在扶手顶
        if T(3) <= gt < T(8) and not (i == 3 and t < self.tl.ev(3, "phone") + 0.2):
            D.rrect(c, 486, 582, 64, 14, 5, D.fill("#000000", 0.5, blur=4))
            D.rrect(c, 486, 580, 64, 13, 5, D.fill("#3A3C42"))
            D.rrect(c, 486, 580, 64, 13, 5, D.stroke(GOLD, 1.4, 0.8))
        # 第 9—12 镜：评价卡放在膝上，驱动线仍连着传送带
        if T(9) <= gt < T(13):
            pos = CARD_LAP
            a = 1.0
            if i == 12:
                dr = self.tl.ev(12, "drawer")
                k = ease_in_out(prog(t, dr, 0.6))
                pos = (lerp(CARD_LAP[0], 690, k), lerp(CARD_LAP[1], 650, k))
                a = 1 - prog(t, dr + 0.45, 0.2)
            if a > 0:
                D.icon_eval_card(c, pos[0], pos[1], 0.8, a, glow=0.2, rot=-4)
                self.drive_line(c, (pos[0], pos[1] + 18), 0.3 * a, gt)

    def drive_line(self, c, p, g, gt):
        """评价卡 → 传送带前滚轮的金色驱动线（视觉比喻）；发光脉冲沿线流动。"""
        q = (720, D.FLOOR_Y + 13)
        path = skia.Path()
        path.moveTo(*p)
        path.cubicTo(p[0] + 120, p[1] + 60, q[0] + 40, q[1] - 160, *q)
        a = clamp01(0.35 + g)
        c.drawPath(path, D.stroke(GOLD, 8, 0.35 * a, blur=6))
        c.drawPath(path, D.stroke(GOLD, 2.2, 0.9 * a))
        meas = skia.PathMeasure(path, False)
        Ln = meas.getLength()
        for k in range(3):
            d = ((gt * 160 + k * Ln / 3) % Ln)
            pos, _ = meas.getPosTan(d)
            c.drawCircle(pos.x(), pos.y(), 5, D.fill("#FFF2D0", 0.9 * a))

    def table_items(self, c, i, t, gt):
        T, E = self.T, self.E
        dim = 1.0
        if gt >= T(11):
            dim = 0.6
        if gt < T(11):
            it = E(10, "items")
            k = ease_out_back(prog(gt, it - 0.18, 0.3), 1.0)
            tidy = ease_in_out(prog(gt, E(10, "tidy"), 1.4))
            if k > 0:
                bx = lerp(lerp(676, STACK_ON_TABLE[0], tidy), STACK_ON_TABLE[0], 0)
                D.icon_bill(c, lerp(676, STACK_ON_TABLE[0], tidy), lerp(TABLE_TOP - 150, TABLE_TOP - 34, k) - 4 * tidy,
                            0.9, 1.0, rot=lerp(-14, 0, tidy))
                D.icon_notice(c, lerp(720, STACK_ON_TABLE[0], tidy), lerp(TABLE_TOP - 190, TABLE_TOP - 18, k) - 20 * tidy,
                              0.9, 1.0, rot=lerp(12, 0, tidy))
            return
        D.icon_bill(c, STACK_ON_TABLE[0], TABLE_TOP - 38, 0.9, dim)
        D.icon_notice(c, STACK_ON_TABLE[0], TABLE_TOP - 38, 0.9, dim)
        chosen = 0.0
        if gt >= T(12):
            chosen = ease_out(prog(gt, E(12, "choose"), 0.5))
        objs = (("obj1", "shoe"), ("obj2", "cup"), ("obj3", "photo"))
        for name, kind in objs:
            e = E(11, name)
            k = ease_out_back(prog(gt, e - 0.15, 0.35), 1.6)
            if k <= 0:
                continue
            a = min(1, k) * (1 - 0.45 * chosen if kind != "cup" else 1)
            if kind == "shoe":
                D.icon_shoe(c, 790, D.FLOOR_Y - 14, k, a)
            elif kind == "cup":
                if self.cup_held(gt):
                    continue
                D.icon_cup(c, CUP_ON_TABLE[0], CUP_ON_TABLE[1] - 12, k, a, glow=chosen)
            else:
                D.icon_photo(c, PHOTO_ON_TABLE[0], PHOTO_ON_TABLE[1] - 14, k, a)

    # ------------------------------------------------------------ 研究段

    def paper_roll(self, c, t):
        """第 5 镜：传送带卷起成论文页，随后出现 阅读材料 → 看视频 → 填写反馈 三个无字图标。"""
        r = self.tl.ev(5, "roll")
        k = ease_in_out(prog(t, r, 0.8))
        if k <= 0:
            return
        x0, y0, w0, h0 = 94, 846, 652, 34
        x1, y1, w1, h1 = 380, 300, 240, 300
        x, y = lerp(x0, x1, k), lerp(y0, y1, k)
        w, h = lerp(w0, w1, k), lerp(h0, h1, k)
        c.save()
        c.translate(x + w / 2, y + h / 2)
        c.rotate(lerp(0, -3, k) + 8 * math.sin(math.pi * k))
        D.paper_card(c, -w / 2, -h / 2, w, h, 1.0, dark=k < 0.5, r=lerp(17, 8, k), lift=lerp(0.3, 1.0, k))
        if k > 0.6:
            a = (k - 0.6) / 0.4
            for n in range(7):
                ly = -h / 2 + 50 + n * 32
                D.line(c, -w / 2 + 30, ly, w / 2 - 30 - (n % 3 == 2) * 50, ly, D.stroke("#9A8C72", 3, a))
            D.rrect(c, -w / 2 + 30, -h / 2 + 18, 70, 12, 4, D.fill(GOLD, a))
        c.restore()
        xs = (250, 500, 750)
        y = 740
        icons = (D.icon_document, D.icon_play, D.icon_form)
        for n, (xx, fn) in enumerate(zip(xs, icons)):
            e = self.tl.ev(5, f"icon{n + 1}")
            g = ease_out_back(prog(t, e - 0.12, 0.35), 1.4)
            if g <= 0:
                continue
            if n > 0:
                lk = ease_out(prog(t, e - 0.3, 0.3))
                D.gold_line(c, [(xs[n - 1] + 62, y), (lerp(xs[n - 1] + 62, xx - 62, lk), y)], 2.2, 1.0)
                if lk >= 1:
                    tri = D._path([(xx - 70, y - 8), (xx - 60, y), (xx - 70, y + 8)])
                    c.drawPath(tri, D.stroke(GOLD, 2.2))
            c.drawCircle(xx, y, 70, D.fill(GOLD, 0.12 * min(g, 1), blur=20))
            fn(c, xx, y, 1.15 * g, min(1, g))

    def panels(self, c, i, t, research):
        """第 6、7 镜：两组「不同封面材料 + 同一段猫咪短片」；横屏左右对照，竖屏上下递进。"""
        L = self.L
        a = research
        if i == 8:
            a = 1 - ease_in_out(prog(t, 0.0, 0.45))
            if a <= 0:
                return
        if a < 1:
            c.saveLayerAlpha(None, int(255 * a))
        tl6 = self.T(6)
        gt6 = self.T(i) + t - tl6
        cov = ease_out_back(prog(gt6, self.tl.ev(6, "covers") - 0.2, 0.4), 1.2) if i == 6 else 1.0
        play_t = self.tl.ev(6, "play")
        playing = gt6 >= play_t
        clip_t = max(0.0, gt6 - play_t)
        cover_k = 0.0
        if i >= 7:
            cover_k = ease_out_back(prog(gt6 - (self.T(7) - tl6), self.tl.ev(7, "cover") - 0.18, 0.36), 1.0)
        if i == 8:
            cover_k = 1.0
        for side in (0, 1):
            if L.horizontal:
                px, py, pw, ph = (20 + side * 500, 170, 460, 640)
                cv = (px + pw / 2, py + 110)
                sc = (px + 30, py + 260, pw - 60, 320)
            else:
                px, py, pw, ph = (20, 40 + side * 480, 960, 440)
                cv = (px + 150, py + ph / 2)
                sc = (px + 300, py + 50, pw - 340, ph - 100)
            D.rrect(c, px, py, pw, ph, 18, D.fill("#111316"))
            D.rrect(c, px, py, pw, ph, 18, D.stroke(GOLD, 1.4, 0.4))
            if cov > 0:
                c.save()
                c.translate(*cv)
                c.scale(max(0.05, min(cov, 1.2)), min(cov, 1.2))
                if side == 0:
                    D.paper_card(c, -60, -78, 120, 156, 1.0, r=8)
                    for n in range(3):
                        wave = skia.Path()
                        wave.moveTo(-40, -30 + n * 30)
                        wave.quadTo(-20, -44 + n * 30, 0, -30 + n * 30)
                        wave.quadTo(20, -16 + n * 30, 40, -30 + n * 30)
                        c.drawPath(wave, D.stroke("#8E8066", 3))
                else:
                    D.hourglass_card(c, 0, 0, 1.3, 1.0)
                c.restore()
            x, y, w, h = sc
            D.rrect(c, x - 6, y - 6, w + 12, h + 12, 12, D.fill("#050506"))
            D.rrect(c, x - 6, y - 6, w + 12, h + 12, 12, D.stroke(GOLD, 1.6, 0.7))
            if playing or i >= 7:
                D.cat_clip(c, x, y, w, h, clip_t, 1.0)
            else:
                D.rrect(c, x, y, w, h, 6, D.fill("#14171B"))
                D.icon_play(c, x + w / 2, y + h / 2, 1.0, 0.8)
            if side == 1 and cover_k > 0:
                ox, oy = cv
                tx, ty = x + w * 0.22, y + h * 0.62
                c.save()
                c.translate(lerp(ox, tx, min(cover_k, 1.05)), lerp(oy, ty, min(cover_k, 1.05)))
                c.rotate(lerp(0, -6, min(cover_k, 1)))
                D.rrect(c, -90, -70, 180, 140, 10, D.fill("#000000", 0.5, blur=14))
                D.hourglass_card(c, 0, 0, 1.25, 1.0)
                c.restore()
                c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), D.fill(INK, 0.32 * min(cover_k, 1)))
        if a < 1:
            c.restore()

    # ------------------------------------------------------------ 文字层

    def text_alpha(self, i: int, t: float, dur: float) -> tuple:
        if i == 1:
            a, rise = 1.0, 0.0
        else:
            k = ease_out(prog(t, 0.02, ENTER - 0.06))
            a, rise = k, 28 * (1 - k)
        a *= 1 - ease_in_out(prog(t, dur - EXIT + 0.03, EXIT - 0.08))
        return a, rise

    def beat_node(self, f: int) -> float:
        best = 0.0
        for b in self.tl.beats:
            if b <= f < b + 12:
                best = max(best, math.exp(-(f - b) / FPS / 0.12))
        return best

    def text_layer(self, c, i, t, dur):
        shot = story.SHOTS[i - 1]
        a, rise = self.text_alpha(i, t, dur)
        f = self.tl.bounds[i - 1] + int(round(t * FPS))
        D.main_card(c, self.L, shot.text, shot.hi, a, rise, self.beat_node(f), shot.source)
        ta = 1.0 if i == 1 else ease_out(prog(t, 0.0, 0.25))
        ta *= 1 - prog(t, dur - 0.2, 0.18)
        D.tag(c, self.L, shot.tag, ta)
