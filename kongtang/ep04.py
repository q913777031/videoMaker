"""04 绿色开胃菜：饭前先吃一盘菜，有什么用？（书中第 2 个方法）"""

import math

from engine.gfx import clamp01, ease_in_out

from adler import kit as K
from adler.core import Big, Bubble, Custom, Episode, Shot, Txt

from . import kit_tang as T
from .common import SERIES, TITLES, ending, refs

ACC = "#4E8C3A"
REFS = refs("Imai 等（2011）Asia Pac J Clin Nutr 20(2):161–168")


def spike_fn(u):
    return T.bump(u, 0.95, 0.2, 2.6, 0.12)


def flat_fn(u):
    return T.bump(u, 0.5, 0.3, 1.7)


# ---------------------------------------------------------------- 1 餐厅

def menu(c, g, t, d):
    """菜单卡：主食、主菜，第 4 拍在最上面加一行“开胃菜：一盘青菜”。"""
    K.card(c, 0, 0, 560, 520, K.PAPER, 1, 24, 1.0, 0, 1, ACC)
    K.text(c, "今日午餐", 0, -190, 44, "serif_black", K.INK)
    rows = [("rice", "米饭"), ("drumstick", "红烧鸡腿")]
    k = clamp01(g.since(d["b0"]) / 0.4) if d.get("b0") is not None else 0
    off = 110 * ease_in_out(k)
    if k > 0:
        T.food(c, "salad", -160, -80, 100, k)
        K.text(c, "先来一盘青菜", -80, -80, 38, "serif_black", ACC, k, "left")
    for i, (f, s) in enumerate(rows):
        y = -80 + i * 110 + off
        T.food(c, f, -160, y, 100, 1)
        K.text(c, s, -80, y, 38, "serif", K.INK, 1, "left")


# ---------------------------------------------------------------- 4 drop

def green_bowls(c, g, t, d):
    items = ["salad", "broccoli", "salad"]
    labels = ["凉拌菜", "清炒青菜", "沙拉"]
    for i, (f, s) in enumerate(zip(items, labels)):
        k = clamp01(g.since(4 + 2 * i) / 0.3)
        if k <= 0:
            continue
        x = -300 + i * 300
        T.food(c, f, x, 0, 190, k, 0, 0.3 + 0.7 * K.ease_out_back(k, 1.8))
        K.text(c, s, x, 150, 34, "sans_medium", K.INK2, k)


# ---------------------------------------------------------------- 6 曲线

def compare(c, g, t, d):
    p1 = clamp01(g.since(1) / max(0.1, g.b(5) - g.b(1)))
    p2 = clamp01(g.since(6) / max(0.1, g.b(10) - g.b(6)))
    T.chart(c, 0, 0, 820, 520, [(spike_fn, T.SPIKE, p1, 9, "直接吃主食"), (flat_fn, T.FLAT, p2, 9, "先吃一盘菜")])


# ---------------------------------------------------------------- 7 纤维先到

def fiber_first(c, g, t, d):
    """肠道示意：青菜先下去铺开，后面的米饭再到。"""
    T.vessel(c, 0, 40, 900, 260)
    K.text(c, "肠道（示意）", -420, -130, 30, "sans_medium", K.INK2, 1, "left")
    k = clamp01(g.since(1) / 0.8)
    for i in range(int(10 * k)):
        x = -400 + i * 85
        T.food(c, "broccoli", x, 40 + 20 * math.sin(i), 70, 1)
    kk = clamp01(g.since(5) / 0.5)
    if kk > 0:
        T.particles(c, -440, 40, 440, 40, g.t, 6, 16, T.GLU, kk, 0.15, 2, 50)
        K.pill(c, 0, 250, "先到的纤维，让后面的吸收慢一些", 32, ACC, K.PAPER, clamp01(g.since(7) / 0.35))


# ---------------------------------------------------------------- 9–10 研究证据

