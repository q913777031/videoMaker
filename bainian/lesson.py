"""《百年孤独》白板手绘系列公共模块：复用《资治通鉴》的 Lesson（zizhi/lesson.py，内含丰田的 fengtian/common.Lesson），
换上本系列的文案（bainian/PLAN.md）、系列名，再加马孔多人物造型、拉美小镇道具和分镜常用件。

分镜模块写法同资治通鉴（见 bainian/ep01_ice.py）：

    from bainian import lesson as N
    SCREENS = [([], "开场", 0), ([0, 1], "生活里", 1), ...]
    L = N.Lesson("01", SCREENS, drop_screen=2, theme=BT.get("01"))
    ...
    L.finish(cover_shot=…, square_shot=…, notes=NOTES)
    L.export(globals())

人物区分：
- 今人：小李 draw_li（黑线小人 + 领带）、小王 draw_wang（短发 + 橙发卡、白衬衫），在办公室、家里、手机旁，线条是黑 / 蓝。
- 书中人 draw_man / draw_lady：一百多年前的加勒比小镇打扮——男人粗布衬衫、背带长裤、草帽或大胡子，女人长到脚面的大摆裙、
  发髻、围裙；吉卜赛人梅尔基亚德斯戴一顶宽檐黑帽。书中人出场的屏用“羊皮卷”框（左上角一只黄蝴蝶，角上“马孔多”小章），
  头顶挂名牌（人名 + 辈分），和今人的场景一眼分得开。
"""

import math

import skia

from adler import core
from adler import kit as K
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from fengtian import common as C
from fengtian.common import BLACK, BLUE, GREEN, ORANGE, RED, YELLOW, draw_li, pop_scale, rest_hands, slam_scale  # noqa: F401
from whiteboard import engine as wb
from whiteboard.engine import P
from zizhi import lesson as Z
from zizhi.lesson import (BLUE_FILL, GRAY, GRAY_FILL, GREEN_FILL, INK, NOTE_FILL, RED_FILL, at_pop, box,  # noqa: F401
                          bubble_box, chip, desk, doc_card, draw_wang, phone, seal, sparkle)
from bainian import hooks as _hooks  # noqa: F401  注册开场钩子（放在 zizhi 之后，覆盖系列小字）
from bainian import plan

core.SERIES.update(name="百年孤独", count="第一季", prefix="百年孤独")
_hooks.FH.SERIES_SUB = "百年孤独 · 写给今天的我们"   # zizhi.lesson 导入时会改成资治通鉴的，这里改回来（与导入顺序无关）

HAIR = "#2E2A28"
SKIN = "#FFFFFF"
PARCH, PARCH_LINE = "#F3E3C0", "#8A6A3A"
BUTTER = "#F2C230"                 # 黄蝴蝶、黄花
ICE, ICE_LINE = "#D6ECF7", "#3F7FB8"
ADOBE, ADOBE_LINE = "#E7C3A0", "#8A4B2A"
LEAF, LEAF_LINE = "#BFD9A8", "#3F6B3A"

# 书中人配色（衣服, 线色）
CLOTH = dict(white=("#FFFFFF", "#5E4128"), ochre=("#F0DDB8", "#8A5A1E"), blue=("#D4E1F2", "#2F5B8E"),
             green=("#D6E8D0", "#3F6B3A"), red=("#F4CFC8", "#9C2F25"), purple=("#E6D6EE", "#6B3F7A"),
             black=("#4A4A4A", "#1E1E1E"), gray=("#E2E2DE", "#5E5E58"), yellow=("#FBE7A6", "#9C7A1A"))


