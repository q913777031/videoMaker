"""06 处女座：处女座，天上到底长什么样？"""

import math

import skia

from engine.gfx import clamp01, ease_in_out, ease_out

from adler import kit as K
from adler.core import Custom, Label, Shot, Txt

from . import kit_xz as X
from .series import GROUND, episode

AB = "Vir"
WHEAT = "#D9A441"
M87 = (187.71, 12.39)          # M87 星系（J2000 赤经、赤纬，度）


def wheat(c, x, y, s, alpha=1.0):
    """一束麦穗：三根麦秆，顶端一串麦粒（以麦秆底部为原点）。"""
    for i, ang in enumerate((-14, 0, 14)):
        a = math.radians(ang)
        tx, ty = x + math.sin(a) * s, y - math.cos(a) * s
        K.seg(c, x, y, tx, ty, K.shade(WHEAT, 0.25), 6, alpha)
        for j in range(6):
            q = 0.55 + j * 0.08
            px, py = x + math.sin(a) * s * q, y - math.cos(a) * s * q
            for side in (-1, 1):
                with K.at(c, px + side * 9, py, ang + side * 28):
                    K.rr(c, 0, 0, 14, 26, 7, WHEAT, alpha)


def goddess(c, g, t, d):
    """正义女神手持麦穗，第 6 拍缓缓升向星空；身后小星点逐个亮起。"""
    rise = ease_in_out(clamp01(g.since(6) / 1.4))
    y = -rise * 160
    for i in range(14):
        k = clamp01(g.since(4 + i * 0.3) / 0.3)
        if k > 0:
            ang = i * 2.4
            X.star_icon(c, math.cos(ang) * (260 + 30 * (i % 3)), -260 + math.sin(ang) * 120 - 60, 10 + 4 * (i % 2),
                        K.GOLD, k * (0.6 + 0.4 * math.sin(g.t * 3 + i)))
    k = clamp01(g.since(2) / 0.35)
    K.figure(c, 0, 300 + y, 400, "reach", "#8E7AA8", hair="long", mood="calm", face=1, lift=0.8)
    if k > 0:
        wheat(c, 120, 50 + y, 150 * (0.4 + 0.6 * K.ease_out_back(k, 1.8)), k)
        K.spotlight(c, 120, -60 + y, 90 * k, K.GOLD, 0.4 * k)


def ground_draw(g):
    K.ground(g.c, GROUND, 1 - ease_out(clamp01(g.since(6) / 1.0)) * 0.7)


def longest(c, g, t, d):
    """黄道星座条：室女座一段高亮，上方括号标出太阳停留的 45 天。"""
    a, b, n = X.DATA["sun"][AB]
    X.ecliptic_strip(c, 0, 0, 960, 130, (AB,), (a, b), clamp01(g.since(1) / 0.5), None, 1, True, 0.0, 26,
                     f"{n} 天")
    k = clamp01(g.since(3) / 0.35)
    if k > 0:
        with K.at(c, 0, -300, 0, 0.4 + 0.6 * K.ease_out_back(k, 1.8)):
            K.text(c, f"{n}", -40, 0, 170, "serif_black", g.acc, k, "right")
            K.text(c, "天", -20, 30, 64, "serif_black", K.INK, k, "left")
        K.text(c, "全天面积第二，仅次于长蛇座", 0, 230, 34, "sans_medium", K.INK2, k)


