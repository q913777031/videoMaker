"""《丰田模式》音色试听 3：IndexTTS2 各情绪设置 vs 现用 CosyVoice3（第 01 讲的一段），无配乐。

- 段落取自第 01 讲（5 句）；每个方案逐句合成（和成片一样），多音字标注沿用 ep01 的 PINYIN（引擎自动换成 IndexTTS2 写法）；
- 现用 = CosyVoice3 语气指令版（cv3i_yunjian，第二轮试听的“候选 2”），直接取 .cache/tts 里 ep01 的合成结果；
- IndexTTS2 音色提示全程用本地合成音：ix2_cv3jian（ep01 现用旁白里的两句，音色一致）、ix2_yunjian（ZipVoice 对照）；
- 停顿统一：逗号/冒号处最安静的一段改成 0.25 秒，句与句之间 0.5 秒，方案之间 1 秒静音；
- 响度：每段单独对齐到 -16 LUFS，再过真峰值限幅（≤ -1 dBTP）；
- 指标：语速（含停顿）、基频范围（5%–95% 分位，半音）、能量起伏（dB 标准差），多音字处基频走向粗查；
  --asr DIR：sherpa-onnx paraformer 中文模型复核读字（按无调拼音比较）。

用法：python3 -m fengtian.voice_audition3 [--gen-only] [--asr DIR]   → out/fengtian/voice_audition3.mp4
"""

import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
import skia
import soundfile as sf
from scipy import signal

from adler import kit as K
from engine import audio
from engine.gfx import clamp01, ease_out
from fengtian.voice_audition2 import asr_check, expressiveness, han, measure, py_errs, true_peak_limit

W, H, FPS = 1080, 1620, 30
OUT = Path(__file__).resolve().parent.parent / "out" / "fengtian"
SENTS = ["你是不是也这样：同一个问题，改了三遍还在返工。", "补了又坏，坏了又补，越改越心累。",
         "你可能会想：停线多亏啊，为什么还要停？", "你怕麻烦，麻烦就会找上你。", "我知道，当场说出来，需要一点勇气。"]
PINYIN = [("组长", "组[zh][ǎng]"), ("重新", "[ch][óng]新"), ("宁可", "[n][ìng]可"), ("当场", "[d][āng]场"),
          ("个数", "个[sh][ù]"), ("应付", "[y][ìng]付"), ("少一点", "[sh][ǎo]一点"), ("扛着", "[k][áng]着")]
COMMA, PERIOD, BETWEEN, LEAD, TAIL = 0.25, 0.5, 1.0, 0.8, 0.4
LUFS = -16.0

# 每句的情绪：温和讲解 / 关切 / 略带惊讶的疑问 / 关切提醒 / 平静收尾
EMO_TEXT = ["语气温和，像跟朋友聊天一样耐心讲解", "带着体谅和关心，有点心疼对方", "略带惊讶，好奇地反问",
            "认真、关切地提醒", "平静、温暖，让人安心"]
EMO_VEC = [{"calm": 0.8, "happy": 0.2}, {"calm": 0.65, "melancholic": 0.35}, {"calm": 0.5, "surprised": 0.5},
           {"calm": 0.75, "melancholic": 0.25}, {"calm": 0.85, "happy": 0.15}]
SPEED = 1.0