class Lesson(Z.Lesson):
    """资治通鉴的 Lesson（拍点小工具 wp / kq / nx / cap / ev / pop_fn / seal_ev）+ 本系列文案。"""

    PLAN = plan

    def captions(self):
        """同丰田 Lesson.captions，另外允许字幕在外文名的间隔号“·”处断开（断开处的“·”不上屏）。"""
        caps = []
        for li, (text, pieces, _) in enumerate(self.LINES):
            plain = [ch for ch in text if ch not in C._PUNCT]
            idx = 0
            for cap in pieces:
                body = [ch for ch in cap if ch not in C._PUNCT + "【】"]
                if idx < len(plain) and plain[idx] == "·" and body[:1] != ["·"]:
                    idx += 1
                if plain[idx: idx + len(body)] != body:
                    raise ValueError(f"字幕与旁白不一致：{text} / {cap}")
                caps.append([self.char_time(li, idx), None, cap.rstrip("，。；：")])
                idx += len(body)
            if idx != len(plain):
                raise ValueError(f"字幕没有覆盖整句：{text}")
        for i, cp in enumerate(caps):
            cp[1] = caps[i + 1][0] if i + 1 < len(caps) else None
        return caps


# ================================================================ 书中人

def _face(c, hx, hy, s, mood, alpha):
    Z._face(c, hx, hy, s, mood, alpha)


def _arm(c, sh, hd, s, fill, line, alpha, w0=14, w1=18):
    dx, dy = hd[0] - sh[0], hd[1] - sh[1]
    d = math.hypot(dx, dy) or 1.0
    nx_, ny_ = -dy / d, dx / d
    sl = P((sh[0] + nx_ * w0 * s, sh[1] + ny_ * w0 * s), (hd[0] + nx_ * w1 * s, hd[1] + ny_ * w1 * s),
           (hd[0] - nx_ * w1 * s, hd[1] - ny_ * w1 * s), (sh[0] - nx_ * w0 * s, sh[1] - ny_ * w0 * s), close=True)
    c.drawPath(sl, K.paint(fill, alpha))
    c.drawPath(sl, wb.marker(line, 5, alpha))
    c.drawCircle(hd[0] + dx / d * 10 * s, hd[1] + dy / d * 10 * s, 11 * s, K.paint(SKIN, alpha))
    c.drawCircle(hd[0] + dx / d * 10 * s, hd[1] + dy / d * 10 * s, 11 * s, wb.marker(BLACK, 4, alpha))


def _head(c, hx, hy, s, alpha):
    c.drawCircle(hx, hy, 45 * s, K.paint(SKIN, alpha))
    c.drawCircle(hx, hy, 45 * s, wb.marker(BLACK, 9, alpha))


def _hat(c, hx, hy, s, hat, alpha):
    if hat == "straw":                     # 草帽：宽檐 + 矮帽顶 + 一道帽带
        c.drawOval(skia.Rect.MakeXYWH(hx - 86 * s, hy - 58 * s, 172 * s, 30 * s), K.paint("#E9CF8A", alpha))
        c.drawOval(skia.Rect.MakeXYWH(hx - 86 * s, hy - 58 * s, 172 * s, 30 * s), wb.marker("#8A6A2A", 5, alpha))
        top = P((hx - 44 * s, hy - 46 * s), (hx - 36 * s, hy - 96 * s), (hx + 36 * s, hy - 96 * s), (hx + 44 * s, hy - 46 * s),
                close=True)
        c.drawPath(top, K.paint("#E9CF8A", alpha))
        c.drawPath(top, wb.marker("#8A6A2A", 5, alpha))
        c.drawRect(skia.Rect.MakeLTRB(hx - 42 * s, hy - 62 * s, hx + 42 * s, hy - 50 * s), K.paint("#5E4128", alpha))
    elif hat == "gypsy":                   # 吉卜赛人的宽檐黑帽（像张开的乌鸦翅膀）
        c.drawPath(P((hx - 120 * s, hy - 40 * s), (hx, hy - 70 * s), (hx + 120 * s, hy - 40 * s), (hx, hy - 52 * s), close=True),
                   K.paint("#1E1E1E", alpha))
        top = P((hx - 46 * s, hy - 50 * s), (hx - 40 * s, hy - 110 * s), (hx + 40 * s, hy - 110 * s), (hx + 46 * s, hy - 50 * s),
                close=True)
        c.drawPath(top, K.paint("#1E1E1E", alpha))
    elif hat == "kepi":                    # 上校的军帽
        c.drawRect(skia.Rect.MakeLTRB(hx - 40 * s, hy - 92 * s, hx + 40 * s, hy - 44 * s), K.paint("#3D4A63", alpha))
        c.drawPath(P((hx - 46 * s, hy - 44 * s), (hx + 46 * s, hy - 44 * s), (hx + 30 * s, hy - 32 * s), (hx - 50 * s, hy - 34 * s),
                     close=True), K.paint("#1E1E1E", alpha))
        C.line(c, (hx - 40 * s, hy - 70 * s), (hx + 40 * s, hy - 70 * s), "#C9A34A", 4, alpha)


