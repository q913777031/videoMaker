"""竖屏 9:16 短视频版：离线 TTS 逐句配音 + 合成背景音乐 + 烧录字幕。

每个场景的时长由其旁白长度决定，动画入场时间与对应句子的开始时间对齐。

用法：python3 dyl_short.py [输出路径]
依赖：models/vits-melo-tts-zh_en（sherpa-onnx MeloTTS 中文模型，见 README）
"""

import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from typing import Callable

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw

from dyl_video import ACCENT, BG, COLORS, INK, MUTED, appear, font, mix, text

W, H = 1080, 1920
FPS = 30
SR = 44100
LEFT = 90
RIGHT = W - 160  # 右侧留出短视频平台的点赞/评论按钮区域
SUB_Y = 1500     # 字幕中心线，避开底部标题与进度条区域
MODEL_DIR = os.environ.get("DYL_TTS_MODEL", "models/vits-melo-tts-zh_en")
TTS_SPEED = 1.15

LEAD_IN = 0.5
GAP = 0.25
TAIL = 0.8
FADE = 0.3

Cue = Callable[[int], float]


@dataclass
class Scene:
    lines: list[str]
    draw: Callable[[ImageDraw.ImageDraw, float, Cue], None]
    starts: list[float] = field(default_factory=list)
    ends: list[float] = field(default_factory=list)
    duration: float = 0.0


def header(d, t, kicker: str, title: str, en: str = ""):
    """竖屏场景通用标题：标签 + 大标题（可多行）+ 英文副标题 + 强调线。"""
    text(d, (LEFT, 260), kicker, 38, ACCENT, appear(t, 0.0))
    d_lines = title.split("\n")
    for i, s in enumerate(d_lines):
        text(d, (LEFT, 320 + i * 100), s, 84, INK, appear(t, 0.1 + i * 0.1))
    y = 320 + len(d_lines) * 100
    if en:
        text(d, (LEFT, y + 10), en, 40, ACCENT, appear(t, 0.3))
        y += 70
    w = 120 * appear(t, 0.4)
    if w > 0:
        d.rectangle([LEFT, y + 30, LEFT + w, y + 38], fill=ACCENT)


def chip(d, xy, s: str, size: int, color, a: float, anchor: str = "l"):
    """绘制圆角标签；anchor 为 "r" 时以 xy 为右端对齐。返回标签宽度。"""
    if a <= 0:
        return 0
    x, y = xy
    w = font(size).getlength(s) + size * 1.2
    if anchor == "r":
        x -= w
    h = size * 1.7
    d.rounded_rectangle([x, y, x + w, y + h], radius=h / 2, fill=mix(BG, color, a))
    d.text((x + w / 2, y + h / 2), s, font=font(size), fill=mix(BG, (255, 255, 255), a), anchor="mm")
    return w


