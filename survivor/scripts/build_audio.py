"""幸存者偏差短视频：旁白合成 → 按真实时长排时间轴 → 配乐与音效 → 混音。

输出（均由同一份时间轴推出，画面与声音不会各算各的）：
  src/generated/timeline.json   Remotion 读取的时间轴（秒）
  public/mix.wav                成片音轨（人声 + 配乐 + 音效）
  deliverables/subtitles.srt    SRT 字幕
  deliverables/narration.md     旁白稿与分镜时间轴

用法：python3 scripts/build_audio.py            # 离线 TTS 配音
      python3 scripts/build_audio.py --no-voice # 不配音：按估算时长排时间轴，成片标注“未配音”
"""

import json
import math
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE.parent))

from engine import audio as A  # noqa: E402
from engine.audio import SR, place, pan, hz, reverb  # noqa: E402

NARRATOR = "zv_001"   # 旁白：ZipVoice，音色提示来自 Kokoro zf_001（合成音色，非真人）
CHAMPION = "zv_009"   # 冠军：ZipVoice，音色提示来自 Kokoro zm_009

# 台词：(id, 说话人, 配音文本, 字幕文本【重点】, 语速, 句后停顿秒)
LINES = [
    ("hook1", "n", "连续猜中十次硬币的人，教你成功秘诀。", "连续猜中【10次】硬币的人，教你成功秘诀。", 1.08, 0.12),
    ("hook2", "n", "你学不学？", "【你学不学？】", 1.0, 0.0),
    ("setup1", "n", "让一千零二十四个人猜硬币，", "让【1024】个人猜硬币，", 1.05, 0.12),
    ("setup2", "n", "猜错退出，猜对继续。", "猜错【退出】，猜对【继续】。", 1.0, 0.0),
    ("round1", "n", "为了看清过程，我们按每轮一半晋级来演示。", "为了看清过程，我们按【每轮一半晋级】来演示。", 1.05, 0.0),
    ("round2", "n", "十轮以后，剩下一位十连胜冠军。", "十轮以后，剩下一位【十连胜冠军】。", 1.0, 0.0),
    ("guru1", "c", "我的秘诀？", "我的秘诀？", 0.95, 0.3),
    ("guru2", "c", "相信自己，", "【相信自己】，", 0.95, 0.3),
    ("guru3", "c", "坚持判断，", "【坚持判断】，", 0.95, 0.35),
    ("guru4", "c", "还有，", "还有——", 0.9, 0.35),
    ("guru5", "c", "保持手感。", "【保持手感】。", 0.9, 0.0),
    ("freeze1", "n", "听起来有道理？", "听起来有道理？", 1.0, 0.4),
    ("freeze2", "n", "等等，其他人去哪了？", "等等，【其他人】去哪了？", 0.95, 0.0),
    ("reveal1", "n", "镜头外，还有一千零二十三个人。", "镜头外，还有【1023】个人。", 1.0, 0.4),
    ("reveal2", "n", "刚才，我们只盯着赢家，", "刚才，我们只盯着【赢家】，", 1.0, 0.1),
    ("reveal3", "n", "却没问输家是不是也相信自己、坚持判断。", "却没问【输家】是不是也相信自己、坚持判断。", 1.0, 0.0),
    ("name1", "n", "这叫幸存者偏差。", "这叫【幸存者偏差】。", 0.95, 0.3),
    ("name2", "n", "只看留下来的样本，就可能误判全貌。", "只看【留下来】的样本，就可能误判全貌。", 1.0, 0.35),
    ("name3", "n", "学习经验分享，也要问问没成功的人。", "学习经验分享，也要问问【没成功的人】。", 1.0, 0.0),
    ("outro1", "n", "经验可以参考，", "经验【可以参考】，", 1.0, 0.15),
    ("outro2", "n", "但别只问赢家做了什么。", "但别只问赢家做了什么。", 1.0, 0.3),
    ("outro3", "n", "还要问：", "还要问：", 1.0, 0.2),
    ("outro4", "n", "做了同样的事，却没成功的人呢？", "做了同样的事，【却没成功的人呢？】", 0.92, 0.0),
]

ROUND_SLOW = [2.4, 2.1]      # 前两轮慢放，让观众看懂规则
ROUND_FAST = 0.85            # 第 3—10 轮加速
TAIL_HOLD = 2.8              # 最后一句大字在旁白结束后至少保留的秒数


