"""科普动画短视频《为什么人会信星座？》：无旁白，黑金风格，全片按 BGM 实测拍点卡点。

流程：bgm.detect() 检测真实拍点 → CUES 把每个关键动作吸附到邻近的检测拍点 → 逐帧绘制竖屏 / 横屏两版
→ 合成打击乐音效轨，与配乐轻微闪避后混音 → 输出成片、封面、分轨、卡点表与文案资料。

用法：python3 zodiac.py [输出目录，默认 out/zodiac] [--only portrait|landscape] [--no-video]
"""

import csv
import math
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from multiprocessing import get_context
from pathlib import Path

import numpy as np
import skia
import soundfile as sf
from scipy import signal

from engine import audio, bgm, gfx, perc
from engine.gfx import clamp01, ease_in_out, ease_out, lerp

FPS = 30
BG = "#050505"
GOLD = "#D8BD8A"
GOLD_HI = "#F4DFB2"
GOLD_DIM = "#8A7550"
WHITE = "#F2ECE1"
MUTED = "#A59D90"
CLAY = "#6B5238"

# ---------------------------------------------------------------- 拍点

DET = bgm.detect()
BEATS = DET["beats"]
SECTIONS = DET["sections"]


def beat(ref: float, tol: float = 0.12) -> dict:
    """取离参考时刻最近的实测拍点；偏差超过 tol 说明分镜写错了拍点，直接报错而不是伪造。"""
    b = min(BEATS, key=lambda x: abs(x["t"] - ref))
    if abs(b["t"] - ref) > tol:
        raise ValueError(f"no detected beat near {ref:.2f}s (closest {b['t']:.2f}s)")
    return b


def accent(b: dict) -> float:
    """重音值：全频起音、低频（底鼓）起音、中高频（军鼓/拍手）起音取大者，后两者打 0.9 折。"""
    return max(b["strength"], 0.9 * b["low"], 0.9 * b["high"])


def level(b: dict) -> str:
    """重音强度分级：强 = 重音值 ≥0.85 且在第 1/3 拍或段落起点；中 = 重音值 ≥0.5；其余为弱。"""
    at_section = any(abs(b["t"] - s) < 0.05 for s in SECTIONS)
    if accent(b) >= 0.85 and (b["bar_pos"] in (0, 2) or at_section):
        return "强"
    return "中" if accent(b) >= 0.5 else "弱"


@dataclass
class Cue:
    ref: float
    scene: str
    action: str
    caption: str = ""
    sfx: str | None = None
    gain: float = 1.0
    hit: bool = False

    def __post_init__(self):
        self.b = beat(self.ref)
        self.t = self.b["t"]


C = Cue
CUES = [
    C(0.12, "开场钩子", "黑暗中金色星座卡淡入，星盘缓转"),
    C(1.18, "开场钩子", "第一行字幕上浮", "星座说的……", "shaker", 0.8),
    C(3.31, "开场钩子", "关键词落版（“像我”点金）", "怎么这么像我？", "kick", 0.85, True),
    C(4.38, "开场钩子", "十二张星座卡第 1 组飞出排列，镜头推进", "", "shaker", 0.7),
    C(4.91, "开场钩子", "第 2 组卡片入位"),
    C(5.45, "开场钩子", "第 3 组卡片入位，卡背隐约透出相同文字"),
    C(5.98, "开场钩子", "镜头推进停住"),
    C(6.51, "亲自体验", "描述一入场，出现 1 个人物轮廓", "你希望被理解，／但不会轻易暴露脆弱。", "shaker", 0.8),
    C(7.56, "亲自体验", "关键词“被理解”点亮"),
    C(8.63, "亲自体验", "关键词“脆弱”点亮，人物增至 3 个"),
    C(9.69, "亲自体验", "描述二入场", "你有时喜欢热闹，／有时也想独处。", "shaker", 0.8),
    C(10.76, "亲自体验", "关键词“热闹”点亮，人物增至 7 个"),
    C(12.89, "亲自体验", "停顿后关键词“独处”点亮，人物增至 15 个"),
    C(15.01, "亲自体验", "提问落版，之后不加新音效（留思考空间）", "你也觉得很准吗？"),
    C(17.14, "第一次反转", "音乐进入高能段：十二张卡同时翻面，背面是同一句描述", "", "rim", 1.0, True),
    C(20.33, "第一次反转", "大字落版", "同一句话，／也可能让很多人觉得准。"),
    C(21.39, "第一次反转", "第 1 组卡片汇入中央模板"),
    C(21.92, "第一次反转", "第 2 组卡片汇入"),
    C(22.45, "第一次反转", "第 3 组卡片汇入，合成同一个文本模板"),
    C(23.51, "第一次反转", "概念落版", "巴纳姆效应", "tom", 0.9, True),
    C(24.58, "第一次反转", "小字解释浮现", "把普遍、模糊的描述，／理解为特别符合自己。"),
    C(27.76, "实验依据", "金色时间轴延伸并停在 1949", "1949｜福勒的课堂实验", "wood_high", 0.9),
    C(28.83, "实验依据", "流程节点 1 点亮", "学生填写问卷", "wood_high", 0.8),
    C(29.90, "实验依据", "流程节点 2 点亮", "收到看似个人化的分析", "wood_high", 0.8),
    C(30.95, "实验依据", "流程节点 3 点亮", "多份报告展开", "wood_high", 0.8),
    C(32.02, "实验依据", "报告 1 展开"),
    C(32.55, "实验依据", "报告 2 展开"),
    C(33.08, "实验依据", "报告 3 展开"),
    C(33.61, "实验依据", "报告 4 展开"),
    C(34.14, "实验依据", "揭示“内容相同”：各报告同一段落被金线连起", "看似量身定制的报告，／其实给了大家相同的描述。",
      "kick", 0.75, True),
    C(36.27, "实验依据", "结论落版", "觉得准确，／不等于真的具有区分力。", "rim", 0.85, True),
    C(40.52, "历史缘由", "第二个钩子：卡片居中", "那星座，最初从哪里来？", "frame", 0.9, True),
    C(42.64, "历史缘由", "卡片变形为泥板（段落起点）", "今天的十二宫体系"),
    C(44.77, "历史缘由", "泥板展开为黄道圆环；第 1 组 3 个节点点亮", "有古代美索不达米亚的历史根源", "wood_low", 0.75),
    C(45.30, "历史缘由", "第 2 组节点点亮", "", "wood_low", 0.65),
    C(45.84, "历史缘由", "第 3 组节点点亮", "", "wood_low", 0.65),
    C(46.37, "历史缘由", "第 4 组节点点亮", "", "wood_low", 0.65),
    C(46.89, "历史缘由", "历史时间轴节点 1", "后来不断传播与演变"),
    C(47.96, "历史缘由", "历史时间轴节点 2"),
    C(49.02, "历史缘由", "历史时间轴节点 3"),
    C(50.09, "历史缘由", "收束字幕落版", "历史悠久，／并不等于预测有效。", "tom", 0.7, True),
    C(53.28, "确认偏误", "第三个钩子落版", "没说准的部分，／你还记得吗？", "cymbal", 0.7, True),
    C(55.40, "确认偏误", "“预测”与“经历”卡片散开", "我们可能更留意／支持原有想法的信息。", "shaker", 0.8),
    C(55.94, "确认偏误", "第 1 张相符卡片被金框选中", "", "wood_high", 0.75),
    C(56.99, "确认偏误", "第 2 张被选中", "", "wood_high", 0.75),
    C(57.53, "确认偏误", "第 3 张被选中", "", "wood_high", 0.75),
    C(58.58, "确认偏误", "第 4 张被选中", "", "wood_high", 0.75),
    C(59.65, "确认偏误", "不相符的卡片移到一旁（仍可见）", "对不符合的信息，／则容易忽略或另作解释。", "shaker", 0.8),
    C(61.78, "确认偏误", "概念揭示 + 信息筛选漏斗（机制示意）", "确认偏误", "clap", 0.9, True),
    C(66.03, "不止一种理由", "提问落版", "聊星座，就一定相信它吗？"),
    C(68.15, "不止一种理由", "圆形标签 1", "娱乐", "bongo_high", 0.8),
    C(69.22, "不止一种理由", "圆形标签 2（音乐短暂回落）", "社交话题", "bongo_low", 0.8),
    C(70.28, "不止一种理由", "圆形标签 3", "理解自己的语言", "bongo_high", 0.8),
    C(71.34, "不止一种理由", "三个圆连向人物群像，连线粗细各不相同", "不同的人，／投入程度和理由也不同。"),
    C(74.54, "小实验", "第四个钩子落版", "把星座名字遮住，／你还认得出“自己的那份”吗？", "cymbal", 0.6, True),
    C(75.59, "小实验", "三张性格卡入场", "", "shaker", 0.7),
    C(77.71, "小实验", "遮住星座标签", "", "rim", 0.85, True),
    C(78.77, "小实验", "打乱顺序（第 1 次交换）", "", "shaker", 0.7),
    C(79.83, "小实验", "打乱顺序（第 2 次交换）", "", "shaker", 0.6),
    C(80.90, "小实验", "选择时间开始（不加音效）；步骤 1", "先看描述，再看标签。"),
    C(81.97, "小实验", "步骤 2", "也记录不符合的部分。"),
    C(83.03, "小实验", "步骤 3", "检查它是否同样适合很多人。"),
    C(85.15, "收束", "收束第一句（段落起点）", "被说中的感觉，／值得再问一句："),
    C(87.28, "收束", "最后一句落版，星盘线条开始收拢成问号", "这句话，只适合我吗？", "kick", 0.6, True),
    C(87.30, "收束", "吊镲余韵", "", "cymbal", 0.45),
    C(89.41, "收束", "参考资料署名浮现，音乐最后一击后自然衰减"),
]
T = {round(c.ref, 2): c.t for c in CUES}


def at(ref: float) -> float:
    return T[round(ref, 2)]


MUSIC_END = 89.41 + 0.3
END = 92.6

# ---------------------------------------------------------------- 版式


@dataclass(frozen=True)
class Layout:
    """一版画幅的排版参数：portrait 为 1080×1920 竖屏，否则 1920×1080 横屏。"""
    w: int
    h: int

    @property
    def portrait(self) -> bool:
        return self.h > self.w

    @property
    def cx(self) -> float:
        return self.w / 2

    def P(self, portrait, landscape):
        return portrait if self.portrait else landscape


PORTRAIT = Layout(1080, 1920)
LANDSCAPE = Layout(1920, 1080)

# ---------------------------------------------------------------- 动画与绘图工具


def prog(t: float, t0: float, dur: float) -> float:
    return clamp01((t - t0) / dur) if dur > 0 else float(t >= t0)


def win(t: float, t0: float, t1: float, fin: float = 0.25, fout: float = 0.3) -> float:
    """[t0, t1] 内可见：t0 起 fin 秒淡入，t1 前 fout 秒淡出。"""
    if t < t0 or t > t1:
        return 0.0
    return min(prog(t, t0, fin), 1 - prog(t, t1 - fout, fout))


