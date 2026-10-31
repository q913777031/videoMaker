"""《丰田模式》系列入口：竖屏 2:3（1080×1620）白板手绘 + AI 旁白，带平台安全区。

用法：
    python3 -m fengtian.build 01 --sheet      # 关键帧 + 安全区检查图（out/fengtian/ep01/）
    python3 -m fengtian.build 01              # 渲染成片到 out/fengtian/ep01/
    python3 -m fengtian.build 01 --publish    # 渲染并交付到 videos/fengtian/01_<概念>/（接频道片尾、封面、标题与话题、横屏封面）
    加 --asr <sherpa-onnx paraformer 目录> 用语音识别核对旁白。

画幅与安全区（1080×1620）：
- 顶部 0–130 不放内容（平台搜索栏 / 状态栏），页眉在 140–262；
- 底部 1330–1620 不放内容（标题文案、话题、进度条），字幕条在 1190–1320；
- 右侧 920–1080 不放关键内容（头像、点赞、评论、分享），左侧留 48；
- 白板舞台 x 48–920、y 280–1180，中心 (484, 730)，各屏取景让人物、标签、砸字、震屏都落在舞台内。
白板、相机、角色、旁白排期都来自分镜模块（如 fengtian/ep01_andon.py）；本文件只在本进程内调整白板引擎的舞台位置，
不改动引擎对其他系列的行为。
"""

import importlib
import json
import math
import shutil
import subprocess
import sys
import tempfile
from multiprocessing import get_context
from pathlib import Path

import numpy as np
import skia
import soundfile as sf
from scipy.ndimage import minimum_filter1d, uniform_filter1d

from adler import core, fx
from adler import kit as K
from engine import audio, gfx, perc, wording
from engine.gfx import clamp01, ease_in_out, ease_out, lerp
from whiteboard import engine as wb

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out" / "fengtian"
VIDEOS = ROOT / "videos" / "fengtian"
MODS = {"01": "ep01_andon"}
W, H, FPS = 1080, 1620, 30
SAFE = dict(top=130, bottom=290, right=160, left=48)
STAGE = (48, 280, 920, 1180)                       # 白板舞台（左、上、右、下）
SCX, SCY = (STAGE[0] + STAGE[2]) / 2, (STAGE[1] + STAGE[3]) / 2
CAP_BAND = (1190, 1320)
CAP_Y, CAP_SIZE = 1252, 64
HEAD_BOTTOM = 270
PROGRESS_Y = 262
BG = "#FBFBF9"
MUSIC_DB, DUCK, SFX_DB = -12.5, 0.45, -9.0
# 原分镜的取景按 1080×970 的可视区设计；新舞台 872×900，统一缩小
VIEW_SCALE = 1.0

M = None                                          # 当前分镜模块


def load(key):
    global M
    M = importlib.import_module(f"fengtian.{MODS[key]}")
    if not getattr(M, "_scaled", False):
        M.b.views = [(cx, cy, z * VIEW_SCALE) for cx, cy, z in M.b.views]
        for j, mv in M.b.moves.items():
            M.b.moves[j] = [(k, (v[0], v[1], v[2] * VIEW_SCALE), d) for k, v, d in mv]
        M._scaled = True
    return M


# ---------------------------------------------------------------- 画面

def board_at(view, sx, sy):
    cx, cy, z = view
    return cx + (sx - SCX) / z, cy + (sy - SCY) / z


def idle_tip(T):
    """手的停放：最近画完那一笔的终点；空闲 0.4 秒后慢慢挪到画面右下角外（让出画面）。逐帧独立求值。"""
    b, ep = M.b, M.ep
    best, tip = -1.0, None
    dummy = skia.Surface(8, 8).getCanvas()
    for it in b.items:
        t1 = b.t_of(it["j"], it["k1"])
        if t1 > T or t1 < best:
            continue
        if it["kind"] == "path":
            p = wb.partial(it["path"], 0.999)[1]
        elif it["kind"] == "text":
            p = (it["x"] + K.text_w(it["s"], it["size"], it["font"]) / 2, it["y"])
        else:
            p = it["fn"](dummy, 0.999, t1 - 1e-3)
            if p is None:
                continue
        best, tip = t1, p
    j = ep.shot_at(T)
    rest = board_at(b.end_view(j), W + 60, CAP_BAND[1] + 80)
    if tip is None or best < ep.shots[j].t0:
        return rest
    m = ease_in_out(clamp01((T - best - 0.4) / 0.6))
    return lerp(tip[0], rest[0], m), lerp(tip[1], rest[1], m)