def estimate(text: str, speed: float) -> float:
    """无 TTS 时的时长估算：每秒约 4.6 个汉字。"""
    n = sum(1 for ch in text if "一" <= ch <= "鿿")
    return n / 4.6 / speed + 0.2


def synth(voiced: bool) -> dict[str, np.ndarray | float]:
    """逐句合成；返回 id → 音频（配音）或 id → 时长（未配音）。"""
    if not voiced:
        return {lid: estimate(text, sp) for lid, _, text, _, sp, _ in LINES}
    voices = {"n": A.Narrator(NARRATOR), "c": A.Narrator(CHAMPION)}
    out = {}
    for lid, who, text, _, sp, _ in LINES:
        out[lid] = A.process_voice(voices[who].generate(text.replace("？", "?"), sp))
    return out


def dur_of(x) -> float:
    return len(x) / SR if isinstance(x, np.ndarray) else float(x)


def build_timeline(clips: dict) -> dict:
    """由真实旁白时长排出全部场景、台词与事件时刻（秒）。"""
    by_id = {l[0]: l for l in LINES}
    t_line: dict[str, tuple[float, float]] = {}

    def say(lid: str, start: float) -> float:
        d = dur_of(clips[lid])
        t_line[lid] = (start, start + d)
        return start + d + by_id[lid][5]

    ev: dict = {}
    scenes: dict = {}

    # 0 开场：先展示赢家
    t = say("hook1", 0.35)
    ev["stamp"] = 0.45
    t = say("hook2", t)
    hook_end = t + 0.45
    scenes["hook"] = [0.0, hook_end]

    # 1 启动游戏：32×32 阵列
    t = say("setup1", hook_end + 0.5)
    ev["rules"] = t
    t = say("setup2", t)
    setup_end = max(t + 0.5, hook_end + 4.6)
    scenes["setup"] = [hook_end, setup_end]

    # 2 连续筛选：10 轮
    rounds = []
    rt = setup_end + 0.1
    for r in range(10):
        d = ROUND_SLOW[r] if r < 2 else ROUND_FAST
        rounds.append([rt, d])
        rt += d
    rounds_end = rt
    say("round1", setup_end + 0.25)
    r2_start = max(t_line["round1"][1] + 0.4, rounds_end - 0.9)
    t = say("round2", r2_start)
    rounds_scene_end = max(t + 0.35, rounds_end + 0.6)
    scenes["rounds"] = [setup_end, rounds_scene_end]
    ev["rounds"] = rounds

    # 3 冠军开课
    g0 = rounds_scene_end
    ev["podium"] = g0 + 0.25
    ev["crown"] = g0 + 0.9           # 皇冠开始下落
    ev["crownLand"] = g0 + 1.3
    t = say("guru1", g0 + 1.6)
    ev["secrets"] = []
    for lid in ("guru2", "guru3"):
        ev["secrets"].append(t)
        t = say(lid, t)
    t = say("guru4", t)
    ev["secrets"].append(t)
    t = say("guru5", t)
    ev["absurd"] = t - 0.05
    guru_end = t + 0.9
    scenes["guru"] = [g0, guru_end]

    # 4 暂停与提问
    ev["freeze"] = guru_end
    ev["viewfinder"] = guru_end + 0.35
    t = say("freeze1", guru_end + 0.7)
    t = say("freeze2", t)
    freeze_end = t + 0.6               # 约半秒思考停顿
    scenes["freeze"] = [guru_end, freeze_end]

    # 5 主反转：镜头拉远
    r0 = freeze_end
    ev["zoom1"] = [r0, r0 + 2.4]
    t = say("reveal1", r0 + 0.5)
    ev["zoom2"] = [r0 + 2.7, max(r0 + 5.6, t + 0.6)]
    ev["caption"] = t
    t = say("reveal2", t)
    ev["bubbles"] = t
    t = say("reveal3", t)
    reveal_end = t + 0.7
    scenes["reveal"] = [r0, reveal_end]

    # 6 命名与现实迁移
    n0 = reveal_end
    ev["phone"] = n0
    t = say("name1", n0 + 0.5)
    ev["term"] = t_line["name1"][0]
    t = say("name2", t)
    ev["others"] = t
    t = say("name3", t)
    name_end = t + 0.5
    scenes["name"] = [n0, name_end]

    # 7 带走一句话
    o0 = name_end
    t = say("outro1", o0 + 0.3)
    ev["reference"] = t_line["outro1"][0]
    t = say("outro2", t)
    ev["compare"] = t_line["outro2"][0]
    t = say("outro3", t)
    ev["final"] = t
    t = say("outro4", t)
    end = t + TAIL_HOLD
    scenes["outro"] = [o0, end]

    lines = [{"id": lid, "speaker": who, "text": text, "sub": sub,
              "start": round(t_line[lid][0], 3), "end": round(t_line[lid][1], 3)}
             for lid, who, text, sub, _, _ in LINES]
    return {"duration": round(end, 3), "scenes": scenes, "lines": lines, "events": ev}