def _beard(c, hx, hy, s, beard, alpha):
    if not beard:
        return
    col = {"white": "#F2F2F2", "gray": "#BDBDB8"}.get(beard, HAIR)
    if beard == "mustache":
        for sg in (-1, 1):
            c.drawPath(P((hx, hy + 12 * s), (hx + sg * 28 * s, hy + 18 * s), (hx + sg * 34 * s, hy + 26 * s), (hx, hy + 18 * s),
                         close=True), K.paint(HAIR, alpha))
        return
    bp = P((hx - 40 * s, hy + 4 * s), (hx - 30 * s, hy + 64 * s), (hx, hy + 84 * s), (hx + 30 * s, hy + 64 * s), (hx + 40 * s, hy + 4 * s),
           (hx + 18 * s, hy + 30 * s), (hx - 18 * s, hy + 30 * s), close=True)
    c.drawPath(bp, K.paint(col, alpha))
    c.drawPath(bp, wb.marker(GRAY if beard in ("white", "gray") else HAIR, 4, alpha))


def draw_man(c, x, y, s, color="white", hat=None, beard=None, mood="flat", lh=None, rh=None, head_dx=0.0, alpha=1.0,
             hair=HAIR, vest=None, tall=1.0):
    """书中男人：粗布衬衫 + 背带长裤 + 靴子；hat：None / straw 草帽 / gypsy 宽檐黑帽 / kepi 军帽；
    beard：None / full / mustache / white / gray；vest：坎肩颜色。(x, y) 为脚底，身高约 330·s·tall。"""
    shirt, line = CLOTH[color]
    d_lh, d_rh = rest_hands(x, y, s)
    hy = y - 290 * s * tall
    lh, rh = lh or (d_lh[0], d_lh[1] - 290 * s * (tall - 1)), rh or (d_rh[0], d_rh[1] - 290 * s * (tall - 1))
    hip = y - 130 * s
    pants = "#6B5A48"
    for sg in (-1, 1):
        leg = P((x + sg * 6 * s, hip), (x + sg * 40 * s, hip), (x + sg * 44 * s, y - 16 * s), (x + sg * 12 * s, y - 16 * s), close=True)
        c.drawPath(leg, K.paint(pants, alpha))
        c.drawPath(leg, wb.marker(BLACK, 4, alpha))
        c.drawRoundRect(skia.Rect.MakeXYWH(x + sg * 28 * s - 22 * s, y - 20 * s, 44 * s, 20 * s), 8 * s, 8 * s,
                        K.paint(INK, alpha))
    torso = skia.Rect.MakeLTRB(x - 44 * s, hy + 56 * s, x + 44 * s, hip + 6 * s)
    c.drawRoundRect(torso, 16 * s, 16 * s, K.paint(shirt, alpha))
    c.drawRoundRect(torso, 16 * s, 16 * s, wb.marker(line, 6, alpha))
    if vest:
        for sg in (-1, 1):
            c.drawPath(P((x + sg * 44 * s, hy + 62 * s), (x + sg * 14 * s, hy + 70 * s), (x + sg * 10 * s, hip + 4 * s),
                         (x + sg * 44 * s, hip + 4 * s), close=True), K.paint(vest, alpha))
    else:
        for sg in (-1, 1):
            C.line(c, (x + sg * 24 * s, hy + 60 * s), (x + sg * 24 * s, hip + 4 * s), "#5E4128", 5, alpha)
    c.drawPath(P((x - 18 * s, hy + 56 * s), (x, hy + 80 * s), (x + 18 * s, hy + 56 * s)), wb.marker(line, 5, alpha))
    sh_l, sh_r = (x - 38 * s, hy + 74 * s), (x + 38 * s, hy + 74 * s)
    _arm(c, sh_l, lh, s, shirt, line, alpha)
    _arm(c, sh_r, rh, s, shirt, line, alpha)
    hx = x + head_dx
    _head(c, hx, hy, s, alpha)
    if hair and hat not in ("straw", "gypsy", "kepi"):
        cap = skia.Path()
        cap.addArc(skia.Rect.MakeXYWH(hx - 47 * s, hy - 50 * s, 94 * s, 66 * s), 180, 180)
        cap.close()
        c.drawPath(cap, K.paint(hair, alpha))
    _face(c, hx, hy, s, mood, alpha)
    _beard(c, hx, hy, s, beard, alpha)
    if beard in ("full", "white", "gray") and mood in ("laugh", "o"):
        c.drawCircle(hx, hy + 26 * s, 8 * s, K.paint(BLACK, alpha))
    _hat(c, hx, hy, s, hat, alpha)


