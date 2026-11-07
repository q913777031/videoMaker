"""《丰田模式》配音试听 4：治“突然情绪高昂”——现用 vs IndexTTS2 修正版 vs 新开源模型，无配乐。

- 文本：第 02 讲第 0、1、2、3、10、11、28 句（plan.load("02")），多音字标注沿用第 02 讲 PINYIN；
- 逗号停顿同成片（fengtian.common.stretch：补到 0.25 秒、模型自带的长停顿压到 0.6 秒），句与句之间 0.5 秒，方案之间 1 秒；
- 每段单独对齐 -16 LUFS，再过真峰值限幅（≤ -1 dBTP）；
- 指标（逐句裁好首尾静音的原始合成音）：
    f0_dev_st   逐句基频中位数偏离全段基频中位数的最大值（半音）——“突然高八度”就看它；
    loud_dev_db 逐句响度（LUFS）偏离全段响度的最大值（dB）；
    rate        语速含停顿（字/秒，按上面的停顿规则拼好后算）；speech_rate 不含停顿（去掉 ≥0.12 秒的静音段）；
    asr_errs    sherpa-onnx paraformer 复核读字（无调拼音编辑距离，同音字不算错）；
    secs_per_10s 每 10 秒语音的合成耗时（命中缓存的读 stats 里上次记下的值）。

方案：
  现用    fengtian.voice.synthesize（逐句文字情绪，强度 0.7）——命中缓存；
  方案 1  IndexTTS2 不加情绪，同屏几句连成一段一次合成（屏内语调连贯），合成后按句间停顿切回逐句；
  方案 2  IndexTTS2 全程固定情绪向量（平静 0.8 + 喜 0.1，强度 0.35），逐句合成；
  方案 3  方案 1 + 方案 2：固定平静向量 + 同屏连读；
  方案 4  VoxCPM 1.5（Apache-2.0，engine/voxcpm_worker.py）：同一音色提示 + 提示文本续写，逐句合成；
  方案 5  VoxCPM 1.5 同屏连读。
合成耗时按方案记在 out/fengtian/audition4_secs.json（命中缓存时沿用上次实测）。

用法：python3 -m fengtian.voice_audition4 [--gen-only] [--only 方案1,方案2] [--asr DIR]  → out/fengtian/voice_audition4.mp4
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
from fengtian import plan, voice
from fengtian.common import stretch
from fengtian.voice_audition2 import asr_check, han, measure, py_errs, true_peak_limit

W, H, FPS = 1080, 1620, 30
OUT = Path(__file__).resolve().parent.parent / "out" / "fengtian"
STATS = OUT / "voice_audition4_stats.json"
SECS = OUT / "audition4_secs.json"
P = plan.load("02")
IDX = [0, 1, 2, 3, 10, 11, 28]
GROUPS = [[0, 1], [2], [3], [10, 11], [28]]          # 第 02 讲 SCREENS 里同屏的句子（第 3 句同屏的第 4 句不在本段）
SENTS = [P["LINES"][i][0] for i in IDX]
MOODS = [P["LINE_MOOD"][i] for i in IDX]
PERIOD, BETWEEN, LEAD, TAIL = 0.5, 1.0, 0.8, 0.4
LUFS = -16.0
CALM = {"vector": {"calm": 0.8, "happy": 0.1}, "alpha": 0.35}

SCHEMES = [
    ("现用", "now", ("IndexTTS2 · 逐句文字情绪 · 强度 0.7", "每句单独合成，情绪按句子换")),
    ("方案 1", "ix2_plain_group", ("IndexTTS2 · 不加情绪 · 同屏连读", "一屏几句一次合成，语调连成一段")),
    ("方案 2", "ix2_calm", ("IndexTTS2 · 固定平静情绪 · 强度 0.35", "全程平静 0.8 + 喜 0.1，逐句合成")),
    ("方案 3", "ix2_calm_group", ("IndexTTS2 · 固定平静 + 同屏连读", "方案 1 和方案 2 合在一起")),
    ("方案 4", "vx", ("VoxCPM 1.5 · 新开源模型", "同一音色提示，续写模式，逐句合成")),
    ("方案 5", "vx_group", ("VoxCPM 1.5 · 同屏连读", "方案 4 换成一屏几句一次合成")),
]


def tts(i):
    return voice.tts_text(SENTS[i], P["PINYIN"])


# ---------------------------------------------------------------- 合成

def _gen(nar, text, emo):
    """合成一段；返回 (音频, 本次合成耗时或 None（命中缓存）)。"""
    c = nar._ix2 or nar._vx
    c["last"] = None
    x = nar.generate(text, 1.0, 8, emo=emo)
    last = c.get("last")
    return x, (last["secs"] if last else None)


def split_group(x, texts):
    """一段连读音频按句切开：句界预期位置（按字数）±15% 内最长的静音段，从中间切。"""
    hop = int(0.01 * audio.SR)
    n = len(x) // hop
    r = np.sqrt(np.mean(x[: n * hop].reshape(n, hop) ** 2, 1) + 1e-12)
    r3 = np.convolve(r, np.ones(3) / 3, "same")
    quiet = r3 < r.max() * 10 ** (-35 / 20)
    runs, i = [], 0
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]:
                j += 1
            runs.append((i, j))
            i = j
        else:
            i += 1
    tot = sum(map(han, texts))
    cuts, acc = [0], 0
    for t in texts[:-1]:
        acc += han(t)
        c = acc / tot * n
        cand = [(b - a, a, b) for a, b in runs if abs((a + b) / 2 - c) < 0.15 * n]
        if not cand:
            raise RuntimeError(f"找不到句界：{t}")
        _, a, b = max(cand)
        cuts.append((a + b) // 2)
    cuts.append(n)
    return [audio._trim(x[a * hop: b * hop]) for a, b in zip(cuts, cuts[1:])]


def synth(kind, log=sys.stdout):
    """返回 (逐句原始音频, [(合成秒, 语音秒)])。"""
    if kind == "now":
        xs = voice.synthesize([P["LINES"][i] for i in IDX], MOODS, P["PINYIN"])
        return xs, []
    if kind.startswith("vx"):
        nar, emo = audio.Narrator("vx_cv3jian"), None
    else:
        nar, emo = audio.Narrator("ix2_cv3jian"), (CALM if "calm" in kind else None)
    xs, secs = [], []
    groups = GROUPS if "group" in kind else [[k] for k in IDX]
    for g in groups:
        ks = [IDX.index(i) for i in g]
        text = "".join(tts(k) for k in ks)
        t = time.perf_counter()
        x, s = _gen(nar, text, emo)
        if s is not None:
            secs.append((s, len(x) / audio.SR))
        parts = split_group(x, [SENTS[k] for k in ks]) if len(ks) > 1 else [x]
        xs += parts
        print(f"  [{kind}] {g} {len(x) / audio.SR:.1f}s audio, {time.perf_counter() - t:.0f}s wall", file=log, flush=True)
    nar.close()
    known = json.loads(SECS.read_text()) if SECS.exists() else {}
    if secs:
        known[kind] = secs
        SECS.write_text(json.dumps(known, ensure_ascii=False, indent=1))
    return xs, known.get(kind, [])


# ---------------------------------------------------------------- 指标

def _f0(x):
    import parselmouth

    x16 = signal.resample_poly(x, 160, 441)
    p = parselmouth.Sound(x16, 16000).to_pitch_ac(time_step=0.01, pitch_floor=60, pitch_ceiling=400)
    f = p.selected_array["frequency"]
    return f[f > 0]


def speech_secs(x, min_gap=0.12):
    hop = int(0.01 * audio.SR)
    n = len(x) // hop
    r = np.sqrt(np.mean(x[: n * hop].reshape(n, hop) ** 2, 1) + 1e-12)
    r3 = np.convolve(r, np.ones(3) / 3, "same")
    quiet = r3 < r.max() * 10 ** (-35 / 20)
    drop, i = 0, 0
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]:
                j += 1
            if j - i >= min_gap * 100:
                drop += j - i
            i = j
        else:
            i += 1
    return (n - drop) / 100


def metrics(raw, built):
    import pyloudnorm

    meter = pyloudnorm.Meter(audio.SR)
    f0s = [_f0(x) for x in raw]
    allf = np.concatenate(f0s)
    ref = np.median(allf)
    med = [12 * np.log2(np.median(f) / ref) for f in f0s]
    whole = meter.integrated_loudness(np.concatenate(raw))
    loud = [meter.integrated_loudness(x) - whole for x in raw]
    nh = sum(map(han, SENTS))
    return dict(f0_med_hz=round(float(ref), 1), f0_dev_st=[round(float(v), 1) for v in med],
                f0_dev_max=round(float(np.max(np.abs(med))), 1),
                loud_dev_db=[round(float(v), 1) for v in loud], loud_dev_max=round(float(np.max(np.abs(loud))), 1),
                rate=round(nh / built["total"], 2), speech_rate=round(nh / sum(map(speech_secs, raw)), 2))


# ---------------------------------------------------------------- 拼段

def build(raw):
    parts, lines, t = [], [], 0.0
    for k, x in enumerate(raw):
        y, _ = stretch(x, P["LINES"][IDX[k]][0], 0.25, 0.6)
        if k:
            parts.append(np.zeros(int(PERIOD * audio.SR)))
            t += PERIOD
        lines.append((t, t + len(y) / audio.SR, SENTS[k]))
        parts.append(y)
        t += len(y) / audio.SR
    y = np.concatenate(parts)
    return dict(y=y, lines=lines, total=len(y) / audio.SR)


# ---------------------------------------------------------------- 画面

SEGS: list = []
INK, SUB, ACC, OK, BAD = "#1E1E24", "#6B7080", "#C8102E", "#2E7D32", "#C8102E"


def _wrap(s):
    parts = [p for p in s.replace("：", "：，").replace("？", "？，").rstrip("。").split("，") if p]
    out, cur = [], ""
    for p in parts:
        if cur and han(cur + p) > 11:
            out.append(cur)
            cur = p
        else:
            cur = cur + ("" if not cur or cur.endswith(("：", "？")) else "，") + p
    return out + [cur]


def frame(c, t):
    c.drawColor(skia.ColorSetRGB(255, 255, 255))
    for seg in SEGS:
        if seg["t0"] - 0.0001 <= t < seg["t1"]:
            break
    else:
        seg = SEGS[-1]
    k = ease_out(clamp01((t - seg["t0"]) / 0.35))
    m = seg["m"]
    K.text(c, "《丰田模式》配音试听 · 第四轮", W / 2, 110, 40, "sans_medium", SUB, 1.0)
    K.text(c, f"{seg['i'] + 1} / {len(SEGS)}", W / 2, 170, 32, "sans_medium", SUB, 1.0)
    K.text(c, seg["label"], W / 2, 370 + 30 * (1 - k), 180, "serif_black", INK, k)
    K.text(c, seg["note"][0], W / 2, 560, 48, "serif_black", INK, k)
    K.text(c, seg["note"][1], W / 2, 640, 38, "sans_medium", ACC, k)
    ok = lambda v: OK if v else BAD
    K.text(c, f"音高最大偏离 {m['f0_dev_max']:.1f} 半音 · 响度最大偏差 {m['loud_dev_max']:.1f} dB", W / 2, 720, 32,
           "sans_medium", ok(m["f0_dev_max"] <= 3 and m["loud_dev_max"] <= 2), k)
    K.text(c, f"语速 {m['rate']:.1f} 字/秒（含停顿）", W / 2, 775, 32, "sans_medium",
           ok(3.8 <= m["rate"] <= 4.3), k)
    cur = None
    for a, b, s in seg["lines"]:
        if a - 0.05 <= t:
            cur = (a, b, s)
    if cur is not None:
        a, b, s = cur
        al = clamp01((t - a + 0.05) / 0.15)
        for j, ln in enumerate(_wrap(s)):
            K.text(c, ln, W / 2, 1040 + j * 100, 62, "serif", INK, al)
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
    only = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
    schemes = SCHEMES
    if only:
        schemes = [s for s in schemes if s[0].replace(" ", "") in only]
    raws = {}
    for label, kind, _ in schemes:
        print(f"== {label} {kind}", flush=True)
        raws[label] = synth(kind)
    if "--gen-only" in sys.argv:
        return
    meter = pyloudnorm.Meter(audio.SR)
    track, rows, t = [], [], 0.0
    for i, (label, kind, note) in enumerate(schemes):
        raw, secs = raws[label]
        r = build(raw)
        m = metrics(raw, r)
        if secs:
            m["secs_per_10s"] = round(10 * sum(a for a, _ in secs) / sum(b for _, b in secs), 1)
        if asr:
            hyp = asr_check(asr, raw)
            m["asr"] = hyp
            m["asr_errs"] = [py_errs(a, b) for a, b in zip(SENTS, hyp)]
        y = r["y"] * 10 ** ((LUFS - 3.01 - meter.integrated_loudness(r["y"])) / 20)   # 单声道复制成双声道后 +3dB
        y = true_peak_limit(y)
        a0 = t + LEAD
        t1 = a0 + len(y) / audio.SR + (BETWEEN if i < len(schemes) - 1 else TAIL)
        SEGS.append(dict(i=i, label=label, note=note, m=m, t0=t, t1=t1, a0=a0, a1=a0 + len(y) / audio.SR,
                         lines=[(a0 + a, a0 + b, s) for a, b, s in r["lines"]]))
        track.append((a0, y))
        rows.append(dict(label=label, kind=kind, total=round(r["total"], 2), **m))
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
    STATS.write_text(json.dumps(dict(rows=rows, lufs=lufs, true_peak=tp), ensure_ascii=False, indent=1))
    out = OUT / "voice_audition4.mp4"
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
    for (label, *_), (_, y) in zip(schemes, track):
        sf.write(OUT / f"audition4_{label.replace(' ', '')}.wav", y.astype(np.float32), audio.SR)
    print(out)


if __name__ == "__main__":
    main()
