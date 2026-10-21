"""03 进食顺序：同一顿饭，换个顺序吃？（书中第 1 个方法）"""

from engine.gfx import clamp01, ease_in_out

from adler import kit as K
from adler.core import Big, Bubble, Custom, Episode, Fig, Shot, Txt

from . import kit_tang as T
from .common import GROUND, SERIES, TITLES, ending, ground, refs

ACC = "#5E9A4E"
REFS = refs("Shukla 等（2015）Diabetes Care 38(7):e98–e99")
ORDER = [("broccoli", "蔬菜"), ("drumstick", "蛋白质、脂肪"), ("rice", "淀粉、糖")]


def spike_fn(u):
    return T.bump(u, 1.0, 0.2, 2.6, 0.15)


def flat_fn(u):
    return T.bump(u, 0.5, 0.3, 1.7)


# ---------------------------------------------------------------- 1–2 一桌饭

def meal(c, g, t, d):
    T.plate(c, 0, 0, 300)
    T.food(c, "rice", -110, -60, 150, clamp01(g.since(0) / 0.3))
    T.food(c, "broccoli", 110, -60, 150, clamp01(g.since(1) / 0.3))
    T.food(c, "drumstick", 0, 110, 150, clamp01(g.since(2) / 0.3))


def first_bite(c, g, t, d):
    """筷子先夹米饭：米饭被高亮。"""
    meal(c, g, t, d)
    k = clamp01(g.since(d["b0"]) / 0.35)
    if k > 0:
        K.ring(c, -110, -60, 100 + 10 * (1 - k), K.RED, 7, k)
        K.text(c, "先吃这个？", -110, -210, 34, "serif_black", K.RED, k)


# ---------------------------------------------------------------- 4 drop 顺序

def order_row(c, g, t, d):
    T.step_order(c, 0, 0, ORDER, [clamp01(g.since(4 + 2 * i) / 0.3) for i in range(3)], 160, 300)


# ---------------------------------------------------------------- 6 两条曲线

def compare(c, g, t, d):
    p1 = clamp01(g.since(1) / max(0.1, g.b(5) - g.b(1)))
    p2 = clamp01(g.since(6) / max(0.1, g.b(10) - g.b(6)))
    T.chart(c, 0, 0, 820, 520, [(spike_fn, T.SPIKE, p1, 9, "先吃饭"), (flat_fn, T.FLAT, p2, 9, "饭放最后")])


# ---------------------------------------------------------------- 7 纤维网

def fiber_net(c, g, t, d):
    """肠道剖面：先进去的纤维铺成一张网，后来的葡萄糖穿过时慢下来。"""
    T.vessel(c, 0, 0, 900, 300)
    K.text(c, "肠道（示意）", -420, -190, 30, "sans_medium", K.INK2, 1, "left")
    k = clamp01(g.since(2) / 0.8)
    for i in range(9):
        x = -360 + i * 90
        K.seg(c, x, -130 * k, x + 50, 130 * k, T.VEG, 7, 0.85)
        K.seg(c, x + 50, -130 * k, x, 130 * k, T.VEG2, 6, 0.85)
    slow = 0.15 if g.since(6) >= 0 else 0.6
    T.particles(c, -440, 0, 440, 0, g.t, 8, 18, T.GLU, clamp01(g.since(5) / 0.4), slow, 2, 60)
    kk = clamp01(g.since(8) / 0.35)
    if kk > 0:
        K.pill(c, 0, 220, "葡萄糖吸收变慢", 36, ACC, K.PAPER, kk)


# ---------------------------------------------------------------- 8 研究证据

