"""《资治通鉴》系列级交付：合集.png（各讲封面拼图）、系列横屏封面_1080x1080.png、合集简介.txt（取自 PLAN.md）。

用法：python3 -m zizhi.series   → videos/zizhi/ 下三个文件（各讲交付目录需已有 cover.png）
版式同丰田（fengtian/series.py）：1080×1080，单张 ≤5MB（超限自动减色压缩）。
"""
import re
import sys
from pathlib import Path

import skia

from adler import kit as K
from adler.build import BRAND, _save_capped
from engine import wording
from fengtian import series as FS

ROOT = Path(__file__).resolve().parent.parent
DST = ROOT / "videos" / "zizhi"
ACC = "#B23A2B"
BG = skia.Color(244, 236, 219)
S = 1080


def episodes():
    out = []
    for d in sorted(DST.iterdir()):
        m = re.match(r"(\d\d)_(.+)", d.name)
        if d.is_dir() and m and (d / "cover.png").exists():
            out.append((int(m.group(1)), m.group(2), d / "cover.png"))
    return out


def intro_text():
    s = (Path(__file__).with_name("PLAN.md")).read_text(encoding="utf-8")
    return re.search(r"## 三、合集简介\s*```text\n(.*?)```", s, re.S).group(1).strip() + "\n"


def collage(eps, path, head):
    surf = FS._surf()
    c = surf.getCanvas()
    c.drawColor(BG)
    K.text(c, BRAND, S / 2, 56, 34, "sans_medium", K.INK2)
    K.text(c, head, S / 2, 130, min(58.0, 58 * 1000 / K.text_w(head, 58, "serif_black")), "serif_black", ACC)
    cols = 5 if len(eps) > 8 else max(1, min(4, len(eps)))
    gap, lab, top = 16, 46, 190
    rows = (len(eps) + cols - 1) // cols
    tw = min((S - (cols + 1) * gap) / cols, ((S - top - 30) / rows - lab - gap) / 1.5)
    th = tw * 1.5
    y0 = top + (S - top - rows * (th + lab + gap) + gap) / 2
    for i, (no, concept, cover) in enumerate(eps):
        r, j = divmod(i, cols)
        n_row = min(cols, len(eps) - r * cols)
        x = S / 2 - (n_row * tw + (n_row - 1) * gap) / 2 + j * (tw + gap)
        y = y0 + r * (th + lab + gap)
        K.card(c, x + tw / 2, y + th / 2, tw, th, K.PAPER, 1, r=10)
        c.save()
        c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, tw, th), 10, 10), doAntiAlias=True)
        c.drawImageRect(skia.Image.open(str(cover)), skia.Rect.MakeXYWH(x, y, tw, th),
                        skia.SamplingOptions(skia.FilterMode.kLinear))
        c.restore()
        label = f"{no:02d} {concept}"
        K.text(c, label, x + tw / 2, y + th + lab / 2 + 2, min(30.0, 30 * (tw - 8) / K.text_w(label, 30, "serif_black")),
               "serif_black", K.INK)
    _save_capped(surf.makeImageSnapshot(), path)


def square_cover(eps, path, sub):
    surf = FS._surf()
    c = surf.getCanvas()
    c.drawColor(BG)
    K.text(c, BRAND, S / 2, 120, 40, "sans_medium", K.INK2)
    K.text(c, "资治通鉴", S / 2, 330, 200, "serif_black", ACC)
    K.text(c, sub, S / 2, 500, min(64.0, 64 * 960 / K.text_w(sub, 64, "serif_black")), "serif_black", K.INK)
    K.text(c, "每讲约三分钟 · 白板手绘", S / 2, 580, 38, "sans_medium", K.INK2)
    cols, w, h, gx, gy = 5, 184, 70, 18, 16
    for i, (no, concept, _) in enumerate(eps):
        r, j = divmod(i, cols)
        x = S / 2 - (cols * w + (cols - 1) * gx) / 2 + j * (w + gx) + w / 2
        y = 670 + r * (h + gy) + h / 2
        K.card(c, x, y, w, h, K.PAPER, 1, r=14)
        K.text(c, f"{no:02d}", x - w / 2 + 32, y, 28, "black", ACC)
        K.text(c, concept, x + 18, y, min(34.0, 34 * 110 / K.text_w(concept, 34, "serif_black")), "serif_black", K.INK)
    _save_capped(surf.makeImageSnapshot(), path)


def main():
    eps = episodes()
    intro = intro_text()
    for h in wording.check(intro):
        print(f"  文案警告 合集简介：{h}")
    title = intro.splitlines()[0]
    sub = title.split("｜", 1)[1] if "｜" in title else title
    (DST / "合集简介.txt").write_text(intro, encoding="utf-8")
    collage(eps, DST / "合集.png", title.replace("｜", " · "))
    square_cover(eps, DST / "横屏封面_1080x1080.png", sub)
    print(f"{len(eps)} 讲 →", DST / "合集.png", DST / "横屏封面_1080x1080.png", DST / "合集简介.txt", file=sys.stdout)


if __name__ == "__main__":
    main()
