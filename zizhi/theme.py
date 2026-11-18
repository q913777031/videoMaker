"""《资治通鉴》每讲一个样式（字段同 fengtian/theme.py 的 THEMES，由 fengtian.theme.finish 补齐派生色）。

纸张多用古风纹理：宣纸 xuan、竹简 bamboo、绢本 silk（fengtian/theme.py board_bg 里），也穿插丰田用过的点阵、方格、黑板，
相邻两讲纸色、纹理、主题色、页眉、开场钩子、转场都不同。主题色多取传统色：朱砂、黛青、石绿、赭石、藤黄……
"""
from fengtian import theme as FT

THEMES = {
    "01": dict(name="宣纸朱砂", acc="#B23A2B", paper="#F4ECDB", pattern="xuan", pat="#B9A27A",
               header="stamp", hook="zz_credit", move="pullpush", move_s=1.4),
    "02": dict(name="竹简黛青", acc="#2B4C6F", paper="#EBDDB5", pattern="bamboo", pat="#B79B5E", rope="#7A5B2E", grid=110,
               header="bar", hook="zz_unread", move="pan", move_s=1.35),
    "03": dict(name="墨色黑板", acc="#E8B04B", paper="#24302B", pattern="chalk", pat="#FFFFFF", dark=True,
               header="tab", hook="zz_slides", move="tilt", move_s=1.4),
    "04": dict(name="绢本石绿", acc="#2F7D5B", paper="#EFE4CC", pattern="silk", pat="#A88C5C",
               header="circle", hook="zz_blush", move="swing", move_s=1.3),
    "05": dict(name="赭石方格", acc="#9A4A1C", paper="#F3E6CF", pattern="grid", pat="#D9BE94", grid=90,
               header="stamp", hook="zz_rules", move="drop", move_s=1.3),
    "06": dict(name="藏青蓝图", acc="#F2B45A", paper="#1E2D45", pattern="blueprint", pat="#6E8FC4", dark=True,
               header="tab", hook="zz_tall", move="arc", move_s=1.4),
    "07": dict(name="竹简赭红", acc="#A0352A", paper="#EADCB8", pattern="bamboo", pat="#B79B5E", rope="#7A5B2E", grid=130,
               header="pill", hook="zz_toss", move="wipe", move_s=1.05),
    "08": dict(name="绢本绛紫", acc="#7A2E5C", paper="#F1E6D6", pattern="silk", pat="#A88C6C",
               header="bar", hook="zz_shots", move="pullpush", move_s=1.35),
    "09": dict(name="宣纸石青", acc="#1F5F7A", paper="#F2EEE3", pattern="xuan", pat="#9DB3BA",
               header="circle", hook="zz_knock", move="swing", move_s=1.3),
}


def get(nn):
    return FT.finish(dict(THEMES[nn]))