def draw_lady(c, x, y, s, color="blue", hair="bun", apron=False, mood="flat", lh=None, rh=None, head_dx=0.0, alpha=1.0,
              bandage=None, hair_color=HAIR):
    """书中女人：高领上衣 + 长到脚面的大摆裙；hair：bun 发髻 / long 长发 / gray 花白发髻 / veil 黑头纱 / short 齐耳 / none 剃光；
    apron=True 系围裙；bandage="l"/"r" 那只手缠黑纱布（阿玛兰妲）。(x, y) 为脚底，身高约 330·s。"""
    dress, line = CLOTH[color]
    d_lh, d_rh = rest_hands(x, y, s)
    lh, rh = lh or d_lh, rh or d_rh
    hy = y - 290 * s
    skirt = P((x - 40 * s, hy + 150 * s), (x + 40 * s, hy + 150 * s), (x + 92 * s, y - 4 * s), (x - 92 * s, y - 4 * s), close=True)
    c.drawPath(skirt, K.paint(dress, alpha))
    c.drawPath(skirt, wb.marker(line, 6, alpha))
    for dx in (-40, 0, 40):
        C.line(c, (x + dx * 0.35 * s, hy + 170 * s), (x + dx * s, y - 12 * s), line, 3, 0.5 * alpha)
    if apron:
        ap = P((x - 34 * s, hy + 156 * s), (x + 34 * s, hy + 156 * s), (x + 44 * s, y - 60 * s), (x - 44 * s, y - 60 * s), close=True)
        c.drawPath(ap, K.paint("#FFFFFF", alpha))
        c.drawPath(ap, wb.marker(line, 4, alpha))
    torso = skia.Rect.MakeLTRB(x - 38 * s, hy + 52 * s, x + 38 * s, hy + 158 * s)
    c.drawRoundRect(torso, 14 * s, 14 * s, K.paint(dress, alpha))
    c.drawRoundRect(torso, 14 * s, 14 * s, wb.marker(line, 6, alpha))
    c.drawRect(skia.Rect.MakeLTRB(x - 40 * s, hy + 146 * s, x + 40 * s, hy + 160 * s), K.paint(line, alpha))
    sh_l, sh_r = (x - 34 * s, hy + 70 * s), (x + 34 * s, hy + 70 * s)
    _arm(c, sh_l, lh, s, dress, line, alpha, 12, 15)
    _arm(c, sh_r, rh, s, dress, line, alpha, 12, 15)
    for side, hd in (("l", lh), ("r", rh)):
        if bandage == side:
            c.drawCircle(hd[0], hd[1], 17 * s, K.paint("#1E1E1E", alpha))
    hx = x + head_dx
    hc = "#BDBDB8" if hair == "gray" else hair_color
    if hair == "long":                       # 长发：两侧垂到肩下（不画在下巴底下，免得像胡子）
        for sg in (-1, 1):
            c.drawRoundRect(skia.Rect.MakeXYWH(hx + sg * 38 * s - 18 * s, hy - 30 * s, 36 * s, 140 * s), 16 * s, 16 * s,
                            K.paint(hc, alpha))
    if hair == "veil":
        c.drawPath(P((hx - 62 * s, hy - 30 * s), (hx, hy - 70 * s), (hx + 62 * s, hy - 30 * s), (hx + 70 * s, hy + 120 * s),
                     (hx - 70 * s, hy + 120 * s), close=True), K.paint("#2A2A2A", alpha))
    _head(c, hx, hy, s, alpha)
    if hair != "none":                        # none：剃光的头（俏姑娘雷梅黛丝）
        cap = skia.Path()
        cap.addArc(skia.Rect.MakeXYWH(hx - 48 * s, hy - 50 * s, 96 * s, 70 * s), 180, 180)
        cap.close()
        c.drawPath(cap, K.paint("#2A2A2A" if hair == "veil" else hc, alpha))
    if hair in ("bun", "gray"):
        c.drawCircle(hx, hy - 54 * s, 22 * s, K.paint(hc, alpha))
    elif hair == "short":
        for sg in (-1, 1):
            c.drawRoundRect(skia.Rect.MakeXYWH(hx + sg * 40 * s - 10 * s, hy - 24 * s, 20 * s, 54 * s), 10 * s, 10 * s,
                            K.paint(hc, alpha))
    _face(c, hx, hy, s, mood, alpha)