def _visible_items(T, j=None):
    """镜头到位后只画本屏所在区块（以及上一屏区块，直到镜头移动结束）。"""
    b, ep = M.b, M.ep
    if j is None:
        j = ep.shot_at(T)
        moving = j > 0 and T - ep.shots[j].t0 < 1.15
        groups = {M.GROUP[j]} | ({M.GROUP[j - 1]} if moving else set())
    else:
        groups = {M.GROUP[j]}
    return [it for it in b.items if M.GROUP[it["j"]] in groups]


def draw_board(c, T, view=None, hand=True, j=None):
    items = M.b.items
    M.b.items = _visible_items(T, j)
    c.save()
    c.translate(SCX - core.W / 2, 0)
    wb.STAGE_Y = SCY
    try:
        wb.render_board(c, M.b, T, view=view, hand_on=hand)
    finally:
        M.b.items = items
    c.restore()


def draw_header(c, s, t):
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, HEAD_BOTTOM + 8), K.paint(BG, 1.0, blur=6))
    x0 = SAFE["left"] + 8
    K.text(c, f"{core.SERIES['name']} · {core.SERIES['count']}", x0, 168, 30, "sans_medium", K.INK2, 1, "left")
    K.rr(c, x0 + 46, 220, 92, 50, 25, M.ACC)
    K.text(c, f"{M.NO:02d}", x0 + 46, 220, 32, "black", K.PAPER)
    K.text(c, M.CONCEPT, x0 + 108, 220, 34, "serif_black", K.INK, 1, "left")
    if s.tag:
        k = ease_out(clamp01((t - s.t0 + M.S) / 0.4)) if False else 1.0
        w = K.text_w(s.tag, 28, "sans_medium") + 44
        xr = W - SAFE["right"] - 20
        K.rr(c, xr - w / 2, 220, w, 50, 25, K.PAPER)
        K.rr_stroke(c, xr - w / 2, 220, w, 50, 25, M.ACC, 3)
        K.text(c, s.tag, xr - w / 2, 220, 28, "sans_medium", M.ACC)
    xa, xb = x0, W - SAFE["right"] - 20
    K.seg(c, xa, PROGRESS_Y, xb, PROGRESS_Y, K.LINE, 4)
    K.seg(c, xa, PROGRESS_Y, xa + (xb - xa) * clamp01(t / M.END_LOCAL), PROGRESS_Y, M.ACC, 4)


CAPS: list = []


def draw_caption(c, t):
    c.drawRect(skia.Rect.MakeLTRB(0, CAP_BAND[0], W, CAP_BAND[1]), K.paint("#FFFFFF", 0.86, blur=8))
    for t0, t1, cap in CAPS:
        if t0 <= t and (t1 is None or t < t1):
            break
    else:
        return
    k = clamp01((t - t0) / 0.2)
    segs = gfx.parse_marks(cap)
    total = sum(K.text_w(s, CAP_SIZE, "serif") for s, _ in segs)
    x = SCX - total / 2
    y = CAP_Y + 8 * (1 - ease_out(k))
    for s, hi in segs:
        w = K.text_w(s, CAP_SIZE, "serif")
        if hi:
            c.drawRoundRect(skia.Rect.MakeXYWH(x - 6, y + CAP_SIZE * 0.08, w + 12, CAP_SIZE * 0.38), 8, 8,
                            K.paint(K.tint(M.ACC, 0.6), 0.85 * k))
        x += K.text(c, s, x, y, CAP_SIZE, "serif", K.INK, k, "left")