def imai(c, g, t, d):
    """两组 HbA1c 柱子：先吃蔬菜组 8.3%→6.8%，交换份组 8.2%→7.3%。"""
    groups = [("先吃蔬菜组", 8.3, 6.8, ACC, "69 人"), ("传统交换份组", 8.2, 7.3, K.OTHER2, "32 人")]
    base, top = 6.0, 8.6
    H = 380
    for i, (lab, a, b, col, n) in enumerate(groups):
        x = -230 + i * 460
        k = clamp01(g.since(i * 2) / 0.4)
        if k <= 0:
            continue
        K.card(c, x, 0, 400, 620, K.PAPER, k, 24, 0.9, 0, 1, col)
        K.text(c, lab, x, -250, 36, "serif_black", col, k)
        K.text(c, n, x, -200, 28, "sans_medium", K.INK3, k)
        kb = clamp01(g.since(4 + i) / 0.6)
        for j, (v, tag_) in enumerate(((a, "开始"), (b, "2 年后"))):
            hh = H * (v - base) / (top - base) * (k if j == 0 else ease_in_out(kb))
            bx = x - 70 + j * 140
            K.rr(c, bx, 230 - hh / 2, 100, max(1, hh), 12, K.tint(col, 0.4 if j == 0 else 0.0))
            if j == 0 or kb > 0.9:
                K.text(c, f"{v}%", bx, 230 - hh - 26, 32, "black", col, k)
            K.text(c, tag_, bx, 270, 26, "sans_medium", K.INK2, k)
    K.text(c, "糖化血红蛋白（HbA1c）", 0, -340, 30, "sans_medium", K.INK2, clamp01(g.since(1) / 0.3))


# ---------------------------------------------------------------- 11 专家提醒

def caveat(c, g, t, d):
    for i, (lab, col, k0) in enumerate((("糖尿病患者", K.OTHER3, 1), ("健康人", K.HERO, 4))):
        k = clamp01(g.since(k0) / 0.35)
        if k <= 0:
            continue
        x = -240 + i * 480
        K.figure(c, x, 200, 340, "stand", col, mood="calm", alpha=k, hair=("bun", "short")[i])
        K.text(c, lab, x, 260, 36, "serif_black", col, k)
        if i == 0:
            K.pill(c, x, -260, "有研究结果", 30, ACC, K.PAPER, k)
    k = clamp01(g.since(6) / 0.3)
    if k > 0:
        K.icon(c, "question", 240, -260, 110, K.HERO, k, 0.6)


# ---------------------------------------------------------------- 12 常见误解

def balance(c, g, t, d):
    """左：一桌只有菜（打叉）；右：菜 + 肉 + 饭（打勾）。"""
    for i, (items, ok) in enumerate(((["salad", "broccoli", "salad"], False),
                                     (["salad", "drumstick", "rice"], True))):
        x = -250 + i * 500
        T.plate(c, x, 0, 210)
        for j, f in enumerate(items):
            T.food(c, f, x - 80 + j * 80, -10 + 40 * (j % 2), 95, 1)
        k = clamp01(g.since(3 + 3 * i) / 0.3)
        if k > 0:
            K.icon(c, "check" if ok else "cross", x, -240, 90, K.GREEN if ok else K.RED, k, 0.5)
    k = clamp01(g.since(9) / 0.35)
    if k > 0:
        K.pill(c, 0, 290, "先吃菜，其余照常吃", 34, ACC, K.PAPER, k)


# ---------------------------------------------------------------- 12 小练习

def bites(c, g, t, d):
    """一盘青菜，筷子按拍夹起三口。"""
    T.plate(c, 0, 0, 260)
    for i in range(5):
        T.food(c, "broccoli", -120 + i * 60, -20 + 30 * (i % 2), 100, 1 - clamp01(g.since(2 + 2 * i) / 0.3) * (i < 3))
    for i in range(3):
        k = clamp01(g.since(2 + 2 * i) / 0.3)
        if k > 0:
            K.text(c, f"第 {i + 1} 口", -240 + i * 240, -320, 34, "serif_black", ACC, k)