def study(c, g, t, d):
    """左：先吃碳水；右：先吃菜和蛋白质；下面各一条曲线（示意）。"""
    for i, (lab, items, fn, col) in enumerate((("先吃碳水", ["rice", "broccoli", "drumstick"], spike_fn, T.SPIKE),
                                               ("先吃菜和蛋白质", ["broccoli", "drumstick", "rice"], flat_fn, T.FLAT))):
        x = -220 + i * 440
        k = clamp01(g.since(i * 2) / 0.35)
        if k <= 0:
            continue
        K.card(c, x, 0, 400, 560, K.PAPER, k, 24, 0.9, 0, 1, col)
        K.text(c, lab, x, -220, 34, "serif_black", col, k)
        for j, name in enumerate(items):
            T.food(c, name, x - 120 + j * 120, -110, 90, k)
        pk = clamp01(g.since(4 + i * 2) / 1.2)
        T.chart(c, x, 120, 300, 200, [(fn, col, pk, 6, "")], k, None, "", "", False, False)
    kk = clamp01(g.since(1) / 0.35)
    if kk > 0:
        K.pill(c, 0, -360, "11 位 2 型糖尿病患者 · 同样一餐", 32, K.INK2, K.PAPER, kk)


# ---------------------------------------------------------------- 10 常见误解

def same_plate(c, g, t, d):
    """左右两盘一模一样的饭，中间一个等号。"""
    for i, x in enumerate((-250, 250)):
        T.plate(c, x, 0, 200)
        for j, (name, _) in enumerate(ORDER):
            T.food(c, name, x - 70 + j * 70, -10 + 40 * (j % 2), 90, 1)
        K.text(c, ("原来", "现在")[i], x, 250, 34, "serif_black", K.INK2)
    k = clamp01(g.since(2) / 0.35)
    if k > 0:
        K.text(c, "=", 0, 0, 120, "black", ACC, k)
    k = clamp01(g.since(6) / 0.35)
    if k > 0:
        K.pill(c, 0, -280, "吃的东西不变，只换顺序", 34, ACC, K.PAPER, k)


# ---------------------------------------------------------------- 11 盖饭

def topping(c, g, t, d):
    """一碗盖饭，上面的青菜和肉按拍被夹走，最后露出米饭。"""
    T.food(c, "rice", 0, 40, 360, 1)
    k1 = clamp01(g.since(2) / 0.5)
    k2 = clamp01(g.since(5) / 0.5)
    T.food(c, "broccoli", -80 - 300 * k1, -60 - 200 * k1, 130, 1 - 0.3 * k1)
    T.food(c, "drumstick", 80 + 300 * k2, -60 - 200 * k2, 130, 1 - 0.3 * k2)
    k3 = clamp01(g.since(8) / 0.35)
    if k3 > 0:
        K.pill(c, 0, 280, "米饭留到最后", 34, ACC, K.PAPER, k3)


# ---------------------------------------------------------------- 12 小练习

def rice_last(c, g, t, d):
    """米饭碗从中间被挪到最右边，标“最后吃”。"""
    T.plate(c, -150, 0, 240)
    T.food(c, "broccoli", -230, -40, 120, 1)
    T.food(c, "drumstick", -90, 60, 120, 1)
    m = ease_in_out(clamp01(g.since(2) / 0.6))
    x = -150 + 450 * m
    T.food(c, "rice", x, -60 + 60 * m, 150, 1)
    k = clamp01(g.since(5) / 0.35)
    if k > 0:
        K.pill(c, 300, 120, "最后吃", 36, ACC, K.PAPER, k)


