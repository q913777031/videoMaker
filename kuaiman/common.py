"""《思考，快与慢》系列共用：Episode 构造。"""

from adler.core import Episode

BOOK = "丹尼尔·卡尼曼《思考，快与慢》（Thinking, Fast and Slow）"
TAGS = "#思考快与慢 #卡尼曼 #心理学 #读书 #打工人"


def episode(no, key, concept, title, acc, shots, refs, cover_title, cover_shot, notes, tags="") -> Episode:
    return Episode(no, key, concept, title, acc, shots, refs=refs, publish_title=f"Vibe知识大赏｜{title}",
                   hashtags=f"{TAGS} {tags}".strip(), cover_title=cover_title, cover_sub=f"思考，快与慢 · {concept}",
                   cover_shot=cover_shot, cover_t=1.5, notes=notes).build()


# ---------------------------------------------------------------- 系列角色：快快（系统1）与慢慢（系统2）
# 快快：红笔，头顶一道闪电，动作快、爱抢答；慢慢：蓝笔，圆眼镜，爱偷懒，能不动就不动。
# 两个函数返回 skia.Path，与 whiteboard.engine.stick 同一坐标约定：(x, y) 为脚底，身高约 330·s；五官另用 face() 画。

import skia  # noqa: E402

from whiteboard.engine import P, circle, join, stick  # noqa: E402

KUAI = "快快"
MAN = "慢慢"


def kuai(x, y, s=1.0, arms="up") -> skia.Path:
    """快快：小人 + 头顶闪电。建议用 RED 描。"""
    hy = y - 290 * s
    bolt = P((x + 8 * s, hy - 120 * s), (x - 18 * s, hy - 78 * s), (x + 6 * s, hy - 78 * s), (x - 14 * s, hy - 48 * s))
    return join(stick(x, y, s, arms), bolt)


def man(x, y, s=1.0, arms="down") -> skia.Path:
    """慢慢：小人 + 圆眼镜。建议用 BLUE 描。"""
    hy = y - 290 * s
    glasses = join(circle(x - 16 * s, hy - 8 * s, 13 * s), circle(x + 16 * s, hy - 8 * s, 13 * s),
                   P((x - 3 * s, hy - 10 * s), (x + 3 * s, hy - 10 * s)))
    return join(stick(x, y, s, arms), glasses)