def frame(c, t):
    T = M.S + t
    M.b._last_tip = idle_tip(T)
    ep = M.ep
    s = ep.shots[ep.shot_at(T)]
    g = core.G(c, ep, s, T - s.t0)
    c.drawColor(skia.Color(251, 251, 249))
    draw_board(c, T)
    for kb_, pk in s.flashes:
        a = fx.flash_alpha(g.since(kb_), pk)
        if a > 0:
            c.drawPaint(K.paint("#FFFFFF", a))
    draw_caption(c, t)
    draw_header(c, s, t)


def _surface(w=W, h=H):
    return skia.Surface.MakeRaster(skia.ImageInfo.Make(w, h, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType))


def _render(i):
    surf = _surface()
    frame(surf.getCanvas(), i / FPS)
    return surf.makeImageSnapshot().tobytes()


def still(t, path, safe=False):
    surf = _surface()
    c = surf.getCanvas()
    frame(c, t)
    if safe:
        red = K.paint("#FF0000", 0.28)
        c.drawRect(skia.Rect.MakeLTRB(0, 0, W, SAFE["top"]), red)
        c.drawRect(skia.Rect.MakeLTRB(0, H - SAFE["bottom"], W, H), red)
        c.drawRect(skia.Rect.MakeLTRB(W - SAFE["right"], SAFE["top"], W, H - SAFE["bottom"]), red)
        c.drawRect(skia.Rect.MakeLTRB(0, SAFE["top"], SAFE["left"], H - SAFE["bottom"]), red)
        c.drawRect(skia.Rect.MakeLTRB(*STAGE), K.paint("#2E8A57", 1, 3))
        K.text(c, f"t={t:.1f}s", 60, H - 240, 40, "sans_medium", "#FFFFFF")
    surf.makeImageSnapshot().save(str(path), skia.kPNG)


# ---------------------------------------------------------------- 混音

def _lufs(x):
    import pyloudnorm
    return pyloudnorm.Meter(audio.SR).integrated_loudness(x)


def limiter(x, ceil_db=-2.0, look=0.004):
    ceil = 10 ** (ceil_db / 20)
    need = np.minimum(1.0, ceil / np.maximum(np.max(np.abs(x), axis=1), 1e-9))
    w = 2 * max(3, int(look * audio.SR)) + 1
    g = uniform_filter1d(minimum_filter1d(need, w), w)
    return x * np.minimum(g, minimum_filter1d(need, 3))[:, None]


def build_audio():
    n = int(M.END_LOCAL * audio.SR)
    v = np.zeros(n)
    for st, x in zip(M.STARTS, M.CLIPS):
        audio.place(v, x, st)
    v = audio.process_voice(v)
    voice = audio.pan(v, 0) * 1.41
    m0 = int(round(M.S * audio.SR))
    full = core.music_track()                         # 原曲 + 最后一击后的混响尾音
    music = np.zeros((n, 2))
    seg = full[m0: m0 + n]
    music[: len(seg)] = seg
    fi = int(0.3 * audio.SR)
    music[:fi] *= np.linspace(0, 1, fi)[:, None]
    sfx = np.zeros((n, 2))
    events = []
    for k, s in enumerate(M.ep.shots):
        for beat, name, gain, note in s.all_hits():
            gi = s.b0 + int(round(beat))
            bt_ = core.BEATS[gi]
            name = core.resolve_sfx(name, bt_)
            clip = perc.sound(name) * core.SFX_LEVEL.get(name, 0.3) * gain
            t = bt_["t"] - M.S
            audio.place(sfx, audio.pan(clip, 0), t - perc.attack_ms(name) / 1000)
            fr = int(round(t * FPS))
            events.append(dict(shot=k + 1, kb=int(round(beat)), beat=gi, t=t, sfx=name, note=note, frame=fr,
                               frame_err=round(t * FPS - fr, 2)))
    lv = _lufs(voice)
    music *= 10 ** ((lv + MUSIC_DB - _lufs(music)) / 20)
    sfx *= 10 ** ((lv + SFX_DB - _lufs(sfx)) / 20)
    music_d = music * (1 - DUCK * audio.duck_envelope(v))[:, None]
    mix = voice + music_d + sfx
    gain = 10 ** ((-14.0 - _lufs(mix)) / 20)
    stems = {"voice": voice * gain, "music": music_d * gain, "sfx": sfx * gain}
    mix = limiter(mix * gain)
    mix = limiter(mix * 10 ** ((-14.0 - _lufs(mix)) / 20))
    return mix.astype(np.float32), stems, sorted(events, key=lambda e: e["t"])


