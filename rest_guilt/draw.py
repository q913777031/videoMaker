"""绘制基元：舞台坐标、2.5D 景深层、原创人物骨架、沙发 / 传送带 / 边桌、无字图标、主卡与角标排版。

舞台坐标为 1000×1000 单位（背景元素可超出），由 Layout 映射到竖屏或横屏画面。
所有函数都是参数的纯函数，保证逐帧并行渲染结果确定。
"""

import math
from dataclasses import dataclass

import skia

from engine import gfx
from engine.gfx import clamp01, ease_in_out, ease_out, lerp

from .story import GOLD, INK, WHITE

CLOTH = "#252A31"
CLOTH_FAR = "#1A1D22"
SKIN = "#C4A285"
SKIN_FAR = "#A2846C"
HAIR = "#1D1916"
PAPER = "#E9E1D2"
PAPER_DARK = "#1A1C20"
SOFA = "#3A3530"
SOFA_DARK = "#2B2723"
SOFA_LIGHT = "#4A433C"
WOOD = "#3B3027"
FLOOR_Y = 850


# ---------------------------------------------------------------- 版式

@dataclass(frozen=True)
class Layout:
    name: str
    W: int
    H: int
    stage_x: float
    stage_y: float
    stage_s: float
    text_cx: float
    text_y: float
    text_maxw: float
    text_size: float
    text_min: float
    line_gap: float
    tag_x: float
    tag_y: float
    tag_size: float
    body_size: float
    body_min: float
    safe: tuple  # 关键内容安全区 (x0, y0, x1, y1)
    horizontal: bool


VERTICAL = Layout("vertical", 1080, 1920, -40, 560, 1.2, 505, 470, 830, 92, 78, 118,
                  90, 196, 36, 62, 54, (90, 180, 920, 1580), False)
HORIZONTAL = Layout("horizontal", 1920, 1080, 40, 50, 1.0, 1470, 470, 740, 84, 72, 110,
                    80, 80, 30, 52, 44, (80, 80, 1840, 1000), True)


def stage_to_screen(L: Layout, cam: tuple, x: float, y: float) -> tuple:
    s, fx, fy = cam
    return (L.stage_x + L.stage_s * (500 + s * (x - fx)), L.stage_y + L.stage_s * (500 + s * (y - fy)))


def apply_camera(c: skia.Canvas, L: Layout, cam: tuple, parallax: float = 1.0):
    """把画布变换到舞台坐标；parallax < 1 的远景层缩放与位移都更小，形成 2.5D 视差。"""
    s, fx, fy = cam
    s = 1 + (s - 1) * parallax
    fx = 500 + (fx - 500) * parallax
    fy = 500 + (fy - 500) * parallax
    c.translate(L.stage_x, L.stage_y)
    c.scale(L.stage_s, L.stage_s)
    c.translate(500, 500)
    c.scale(s, s)
    c.translate(-fx, -fy)


# ---------------------------------------------------------------- 画笔

def fill(color, a=1.0, blur=0.0) -> skia.Paint:
    p = skia.Paint(AntiAlias=True, Color=gfx.col(color, a))
    if blur > 0:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


def stroke(color, w, a=1.0, cap=skia.Paint.kRound_Cap, blur=0.0) -> skia.Paint:
    p = skia.Paint(AntiAlias=True, Color=gfx.col(color, a), Style=skia.Paint.kStroke_Style,
                   StrokeWidth=w, StrokeCap=cap, StrokeJoin=skia.Paint.kRound_Join)
    if blur > 0:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


def rrect(c, x, y, w, h, r, paint):
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r), paint)


def line(c, x0, y0, x1, y1, paint):
    c.drawLine(x0, y0, x1, y1, paint)


def soft_shadow(c, cx, cy, rx, ry, a=0.5):
    c.drawOval(skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry), fill("#000000", a, blur=ry * 0.8 + 4))


def gold_line(c, pts, w=2.4, a=1.0, glow=0.0):
    """金属细线：暗金底线 + 亮香槟金高光，可选柔光。"""
    path = skia.Path()
    path.moveTo(*pts[0])
    for p in pts[1:]:
        path.lineTo(*p)
    if glow > 0:
        c.drawPath(path, stroke(GOLD, w * 4, a * glow * 0.5, blur=w * 3))
    c.drawPath(path, stroke("#8C7444", w * 1.6, a))
    c.drawPath(path, stroke(GOLD, w, a))


def paper_card(c, x, y, w, h, a=1.0, dark=False, r=10, lift=1.0):
    """纸卡：投影 + 纸面 + 顶部微高光。dark=True 为深色卡纸。"""
    if a <= 0:
        return
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x + 6 * lift, y + 14 * lift, w, h), r, r),
                fill("#000000", 0.55 * a, blur=12 * lift + 2))
    base = PAPER_DARK if dark else PAPER
    p = fill(base, a)
    top = gfx.mix(base, "#FFFFFF", 0.08)
    p.setShader(skia.GradientShader.MakeLinear([(x, y), (x, y + h)], [gfx.col(top, a), gfx.col(base, a)]))
    rrect(c, x, y, w, h, r, p)
    rrect(c, x + 0.5, y + 0.5, w - 1, h - 1, r, stroke(GOLD if dark else "#BFAF92", 1.4, a * (0.6 if dark else 0.5)))


def blur_layer(c, sigma):
    """开启景深模糊图层，需与 c.restore() 配对。"""
    p = skia.Paint()
    p.setImageFilter(skia.ImageFilters.Blur(sigma, sigma))
    c.saveLayer(None, p)


# ---------------------------------------------------------------- 房间与家具

def background(c, L: Layout, warm: float = 1.0, dark: float = 0.0):
    """全画面背景：近黑底 + 偏暖的地面反光 + 暗角。dark 让整体再压暗（研究段与结尾）。"""
    c.drawPaint(fill(INK))
    cx, cy = L.W * (0.32 if L.horizontal else 0.5), L.H * (0.62 if L.horizontal else 0.66)
    r = max(L.W, L.H) * 0.75
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeRadial((cx, cy), r, [gfx.col("#1B1813", 0.9 * warm * (1 - dark)),
                                                            gfx.col(INK, 0)]))
    c.drawPaint(p)