# 主要人物的固定造型（同一个人每讲长一样）
def jose(c, x, y, s, **kw):
    """何塞·阿尔卡蒂奥·布恩迪亚（第一代，创立马孔多）：大胡子、白衬衫、坎肩。"""
    kw.setdefault("beard", "full")
    draw_man(c, x, y, s, "white", vest="#8A5A2E", tall=1.05, **kw)


def ursula(c, x, y, s, old=False, **kw):
    """乌尔苏拉（第一代，撑起整个家）：蓝裙、围裙、发髻（老年花白）。"""
    draw_lady(c, x, y, s, "blue", hair="gray" if old else "bun", apron=True, **kw)


def melquiades(c, x, y, s, **kw):
    """吉卜赛人梅尔基亚德斯：宽檐黑帽、灰胡子、深色坎肩。"""
    kw.setdefault("beard", "gray")
    draw_man(c, x, y, s, "gray", hat="gypsy", vest="#3A3A3A", **kw)


def colonel(c, x, y, s, **kw):
    """奥雷里亚诺·布恩迪亚上校（第二代）：军帽、小胡子、蓝灰军装。"""
    kw.setdefault("beard", "mustache")
    kw.setdefault("hat", "kepi")
    draw_man(c, x, y, s, "blue", **kw)


def amaranta(c, x, y, s, **kw):
    """阿玛兰妲（第二代）：紫裙、发髻；左手缠黑纱布（烫伤之后）。"""
    draw_lady(c, x, y, s, "purple", hair="bun", **kw)


# ================================================================ 道具

