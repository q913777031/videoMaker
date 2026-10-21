"""《十二星座》系列共用：十二星座表、留存骨架的镜头模板与 Episode 构造。

每讲镜头小节数固定为 2,2,4 | 4,4,4 | 4,4,4,2 | 2,2,2,2（共 42 小节）：
钩子 → 先说结论 → 日常情境 → drop 星座落版 → 性格高光 → 金句 → 二次钩子 → 加分项×3 → 误解重击 → 真相 → 互动 → 片尾。
星座性格是大众文化里的常见印象，整个系列为娱乐向，不作任何科学结论；每讲 notes 里写明。
"""

from dataclasses import dataclass

from adler import kit as K
from adler.core import END, Big, Custom, Episode, Fig, G, Glow, Pops, Rays, Shot, Spark, W

from . import art as A

TAGS = "#十二星座 #星座 #星座性格 #星座解读"


@dataclass(frozen=True)
class Sign:
    no: int
    key: str
    name: str
    en: str
    dates: str
    element: str


SIGNS = [
    Sign(1, "aries", "白羊座", "Aries", "3.21 – 4.19", "火"),
    Sign(2, "taurus", "金牛座", "Taurus", "4.20 – 5.20", "土"),
    Sign(3, "gemini", "双子座", "Gemini", "5.21 – 6.21", "风"),
    Sign(4, "cancer", "巨蟹座", "Cancer", "6.22 – 7.22", "水"),
    Sign(5, "leo", "狮子座", "Leo", "7.23 – 8.22", "火"),
    Sign(6, "virgo", "处女座", "Virgo", "8.23 – 9.22", "土"),
    Sign(7, "libra", "天秤座", "Libra", "9.23 – 10.23", "风"),
    Sign(8, "scorpio", "天蝎座", "Scorpio", "10.24 – 11.22", "水"),
    Sign(9, "sagittarius", "射手座", "Sagittarius", "11.23 – 12.21", "火"),
    Sign(10, "capricorn", "摩羯座", "Capricorn", "12.22 – 1.19", "土"),
    Sign(11, "aquarius", "水瓶座", "Aquarius", "1.20 – 2.18", "风"),
    Sign(12, "pisces", "双鱼座", "Pisces", "2.19 – 3.20", "水"),
]


def sign(key: str) -> Sign:
    return next(s for s in SIGNS if s.key == key)


def hook(words, tag, size=100):
    """0–4 秒钩子：问题逐词弹出 + 闪白；tag 写成“白羊座请进”，让目标观众一眼看到自己。"""
    return Shot(2, "", tag, [Glow(540, 760, 520, at=0, alpha=0.3), Pops(words, 540, 760, size, at=0, step=1)],
                punch=0.025, flashes=[0], note="钩子：问题逐词弹出")


def loop(text, pose="proud", mood="happy", **fig):
    """4–8 秒：一句话点明主题、先夸为敬，并留悬念；火苗在第 1 拍弹出。"""
    fig.setdefault("hair", "short")
    return Shot(2, text, "先说结论", [Fig(540, A.GROUND_Y, 330, at=0, pose=pose, mood=mood, **fig),
                                     Custom(A.flame, x=770, y=560, at=1, enter="pop", s=170, sfx="rim"),
                                     Spark(770, 560, at=1)], draw=A.ground, text_beat=0, note="一句话点题")


def drop(s: Sign, text, mascot=None, size=190):
    """17.14 秒音乐 drop：星座名砸下（光束 + 光晕 + 扫光 + 星光 + 闪白 + 抖动），第 2 拍吉祥物弹出。"""
    top = Custom(mascot, x=540, y=470, at=2, enter="pop", s=150, sfx="ding", glow=True) if mascot else \
        Custom(A.glyph, x=540, y=470, at=2, enter="pop", sign=s.key, s=150, sfx="ding")
    return Shot(4, text, "黄道第一宫" if s.no == 1 else f"黄道第{s.no}宫",
                [Big(s.name, 540, 790, size, at=0, sfx="kick", sub=f"{s.en} · {s.dates}", rays=True, glow=True,
                     shine=True, spark=True, note="星座落版（音乐 drop）"), top, Spark(540, 470, at=2)],
                punch=0.035, flashes=[0], shake=[0], note="drop 处星座名砸下")