def room_far(c, t, light=1.0):
    """远景墙面元素（窗、层架、落地灯光晕），由调用方套景深模糊。"""
    # 墙面与地面分界
    c.drawRect(skia.Rect.MakeLTRB(-1500, FLOOR_Y, 2500, 2400), fill("#0D0E10", 1))
    # 窗
    rrect(c, -230, 170, 300, 380, 6, fill("#12161B", light))
    for k in range(2):
        rrect(c, -214 + k * 148, 186, 136, 348, 3, fill("#171C23", light))
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeLinear([(-230, 170), (70, 550)],
                                               [gfx.col("#2A3340", 0.55 * light), gfx.col("#12161B", 0)]))
    rrect(c, -230, 170, 300, 380, 6, p)
    # 层架
    rrect(c, 760, 330, 330, 10, 3, fill(WOOD, 0.9 * light))
    for i, (bx, bh, colr) in enumerate([(780, 70, "#2C2A28"), (806, 84, "#3A3229"), (836, 62, "#2A2F35"),
                                        (930, 46, "#33302B")]):
        rrect(c, bx, 330 - bh, 22 if i < 3 else 60, bh, 2, fill(colr, light))
    # 落地灯
    line(c, 1180, 300, 1180, FLOOR_Y, stroke("#3A332B", 6, light))
    g = skia.Paint(AntiAlias=True)
    g.setShader(skia.GradientShader.MakeRadial((1180, 300), 420, [gfx.col("#E8C98A", 0.22 * light),
                                                                  gfx.col("#E8C98A", 0)]))
    c.drawCircle(1180, 300, 420, g)
    rrect(c, 1120, 250, 120, 70, 30, fill("#5A4C38", light))


def floor_line(c, a=1.0):
    gold_line(c, [(-1500, FLOOR_Y + 2), (2500, FLOOR_Y + 2)], 1.6, 0.35 * a)


def sofa_back(c, a=1.0):
    """沙发靠背与坐垫（人物身后的部分）。"""
    if a <= 0:
        return
    soft_shadow(c, 420, FLOOR_Y, 300, 16, 0.6 * a)
    path = skia.Path()
    path.moveTo(205, 770)
    path.lineTo(176, 470)
    path.quadTo(176, 440, 210, 438)
    path.lineTo(250, 438)
    path.quadTo(282, 440, 286, 470)
    path.lineTo(300, 770)
    path.close()
    c.drawPath(path, fill(SOFA_DARK, a))
    rrect(c, 250, 690, 360, 52, 18, fill(SOFA, a))
    rrect(c, 254, 692, 352, 10, 6, fill(SOFA_LIGHT, 0.6 * a))
    rrect(c, 220, 735, 410, 80, 10, fill(SOFA_DARK, a))


def sofa_front(c, a=1.0, top_glow=0.0):
    """近侧扶手面板（遮住人物髋部）。top_glow 让扶手顶边以金线亮起，用于转场匹配。"""
    if a <= 0:
        return
    path = skia.Path()
    path.moveTo(214, 815)
    path.lineTo(214, 640)
    path.quadTo(214, 598, 256, 598)
    path.lineTo(552, 598)
    path.quadTo(600, 598, 600, 640)
    path.quadTo(600, 676, 566, 680)
    path.lineTo(566, 815)
    path.close()
    p = fill(SOFA, a)
    p.setShader(skia.GradientShader.MakeLinear([(0, 598), (0, 815)], [gfx.col(SOFA_LIGHT, a), gfx.col(SOFA_DARK, a)]))
    c.drawPath(path, p)
    line(c, 236, 612, 580, 612, stroke("#5A5148", 2, 0.6 * a))
    for lx in (236, 544):
        rrect(c, lx, 815, 14, 34, 3, fill("#1A1714", a))
    if top_glow > 0:
        gold_line(c, [(214, 640), (220, 606), (256, 598), (552, 598), (592, 610), (600, 640)], 2.4, top_glow, 0.8)


ARMREST_TOP = ((256, 598), (552, 598))


def belt(c, t, offset, a=1.0, flash=0.0, roll=0.0, x0=120, x1=720):
    """家具下的跑步机传送带。offset 为带面累计位移（单位），flash 为金色闪光强度，roll 0—1 为卷起进度。"""
    if a <= 0:
        return
    y = FLOOR_Y
    c.save()
    if roll > 0:
        c.saveLayerAlpha(None, int(255 * (1 - roll)))
    rrect(c, x0 - 26, y - 4, x1 - x0 + 52, 34, 17, fill("#15171A", a))
    rrect(c, x0 - 26, y - 4, x1 - x0 + 52, 34, 17, stroke(GOLD, 1.6, 0.55 * a))
    for rx in (x0, x1):
        c.drawCircle(rx, y + 13, 14, fill("#23262B", a))
        c.drawCircle(rx, y + 13, 14, stroke(GOLD, 1.4, 0.7 * a))
        ang = -offset / 14
        line(c, rx, y + 13, rx + 10 * math.cos(ang), y + 13 + 10 * math.sin(ang), stroke(GOLD, 1.6, 0.8 * a))
    gap = 34
    c.clipRect(skia.Rect.MakeLTRB(x0 - 10, y - 6, x1 + 10, y + 4))
    k0 = math.floor((x0 - 40 + offset) / gap)
    for k in range(k0, k0 + int((x1 - x0 + 80) / gap) + 2):
        x = k * gap - offset
        line(c, x, y - 3, x - 8, y + 3, stroke(gfx.mix("#6E6250", GOLD, flash), 2.2, a * (0.7 + 0.3 * flash)))
    c.restore()
    if roll > 0:
        c.restore()
    if flash > 0:
        line(c, x0 - 20, y - 4, x1 + 20, y - 4, stroke(GOLD, 6, 0.5 * flash * a, blur=6))