def black_hole(c, g, t, d):
    """星图上标出 M87，第 2 拍弹出黑洞照片示意圈（橙色光环）。"""
    def extra(c, P):
        px, py = P(*M87)
        k = clamp01(g.since(1) / 0.3)
        if k > 0:
            K.ring(c, px, py, 22 + 10 * (1 - k), "#FF9F80", 5, k)
            K.text(c, "M87", px + 34, py - 34, 34, "sans_medium", "#FFC9B8", k, "left")
        q = clamp01(g.since(2) / 0.4)
        if q > 0:
            ix, iy = 250, 120
            K.seg(c, px, py, lerp_pt(px, ix, q), lerp_pt(py, iy, q), "#FF9F80", 3, q)
            with K.at(c, ix, iy, 0, 0.3 + 0.7 * K.ease_out_back(q, 1.6)):
                K.dot(c, 0, 0, 120, "#0B0B12", q)
                sh = skia.GradientShader.MakeSweep(0, 0, [K.col("#FFB347", q), K.col("#8A2B0E", q), K.col("#FFD27A", q),
                                                          K.col("#FFB347", q)], [0, 0.45, 0.8, 1])
                p = skia.Paint(AntiAlias=True, Shader=sh, Style=skia.Paint.kStroke_Style, StrokeWidth=34)
                p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 9))
                c.drawCircle(0, 0, 66, p)
                K.dot(c, 0, 0, 44, "#050508", q)
                K.text(c, "2019", 0, 150, 30, "sans_medium", "#FFC9B8", q)
    X.sky_card(c, 0, 0, 900, 660, AB, 1, g.t, 1, line_color=X.FAINT, margin=90, extra=extra)


def lerp_pt(a, b, k):
    return a + (b - a) * k


def build():
    mid = [
        Shot(3, "神话里，她是最后|离开人间的正义女神。", "希腊神话", [
            Custom(goddess, x=540, y=830, at=0, enter="fade"),
            Label("阿斯特赖亚", 300, 520, 32, at=3, fill="#8E7AA8", sfx="wood_high", note="名字标签"),
            Txt("手中麦穗：角宿一 Spica，拉丁文意为“麦穗”", 540, 1245, 28, at=4, font="sans_medium", color=K.INK2),
        ], draw=ground_draw, hits=[(2, "wood_low", 0.8, "麦穗出现"), (6, "shaker", 0.7, "女神升向星空")],
            note="正义女神手持麦穗，第 6 拍缓缓升向星空，身后星点亮起"),
        Shot(2, "最大的黄道星座，|太阳走 45 天。", "天文观测", [
            Custom(longest, x=540, y=820, at=0, enter="fade"),
        ], hits=[(1, "wood_high", 0.8, "括号标出 45 天"), (3, "rim", 0.9, "“45 天”砸出")], text_beat=0,
            note="黄道星座条上室女座最长，括号标出太阳停留 45 天；全天面积第二"),
        Shot(2, "第一张黑洞照片，|就拍在室女座方向。", "天文观测", [
            Custom(black_hole, x=540, y=800, at=0, enter="fade"),
        ], hits=[(1, "wood_low", 0.8, "M87 圈出"), (2, "bongo_high", 0.85, "黑洞照片示意弹出")], text_beat=0,
            note="室女座星图上圈出 M87，旁边弹出橙色光环的黑洞照片示意（2019）"),
    ]
    return episode(
        6, AB, "处女座：|天文上叫“室女座”。", mid,
        refs=["阿拉托斯《物象》", "EHT 合作组（2019），ApJL 875, L1"],
        notes=[
            "神话版本不一：处女座常被认作正义女神阿斯特赖亚（人类堕落后最后一个离开人间的神），也有说法认作手持麦穗的农业女神"
            "得墨忒耳或其女珀耳塞福涅。",
            "角宿一的西方名 Spica 来自拉丁文，意思是“麦穗”。",
            "室女座面积约 1294 平方度，是黄道星座中最大的、全天第二大（仅次于长蛇座）；按 IAU 边界计算，太阳每年在室女座停留约 45 天，"
            "为黄道星座中最长。",
            "2019 年 4 月，事件视界望远镜（EHT）发布第一张黑洞照片，对象是室女座方向 M87 星系中心的黑洞（距离约 5500 万光年）。"
            "片中光环为示意画，不是原始图像。",
            "占星“处女座”在天文学中的正式中文名是“室女座”。",
        ],
        hashtags="#处女座 #星座 #天文 #科普 #黑洞",
        cover_title="生日在处女座，|太阳却在【狮子座】？", cover_sub="处女座：天上到底长什么样")
