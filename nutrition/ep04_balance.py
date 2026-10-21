"""04 动物也会配餐：黏菌没有大脑，却会挑食"""

import math

import skia

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Arrow, Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import art as A

ACC = "#B08A2A"
GROUND = A.GROUND_Y
REFS = ["Dussutour, A., et al. (2010). Amoeboid organism solves complex nutritional challenges. PNAS, 107(10).",
        "Johnson, C. A., et al. (2013). 30 days in the life: daily nutrient balancing in a wild chacma baboon. PLoS ONE.",
        "Rothman, J. M., Raubenheimer, D., & Chapman, C. A. (2011). Biology Letters, 7(6)."]


def ring_food(c, g, el_t, d):
    """黏菌放在中间，一圈 11 块配比不同的食物；d['grow'] 拍后菌体长向最佳那一块。"""
    R = 330
    best = 3
    for i in range(11):
        a = -math.pi / 2 + i / 11 * math.tau
        x, y = math.cos(a) * R, math.sin(a) * R
        pr = 0.2 + 0.6 * i / 10
        K.dot(c, x, y, 40, A.CARB)
        path = skia.Path()
        path.moveTo(x, y)
        path.arcTo(skia.Rect.MakeXYWH(x - 40, y - 40, 80, 80), -90, 360 * pr, False)
        path.close()
        c.drawPath(path, K.paint(A.PROTEIN))
        if i == best and g.since(d.get("grow", 99)) >= 0:
            K.ring(c, x, y, 52, K.GOLD, 6, ease_out(clamp01(g.since(d["grow"]) / 0.6)))
    p = ease_out(clamp01(g.since(d.get("grow", 99)) / 2.0)) if d.get("grow") is not None else 0.4
    a = -math.pi / 2 + best / 11 * math.tau
    A.slime(c, 0, 0, 220, 0.4 + 0.6 * p, g.t, 1, (math.cos(a), math.sin(a)) if p > 0.05 else None)