def side_table(c, a=1.0, drawer=0.0):
    """边桌（有抽屉），紧挨扶手前缘。drawer 0—1 为抽屉拉出程度。桌面 y=606，范围 x 600—770。"""
    if a <= 0:
        return
    soft_shadow(c, 685, FLOOR_Y, 110, 10, 0.5 * a)
    rrect(c, 600, 598, 170, 16, 4, fill("#4A3D31", a))
    rrect(c, 610, 614, 150, 74, 3, fill(WOOD, a))
    for lx in (614, 744):
        rrect(c, lx, 688, 12, FLOOR_Y - 688, 2, fill("#2C241D", a))
    dx = 64 * drawer
    if drawer > 0:
        rrect(c, 618, 624, 134, 52, 2, fill("#120E0B", a))
    rrect(c, 618 + dx, 624, 134, 52, 3, fill("#4A3D31", a))
    rrect(c, 618 + dx, 624, 134, 52, 3, stroke("#5E4F40", 1.4, a))
    rrect(c, 672 + dx, 646, 26, 6, 3, fill(GOLD, 0.8 * a))


# ---------------------------------------------------------------- 人物

POSE_SIT = dict(hip=(330, 690), lean=10, neck=2, sh_n=18, el_n=72, sh_f=8, el_f=60, th_n=88, kn_n=6, th_f=86, kn_f=10)
POSE_RECLINE = dict(hip=(320, 698), lean=42, neck=-14, sh_n=40, el_n=105, sh_f=30, el_f=95, th_n=78, kn_n=28, th_f=74,
                    kn_f=34)
TORSO, NECK, HEAD = 196, 26, 44
UPPER, FORE, THIGH, SHIN = 104, 92, 272, 150


def pose_mix(a: dict, b: dict, x: float) -> dict:
    x = clamp01(x)
    out = {}
    for k in a:
        if isinstance(a[k], tuple):
            out[k] = (lerp(a[k][0], b[k][0], x), lerp(a[k][1], b[k][1], x))
        else:
            out[k] = lerp(a[k], b[k], x)
    return out


def _limb(p, ang, length):
    r = math.radians(ang)
    return (p[0] + length * math.sin(r), p[1] + length * math.cos(r))


def joints(P: dict) -> dict:
    hip = P["hip"]
    lr = math.radians(P["lean"])
    up = (-math.sin(lr), -math.cos(lr))
    sh = (hip[0] + up[0] * TORSO, hip[1] + up[1] * TORSO)
    hr = math.radians(P["lean"] + P["neck"])
    hu = (-math.sin(hr), -math.cos(hr))
    head = (sh[0] + hu[0] * (NECK + HEAD), sh[1] + hu[1] * (NECK + HEAD))
    j = {"hip": hip, "sh": sh, "head": head, "up": up, "hu": hu}
    ls = P.get("leg_scale", 1.0)
    for side in ("n", "f"):
        el = _limb(sh, P["sh_" + side], UPPER)
        j["el_" + side] = el
        j["ha_" + side] = _limb(el, P["el_" + side], FORE)
        kn = _limb(hip, P["th_" + side], THIGH * ls)
        j["kn_" + side] = kn
        j["ft_" + side] = _limb(kn, P["kn_" + side], SHIN * ls)
    return j


def _path(pts):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    return p


def person_back(c, P: dict, a=1.0):
    """人物身后部分：远侧臂、远侧腿、躯干、头、近侧腿（扶手面板会盖在髋部之上）。"""
    if a <= 0:
        return
    j = joints(P)
    if a < 1:
        c.saveLayerAlpha(None, int(255 * a))
    c.drawPath(_path([j["sh"], j["el_f"], j["ha_f"]]), stroke(CLOTH_FAR, 28))
    c.drawCircle(*j["ha_f"], 12, fill(SKIN_FAR))
    c.drawPath(_path([j["hip"], j["kn_f"], j["ft_f"]]), stroke(CLOTH_FAR, 38))
    _foot(c, j["ft_f"], "#121315")
    # 躯干
    hip, sh = j["hip"], j["sh"]
    c.drawPath(_path([hip, sh]), stroke(CLOTH, 84))
    # 金色识别线：外套前襟（躯干正面一侧的细线）
    nx, ny = -j["up"][1], j["up"][0]
    off = -36
    a0 = (hip[0] + j["up"][0] * 20 - nx * off, hip[1] + j["up"][1] * 20 - ny * off)
    a1 = (sh[0] - j["up"][0] * 18 - nx * off, sh[1] - j["up"][1] * 18 - ny * off)
    if nx * off < 0:
        a0 = (hip[0] + j["up"][0] * 20 + nx * off, hip[1] + j["up"][1] * 20 + ny * off)
        a1 = (sh[0] - j["up"][0] * 18 + nx * off, sh[1] - j["up"][1] * 18 + ny * off)
    c.drawPath(_path([a0, a1]), stroke(GOLD, 3.2))
    # 颈与头
    neck = (sh[0] + j["hu"][0] * NECK * 0.6, sh[1] + j["hu"][1] * NECK * 0.6)
    c.drawPath(_path([sh, neck]), stroke(SKIN_FAR, 30))
    hx, hy = j["head"]
    up = j["hu"]
    fwd = (-up[1], up[0])
    if fwd[0] < 0:
        fwd = (-fwd[0], -fwd[1])
    # 头发为整圆，脸部为偏前下方的肤色圆并裁切在头部轮廓内：短发覆盖头顶与后脑
    c.drawCircle(hx, hy, HEAD + 3, fill(HAIR))
    c.save()
    clip = skia.Path()
    clip.addCircle(hx, hy, HEAD)
    c.clipPath(clip, doAntiAlias=True)
    c.drawCircle(hx + fwd[0] * 14 - up[0] * 12, hy + fwd[1] * 14 - up[1] * 12, HEAD - 2, fill(SKIN))
    c.restore()
    ex, ey = hx + fwd[0] * 26 - up[0] * 2, hy + fwd[1] * 26 - up[1] * 2
    if P.get("eyes_closed", 0) > 0.5:
        lid = skia.Path()
        lid.moveTo(ex - 6 * up[0], ey - 6 * up[1])
        lid.quadTo(ex + 4 * fwd[0], ey + 4 * fwd[1], ex + 6 * up[0], ey + 6 * up[1])
        c.drawPath(lid, stroke("#2A211B", 2.6))
    else:
        line(c, ex - 5 * fwd[0], ey - 5 * fwd[1], ex + 5 * fwd[0], ey + 5 * fwd[1], stroke("#2A211B", 3))
    nose = (hx + fwd[0] * (HEAD + 2) - up[0] * 10, hy + fwd[1] * (HEAD + 2) - up[1] * 10)
    c.drawCircle(*nose, 6, fill(SKIN))
    c.drawCircle(hx - fwd[0] * 6 - up[0] * 6, hy - fwd[1] * 6 - up[1] * 6, 7, fill(SKIN_FAR))
    # 近侧腿
    c.drawPath(_path([j["hip"], j["kn_n"], j["ft_n"]]), stroke(CLOTH, 40))
    _foot(c, j["ft_n"], "#16171A")
    if a < 1:
        c.restore()