def paint(color, alpha: float = 1.0, stroke: float = 0.0, blur: float = 0.0, cap_round: bool = True) -> skia.Paint:
    p = skia.Paint(AntiAlias=True, Color=gfx.col(color, clamp01(alpha)))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        if cap_round:
            p.setStrokeCap(skia.Paint.kRound_Cap)
            p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


def line(c, x0, y0, x1, y1, color=GOLD, alpha=1.0, width=2.0, p=1.0, glow=0.0):
    if p <= 0 or alpha <= 0:
        return
    x1, y1 = lerp(x0, x1, p), lerp(y0, y1, p)
    if glow:
        c.drawLine(x0, y0, x1, y1, paint(color, alpha * 0.5, width * 3, glow))
    c.drawLine(x0, y0, x1, y1, paint(color, alpha, width))


def ring(c, x, y, r, color=GOLD, alpha=1.0, width=2.0, fill=None, fill_alpha=1.0, glow=0.0):
    if fill is not None:
        c.drawCircle(x, y, r, paint(fill, alpha * fill_alpha))
    if glow:
        c.drawCircle(x, y, r, paint(color, alpha * 0.45, width * 3, glow))
    if width:
        c.drawCircle(x, y, r, paint(color, alpha, width))


def rrect(c, x, y, w, h, r, color=GOLD, alpha=1.0, width=2.0, fill=None, fill_alpha=1.0, glow=0.0):
    rect = skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h)
    if fill is not None:
        c.drawRoundRect(rect, r, r, paint(fill, alpha * fill_alpha))
    if glow:
        c.drawRoundRect(rect, r, r, paint(color, alpha * 0.5, width * 3, glow))
    if width:
        c.drawRoundRect(rect, r, r, paint(color, alpha, width))


def text(c, s, x, y, size, font="serif", color=WHITE, alpha=1.0, align="center", glow=None):
    return gfx.draw_text(c, s, x, y, size, font, color, alpha, align, glow=glow)


def slam(t: float, t0: float, dur: float = 0.28) -> tuple[float, float]:
    """落版动画：返回 (透明度, 缩放)。前 0.1 秒淡入，缩放 1.14→1 带轻微回弹。"""
    if t < t0:
        return 0.0, 1.14
    k = prog(t, t0, dur)
    return prog(t, t0, 0.1), 1 + 0.14 * (1 - gfx.ease_out_back(k, 1.2))


def rise(t: float, t0: float, dur: float = 0.45) -> tuple[float, float]:
    """上浮入场：返回 (透明度, y 偏移)。"""
    k = ease_out(prog(t, t0, dur))
    return prog(t, t0, dur * 0.7), (1 - k) * 26


@dataclass
class Key:
    word: str
    t: float


def rich_line(c, s, x, y, size, font, t, keys=(), color=WHITE, alpha=1.0, align="center", hi=GOLD_HI):
    """单行文字，keys 中的关键词在各自时刻由暖白渐变为香槟金，并在下方画出延伸的金线。"""
    if alpha <= 0:
        return
    segs, rest = [], s
    for k in sorted(keys, key=lambda k: s.find(k.word)):
        i = rest.find(k.word)
        if i < 0:
            continue
        if i:
            segs.append((rest[:i], None))
        segs.append((k.word, k.t))
        rest = rest[i + len(k.word):]
    if rest:
        segs.append((rest, None))
    w = sum(gfx.text_width(p, size, font) for p, _ in segs)
    x0 = x - w / 2 if align == "center" else x
    for p, kt in segs:
        pw = gfx.text_width(p, size, font)
        if kt is None:
            text(c, p, x0, y, size, font, color, alpha, "left")
        else:
            lit = ease_out(prog(t, kt, 0.3))
            col = gfx.mix(color, hi, lit)
            text(c, p, x0, y, size, font, col, alpha, "left",
                 glow=(gfx.mix(BG, GOLD, 0.6), size * 0.18) if lit > 0.05 else None)
            line(c, x0, y + size * 0.62, x0 + pw, y + size * 0.62, GOLD, alpha * lit, max(2, size / 26), p=lit)
        x0 += pw


def block(c, lines, x, y, size, t, t0, t1, font="serif", keys=(), mode="slam", gap=1.42, color=WHITE,
          align="center", fin=0.12, fout=0.3):
    """多行文案块：[t0, t1] 可见，mode 为 slam（落版）或 rise（上浮）。y 为整块中心。"""
    a = win(t, t0, t1, fin, fout)
    if a <= 0:
        return
    if mode == "slam":
        a2, sc = slam(t, t0)
        dy = 0.0
    else:
        a2, dy = rise(t, t0)
        sc = 1.0
    a = min(a, a2)
    n = len(lines)
    c.save()
    c.translate(x, y + dy)
    c.scale(sc, sc)
    for i, ln in enumerate(lines):
        yy = (i - (n - 1) / 2) * size * gap
        rich_line(c, ln, 0, yy, size, font, t, keys, color, a, align)
    c.restore()


# ---------------------------------------------------------------- 图形元件

SIGNS = ["白羊座", "金牛座", "双子座", "巨蟹座", "狮子座", "处女座", "天秤座", "天蝎座", "射手座", "摩羯座", "水瓶座", "双鱼座"]
BARNUM = ["你希望被理解，", "但不会轻易", "暴露脆弱。"]


def _rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)


def constellation(c, cx, cy, s, seed, alpha=1.0, p=1.0):
    """装饰性星点连线（每个星座一种固定图案，仅作视觉符号）。"""
    r = _rng(seed + 40)
    n = 5 + seed % 3
    pts = [(cx + (r.random() - 0.5) * s, cy + (r.random() - 0.5) * s * 0.8) for _ in range(n)]
    pts.sort(key=lambda q: q[0])
    for i in range(n - 1):
        line(c, *pts[i], *pts[i + 1], GOLD, alpha * 0.7, max(1.2, s / 90), p=clamp01(p * (n - 1) - i))
    for i, (px, py) in enumerate(pts):
        ring(c, px, py, s / 34 if i % 3 else s / 24, GOLD_HI, alpha, 0, fill=GOLD_HI)


def card_quad(cx, cy, w, h, theta, focal=1800.0):
    """绕竖直轴旋转 theta 的卡片四角投影（透视）。"""
    pts = []
    for x, y in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)):
        xr, zr = x * math.cos(theta), x * math.sin(theta)
        k = focal / (focal + zr)
        pts.append(skia.Point(cx + xr * k, cy + y * k))
    return pts


def card(c, cx, cy, w, h, theta, front, back, alpha=1.0, scale=1.0, glow=0.0):
    """3D 翻转卡片：theta=0 正面朝前，theta=π 背面朝前；front/back(c, w, h, alpha) 在 (0,0)-(w,h) 局部坐标中绘制。"""
    if alpha <= 0:
        return
    w, h = w * scale, h * scale
    showing_back = math.cos(theta) < 0
    th = theta - math.pi if showing_back else theta
    m = skia.Matrix()
    src = [skia.Point(0, 0), skia.Point(w, 0), skia.Point(w, h), skia.Point(0, h)]
    if not m.setPolyToPoly(src, card_quad(cx, cy, w, h, th)):
        return
    c.save()
    c.concat(m)
    r = w * 0.07
    rect = skia.Rect.MakeWH(w, h)
    if glow:
        c.drawRoundRect(rect, r, r, paint(GOLD, alpha * glow * 0.5, 0, w * 0.08))
    c.drawRoundRect(rect, r, r, paint("#0D0B08", alpha))
    c.drawRoundRect(rect, r, r, paint(GOLD, alpha * 0.9, max(1.5, w / 110)))
    inset = skia.Rect.MakeXYWH(w * 0.05, w * 0.05, w * 0.9, h - w * 0.1)
    c.drawRoundRect(inset, r * 0.6, r * 0.6, paint(GOLD_DIM, alpha * 0.8, max(1, w / 220)))
    (back if showing_back else front)(c, w, h, alpha)
    c.restore()


def sign_front(i, hint=0.0):
    def draw(c, w, h, a):
        constellation(c, w / 2, h * 0.42, w * 0.55, i, a)
        text(c, SIGNS[i], w / 2, h * 0.8, w * 0.15, "serif", WHITE, a)
        if hint > 0:
            for k, s in enumerate(BARNUM):
                text(c, s, w / 2, h * (0.3 + 0.12 * k), w * 0.1, "serif_medium", GOLD_HI, a * hint * 0.35)
    return draw


def sign_back(i, label=True):
    def draw(c, w, h, a):
        if label:
            text(c, SIGNS[i], w / 2, h * 0.14, w * 0.1, "sans_medium", GOLD, a)
            line(c, w * 0.3, h * 0.21, w * 0.7, h * 0.21, GOLD_DIM, a, 1.2)
        for k, s in enumerate(BARNUM):
            text(c, s, w / 2, h * (0.42 + 0.14 * k), w * 0.115, "serif", WHITE, a)
    return draw


def template_back(c, w, h, a):
    text(c, "［任意星座］", w / 2, h * 0.14, w * 0.09, "sans_medium", GOLD, a)
    line(c, w * 0.3, h * 0.21, w * 0.7, h * 0.21, GOLD_DIM, a, 1.2)
    for k, s in enumerate(BARNUM):
        text(c, s, w / 2, h * (0.42 + 0.14 * k), w * 0.115, "serif", WHITE, a)


def person(c, x, y, s, alpha=1.0, color=WHITE, outline=False):
    """人物轮廓：头 + 肩部半椭圆。y 为脚底（肩部底边）。"""
    if alpha <= 0:
        return
    head = paint(color, alpha, s * 0.06 if outline else 0)
    c.drawCircle(x, y - s * 0.78, s * 0.2, head)
    body = skia.Path()
    body.addArc(skia.Rect.MakeXYWH(x - s * 0.36, y - s * 0.5, s * 0.72, s), 180, 180)
    body.close()
    c.drawPath(body, paint(color, alpha, s * 0.06 if outline else 0))


def crowd_slots(n, cx, cy, wmax, s):
    """n 个人物的排布：前后错落的多排，返回 [(x, y, 缩放)]。"""
    rng = _rng(7)
    out = []
    cols = 8
    for i in range(n):
        if i == 0:
            out.append((cx, cy, 1.0))
            continue
        row = i // cols
        k = i % cols
        x = cx + (k - (cols - 1) / 2) * wmax / cols + (rng.random() - 0.5) * s * 0.3
        y = cy + (row - 0.5) * s * 1.1 - (k % 2) * s * 0.25
        out.append((x, y, 0.7 + 0.25 * rng.random()))
    return out