# ---------------------------------------------------------------- 音效（全部代码合成）

def _t(d):
    return np.arange(int(d * SR)) / SR


def coin_flip(seed: int = 0) -> np.ndarray:
    """弹指 + 金属旋转嗡鸣。"""
    t = _t(0.55)
    flick = A.highpass(A._noise(int(0.01 * SR), 40 + seed), 2500) * np.exp(-np.arange(int(0.01 * SR)) / 60)
    ring = sum(a * np.sin(2 * np.pi * f * t) for f, a in ((2793, 0.5), (4186, 0.3), (5588, 0.15)))
    wob = 0.5 + 0.5 * np.sin(2 * np.pi * (14 + 10 * t) * t)
    y = ring * wob * np.exp(-t * 6) * 0.35
    y[: len(flick)] += flick
    return A._fade(y, 0.001, 0.05)


def coin_land() -> np.ndarray:
    t = _t(0.7)
    y = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, a, d in ((2093, 0.6, 7), (3136, 0.35, 9), (5274, 0.2, 14)))
    return A._fade(y * 0.6, 0.001, 0.08)


def exit_sound() -> np.ndarray:
    """退出：柔和下滑的“噗”。"""
    t = _t(0.35)
    f = 420 * (0.45 ** (t / 0.35))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    return A._fade(A.lowpass(y, 1800) * 0.55)


def crown_drop() -> np.ndarray:
    y = np.zeros(int(1.6 * SR))
    place(y, A._whoosh(0.4, 5, False) * 0.4, 0.0)
    place(y, coin_land() * 0.9, 0.4)
    place(y, A._shimmer() * 0.5, 0.42)
    return y


def slide_whistle() -> np.ndarray:
    """荒诞音效：滑哨上滑再落下。"""
    t = _t(0.9)
    f = np.where(t < 0.35, 600 + 900 * (t / 0.35) ** 0.7, 1500 - 1100 * np.clip((t - 0.35) / 0.55, 0, None) ** 1.4)
    f = f * (1 + 0.025 * np.sin(2 * np.pi * 7 * t))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.1 * A.bandpass(A._noise(len(t), 77), 1200, 3000)
    env = np.minimum(1, t / 0.03) * np.where(t > 0.75, np.maximum(0, 1 - (t - 0.75) / 0.15), 1)
    return A._fade(y * env * 0.35)


def tape_stop() -> np.ndarray:
    """暂停：唱片急停。"""
    t = _t(0.5)
    f = 220 * (0.08 ** (t / 0.5))
    y = np.tanh(2 * np.sin(2 * np.pi * np.cumsum(f) / SR))
    y += 0.3 * A.bandpass(A._noise(len(t), 88), 300, 2400) * np.exp(-t * 8)
    return A._fade(A.lowpass(y, 2400) * np.exp(-t * 2) * 0.5, 0.001, 0.08)


def stamp() -> np.ndarray:
    t = _t(0.5)
    thud = np.sin(2 * np.pi * np.cumsum(70 + 90 * np.exp(-t * 40)) / SR) * np.exp(-t * 12)
    slap = A.bandpass(A._noise(len(t), 91), 400, 3000) * np.exp(-t * 35) * 0.6
    return A._fade(np.tanh(1.6 * (thud + slap)) * 0.7, 0.0, 0.05)