def person_front(c, P: dict, a=1.0, hand_item=None):
    """近侧手臂（搭在扶手之上）。hand_item(c, hand_xy) 在手部绘制手持物，手指盖在物体之上。"""
    if a <= 0:
        return
    j = joints(P)
    if a < 1:
        c.saveLayerAlpha(None, int(255 * a))
    c.drawPath(_path([j["sh"], j["el_n"], j["ha_n"]]), stroke(CLOTH, 32))
    if hand_item:
        hand_item(c, j["ha_n"])
    c.drawCircle(*j["ha_n"], 13, fill(SKIN))
    if a < 1:
        c.restore()


def _foot(c, ft, colr):
    rrect(c, ft[0] - 16, ft[1] - 4, 50, 22, 10, fill(colr))


def hand_pos(P: dict) -> tuple:
    return joints(P)["ha_n"]


# ---------------------------------------------------------------- 无字图标

def icon_phone(c, x, y, s=1.0, face=1.0, a=1.0, lit=0.0):
    """手机。face 1 为屏幕朝外，-1 为背面（反扣），中间值为翻转过程（水平压缩）。"""
    c.save()
    c.translate(x, y)
    c.scale(max(abs(face), 0.04) * s, s)
    w, h = 34, 62
    rrect(c, -w / 2, -h / 2, w, h, 7, fill("#0F1012", a))
    if face > 0:
        rrect(c, -w / 2 + 3, -h / 2 + 4, w - 6, h - 8, 5, fill(gfx.mix("#14171C", "#3E4A5A", lit), a))
    else:
        rrect(c, -w / 2 + 2, -h / 2 + 2, w - 4, h - 4, 6, fill("#2A2C30", a))
        c.drawCircle(-6, -h / 2 + 11, 4, stroke(GOLD, 1.4, 0.7 * a))
    c.restore()


