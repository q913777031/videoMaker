"""《熬夜欠的觉，周末能补回来吗？》分镜：场景、旁白、音效事件与配乐自动化。

旁白后的注释为出处编号（见 sleep/事实清单.md）。多音字用 Line.say 改成同音字送去合成：
“觉”在本片都读 jiào（写作“叫”）；“还”作归还讲时读 huán（写作“环”）。
"""

import math

from engine.gfx import (chip, draw_emoji, draw_kinetic, draw_text, ease_in_out, ease_out, gradient_bg,
                        light_rays, plain, prog, sparkles)
from engine.timeline import Event, Line, Scene

from . import art


def w(x, i: int, word: str) -> float:
    """第 i 句读到 word 的估计时刻。"""
    idx = plain(x.s.lines[i].text).find(word)
    if idx < 0:
        raise ValueError(f"'{word}' not in line {i} of scene {x.s.name}")
    return x.at(i, idx)


def ci(text: str, word: str) -> int:
    """word 在去掉标记的 text 中的字序号，供 Event.char 使用。"""
    idx = plain(text).find(word)
    if idx < 0:
        raise ValueError(f"'{word}' not in {text!r}")
    return idx


def fade(t: float, start: float, end: float | None = None, dur: float = 0.35) -> float:
    a = prog(t, start, dur)
    if end is not None:
        a *= 1 - prog(t, end, 0.3)
    return a


# ---------------------------------------------------------------- 钩子 1：周五熬到三点，周六睡到中午

L_FRI = "周五熬到三点，周六睡到中午。"


def s_friday(x):
    c, t = x.c, x.t
    t_three, t_sat, t_noon = w(x, 0, "三点"), w(x, 0, "周六"), w(x, 0, "中午")
    night = 23 + 4 * ease_in_out(prog(t, 0.0, t_three + 0.25))
    day = 9 * ease_in_out(prog(t, t_sat, t_noon + 0.3 - t_sat))
    hour = night + day
    warm = ease_out(prog(t, t_sat, 0.6))

    draw_emoji(c, "Crescent moon", 220, 430, 200 * (1 - 0.4 * warm), 1 - warm, rot=-12 + 4 * math.sin(t * 1.5))
    draw_emoji(c, "Sunrise", 860, 430, 220, warm, glow=("#FFD27A", 40) if warm > 0 else None)
    chip(c, 540, 330, "周五 深夜" if t < t_sat else "周六", 40, fill="#141C48" if t < t_sat else "#FFE08A",
         fg=art.GLASS if t < t_sat else art.INK, scale=0.9 + 0.1 * ease_out(prog(t, t_sat, 0.3)))

    shake = 6 * math.exp(-max(0.0, t - t_three) * 6) * (t > t_three)
    art.clock(c, 540 + shake * math.sin(t * 90), 780, 270, hour, glow=art.C_COL if t < t_sat else "#FFD27A")
    draw_text(c, art.hhmm(hour), 540, 1110, 92, "title", "#FFFFFF", stroke=(art.INK, 10),
              glow=(art.S_COL, 22 * math.exp(-max(0.0, t - t_three) * 3)) if t > t_three else None)

    phone_a = 1 - warm
    if phone_a > 0:
        draw_emoji(c, "Mobile phone", 860, 1020, 190, phone_a, rot=10 + 3 * math.sin(t * 7),
                   glow=("#6FA8FF", 50))
    bed_a = warm
    if bed_a > 0:
        draw_emoji(c, "Person in bed", 230, 1030, 230, bed_a, rot=-4)
        for k in range(3):
            ph = (t * 0.7 + k / 3) % 1
            draw_text(c, "Z", 330 + 40 * k + 30 * ph, 930 - 120 * ph, 46 + 14 * k, "title", "#FFF1D0",
                      bed_a * math.sin(math.pi * ph))


def bg_friday(x):
    t_sat = w(x, 0, "周六")
    k = ease_out(prog(x.t, t_sat, 0.6))
    if k > 0:
        gradient_bg(x.c, art.NOON_BG, alpha=k)


