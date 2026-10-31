"""《丰田模式》音色试听：6 个 ZipVoice 候选念同一段旁白（样片前两句），慢速讲解语速，无配乐。

- 每个候选的提示音来自本地 Kokoro 音色（不使用任何真人录音），ZipVoice 只借音色、韵律自己生成；
- 放慢靠“慢提示音”：Narrator(prompt_speed=…) 让提示音念得慢，ZipVoice 跟着提示音的语速走；
  每个音色的提示语速单独校准到整段约 4.0 字/秒（含停顿）；去噪步数 8；
- 停顿：逗号处在最安静的位置补到约 0.25 秒，句号后 0.5 秒；各候选之间 1 秒静音；
- 可选 ASR 复核（--asr 模型目录，sherpa-onnx paraformer 中文模型），检查吞字。

用法：python3 -m fengtian.voice_audition [--asr DIR]   → out/fengtian/voice_audition.mp4
"""

import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import skia
import soundfile as sf

from adler import core
from adler import kit as K
from engine import audio
from engine.gfx import clamp01, ease_out

OUT = Path(__file__).resolve().parent.parent / "out" / "fengtian"
SENTS = ["同一个问题，返工第三遍了。", "补了又坏，坏了又补。"]
COMMA_AT = [5 / 11, 4 / 8]            # 逗号在句中的位置（按字数）
HAN = 19
TARGET = 4.0                           # 目标：整段（含停顿）字/秒
STEPS = 8
COMMA, PERIOD, BETWEEN, LEAD = 0.25, 0.5, 1.0, 0.7

# (标签, 音色, 提示用 Kokoro 音色, 特点)
CANDS = [
    ("A", "zv_yunxi", "zm_yunxi", "男声 · 年轻清亮"),
    ("B", "zv_yunjian", "zm_yunjian", "男声 · 浑厚有力"),
    ("C", "zv_yunyang", "zm_yunyang", "男声 · 播音沉稳"),
    ("D", "zv_009", "zm_009", "男声 · 低沉温和"),
    ("E", "zv_xiaoxiao", "zf_xiaoxiao", "女声 · 温暖亲切"),
    ("F", "zv_001", "zf_001", "女声 · 柔和自然"),
]


def stretch_comma(x, frac, target=COMMA):
    """在逗号附近（预期位置 ±12%）找最安静的 30ms，补静音到约 target 秒。"""
    hop = int(0.01 * audio.SR)
    n = len(x) // hop
    r = np.sqrt(np.mean(x[: n * hop].reshape(n, hop) ** 2, 1))
    r3 = np.convolve(r, np.ones(3) / 3, "same")
    lo, hi = int(n * (frac - 0.12)), int(n * (frac + 0.12))
    i = lo + int(np.argmin(r3[lo:hi]))
    quiet = r3 < r.max() * 10 ** (-32 / 20)
    a = i
    while a > 0 and quiet[a - 1]:
        a -= 1
    b = i
    while b < n and quiet[b]:
        b += 1
    have = (b - a) / 100 if quiet[i] else 0.0
    add = max(0.0, target - have)
    cut = i * hop
    f = int(0.008 * audio.SR)
    left, right = x[:cut].copy(), x[cut:].copy()
    left[-f:] *= np.linspace(1, 0, f)
    right[:f] *= np.linspace(0, 1, f)
    return np.concatenate([left, np.zeros(int(add * audio.SR)), right]), round(have, 2)


def take(voice, ps):
    nar = audio.Narrator(voice, prompt_speed=ps)
    raw = [nar.generate(s, 1.0, STEPS) for s in SENTS]
    parts, gaps = [], []
    for x, frac in zip(raw, COMMA_AT):
        y, g = stretch_comma(x, frac)
        parts.append(y)
        gaps.append(g)
    y = np.concatenate([parts[0], np.zeros(int(PERIOD * audio.SR)), parts[1]])
    speech = sum(len(x) for x in raw) / audio.SR
    return dict(y=y, raw=raw, ps=ps, d1=len(parts[0]) / audio.SR, total=len(y) / audio.SR, rate=HAN / (len(y) / audio.SR),
                speech_rate=HAN / speech, gaps=gaps)


def calibrate(voice):
    """提示语速与生成语速近似成正比：先试 0.8，按比例算一次，再取两者中更接近目标的。"""
    tries = [take(voice, 0.8)]
    ps = round(min(1.0, max(0.6, 0.8 * TARGET / tries[0]["rate"])) / 0.05) * 0.05
    if abs(ps - 0.8) > 1e-6:
        tries.append(take(voice, ps))
    return min(tries, key=lambda r: abs(r["rate"] - TARGET))


def asr_check(model_dir, clips):
    import sherpa_onnx
    from scipy import signal as sg

    d = Path(model_dir)
    rec = sherpa_onnx.OfflineRecognizer.from_paraformer(paraformer=str(d / "model.int8.onnx"),
                                                       tokens=str(d / "tokens.txt"), num_threads=4)
    out = []
    for x in clips:
        s = rec.create_stream()
        s.accept_waveform(16000, sg.resample_poly(x, 160, 441).astype(np.float32))
        rec.decode_stream(s)
        out.append(s.result.text.replace(" ", ""))
    return out


def edit(a, b):
    dp = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        prev, dp[0] = dp[0], i
        for j, cb in enumerate(b, 1):
            prev, dp[j] = dp[j], min(dp[j] + 1, dp[j - 1] + 1, prev + (ca != cb))
    return dp[-1]