def icon_book(c, x, y, s=1.0, a=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    rrect(c, -40, -28, 38, 56, 4, fill("#C9BCA4", a))
    rrect(c, 2, -28, 38, 56, 4, fill("#D8CCB4", a))
    line(c, 0, -28, 0, 28, stroke("#8E8066", 2, a))
    for k in range(3):
        line(c, -32, -14 + k * 12, -10, -14 + k * 12, stroke("#9A8C72", 2, a))
        line(c, 10, -14 + k * 12, 32, -14 + k * 12, stroke("#9A8C72", 2, a))
    c.restore()


def icon_checklist(c, x, y, s=1.0, a=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    rrect(c, -30, -38, 60, 76, 5, fill("#D8CCB4", a))
    for k in range(3):
        yy = -20 + k * 20
        rrect(c, -20, yy - 6, 12, 12, 2, stroke("#8E8066", 2, a))
        line(c, -2, yy, 20, yy, stroke("#9A8C72", 2.4, a))
    c.restore()


def icon_document(c, x, y, s=1.0, a=1.0, dark=False):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    paper_card(c, -34, -44, 68, 88, a, dark=dark, r=6, lift=0.5)
    for k in range(4):
        line(c, -20, -24 + k * 14, 20 - (k == 3) * 14, -24 + k * 14, stroke("#9A8C72" if not dark else GOLD, 2.4, a * 0.8))
    c.restore()


def icon_play(c, x, y, s=1.0, a=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    rrect(c, -46, -32, 92, 64, 8, fill("#15181C", a))
    rrect(c, -46, -32, 92, 64, 8, stroke(GOLD, 2, 0.8 * a))
    tri = _path([(-10, -14), (16, 0), (-10, 14)])
    tri.close()
    c.drawPath(tri, fill(WHITE, 0.9 * a))
    c.restore()


def icon_form(c, x, y, s=1.0, a=1.0):
    """填写反馈：空白表单 + 铅笔（无文字、无刻度）。"""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    paper_card(c, -32, -42, 64, 84, a, r=6, lift=0.5)
    for k in range(3):
        yy = -22 + k * 20
        c.drawCircle(-16, yy, 5, stroke("#8E8066", 2, a))
        line(c, -6, yy, 18, yy, stroke("#9A8C72", 2.2, a))
    c.save()
    c.translate(22, 20)
    c.rotate(-40)
    rrect(c, -5, -30, 10, 46, 2, fill(GOLD, a))
    tri = _path([(-5, 16), (5, 16), (0, 26)])
    tri.close()
    c.drawPath(tri, fill("#6B5A3A", a))
    c.restore()
    c.restore()


def icon_eval_card(c, x, y, s=1.0, a=1.0, glow=0.0, rot=0.0):
    """评价卡：对勾 + 无刻度弧形表盘（不画数值）。"""
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    if glow > 0:
        rrect(c, -44, -32, 88, 64, 10, fill(GOLD, 0.45 * glow * a, blur=14))
    paper_card(c, -40, -28, 80, 56, a, dark=True, r=8, lift=0.4)
    arc = skia.Path()
    arc.addArc(skia.Rect.MakeLTRB(-26, -14, 6, 18), 180, 180)
    c.drawPath(arc, stroke(GOLD, 2.6, a))
    line(c, -10, 2, -2 + 6 * glow, -8, stroke(GOLD, 2.6, a))
    ck = _path([(12, 0), (19, 8), (31, -8)])
    c.drawPath(ck, stroke(WHITE, 3.2, a))
    c.restore()


def icon_bill(c, x, y, s=1.0, a=1.0, rot=0.0):
    """账单：锯齿底边的票据，只有横线不写字。"""
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    p = skia.Path()
    p.moveTo(-24, -34)
    p.lineTo(24, -34)
    p.lineTo(24, 30)
    for k in range(6):
        p.lineTo(24 - 4 - 8 * k, 36 if k % 2 == 0 else 30)
    p.lineTo(-24, 30)
    p.close()
    c.drawPath(p, fill("#000000", 0.45 * a, blur=6))
    c.drawPath(p, fill("#DDD3C2", a))
    for k in range(4):
        line(c, -14, -20 + k * 12, 14 - (k == 3) * 12, -20 + k * 12, stroke("#948770", 2.2, a))
    c.restore()


def icon_notice(c, x, y, s=1.0, a=1.0, rot=0.0):
    """工作通知：信封 + 小圆点提示（无文字）。"""
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    rrect(c, -30, -20, 60, 40, 4, fill("#000000", 0.45 * a, blur=6))
    rrect(c, -30, -20, 60, 40, 4, fill("#CFC4B1", a))
    c.drawPath(_path([(-30, -20), (0, 4), (30, -20)]), stroke("#8E8066", 2.2, a))
    c.drawCircle(26, -20, 7, fill(GOLD, a))
    c.restore()


def icon_shoe(c, x, y, s=1.0, a=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    p = skia.Path()
    p.moveTo(-34, 10)
    p.lineTo(-30, -14)
    p.quadTo(-20, -18, -10, -12)
    p.quadTo(6, 0, 30, 2)
    p.quadTo(40, 4, 38, 12)
    p.lineTo(-34, 12)
    p.close()
    soft_shadow(c, 0, 13, 36, 4, 0.5 * a)
    c.drawPath(p, fill("#BDB2A0", a))
    line(c, -34, 10, 38, 10, stroke("#6B6152", 3, a))
    line(c, -14, -8, -4, -2, stroke(GOLD, 2, a))
    c.restore()


def icon_cup(c, x, y, s=1.0, a=1.0, glow=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    if glow > 0:
        c.drawCircle(0, -6, 40, fill(GOLD, 0.25 * glow * a, blur=18))
    p = skia.Path()
    p.moveTo(-18, -22)
    p.lineTo(18, -22)
    p.lineTo(14, 8)
    p.quadTo(0, 14, -14, 8)
    p.close()
    c.drawPath(p, fill("#E4DACA", a))
    arc = skia.Path()
    arc.addArc(skia.Rect.MakeLTRB(10, -16, 30, 2), -90, 180)
    c.drawPath(arc, stroke("#E4DACA", 4, a))
    line(c, -16, -22, 16, -22, stroke(GOLD, 2, a))
    c.restore()


def icon_photo(c, x, y, s=1.0, a=1.0):
    """朋友合照：小相框内两个简化剪影。"""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    rrect(c, -30, -36, 60, 48, 3, fill("#000000", 0.45 * a, blur=5))
    rrect(c, -30, -36, 60, 48, 3, fill("#4A3D31", a))
    rrect(c, -24, -30, 48, 36, 2, fill("#20242A", a))
    for dx, h in ((-9, 0), (9, 3)):
        c.drawCircle(dx, -16 + h, 6, fill("#C9B497", a))
        rrect(c, dx - 8, -8 + h, 16, 14, 6, fill("#8C7F6B", a))
    line(c, -14, 12, 14, 12, stroke("#4A3D31", 4, a))
    line(c, 0, 12, 0, 20, stroke("#4A3D31", 4, a))
    c.restore()


def checkbox_frame(c, x, y, grow=1.0, a=1.0, morph=0.0, tick=0.0):
    """打卡框：从地面长出的竖立框体与空勾选框；morph 0—1 退成普通横向相框（挂在墙上）。"""
    if a <= 0 or grow <= 0:
        return
    w = lerp(110, 150, morph)
    h = lerp(150, 104, morph) * clamp01(grow)
    cy = lerp(y - h / 2, 380, morph)
    cx = lerp(x, x + 10, morph)
    rrect(c, cx - w / 2, cy - h / 2, w, h, lerp(10, 3, morph), fill("#000000", 0.5 * a, blur=10))
    rrect(c, cx - w / 2, cy - h / 2, w, h, lerp(10, 3, morph), fill(gfx.mix(PAPER_DARK, "#4A3D31", morph), a))
    rrect(c, cx - w / 2, cy - h / 2, w, h, lerp(10, 3, morph), stroke(GOLD, 2, a * (1 - 0.6 * morph)))
    if grow >= 0.6:
        g = clamp01((grow - 0.6) / 0.4)
        bx = 34 * (1 - morph)
        if morph < 1:
            rrect(c, cx - bx, cy - bx, 2 * bx, 2 * bx, 4, stroke(WHITE, 3, a * g * (1 - morph)))
        if tick > 0:
            c.drawPath(_path([(cx - 16, cy), (cx - 4, cy + 12), (cx - 4 + 22 * tick, cy + 12 - 26 * tick)]),
                       stroke(GOLD, 4, a))
        if morph > 0:
            iw, ih = w - 14, h - 14
            rrect(c, cx - iw / 2, cy - ih / 2, iw, ih, 2, fill("#1E242B", a * morph))
            hill = _path([(cx - iw / 2, cy + ih / 2 - 6), (cx - 18, cy - 4), (cx + 4, cy + 12), (cx + 24, cy - 10),
                          (cx + iw / 2, cy + ih / 2 - 10)])
            c.drawPath(hill, stroke("#7C8790", 2.4, a * morph))
            c.drawCircle(cx + 30, cy - 22, 7, fill("#C9B497", a * morph * 0.8))


def cat_clip(c, x, y, w, h, t, a=1.0, dim=0.0):
    """同一段原创猫咪轮廓短片：轮廓猫拍打毛线球（循环 2.4 秒）。两侧调用参数相同即画面完全一致。"""
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(x, y, w, h))
    bgc = gfx.mix("#1F2630", "#14171B", dim)
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), fill(bgc, a))
    s = h / 160
    cx, cy = x + w * 0.42, y + h * 0.72
    ph = (t % 2.4) / 2.4
    paw = math.sin(ph * 2 * math.pi)
    colr = gfx.mix("#E6DCCB", "#8F887D", dim)
    c.translate(cx, cy)
    c.scale(s, s)
    c.drawOval(skia.Rect.MakeLTRB(-50, -34, 34, 16), fill(colr, a))
    c.drawCircle(42, -40, 24, fill(colr, a))
    for ex in (30, 52):
        tri = _path([(ex - 9, -56), (ex, -78), (ex + 9, -56)])
        tri.close()
        c.drawPath(tri, fill(colr, a))
    tail = skia.Path()
    tail.moveTo(-48, -6)
    tail.quadTo(-86, -30 + 10 * paw, -72, -64)
    c.drawPath(tail, stroke(colr, 10, a))
    line(c, 20, 10, 58 + 10 * paw, -6 - 18 * max(paw, 0), stroke(colr, 11, a))
    bx = 92 + 14 * math.sin(ph * 2 * math.pi + 1.2)
    c.drawCircle(bx, 0, 15, fill(gfx.mix(GOLD, "#7A6F5C", dim), a))
    line(c, bx - 10, -6, bx + 9, 7, stroke("#8C7444", 2, a))
    c.restore()


def hourglass_card(c, x, y, s=1.0, a=1.0):
    """框架卡：深色纸卡上的沙漏（"浪费时间"的框架示意，无文字）。"""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    paper_card(c, -46, -56, 92, 112, a, dark=True, r=8, lift=0.8)
    p = _path([(-20, -34), (20, -34), (2, 0), (20, 34), (-20, 34), (-2, 0)])
    p.close()
    c.drawPath(p, stroke(GOLD, 2.6, a))
    tri = _path([(-12, 30), (12, 30), (0, 16)])
    tri.close()
    c.drawPath(tri, fill(GOLD, 0.8 * a))
    c.restore()


def steam(c, x, y, t, a=1.0):
    """杯口热气：三缕缓升的细线，仅局部点缀。"""
    for k in range(3):
        ph = (t * 0.35 + k / 3) % 1
        yy = y - 10 - ph * 70
        sway = 6 * math.sin(t * 1.4 + k * 2.1 + ph * 3)
        p = skia.Path()
        p.moveTo(x - 10 + k * 10 + sway, yy)
        p.quadTo(x - 4 + k * 10 - sway, yy - 16, x - 10 + k * 10 + sway, yy - 32)
        c.drawPath(p, stroke(WHITE, 3.0, a * 0.7 * math.sin(math.pi * ph)))


# ---------------------------------------------------------------- 文字

def text_size(L: Layout, lines: tuple, source: bool = False) -> float:
    """主卡字号：按最宽一行适配可用宽度；来源卡用正文字号。"""
    base = L.body_size if source else L.text_size
    widest = max(gfx.text_width(t, base, "bold") for t in lines)
    return base * min(1.0, (L.text_maxw - 2) / widest)


def main_card(c, L: Layout, lines: tuple, hi: tuple, a: float, rise: float, node: float = 0.0,
              source: bool = False):
    """主卡：两行主字幕（正面、无透视），上方金属细线与菱形节点；node 为节拍点亮强度。
    a 为入场 / 退场不透明度，rise 为入场位移（阅读窗口内恒为 0）。"""
    if a <= 0:
        return
    size = text_size(L, lines, source)
    gap = L.line_gap * (size / L.text_size if source else 1.0) * (1.25 if source else 1.0)
    n = len(lines)
    y0 = L.text_y - (n - 1) * gap / 2 + rise
    cx = L.text_cx
    sc = skia.Paint(AntiAlias=True)
    sc.setShader(skia.GradientShader.MakeRadial((cx, y0 + (n - 1) * gap / 2), L.text_maxw * 0.62,
                                               [gfx.col(INK, 0.75 * a), gfx.col(INK, 0)]))
    c.drawCircle(cx, y0 + (n - 1) * gap / 2, L.text_maxw * 0.62, sc)
    ry = y0 - size * 0.95
    half = min(L.text_maxw / 2, 260)
    gold_line(c, [(cx - half, ry), (cx - 14, ry)], 1.6, 0.8 * a)
    gold_line(c, [(cx + 14, ry), (cx + half, ry)], 1.6, 0.8 * a)
    d = _path([(cx, ry - 8), (cx + 8, ry), (cx, ry + 8), (cx - 8, ry)])
    d.close()
    if node > 0:
        c.drawCircle(cx, ry, 16, fill(GOLD, 0.5 * node * a, blur=8))
    c.drawPath(d, fill(GOLD, a))
    for k, t in enumerate(lines):
        y = y0 + k * gap
        segs = _split_hi(t, hi)
        w = sum(gfx.text_width(s, size, "bold") for s, _ in segs)
        x = cx - w / 2
        for s, h in segs:
            x += gfx.draw_text(c, s, x, y, size, "bold", GOLD if h else WHITE, a, "left",
                               shadow=(0, 4, 8, "#000000"))


def _split_hi(t: str, hi: tuple) -> list:
    for h in hi:
        i = t.find(h)
        if i >= 0:
            return [(s, f) for s, f in ((t[:i], False), (h, True), (t[i + len(h):], False)) if s]
    return [(t, False)]


def main_card_bounds(L: Layout, lines: tuple, source: bool = False) -> tuple:
    """主卡文字外接框（屏幕坐标）与字号，用于安全区与溢出检查。"""
    size = text_size(L, lines, source)
    gap = L.line_gap * (size / L.text_size if source else 1.0) * (1.25 if source else 1.0)
    n = len(lines)
    y0 = L.text_y - (n - 1) * gap / 2
    w = max(gfx.text_width(t, size, "bold") for t in lines)
    return (L.text_cx - w / 2, y0 - size * 0.62, L.text_cx + w / 2, y0 + (n - 1) * gap + size * 0.5, size)


def tag(c, L: Layout, text: str, a: float = 1.0):
    """固定角标：香槟金描边胶囊 + 暖白小字。"""
    if a <= 0:
        return
    size = L.tag_size
    w = gfx.text_width(text, size, "bold") + size * 1.3
    h = size * 1.7
    x, y = L.tag_x, L.tag_y
    rrect(c, x, y, w, h, h / 2, fill(INK, 0.7 * a))
    rrect(c, x, y, w, h, h / 2, stroke(GOLD, 1.6, 0.85 * a))
    c.drawCircle(x + size * 0.55, y + h / 2, size * 0.13, fill(GOLD, a))
    gfx.draw_text(c, text, x + size * 0.85, y + h / 2, size, "bold", WHITE, 0.92 * a, "left")


# ---------------------------------------------------------------- 卧室（深夜版）

BED_X0, BED_X1, MATTRESS_Y = 250, 830, 640
STAND_X0, STAND_X1, STAND_Y = 0, 220, 600


def room_far_night(c, t, light=1.0, lamp=1.0, door=False):
    """远景：夜色窗户与月亮、墙面、可选的门（第 6 镜拉远时露出），由调用方套景深模糊。"""
    c.drawRect(skia.Rect.MakeLTRB(-1500, FLOOR_Y, 2500, 2400), fill("#0B0C0E", 1))
    rrect(c, 420, 150, 240, 260, 6, fill("#10151C", light))
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeLinear([(420, 150), (660, 410)],
                                               [gfx.col("#26324A", 0.8 * light), gfx.col("#121722", 0.9 * light)]))
    rrect(c, 428, 158, 224, 244, 4, p)
    c.drawCircle(600, 215, 26, fill("#E9E1CB", 0.85 * light))
    c.drawCircle(612, 207, 24, fill("#1E2738", 0.95 * light))
    line(c, 540, 158, 540, 402, stroke("#0D1117", 6, light))
    line(c, 428, 280, 652, 280, stroke("#0D1117", 6, light))
    g = skia.Paint(AntiAlias=True)
    g.setShader(skia.GradientShader.MakeRadial((540, 520), 380, [gfx.col("#8FA6C8", 0.10 * light), gfx.col("#8FA6C8", 0)]))
    c.drawCircle(540, 520, 380, g)
    if lamp > 0:
        g2 = skia.Paint(AntiAlias=True)
        g2.setShader(skia.GradientShader.MakeRadial((190, 470), 360, [gfx.col("#E8C98A", 0.30 * lamp * light),
                                                                    gfx.col("#E8C98A", 0)]))
        c.drawCircle(190, 470, 360, g2)
    if door:
        rrect(c, 1010, 300, 170, 550, 4, fill("#121316", light))
        rrect(c, 1022, 312, 146, 538, 3, fill("#17191D", light))
        c.drawCircle(1150, 590, 7, fill(GOLD, 0.5 * light))


def bed_back(c, a=1.0):
    """床头板、床体与床垫（人物之下的部分）。"""
    if a <= 0:
        return
    soft_shadow(c, 540, FLOOR_Y, 330, 16, 0.6 * a)
    rrect(c, 214, 470, 40, 330, 10, fill("#2E2822", a))
    rrect(c, 214, 470, 40, 12, 6, fill("#4A4036", a))
    rrect(c, 250, 700, 580, 92, 8, fill("#2B2520", a))
    rrect(c, 250, 700, 580, 92, 8, stroke("#3E352C", 1.4, a))
    for lx in (270, 800):
        rrect(c, lx, 792, 14, FLOOR_Y - 792, 3, fill("#1A1612", a))
    rrect(c, 252, MATTRESS_Y, 576, 66, 18, fill("#3C4048", a))
    rrect(c, 256, MATTRESS_Y + 2, 568, 10, 6, fill("#4D525B", 0.7 * a))
    rrect(c, 262, 600, 120, 48, 22, fill("#C9C2B4", a))
    rrect(c, 268, 604, 108, 12, 6, fill("#DDD6C9", 0.7 * a))


def blanket(c, P: dict, a=1.0, from_hip=False):
    """被子：沿人物身体上方 30 单位的平滑轮廓盖到床尾；from_hip=True 时只盖腿（坐起时）。"""
    if a <= 0:
        return
    j = joints(P)
    pts = [j["hip"], j["kn_n"], j["ft_n"]]
    if not from_hip:
        mid = ((j["sh"][0] + j["hip"][0]) / 2, (j["sh"][1] + j["hip"][1]) / 2)
        pts = [(j["sh"][0] + 26, j["sh"][1]), mid] + pts
    path = skia.Path()
    x0 = pts[0][0]
    path.moveTo(x0, MATTRESS_Y + 30)
    path.lineTo(x0, pts[0][1] - 30)
    for k in range(1, len(pts)):
        px, py = pts[k - 1]
        qx, qy = pts[k]
        path.quadTo(px, py - 34, (px + qx) / 2, min(py, qy) - 32)
    path.quadTo(min(BED_X1 - 6, pts[-1][0] + 40), pts[-1][1] - 30, BED_X1 + 6, MATTRESS_Y + 6)
    path.lineTo(BED_X1 + 8, MATTRESS_Y + 74)
    path.lineTo(x0, MATTRESS_Y + 74)
    path.close()
    c.drawPath(path, fill("#000000", 0.35 * a, blur=10))
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeLinear([(0, 560), (0, 720)], [gfx.col("#6A6152", a), gfx.col("#463F35", a)]))
    c.drawPath(path, p)
    c.drawPath(path, stroke("#857A68", 1.6, 0.6 * a))
    line(c, x0 + 6, pts[0][1] - 22, x0 + 6, MATTRESS_Y + 60, stroke("#8C826F", 3, 0.5 * a))


