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
TTS_SPEED = 1.1

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


def scene_title(d, t, cue):
    text(d, (W // 2, 620), "设计你的", 150, INK, appear(t, 0.2, 0.9), "mm")
    text(d, (W // 2, 800), "人生", 150, INK, appear(t, 0.4, 0.9), "mm")
    text(d, (W // 2, 960), "Designing Your Life", 60, ACCENT, appear(t, 0.9), "mm")
    w = 360 * appear(t, 1.2)
    if w > 0:
        d.rectangle([W // 2 - w / 2, 1040, W // 2 + w / 2, 1046], fill=ACCENT)
    text(d, (W // 2, 1110), "Stanford Life Design Lab", 38, MUTED, appear(t, cue(1)), "mm")
    text(d, (W // 2, 1170), "Bill Burnett & Dave Evans", 38, MUTED, appear(t, cue(1) + 0.2), "mm")


def scene_idea(d, t, cue):
    header(d, t, "核心观点", "人生不是一道\n等待解开的题")
    text(d, (LEFT, 700), "而是一件可以被", 64, INK, appear(t, cue(0) + 2.2))
    text(d, (LEFT, 790), "设计的作品。", 64, ACCENT, appear(t, cue(0) + 2.5))
    steps = ["理解自己", "大胆构想", "做原型", "去测试", "不断迭代"]
    for i, s in enumerate(steps):
        a = appear(t, cue(1) + i * 0.55)
        if a <= 0:
            continue
        y = 950 + i * 92
        d.rounded_rectangle([LEFT, y, LEFT + 360, y + 64], radius=32, fill=mix(BG, COLORS[i], a))
        d.text((LEFT + 180, y + 32), s, font=font(36), fill=mix(BG, (255, 255, 255), a), anchor="mm")
        if i < len(steps) - 1:
            d.text((LEFT + 400, y + 32), "↓", font=font(36), fill=mix(BG, MUTED, a), anchor="lm")


def scene_mindsets(d, t, cue):
    header(d, t, "五种设计思维", "Designer Mindsets")
    items = [("好奇心", "Curiosity", "对一切保持好奇"),
             ("行动导向", "Bias to Action", "先动手，别只空想"),
             ("重新定义问题", "Reframing", "换个问法，答案就变了"),
             ("觉察过程", "Awareness", "接受过程中的混乱"),
             ("深度合作", "Radical Collaboration", "寻求他人的帮助")]
    for i, (zh, en, desc) in enumerate(items):
        a = appear(t, cue(i + 1))
        if a <= 0:
            continue
        y = 560 + i * 170
        r = 34 * a
        d.ellipse([LEFT + 34 - r, y + 40 - r, LEFT + 34 + r, y + 40 + r], fill=COLORS[i])
        d.text((LEFT + 34, y + 40), str(i + 1), font=font(36), fill=BG, anchor="mm")
        text(d, (LEFT + 100, y), zh, 56, INK, a, rise=0)
        text(d, (LEFT + 100 + font(56).getlength(zh) + 24, y + 18), en, 32, COLORS[i], a, rise=0)
        text(d, (LEFT + 100, y + 80), desc, 38, MUTED, a, rise=0)


def scene_journal(d, t, cue):
    header(d, t, "工具一", "好时光日志", "Good Time Journal")
    text(d, (LEFT, 650), "做了什么？有多投入？", 44, MUTED, appear(t, cue(1)))
    text(d, (LEFT, 710), "精力是充电还是消耗？", 44, MUTED, appear(t, cue(1) + 0.3))
    rows = [("带新人做项目", 0.9, 0.8), ("写周报", 0.3, -0.6), ("调试视觉算法", 0.85, 0.5),
            ("开跨部门会议", 0.35, -0.4), ("周末徒步", 0.8, 0.9)]
    la = appear(t, cue(1) + 0.6)
    text(d, (LEFT, 790), "投入度", 32, COLORS[1], la, rise=0)
    text(d, (690, 790), "精力", 32, COLORS[2], la, rise=0)
    for i, (name, engage, energy) in enumerate(rows):
        start = cue(1) + 0.8 + i * 0.45
        a = appear(t, start)
        if a <= 0:
            continue
        y = 850 + i * 105
        text(d, (LEFT, y), name, 40, INK, a, rise=0)
        grow = appear(t, start + 0.2, 1.0)
        by = y + 60
        d.rectangle([LEFT, by, LEFT + 480, by + 30], fill=mix(BG, (225, 220, 210), a))
        d.rectangle([LEFT, by, LEFT + 480 * engage * grow, by + 30], fill=COLORS[1])
        cx = 770
        d.line([cx, by - 8, cx, by + 38], fill=mix(BG, MUTED, a), width=3)
        end = cx + 140 * energy * grow
        d.rectangle([min(cx, end), by, max(cx, end), by + 30],
                    fill=COLORS[2] if energy > 0 else ACCENT)


def scene_odyssey(d, t, cue):
    header(d, t, "工具二", "奥德赛计划", "Odyssey Plans")
    text(d, (LEFT, 650), "未来五年，三种完全不同的人生", 44, MUTED, appear(t, cue(1)))
    plans = [("A", "当前路径", "沿着现在的方向继续走下去"),
             ("B", "备选人生", "如果现在这条路突然消失了"),
             ("C", "疯狂想法", "如果钱和面子都不是问题")]
    for i, (tag, name, desc) in enumerate(plans):
        a = appear(t, cue(i + 2), 0.8)
        if a <= 0:
            continue
        y = 740 + i * 230 + (1 - a) * 60
        d.rounded_rectangle([LEFT, y, RIGHT, y + 200], radius=28,
                            fill=mix(BG, (255, 255, 255), a), outline=mix(BG, COLORS[i], a), width=4)
        d.rectangle([LEFT, y + 20, LEFT + 14, y + 180], fill=mix(BG, COLORS[i], a))
        d.text((LEFT + 50, y + 36), f"版本 {tag}", font=font(34), fill=mix(BG, COLORS[i], a))
        d.text((LEFT + 50, y + 82), name, font=font(56), fill=mix(BG, INK, a))
        d.text((LEFT + 50, y + 152), desc, font=font(34), fill=mix(BG, MUTED, a))


def scene_prototype(d, t, cue):
    header(d, t, "工具三", "做原型", "Prototyping")
    pairs = [("原型对话", "找正在过那种生活的人", "聊一聊，听真实的故事"),
             ("原型体验", "花一天、一周", "亲身去试一试，代价很小")]
    for i, (name, l1, l2) in enumerate(pairs):
        a = appear(t, cue(i + 1))
        y = 680 + i * 260
        if a > 0:
            d.rectangle([LEFT, y, LEFT + 12, y + 190], fill=mix(BG, COLORS[i + 1], a))
        text(d, (LEFT + 50, y), name, 60, INK, a)
        text(d, (LEFT + 50, y + 90), l1, 40, MUTED, a)
        text(d, (LEFT + 50, y + 145), l2, 40, MUTED, a)
    text(d, (LEFT, 1250), "低成本试错，", 56, ACCENT, appear(t, cue(3)))
    text(d, (LEFT, 1330), "用真实代替空想。", 56, ACCENT, appear(t, cue(3) + 0.3))


def scene_end(d, t, cue):
    text(d, (W // 2, 700), "人生没有", 96, INK, appear(t, cue(0), 0.9), "mm")
    text(d, (W // 2, 820), "唯一正确答案", 96, INK, appear(t, cue(0) + 0.3, 0.9), "mm")
    text(d, (W // 2, 980), "只有不断迭代的版本", 72, ACCENT, appear(t, cue(1), 0.9), "mm")
    text(d, (W // 2, 1200), "参考：《Designing Your Life》", 34, MUTED, appear(t, cue(2)), "mm")
    text(d, (W // 2, 1250), "Bill Burnett & Dave Evans", 34, MUTED, appear(t, cue(2) + 0.2), "mm")


SCENES = [
    Scene(["斯坦福大学有一门超火的课，叫做设计你的人生。",
           "它教你用设计师的思维，规划自己的人生。"], scene_title),
    Scene(["它的核心观点是，人生不是一道等待解开的题，而是一件可以被设计的作品。",
           "先理解自己，再大胆构想，然后做原型、去测试、不断迭代。"], scene_idea),
    Scene(["设计师有五种思维。",
           "保持好奇。",
           "先动手，别空想。",
           "换个问法，重新定义问题。",
           "觉察过程，接受混乱。",
           "寻求他人，深度合作。"], scene_mindsets),
    Scene(["第一个工具，叫好时光日志。",
           "每天记录你做了什么，有多投入，精力是充电还是消耗。",
           "坚持几周，你就能看清什么让你真正投入。"], scene_journal),
    Scene(["第二个工具，奥德赛计划。",
           "为未来五年，写下三种完全不同的人生。",
           "一，沿着当前的路走下去。",
           "二，如果这条路突然消失了。",
           "三，如果钱和面子都不是问题。"], scene_odyssey),
    Scene(["第三个工具，做原型。",
           "找正在过那种生活的人聊一聊，",
           "或者花一天，亲身去试一试。",
           "用低成本的尝试，代替空想。"], scene_prototype),
    Scene(["人生没有唯一正确答案，",
           "只有不断迭代的版本。",
           "从今天起，开始设计你的人生吧。"], scene_end),
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