def astrolabe(c, cx, cy, r, rot, alpha=1.0, tilt=1.0, nodes=None, labels=False, t=0.0):
    """星盘：三重圆环、12 等分辐线、72 个刻度；tilt<1 时纵向压缩呈 3D 倾斜。nodes 为 12 个节点的点亮程度。"""
    if alpha <= 0:
        return
    c.save()
    c.translate(cx, cy)
    c.scale(1, tilt)
    for rr, a, wd in ((r, 0.9, 2.2), (r * 0.86, 0.55, 1.4), (r * 0.62, 0.7, 1.6), (r * 0.2, 0.4, 1.2)):
        ring(c, 0, 0, rr, GOLD, alpha * a, wd / max(tilt, 0.3) ** 0.3)
    for k in range(72):
        ang = rot + k * math.tau / 72
        r0 = r * (0.94 if k % 6 else 0.86)
        line(c, r0 * math.cos(ang), r0 * math.sin(ang), r * math.cos(ang), r * math.sin(ang), GOLD,
             alpha * (0.8 if k % 6 == 0 else 0.4), 1.3)
    for k in range(12):
        ang = rot + k * math.tau / 12
        line(c, r * 0.62 * math.cos(ang), r * 0.62 * math.sin(ang), r * 0.86 * math.cos(ang), r * 0.86 * math.sin(ang),
             GOLD, alpha * 0.6, 1.3)
        mid = ang + math.tau / 24
        px, py = r * 0.74 * math.cos(mid), r * 0.74 * math.sin(mid)
        lit = nodes[k] if nodes is not None else 0.0
        ring(c, px, py, r * 0.022 * (1 + lit), GOLD_HI, alpha * (0.45 + 0.55 * lit), 0, fill=GOLD_HI)
        if lit > 0:
            ring(c, px, py, r * 0.05 * (1 + 0.6 * lit), GOLD_HI, alpha * lit * 0.6, 0, fill=GOLD_HI, fill_alpha=0.25)
        if labels:
            lx, ly = r * 1.13 * math.cos(mid), r * 1.13 * math.sin(mid)
            c.save()
            c.translate(lx, ly)
            c.scale(1, 1 / tilt)
            text(c, SIGNS[k], 0, 0, r * 0.075, "sans_medium", gfx.mix(MUTED, GOLD_HI, lit), alpha * (0.55 + 0.45 * lit))
            c.restore()
    for k in range(3):
        a0 = rot * 1.7 + k * 2.1
        line(c, 0, 0, r * 0.62 * math.cos(a0), r * 0.62 * math.sin(a0), GOLD_DIM, alpha * 0.6, 1.2)
    c.restore()


def stars(c, L, t, alpha=1.0, n=80):
    """稀疏暖色星点，缓慢漂移与闪烁。"""
    rng = _rng(3)
    xs, ys = rng.random(n), rng.random(n)
    ph, sz = rng.random(n) * math.tau, 0.6 + rng.random(n) * 1.8
    for i in range(n):
        a = alpha * (0.15 + 0.35 * (0.5 + 0.5 * math.sin(t * 0.9 + ph[i])))
        x = (xs[i] * L.w + t * 4 * (0.3 + sz[i])) % L.w
        c.drawCircle(x, ys[i] * L.h, sz[i], paint(WHITE if i % 4 else GOLD_HI, a))


def glow_bg(c, L, x, y, r, alpha):
    if alpha <= 0:
        return
    sh = skia.GradientShader.MakeRadial((x, y), r, [gfx.col("#3A2C17", alpha), gfx.col("#3A2C17", 0)])
    c.drawPaint(skia.Paint(Shader=sh))


# ---------------------------------------------------------------- 场景


def card_grid(L, n=12):
    """十二张卡的网格位置与卡片尺寸：竖屏 3 列 × 4 行，横屏 6 列 × 2 行。"""
    if L.portrait:
        cw, ch, cols, rows, gx, gy, cy = 196, 262, 3, 4, 34, 30, 1110
    else:
        cw, ch, cols, rows, gx, gy, cy = 196, 262, 6, 2, 34, 36, 640
    out = []
    for i in range(n):
        r, k = divmod(i, cols)
        x = L.cx + (k - (cols - 1) / 2) * (cw + gx)
        y = cy + (r - (rows - 1) / 2) * (ch + gy)
        out.append((x, y))
    return out, cw, ch