def nightstand(c, a=1.0, drawer=0.0):
    """床头柜（有抽屉），台面 y=600，x 0—220。"""
    if a <= 0:
        return
    soft_shadow(c, 110, FLOOR_Y, 120, 10, 0.5 * a)
    rrect(c, STAND_X0, STAND_Y - 8, 220, 16, 4, fill("#4A3D31", a))
    rrect(c, 10, STAND_Y + 8, 200, 92, 3, fill(WOOD, a))
    for lx in (14, 194):
        rrect(c, lx, STAND_Y + 100, 12, FLOOR_Y - STAND_Y - 100, 2, fill("#2C241D", a))
    dx = 70 * drawer
    if drawer > 0:
        rrect(c, 22, STAND_Y + 20, 176, 56, 2, fill("#120E0B", a))
    rrect(c, 22 + dx, STAND_Y + 20, 176, 56, 3, fill("#4A3D31", a))
    rrect(c, 22 + dx, STAND_Y + 20, 176, 56, 3, stroke("#5E4F40", 1.4, a))
    rrect(c, 96 + dx, STAND_Y + 44, 28, 6, 3, fill(GOLD, 0.8 * a))


def clock(c, text: str, colon: bool, a=1.0, glow=0.0):
    """床头数字时钟（x 14—104），显示 HH:MM；colon 控制冒号随拍闪烁。"""
    if a <= 0:
        return
    rrect(c, 14, STAND_Y - 52, 92, 46, 8, fill("#0E0F11", a))
    rrect(c, 14, STAND_Y - 52, 92, 46, 8, stroke("#3A332B", 1.6, a))
    if glow > 0:
        rrect(c, 10, STAND_Y - 56, 100, 54, 10, fill(GOLD, 0.35 * glow * a, blur=12))
    hh, mm = text.split(":")
    y = STAND_Y - 29
    gfx.draw_text(c, hh, 40, y, 30, "bold", GOLD, a)
    gfx.draw_text(c, mm, 80, y, 30, "bold", GOLD, a)
    if colon:
        c.drawCircle(60, y - 7, 2.6, fill(GOLD, a))
        c.drawCircle(60, y + 7, 2.6, fill(GOLD, a))