def ice_block(c, x, y, w=220, h=170, T=0.0, alpha=1.0):
    """一块冰（斜 45° 的立方体）+ 冷气 + 闪光。(x, y) 为底面中心。"""
    d = w * 0.32
    front = skia.Rect.MakeXYWH(x - w / 2, y - h, w, h)
    top = P((x - w / 2, y - h), (x - w / 2 + d, y - h - d * 0.6), (x + w / 2 + d, y - h - d * 0.6), (x + w / 2, y - h), close=True)
    side = P((x + w / 2, y - h), (x + w / 2 + d, y - h - d * 0.6), (x + w / 2 + d, y - d * 0.6), (x + w / 2, y), close=True)
    for p_, col in ((top, "#EAF6FC"), (side, "#B9DBEE")):
        c.drawPath(p_, K.paint(col, alpha))
        c.drawPath(p_, wb.marker(ICE_LINE, 5, alpha))
    c.drawRect(front, K.paint(ICE, alpha))
    c.drawRect(front, wb.marker(ICE_LINE, 6, alpha))
    C.line(c, (x - w / 2 + 24, y - h + 30), (x - w / 2 + 60, y - h + 90), "#FFFFFF", 9, alpha)
    for q in range(3):
        f = ((T * 0.6) + q / 3) % 1
        xx = x - w / 3 + q * w / 3 + 14 * math.sin(T * 2 + q)
        c.drawCircle(xx, y - h - d * 0.6 - 30 - 120 * f, 16 + 14 * f, K.paint("#FFFFFF", 0.6 * (1 - f) * alpha))
        c.drawCircle(xx, y - h - d * 0.6 - 30 - 120 * f, 16 + 14 * f, wb.marker(ICE_LINE, 2, 0.4 * (1 - f) * alpha))


def magnet(c, x, y, s=1.0, rot=0.0, alpha=1.0):
    """马蹄形磁铁（红身灰头）。"""
    with K.at(c, x, y, rot, s):
        p = skia.Path()
        p.addArc(skia.Rect.MakeXYWH(-70, -70, 140, 140), 180, 180)
        c.drawPath(p, wb.marker(RED, 40, alpha))
        for sg in (-1, 1):
            c.drawRect(skia.Rect.MakeXYWH(sg * 70 - 20, 0, 40, 60), K.paint(RED, alpha))
            c.drawRect(skia.Rect.MakeXYWH(sg * 70 - 20, 60, 40, 34), K.paint("#C9CED6", alpha))
            c.drawRect(skia.Rect.MakeXYWH(sg * 70 - 20, 0, 40, 94), wb.marker(INK, 4, alpha))


def magnifier(c, x, y, s=1.0, rot=0.0, alpha=1.0):
    with K.at(c, x, y, rot, s):
        C.line(c, (40, 40), (120, 120), "#6E4E22", 22, alpha)
        c.drawCircle(0, 0, 62, K.paint("#E3F1FA", alpha))
        c.drawCircle(0, 0, 62, wb.marker(INK, 10, alpha))
        C.line(c, (-30, -20), (-10, -42), "#FFFFFF", 8, alpha)


def butterfly(c, x, y, s=1.0, T=0.0, alpha=1.0, color=BUTTER, rot=0.0):
    """黄蝴蝶（扇着翅膀）。"""
    f = 0.55 + 0.45 * abs(math.sin(T * 9))
    with K.at(c, x, y, rot, s):
        for sg in (-1, 1):
            c.save()
            c.scale(sg * f, 1)
            w1 = P((0, -4), (44, -46), (62, -10), (30, 8), close=True)
            w2 = P((0, 4), (40, 14), (34, 46), (8, 30), close=True)
            for w_ in (w1, w2):
                c.drawPath(w_, K.paint(color, alpha))
                c.drawPath(w_, wb.marker("#8A6A1A", 3, alpha))
            c.restore()
        C.line(c, (0, -20), (0, 26), INK, 6, alpha)
        C.line(c, (0, -20), (-12, -40), INK, 3, alpha)
        C.line(c, (0, -20), (12, -40), INK, 3, alpha)