def s_hook(c, L, t):
    t_card, t1, t2, g1, cam_stop = at(0.12), at(1.18), at(3.31), at(4.38), at(5.98)
    end = at(6.51)
    a_scene = 1 - prog(t, end - 0.3, 0.3)
    slots, cw, ch = card_grid(L)
    big_w, big_h = L.P((380, 508), (330, 440))
    center = (L.cx, L.P(1090, 620))
    cam = 1 + 0.08 * ease_out(prog(t, g1, cam_stop - g1))
    c.save()
    c.translate(L.cx, L.h / 2)
    c.scale(cam, cam)
    c.translate(-L.cx, -L.h / 2)
    glow_bg(c, L, center[0], center[1], L.P(700, 600), 0.9 * a_scene * prog(t, t_card, 1.0))
    rot = math.radians(-6 + 10 * ease_in_out(prog(t, 0, 6.5)))
    astrolabe(c, center[0], center[1], L.P(470, 420), rot, 0.45 * a_scene * prog(t, t_card, 1.2), tilt=0.92)
    groups = [g1, at(4.91), at(5.45)]
    order = [4, 0, 8, 2, 6, 10, 1, 5, 9, 3, 7, 11]
    hint = 0.6 * prog(t, at(5.45), 0.6)
    for j, i in enumerate(order):
        gt = groups[j // 4] + (j % 4) * 0.04
        k = ease_out(prog(t, gt, 0.42))
        if j == 0:
            k = ease_in_out(prog(t, g1 - 0.05, 0.5))
            x, y = lerp(center[0], slots[i][0], k), lerp(center[1], slots[i][1], k)
            sc = lerp(big_w / cw, 1.0, k)
            a = prog(t, t_card, 0.7)
            sweep = prog(t, t_card + 0.2, 1.2)
            card(c, x, y, cw, ch, math.radians(8 * (1 - k)) * math.sin(t * 1.3), sign_front(i, hint), sign_back(i),
                 a * a_scene, sc, glow=0.6 * (1 - abs(2 * sweep - 1)))
        elif t >= gt:
            x, y = lerp(center[0], slots[i][0], k), lerp(center[1], slots[i][1], k)
            card(c, x, y, cw, ch, math.radians(25 * (1 - k)), sign_front(i, hint), sign_back(i),
                 prog(t, gt, 0.15) * a_scene, lerp(0.6, 1.0, k))
    c.restore()
    ty = L.P(250, 150)
    gap = L.P(115, 100)
    size = L.P(72, 64)
    a1, dy = rise(t, t1)
    text(c, "星座说的……", L.cx, ty + dy, size * 0.8, "serif_medium", WHITE, a1 * a_scene)
    block(c, ["怎么这么像我？"], L.cx, ty + gap, size, t, t2, end, keys=[Key("像我", t2)])


def s_experience(c, L, t):
    t0, k1, k2, t3, k3, k4, tq, end = (at(x) for x in (6.51, 7.56, 8.63, 9.69, 10.76, 12.89, 15.01, 17.14))
    ty = L.P(560, 300)
    size = L.P(70, 64)
    gap_y = L.P(1.45, 1.4)
    fw, fh = L.P((900, 330), (1200, 270))
    fa = win(t, t0, tq + 0.1, 0.35, 0.3)
    if fa > 0:
        x0, y0, x1, y1 = L.cx - fw / 2, ty - fh / 2, L.cx + fw / 2, ty + fh / 2
        arm = 46
        for (px, py, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
            line(c, px, py, px + sx * arm, py, GOLD, fa * 0.8, 2, p=ease_out(prog(t, t0, 0.5)))
            line(c, px, py, px, py + sy * arm, GOLD, fa * 0.8, 2, p=ease_out(prog(t, t0, 0.5)))
        text(c, "一段描述", L.cx, y0 - 2, L.P(26, 24), "sans", GOLD_DIM, fa * 0.9)
    block(c, ["你希望被理解，", "但不会轻易暴露脆弱。"], L.cx, ty, size, t, t0, t3, keys=[Key("被理解", k1), Key("脆弱", k2)],
          mode="rise", gap=gap_y, fin=0.3)
    block(c, ["你有时喜欢热闹，", "有时也想独处。"], L.cx, ty, size, t, t3, tq, keys=[Key("热闹", k3), Key("独处", k4)],
          mode="rise", gap=gap_y, fin=0.3)
    block(c, ["你也觉得很准吗？"], L.cx, ty, L.P(84, 76), t, tq, end, mode="slam", fout=0.2)
    counts = [(t0, 1), (k2, 3), (k3, 7), (k4, 15)]
    n = max([m for tt, m in counts if t >= tt] or [0])
    ps = L.P(118, 92)
    slots = crowd_slots(15, L.cx, L.P(1330, 800), L.P(940, 1500), ps)
    a_out = 1 - prog(t, end - 0.25, 0.25)
    for i in range(n):
        born = min(tt for tt, m in counts if m > i)
        k = gfx.ease_out_back(prog(t, born + (i % 8) * 0.03, 0.35))
        x, y, s = slots[i]
        person(c, x, y, ps * s * k, a_out * (0.95 if i == 0 else 0.55) * prog(t, born, 0.15),
               WHITE if i == 0 else GOLD, outline=i != 0)


def s_reversal(c, L, t):
    t_flip, t_title, m1, m2, m3, t_key, t_exp, end = (at(x) for x in (17.14, 20.33, 21.39, 21.92, 22.45, 23.51,
                                                                       24.58, 27.76))
    slots, cw, ch = card_grid(L)
    a_in = prog(t, t_flip - 0.3, 0.25)
    a_out = 1 - prog(t, end - 0.3, 0.3)
    flip = ease_out(prog(t, t_flip, 0.42))
    shrink = ease_in_out(prog(t, t_title - 0.1, 0.5))
    groups = [m1, m2, m3]
    tw, th = L.P((430, 575), (330, 440))
    tpl = (L.cx, L.P(1060, 640))
    if t >= t_key:
        tpl = (L.cx, lerp(tpl[1], L.P(1120, 610), ease_in_out(prog(t, t_key, 0.5))))
    merged = ease_in_out(prog(t, m3, 0.45))
    glow_bg(c, L, tpl[0], tpl[1], L.P(650, 520), 0.7 * a_out * a_in)
    for i in range(12):
        g = groups[i % 3]
        k = ease_in_out(prog(t, g, 0.45))
        x0, y0 = slots[i]
        cy0 = lerp(y0, L.P(1080, 650) + (y0 - L.P(1080, 650)) * 0.86, shrink)
        x0 = lerp(x0, L.cx + (x0 - L.cx) * 0.9, shrink)
        x, y = lerp(x0, tpl[0], k), lerp(cy0, tpl[1], k)
        sc = lerp(lerp(1, 0.9, shrink), tw / cw, k)
        a = a_in * a_out * (1 - merged if k >= 1 else 1)
        card(c, x, y, cw, ch, math.pi * flip + math.radians(6) * (1 - k) * math.sin(t * 2 + i), sign_front(i),
             sign_back(i), a, sc)
    if merged > 0:
        card(c, tpl[0], tpl[1], tw, th, math.pi, sign_front(0), template_back, merged * a_out, 1.0, glow=0.5 * merged)
    block(c, ["同一句话，", "也可能让很多人觉得准。"], L.cx, L.P(330, 150), L.P(70, 60), t, t_title, t_key, keys=[
        Key("很多人", t_title + 0.35)], gap=1.4)
    ka, ks = slam(t, t_key)
    a = win(t, t_key, end, 0.1, 0.3) * ka
    c.save()
    c.translate(L.cx, L.P(330, 140))
    c.scale(ks, ks)
    text(c, "巴纳姆效应", 0, 0, L.P(116, 96), "serif_black", GOLD_HI, a, glow=(GOLD_DIM, 26))
    text(c, "BARNUM EFFECT", 0, L.P(96, 80), L.P(28, 24), "sans_medium", GOLD_DIM, a)
    c.restore()
    block(c, ["把普遍、模糊的描述，", "理解为特别符合自己。"], L.cx, L.P(1600, 935), L.P(46, 40), t, t_exp, end,
          font="serif_medium", mode="rise", color=WHITE, keys=[Key("普遍、模糊", t_exp + 0.6), Key("特别符合自己", t_exp + 1.1)])


def report(c, x, y, w, h, alpha, hi=0.0, n_id=0):
    """一份“个性分析报告”：顶部编号 + 若干文本行，hi>0 时其中的共同段落被金色描亮。"""
    if alpha <= 0:
        return
    rrect(c, x, y, w, h, 10, GOLD, alpha, 1.6, fill="#0F0D0A")
    text(c, f"个性分析 · No.{n_id:02d}", x, y - h * 0.38, w * 0.085, "sans_medium", GOLD, alpha)
    for k in range(6):
        ly = y - h * 0.2 + k * h * 0.11
        lw = w * (0.72 if k % 3 == 2 else 0.8)
        common = 1 <= k <= 3
        col = gfx.mix(MUTED, GOLD_HI, hi) if common else MUTED
        line(c, x - w * 0.4, ly, x - w * 0.4 + lw, ly, col, alpha * (0.6 + 0.4 * hi * common), max(2, w / 70))


def flow_icon(c, kind, x, y, s, alpha, lit):
    col = gfx.mix(GOLD_DIM, GOLD_HI, lit)
    ring(c, x, y, s, col, alpha, 2, fill="#0D0B08", glow=8 * lit)
    if kind == 0:
        rrect(c, x, y + s * 0.05, s * 0.8, s * 1.0, 5, col, alpha, 1.6)
        for k in range(3):
            line(c, x - s * 0.25, y - s * 0.2 + k * s * 0.25, x + s * 0.25, y - s * 0.2 + k * s * 0.25, col, alpha, 1.6)
    elif kind == 1:
        rrect(c, x, y, s * 0.95, s * 0.68, 4, col, alpha, 1.6)
        line(c, x - s * 0.47, y - s * 0.34, x, y + s * 0.05, col, alpha, 1.6)
        line(c, x + s * 0.47, y - s * 0.34, x, y + s * 0.05, col, alpha, 1.6)
    else:
        for k in range(3):
            rrect(c, x - s * 0.15 + k * s * 0.15, y - s * 0.12 + k * s * 0.12, s * 0.6, s * 0.8, 4, col, alpha, 1.4,
                  fill="#0D0B08")


def s_forer(c, L, t):
    t0, n1, n2, n3 = at(27.76), at(28.83), at(29.90), at(30.95)
    fans = [at(32.02), at(32.55), at(33.08), at(33.61)]
    t_same, t_conc, end = at(34.14), at(36.27), at(40.52)
    a_out = 1 - prog(t, end - 0.3, 0.3)
    ty = L.P(250, 120)
    span = L.P(860, 1500)
    x0 = L.cx - span / 2
    p_line = ease_out(prog(t, t0 - 0.2, 0.9))
    line(c, x0, ty, x0 + span, ty, GOLD_DIM, a_out, 2, p=p_line)
    years = [1900, 1925, 1949, 1975, 2000]
    for k, yv in enumerate(years):
        x = x0 + span * k / (len(years) - 1)
        a = a_out * prog(t, t0 - 0.2 + 0.18 * k, 0.2)
        line(c, x, ty - 10, x, ty + 10, GOLD_DIM, a, 2)
        if yv != 1949:
            text(c, str(yv), x, ty + 34, L.P(22, 22), "sans", MUTED, a * 0.8)
    mx = x0 + span * 0.5
    k = ease_out(prog(t, t0, 0.35))
    ring(c, mx, ty, 12 * k, GOLD_HI, a_out, 0, fill=GOLD_HI)
    ring(c, mx, ty, 26 * k, GOLD_HI, a_out * 0.5 * k, 1.5)
    block(c, ["1949｜福勒的课堂实验"], L.cx, ty + L.P(90, 80), L.P(54, 50), t, t0, end, mode="slam",
          keys=[Key("1949", t0)])
    conc = ease_in_out(prog(t, t_conc, 0.5))
    nodes = [(n1, "学生填写问卷"), (n2, "收到看似个人化的分析"), (n3, "多份报告展开")]
    ny = L.P(560, 380)
    nx = [L.cx - L.P(330, 520), L.cx, L.cx + L.P(330, 520)]
    na = a_out * (1 - conc)
    for i, (nt, label) in enumerate(nodes):
        a = na * prog(t, nt, 0.2)
        if a <= 0:
            continue
        lit = 1 - 0.6 * prog(t, nt + 0.5, 0.5)
        if i:
            line(c, nx[i - 1] + 60, ny, nx[i] - 60, ny, GOLD, a, 2, p=ease_out(prog(t, nt - 0.1, 0.3)))
        flow_icon(c, i, nx[i], ny, L.P(46, 44), a, lit)
        if L.portrait and len(label) > 6:
            text(c, label[:5], nx[i], ny + 92, 30, "sans_medium", WHITE, a)
            text(c, label[5:], nx[i], ny + 132, 30, "sans_medium", WHITE, a)
        else:
            text(c, label, nx[i], ny + L.P(92, 86), L.P(30, 30), "sans_medium", WHITE, a)
    rw, rh = L.P((200, 280), (210, 260))
    ry = L.P(1060, 640)
    ry = lerp(ry, L.P(800, 520), conc)
    spread = [(-1.5, -6), (-0.5, -2), (0.5, 2), (1.5, 6)]
    gapx = L.P(230, 270)
    hi = ease_out(prog(t, t_same, 0.4))
    for i, ft in enumerate(fans):
        k = ease_out(prog(t, ft, 0.35))
        if t < ft:
            continue
        x = lerp(nx[2], L.cx + spread[i][0] * gapx, k)
        y = lerp(ny, ry, k)
        c.save()
        c.translate(x, y)
        c.rotate(spread[i][1] * (1 - hi * 0.7))
        report(c, 0, 0, rw * lerp(0.4, 1, k), rh * lerp(0.4, 1, k), a_out * prog(t, ft, 0.15) * (1 - 0.65 * conc),
               hi, [7, 23, 41, 58][i])
        c.restore()
    if hi > 0:
        for k in range(1, 4):
            ly = ry - rh * 0.2 + k * rh * 0.11
            line(c, L.cx - 1.5 * gapx - rw * 0.4, ly, L.cx + 1.5 * gapx + rw * 0.3, ly, GOLD_HI,
                 a_out * 0.5 * (1 - 0.7 * conc), 1.4, p=hi)
        ka, ks = slam(t, t_same)
        c.save()
        c.translate(L.cx, ry + rh * 0.5 + L.P(70, 42))
        c.scale(ks, ks)
        text(c, "内容相同", 0, 0, L.P(52, 46), "serif", GOLD_HI, ka * a_out * (1 - conc), glow=(GOLD_DIM, 16))
        c.restore()
    block(c, ["看似量身定制的报告，", "其实给了大家相同的描述。"], L.cx, L.P(1560, 932), L.P(46, 40), t, t_same, end,
          font="serif_medium", mode="rise", keys=[Key("相同的描述", t_same + 0.4)])
    block(c, ["觉得准确，", "不等于真的具有区分力。"], L.cx, L.P(1200, 745), L.P(72, 64), t, t_conc, end,
          keys=[Key("区分力", t_conc + 0.45)])
    text(c, "注：一次课堂演示，不能解释所有人为什么会信星座", L.cx, L.P(1760, 1022), L.P(24, 22), "sans", MUTED,
         win(t, t_conc, end) * 0.9)


def tablet(c, x, y, w, h, alpha, marks=1.0, seed=5):
    """泥板（示意）：圆角土色板面 + 逐渐刻出的楔形纹样（装饰，不代表真实文字）。"""
    if alpha <= 0:
        return
    rrect(c, x, y, w, h, w * 0.12, GOLD_DIM, alpha, 2, fill=CLAY, fill_alpha=0.55)
    rng = _rng(seed)
    rows = 7
    for r in range(rows):
        yy = y - h * 0.36 + r * h * 0.72 / (rows - 1)
        line(c, x - w * 0.4, yy + h * 0.05, x + w * 0.4, yy + h * 0.05, "#2A2016", alpha * 0.5, 1)
        for k in range(6):
            if (r * 6 + k) / (rows * 6) > marks:
                break
            xx = x - w * 0.36 + k * w * 0.14 + rng.random() * w * 0.03
            s = w * (0.03 + 0.02 * rng.random())
            path = skia.Path()
            path.moveTo(xx, yy - s)
            path.lineTo(xx + s * 0.7, yy)
            path.lineTo(xx, yy + s * 0.3)
            path.close()
            c.drawPath(path, paint(GOLD_HI, alpha * 0.75))
            line(c, xx + s * 0.4, yy, xx + s * 1.6, yy, GOLD_HI, alpha * 0.5, 1.2)


def s_history(c, L, t):
    t0, t_tab, t_ring = at(40.52), at(42.64), at(44.77)
    groups = [at(44.77), at(45.30), at(45.84), at(46.37)]
    tl = [at(46.89), at(47.96), at(49.02)]
    t_close, end = at(50.09), at(53.28)
    a_out = 1 - prog(t, end - 0.3, 0.3)
    ccx, ccy = L.P((L.cx, 880), (600, 560))
    R = L.P(310, 300)
    glow_bg(c, L, ccx, ccy, R * 2, 0.6 * a_out)
    morph1 = ease_in_out(prog(t, t_tab - 0.05, 0.6))
    morph2 = ease_in_out(prog(t, t_ring - 0.05, 0.7))
    cw, chh = L.P((300, 400), (270, 360))
    if morph1 < 1:
        a = prog(t, t0, 0.3) * (1 - morph1)
        card(c, lerp(L.cx, ccx, morph1), lerp(L.P(1150, 720), ccy, morph1), cw, chh,
             math.radians(10 * math.sin(t * 1.4)), sign_front(4), sign_back(4), a, 1.0)
    if morph1 > 0 and morph2 < 1:
        tablet(c, ccx, ccy, lerp(cw, R * 1.1, morph1), lerp(chh, R * 1.4, morph1), a_out * morph1 * (1 - morph2),
               marks=prog(t, t_tab, 1.6))
    if morph2 > 0:
        nodes = []
        for k in range(12):
            g = groups[k // 3]
            nodes.append(ease_out(prog(t, g, 0.25)) * (1 - 0.55 * prog(t, g + 0.6, 0.6)))
        sc = lerp(0.4, 1.0, morph2)
        astrolabe(c, ccx, ccy, R * sc, math.radians(-90 - 15) + 0.02 * (t - t_ring), a_out * morph2 *
                  (1 - 0.6 * prog(t, t_close, 0.5)), tilt=lerp(1.0, 0.94, morph2), nodes=nodes, labels=True)
    block(c, ["那星座，最初从哪里来？"], L.cx, L.P(560, 300), L.P(74, 66), t, t0, t_tab, fout=0.25)
    if L.portrait:
        cap_x, cap_y, align = L.cx, 330, "center"
    else:
        cap_x, cap_y, align = 1060, 230, "left"
    size = L.P(52, 46)
    a12 = win(t, t_tab, tl[0], 0.25, 0.3)
    a1, d1 = rise(t, t_tab)
    a2, d2 = rise(t, t_ring)
    text(c, "今天的十二宫体系", cap_x, cap_y + d1 - L.P(40, 36), size, "serif", WHITE, a12 * a1, align)
    rich_line(c, "有古代美索不达米亚的历史根源", cap_x, cap_y + d2 + L.P(40, 36), size, "serif", t,
              [Key("美索不达米亚", t_ring + 0.3)], WHITE, a12 * a2, align)
    block(c, ["后来不断传播与演变"], cap_x if L.portrait else cap_x + gfx.text_width("后来不断传播与演变", size, "serif") / 2,
          cap_y, size, t, tl[0], t_close, mode="rise", fin=0.3)
    items = [("约公元前 5 世纪", "巴比伦：黄道分为十二等份"), ("约公元前 2—1 世纪", "希腊化时期：本命盘占星成形"),
             ("20 世纪 30 年代起", "报刊“太阳星座”专栏流行")]
    if L.portrait:
        bx, by, step = 190, 1320, 118
    else:
        bx, by, step = 1080, 470, 128
    ta = win(t, tl[0], end, 0.25, 0.3) * (1 - 0.5 * prog(t, t_close, 0.4))
    if ta > 0:
        line(c, bx, by - 30, bx, by + step * 2 + 30, GOLD_DIM, ta, 2, p=ease_out(prog(t, tl[0], 2.4)))
    for i, (when, what) in enumerate(items):
        a = ta * prog(t, tl[i], 0.25)
        if a <= 0:
            continue
        y = by + i * step
        ring(c, bx, y, 9, GOLD_HI, a, 0, fill=GOLD_HI)
        ring(c, bx, y, 18 * (1 - 0.5 * prog(t, tl[i] + 0.3, 0.5)), GOLD_HI, a * 0.6, 1.4)
        text(c, when, bx + 36, y - L.P(20, 20), L.P(28, 26), "sans_medium", GOLD, a, "left")
        text(c, what, bx + 36, y + L.P(22, 22), L.P(36, 34), "serif_medium", WHITE, a, "left")
    block(c, ["历史悠久，", "并不等于预测有效。"], L.cx if L.portrait else 1340, L.P(330, 300), L.P(66, 60), t,
          t_close, end, keys=[Key("预测有效", t_close + 0.4)])
    text(c, "天文学研究天体本身；占星术用天象解读人事——二者不同", L.cx, L.P(1760, 1022), L.P(26, 24), "sans", MUTED,
         win(t, tl[0], end) * 0.95)


EXPERIENCES = [("被朋友夸奖", True), ("一切如常", False), ("有点累", True), ("没遇到惊喜", False),
               ("遇到小惊喜", True), ("睡得很好", False), ("收到好消息", True), ("心情平静", False)]


def s_confirm(c, L, t):
    t0, t_cards, t_aside, t_key, end = at(53.28), at(55.40), at(59.65), at(61.78), at(66.03)
    sel = [at(55.94), at(56.99), at(57.53), at(58.58)]
    a_out = 1 - prog(t, end - 0.3, 0.3)
    block(c, ["没说准的部分，", "你还记得吗？"], L.cx, L.P(860, 520), L.P(78, 70), t, t0, t_cards + 0.1,
          keys=[Key("没说准", t0 + 0.3)], fout=0.25)
    pa = win(t, t_cards, t_key + 0.2, 0.3, 0.3)
    if pa > 0:
        py = L.P(300, 140)
        rrect(c, L.cx, py, L.P(760, 900), L.P(110, 96), 14, GOLD, pa, 1.8, fill="#0F0D0A")
        text(c, "预测：本周会有小惊喜，也可能有点累", L.cx, py, L.P(36, 34), "serif_medium", GOLD_HI, pa)
    if L.portrait:
        cols, cw, chh, gx, gy, cy0 = 2, 380, 120, 40, 34, 880
    else:
        cols, cw, chh, gx, gy, cy0 = 4, 330, 120, 36, 40, 470
    rows = len(EXPERIENCES) // cols
    funnel_k = ease_in_out(prog(t, t_key, 0.8))
    fx, fy = L.P((L.cx, 980), (760, 600))
    aside_k = ease_in_out(prog(t, t_aside, 0.6))
    matched = [i for i, (_, m) in enumerate(EXPERIENCES) if m]
    unmatched = [i for i, (_, m) in enumerate(EXPERIENCES) if not m]
    if funnel_k > 0:
        fa = a_out * funnel_k
        top, bot, hgt = L.P(560, 520), L.P(120, 110), L.P(520, 400)
        y0 = fy - hgt / 2
        path = skia.Path()
        path.moveTo(fx - top / 2, y0)
        path.lineTo(fx - bot / 2, y0 + hgt * 0.75)
        path.lineTo(fx - bot / 2, y0 + hgt)
        path.moveTo(fx + top / 2, y0)
        path.lineTo(fx + bot / 2, y0 + hgt * 0.75)
        path.lineTo(fx + bot / 2, y0 + hgt)
        c.drawPath(path, paint(GOLD, fa, 2.4))
        c.drawPath(path, paint(GOLD, fa * 0.4, 7, 6))
        line(c, fx - top / 2, y0, fx + top / 2, y0, GOLD_DIM, fa * 0.6, 1.4)
        text(c, "被记住的“准”", fx, y0 + hgt + L.P(44, 40), L.P(34, 32), "serif", GOLD_HI, fa)
        rrect(c, fx + top / 2 - L.P(60, 60), y0 - L.P(40, 36), L.P(120, 110), 38, 19, GOLD_DIM, fa, 1.4)
        text(c, "机制示意", fx + top / 2 - L.P(60, 60), y0 - L.P(40, 36), L.P(22, 20), "sans_medium", GOLD, fa)
    for idx, (label, ok) in enumerate(EXPERIENCES):
        r, k = divmod(idx, cols)
        gx0 = L.cx - (cols - 1) / 2 * (cw + gx) if L.portrait else 760 - (cols - 1) / 2 * (cw + gx)
        x = gx0 + k * (cw + gx)
        y = cy0 + (r - (rows - 1) / 2) * (chh + gy)
        appear = ease_out(prog(t, t_cards + idx * 0.05, 0.4))
        if appear <= 0:
            continue
        lit = 0.0
        if ok:
            j = matched.index(idx)
            lit = ease_out(prog(t, sel[j], 0.2))
            if funnel_k > 0:
                step = chh * 0.7 + 12
                x = lerp(x, fx, funnel_k)
                y = lerp(y, fy - L.P(200, 150) + j * step - 1.5 * step + L.P(60, 40), funnel_k)
        else:
            j = unmatched.index(idx)
            if L.portrait:
                ax, ay = 140 + j * 267, 1440
            else:
                ax, ay = 1610, 300 + j * 135
            x, y = lerp(x, ax, aside_k), lerp(y, ay, aside_k)
        sc = lerp(1.0, 0.7, funnel_k)
        if not ok:
            sc = lerp(1.0, L.P(0.62, 0.78), aside_k)
        a = a_out * appear * (1 - 0.45 * aside_k * (not ok))
        w_, h_ = cw * sc, chh * sc
        rrect(c, x, y + (1 - appear) * 30, w_, h_, 12, gfx.mix(GOLD_DIM, GOLD_HI, lit), a,
              1.5 + 2 * lit, fill="#0E0C09", glow=10 * lit)
        text(c, "经历", x - w_ / 2 + 18 * sc, y - h_ * 0.22, 20 * sc, "sans", MUTED, a, "left")
        text(c, label, x, y + h_ * 0.12, L.P(40, 36) * sc, "serif_medium", gfx.mix(WHITE, GOLD_HI, lit), a)
        if lit > 0:
            gfx.check(c, x + w_ / 2 - 26 * sc, y - h_ / 2 + 24 * sc, 26 * sc, lit, GOLD_HI, 4 * sc, a)
    if aside_k > 0:
        if L.portrait:
            text(c, "仍然发生过，只是容易被略过", L.cx, 1350, 28, "sans", MUTED, a_out * aside_k)
        else:
            text(c, "仍然发生过", 1610, 220, 26, "sans", MUTED, a_out * aside_k)
    ka, ks = slam(t, t_key)
    a = win(t, t_key, end, 0.1, 0.3) * ka
    if a > 0:
        c.save()
        c.translate(L.cx if L.portrait else 760, L.P(300, 150))
        c.scale(ks, ks)
        text(c, "确认偏误", 0, 0, L.P(110, 92), "serif_black", GOLD_HI, a, glow=(GOLD_DIM, 26))
        text(c, "CONFIRMATION BIAS", 0, L.P(92, 76), L.P(26, 22), "sans_medium", GOLD_DIM, a)
        c.restore()
    cap_y = L.P(1640, 970)
    block(c, ["我们可能更留意", "支持原有想法的信息。"], L.cx, cap_y, L.P(48, 42), t, t_cards, t_aside, font="serif_medium",
          mode="rise", keys=[Key("支持原有想法", t_cards + 0.6)])
    block(c, ["对不符合的信息，", "则容易忽略或另作解释。"], L.cx, cap_y, L.P(48, 42), t, t_aside, end, font="serif_medium",
          mode="rise", keys=[Key("忽略或另作解释", t_aside + 0.6)])


def s_social(c, L, t):
    t0 = at(66.03)
    nodes = [at(68.15), at(69.22), at(70.28)]
    t_link, end = at(71.34), at(74.54)
    a_out = 1 - prog(t, end - 0.3, 0.3)
    block(c, ["聊星座，就一定相信它吗？"], L.cx, L.P(330, 140), L.P(66, 60), t, t0, end, keys=[Key("相信", t0 + 0.4)])
    labels = [["娱乐"], ["社交话题"], ["理解自己", "的语言"]]
    if L.portrait:
        pos = [(250, 760), (830, 760), (540, 1040)]
        r = 150
    else:
        pos = [(560, 430), (960, 430), (1360, 430)]
        r = 140
    crowd_y = L.P(1500, 860)
    people = [(L.cx + (k - 4.5) * L.P(96, 150), crowd_y + (k % 2) * L.P(40, 30)) for k in range(10)]
    links = [(0, 0, 1.0), (0, 3, 0.4), (1, 1, 0.8), (1, 4, 1.0), (1, 6, 0.5), (2, 2, 0.6), (2, 5, 1.0), (0, 7, 0.7),
             (2, 8, 0.3), (1, 9, 0.6)]
    lk = ease_out(prog(t, t_link, 0.8))
    for j, (ni, pi, wgt) in enumerate(links):
        if lk <= 0:
            break
        x0, y0 = pos[ni]
        x1, y1 = people[pi]
        line(c, x0, y0 + r, x1, y1 - L.P(120, 110), GOLD, a_out * (0.25 + 0.5 * wgt), 1 + 3 * wgt,
             p=clamp01(lk * 1.6 - j * 0.06))
    for k, (x, y) in enumerate(people):
        a = a_out * prog(t, t_link + k * 0.04, 0.3)
        person(c, x, y, L.P(82, 88), a * 0.8, GOLD if k % 3 else WHITE, outline=k % 3 != 0)
    for i, ((x, y), lab) in enumerate(zip(pos, labels)):
        k = gfx.ease_out_back(prog(t, nodes[i], 0.4), 1.4)
        a = a_out * prog(t, nodes[i], 0.15)
        if a <= 0:
            continue
        ring(c, x, y, r * k, GOLD, a, 2.2, fill="#0E0C09", glow=6)
        ring(c, x, y, r * k * 0.88, GOLD_DIM, a * 0.6, 1.2)
        for j, s in enumerate(lab):
            text(c, s, x, y + (j - (len(lab) - 1) / 2) * L.P(56, 52), L.P(46, 42), "serif", WHITE, a)
    block(c, ["不同的人，", "投入程度和理由也不同。"], L.cx, L.P(1760, 1000) if L.portrait else 1000, L.P(44, 38),
          t, t_link, end, font="serif_medium", mode="rise", gap=1.35, keys=[Key("投入程度", t_link + 0.5), Key("理由", t_link + 0.9)])


TRIAL = [("狮子座", ["热情外向，", "也需要被看见。"]), ("处女座", ["做事认真，", "偶尔对自己苛刻。"]), ("双鱼座", ["情感细腻，", "容易共情别人。"])]


def s_trial(c, L, t):
    t0, t_cards, t_cover, sw1, sw2, t_choice = at(74.54), at(75.59), at(77.71), at(78.77), at(79.83), at(80.90)
    steps = [at(80.90), at(81.97), at(83.03)]
    end = at(85.15)
    a_out = 1 - prog(t, end - 0.3, 0.3)
    block(c, ["把星座名字遮住，", "你还认得出“自己的那份”吗？"], L.cx, L.P(330, 140), L.P(56, 50), t, t0, t_choice,
          keys=[Key("遮住", t0 + 0.3), Key("自己的那份", t0 + 0.7)])
    if L.portrait:
        slots = [(200, 900), (540, 900), (880, 900)]
        cw, chh = 300, 420
    else:
        slots = [(330, 590), (650, 590), (970, 590)]
        cw, chh = 290, 400
    perm1, perm2 = [1, 0, 2], [1, 2, 0]
    k1, k2 = ease_in_out(prog(t, sw1, 0.5)), ease_in_out(prog(t, sw2, 0.5))
    cover = ease_out(prog(t, t_cover, 0.25))
    for i, (sign, desc) in enumerate(TRIAL):
        a = a_out * ease_out(prog(t, t_cards + i * 0.08, 0.4))
        if a <= 0:
            continue
        p0 = slots[i]
        p1 = slots[perm1[i]]
        p2 = slots[perm2[i]]
        x = lerp(lerp(p0[0], p1[0], k1), p2[0], k2)
        y = lerp(lerp(p0[1], p1[1], k1), p2[1], k2) - 60 * math.sin(math.pi * k1) * (1 if i % 2 else -1) \
            - 50 * math.sin(math.pi * k2) * (1 if i else -1)
        y += (1 - ease_out(prog(t, t_cards + i * 0.08, 0.4))) * 40
        rrect(c, x, y, cw, chh, 18, GOLD, a, 2, fill="#0E0C09")
        rrect(c, x, y, cw - 22, chh - 22, 12, GOLD_DIM, a * 0.7, 1.2)
        ly = y - chh * 0.34
        text(c, sign, x, ly, L.P(40, 38), "serif", GOLD_HI, a * (1 - cover))
        if cover > 0:
            rrect(c, x, ly, (cw - 70) * cover, L.P(66, 62), 10, GOLD, a, 0, fill=GOLD, fill_alpha=0.92)
            text(c, "？？？", x, ly, L.P(34, 32), "sans_medium", BG, a * cover)
        constellation(c, x, y - chh * 0.08, cw * 0.4, 3 + i * 4, a * 0.6)
        for j, s in enumerate(desc):
            text(c, s, x, y + chh * (0.16 + 0.12 * j), L.P(30, 28), "serif_medium", WHITE, a)
        if t >= t_choice:
            letter = "ABC"[slots.index(p2)]
            la = a * prog(t, t_choice, 0.3)
            ring(c, x, y + chh / 2 + L.P(56, 50), 26, GOLD, la, 1.8)
            text(c, letter, x, y + chh / 2 + L.P(56, 50), 28, "sans_medium", GOLD_HI, la)
    if t >= t_choice:
        dur = end - t_choice
        k = prog(t, t_choice, dur)
        if L.portrait:
            rx, ry_, rr = 540, 1330, 70
        else:
            rx, ry_, rr = 1250, 330, 56
        ra = a_out * prog(t, t_choice, 0.3)
        ring(c, rx, ry_, rr, GOLD_DIM, ra, 2)
        arc = skia.Path()
        arc.addArc(skia.Rect.MakeXYWH(rx - rr, ry_ - rr, 2 * rr, 2 * rr), -90, 360 * (1 - k))
        c.drawPath(arc, paint(GOLD_HI, ra, 4))
        text(c, "选择时间", rx, ry_, L.P(26, 22), "sans_medium", WHITE, ra)
        labels = ["先看描述，再看标签。", "也记录不符合的部分。", "检查它是否同样适合很多人。"]
        if L.portrait:
            sx, sy, step, size = 150, 1500, 92, 42
        else:
            sx, sy, step, size = 1180, 520, 96, 40
        for i, s in enumerate(labels):
            a, dy = rise(t, steps[i])
            a *= a_out
            if a <= 0:
                continue
            y = sy + i * step + dy
            ring(c, sx + 16, y, 16, GOLD, a, 1.6)
            text(c, str(i + 1), sx + 16, y, 20, "sans_medium", GOLD_HI, a)
            text(c, s, sx + 50, y, size, "serif_medium", WHITE, a, "left")
        text(c, "这是帮助反思的互动练习，不是检验占星术的正式实验", L.cx, L.P(1790, 1022), L.P(24, 22), "sans", MUTED,
             a_out * prog(t, t_choice, 0.4))


def question_points(cx, cy, s, n):
    """问号（不含下方圆点）路径上均匀取 n 个点。"""
    path = skia.Path()
    path.addArc(skia.Rect.MakeXYWH(cx - s * 0.36, cy - s * 0.95, s * 0.72, s * 0.72), 200, 250)
    path.cubicTo(cx + s * 0.05, cy - s * 0.2, cx, cy - s * 0.05, cx, cy + s * 0.18)
    meas = skia.PathMeasure(path, False)
    total = meas.getLength()
    pts = []
    for k in range(n):
        pos, _ = meas.getPosTan(total * k / (n - 1))
        pts.append((pos.x(), pos.y()))
    return pts


def s_end(c, L, t):
    t0, t_q, t_ref = at(85.15), at(87.28), at(89.41)
    fade = 1 - prog(t, END - 0.9, 0.85)
    ccx, ccy = L.cx, L.P(640, 400)
    R = L.P(300, 250)
    n = 40
    ring_pts = [(ccx + R * math.cos(-math.pi / 2 + k * math.tau / n), ccy + R * 0.9 * math.sin(-math.pi / 2 + k * math.tau / n))
                for k in range(n)]
    q_pts = question_points(ccx, ccy + R * 0.25, R * 1.25, n)
    m = ease_in_out(prog(t, t_q, 1.9))
    a_ast = prog(t, t0, 0.6) * fade
    glow_bg(c, L, ccx, ccy, R * 2.2, 0.7 * a_ast)
    astrolabe(c, ccx, ccy, R, math.radians(-90) + 0.05 * (t - t0), a_ast * (1 - m) * 0.8, tilt=0.9)
    pts = [(lerp(a[0], b[0], m), lerp(a[1], b[1], m)) for a, b in zip(ring_pts, q_pts)]
    la = a_ast
    for k in range(n - 1 if m > 0.5 else n):
        p0, p1 = pts[k], pts[(k + 1) % n]
        line(c, *p0, *p1, GOLD_HI if m > 0 else GOLD, la * (0.6 + 0.4 * m), 2.4 + 1.6 * m, glow=6 * m)
    for k, (x, y) in enumerate(pts):
        ring(c, x, y, 3.2, GOLD_HI, la, 0, fill=GOLD_HI)
    dot = ease_out(prog(t, t_q + 1.2, 0.5))
    if dot > 0:
        ring(c, ccx, ccy + R * 0.25 + R * 1.25 * 0.42, 16 * dot, GOLD_HI, la, 0, fill=GOLD_HI)
        ring(c, ccx, ccy + R * 0.25 + R * 1.25 * 0.42, 32 * dot, GOLD_HI, la * 0.4, 1.5)
    ty = L.P(1240, 790)
    a1, d1 = rise(t, t0, 0.5)
    dim = 1 - 0.35 * prog(t, t_q, 0.4)
    size1 = L.P(56, 48)
    text(c, "被说中的感觉，", L.cx, ty - size1 * 0.75 + d1, size1, "serif_medium", WHITE, a1 * fade * dim)
    text(c, "值得再问一句：", L.cx, ty + size1 * 0.75 + d1, size1, "serif_medium", WHITE, a1 * fade * dim)
    ka, ks = slam(t, t_q)
    c.save()
    c.translate(L.cx, ty + L.P(210, 150))
    c.scale(ks, ks)
    rich_line(c, "这句话，只适合我吗？", 0, 0, L.P(78, 66), "serif_black", t, [Key("只适合我", t_q + 0.35)], WHITE, ka * fade)
    c.restore()
    ra = prog(t, t_ref, 0.6) * fade
    refs = "参考：Forer (1949)  ·  Meehl (1956)  ·  Nickerson (1998)  ·  Rochberg (2004)  ·  Carlson (1985)"
    if L.portrait:
        text(c, "参考：Forer (1949) · Meehl (1956) · Nickerson (1998)", L.cx, 1720, 24, "sans", MUTED, ra)
        text(c, "Rochberg (2004) · Carlson (1985)", L.cx, 1760, 24, "sans", MUTED, ra)
    else:
        text(c, refs, L.cx, 1030, 22, "sans", MUTED, ra)


SCENES = [
    (0.0, at(6.51), s_hook),
    (at(6.51) - 0.05, at(17.14), s_experience),
    (at(17.14) - 0.35, at(27.76), s_reversal),
    (at(27.76) - 0.25, at(40.52), s_forer),
    (at(40.52) - 0.05, at(53.28), s_history),
    (at(53.28) - 0.05, at(66.03), s_confirm),
    (at(66.03) - 0.05, at(74.54), s_social),
    (at(74.54) - 0.05, at(85.15), s_trial),
    (at(85.15) - 0.05, END + 0.1, s_end),
]


def beat_thread(c, L, t):
    """底部金色细线：每个实测拍点向前延伸一小段（普通拍点的小动作），强拍处节点微亮。"""
    y = L.h - L.P(120, 22)
    x0, x1 = L.P(120, 160), L.w - L.P(120, 160)
    a = 0.4 * (1 - prog(t, MUSIC_END - 1.0, 1.0))
    passed = [b for b in BEATS if b["t"] <= t]
    if not passed or a <= 0:
        return
    last = passed[-1]
    k = len(passed) - 1 + ease_out(prog(t, last["t"], 0.18))
    p = clamp01(k / len(BEATS))
    line(c, x0, y, x1, y, GOLD_DIM, a * 0.35, 1)
    line(c, x0, y, lerp(x0, x1, p), y, GOLD, a, 1.6)
    pulse = math.exp(-(t - last["t"]) * 6) * (1.0 if last["bar_pos"] == 0 else 0.5)
    ring(c, lerp(x0, x1, p), y, 3 + 4 * pulse, GOLD_HI, a * (0.6 + 0.4 * pulse), 0, fill=GOLD_HI)


def draw_frame(c, L, t):
    c.clear(gfx.col(BG))
    stars(c, L, t, 0.8 * (1 - prog(t, END - 0.9, 0.85)), n=L.P(70, 90))
    for t0, t1, fn in SCENES:
        if t0 <= t < t1:
            fn(c, L, t)
    beat_thread(c, L, t)
    fin = 1 - prog(t, 0.0, 0.35)
    if fin > 0:
        c.drawPaint(paint(BG, fin))


# ---------------------------------------------------------------- 渲染

_LAYOUT: Layout | None = None


def _render(frame: int) -> bytes:
    L = _LAYOUT
    assert L is not None
    info = skia.ImageInfo.Make(L.w, L.h, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType)
    surf = skia.Surface.MakeRaster(info)
    draw_frame(surf.getCanvas(), L, frame / FPS)
    return surf.makeImageSnapshot().tobytes()


def still(L: Layout, t: float, path: str):
    global _LAYOUT
    _LAYOUT = L
    buf = _render(int(round(t * FPS)))
    img = skia.Image.fromarray(np.frombuffer(buf, np.uint8).reshape(L.h, L.w, 4).copy(), skia.kRGBA_8888_ColorType)
    img.save(path, skia.kPNG)


def render(L: Layout, wav: str, out: str, workers: int = 4):
    """多进程逐帧渲染，与混音合成为 MP4；任一环节失败抛出 RuntimeError。"""
    global _LAYOUT
    _LAYOUT = L
    n = int(round(END * FPS))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{L.w}x{L.h}",
           "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert proc.stdin is not None
    try:
        with get_context("fork").Pool(workers) as pool:
            for buf in pool.imap(_render, range(n), chunksize=8):
                proc.stdin.write(buf)
    finally:
        proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError(f"ffmpeg exited with code {proc.returncode}")


# ---------------------------------------------------------------- 音频

SFX_LEVEL = {"kick": 0.5, "kick_light": 0.5, "rim": 0.34, "wood_high": 0.3, "wood_low": 0.3, "shaker": 0.24,
             "frame": 0.55, "tom": 0.48, "bongo_high": 0.34, "bongo_low": 0.36, "clap": 0.34, "cymbal": 0.3}
DUCK_DEPTH = {"kick": 0.22, "kick_light": 0.18, "rim": 0.12, "frame": 0.22, "tom": 0.18, "clap": 0.12, "cymbal": 0.08}


def resolve_sfx(cue: Cue) -> str:
    """音乐自身在该拍已有重底鼓（低频起音 ≥0.7）时，低音鼓改用高通版本，避免叠加过重低频。"""
    if cue.sfx == "kick" and cue.b["low"] >= 0.7:
        return "kick_light"
    return cue.sfx or ""


def music_track() -> np.ndarray:
    """配乐：原曲播放到最后一击后 0.3 秒，再接其混响尾音约 2.6 秒自然衰减到静音（原曲在 90 秒处是硬截断）。"""
    sr = audio.SR
    x = bgm.load()
    n = int(END * sr)
    cut = int(MUSIC_END * sr)
    out = np.zeros((n, 2))
    body = x[:cut].copy()
    fo = int(0.25 * sr)
    body[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5
    out[:cut] = body
    seed = x[cut - int(1.2 * sr): cut]
    lead = int(0.12 * sr)
    length = n - cut + lead
    tail = np.zeros((length, 2))
    for ch, irs in enumerate((11, 23)):
        wet = signal.fftconvolve(seed[:, ch], audio.reverb_ir(2.4, irs))[len(seed) - lead:][:length]
        tail[: len(wet), ch] = wet
    ref = np.sqrt(np.mean(body[-int(0.6 * sr): -fo] ** 2))
    tail *= ref / (np.sqrt(np.mean(tail[: int(0.4 * sr)] ** 2)) + 1e-9) * 0.5
    r = int(0.08 * sr)
    tail[:r] *= np.linspace(0, 1, r)[:, None]
    out[cut - lead:] += tail
    fade = int(0.6 * sr)
    out[-fade:] *= np.linspace(1, 0, fade)[:, None]
    return out


def build_audio() -> tuple[np.ndarray, np.ndarray, np.ndarray, list[dict]]:
    """返回 (混音, 配乐分轨, 音效分轨, 音效清单)；两条分轨乘的是同一个总增益，相加即混音（限幅前）。"""
    n = int(END * audio.SR)
    music = music_track()
    sfx = np.zeros((n, 2))
    duck = np.zeros(n)
    rel = np.exp(-np.arange(int(0.45 * audio.SR)) / audio.SR / 0.16)
    att = int(0.012 * audio.SR)
    events = []
    for cue in CUES:
        if not cue.sfx:
            continue
        name = resolve_sfx(cue)
        clip = perc.sound(name) * SFX_LEVEL[name] * cue.gain
        lead = perc.attack_ms(name) / 1000
        i = int(round((cue.t - lead) * audio.SR))
        seg = sfx[i: i + len(clip)]
        seg += audio.pan(clip[: len(seg)], 0)
        d = DUCK_DEPTH.get(name, 0.05) * cue.gain
        a0 = max(0, i - att)
        duck[a0:i] = np.maximum(duck[a0:i], np.linspace(0, d, i - a0))
        tail = duck[i: i + len(rel)]
        duck[i: i + len(rel)] = np.maximum(tail, d * rel[: len(tail)])
        frame = int(round(cue.t * FPS))
        peak_t = i / audio.SR + lead
        events.append(dict(t=cue.t, name=name, frame=frame, frame_err=round(peak_t * FPS - frame, 2), cue=cue))
    duck = signal.lfilter([0.02], [1, -0.98], duck)
    music_d = music * (1 - np.clip(duck, 0, 0.3))[:, None]
    import pyloudnorm

    meter = pyloudnorm.Meter(audio.SR)
    mix = music_d + sfx
    g = 10 ** ((-14.0 - meter.integrated_loudness(mix)) / 20)
    music_d, sfx = music_d * g, sfx * g
    mix = music_d + sfx
    a = np.abs(mix)
    knee, ceil = 0.6, 0.84
    over = a > knee
    mix[over] = np.sign(mix[over]) * (knee + (ceil - knee) * np.tanh((a[over] - knee) / (ceil - knee)))
    return mix.astype(np.float32), music_d.astype(np.float32), sfx.astype(np.float32), events


# ---------------------------------------------------------------- 封面


def cover(L: Layout, path: str):
    info = skia.ImageInfo.Make(L.w, L.h, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType)
    surf = skia.Surface.MakeRaster(info)
    c = surf.getCanvas()
    c.clear(gfx.col(BG))
    stars(c, L, 2.0, 0.9, n=L.P(90, 110))
    acx, acy = L.P((540, 1180), (1350, 560))
    glow_bg(c, L, acx, acy, L.P(800, 700), 1.0)
    astrolabe(c, acx, acy, L.P(430, 400), math.radians(-100), 0.55, tilt=0.9,
              nodes=[1.0 if k in (0, 4, 8) else 0.2 for k in range(12)])
    for k, (i, ang, dx) in enumerate(((3, -14, -1), (7, 14, 1), (0, 0, 0))):
        cx = acx + dx * L.P(200, 190)
        cy = acy + abs(dx) * L.P(40, 40)
        c.save()
        c.translate(cx, cy)
        c.rotate(ang)
        card(c, 0, 0, L.P(270, 250), L.P(360, 334), math.radians(dx * -18), sign_front(i), sign_back(i), 1.0, 1.0,
             glow=0.8 if dx == 0 else 0.2)
        c.restore()
    if L.portrait:
        tx, ty, size, align = 540, 420, 110, "center"
    else:
        tx, ty, size, align = 130, 420, 112, "left"
    gfx.draw_text(c, "星座为什么", tx, ty, size, "serif_black", GOLD_HI, 1.0, align,
                  glow=(GOLD_DIM, 30), gradient=[GOLD_HI, GOLD])
    gfx.draw_text(c, "这么准？", tx, ty + size * 1.25, size, "serif_black", GOLD_HI, 1.0, align,
                  glow=(GOLD_DIM, 30), gradient=[GOLD_HI, GOLD])
    sub_y = ty + size * 1.25 + L.P(150, 150)
    if L.portrait:
        line(c, 330, sub_y - 70, 750, sub_y - 70, GOLD, 0.8, 2)
    else:
        line(c, tx, sub_y - 70, tx + 420, sub_y - 70, GOLD, 0.8, 2)
    gfx.draw_text(c, "先别看你的星座", tx, sub_y, L.P(60, 58), "serif_medium", WHITE, 1.0, align)
    gfx.draw_text(c, "巴纳姆效应 · 确认偏误 · 一个心理学小实验", tx, sub_y + L.P(80, 76), L.P(30, 28), "sans", MUTED, 1.0,
                  align)
    surf.makeImageSnapshot().save(path, skia.kPNG)


# ---------------------------------------------------------------- 文档

def tc(t: float) -> str:
    m, s = divmod(t, 60)
    return f"{int(m):02d}:{s:05.2f}"


def write_cue_sheet(out_dir: Path, events: list[dict]):
    rows = []
    sfx_of = {id(e["cue"]): e for e in events}
    for cue in CUES:
        b = cue.b
        e = sfx_of.get(id(cue))
        sec = "段落起点" if any(abs(b["t"] - s) < 0.05 for s in SECTIONS) else ""
        rows.append(dict(
            时间码=tc(cue.t), 帧=int(round(cue.t * FPS)), 实测拍点秒=f"{b['t']:.3f}", 小节位置=b["bar_pos"] + 1,
            起音强度=f"{b['strength']:.2f}", 低频起音=f"{b['low']:.2f}", 高频起音=f"{b['high']:.2f}",
            重音值=f"{accent(b):.2f}", 重音等级=level(b) + (f"·{sec}" if sec else ""), 段落=cue.scene, 画面动作=cue.action,
            字幕=cue.caption.replace("／", " / "),
            打击乐=(perc.TIMBRES[e["name"]] if e else "—"),
            音画偏差帧=(f"{e['frame_err']:+.2f}" if e else "—")))
    with open(out_dir / "cue_sheet.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    cols = list(rows[0].keys())
    md = ["# 《为什么人会信星座？》实际卡点表", "",
          "拍点全部来自 `engine/bgm.py` 的 `detect()`（librosa 动态规划节拍跟踪，拍长不设为常数）对 `music/bgm.m4a` 的实测结果；"
          "表中每个动作都吸附在离分镜参考时间最近的实测拍点上（偏差超过 0.12 秒即报错），没有人工补拍。", "",
          "- 起音强度 / 低频起音 / 高频起音：该拍 ±40 ms 内的起音包络峰值，按全曲 5%–99.7% 分位归一到 0–1",
          "- 小节位置：1 为强拍（按低频起音最强的相位估计）",
          "- 重音值 = max(起音强度, 0.9×低频起音, 0.9×高频起音)；重音等级：强 = 重音值 ≥0.85 且位于第 1/3 拍或段落起点；"
          "中 = 重音值 ≥0.5；其余为弱",
          "- 音画偏差帧：音效起音峰值相对画面撞击帧的偏差（单位：帧，30 fps）；音效按各自起音时间提前放置，使峰值落在实测拍点上", "",
          "| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in rows:
        md.append("| " + " | ".join(str(r[k]) for k in cols) + " |")
    ibi = np.diff([b["t"] for b in BEATS])
    md += ["", "## 音乐结构（实测）", "",
           f"- 检测到 {len(BEATS)} 个拍点，拍间隔 {ibi.min():.3f}–{ibi.max():.3f} 秒（中位数 {np.median(ibi):.3f} 秒，"
           f"约 {60 / np.median(ibi):.1f} BPM，标准差 {ibi.std() * 1000:.1f} ms）——速度实测基本稳定，但卡点仍逐拍使用检测时间",
           "- 段落边界（节拍同步的和声/音色特征层次聚类）：" + "、".join(f"{s:.2f}s" for s in SECTIONS),
           "- 明显停顿（连续拍点起音强度 <0.2）：" + "、".join(_gaps()),
           "- 情绪：0–17.1 秒前奏较弱（约 -21 dB）→ 17.1 秒进入高能段（约 -16 dB）→ 约 48 秒起略回落（约 -19 dB）"
           "→ 77.7 秒短暂抽空后 78.8 秒再起 → 87.8–88.9 秒停顿，89.4 秒最后一击；原曲在 90.0 秒处直接截断，成片以混响尾音自然淡出",
           "", "## 打击乐音色", "", "| 音色 | 起音峰值 | 尾音（-50 dB） |", "|---|---|---|"]
    for k, v in perc.TIMBRES.items():
        md.append(f"| {v} | {perc.attack_ms(k):.1f} ms | {perc.tail_s(k):.2f} s |")
    (out_dir / "cue_sheet.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def _gaps() -> list[str]:
    out, run = [], []
    for b in BEATS:
        if b["strength"] < 0.2:
            run.append(b["t"])
        else:
            if len(run) >= 1:
                out.append(f"{run[0]:.2f}–{run[-1] + 0.53:.2f}s")
            run = []
    return out


COPY = """# 《为什么人会信星座？》屏幕文案与参考资料

## 发布信息

- 发布标题：《为什么星座总像在说你？一个心理学小实验》
- 封面主标题：星座为什么这么准？
- 封面副标题：先别看你的星座
- 话题：#知识科普 #心理学 #星座 #巴纳姆效应 #确认偏误

## 屏幕文案（按出现顺序）

{lines}

## 参考资料

1. Forer, B. R. (1949). The fallacy of personal validation: A classroom demonstration of gullibility.
   *Journal of Abnormal and Social Psychology, 44*(1), 118–123. https://doi.org/10.1037/h0059240
   —— 片中“1949｜福勒的课堂实验”：学生做问卷后拿到看似个人化、实际相同的描述。片中未引用任何人数或评分。
2. Meehl, P. E. (1956). Wanted—a good cookbook. *American Psychologist, 11*(6), 263–272.
   https://doi.org/10.1037/h0044164 —— “巴纳姆效应（Barnum effect）”一词的出处。
3. Dickson, D. H., & Kelly, I. W. (1985). The "Barnum effect" in personality assessment: A review of the literature.
   *Psychological Reports, 57*(2), 367–382. https://doi.org/10.2466/pr0.1985.57.2.367 —— 巴纳姆效应研究综述。
4. Nickerson, R. S. (1998). Confirmation bias: A ubiquitous phenomenon in many guises.
   *Review of General Psychology, 2*(2), 175–220. https://doi.org/10.1037/1089-2680.2.2.175 —— 确认偏误。
5. Rochberg, F. (2004). *The Heavenly Writing: Divination, Horoscopy, and Astronomy in Mesopotamian Culture.*
   Cambridge University Press. https://doi.org/10.1017/CBO9780511617409 —— 美索不达米亚天象占卜与黄道十二宫的起源。
6. Encyclopaedia Britannica, “Zodiac” 与 “Astrology” 词条 —— 黄道十二等分约形成于公元前 5 世纪的巴比伦；
   本命盘占星在希腊化时期（约公元前 2—1 世纪）成形；20 世纪 30 年代起报刊“太阳星座”专栏流行。
7. Carlson, S. (1985). A double-blind test of astrology. *Nature, 318*, 419–425. https://doi.org/10.1038/318419a0
   —— “遮住标签再选描述”的盲选思路来源；片中的互动练习只用于自我反思，不是正式实验，也未引用其结果数字。

## 表达边界（制作时遵守）

- 不嘲讽相信星座的人；“不止一种理由”段落明确：娱乐、社交、理解自己的语言，投入程度和理由因人而异。
- 福勒实验标注为“一次课堂演示”，不当作对所有星座信念的完整解释。
- 漏斗图标注“机制示意”，卡片数量不代表任何实验数据；全片没有百分比或统计数字。
- 历史段区分天文学（研究天体本身）与占星术（用天象解读人事），不把现代星座性格测试说成古代已有的同一种产品。
"""


def write_copy(out_dir: Path):
    lines = []
    for cue in CUES:
        if cue.caption:
            lines.append(f"- `{tc(cue.t)}` 【{cue.scene}】{cue.caption.replace('／', ' / ')}")
    extra = [
        "- 小字：BARNUM EFFECT / CONFIRMATION BIAS（概念英文名）",
        "- 小字：注：一次课堂演示，不能解释所有人为什么会信星座",
        "- 历史时间轴：约公元前 5 世纪｜巴比伦：黄道分为十二等份；约公元前 2—1 世纪｜希腊化时期：本命盘占星成形；"
        "20 世纪 30 年代起｜报刊“太阳星座”专栏流行",
        "- 小字：天文学研究天体本身；占星术用天象解读人事——二者不同",
        "- 卡片：预测：本周会有小惊喜，也可能有点累；经历：被朋友夸奖 / 有点累 / 遇到小惊喜 / 收到好消息（被选中）；"
        "一切如常 / 没遇到惊喜 / 睡得很好 / 心情平静（移到一旁：仍然发生过，只是容易被略过）；漏斗：被记住的“准”（机制示意）",
        "- 小实验卡片：狮子座「热情外向，也需要被看见。」处女座「做事认真，偶尔对自己苛刻。」双鱼座「情感细腻，容易共情别人。」",
        "- 小字：这是帮助反思的互动练习，不是检验占星术的正式实验",
        "- 片尾：参考：Forer (1949) · Meehl (1956) · Nickerson (1998) · Rochberg (2004) · Carlson (1985)",
    ]
    (out_dir / "copy_and_references.md").write_text(COPY.format(lines="\n".join(lines + extra)), encoding="utf-8")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out_dir = Path(args[0] if args else "out/zodiac")
    out_dir.mkdir(parents=True, exist_ok=True)
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1]
    mix, music, sfx, events = build_audio()
    sf.write(out_dir / "bgm_track.wav", music, audio.SR, subtype="PCM_24")
    sf.write(out_dir / "sfx_track.wav", sfx, audio.SR, subtype="PCM_24")
    sf.write(out_dir / "mix.wav", mix, audio.SR, subtype="PCM_24")
    write_cue_sheet(out_dir, events)
    write_copy(out_dir)
    worst = max(abs(e["frame_err"]) for e in events)
    print(f"sfx events {len(events)}, max audio/visual offset {worst:.2f} frame, peak {np.max(np.abs(mix)):.3f}")
    for name, L in (("portrait", PORTRAIT), ("landscape", LANDSCAPE)):
        cover(L, str(out_dir / f"cover_{name}.png"))
        if "--no-video" in sys.argv or (only and only != name):
            continue
        with tempfile.TemporaryDirectory() as tmp:
            wav = str(Path(tmp) / "mix.wav")
            sf.write(wav, mix, audio.SR)
            out = out_dir / f"zodiac_{name}_{L.w}x{L.h}.mp4"
            render(L, wav, str(out))
            print(f"written: {out}")


if __name__ == "__main__":
    main()
