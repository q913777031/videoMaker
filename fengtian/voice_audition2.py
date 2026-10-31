"""《丰田模式》音色试听 2：开源/在线中文 TTS 候选横向对比（像真人 + 有情绪），无配乐。

- 旁白 5 句（慢速讲解）：前 3 句同第一次试听，“少了”的“少”检查第三声；后 2 句检查情绪（恳切提醒、疑问）。
- 每个候选的逐句音频预先生成，放在 out/fengtian/audition2_src/<标签>_s<句号>.(wav|mp3)；
  生成方式见各候选的说明（CosyVoice 需在 models/venv_tts 里跑，edge-tts 需联网）。
- 停顿统一：逗号处最安静的一段改成 0.25 秒，句与句之间 0.5 秒，候选之间 1 秒静音；
- 响度：每段单独对齐到 -16 LUFS，再过 4 倍过采样的真峰值限幅（≤ -1 dBTP），整条约 -16 LUFS。
- 指标：语速（含停顿，字/秒）、每句基频范围（5%–95% 分位，半音）、能量起伏（语音帧 dB 标准差）；
  --asr DIR：sherpa-onnx paraformer 中文模型复核读字（按无调拼音比较，同音字不算错）。

用法：python3 -m fengtian.voice_audition2 [--asr DIR]   → out/fengtian/voice_audition2.mp4
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import skia
import soundfile as sf
from scipy import signal

from adler import core
from adler import kit as K
from engine import audio
from engine.gfx import clamp01, ease_out

OUT = Path(__file__).resolve().parent.parent / "out" / "fengtian"
SRC = OUT / "audition2_src"
SENTS = ["同一个问题，返工第三遍了。", "补了又坏，坏了又补。", "停线这么狠，返工反倒少了。",
         "你怕麻烦，麻烦就会找上你。", "停线多亏啊，为什么还要停？"]
COMMA, PERIOD, BETWEEN, LEAD, TAIL = 0.25, 0.5, 1.0, 0.8, 0.3
LUFS, TP = -16.0, -1.0

# (标签, 文件前缀, 模型名, 性别, 一句特点)
CANDS = [
    ("现用", "zvjian", "ZipVoice · zv_yunjian", "男声", "本地离线，现在成片用的就是它"),
    ("1", "cv3zs", "CosyVoice3 · 零样本", "男声", "音色同现用，韵律更像人说话"),
    ("2", "cv3ins", "CosyVoice3 · 语气指令", "男声", "音色同现用，提示“恳切、有起伏”"),
    ("3", "cv3insB", "CosyVoice3 · 语气指令", "男声", "换一种音色，语气更外放"),
    ("4", "sftm", "CosyVoice-300M · 中文男", "男声", "模型自带音色，平稳清楚"),
    ("5", "sftf", "CosyVoice-300M · 中文女", "女声", "模型自带音色，干净利落"),
    ("6", "edgeYunjian", "微软 Yunjian（在线）", "男声", "解说腔，有力度"),
    ("7", "edgeYunxi", "微软 Yunxi（在线）", "男声", "年轻自然，像聊天"),
    ("8", "edgeYunyang", "微软 Yunyang（在线）", "男声", "新闻播音腔，稳"),
    ("9", "edgeXiaoxiao", "微软 Xiaoxiao（在线）", "女声", "温暖亲切，起伏大"),
]


def load(prefix, i):
    for ext in ("wav", "mp3"):
        p = SRC / f"{prefix}_s{i}.{ext}"
        if p.exists():
            if ext == "mp3":
                with tempfile.TemporaryDirectory() as tmp:
                    w = Path(tmp) / "a.wav"
                    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(p), "-ac", "1", "-ar", str(audio.SR), str(w)],
                                   check=True)
                    x, _ = sf.read(w)
            else:
                x, sr = sf.read(p)
                if x.ndim > 1:
                    x = x.mean(1)
                if sr != audio.SR:
                    x = signal.resample_poly(x, audio.SR, sr)
            return audio._trim(np.asarray(x, np.float64))
    raise FileNotFoundError(f"{SRC}/{prefix}_s{i}.wav|mp3")


def set_comma(x, frac, target=COMMA):
    """在逗号附近（按字数估计位置 ±15%）找最安静的一段，整段换成 target 秒静音（短了补、长了剪）。"""
    hop = int(0.01 * audio.SR)
    n = len(x) // hop
    r = np.sqrt(np.mean(x[: n * hop].reshape(n, hop) ** 2, 1) + 1e-12)
    r3 = np.convolve(r, np.ones(3) / 3, "same")
    lo, hi = max(1, int(n * (frac - 0.15))), min(n - 1, int(n * (frac + 0.15)))
    i = lo + int(np.argmin(r3[lo:hi]))
    quiet = r3 < r.max() * 10 ** (-30 / 20)
    a = b = i
    if quiet[i]:
        while a > 0 and quiet[a - 1]:
            a -= 1
        while b < n and quiet[b]:
            b += 1
    have = (b - a) / 100
    f = int(0.01 * audio.SR)
    left, right = x[: a * hop].copy(), x[b * hop:].copy()
    left[-f:] *= np.linspace(1, 0, f)
    right[:f] *= np.linspace(0, 1, f)
    return np.concatenate([left, np.zeros(int(target * audio.SR)), right]), round(have, 2)


def han(s):
    return sum(1 for ch in s if "一" <= ch <= "鿿")


def build(prefix):
    parts, gaps, raw, lines, t = [], [], [], [], 0.0
    for i, s in enumerate(SENTS):
        x = load(prefix, i)
        raw.append(x)
        frac = han(s.split("，")[0]) / han(s)
        y, g = set_comma(x, frac)
        gaps.append(g)
        if i:
            parts.append(np.zeros(int(PERIOD * audio.SR)))
            t += PERIOD
        lines.append((t, t + len(y) / audio.SR, s.rstrip("。")))
        parts.append(y)
        t += len(y) / audio.SR
    y = np.concatenate(parts)
    return dict(y=y, raw=raw, lines=lines, gaps=gaps, total=len(y) / audio.SR,
                rate=sum(map(han, SENTS)) / (len(y) / audio.SR),
                speech_rate=sum(map(han, SENTS)) / (sum(len(r) for r in raw) / audio.SR))


# ---------------------------------------------------------------- 情绪起伏指标

def expressiveness(x):
    """基频范围（5%–95% 分位，半音）与能量起伏（语音帧 dB 标准差）。"""
    import parselmouth

    x16 = signal.resample_poly(x, 160, 441)
    snd = parselmouth.Sound(x16, 16000)
    p = snd.to_pitch_ac(time_step=0.01, pitch_floor=60, pitch_ceiling=450)
    f = p.selected_array["frequency"]
    f = f[f > 0]
    st = 12 * np.log2(f / np.median(f))
    st = st[np.abs(st) < 12]                      # 去掉倍频/半频误判
    rng = float(np.percentile(st, 95) - np.percentile(st, 5)) if len(st) > 5 else 0.0
    hop = 400
    n = len(x16) // hop
    db = 20 * np.log10(np.sqrt(np.mean(x16[: n * hop].reshape(n, hop) ** 2, 1)) + 1e-9)
    sp = db[db > db.max() - 35]
    return round(rng, 1), round(float(np.std(sp)), 1)


# ---------------------------------------------------------------- 响度

def true_peak_limit(y, ceiling_db=TP - 0.2):
    """4 倍过采样估计真峰值，超出部分用 5ms 起音 / 80ms 释放的增益包络压下去。"""
    up = signal.resample_poly(y, 4, 1)
    pk = np.abs(up).reshape(-1, 4).max(1)[: len(y)]
    pk = np.pad(pk, (0, len(y) - len(pk)), mode="edge")
    lim = 10 ** (ceiling_db / 20)
    need = np.minimum(1.0, lim / np.maximum(pk, 1e-9))
    a = int(0.005 * audio.SR)
    from scipy.ndimage import minimum_filter1d
    g = minimum_filter1d(need, 2 * a + 1)
    rel = np.exp(-1 / (0.08 * audio.SR))
    out = np.empty_like(g)
    cur = 1.0
    for i, v in enumerate(g):                     # 逐样本释放（下降立即跟随，回升按指数）
        cur = v if v < cur else v + (cur - v) * rel
        out[i] = cur
    return y * out


def measure(st):
    """ffmpeg ebur128：整体响度与真峰值。"""
    with tempfile.TemporaryDirectory() as tmp:
        w = str(Path(tmp) / "m.wav")
        sf.write(w, st.astype(np.float32), audio.SR)
        r = subprocess.run(["ffmpeg", "-nostats", "-i", w, "-af", "ebur128=peak=true", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
    tail = r[r.rfind("Summary:"):]
    i = float(tail.split("I:")[1].split("LUFS")[0])
    p = float(tail.split("Peak:")[1].split("dBFS")[0])
    return i, p


# ---------------------------------------------------------------- ASR

def asr_check(model_dir, clips):
    import sherpa_onnx

    d = Path(model_dir)
    rec = sherpa_onnx.OfflineRecognizer.from_paraformer(paraformer=str(d / "model.int8.onnx"),
                                                       tokens=str(d / "tokens.txt"), num_threads=4)
    out = []
    for x in clips:
        s = rec.create_stream()
        s.accept_waveform(16000, signal.resample_poly(x, 160, 441).astype(np.float32))
        rec.decode_stream(s)
        out.append(s.result.text.replace(" ", ""))
    return out


def py_errs(ref, hyp):
    """按无调拼音算编辑距离（ASR 的同音字不算错）。"""
    from pypinyin import lazy_pinyin

    a = lazy_pinyin("".join(ch for ch in ref if "一" <= ch <= "鿿"))
    b = lazy_pinyin("".join(ch for ch in hyp if "一" <= ch <= "鿿"))
    dp = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        prev, dp[0] = dp[0], i
        for j, cb in enumerate(b, 1):
            prev, dp[j] = dp[j], min(dp[j] + 1, dp[j - 1] + 1, prev + (ca != cb))
    return dp[-1]


# ---------------------------------------------------------------- 画面

SEGS: list = []
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
    K.text(c, "《丰田模式》音色试听 · 第二轮", W / 2, 200, 44, "sans_medium", SUB, 1.0)
    K.text(c, f"{seg['i'] + 1} / {len(SEGS)}", W / 2, 268, 34, "sans_medium", SUB, 1.0)
    big = "现用" if seg["label"] == "现用" else f"音色 {seg['label']}"
    K.text(c, big, W / 2, 520 + 30 * (1 - k), 190, "serif_black", INK, k)
    K.text(c, seg["model"], W / 2, 730, 62, "serif_black", INK, k)
    K.text(c, f"{seg['gender']} · {seg['trait']}", W / 2, 830, 52, "serif_black", ACC, k)
    K.text(c, f"语速 {seg['rate']:.1f} 字/秒", W / 2, 910, 38, "sans_medium", SUB, k)
    for j, (a, b, s) in enumerate(seg["lines"]):
        if a <= t:
            al = clamp01((t - a) / 0.2)
            K.text(c, s, W / 2, 1110 + j * 115, 66, "serif", INK if t < b + 0.3 else SUB, al)
    p = clamp01((t - seg["a0"]) / max(0.1, seg["a1"] - seg["a0"]))
    K.seg(c, 240, 1760, W - 240, 1760, "#E4E4E8", 8)
    K.seg(c, 240, 1760, 240 + (W - 480) * p, 1760, ACC, 8)


def _render(i):
    surf = skia.Surface.MakeRaster(skia.ImageInfo.Make(core.W, core.H, skia.kRGBA_8888_ColorType,
                                                       skia.kPremul_AlphaType))
    frame(surf.getCanvas(), i / core.FPS)
    return surf.makeImageSnapshot().tobytes()


def main():
    import pyloudnorm

    OUT.mkdir(parents=True, exist_ok=True)
    asr = sys.argv[sys.argv.index("--asr") + 1] if "--asr" in sys.argv else None
    meter = pyloudnorm.Meter(audio.SR)
    track, rows, t = [], [], 0.0
    for i, (label, prefix, model, gender, trait) in enumerate(CANDS):
        r = build(prefix)
        y = r["y"] * 10 ** ((LUFS - 3.01 - meter.integrated_loudness(r["y"])) / 20)   # 单声道复制成双声道后 +3dB
        y = true_peak_limit(y)
        a0 = t + LEAD
        lines = [(a0 + a, a0 + b, s) for a, b, s in r["lines"]]
        t1 = a0 + len(y) / audio.SR + (BETWEEN if i < len(CANDS) - 1 else TAIL)
        SEGS.append(dict(i=i, label=label, model=model, gender=gender, trait=trait, rate=r["rate"], t0=t, t1=t1,
                         a0=a0, a1=a0 + len(y) / audio.SR, lines=lines))
        track.append((a0, y))
        ex = [expressiveness(x) for x in r["raw"]]
        row = dict(label=label, prefix=prefix, model=model, total=round(r["total"], 2), rate=round(r["rate"], 2),
                   speech_rate=round(r["speech_rate"], 2), comma_orig=r["gaps"],
                   f0_range_st=[e[0] for e in ex], energy_std_db=[e[1] for e in ex],
                   f0_range_mean=round(float(np.mean([e[0] for e in ex])), 1),
                   energy_std_mean=round(float(np.mean([e[1] for e in ex])), 1))
        if asr:
            hyp = asr_check(asr, r["raw"])
            row["asr"] = hyp
            row["asr_pinyin_errs"] = [py_errs(a, b) for a, b in zip(SENTS, hyp)]
        rows.append(row)
        t = t1
    total = t
    n = int(round(total * core.FPS)) * audio.SR // core.FPS
    mono = np.zeros(n)
    for a0, y in track:
        i0 = int(a0 * audio.SR)
        mono[i0: i0 + len(y)] += y[: n - i0]
    st = np.stack([mono, mono], 1)
    lufs, tp = measure(st)
    for rw in rows:
        print(json.dumps(rw, ensure_ascii=False))
    print(f"整条 {total:.1f}s  {lufs:.1f} LUFS  真峰值 {tp:.1f} dBTP")
    (OUT / "voice_audition2_stats.json").write_text(json.dumps(dict(rows=rows, lufs=lufs, true_peak=tp), ensure_ascii=False,
                                                               indent=1))
    out = OUT / "voice_audition2.mp4"
    with tempfile.TemporaryDirectory() as tmp:
        wav = str(Path(tmp) / "a.wav")
        sf.write(wav, st.astype(np.float32), audio.SR)
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{core.W}x{core.H}",
               "-r", str(core.FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "22",
               "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for i in range(int(round(total * core.FPS))):
            proc.stdin.write(_render(i))
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError("ffmpeg failed")
    for (label, prefix, *_), (_, y) in zip(CANDS, track):
        sf.write(OUT / f"audition2_{label}_{prefix}.wav", y.astype(np.float32), audio.SR)
    print(out)


if __name__ == "__main__":
    main()