# ---------------------------------------------------------------- 钩子 2：欠的觉，补回来了吗？只补回来一半

L_Q = "欠的觉，补回来了吗？"
L_HALF = "答案是，只补回来【一半】。另一半，你根本感觉不到它还欠着。"


def s_debt(x):
    c, t = x.c, x.t
    out = x.cue(1) - 0.1
    up = ease_in_out(prog(t, out, 0.5))
    title_a = 1 - up
    draw_kinetic(c, "欠的觉，", 540, 520 - 200 * up, 180, t, 0.0, "title", "slam", 0.07, 0.3, fill=art.S_COL,
                 alpha=title_a, stroke=(art.INK, 14), glow=(art.S_COL, 30))
    draw_kinetic(c, "补回来了吗？", 540, 720 - 200 * up, 140, t, w(x, 0, "补") - 0.05, "title", "pop", 0.05, 0.35,
                 alpha=title_a, stroke=(art.INK, 12), shadow=(0, 8, 12, "#000000"))
    t_half, t_other, t_feel = w(x, 1, "一半"), w(x, 1, "另一半"), w(x, 1, "感觉不到")
    if t > t_half:
        light_rays(c, 540 - 200, 880, t, art.OK_COL, 0.18 * (1 - prog(t, t_half + 1.2, 0.8)), 14)
    y = 1040 - 200 * up
    art.ledger(c, 540, y, t, fill_at=0.35, split_at=t_half, ghost_at=t_feel, alpha=prog(t, 0.2, 0.3),
               scale=1.0 + 0.12 * up)
    if t > t_half:
        sparkles(c, t, 330, y, 380, 160, 10, seed=4, alpha=1 - prog(t, t_other, 0.5))
    if t > t_feel:
        q = ease_out(prog(t, t_feel, 0.5))
        draw_text(c, "?", 760, y - 230, 150, "title", art.BAD_COL, q * (0.6 + 0.4 * math.sin(t * 4)),
                  glow=(art.BAD_COL, 24))


# ---------------------------------------------------------------- 开放回路：看完你会拿到一个模型

L_PROMISE = "看完这期，你会拿到一个【模型】，自己就能推出该怎么补觉。"
CH_PROMISE = art.Chart("allnighter", 18, 40, box=(130, 560, 950, 1130))


def s_promise(x):
    c, t = x.c, x.t
    t_model = w(x, 0, "模型")
    chip(c, 540, 330, "睡眠双过程模型", 44, fill="#141C48", fg=art.GLASS, emoji="Test tube",
         scale=ease_out(prog(t, t_model - 0.2, 0.4)))
    p = ease_in_out(prog(t, 0.1, x.end(0) - 0.1))
    CH_PROMISE.draw(c, p, prog(t, 0.0, 0.3), t)
    t_how = w(x, 0, "推出")
    if t > t_how:
        draw_text(c, "?", 860, 470, 120, "title", art.S_COL, ease_out(prog(t, t_how, 0.4)) * (0.7 + 0.3 * math.sin(t * 5)),
                  glow=(art.S_COL, 20))


SAMPLE = [
    Scene("friday", [Line(L_FRI, 1.0, 0.3)], s_friday, "night", bg=bg_friday,
          events=[Event("ding", 0, char=ci(L_FRI, "三点")), Event("whoosh", 0, -0.15, char=ci(L_FRI, "周六")),
                  Event("pop", 0, char=ci(L_FRI, "中午"))]),
    Scene("debt", [Line(L_Q, 1.0, 0.35, say="欠的叫，补回来了吗？"), Line(L_HALF, 1.0, 0.4)], s_debt, "night",
          transition="zoom",
          events=[Event("boom", 0, char=0), Event("impact", 1, char=ci(L_HALF, "一半")),
                  Event("down", 1, char=ci(L_HALF, "感觉不到"))]),
    Scene("promise", [Line(L_PROMISE, 1.0, 0.5, say="看完这期，你会拿到一个模型，自己就能推出该怎么补叫。")], s_promise, "lab",
          transition="whip",
          events=[Event("shimmer", 0, char=ci(L_PROMISE, "模型"))]),
]