def build() -> Episode:
    shots = [
        Shot(3, "一盘菜、一块肉、|一碗米饭。", "情境演绎", [
            Custom(meal, x=540, y=760, at=0, enter="none"),
        ], hits=[(0, "wood_low", 0.7, "米饭"), (1, "wood_high", 0.7, "西兰花"), (2, "bongo_high", 0.7, "鸡腿")],
            note="餐盘里依次出现米饭、西兰花、鸡腿"),
        Shot(3, "饿了，很多人|第一口先扒饭。", "情境演绎", [
            Custom(first_bite, x=540, y=700, at=0, enter="none", b0=4),
            Fig(860, GROUND, 330, at=0, mood="happy", hair="short", face=-1,
                moves=[(4, dict(pose="reach", sfx="wood_high", note="伸手先夹米饭"))]),
        ], draw=ground, hits=[(4, "rim", 0.8, "米饭被红圈圈出")], note="主角伸手，第 4 拍米饭被红圈圈出：先吃这个？"),
        Shot(2, "书里说：|顺序能改变曲线。", "书中观点", [
            Custom(lambda c, g, t, d: T.chart(c, 0, 0, 700, 420, [(spike_fn, T.SPIKE, 1, 8, ""),
                                                                 (flat_fn, T.FLAT, clamp01(g.since(1) / 1.0), 8, "")]),
                   x=540, y=760, at=0, enter="pop", sfx="wood_low", note="两条曲线"),
        ], hits=[(1, "shaker", 0.6, "平稳曲线画出")], text_beat=0, note="一张图里两条曲线：尖峰与平稳（示意）"),
        Shot(3, "先吃菜，再吃肉，|最后吃饭。", "书中观点", [
            Big("进食顺序", 540, 470, 150, at=0, sfx="kick", sub="方法 1 · eat in the right order", note="概念落版（音乐 drop）"),
            Custom(order_row, x=540, y=900, at=0, enter="none"),
        ], hits=[(4, "wood_high", 0.8, "① 蔬菜"), (6, "wood_low", 0.8, "② 蛋白质、脂肪"), (8, "bongo_high", 0.8, "③ 淀粉、糖")],
            note="drop 处“进食顺序”砸下；蔬菜、鸡腿、米饭按 1、2、3 按拍排开"),
        Shot(3, "蔬菜 → 蛋白质和脂肪|→ 淀粉和糖。", "书中观点", [
            Custom(lambda c, g, t, d: T.step_order(c, 0, 0, ORDER, [1, 1, 1], 160, 300), x=540, y=760, at=0,
                   enter="fade"),
            Txt("书中第 1 个方法", 540, 1120, 32, at=4, font="sans_medium", color=K.INK2),
        ], hits=[(4, "wood_high", 0.6, "标注出现")], note="三步顺序完整展示，标“书中第 1 个方法”"),
        Shot(3, "同样的一餐，|换个顺序，曲线更平。", "书中观点", [
            Custom(compare, x=540, y=780, at=0, enter="fade"),
        ], hits=[(1, "shaker", 0.6, "先吃饭的尖峰曲线"), (6, "wood_low", 0.7, "饭放最后的平稳曲线")],
            note="“先吃饭”画出尖峰曲线，“饭放最后”画出平稳曲线（示意）"),
        Shot(3, "书中解释：纤维像一张网，|让葡萄糖吸收慢下来。", "书中观点", [
            Custom(fiber_net, x=540, y=780, at=0, enter="fade"),
        ], hits=[(2, "shaker", 0.7, "纤维网铺开"), (6, "wood_low", 0.7, "葡萄糖穿网变慢"), (8, "wood_high", 0.7, "标签")],
            note="肠道示意图：绿色纤维先铺成网，后来的葡萄糖颗粒穿过时明显变慢"),
        Shot(2, "有研究验证过吗？", "研究证据", [
            Custom(lambda c, g, t, d: K.icon(c, "question", 0, 0, 220, ACC, clamp01(g.since(0) / 0.3), 0.8, 0,
                                             0.4 + 0.6 * K.ease_out_back(clamp01(g.since(0) / 0.4), 2)),
                   x=540, y=760, at=0, enter="none", sfx="bongo_low", note="大问号"),
        ], text_beat=0, note="一个大问号"),
        Shot(2, "2015 年，一项|小型交叉试验：", "研究证据", [
            Custom(lambda c, g, t, d: K.pill(c, 0, 0, "Shukla 等 · Diabetes Care · 2015", 40, K.INK2, K.PAPER,
                                             clamp01(g.since(1) / 0.3)), x=540, y=760, at=0, enter="none",
                   sfx=None),
        ], hits=[(1, "wood_high", 0.7, "论文标签")], text_beat=0, note="论文标签：Shukla 等，Diabetes Care，2015"),
        Shot(4, "11 位患者，同样一餐：|先吃菜肉，血糖明显更低。", "研究证据", [
            Custom(study, x=540, y=820, at=0, enter="none"),
        ], research=True, hits=[(0, "wood_low", 0.7, "先吃碳水卡"), (2, "wood_high", 0.7, "先吃菜和蛋白质卡"),
                                (4, "shaker", 0.6, "尖峰曲线"), (6, "rim", 0.8, "平稳曲线")],
            note="两张卡：先吃碳水 vs 先吃菜和蛋白质，下面各画一条曲线（曲线为示意）"),
        Shot(3, "不是不吃碳水，|只是换个顺序。", "常见误解", [
            Custom(same_plate, x=540, y=780, at=0, enter="none"),
        ], hits=[(2, "rim", 0.8, "等号"), (6, "wood_high", 0.7, "“吃的东西不变”")],
            note="左右两盘一模一样的饭，中间等号：吃的东西不变，只换顺序"),
        Shot(3, "吃盖饭也可以：|先挑上面的菜和肉。", "情境演绎", [
            Custom(topping, x=540, y=760, at=0, enter="none"),
        ], hits=[(2, "wood_high", 0.7, "夹起青菜"), (5, "wood_low", 0.7, "夹起肉"), (8, "bongo_high", 0.7, "最后吃饭")],
            note="一碗盖饭：筷子先夹走上面的青菜，再夹肉，最后露出米饭"),
        Shot(4, "小练习：下一顿，|把米饭放到最后吃。", "小练习", [
            Custom(rice_last, x=540, y=780, at=0, enter="none"),
        ], hits=[(2, "shaker", 0.7, "米饭碗挪到最右"), (5, "wood_high", 0.7, "“最后吃”"), (8, "clap", 0.6, "完成")],
            note="米饭碗从盘中被挪到最右边，标“最后吃”"),
        Shot(2, "下一讲：|饭前先来一盘菜。", "书中观点", [
            Custom(lambda c, g, t, d: T.food(c, "salad", 0, 0, 260, clamp01(g.since(0) / 0.3), 0,
                                             0.4 + 0.6 * K.ease_out_back(clamp01(g.since(0) / 0.4), 1.8)),
                   x=540, y=760, at=0, enter="none", sfx="wood_high", note="一碗沙拉"),
            Bubble("先来一盘！", 760, 560, 40, at=2, sfx="bongo_high", note="气泡"),
        ], text_beat=0, note="一碗沙拉弹出，预告下一期"),
        ending(3, REFS),
    ]
    return Episode(3, "order", "进食顺序", TITLES[3], ACC, shots, refs=REFS,
                   publish_title=f"{TITLES[3]}｜控糖革命03 进食顺序", hashtags="#控糖 #进食顺序 #控糖革命 #健康 #科普",
                   cover_title="同一顿饭，|换个【顺序】吃？", cover_sub="控糖革命 · 方法 1", cover_shot=3, cover_t=5.5,
                   notes=[
                       "“先吃蔬菜，再吃蛋白质和脂肪，最后吃淀粉和糖”是书中第 1 个方法。",
                       "Shukla 等（2015，Diabetes Care 38(7):e98–e99）：11 位服用二甲双胍的 2 型糖尿病患者交叉试验，"
                       "同样一餐，先吃蔬菜和蛋白质、最后吃碳水时，餐后血糖明显更低。样本小，受试者为 2 型糖尿病患者。",
                       "“纤维像一张网减慢吸收”是书中的解释，第 7 镜为示意。所有曲线均为示意，不是论文数据。",
                   ], **SERIES).build()
