"""场景模板：每个镜头一个函数 (c, t, D, cue, view)，在 1000×1000 舞台单位上绘制。

规则（详见 .claude/skills/kepu-video/SKILL.md）：
- 撞击时刻只读 cue[键]，不写死秒数；撞击帧的画面变化必须最大（ease_in 落定、d.pulse 光晕），不用 ease_io 跨过撞击点。
- 文字不在场景里画（主字幕、角标、来源卡由引擎绘制）；场景只画物体与人物。
- 背景铺满 view，关键物体放在舞台 0–1000 范围内。
"""

import math

from kepu import draw as d
from kepu.config import GOLD
from kepu.props import F, RING, desk, doc_on_desk, mark_pos_on_doc, ring_card, ring_floor


def shot01(c, t, D, cue, view):
    desk(c, view)
    land = d.ease_in(d.prog(t, cue["hit"] - 0.5, 0.5))
    doc_on_desk(c, scale=0.4 + 0.6 * land, frame_k=d.prog(t, cue["hit"] - F, 0.35))
    x, y = mark_pos_on_doc()
    d.glow(c, x, y, 160, GOLD, 0.4 * d.pulse(t, cue["hit"], 0.6))


def shot02(c, t, D, cue, view):
    d.backdrop(c, view)
    ring_floor(c, glow_k=d.pulse(t, cue["lap"], 0.4))
    ang = math.pi / 2 + 2 * math.pi * (t - cue["lap"]) / 1.6
    shade = 0.15 + 0.3 * d.ease_out(d.prog(t, cue["lap"], 0.25))
    ring_card(c, ang, shade, ring=RING)


def shot03(c, t, D, cue, view):
    d.backdrop(c, view, a=1.0)


SCENES = {1: shot01, 2: shot02, 3: shot03}