# (标签, 音色, 每句 emo（列表）或 None, 大字下的说明两行)
SCHEMES = [
    ("现用", "cv3", None, ("CosyVoice3 · 语气指令（候选 2）", "第 01 讲现在用的旁白")),
    ("方案 1", "ix2_cv3jian", None, ("IndexTTS2 · 不加情绪控制", "音色提示 = 第 01 讲现用旁白，情绪跟着提示走")),
    ("方案 2", "ix2_cv3jian", [{"text": t, "alpha": 0.7} for t in EMO_TEXT],
     ("IndexTTS2 · 文字描述情绪 · 强度 0.7", "逐句：温和讲解 / 关切 / 略惊讶 / 提醒 / 平静")),
    ("方案 3", "ix2_cv3jian", [{"vector": v, "alpha": 0.7} for v in EMO_VEC],
     ("IndexTTS2 · 情绪向量 · 强度 0.7", "逐句：平静+喜 / 平静+低落 / 平静+惊讶 …")),
    ("方案 4", "ix2_cv3jian", [{"text": s, "alpha": 0.6} for s in SENTS],
     ("IndexTTS2 · 按台词自动判断情绪 · 强度 0.6", "情绪由模型读台词自己判断")),
    ("方案 5", "ix2_yunjian", [{"text": t, "alpha": 0.7} for t in EMO_TEXT],
     ("IndexTTS2 · 换音色提示（ZipVoice 云健）", "情绪设置同方案 2，用来对照音色")),
]
# 多音字粗查：(句号, 词, 词在句中第几个汉字起, 期望声调)
POLY = [(0, "还", 16, [2]), (0, "返工", 18, [3, 1]), (1, "累", 12, [4]), (2, "还", 13, [2]),
        (4, "当场", 3, [1, 3])]


def tts_text(t):
    for a, b in PINYIN:
        t = t.replace(a, b)
    return t


def synth(voice, emos, log):
    """逐句合成（命中缓存则直接取）；返回原始音频列表与每句合成耗时。"""
    if voice == "cv3":
        nar = audio.Narrator("cv3i_yunjian", prompt_speed=0.95)
    else:
        nar = audio.Narrator(voice)
    xs, secs, vecs = [], [], []
    for i, s in enumerate(SENTS):
        t = time.perf_counter()
        x = nar.generate(tts_text(s), SPEED, 8, **({"emo": emos[i]} if emos else {}))
        dt = time.perf_counter() - t
        last = getattr(nar, "_ix2", None) and nar._ix2.get("last")
        if dt > 5 and last:
            secs.append((last["secs"], len(x) / audio.SR))
            vecs.append(last.get("emo_vector"))
            nar._ix2["last"] = None
        else:
            vecs.append(None)
        print(f"  [{voice}] s{i} {len(x) / audio.SR:.2f}s audio, {dt:.0f}s wall", file=log, flush=True)
        xs.append(x)
    if getattr(nar, "_ix2", None) and nar._ix2.get("proc"):
        nar._ix2["proc"].stdin.close()
        nar._ix2["proc"].wait()
    return xs, secs, vecs


# ---------------------------------------------------------------- 停顿统一

def _rms(x):
    hop = int(0.01 * audio.SR)
    n = len(x) // hop
    r = np.sqrt(np.mean(x[: n * hop].reshape(n, hop) ** 2, 1) + 1e-12)
    return r, np.convolve(r, np.ones(3) / 3, "same")


def set_pauses(x, s):
    """句内每个逗号/冒号：在按字数估计的位置 ±12% 内找最安静的一段，整段换成 COMMA 秒静音。返回新音频与原停顿长度。"""
    hop = int(0.01 * audio.SR)
    r, r3 = _rms(x)
    n = len(r)
    quiet = r3 < r.max() * 10 ** (-30 / 20)
    total = han(s)
    fracs, k = [], 0
    for ch in s[:-1]:
        if "一" <= ch <= "鿿":
            k += 1
        elif ch in "，：；,":
            fracs.append(k / total)
    cuts = []
    for f in fracs:
        lo, hi = max(1, int(n * (f - 0.12))), min(n - 1, int(n * (f + 0.12)))
        i = lo + int(np.argmin(r3[lo:hi]))
        a = b = i
        if quiet[i]:
            while a > 0 and quiet[a - 1]:
                a -= 1
            while b < n and quiet[b]:
                b += 1
        cuts.append((a, b))
    parts, gaps, prev = [], [], 0
    f = hop
    for a, b in cuts:
        seg = x[prev * hop: a * hop].copy()
        if prev:
            seg[:f] *= np.linspace(0, 1, f)
        seg[-f:] *= np.linspace(1, 0, f)
        parts += [seg, np.zeros(int(COMMA * audio.SR))]
        gaps.append(round((b - a) / 100, 2))
        prev = b
    seg = x[prev * hop:].copy()
    if prev:
        seg[:f] *= np.linspace(0, 1, f)
    parts.append(seg)
    return np.concatenate(parts), gaps, cuts