# ---------------------------------------------------------------- 检查

def wording_warnings():
    texts = [("旁白", t) for t, _ in M.LINES] + [("字幕", c_) for _, ps in M.LINES for c_ in ps if c_]
    texts += [("白板字", it["s"]) for it in M.b.items if it["kind"] == "text"]
    texts += [("标签", s.tag) for s in M.b.shots] + [("片名", M.TITLE), ("封面", M.COVER_TITLE.replace("|", ""))]
    out = []
    for where, s in texts:
        hits = wording.check(wording.gfx_plain(s))
        if hits:
            out.append(f"{where}“{s}”：{'、'.join(hits)}")
        if where == "字幕" and core.han(s) > 10:
            out.append(f"字幕“{s}”超过 10 字")
    return out


def screen_table():
    rows = []
    for j, (k0, k1) in enumerate(M.BOUNDS):
        a = 0.0 if j == 0 else core.bt(k0) - M.S
        z = M.END_LOCAL if j == len(M.BOUNDS) - 1 else core.bt(k1) - M.S
        s = M.b.shots[j]
        ends = [M.b.t_of(it["j"], it["k1"]) - M.S for it in M.b.items if it["j"] == j]
        ends += [core.bt(s.b0 + h[0]) - M.S for h in s.hits]
        li = M.SCREENS[j][0][-1]
        ve = M.STARTS[li] + M.DUR_L[li]
        rows.append((j + 1, M.SCREENS[j][1], a, z, z - a, max(ends), ve, z - max(max(ends), ve)))
    return rows


def report(asr=None):
    for w in wording_warnings():
        print("文案警告：", w, file=sys.stderr)
    print(f"时长 {M.END_LOCAL:.2f}s，配乐 {M.S:.2f}s 起（drop 在 {core.BEATS[M.DROP]['t'] - M.S:.2f}s）")
    for (text, _), st, du in zip(M.LINES, M.STARTS, M.DUR_L):
        print(f"  旁白 {st:6.2f}–{st + du:6.2f}s {core.han(text) / du:.2f}字/秒  {text}")
    hz = sum(core.han(t) for t, _ in M.LINES)
    print(f"  全片 {hz} 字，纯语音 {sum(M.DUR_L):.1f}s（{hz / sum(M.DUR_L):.2f} 字/秒，含逗号停顿）")
    for r in screen_table():
        print(f"  屏{r[0]:2d} {r[1]:12s} {r[2]:6.2f}–{r[3]:6.2f}s 停留 {r[4]:5.2f}s 最后画面事件 {r[5]:6.2f}s "
              f"旁白止 {r[6]:6.2f}s 之后停 {r[7]:.2f}s")
    if asr:
        from fengtian.voice_audition import asr_check, edit
        res = asr_check(asr, M.RAW)
        for (t, _), a in zip(M.LINES, res):
            ref = "".join(ch for ch in t if ch not in "，。：？、")
            print(f"  ASR {a}（差 {edit(ref, a)} 字）")


# ---------------------------------------------------------------- 封面