def build() -> Episode:
    shots = [
        Shot(3, "点菜时，|大家直奔主食和肉。", "情境演绎", [
            Custom(menu, x=540, y=740, at=0, enter="pop", b0=None),
        ], hits=[(0, "wood_low", 0.7, "菜单出现")], note="菜单上只有米饭和红烧鸡腿"),
        Shot(3, "书里的建议：|最前面加一盘菜。", "书中观点", [
            Custom(menu, x=540, y=740, at=0, enter="none", b0=4),
        ], hits=[(4, "bongo_high", 0.8, "菜单最上面插入“先来一盘青菜”")], cut=True,
            note="第 4 拍菜单最上面插进一行“先来一盘青菜”，其他菜往下挪"),
        Shot(2, "这叫……", "书中观点", [
            Custom(lambda c, g, t, d: T.food(c, "salad", 0, 0, 300, clamp01(g.since(0) / 0.3), 0,
                                             1 + 0.05 * math.sin(g.t * 5)), x=540, y=760, at=0, enter="none",
                   sfx="wood_low", note="沙拉弹出"),
        ], text_beat=0, note="一碗沙拉轻轻晃动"),
        Shot(3, "饭前先吃一份蔬菜，|凉拌、清炒、沙拉都行。", "书中观点", [
            Big("绿色开胃菜", 540, 470, 140, at=0, sfx="kick", sub="方法 2 · green starter", note="概念落版（音乐 drop）"),
            Custom(green_bowls, x=540, y=900, at=0, enter="none"),
        ], hits=[(4, "wood_high", 0.8, "凉拌菜"), (6, "wood_low", 0.8, "清炒青菜"), (8, "bongo_high", 0.8, "沙拉")],
            note="drop 处“绿色开胃菜”砸下；凉拌菜、清炒青菜、沙拉按拍弹出"),
        Shot(3, "它是第 1 个方法的|“加强版”。", "书中观点", [
            Custom(lambda c, g, t, d: T.step_order(c, 0, 0, [("salad", "开胃菜"), ("broccoli", "蔬菜"),
                                                             ("drumstick", "蛋白质"), ("rice", "主食")],
                                                   [clamp01(g.since(i) / 0.3) for i in range(4)], 130, 240),
                   x=540, y=760, at=0, enter="none"),
        ], hits=[(0, "wood_high", 0.7, "开胃菜排在最前"), (3, "bongo_high", 0.7, "主食排最后")],
            note="开胃菜排在进食顺序最前面：开胃菜 → 蔬菜 → 蛋白质 → 主食"),
        Shot(3, "书中的曲线：|先吃菜，峰更低。", "书中观点", [
            Custom(compare, x=540, y=780, at=0, enter="fade"),
        ], hits=[(1, "shaker", 0.6, "直接吃主食的曲线"), (6, "wood_low", 0.7, "先吃一盘菜的曲线")],
            note="两条曲线：直接吃主食更尖，先吃一盘菜更平（示意）"),
        Shot(3, "道理一样：纤维先到，|后面的吸收慢一些。", "书中观点", [
            Custom(fiber_first, x=540, y=780, at=0, enter="fade"),
        ], hits=[(1, "shaker", 0.7, "青菜先铺开"), (5, "wood_low", 0.7, "葡萄糖慢慢通过"), (7, "wood_high", 0.6, "标签")],
            note="肠道示意：青菜先下去铺开，后来的葡萄糖颗粒慢慢通过"),
        Shot(2, "长期这样吃，|有用吗？", "研究证据", [
            Custom(lambda c, g, t, d: K.icon(c, "question", 0, 0, 220, ACC, clamp01(g.since(0) / 0.3), 0.8),
                   x=540, y=760, at=0, enter="none", sfx="bongo_low", note="大问号"),
        ], text_beat=0, note="一个大问号"),
        Shot(2, "日本 2 年研究：|101 位糖尿病患者。", "研究证据", [
            Custom(lambda c, g, t, d: K.crowd(c, 0, 0, 11, 200, g.t, alpha=clamp01(g.since(0) / 0.4), spread=760, rows=2),
                   x=540, y=900, at=0, enter="none", sfx="wood_high", note="一群受试者"),
        ], text_beat=0, note="两排人剪影：101 位 2 型糖尿病患者"),
        Shot(4, "先吃蔬菜组：8.3% → 6.8%|对照组：8.2% → 7.3%", "研究证据", [
            Custom(imai, x=540, y=800, at=0, enter="none"),
            Txt("Imai 等，2011；糖化血红蛋白越低，说明长期血糖控制越好", 540, 1215, 26, at=2, font="sans_medium",
                color=K.INK2),
        ], research=True, hits=[(0, "wood_high", 0.7, "先吃蔬菜组"), (2, "wood_low", 0.7, "对照组"),
                                (4, "rim", 0.8, "先吃蔬菜组降到 6.8%"), (5, "bongo_high", 0.7, "对照组降到 7.3%")],
            note="两组糖化血红蛋白柱子：先吃蔬菜组 8.3%→6.8%，传统交换份组 8.2%→7.3%"),
        Shot(3, "注意：研究对象是糖尿病患者，|健康人效果未必一样。", "专家提醒", [
            Custom(caveat, x=540, y=780, at=0, enter="none"),
        ], hits=[(1, "wood_high", 0.7, "糖尿病患者"), (4, "wood_low", 0.7, "健康人"), (6, "rim", 0.7, "问号")],
            note="左：糖尿病患者（有研究结果）；右：健康人旁边一个问号——结论不能直接外推"),
        Shot(3, "不是越多越好，|也不是只吃菜。", "常见误解", [
            Custom(balance, x=540, y=780, at=0, enter="none"),
        ], hits=[(3, "rim", 0.8, "只吃菜：打叉"), (6, "wood_high", 0.8, "菜肉饭都有：打勾"), (9, "wood_low", 0.6, "标签")],
            note="左盘只有菜（打叉），右盘菜、肉、饭都有（打勾）：先吃菜，其余照常吃"),
        Shot(4, "小练习：每顿饭，|先吃几口菜。", "小练习", [
            Custom(bites, x=540, y=760, at=0, enter="none"),
        ], hits=[(2, "wood_high", 0.7, "第 1 口"), (4, "wood_low", 0.7, "第 2 口"), (6, "bongo_high", 0.7, "第 3 口")],
            note="一盘青菜，按拍被夹走三口"),
        Shot(2, "多一盘菜，多了热量？|下一讲说。", "书中观点", [
            Bubble("热量会不会超？", 540, 720, 46, at=0, sfx="wood_low", note="疑问气泡"),
        ], text_beat=0, note="气泡：热量会不会超？——预告下一期"),
        ending(4, REFS),
    ]
    return Episode(4, "starter", "绿色开胃菜", TITLES[4], ACC, shots, refs=REFS,
                   publish_title=f"{TITLES[4]}｜控糖革命04 绿色开胃菜", hashtags="#控糖 #蔬菜 #控糖革命 #健康 #科普",
                   cover_title="饭前先吃一盘菜，|有什么【用】？", cover_sub="控糖革命 · 方法 2", cover_shot=3, cover_t=5.5,
                   notes=[
                       "“饭前先吃一份蔬菜”是书中第 2 个方法；凉拌菜、清炒青菜为本片举例。",
                       "Imai 等（2011，Asia Pac J Clin Nutr 20(2):161–168）：101 位日本 2 型糖尿病患者随机分组，"
                       "“先吃蔬菜”组（69 人）2 年后糖化血红蛋白由 8.3% 降到 6.8%，传统交换份饮食组（32 人）由 8.2% 降到 7.3%。"
                       "受试者为 2 型糖尿病患者，结论不能直接外推到健康人。",
                       "第 6、7 镜曲线与肠道图为示意。",
                       "书中提到开胃菜会增加一点热量，并认为不必担心——这是下一讲（方法 3）的内容。",
                   ], **SERIES).build()