def build(raw):
    parts, lines, gaps, t = [], [], [], 0.0
    for i, (s, x) in enumerate(zip(SENTS, raw)):
        y, g, _ = set_pauses(x, s)
        gaps.append(g)
        if i:
            parts.append(np.zeros(int(PERIOD * audio.SR)))
            t += PERIOD
        lines.append((t, t + len(y) / audio.SR, s))
        parts.append(y)
        t += len(y) / audio.SR
    y = np.concatenate(parts)
    nh = sum(map(han, SENTS))
    return dict(y=y, lines=lines, gaps=gaps, total=len(y) / audio.SR, rate=nh / (len(y) / audio.SR))


# ---------------------------------------------------------------- 多音字基频粗查

def _pitch(x):
    import parselmouth

    x16 = signal.resample_poly(x, 160, 441)
    p = parselmouth.Sound(x16, 16000).to_pitch_ac(time_step=0.01, pitch_floor=60, pitch_ceiling=450)
    return p.xs(), p.selected_array["frequency"]


def tone_check(x, s, start, n_ch):
    """把句子的字数按时间均分到各语音段（逗号处分开），取目标字所在时间窗的基频走向（半音，起→止）。"""
    _, _, cuts = set_pauses(x, s)             # 只借用逗号位置
    clauses, k = [], 0
    for part in s.replace("：", "，").rstrip("。？").split("，"):
        clauses.append((k, k + han(part)))
        k += han(part)
    r, r3 = _rms(x)
    on = np.where(20 * np.log10(r3 / r3.max() + 1e-9) > -32)[0]
    bounds = [on[0]] + [v for ab in cuts for v in ab] + [on[-1]]
    ts, f = _pitch(x)
    res = []
    for c in range(n_ch):
        ci = next(j for j, (a, b) in enumerate(clauses) if a <= start + c < b)
        a, b = clauses[ci]
        t0, t1 = bounds[2 * ci] / 100, bounds[2 * ci + 1] / 100
        u0 = t0 + (t1 - t0) * (start + c - a) / (b - a)
        u1 = t0 + (t1 - t0) * (start + c + 1 - a) / (b - a)
        m = (ts >= u0) & (ts < u1) & (f > 0)
        if m.sum() < 3:
            res.append(None)
            continue
        st = 12 * np.log2(f[m] / np.median(f[f > 0]))
        q = max(1, len(st) // 4)
        res.append((round(float(np.mean(st[:q])), 1), round(float(np.mean(st[-q:])), 1)))
    return res


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
    K.text(c, "《丰田模式》音色试听 · 第三轮", W / 2, 120, 40, "sans_medium", SUB, 1.0)
    K.text(c, f"{seg['i'] + 1} / {len(SEGS)}", W / 2, 180, 32, "sans_medium", SUB, 1.0)
    K.text(c, seg["label"], W / 2, 380 + 30 * (1 - k), 180, "serif_black", INK, k)
    K.text(c, seg["note"][0], W / 2, 580, 50, "serif_black", INK, k)
    K.text(c, seg["note"][1], W / 2, 660, 38, "sans_medium", ACC, k)
    K.text(c, f"语速 {seg['rate']:.1f} 字/秒（含停顿）", W / 2, 730, 34, "sans_medium", SUB, k)
    cur = None
    for a, b, s in seg["lines"]:
        if a - 0.05 <= t:
            cur = (a, b, s)
    if cur is not None:
        a, b, s = cur
        al = clamp01((t - a + 0.05) / 0.15)
        parts = [p for p in s.replace("：", "，").rstrip("。").split("，") if p]
        lines = parts if len(parts) <= 2 else ["，".join(parts[:-1]), parts[-1]]
        for j, ln in enumerate(lines):
            K.text(c, ln, W / 2, 1060 + j * 100, 62, "serif", INK, al)
    p = clamp01((t - seg["a0"]) / max(0.1, seg["a1"] - seg["a0"]))
    K.seg(c, 200, 1420, W - 200, 1420, "#E4E4E8", 8)
    K.seg(c, 200, 1420, 200 + (W - 400) * p, 1420, ACC, 8)


def _render(i):
    surf = skia.Surface.MakeRaster(skia.ImageInfo.Make(W, H, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType))
    frame(surf.getCanvas(), i / FPS)
    return surf.makeImageSnapshot().tobytes()


def main():
    import pyloudnorm

    OUT.mkdir(parents=True, exist_ok=True)
    asr = sys.argv[sys.argv.index("--asr") + 1] if "--asr" in sys.argv else None
    raws = {}
    for label, voice, emos, _ in SCHEMES:
        print(f"== {label} {voice}", flush=True)
        raws[label] = synth(voice, emos, sys.stdout)
    if "--gen-only" in sys.argv:
        return
    meter = pyloudnorm.Meter(audio.SR)
    track, rows, t = [], [], 0.0
    for i, (label, voice, emos, note) in enumerate(SCHEMES):
        raw, secs, vecs = raws[label]
        r = build(raw)
        y = r["y"] * 10 ** ((LUFS - 3.01 - meter.integrated_loudness(r["y"])) / 20)   # 单声道复制成双声道后 +3dB
        y = true_peak_limit(y)
        a0 = t + LEAD
        lines = [(a0 + a, a0 + b, s) for a, b, s in r["lines"]]
        t1 = a0 + len(y) / audio.SR + (BETWEEN if i < len(SCHEMES) - 1 else TAIL)
        SEGS.append(dict(i=i, label=label, note=note, rate=r["rate"], t0=t, t1=t1, a0=a0, a1=a0 + len(y) / audio.SR,
                         lines=lines))
        track.append((a0, y))
        ex = [expressiveness(x) for x in raw]
        whole = expressiveness(r["y"])
        row = dict(label=label, voice=voice, total=round(r["total"], 2), rate=round(r["rate"], 2),
                   pauses_orig=r["gaps"], f0_range_st=[e[0] for e in ex], energy_std_db=[e[1] for e in ex],
                   f0_range_mean=round(float(np.mean([e[0] for e in ex])), 1),
                   energy_std_mean=round(float(np.mean([e[1] for e in ex])), 1),
                   f0_range_whole=whole[0], energy_std_whole=whole[1],
                   tones={f"s{si}{w}": tone_check(raw[si], SENTS[si], st, len(w)) for si, w, st, _ in POLY})
        if secs:
            row["synth_secs"] = [round(a, 1) for a, _ in secs]
            row["rtf"] = round(sum(a for a, _ in secs) / sum(b for _, b in secs), 1)
        if any(vecs):
            row["emo_vectors"] = vecs
        if asr:
            hyp = asr_check(asr, raw)
            row["asr"] = hyp
            row["asr_pinyin_errs"] = [py_errs(a, b) for a, b in zip(SENTS, hyp)]
        rows.append(row)
        t = t1
    total = t
    n = int(round(total * FPS)) * audio.SR // FPS
    mono = np.zeros(n)
    for a0, y in track:
        i0 = int(a0 * audio.SR)
        mono[i0: i0 + len(y)] += y[: n - i0]
    st = np.stack([mono, mono], 1)
    lufs, tp = measure(st)
    for rw in rows:
        print(json.dumps(rw, ensure_ascii=False))
    print(f"整条 {total:.1f}s  {lufs:.1f} LUFS  真峰值 {tp:.1f} dBTP")
    (OUT / "voice_audition3_stats.json").write_text(json.dumps(dict(rows=rows, lufs=lufs, true_peak=tp),
                                                               ensure_ascii=False, indent=1))
    out = OUT / "voice_audition3.mp4"
    with tempfile.TemporaryDirectory() as tmp:
        wav = str(Path(tmp) / "a.wav")
        sf.write(wav, st.astype(np.float32), audio.SR)
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
               "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "22",
               "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for i in range(int(round(total * FPS))):
            proc.stdin.write(_render(i))
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError("ffmpeg failed")
    for (label, voice, *_), (_, y) in zip(SCHEMES, track):
        sf.write(OUT / f"audition3_{label.replace(' ', '')}.wav", y.astype(np.float32), audio.SR)
    print(out)


if __name__ == "__main__":
    main()