def cover(path):
    """竖版封面 1080×1620：封面屏末尾的白板画面（无手无字幕）+ 期号 + 毛笔大标题。"""
    ep = M.ep
    j = M.COVER_SHOT
    s = ep.shots[j]
    surf = _surface()
    c = surf.getCanvas()
    c.drawColor(skia.Color(251, 251, 249))
    vx, vy, vz = M.b.end_view(j)
    c.save()
    c.translate(0, 60)
    draw_board(c, s.t1 - 0.05, view=(vx, vy, vz * 1.05), hand=False, j=j)
    c.restore()
    c.drawRect(skia.Rect.MakeLTRB(0, 1130, W, H), K.paint(BG))
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 250), K.paint(BG))
    x0 = SAFE["left"] + 24
    K.rr(c, x0 + 70, 190, 140, 70, 35, M.ACC)
    K.text(c, f"{M.NO:02d}", x0 + 70, 190, 46, "black", K.PAPER)
    K.text(c, core.SERIES["name"], x0 + 160, 190, 40, "sans_medium", K.INK2, 1, "left")
    lines = M.COVER_TITLE.split("|")
    widest = max(K.text_w(gfx.plain(ln), 104, "hand") for ln in lines)
    size = min(110.0, 110 * 840 / widest)
    for i, ln in enumerate(lines):
        y = 1260 + i * size * 1.3
        gfx.draw_rich(c, ln, SCX, y, size, "hand", wb.BLACK, wb.RED, 1.0)
    surf.makeImageSnapshot().save(str(path), skia.kPNG)
    return path


def square(path):
    """单讲横屏封面 1080×1080：上方期号与片名大字，下方装裱取景屏的白板画面（人物 + 核心示意），≤5MB。"""
    from adler.build import BRAND, _save_capped

    ep = M.ep
    j = M.SQUARE_SHOT
    s = ep.shots[j]
    stage = _surface()
    sc = stage.getCanvas()
    sc.drawColor(skia.Color(251, 251, 249))
    draw_board(sc, s.t1 - 0.05, view=M.b.end_view(j), hand=False, j=j)
    img = stage.makeImageSnapshot()
    S_ = 1080
    surf = _surface(S_, S_)
    c = surf.getCanvas()
    c.drawColor(skia.Color(243, 236, 224))
    K.rr(c, 110, 78, 104, 56, 28, M.ACC)
    K.text(c, f"{M.NO:02d}", 110, 78, 36, "black", K.PAPER)
    K.text(c, f"{BRAND} · {core.SERIES['name']}", 180, 78, 34, "sans_medium", K.INK2, 1, "left")
    lines = M.COVER_TITLE.split("|")
    widest = max(K.text_w(gfx.plain(ln), 96, "serif_black") for ln in lines)
    size = min(96.0, 96 * 960 / widest)
    for i, ln in enumerate(lines):
        gfx.draw_rich(c, ln, S_ / 2, 185 + i * size * 1.15, size, "serif_black", K.INK, M.ACC, 1.0, "center")
    top = 185 + (len(lines) - 1) * size * 1.15 + size * 0.75
    ph = S_ - top - 60
    pw = min(S_ - 110, ph * (STAGE[2] - STAGE[0]) / (STAGE[3] - STAGE[1]))
    px, py = S_ / 2, top + ph / 2 + 8
    with K.at(c, px, py, -1.2):
        K.card(c, 0, 0, pw + 26, ph + 26, "#FFFFFF", 1, r=10)
        c.save()
        c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-pw / 2, -ph / 2, pw, ph), 6, 6), doAntiAlias=True)
        sw, sh = STAGE[2] - STAGE[0], STAGE[3] - STAGE[1]
        k = max(pw / sw, ph / sh)
        c.drawImageRect(img, skia.Rect.MakeLTRB(*STAGE),
                        skia.Rect.MakeXYWH(-sw * k / 2, -sh * k / 2, sw * k, sh * k),
                        skia.SamplingOptions(skia.FilterMode.kLinear))
        c.restore()
        K.rr_stroke(c, 0, 0, pw + 10, ph + 10, 8, "#B9A27A", 3)
    lw = K.text_w(M.CONCEPT, 40, "serif_black") + 56
    with K.at(c, px + pw / 2 - lw / 2 + 10, py + ph / 2 - 6, -3):
        K.rr(c, 0, 0, lw, 70, 12, M.ACC)
        K.text(c, M.CONCEPT, 0, 0, 40, "serif_black", K.PAPER)
    path.parent.mkdir(parents=True, exist_ok=True)
    _save_capped(surf.makeImageSnapshot(), path)
    return path