def lamp(c, on=1.0, a=1.0):
    """床头柜右侧的小台灯；on 0—1 为亮度。"""
    if a <= 0:
        return
    rrect(c, 172, STAND_Y - 14, 44, 10, 4, fill("#3A332B", a))
    line(c, 194, STAND_Y - 14, 194, STAND_Y - 96, stroke("#3A332B", 4, a))
    shade = _path([(166, STAND_Y - 96), (222, STAND_Y - 96), (210, STAND_Y - 140), (178, STAND_Y - 140)])
    shade.close()
    c.drawPath(shade, fill(gfx.mix("#3E352B", "#E8CF9A", on), a))
    if on > 0:
        c.drawCircle(194, STAND_Y - 90, 70, fill("#E8C98A", 0.30 * on * a, blur=40))


def name_plate(c, x, y, w, name, a=1.0, size=34):
    """作者名牌：深色纸卡 + 金色圆点 + 拉丁字母全名（不画肖像）。"""
    if a <= 0:
        return
    paper_card(c, x, y, w, 70, a, dark=True, r=8, lift=0.6)
    c.drawCircle(x + 32, y + 35, 7, fill(GOLD, a))
    gfx.draw_text(c, name, x + 56, y + 35, size, "bold", WHITE, a, "left")


def label(c, text, x, y, size=34, a=1.0, color=WHITE, align="center"):
    gfx.draw_text(c, text, x, y, size, "bold", color, a, align)