# ---------------------------------------------------------------- 画面

SEGS: list = []
TOTAL = 0.0
INK, SUB, ACC = "#1E1E24", "#6B7080", "#C8102E"


def frame(c, t):
    c.drawColor(skia.ColorSetRGB(255, 255, 255))
    for seg in SEGS:
        if seg["t0"] - 0.0001 <= t < seg["t1"]:
            break
    else:
        seg = SEGS[-1]
    k = ease_out(clamp01((t - seg["t0"]) / 0.35))
    W = core.W
    K.text(c, "《丰田模式》音色试听", W / 2, 230, 46, "sans_medium", SUB, 1.0)
    K.text(c, f"{seg['i'] + 1} / {len(SEGS)}", W / 2, 300, 36, "sans_medium", SUB, 1.0)
    K.text(c, f"音色 {seg['label']}", W / 2, 640 + 30 * (1 - k), 210, "serif_black", INK, k)
    K.text(c, seg["trait"], W / 2, 860, 76, "serif_black", ACC, k)
    K.text(c, f"语速 {seg['rate']:.1f} 字/秒", W / 2, 960, 40, "sans_medium", SUB, k)
    for j, (a, b, s) in enumerate(seg["lines"]):
        if a <= t:
            al = clamp01((t - a) / 0.2)
            K.text(c, s, W / 2, 1300 + j * 110, 64, "serif", INK if t < b + 0.3 else SUB, al)
    # 播放进度
    p = clamp01((t - seg["a0"]) / max(0.1, seg["a1"] - seg["a0"]))
    K.seg(c, 240, 1620, W - 240, 1620, "#E4E4E8", 8)
    K.seg(c, 240, 1620, 240 + (W - 480) * p, 1620, ACC, 8)


def _render(i):
    surf = skia.Surface.MakeRaster(skia.ImageInfo.Make(core.W, core.H, skia.kRGBA_8888_ColorType,
                                                       skia.kPremul_AlphaType))
    frame(surf.getCanvas(), i / core.FPS)
    return surf.makeImageSnapshot().tobytes()


def main():
    global TOTAL
    OUT.mkdir(parents=True, exist_ok=True)
    asr = sys.argv[sys.argv.index("--asr") + 1] if "--asr" in sys.argv else None
    track, t = [], 0.0
    rows = []
    for i, (label, voice, kok, trait) in enumerate(CANDS):
        r = calibrate(voice)
        y = r["y"]
        a0 = t + LEAD
        s1_end = a0 + r["d1"]
        lines = [(a0, s1_end, SENTS[0].rstrip("。")), (s1_end + PERIOD, a0 + len(y) / audio.SR, SENTS[1].rstrip("。"))]
        seg_end = a0 + len(y) / audio.SR + BETWEEN
        SEGS.append(dict(i=i, label=label, trait=trait, rate=r["rate"], t0=t, t1=seg_end, a0=a0,
                         a1=a0 + len(y) / audio.SR, lines=lines))
        track.append((a0, y))
        rows.append(dict(label=label, voice=voice, prompt=kok, trait=trait, **{k: v for k, v in r.items()
                                                                              if k not in ("y", "raw", "d1")}))
        if asr:
            rows[-1]["asr"] = asr_check(asr, r["raw"])
        t = seg_end
    TOTAL = t
    n = int(TOTAL * audio.SR)
    import pyloudnorm
    st = np.zeros((n, 2))
    seg_l = [pyloudnorm.Meter(audio.SR).integrated_loudness(audio.pan(y, 0) * 1.41) for _, y in track]
    st2 = st                                # 各候选单独做响度对齐，比较时音量一致
    for (a0, y), L in zip(track, seg_l):
        i0 = int(a0 * audio.SR)
        seg = audio.pan(y / (np.max(np.abs(y)) + 1e-9) * 0.5, 0) * 1.41 * 10 ** ((-16 - L) / 20)
        st2[i0: i0 + len(seg)] += seg[: n - i0]
    st2 = np.clip(st2, -0.84, 0.84)
    for rw in rows:
        print(f"{rw['label']} {rw['voice']:12s} 提示 {rw['prompt']:12s} 提示语速 {rw['ps']:.2f} 步数 {STEPS} "
              f"整段 {rw['total']:.2f}s {rw['rate']:.2f}字/秒（纯语音 {rw['speech_rate']:.2f}） 原逗号停顿 {rw['gaps']} "
              f"ASR {rw.get('asr')}")
        if "asr" in rw:
            ref = ["".join(ch for ch in s if ch not in "，。") for s in SENTS]
            print(f"   字错数 {[edit(a, b) for a, b in zip(ref, rw['asr'])]}")
    out = OUT / "voice_audition.mp4"
    with tempfile.TemporaryDirectory() as tmp:
        wav = str(Path(tmp) / "a.wav")
        sf.write(wav, st2.astype(np.float32), audio.SR)
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{core.W}x{core.H}",
               "-r", str(core.FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "22",
               "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for i in range(int(round(TOTAL * core.FPS))):
            proc.stdin.write(_render(i))
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError("ffmpeg failed")
        for (label, voice, *_), (_, y) in zip(CANDS, track):
            sf.write(OUT / f"audition_{label}_{voice}.wav", y.astype(np.float32), audio.SR)
    print(out)


if __name__ == "__main__":
    main()