def flower_rain(c, x0, x1, y0, y1, T, t0, n=60, alpha=1.0, seed=3):
    """黄花雨：小黄花从 y0 飘落到 y1，t0 起。"""
    if T < t0:
        return
    for i in range(n):
        r = (i * 9301 + seed * 49297) % 233280 / 233280
        r2 = (i * 7919 + seed * 104729) % 1000 / 1000
        x = x0 + (x1 - x0) * r
        sp = 0.25 + 0.2 * r2
        f = ((T - t0) * sp + r2) % 1
        if T - t0 < r2 / sp:
            continue
        yy = lerp(y0, y1, f)
        xx = x + 18 * math.sin((T - t0) * 2 + i)
        for q in range(5):
            ang = 2 * math.pi * q / 5 + i
            c.drawCircle(xx + 7 * math.cos(ang), yy + 7 * math.sin(ang), 5.5, K.paint(BUTTER, alpha))
        c.drawCircle(xx, yy, 3.5, K.paint("#C4861A", alpha))


def almond_tree(c, x, y, s=1.0, alpha=1.0):
    """杏仁树：(x, y) 为树根。"""
    with K.at(c, x, y, 0, s):
        trunk = P((-18, 0), (-12, -200), (12, -200), (18, 0), close=True)
        c.drawPath(trunk, K.paint("#8A6A3A", alpha))
        c.drawPath(trunk, wb.marker(INK, 4, alpha))
        for dx, dy, r in ((-80, -250, 90), (60, -270, 100), (0, -340, 100), (-20, -220, 80)):
            c.drawCircle(dx, dy, r, K.paint(LEAF, alpha))
            c.drawCircle(dx, dy, r, wb.marker(LEAF_LINE, 5, alpha))


def house(c, x, y, w=420, h=260, alpha=1.0, label=None):
    """马孔多的土坯房：(x, y) 为墙脚中点；坡屋顶、门、窗。"""
    body = skia.Rect.MakeXYWH(x - w / 2, y - h, w, h)
    c.drawRect(body, K.paint(ADOBE, alpha))
    c.drawRect(body, wb.marker(ADOBE_LINE, 6, alpha))
    roof = P((x - w / 2 - 40, y - h), (x, y - h - h * 0.55), (x + w / 2 + 40, y - h), close=True)
    c.drawPath(roof, K.paint("#B5562E", alpha))
    c.drawPath(roof, wb.marker(ADOBE_LINE, 6, alpha))
    c.drawRect(skia.Rect.MakeXYWH(x - 40, y - 150, 80, 150), K.paint("#6E4E22", alpha))
    for sg in (-1, 1):
        r = skia.Rect.MakeXYWH(x + sg * w * 0.3 - 40, y - h + 50, 80, 70)
        c.drawRect(r, K.paint("#F7EFD9", alpha))
        c.drawRect(r, wb.marker(ADOBE_LINE, 4, alpha))
    if label:
        K.text(c, label, x, y - h - h * 0.2, 44, "serif_black", "#FFFFFF", alpha)


def parchment(c, x, y, w, h, open_=1.0, alpha=1.0, lines=0):
    """羊皮卷：从上往下展开（open_ 0–1），上下两根卷轴。(x, y) 为中心。返回内容区 (左, 上, 右, 下)。"""
    hh = max(30.0, h * open_)
    top = y - h / 2
    r = skia.Rect.MakeXYWH(x - w / 2, top, w, hh)
    c.drawRect(r, K.paint(PARCH, alpha))
    c.drawRect(r, wb.marker(PARCH_LINE, 5, alpha))
    for yy in (top, top + hh):
        c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2 - 22, yy - 16, w + 44, 32), 14, 14, K.paint("#C9A46A", alpha))
        c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2 - 22, yy - 16, w + 44, 32), 14, 14, wb.marker(PARCH_LINE, 4, alpha))
    for i in range(lines):
        yy = top + 60 + i * 44
        if yy > top + hh - 30:
            break
        C.line(c, (x - w / 2 + 40, yy), (x + w / 2 - 40 - (i % 3) * 40, yy), "#B89766", 5, alpha)
    return x - w / 2 + 30, top + 20, x + w / 2 - 30, top + hh - 20


