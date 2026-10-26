"""《毛选》系列：复用阿德勒纸片引擎（adler.core / adler.build），快节奏规则（每镜 ≤3 秒）。

用法：
    python3 -m maoxuan.build 01 --sheet     # 逐镜联系表
    python3 -m maoxuan.build 01             # 渲染到 out/maoxuan/ep01/
    python3 -m maoxuan.build --verify       # 核验成片
    python3 -m maoxuan.build --publish      # 交付到 videos/maoxuan/（另出 10 格合集图与 1080×1080 横屏封面）
"""

import sys

from adler import build as B
from adler import core

from . import ink

ink.install()

core.SERIES.update(name="毛选", count="10讲", prefix="毛选", tagline="把难题拆开的方法论，今天还管用")
B.PKG = "maoxuan"
B.OUT = B.ROOT / "out" / "maoxuan"
B.MODS = {"01": "ep01_investigation", "02": "ep02_contradiction", "03": "ep03_practice", "04": "ep04_piano",
          "05": "ep05_protracted", "06": "ep06_spark", "07": "ep07_friends", "08": "ep08_stereotyped",
          "09": "ep09_truth", "10": "ep10_yugong"}

# 系列规划：(期号, 概念, 片名)；已出的讲在合集图里放封面，未出的放“敬请期待”
PLAN = [
    ("01", "没有调查没有发言权", "汇报被领导一句话问住，差在哪？"),
    ("02", "抓主要矛盾", "事情一大堆，先干哪件？"),
    ("03", "实践论", "道理都懂，为什么还是做不好？"),
    ("04", "学会弹钢琴", "好几件事一起来，怎么不乱？"),
    ("05", "论持久战", "目标太远，怎么撑下去？"),
    ("06", "星星之火", "起点太低，还有戏吗？"),
    ("07", "谁是我们的朋友", "职场里，谁才是你的朋友？"),
    ("08", "反对党八股", "写的报告，为什么没人看？"),
    ("09", "实事求是", "开会说漂亮话，为什么没用？"),
    ("10", "愚公移山", "事太难，还干不干？"),
]


def series_cover(path=None):
    """合集图（1080×1080，≤5MB）：系列名 + 卖点 + 10 个格子，已出的讲放封面缩略图，未出的放期号与概念纸卡。"""
    import skia

    from adler import fx
    from adler import kit as K

    done = {k: B.load(k) for k in B.MODS}
    first = next(iter(done.values()))
    acc = first.accent
    S, head, cols, gap, lab = 1080, 250, 5, 16, 46
    tw = (S - (cols + 1) * gap) / cols
    th = tw * 16 / 9
    surf = B._surface(S, S)
    c = surf.getCanvas()
    B._paper(c, first, S, S)
    fx.rays(c, S / 2, 120, 700, K.GOLD, 0, 18, 0.16)
    K.text(c, B.BRAND, S / 2, 52, 32, "sans_medium", K.INK2)
    K.text(c, f"{core.SERIES['name']} · {core.SERIES['count']}", S / 2, 132, 96, "serif_black", acc,
           shadow=(6, 10, 10, K.SHADOW))
    K.text(c, core.SERIES["tagline"], S / 2, 210, 38, "sans_medium", K.INK)
    y0 = head + (S - head - 2 * (th + lab) - gap) / 2
    for i, (k, concept, _) in enumerate(PLAN):
        r, j = divmod(i, cols)
        x = gap + j * (tw + gap)
        y = y0 + r * (th + lab + gap)
        if k in done:
            img = skia.Image.open(str(B.OUT / f"ep{k}" / "cover.png"))
            K.card(c, x + tw / 2, y + th / 2, tw, th, K.PAPER, 1, r=12)
            c.save()
            c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, tw, th), 12, 12), doAntiAlias=True)
            c.drawImageRect(img, skia.Rect.MakeXYWH(x, y, tw, th), skia.SamplingOptions(skia.FilterMode.kLinear))
            c.restore()
            col = K.INK
        else:
            base = "#EFE2C6"
            K.card(c, x + tw / 2, y + th / 2, tw, th, base, 1, r=12)
            K.rr_stroke(c, x + tw / 2, y + th / 2, tw - 24, th - 24, 8, K.shade(base, 0.2), 3, 1, (12, 10))
            K.text(c, k, x + tw / 2, y + th / 2 - 50, 80, "serif_black", K.shade(base, 0.25))
            K.text(c, "敬请期待", x + tw / 2, y + th / 2 + 40, 30, "serif_black", K.shade(base, 0.4))
            col = K.INK3
        label = f"{k} {concept}"
        size = min(26.0, 26 * (tw - 6) / K.text_w(label, 26, "serif_black"))
        K.text(c, label, x + tw / 2, y + th + lab / 2 + 2, size, "serif_black", col)
    path = path or B.ROOT / "videos" / B.PKG / "合集.png"
    B._save_capped(surf.makeImageSnapshot(), path)
    return path


def square_cover(path=None):
    """横屏封面（1080×1080）：沿用引擎版式，下方纸片列出 10 讲概念（未出的讲同样列出，作为系列预告）。"""
    from types import SimpleNamespace

    first = B.load("01")
    eps = [(k, SimpleNamespace(no=int(k), concept=concept, accent=first.accent if k in B.MODS else "#B7A48A"))
           for k, concept, _ in PLAN]
    eps[0] = ("01", first)
    path = path or B.ROOT / "videos" / B.PKG / "横屏封面_1080x1080.png"
    B.square_cover(eps, path)
    return path


if __name__ == "__main__":
    if "--series" in sys.argv:
        print(series_cover())
        print(square_cover())
    else:
        B.main()