def scene_persona(d, t, cue):
    text(d, (LEFT, 260), "你是不是也这样？", 44, ACCENT, appear(t, 0.0))
    a = appear(t, 0.3, 0.8)
    if a > 0:
        d.rounded_rectangle([LEFT, 360, RIGHT, 820], radius=32, fill=mix(BG, (255, 255, 255), a),
                            outline=mix(BG, (225, 220, 210), a), width=3)
        d.ellipse([LEFT + 40, 400, LEFT + 160, 520], fill=mix(BG, COLORS[1], a))
        d.text((LEFT + 100, 460), "周", font=font(60), fill=mix(BG, (255, 255, 255), a), anchor="mm")
    text(d, (LEFT + 190, 405), "老周 · 35岁", 60, INK, a, rise=0)
    text(d, (LEFT + 190, 482), "工作十年的技术骨干", 36, MUTED, a, rise=0)
    tags = [("房贷还有20年", cue(1)), ("孩子刚上小学", cue(1) + 0.9),
            ("晋升卡了3年", cue(2)), ("怕被年轻人取代", cue(2) + 1.2)]
    for i, (tag, start) in enumerate(tags):
        chip(d, (LEFT + 40 + (i % 2) * 360, 590 + (i // 2) * 100), tag, 38, COLORS[[0, 3, 4, 0][i]],
             appear(t, start))
    text(d, (W // 2, 1000), "我的人生", 84, INK, appear(t, cue(3) + 0.8), "mm")
    text(d, (W // 2, 1120), "是不是就这样了？", 84, ACCENT, appear(t, cue(3) + 1.3), "mm")


def scene_title(d, t, cue):
    text(d, (W // 2, 620), "设计你的", 150, INK, appear(t, 0.2, 0.9), "mm")
    text(d, (W // 2, 800), "人生", 150, INK, appear(t, 0.4, 0.9), "mm")
    text(d, (W // 2, 960), "Designing Your Life", 60, ACCENT, appear(t, 0.9), "mm")
    w = 360 * appear(t, 1.2)
    if w > 0:
        d.rectangle([W // 2 - w / 2, 1040, W // 2 + w / 2, 1046], fill=ACCENT)
    text(d, (W // 2, 1110), "Stanford Life Design Lab", 38, MUTED, appear(t, cue(1)), "mm")
    text(d, (W // 2, 1170), "Bill Burnett & Dave Evans", 38, MUTED, appear(t, cue(1) + 0.2), "mm")


def scene_reframe(d, t, cue):
    header(d, t, "焦虑的根源", "问错了问题")
    a = appear(t, cue(1))
    if a > 0:
        d.rounded_rectangle([LEFT, 620, RIGHT, 800], radius=28, fill=mix(BG, (235, 230, 222), a))
    text(d, (LEFT + 40, 650), "我该怎么找到", 52, MUTED, a, rise=0)
    text(d, (LEFT + 40, 720), "那个正确的人生？", 52, MUTED, a, rise=0)
    strike = appear(t, cue(2), 0.5)
    if strike > 0:
        for ly, s_ in ((680, "我该怎么找到"), (750, "那个正确的人生？")):
            lw = font(52).getlength(s_) + 20
            d.line([LEFT + 30, ly, LEFT + 30 + lw * strike, ly], fill=ACCENT, width=5)
    b = appear(t, cue(3))
    text(d, (W // 2, 860), "↓", 60, ACCENT, b, "ma")
    if b > 0:
        d.rounded_rectangle([LEFT, 960, RIGHT, 1140], radius=28, fill=mix(BG, ACCENT, b))
    text(d, (LEFT + 40, 990), "我可以先试试", 52, (255, 255, 255), b, rise=0)
    text(d, (LEFT + 40, 1060), "哪几种可能？", 52, (255, 255, 255), b, rise=0)
    text(d, (LEFT, 1230), "人生不是解题，是设计。", 56, INK, appear(t, cue(4)))


def scene_mindsets(d, t, cue):
    header(d, t, "五种设计思维", "放到老周身上")
    items = [("好奇心", "别问「我还有什么用」，问「我对什么感兴趣」"),
             ("行动导向", "别纠结转不转行，周末先去听场行业分享"),
             ("重新定义问题", "「35岁太晚了」→「十年经验能带去哪？」"),
             ("觉察过程", "迷茫不是失败，是你正在探索的信号"),
             ("深度合作", "找 3 个信任的人，聊聊你的困惑")]
    for i, (zh, desc) in enumerate(items):
        a = appear(t, cue(i + 1))
        if a <= 0:
            continue
        y = 560 + i * 165
        r = 32 * a
        d.ellipse([LEFT + 32 - r, y + 32 - r, LEFT + 32 + r, y + 32 + r], fill=COLORS[i])
        d.text((LEFT + 32, y + 32), str(i + 1), font=font(34), fill=BG, anchor="mm")
        text(d, (LEFT + 90, y), zh, 52, INK, a, rise=0)
        text(d, (LEFT + 90, y + 72), desc, 34, MUTED, a, rise=0)


def scene_journal(d, t, cue):
    header(d, t, "工具一", "好时光日志", "Good Time Journal")
    text(d, (LEFT, 650), "老周记录了两周：", 44, MUTED, appear(t, cue(1)))
    rows = [("给新人讲技术方案", 0.95, 0.9), ("写汇报 PPT", 0.3, -0.7), ("半夜处理线上故障", 0.7, -0.5),
            ("开拉通协调会", 0.35, -0.5), ("周末陪孩子做手工", 0.85, 0.8)]
    la = appear(t, cue(2))
    text(d, (LEFT, 730), "投入度", 32, COLORS[1], la, rise=0)
    text(d, (690, 730), "精力", 32, COLORS[2], la, rise=0)
    for i, (name, engage, energy) in enumerate(rows):
        start = cue(2) + 0.2 + i * 0.45
        a = appear(t, start)
        if a <= 0:
            continue
        y = 780 + i * 100
        text(d, (LEFT, y), name, 40, INK, a, rise=0)
        grow = appear(t, start + 0.2, 1.0)
        by = y + 56
        d.rectangle([LEFT, by, LEFT + 480, by + 28], fill=mix(BG, (225, 220, 210), a))
        d.rectangle([LEFT, by, LEFT + 480 * engage * grow, by + 28], fill=COLORS[1])
        cx = 770
        d.line([cx, by - 8, cx, by + 36], fill=mix(BG, MUTED, a), width=3)
        end = cx + 140 * energy * grow
        d.rectangle([min(cx, end), by, max(cx, end), by + 28],
                    fill=COLORS[2] if energy > 0 else ACCENT)
    text(d, (LEFT, 1300), "线索：讲方案、带人让他充电", 44, ACCENT, appear(t, cue(4)))


def scene_odyssey(d, t, cue):
    header(d, t, "工具二", "奥德赛计划", "Odyssey Plans")
    text(d, (LEFT, 650), "老周的三个五年版本", 44, MUTED, appear(t, cue(1)))
    plans = [("A", "当前路径", "争取技术经理，三年内带起团队"),
             ("B", "如果被裁", "去做企业内训讲师"),
             ("C", "钱和面子都不是问题", "开一间少儿编程工作室")]
    for i, (tag, name, desc) in enumerate(plans):
        a = appear(t, cue(i + 2), 0.8)
        if a <= 0:
            continue
        y = 740 + i * 220 + (1 - a) * 60
        d.rounded_rectangle([LEFT, y, RIGHT, y + 190], radius=28,
                            fill=mix(BG, (255, 255, 255), a), outline=mix(BG, COLORS[i], a), width=4)
        d.rectangle([LEFT, y + 20, LEFT + 14, y + 170], fill=mix(BG, COLORS[i], a))
        d.text((LEFT + 50, y + 30), f"版本 {tag} · {name}", font=font(36), fill=mix(BG, COLORS[i], a))
        d.text((LEFT + 50, y + 96), desc, font=font(48), fill=mix(BG, INK, a))


def scene_prototype(d, t, cue):
    header(d, t, "工具三", "做最小原型", "Prototyping")
    sections = [("原型对话", COLORS[1], 620, [("请老板吃顿饭", "问清技术经理要什么，自己差在哪", "一顿饭"),
                                           ("约内训讲师朋友喝咖啡", "了解真实收入和日常", "一杯咖啡")]),
                ("原型体验", COLORS[2], 950, [("主动做一次内部技术分享", "试试站在台上的感觉", "一个下午"),
                                           ("周末去少儿编程机构当助教", "看看自己是否真的喜欢", "一个周末")])]
    k = 0
    for title, color, y0, items in sections:
        text(d, (LEFT, y0), title, 40, color, appear(t, cue(k + 1)))
        for j, (name, sub, cost) in enumerate(items):
            a = appear(t, cue(k + 1))
            k += 1
            if a <= 0:
                continue
            y = y0 + 64 + j * 135
            d.rectangle([LEFT, y + 4, LEFT + 8, y + 104], fill=mix(BG, color, a))
            text(d, (LEFT + 30, y), name, 44, INK, a, rise=0)
            text(d, (LEFT + 30, y + 62), sub, 34, MUTED, a, rise=0)
            chip(d, (RIGHT, y + 4), cost, 28, ACCENT, a, anchor="r")
    text(d, (LEFT, 1290), "比辞职试错，便宜太多。", 52, ACCENT, appear(t, cue(5)))


def scene_end(d, t, cue):
    text(d, (W // 2, 640), "焦虑不是因为", 88, INK, appear(t, cue(0), 0.9), "mm")
    text(d, (W // 2, 760), "你不够努力", 88, INK, appear(t, cue(0) + 0.3, 0.9), "mm")
    text(d, (W // 2, 900), "而是只盯着一条路", 68, ACCENT, appear(t, cue(1), 0.9), "mm")
    a = appear(t, cue(3))
    if a > 0:
        w = font(44).getlength("这周，做你的第一个最小原型") + 80
        d.rounded_rectangle([W // 2 - w / 2, 1030, W // 2 + w / 2, 1120], radius=45, fill=mix(BG, ACCENT, a))
        d.text((W // 2, 1075), "这周，做你的第一个最小原型", font=font(44),
               fill=mix(BG, (255, 255, 255), a), anchor="mm")
    text(d, (W // 2, 1260), "参考：《Designing Your Life》", 32, MUTED, appear(t, cue(4)), "mm")
    text(d, (W // 2, 1305), "Bill Burnett & Dave Evans", 32, MUTED, appear(t, cue(4) + 0.2), "mm")


SCENES = [
    Scene(["认识一下老周，三十五岁，工作十年的技术骨干。",
           "房贷还有二十年，孩子刚上小学。",
           "晋升卡了三年，看着年轻人冲上来，越来越焦虑。",
           "半夜睡不着，总在想，我的人生，是不是就这样了？"], scene_persona),
    Scene(["如果你也是老周，斯坦福有一门课，叫做设计你的人生。",
           "它专门解决这种卡住了的感觉。"], scene_title),
    Scene(["老周的焦虑，来自一个错误的问题，",
           "我该怎么找到那个正确的人生？",
           "可人生根本没有标准答案。",
           "换个问法，我可以先试试哪几种可能？",
           "人生不是一道题，而是一件可以设计的作品。"], scene_reframe),
    Scene(["设计师有五种思维，放到老周身上是这样的。",
           "好奇心，别问我还有什么用，问我还对什么感兴趣。",
           "行动导向，别纠结转不转行，这周末先去听一场行业分享。",
           "重新定义问题，把三十五岁太晚了，换成十年经验能带去哪里。",
           "觉察过程，迷茫不是失败，是你正在探索的信号。",
           "深度合作，找三个信任的人，聊聊你的困惑。"], scene_mindsets),
    Scene(["第一个工具，好时光日志。",
           "每天记录做了什么，有多投入，精力是充电还是消耗。",
           "老周记了两周，发现给新人讲方案时，他最投入、最有劲。",
           "写汇报、开协调会，最消耗他。",
           "线索出来了，他也许更适合带人和做培训。"], scene_journal),
    Scene(["第二个工具，奥德赛计划。",
           "老周为未来五年，写下了三个完全不同的版本。",
           "第一种，留在现在的路上，争取技术经理，三年内带起团队。",
           "第二种，如果明天被裁，就去做企业内训讲师。",
           "第三种，如果钱和面子都不是问题，开一间少儿编程工作室。",
           "三条路画出来，焦虑就从无路可走，变成了有得选。"], scene_odyssey),
    Scene(["第三个工具，做最小原型，用最低的成本验证想法。",
           "比如，请老板吃顿饭，问问公司对技术经理的期待，自己还差在哪。",
           "约做内训的朋友喝杯咖啡，了解真实的收入和日常。",
           "主动在公司做一次技术分享，试试站在台上的感觉。",
           "周末去少儿编程机构，当一天助教。",
           "一顿饭，一个周末，比辞职试错便宜太多。"], scene_prototype),
    Scene(["焦虑，不是因为你不够努力，",
           "而是你只盯着一条路。",
           "多画几条路，从最小的一步开始。",
           "这周，就去做你的第一个原型吧。",
           "评论区告诉我，你打算先试什么？"], scene_end),
]


def load_tts():
    """加载 sherpa-onnx MeloTTS 模型；模型目录缺失时抛出 FileNotFoundError。"""
    import sherpa_onnx

    d = MODEL_DIR.rstrip("/") + "/"
    if not os.path.isfile(d + "model.onnx"):
        raise FileNotFoundError(f"TTS model not found: {d}model.onnx")
    vits = sherpa_onnx.OfflineTtsVitsModelConfig(
        model=d + "model.onnx", lexicon=d + "lexicon.txt", tokens=d + "tokens.txt", dict_dir=d + "dict")
    cfg = sherpa_onnx.OfflineTtsConfig(
        model=sherpa_onnx.OfflineTtsModelConfig(vits=vits, num_threads=4),
        rule_fsts=f"{d}date.fst,{d}phone.fst,{d}number.fst")
    return sherpa_onnx.OfflineTts(cfg)


def resample(x: np.ndarray, src: int, dst: int) -> np.ndarray:
    """线性插值重采样，用于对齐 TTS 输出与混音采样率。"""
    if src == dst:
        return x
    n = int(len(x) * dst / src)
    return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x).astype(np.float32)


def build_voice(tts) -> np.ndarray:
    """逐句合成旁白并拼接，同时回填每个场景的句子起止时间与场景时长。"""
    parts = []
    for scene in SCENES:
        chunks = [np.zeros(int(LEAD_IN * SR), np.float32)]
        pos = LEAD_IN
        for i, line in enumerate(scene.lines):
            audio = tts.generate(line, sid=0, speed=TTS_SPEED)
            samples = resample(np.asarray(audio.samples, np.float32), audio.sample_rate, SR)
            scene.starts.append(pos)
            pos += len(samples) / SR
            scene.ends.append(pos)
            chunks.append(samples)
            gap = GAP if i < len(scene.lines) - 1 else TAIL
            chunks.append(np.zeros(int(gap * SR), np.float32))
            pos += gap
        # 场景时长按帧取整，并把音频补齐到同样长度，保证逐场景音画不漂移
        scene.duration = int(round(pos * FPS)) / FPS
        audio = np.concatenate(chunks)
        want = int(round(scene.duration * SR))
        parts.append(np.pad(audio, (0, max(0, want - len(audio))))[:want])
    voice = np.concatenate(parts)
    peak = float(np.max(np.abs(voice))) or 1.0
    return voice / peak * 0.9


def build_bgm(seconds: float) -> np.ndarray:
    """合成轻柔的背景音乐：C-Am-F-G 和弦铺底 + 八分音符琶音 + 低音，无版权问题。"""
    n = int(seconds * SR)
    t = np.arange(n) / SR
    bar = 3.0  # 80 BPM，4/4 拍
    chords = [[60, 64, 67], [57, 60, 64], [53, 57, 60], [55, 59, 62]]
    hz = lambda m: 440.0 * 2 ** ((m - 69) / 12)
    out = np.zeros(n, np.float32)
    total_bars = int(np.ceil(seconds / bar))
    for b in range(total_bars):
        chord = chords[b % len(chords)]
        s, e = int(b * bar * SR), min(int((b + 1) * bar * SR), n)
        tt = t[s:e] - b * bar
        env = np.minimum(1, tt / 0.8) * np.minimum(1, (bar - tt) / 0.8)
        for m in chord:
            for det in (-0.12, 0.12):
                out[s:e] += 0.05 * env * np.sin(2 * np.pi * hz(m + det) * tt)
        out[s:e] += 0.10 * env * np.sin(2 * np.pi * hz(chord[0] - 24) * tt)
        arp = chord + [chord[0] + 12]
        for k in range(8):
            ns = s + int(k * bar / 8 * SR)
            if ns >= n:
                break
            ne = min(ns + int(1.2 * SR), n)
            nt = t[ns:ne] - t[ns]
            note = hz(arp[[0, 1, 2, 3, 2, 1, 2, 3][k]] + 12)
            out[ns:ne] += 0.06 * np.exp(-nt * 4) * np.sin(2 * np.pi * note * nt)
    # 滑动平均低通让音色更柔和
    y = np.convolve(out, np.ones(8, np.float32) / 8, mode="same").astype(np.float32)
    fade = int(1.5 * SR)
    y[:fade] *= np.linspace(0, 1, fade)
    y[-fade:] *= np.linspace(1, 0, fade)
    return y / (float(np.max(np.abs(y))) or 1.0)


def mix_audio(voice: np.ndarray, bgm: np.ndarray) -> np.ndarray:
    """人声 + 背景音乐混音；有人声时背景音乐自动压低（ducking）。"""
    active = (np.abs(voice) > 0.02).astype(np.float32)
    win = int(0.3 * SR)
    kernel = np.ones(win, np.float32) / win
    duck = np.clip(np.convolve(active, kernel, mode="same") * 4, 0, 1)
    gain = 0.22 - 0.13 * duck
    out = voice + bgm[: len(voice)] * gain
    return np.clip(out, -1.0, 1.0)


def wrap(s: str, size: int, max_w: float) -> list[str]:
    """按像素宽度对中文字幕折行，各行长度尽量均衡，且标点不出现在行首。"""
    rows = max(1, int(np.ceil(font(size).getlength(s) / max_w)))
    target = min(max_w, font(size).getlength(s) / rows + size)
    lines, cur = [], ""
    for ch in s:
        if font(size).getlength(cur + ch) > target and cur and ch not in "，、。：！？":
            lines.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines


def draw_subtitle(d, scene: Scene, t: float):
    """在当前句子播放期间绘制字幕条。"""
    for line, s, e in zip(scene.lines, scene.starts, scene.ends):
        if s <= t <= e + 0.15:
            rows = wrap(line.rstrip("，。"), 48, RIGHT - LEFT - 60)
            h = len(rows) * 66 + 36
            top = SUB_Y - h / 2
            d.rounded_rectangle([LEFT - 10, top, RIGHT + 10, top + h], radius=24, fill=(34, 40, 49))
            for i, r in enumerate(rows):
                d.text(((LEFT + RIGHT) / 2, top + 18 + 33 + i * 66), r, font=font(48),
                       fill=(255, 255, 255), anchor="mm")
            return


def render_frame(scene: Scene, t: float) -> bytes:
    """渲染单帧：场景动画 + 字幕，场景首尾短暂淡入淡出。"""
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    scene.draw(d, t, lambda i: scene.starts[i])
    fade = min(t / FADE, (scene.duration - t) / FADE, 1.0)
    if fade < 1.0:
        img = Image.blend(Image.new("RGB", (W, H), BG), img, max(fade, 0.0))
        d = ImageDraw.Draw(img)
    draw_subtitle(d, scene, t)
    return img.tobytes()


def main(out_path: str):
    tts = load_tts()
    voice = build_voice(tts)
    total = sum(s.duration for s in SCENES)
    audio = mix_audio(voice, build_bgm(total))
    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, "mix.wav")
        sf.write(wav, audio, SR)
        cmd = ["ffmpeg", "-y", "-loglevel", "error",
               "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
               "-i", wav,
               "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out_path]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        assert proc.stdin is not None
        try:
            for scene in SCENES:
                for i in range(int(round(scene.duration * FPS))):
                    proc.stdin.write(render_frame(scene, i / FPS))
        finally:
            proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError(f"ffmpeg exited with code {proc.returncode}")
    print(f"written: {out_path} ({total:.1f}s)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "out/designing_your_life_short.mp4")