def icon_dumbbell(c, x, y, s=1.0, a=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    line(c, -26, 0, 26, 0, stroke("#BDB2A0", 7, a))
    for sx in (-1, 1):
        rrect(c, sx * 30 - 7, -18, 14, 36, 4, fill("#D8CCB4", a))
        rrect(c, sx * 40 - 5, -12, 10, 24, 3, fill("#BDB2A0", a))
    c.restore()


def icon_certificate(c, x, y, s=1.0, a=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -30, -22, 60, 40, 4, fill("#D8CCB4", a))
    for k in range(2):
        line(c, -20, -10 + k * 10, 14, -10 + k * 10, stroke("#9A8C72", 2.4, a))
    c.drawCircle(18, 12, 9, fill(GOLD, a))
    c.drawPath(_path([(13, 18), (10, 30), (18, 25), (26, 30), (23, 18)]), fill(GOLD, a))
    c.restore()


def icon_laptop(c, x, y, s=1.0, a=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -28, -24, 56, 36, 4, fill("#2A2F37", a))
    rrect(c, -24, -20, 48, 28, 2, fill("#3E4A5A", a))
    rrect(c, -36, 12, 72, 8, 3, fill("#BDB2A0", a))
    c.drawCircle(0, -6, 8, fill(GOLD, a))
    c.restore()


def icon_headphones(c, x, y, s=1.0, a=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    arc = skia.Path()
    arc.addArc(skia.Rect.MakeLTRB(-26, -30, 26, 22), 180, 180)
    c.drawPath(arc, stroke("#D8CCB4", 6, a))
    for sx in (-1, 1):
        rrect(c, sx * 26 - 8, -6, 16, 26, 6, fill(GOLD, a))
    c.restore()


def runner(c, x, y, ph, s=1.0, a=1.0, colr="#BDB2A0"):
    """奔跑小人剪影（无脸）；ph 为步态相位。"""
    c.save(); c.translate(x, y); c.scale(s, s)
    sw = math.sin(ph * 2 * math.pi)
    c.drawCircle(-4, -42, 8, fill(colr, a))
    line(c, -2, -32, 4, -10, stroke(colr, 6, a))
    line(c, 4, -10, 4 - 12 * sw, 8, stroke(colr, 5, a))
    line(c, 4, -10, 4 + 12 * sw, 8, stroke(colr, 5, a))
    line(c, 0, -26, -12 * sw, -16, stroke(colr, 4, a))
    line(c, 0, -26, 12 * sw, -16, stroke(colr, 4, a))
    c.restore()


def phone_feed(c, x, y, w, h, scroll, a=1.0, items=None):
    """放大的手机屏幕：信息流卡片按 scroll（以条计，整数为停稳位置）向上滚动。"""
    if a <= 0:
        return
    rrect(c, x - 10, y - 10, w + 20, h + 20, 30, fill("#000000", 0.5 * a, blur=16))
    rrect(c, x - 10, y - 10, w + 20, h + 20, 30, fill("#0E0F12", a))
    rrect(c, x - 10, y - 10, w + 20, h + 20, 30, stroke(GOLD, 1.6, 0.6 * a))
    c.save()
    c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), 20, 20), doAntiAlias=True)
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), fill("#171B22", a))
    items = items or [icon_dumbbell, icon_certificate, icon_laptop]
    ih = 130
    for k in range(-1, 6):
        idx = k + int(math.floor(scroll))
        yy = y + 20 + k * ih - (scroll - math.floor(scroll)) * ih
        rrect(c, x + 14, yy, w - 28, ih - 18, 12, fill("#222831", a))
        items[idx % len(items)](c, x + 64, yy + (ih - 18) / 2, 1.1, a)
        line(c, x + 120, yy + 38, x + w - 34, yy + 38, stroke("#5A6472", 6, a))
        line(c, x + 120, yy + 62, x + w - 70, yy + 62, stroke("#434B57", 6, a))
        c.drawCircle(x + w - 40, yy + 86, 8, fill(GOLD, 0.7 * a))
    c.restore()