def line(words, size=96, flash=6, gap=26):
    """金句：纯逐词弹出，字幕留空。"""
    return Shot(4, "", "一句话", [Glow(540, 780, 560, at=0, alpha=0.26), Pops(words, 540, 780, size, at=0, step=1, gap=gap)],
                punch=0.02, flashes=[flash], note="金句逐词弹出")


def hook2(text, n, sub, tag="重点来了"):
    """≈45 秒二次钩子：一个数字砸下（“还有 N 个隐藏加分项”）。"""
    return Shot(4, text, tag, [Big(str(n), 540, 720, 230, at=0, sfx="kick", sub=sub, sub_size=48, rays=True, glow=True,
                                   shine=True, spark=True, note="二次钩子：数字砸下")],
                punch=0.03, flashes=[0], shake=[0], note="二次钩子")


def slam(word, text, tag="常见误解", size=170):
    """2 小节重击：一个词砸下。"""
    return Shot(2, text, tag, [Big(word, 540, 760, size, at=0, sfx="kick", glow=True)], text_beat=0, punch=0.03,
                shake=[0], note=f"{word}砸下")


def cta(text, tag="互动", pose="cheer", mascot=None, **fig):
    """回报：请观众转发 / 认领；欢呼人物 + 光束 + 拍手。"""
    fig.setdefault("hair", "short")
    els = [Rays(540, 760, 520, at=0, alpha=0.18), Fig(440, A.GROUND_Y, 330, at=0, pose=pose, mood="happy", **fig),
           Spark(440, 560, at=1, sfx="clap")]
    if mascot:
        els.append(Custom(mascot, x=760, y=640, at=2, enter="pop", s=150, sfx="pop"))
    return Shot(2, text, tag, els, draw=A.ground, text_beat=0, punch=0.02, note="回报：转发与认领")


def outro(s: Sign, next_s: Sign | None, next_title: str, cta_text: str, mascot=None, bars: int = 2) -> Shot:
    """片尾：星群亮起 + 吉祥物 + 评论区互动 + 下一讲预告；最后一击落在原曲最后一个强拍。"""

    def draw(g: G):
        c = g.c
        a = g.p(0, 0.5)
        with K.at(c, W / 2, 700), K.fade(c, a):
            if mascot:
                mascot(c, g, g.since(0), {"s": 170, "glow": True})
            else:
                A.glyph(c, g, g.since(0), {"sign": s.key, "s": 170})
        lines = cta_text.split("|")
        for i, ln in enumerate(lines):
            K.text(c, ln, W / 2, 830 + i * 76, 54, "serif_black", K.INK, g.p(1 + i, 0.4))
        ap = g.p(4, 0.5)
        if next_s:
            K.text(c, "下一讲", W / 2, 1090, 34, "sans_medium", K.INK3, ap)
            K.text(c, f"{next_s.no:02d} {next_s.name} · {next_s.dates}", W / 2, 1160, 48, "serif_black", g.acc, ap)
            size = min(50.0, 50 * 900 / max(1.0, K.text_w(next_title, 50, "serif_black")))
            K.text(c, next_title, W / 2, 1236, size, "serif_black", K.INK, ap)
        else:
            K.text(c, "十二星座 · 全系列完", W / 2, 1180, 56, "serif_black", g.acc, ap)

    def under(g: G):
        with K.at(g.c, 540, 470):
            A.constellation(g.c, g, g.t, {"b0": 0, "step": 1, "scale": 0.75})

    return Shot(bars, "", "下一讲", [], draw=under, over=draw, note="片尾：星群、互动与下一讲预告",
                hits=[(0, "cymbal", 0.5, "片尾落版"), (4 * bars, "kick", 0.55, "原曲最后一击")])


def episode(s: Sign, title, acc, shots, cover_title, notes, tags="") -> Episode:
    return Episode(s.no, s.key, s.name, title, acc, shots, refs=[], publish_title=f"Vibe知识大赏｜{title}",
                   hashtags=f"#{s.name} {TAGS} {tags}".strip(), cover_title=cover_title,
                   cover_sub=f"{s.name} · {s.dates}", cover_shot=3, cover_t=1.6, notes=notes).build()


_ = END