def name_tag(c, x, y, s, color=INK, size=40, a=1.0, sub=None):
    """头顶名牌：人名（一行），sub 为小字（辈分 / 身份）。"""
    w = max(K.text_w(s, size, "serif_black"), K.text_w(sub, size * 0.62, "sans_medium") if sub else 0) + 34
    h = size * (1.4 if not sub else 2.1)
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h), 10, 10, K.paint("#FFFFFF", 0.88 * a))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h), 10, 10, wb.marker(color, 4, a))
    if sub:
        K.text(c, s, x, y - size * 0.32, size, "serif_black", color, a)
        K.text(c, sub, x, y + size * 0.55, size * 0.62, "sans_medium", GRAY, a)
    else:
        K.text(c, s, x, y + 2, size, "serif_black", color, a)


def progress(c, x, y, w, frac, color=RED, a=1.0, h=26):
    """进度条：左端 (x - w/2)。"""
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h), h / 2, h / 2, K.paint("#FFFFFF", a))
    if frac > 0:
        c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, max(h, w * frac), h), h / 2, h / 2, K.paint(color, a))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h), h / 2, h / 2, wb.marker(BLACK, 4, a))


# ================================================================ 分镜常用件

class Kit(Z.Kit):
    """资治通鉴的分镜件（三步圆章 steps_row、评论区与下一讲 ending）+ 本系列的书框与书名。"""

    def gu_frame(self, j, k=0):
        """书中人的屏：羊皮卷底框，左上角一只黄蝴蝶，右下角“马孔多”小章。"""
        L, (cx, cy) = self.L, self.R[j]
        L.note("马孔多")
        fa = self.fa

        def fn(c, kk, T):
            sc = pop_scale(T - L.tb(j, k), 0.25)
            if sc <= 0:
                return None
            a = clamp01(sc)
            r = skia.Rect.MakeXYWH(cx - 580, cy - 585, 1160, 1215)
            c.drawRoundRect(r, 18, 18, K.paint(PARCH, fa * a))
            c.drawRoundRect(r, 18, 18, wb.marker(PARCH_LINE, 6, a))
            r2 = skia.Rect.MakeXYWH(cx - 562, cy - 567, 1124, 1179)
            c.drawRoundRect(r2, 12, 12, wb.marker(PARCH_LINE, 2.5, 0.8 * a))
            butterfly(c, cx - 500, cy - 505, 0.8, T, a, rot=-12)
            seal(c, cx + 480, cy + 540, "马孔多", 34, -4, 1.0, a)
            return None
        L.b.custom(j, k, k + 0.2, fn)

    def book(self, j, k, x=None, y=None, sub="范晔 译"):
        """书：封面“百年孤独 / 马尔克斯”，第 k 拍翻开（muyu）。"""
        L, (cx, cy) = self.L, self.R[j]
        x = cx - 330 if x is None else x
        y = cy - 230 if y is None else y
        L.note("百年孤独", "马尔克斯", sub)

        def fn(c, kk, T):
            sc = pop_scale(T - L.tb(j, k))
            if sc <= 0:
                return None
            with K.at(c, x, y, -4, sc):
                box(c, 0, 0, 300, 400, "#2F6B4F", "#1E3F2E", 7, 12)
                c.drawRect(skia.Rect.MakeXYWH(-150, -200, 26, 400), K.paint("#1E3F2E"))
                K.text(c, "百年", 10, -110, 76, "serif_black", BUTTER)
                K.text(c, "孤独", 10, -20, 76, "serif_black", BUTTER)
                K.text(c, "马尔克斯", 10, 80, 36, "sans_medium", "#FFFFFF")
                K.text(c, sub, 10, 140, 30, "sans_medium", "#DDE7DF")
                butterfly(c, 90, -170, 0.5, T)
            return None
        L.ev(j, k, fn, "muyu", 0.7, 0.4)