def build_sfx(tl: dict, total: float) -> np.ndarray:
    ev = tl["events"]
    tr = np.zeros(int(total * SR) + SR)
    place(tr, stamp(), ev["stamp"] + 0.12, 0.9)
    place(tr, A.sfx("swoosh"), tl["scenes"]["hook"][1] - 0.3, 0.5)
    place(tr, A.sfx("pop2"), ev["rules"], 0.35)
    for r, (st, d) in enumerate(ev["rounds"]):
        g = 0.85 if r < 2 else 0.55
        place(tr, coin_flip(r), st + 0.12 * d, g)
        place(tr, coin_land(), st + 0.45 * d, g * 0.8)
        place(tr, exit_sound(), st + 0.5 * d, g * (0.9 if r < 2 else 0.6))
    place(tr, A.sfx("whoosh"), tl["scenes"]["guru"][0], 0.35)
    place(tr, crown_drop(), ev["crown"], 0.8)
    for s in ev["secrets"]:
        place(tr, A.sfx("pop"), s, 0.45)
    place(tr, slide_whistle(), ev["absurd"] + 0.1, 0.75)
    place(tr, tape_stop(), ev["freeze"], 0.9)
    place(tr, A.sfx("pop2"), ev["viewfinder"], 0.3)
    z1, z2 = ev["zoom1"], ev["zoom2"]
    place(tr, A._whoosh(z1[1] - z1[0], 21, False) * 0.6, z1[0])
    place(tr, A._whoosh(z2[1] - z2[0], 22, False) * 0.6, z2[0])
    for k in range(5):
        place(tr, A.sfx("pop"), ev["bubbles"] + 0.25 + k * 0.32, 0.25)
    place(tr, A.sfx("swoosh"), ev["phone"], 0.4)
    place(tr, A.sfx("ding"), ev["term"], 0.35)
    place(tr, A.sfx("swoosh"), ev["others"], 0.35)
    place(tr, A.sfx("ding"), ev["final"], 0.3)
    return pan(tr[: int(total * SR)], 0) * 1.41


# ---------------------------------------------------------------- 配乐：轻快 + 略带悬疑

BPM = 112
BEAT = 60 / BPM
SNEAK = [(38, (62, 65, 69)), (38, (62, 65, 70)), (34, (62, 65, 70)), (33, (61, 64, 69))]   # Dm  Dm(b6)  Bb  A
BRIGHT = [(41, (65, 69, 72)), (36, (64, 67, 72)), (38, (62, 65, 69)), (34, (62, 65, 70))]  # F C Dm Bb


def _groove(dur: float, chords, drums: bool, pluck_vel: float = 0.2, seed: int = 0) -> np.ndarray:
    """拨弦琶音 + 断奏贝斯 + 轻打击：俏皮、带点鬼祟感。"""
    bar = BEAT * 4
    n = int((dur + 2) * SR)
    pl = np.zeros((n, 2))
    bass, perc = np.zeros(n), np.zeros((n, 2))
    pad_t = np.zeros(n)
    pattern = (0, 2, 1, 2, 0, 2, 1, 3)
    for b in range(int(math.ceil(dur / bar))):
        root, ch = chords[b % len(chords)]
        t0 = b * bar
        place(pad_t, A._pad([m - 12 for m in ch], bar, 900, 0.09), t0)
        for k in range(8):
            notes = (*ch, ch[0] + 12)
            m = notes[pattern[k]]
            place(pl, pan(A._pluck(hz(m), 0.35, pluck_vel), -0.3 if k % 2 else 0.3), t0 + k * BEAT / 2)
            if k in (0, 3, 4, 6):
                place(bass, A._bass(hz(root), BEAT * 0.4, 0.45), t0 + k * BEAT / 2)
        if drums:
            for k in range(4):
                if k in (0, 2):
                    place(perc, pan(A._kick() * 0.55, 0), t0 + k * BEAT)
                for h in range(2):
                    place(perc, pan(A._hat() * (0.9 if h else 0.5), 0.25), t0 + k * BEAT + h * BEAT / 2)
    return pl + reverb(pl[:, 0] + pl[:, 1], 0.3, 1.6) * 0.2 + pan(bass, 0) * 0.6 + reverb(pad_t, 0.3, 2.0) + perc


def _drone(dur: float) -> np.ndarray:
    """反转段：低音铺底 + 稀疏高音，留出空间给旁白。"""
    n = int((dur + 2) * SR)
    y = np.zeros(n)
    place(y, A._pad([38, 45, 50], dur + 0.5, 600, 0.16), 0)
    hi = np.zeros(n)
    for k, m in enumerate((74, 77, 76, 72, 74)):
        place(hi, A._piano(hz(m), 1.0, 0.12), 1.2 + k * 1.9)
    return reverb(y, 0.35, 2.4) + reverb(hi, 0.5, 2.8)