# ---------------------------------------------------------------- 渲染与交付

def render(out_dir):
    global CAPS
    out_dir.mkdir(parents=True, exist_ok=True)
    CAPS = M.captions()
    mix, stems, events = build_audio()
    for e in events:
        print(f"  事件 屏{e['shot']:2d} 第{e['kb']:2d}拍 {e['t']:6.2f}s 帧{e['frame']:4d}（偏差 {e['frame_err']:+.2f}） "
              f"{e['sfx']:10s} {e['note']}")
    for k, x in stems.items():
        sf.write(out_dir / f"{k}_track.wav", x.astype(np.float32), audio.SR, subtype="PCM_16")
    hop = int(0.05 * audio.SR)
    vr = np.sqrt(np.maximum(uniform_filter1d(stems["voice"][:, 0] ** 2, hop), 0))
    on = vr > 0.1 * vr.max()
    db = lambda x, m: 10 * np.log10(np.mean(x[m] ** 2) + 1e-12)
    print(f"  人声段：人声 {db(stems['voice'], on):.1f} dB，配乐 {db(stems['music'], on):.1f} dB；无人声段配乐 "
          f"{db(stems['music'], ~on):.1f} dB；积分响度 人声 {_lufs(stems['voice']):.1f} / 配乐 {_lufs(stems['music']):.1f} / "
          f"音效 {_lufs(stems['sfx']):.1f} LUFS")
    (out_dir / "cue_sheet.json").write_text(json.dumps(events, ensure_ascii=False, indent=1))
    out = out_dir / f"{core.SERIES['prefix']}{M.NO:02d}_{M.CONCEPT}.mp4"
    n = int(round(M.END_LOCAL * FPS))
    with tempfile.TemporaryDirectory() as tmp:
        wav = str(Path(tmp) / "mix.wav")
        sf.write(wav, mix, audio.SR)
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
               "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "20",
               "-tune", "animation", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest",
               "-movflags", "+faststart", str(out)]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        with get_context("fork").Pool(4) as pool:
            for i, buf in enumerate(pool.imap(_render, range(n), chunksize=8)):
                proc.stdin.write(buf)
                if i % 600 == 0:
                    print(f"  帧 {i}/{n}", file=sys.stderr, flush=True)
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError("ffmpeg failed")
    print(out)
    return out


def publish(key, video):
    d = VIDEOS / f"{key}_{M.CONCEPT}"
    d.mkdir(parents=True, exist_ok=True)
    dst = d / video.name
    shutil.copy2(video, dst)
    cover(d / "cover.png")
    square(d / "横屏封面_1080x1080.png")
    (d / "标题与话题.txt").write_text(f"{M.ep.publish_title}\n{M.TAGS}\n")
    subprocess.run([sys.executable, "-m", "brand.append", str(dst)], check=True, cwd=ROOT)
    for p in sorted(d.iterdir()):
        print(p)


def main():
    args = sys.argv[1:]
    keys = [a for a in args if a in MODS] or list(MODS)
    asr = args[args.index("--asr") + 1] if "--asr" in args else None
    for key in keys:
        load(key)
        out_dir = OUT / f"ep{key}"
        out_dir.mkdir(parents=True, exist_ok=True)
        global CAPS
        CAPS = M.captions()
        report(asr)
        if "--sheet" in args:
            ts = [float(x) for x in args[args.index("--times") + 1].split(",")] if "--times" in args else \
                [(core.bt(k1) - M.S) - 0.3 if j < len(M.BOUNDS) - 1 else M.END_LOCAL - 0.2
                 for j, (k0, k1) in enumerate(M.BOUNDS)]
            for t in ts:
                still(t, out_dir / f"sheet_{t:05.2f}.png", safe="--safe" in args)
            cover(out_dir / "cover.png")
            square(out_dir / "square.png")
            continue
        video = render(out_dir)
        if "--publish" in args:
            publish(key, video)


if __name__ == "__main__":
    main()
