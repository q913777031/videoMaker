"""《资治通鉴》系列共用：快节奏镜头模板（每镜 1 小节）、片尾与 Episode 构造。"""

from adler import kit as K
from adler.core import Episode, G, Glow, Pops, Shot, W

from . import art as A

BOOK = "司马光《资治通鉴》"
TAGS = "#资治通鉴 #司马光 #历史 #读书 #识人"


def S(text, tag, els, **kw):
    """快节奏镜头：1 小节（≈2.1 秒），字幕在第 0 拍出现。"""
    kw.setdefault("text_beat", 0)
    return Shot(1, text, tag, els, **kw)


def pops(words, tag, size=110, flash=None, extra=(), **kw):
    """纯弹字镜头（字幕留空）：每拍一个词。"""
    return S("", tag, [Glow(540, 780, 560, at=0, alpha=0.26), Pops(words, 540, 780, size, at=0, step=1)] + list(extra),
             punch=0.02, flashes=[flash] if flash is not None else [], note="弹字", **kw)


def outro(question: str, next_title: str | None, text: str) -> Shot:
    """片尾：天平落定 + 评论区问题卡 + 下一讲预告；最后一击落在原曲最后一个强拍。"""

    def draw(g: G):
        c = g.c
        with K.at(c, W / 2, 620, 0, 1.0):
            K.icon(c, "scale", 0, 0, 260, A.INKWASH, g.p(0, 0.4), 0.8, 0, 1, 0.0, g.acc)
        K.card(c, W / 2, 900, 860, 150, K.PAPER, g.p(1, 0.3), r=30, accent=g.acc)
        K.text(c, question, W / 2, 905, 46, "serif_black", K.INK, g.p(1, 0.3))
        ap = g.p(2, 0.4)
        K.text(c, "下一讲", W / 2, 1060, 34, "sans_medium", K.INK3, ap)
        K.text(c, next_title or "敬请期待", W / 2, 1130, 50, "serif_black", g.acc, ap)

    return Shot(1, text, "评论区见", [], over=draw, text_beat=0, note="片尾：互动与下一讲预告",
                hits=[(0, "cymbal", 0.5, "片尾落版"), (1, "pop", 0.8, "问题卡"), (2, "wood_high", 0.7, "下一讲"),
                      (4, "kick", 0.55, "原曲最后一击")])


def episode(no, key, concept, title, acc, shots, refs, cover_title, cover_shot, notes, tags="") -> Episode:
    return Episode(no, key, concept, title, acc, shots, refs=refs, publish_title=f"Vibe知识大赏｜{title}",
                   hashtags=f"{TAGS} {tags}".strip(), cover_title=cover_title, cover_sub=f"资治通鉴 · {concept}",
                   cover_shot=cover_shot, cover_t=1.5, notes=notes).build()
