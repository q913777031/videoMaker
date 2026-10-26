"""《资治通鉴》系列：复用阿德勒纸片引擎（adler.core / adler.build），快节奏规则（每镜 ≤3 秒）。

用法：
    python3 -m zizhi.build 01 --sheet     # 逐镜联系表
    python3 -m zizhi.build 01             # 渲染到 out/zizhi/ep01/
    python3 -m zizhi.build --verify       # 核验成片
    python3 -m zizhi.build --publish      # 交付到 videos/zizhi/
"""

from adler import build as B
from adler import core

core.SERIES.update(name="资治通鉴", count="10讲", prefix="资治通鉴", tagline="两千年前的识人术，今天还管用")
B.PKG = "zizhi"
B.OUT = B.ROOT / "out" / "zizhi"
B.MODS = {"01": "ep01_talent_virtue"}

if __name__ == "__main__":
    B.main()


def series_cover(done: list[str], total: int = 10):
    """合集封面：系列名 + 一句话卖点 + total 个格子，已出的讲放封面缩略图，未出的放“敬请期待”纸卡。"""
    import skia

    from adler import fx
    from adler import kit as K

    eps = [(k, B.load(k)) for k in done]
    acc = eps[0][1].accent
    cols, tw, th, gap, head = 5, 300, 533, 36, 420
    rows = (total + cols - 1) // cols
    W = cols * tw + (cols + 1) * gap
    H = head + rows * (th + 120) + gap
    surf = B._surface(W, H)
    c = surf.getCanvas()
    B._paper(c, eps[0][1], W, H)
    fx.rays(c, W / 2, 190, 1100, K.GOLD, 0, 18, 0.18)
    K.text(c, B.BRAND, W / 2, 80, 40, "sans_medium", K.INK2)
    K.text(c, core.SERIES["name"], W / 2, 210, 170, "serif_black", acc, shadow=(8, 12, 12, K.SHADOW))
    K.text(c, f"{core.SERIES['tagline']} · {core.SERIES['count']}", W / 2, 350, 52, "serif_black", K.INK)
    shots = dict(eps)
    for i in range(total):
        k = f"{i + 1:02d}"
        x = gap + (i % cols) * (tw + gap)
        y = head + (i // cols) * (th + 120)
        if k in shots:
            img = skia.Image.open(str(B.OUT / f"ep{k}" / "cover.png"))
            K.card(c, x + tw / 2, y + th / 2, tw, th, K.PAPER, 1, r=18)
            c.save()
            c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, tw, th), 18, 18), doAntiAlias=True)
            c.drawImageRect(img, skia.Rect.MakeXYWH(x, y, tw, th), skia.SamplingOptions(skia.FilterMode.kLinear))
            c.restore()
            label, col = shots[k].concept, K.INK
        else:
            K.card(c, x + tw / 2, y + th / 2, tw, th, "#EFE2C6", 1, r=18)
            K.rr_stroke(c, x + tw / 2, y + th / 2, tw - 40, th - 40, 12, K.shade("#EFE2C6", 0.2), 4, 1, (18, 14))
            K.text(c, k, x + tw / 2, y + th / 2 - 40, 110, "serif_black", K.shade("#EFE2C6", 0.25))
            K.text(c, "敬请期待", x + tw / 2, y + th / 2 + 70, 40, "serif_black", K.shade("#EFE2C6", 0.4))
            label, col = "待更新", K.INK3
        K.rr(c, x + 44, y + th + 50, 72, 44, 22, acc if k in shots else K.INK3)
        K.text(c, k, x + 44, y + th + 50, 28, "black", K.PAPER)
        K.text(c, label, x + 92, y + th + 50, 36, "serif_black", col, 1, "left")
    path = B.ROOT / "videos" / PKG_DIR / "合集.png"
    surf.makeImageSnapshot().save(str(path), skia.kPNG)
    return path


PKG_DIR = "zizhi"