def build() -> Episode:
    shots = [
        Shot(3, "猫不会看营养成分表|为什么吃得这么准？", "情境演绎", [
            Custom(lambda c, g, t, d: A.cat(c, 0, 0, 340, t=g.t), x=420, y=GROUND, at=0, sfx="wood_low"),
            Icon("question", 740, 620, 110, color=ACC, at=4, sfx="rim"),
        ], draw=A.ground, note="一只坐着的猫"),
        Shot(3, "作者在很多动物身上|找到了同样的本事", "原书 · 大意", [
            Custom(lambda c, g, t, d: A.locust(c, 0, 0, 200, g.t), x=240, y=760, at=0, sfx="wood_low"),
            Custom(lambda c, g, t, d: A.mouse(c, 0, 0, 180, t=g.t), x=540, y=800, at=2, sfx="wood_low"),
            Custom(lambda c, g, t, d: A.baboon(c, 0, 0, 260, t=g.t), x=830, y=860, at=4, sfx="wood_low"),
        ], note="蝗虫、小鼠、狒狒"),
        Shot(2, "连没有大脑的生物|也会——", "原书 · 大意", [
            Custom(lambda c, g, t, d: A.slime(c, 0, 0, 300, ease_out(clamp01(t / 1.4)), g.t), x=540, y=760, at=0),
        ], text_beat=0, hits=[(4, "rim", 0.8, "黏菌定格")], note="黏菌展开"),
        Shot(4, "按营养比例|给自己配餐", "原书 · 大意", [
            Big("动物也会配餐", 540, 540, 120, at=0, sfx="kick", sub="Nutrient Balancing", note="概念落版（音乐 drop）"),
            Custom(lambda c, g, t, d: A.slime(c, 0, 0, 200, 1, g.t), x=540, y=960, at=2, enter="fade"),
        ], note="drop 处“动物也会配餐”砸下"),
        Shot(4, "把黏菌放在一圈|配比不同的食物中间", "研究证据", [
            Custom(ring_food, x=540, y=760, at=0, enter="fade", sfx="wood_low"),
            Txt("Dussutour 等，PNAS，2010", 540, 1160, 30, at=4, font="sans_medium", color=K.INK2),
        ], note="中心黏菌，周围 11 块食物"),
        Shot(4, "它会长向|配比最合适的那一块", "研究证据", [
            Custom(ring_food, x=540, y=760, at=0, enter="none", grow=1),
        ], hits=[(1, "wood_low", 0.6, "开始伸展"), (5, "clap", 0.8, "到达最佳配比")], note="菌体伸向最佳配比那一块"),
        Shot(4, "家猫：换着花样给吃的|它吃进的配比依然很稳", "研究证据", [
            Custom(lambda c, g, t, d: A.cat(c, 0, 0, 320, t=g.t), x=300, y=GROUND, at=0, enter="none"),
            Custom(lambda c, g, t, d: A.plate(c, 0, 0, 70, (0.5, 0.15, 0.35)), x=640, y=700, at=2, sfx="wood_low"),
            Custom(lambda c, g, t, d: A.plate(c, 0, 0, 70, (0.5, 0.15, 0.35)), x=840, y=900, at=4, sfx="wood_low", gain=0.85),
            Txt("Hewson-Hughes 等，2013", 540, 1220, 30, at=4, font="sans_medium", color=K.INK2),
        ], draw=A.ground, note="不同食物，最后的配比餐盘一样"),
        Shot(2, "城郊的一只狒狒|一个月配比都稳", "研究证据", [
            Custom(lambda c, g, t, d: A.baboon(c, 0, 0, 360, t=g.t), x=540, y=GROUND, at=0, sfx="wood_low"),
        ], draw=A.ground, text_beat=0, note="开普半岛的狒狒"),
        Shot(2, "就算它也吃|人类的食物", "研究证据", [
            Custom(lambda c, g, t, d: A.chips(c, 0, 0, 160), x=760, y=980, at=0, sfx="wood_high"),
            Custom(lambda c, g, t, d: A.baboon(c, 0, 0, 320, t=g.t, face=1), x=420, y=GROUND, at=0, enter="none"),
        ], draw=A.ground, text_beat=0, note="狒狒与零食袋"),
        Shot(3, "也有例外：|乌干达的山地大猩猩", "研究证据", [
            Custom(lambda c, g, t, d: A.gorilla(c, 0, 0, 380), x=540, y=GROUND, at=0, sfx="tom"),
            Txt("Rothman、Raubenheimer & Chapman，2011", 540, 1220, 30, at=2, font="sans_medium", color=K.INK2),
        ], draw=A.ground, note="大猩猩"),
        Shot(3, "树叶季它们吃下多余的蛋白|为的是凑够热量", "研究证据", [
            Icon("sprout", 360, 760, 180, color=A.LEAF, at=0, sfx="wood_low"),
            Arrow((480, 760), (640, 760), at=2, color=ACC, width=12, sfx="rim"),
            Label("热量优先", 780, 760, 40, at=4, fill=A.CARB, sfx="wood_high"),
        ], note="树叶 → 热量优先"),
        Shot(2, "动物配餐靠本能|不是靠营养表", "原书 · 大意", [
            Icon("heart", 540, 760, 200, color=K.RED, at=0, sfx="wood_low"),
        ], text_beat=0, note="心"),
        Shot(2, "试试：观察一下|家里宠物怎么吃", "小练习", [
            Custom(lambda c, g, t, d: A.cat(c, 0, 0, 300, t=g.t), x=540, y=GROUND, at=0, sfx="wood_high"),
        ], draw=A.ground, text_beat=0, note="猫"),
        Shot(2, "下一讲：|低蛋白为什么停不下嘴", "下一讲", [
            Custom(lambda c, g, t, d: A.lever(c, 0, 0, 320, -8), x=480, y=800, at=0, sfx="wood_high"),
        ], text_beat=0, note="预告第 05 讲：蛋白质杠杆"),
        end_shot(REFS, "05 蛋白质杠杆：为什么低蛋白饮食让人停不下嘴？"),
    ]
    return Episode(4, "balance", "动物也会配餐", "黏菌没有大脑，却会挑食", ACC, shots, refs=REFS,
                   publish_title="黏菌没有大脑，却会挑食｜动物为什么吃不胖04 动物也会配餐",
                   hashtags="#动物为什么吃不胖 #营养学 #黏菌 #猫",
                   cover_title="黏菌没有大脑|却会【挑食】", cover_sub="动物为什么吃不胖 · 动物也会配餐", cover_shot=5, cover_t=6.0,
                   notes=["黏菌实验见 Dussutour 等（2010，PNAS）：多头绒泡菌在多块蛋白质碳水配比不同的食物之间，会长向配比最合适的一块。片中 11 块食物为示意。",
                          "家猫见 Hewson-Hughes 等（2013，Journal of Nutrition）：换着给不同成分的食物，成年家猫选择的宏量营养比例保持一致。",
                          "狒狒见开普半岛一只城郊狒狒连续 30 天的营养几何分析，即使吃人类食物，蛋白质与非蛋白能量的比例依然稳定。",
                          "大猩猩是例外：Rothman 等（2011，Biology Letters）发现乌干达山地大猩猩优先保证非蛋白能量，树叶季会吃下多余的蛋白质；原书在「寻找例外」一章讨论这一类情况。"]).build()