def _section(music, seg, start, end, fin=0.05, fout=0.4):
    dur = end - start
    seg = seg[: int((dur + fout) * SR)].copy()
    a, b = int(fin * SR), int(fout * SR)
    if a:
        seg[:a] *= np.linspace(0, 1, a)[:, None]
    if b and len(seg) > b:
        seg[-b:] *= np.linspace(1, 0, b)[:, None]
    i = int(start * SR)
    music[i: i + len(seg)] += seg[: len(music) - i]


def build_music(tl: dict, total: float) -> np.ndarray:
    sc, ev = tl["scenes"], tl["events"]
    m = np.zeros((int(total * SR) + SR, 2))
    _section(m, _groove(sc["hook"][1], SNEAK, False, 0.16), 0.0, sc["hook"][1] + 0.1, 0.3, 0.3)
    _section(m, _groove(sc["rounds"][1] - sc["setup"][0], SNEAK, True, 0.2), sc["setup"][0], sc["rounds"][1] + 0.2, 0.05, 0.3)
    _section(m, _groove(ev["freeze"] - sc["guru"][0], BRIGHT, True, 0.22), sc["guru"][0], ev["freeze"] + 0.03, 0.05, 0.03)
    # 暂停：音乐主动收住，留白到反转开始
    _section(m, _drone(sc["reveal"][1] - sc["reveal"][0]), sc["reveal"][0], sc["reveal"][1] + 0.3, 1.0, 0.6)
    _section(m, _groove(sc["outro"][1] - sc["name"][0], BRIGHT, False, 0.15), sc["name"][0], sc["outro"][1], 0.8, 2.5)
    m = m[: int(total * SR)]
    return m / (np.max(np.abs(m)) + 1e-9) * 0.5


# ---------------------------------------------------------------- 输出

def fmt_srt(t: float) -> str:
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def write_docs(tl: dict, voiced: bool):
    out = HERE / "deliverables"
    out.mkdir(exist_ok=True)
    srt = []
    for i, l in enumerate(tl["lines"], 1):
        text = l["sub"].replace("【", "").replace("】", "")
        srt.append(f"{i}\n{fmt_srt(l['start'])} --> {fmt_srt(l['end'] + 0.15)}\n{text}\n")
    (out / "subtitles.srt").write_text("\n".join(srt), encoding="utf-8")

    names = {"hook": "先展示赢家", "setup": "启动游戏", "rounds": "连续筛选", "guru": "冠军开课",
             "freeze": "暂停与提问", "reveal": "主反转：镜头拉远", "name": "命名与现实迁移", "outro": "带走一句话"}
    md = ["# 旁白稿与分镜时间轴", "",
          f"总时长 {tl['duration']:.2f} 秒（{'离线 TTS 配音' if voiced else '未配音，时长为估算'}）。时间均由 `scripts/build_audio.py` 按真实配音时长生成。", ""]
    for key, (s, e) in tl["scenes"].items():
        md.append(f"## {s:5.2f}–{e:5.2f}s　{names[key]}")
        md.append("")
        for l in tl["lines"]:
            if s <= l["start"] < e:
                who = "冠军" if l["speaker"] == "c" else "旁白"
                md.append(f"- `{l['start']:5.2f}–{l['end']:5.2f}` {who}：{l['text']}")
        md.append("")
    (out / "narration.md").write_text("\n".join(md), encoding="utf-8")


def main():
    voiced = "--no-voice" not in sys.argv
    clips = synth(voiced)
    tl = build_timeline(clips)
    tl["voiced"] = voiced
    total = tl["duration"]

    voice = np.zeros(int(total * SR) + SR)
    if voiced:
        for l in tl["lines"]:
            place(voice, clips[l["id"]], l["start"])
    voice = voice[: int(total * SR)]
    music = build_music(tl, total)
    fx = build_sfx(tl, total)
    if voiced:
        mix = A.master(voice, music, fx)
    else:
        mix = (music * 0.8 + fx * 0.5).astype(np.float32)
    pub = HERE / "public"
    pub.mkdir(exist_ok=True)
    sf.write(pub / "mix.wav", mix, SR, subtype="PCM_16")

    gen = HERE / "src" / "generated"
    gen.mkdir(parents=True, exist_ok=True)
    (gen / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")
    write_docs(tl, voiced)
    print(f"duration {total:.2f}s, voiced={voiced}")


if __name__ == "__main__":
    main()
