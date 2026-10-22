"""《传习录》系列的成片类：在 engine.timeline.Video 上换成宣纸底、墨色逐字字幕与系列页眉。

排时、卡点（场景切换吸附半小节线、drop 对齐）、旁白混音、渲染全部沿用引擎。
"""

import math

import skia

from engine import gfx, timeline
from engine.timeline import Event, Line, Scene, Video

from . import ink, script, voice

INK_HEX, CINNABAR_HEX = "#1E1B18", "#B2332A"
PALETTES = {"paper": {"bg": ["#EEE5D1", "#E6DAC0"], "blobs": ["#EEE5D1", "#E6DAC0", "#EEE5D1"], "dust": "#000000",
                      "dust_n": 0, "dust_a": 0.0, "hi": CINNABAR_HEX}}
CAPTION_Y, CAPTION_SIZE, CAPTION_W = 1500, 50, 900


class InkVideo(Video):
    """宣纸水墨版 Video：背景为固定宣纸纹理（全分辨率），字幕为宋体墨色逐字点亮，左上角系列页眉。"""

    def __init__(self, scenes: list[Scene], header: str, drop_at: str | None = None):
        super().__init__(scenes, PALETTES, voice=voice.VOICE, base_speed=1.0, drop_at=drop_at)
        self.header = header

    def build(self, with_audio: bool = True):
        super().build(with_audio)
        self.punches = [(t, s * 0.5) for t, s in self.punches]

    def draw_background(self, c: skia.Canvas, frame: int):
        c.clear(ink.color(ink.PAPER))

    def draw_foreground(self, c: skia.Canvas, frame: int) -> float:
        ink.draw_paper(c)
        amount = super().draw_foreground(c, frame)
        self._draw_header(c, frame / timeline.FPS)
        return amount

    def _draw_header(self, c: skia.Canvas, gt: float):
        a = gfx.prog(gt, 0.3, 0.8) * (1 - gfx.prog(gt, self.total - 1.2, 1.0))
        if a <= 0:
            return
        ink.label(c, "传习录", 92, 150, 34, tone=ink.CINNABAR, alpha=a * 0.9)
        ink.label(c, self.header, 92, 204, 26, tone=ink.OCHRE, alpha=a * 0.85, name="serif_medium", align="left")
        c.drawLine(40, 150 - 20, 40, 216, ink.paint(ink.CINNABAR, a * 0.8, stroke=4))

    def _draw_caption(self, c: skia.Canvas, s: Scene, t: float, pal: dict):
        """墨色字幕：未读字淡墨、已读字浓墨，【】关键词朱砂；底衬一条柔和的纸色光带保证可读。"""
        for i, ln in enumerate(s.lines):
            st, en = s.starts[i], s.ends[i]
            nxt = s.starts[i + 1] if i + 1 < len(s.lines) else s.duration
            stop = min(en + 0.35, nxt - 0.02)
            if not ln.caption or not (st - 0.05 <= t <= stop):
                continue
            rows = timeline._wrap_marks(ln.text, CAPTION_SIZE * 1.04, CAPTION_W)
            a = gfx.prog(t, st - 0.05, 0.12) * (1 - gfx.prog(t, stop - 0.12, 0.12))
            spoken = gfx.clamp01((t - st) / max(en - st, 0.1)) * sum(len(gfx.plain(r)) for r in rows)
            y0 = CAPTION_Y - (len(rows) - 1) * 36
            band_h = len(rows) * 72 + 40
            c.drawRoundRect(skia.Rect.MakeXYWH(60, y0 - 62, gfx.W - 120, band_h), 40, 40,
                            ink.paint((247, 241, 228), 0.78 * a, blur=18))
            for r, row in enumerate(rows):
                y = y0 + r * 72
                n_row = len(gfx.plain(row))
                w = sum(gfx.text_width(seg, CAPTION_SIZE, "serif_black") for seg, _ in gfx.parse_marks(row))
                gfx.draw_rich(c, row, gfx.W / 2, y, CAPTION_SIZE, "serif_black", INK_HEX, CINNABAR_HEX, a * 0.28)
                lit = min(n_row, spoken)
                spoken -= n_row
                if lit > 0:
                    cut = gfx.text_width(gfx.plain(row)[: int(math.ceil(lit))], CAPTION_SIZE, "serif_black")
                    c.save()
                    c.clipRect(skia.Rect.MakeLTRB(gfx.W / 2 - w / 2 - 20, y - 60, gfx.W / 2 - w / 2 + cut, y + 60))
                    gfx.draw_rich(c, row, gfx.W / 2, y, CAPTION_SIZE, "serif_black", INK_HEX, CINNABAR_HEX, a)
                    c.restore()
            return


# ---------------------------------------------------------------- 分镜辅助

class Ep:
    """一讲的文案：按 (节, 句) 取旁白句，生成 Line；场景内用 word() 求关键词的读出时刻。"""

    def __init__(self, ep: str):
        self.sections = {s.index: s for s in script.load(ep)}

    def line(self, sec: int, i: int, marks: tuple[str, ...] = ()) -> Line:
        s = self.sections[sec].sentences[i]
        text = s.text
        for m in marks:
            if m not in text:
                raise ValueError(f"'{m}' not in {sec}.{i}: {text}")
            text = text.replace(m, f"【{m}】", 1)
        return Line(text, s.speed, s.pause)

    def scene(self, name: str, sec: int, idx: list[int], draw, events: list[tuple] = (), marks: dict | None = None,
              tail: float = 0.3) -> Scene:
        """events 元素为 (类型, 场景内句序号, 关键词或 None, 偏移秒)；关键词找不到时抛 ValueError。"""
        lines = [self.line(sec, i, (marks or {}).get(k, ())) for k, i in enumerate(idx)]
        evs = []
        for kind, li, word, off in events:
            char = None
            if word is not None:
                char = gfx.plain(lines[li].text).find(word)
                if char < 0:
                    raise ValueError(f"event word '{word}' not in {name} line {li}")
            evs.append(Event(kind, li, off, char))
        return Scene(name, lines, draw, "paper", events=evs, tail=tail)


def word(ctx, i: int, w: str, end: bool = False) -> float:
    """场景内第 i 句读到关键词 w（开头或结尾）的时刻。"""
    text = gfx.plain(ctx.s.lines[i].text)
    k = text.find(w)
    if k < 0:
        raise ValueError(f"'{w}' not in line {i}: {text}")
    return ctx.at(i, k + (len(w) if end else 0))


def env(ctx, fade_in: float = 0.35, fade_out: float = 0.3) -> float:
    """场景整体透明度：开头从宣纸淡入、结尾淡回宣纸（相当于“过纸”转场）。"""
    return gfx.prog(ctx.t, 0, fade_in) * (1 - gfx.prog(ctx.t, ctx.dur - fade_out, fade_out))
