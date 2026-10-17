"""命令行入口：读取原曲 → 分析 → 校准时间轴 → 合成音效与混音 → 渲染双版本 → 媒体核验 → 交付说明。

用法：
    python3 -m rest_guilt.build --bgm path/to/bgm.m4a      # 完整成片
    python3 -m rest_guilt.build                             # 未提供原曲：只出画面预览（无音频流）与素材，状态为待配乐

原曲缺失、不可解码或短于 87 秒时不会输出带配乐的成片，也不会用其他音乐替代。
"""

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import skia

from . import draw as D
from . import mix as M
from . import music, render, sfx, story
from . import timeline as TL
from .scenes import Film
from .story import FPS

ROOT = Path(__file__).resolve().parent.parent
ACTION = {
    (1, "flip"): "时钟 23:59 翻到 00:00，传送带金光闪过", (1, "lurch"): "传送带随拍一顿",
    (2, "settle"): "人躺平、被子落定", (2, "lamp"): "伸手关灯，台灯熄灭",
    (3, "card1"): "待办卡一挂上轨道", (3, "card2"): "待办卡二挂上轨道", (3, "card3"): "待办卡三挂上轨道",
    (4, "phone"): "举起手机，放大的信息流出现", (4, "feed2"): "信息流滚动一条", (4, "feed3"): "信息流滚动一条",
    (4, "feed4"): "信息流滚动一条",
    (5, "pass1"): "别人的小人超过「我」，传送带加速", (5, "pass2"): "又一个小人超过「我」",
    (6, "pull"): "镜头开始拉远，露出空房间", (6, "empty"): "传送带金光闪过，房间里没有别人",
    (7, "roll"): "传送带卷成论文页", (7, "name1"): "作者名牌 Tonietto 落下", (7, "name2"): "作者名牌 Malkoc 落下",
    (7, "name3"): "作者名牌 Reczek 落下", (7, "name4"): "作者名牌 Norton 落下",
    (8, "cards"): "「浪费」与「休闲」两张卡弹出", (8, "ask"): "问号落下",
    (9, "covers"): "两组材料封面翻入", (9, "play"): "两块屏幕播放同一段猫咪短片",
    (10, "answer"): "框架卡遮住「浪费」一侧屏幕并变暗", (10, "glow"): "另一侧屏幕边框亮起",
    (11, "reveal"): "评价卡发光，驱动线点亮到传送带", (11, "line"): "驱动线光点流动",
    (12, "box"): "床尾长出打卡框", (12, "reach"): "伸手想勾，停在半空",
    (13, "items"): "账单与工作通知落在床头柜", (13, "tidy"): "整理成整齐一叠",
    (14, "obj1"): "选项卡：耳机", (14, "obj2"): "选项卡：热水", (14, "obj3"): "选项卡：朋友合照",
    (15, "choose"): "戴上耳机、捧起热水", (15, "drawer"): "评价卡放进抽屉",
    (16, "settle"): "打卡框退成墙上相框，传送带开始减速停下",
    (17, "return"): "回扣首帧：躺下，传送带已消失", (17, "sleep"): "闭眼，台灯熄灭",
    (18, "end"): "署名落版，音乐进入 3 秒淡出",
}


def tc(f: int) -> str:
    s = f // FPS
    return f"{s // 3600:02d}:{s // 60 % 60:02d}:{s % 60:02d}:{f % FPS:02d}"


def find_bgm(arg: str | None) -> Path | None:
    if arg:
        return Path(arg)
    for p in (ROOT / "music" / "bgm.m4a", ROOT / "bgm.m4a", ROOT / "assets" / "bgm.m4a"):
        if p.exists():
            return p
    return None


# ---------------------------------------------------------------- 文本交付物

def write_texts(out: Path, tl: TL.Timeline):
    lines = ["《你不是在休息，你是在为休息感到内疚》逐屏文案", ""]
    for s in story.SHOTS:
        a, b = tl.shot_range(s.idx)
        r0, r1 = tl.read_window(s.idx)
        lines += [f"镜头{s.idx:02d}｜{tc(a)}—{tc(b)}｜{s.bars or '至曲终'} 小节｜角标：{s.tag}",
                  "主字幕：" + "／".join(s.text),
                  f"汉字 {story.shot_han(s)} 字；稳定窗 {r0:.2f}—{r1:.2f} 秒（{r1 - r0:.2f} 秒，预算 {story.read_budget(s):.2f} 秒）",
                  f"画面：{s.action}", ""]
    lines += [f"主卡汉字合计：{sum(story.shot_han(s) for s in story.SHOTS)}", "",
              "封面主标题：" + story.COVER["title"], "封面副标题：" + story.COVER["subtitle"],
              "发布标题：" + story.PUBLISH_TITLE, "话题：" + story.HASHTAGS]
    (out / "逐屏文案.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    ref = [
        "参考资料", "",
        story.REFERENCE, "原论文：" + story.PAPER_URL, "",
        "片中使用的事实（白名单）：",
        "- 2021 年 Tonietto、Malkoc、Reczek、Norton 四位作者研究休闲信念与享受；年份为文献发表年份，不是现象首次出现的年份。",
        "- 片中研究问题：把休息（休闲）当成浪费，还能好好享受吗？——为对研究主题的通俗转述。",
        "- 片中答案：视为浪费的人，享受得更少。——对应白名单结论「将休闲描述为浪费的框架会削弱该情境下的享受」。",
        "- 作者仅写全名，未写职称与任职机构：本环境无法核验，避免写错。",
        "- 片中「休闲是浪费」「其他说法」两张材料标签为示意，不是原研究材料原文；对照组的具体内容未写出。",
        "- 实验先让参与者阅读不同框架的材料，再观看同一段休闲视频并报告享受程度。",
        "- 将休闲描述为浪费的框架，会削弱该情境下的享受。",
        "", "片中未使用：样本量、量表分数、效应大小与任何柱高或百分比。",
        "片中猫咪短片为原创轮廓动画，仅示意「同一段休闲视频」，不是原研究所用视频。",
        "反思练习为改编的反思工具，不是验证理论的正式实验；不推导「只要换想法就不疲惫」。",
        "", "核验范围：本次制作环境无法访问上述论文链接与 DOI（网络策略拒绝），",
        "依据提示词所附摘要与方法范围制作，未额外核验，未补充任何实验细节。",
    ]
    (out / "参考资料.txt").write_text("\n".join(ref) + "\n", encoding="utf-8")


def write_cues(out: Path, tl: TL.Timeline, seg_start: float | None, onsets: list | None = None):
    rows = []
    for k in range(len(story.SHOTS)):
        f = tl.bounds[k]
        hit = [o for o in (onsets or []) if round(o["t"] * FPS) == f and k > 0]
        o = max(hit, key=lambda o: o["strength"]) if hit else None
        rows.append({"视频时间码": tc(f), "帧号": f,
                     "原曲时间": f"{seg_start + (o['t'] if o else f / FPS):.3f}" if seg_start is not None else "未确认",
                     "事件类型": "镜头边界｜贴原曲起音" if o else "镜头边界",
                     "相对重音强度": f"{o['strength']:.3f}" if o else "未确认",
                     "强度口径": tl.music.get("strength_norm", "") if o else "",
                     "检测/复核方式": tl.music.get("method", "") if o else "",
                     "置信度": ("高" if o["strength"] >= 0.6 else "中") if o else "未确认",
                     "镜头号": k + 1, "视觉撞击动作": "切入新镜头", "字幕": "／".join(story.SHOTS[k].text),
                     "音效类型": "", "音效起音帧": "", "混音调整": ""})
    norm = tl.music.get("strength_norm", "")
    for e in tl.events:
        rows.append({
            "视频时间码": tc(e.frame), "帧号": e.frame,
            "原曲时间": f"{e.music_time:.3f}" if e.music_time is not None else "未确认",
            "事件类型": {"strong": "关键撞击", "soft": "柔和动作", "none": "候选（未校准）"}[e.mode] + f"｜{e.source}",
            "相对重音强度": f"{e.strength:.3f}" if e.strength is not None else "未确认",
            "强度口径": norm if e.strength is not None else "",
            "检测/复核方式": e.method, "置信度": e.confidence, "镜头号": e.shot,
            "视觉撞击动作": ACTION[(e.shot, e.name)], "字幕": "／".join(story.SHOTS[e.shot - 1].text),
            "音效类型": story.SFX_LABEL.get(e.sfx, "") if e.sfx else "无",
            "音效起音帧": (e.frame if tl.calibrated else f"未确认（基准候选 {e.frame}）") if e.sfx else "", "混音调整": e.mix_note or ("候选位置，未混音" if not tl.calibrated else ""),
        })
    rows.sort(key=lambda r: (r["帧号"], r["事件类型"] != "镜头边界"))
    with open(out / "卡点表.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def write_sfx_library(out: Path) -> dict:
    d = out / "sfx_samples"
    d.mkdir(parents=True, exist_ok=True)
    bank = sfx.bank()
    info = {}
    audition = []
    for name, x in bank.items():
        M.write24(d / f"{name}.wav", x)
        info[name] = {k: round(v, 3) for k, v in sfx.describe(x).items()}
        audition += [x, np.zeros((int(0.6 * sfx.SR), 2))]
    M.write24(d / "audition_all.wav", np.concatenate(audition))
    (d / "metrics.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    return info


# ---------------------------------------------------------------- 核验

def check_layout() -> list[str]:
    """静态版式检查：主卡字号下限、文字是否落在安全区内、角标字号。"""
    probs = []
    for L in (D.VERTICAL,):
        x0, y0, x1, y1 = L.safe
        for s in story.SHOTS:
            bx0, by0, bx1, by1, size = D.main_card_bounds(L, s.text, s.source)
            lo = L.body_min if s.source else L.text_min
            if size < lo:
                probs.append(f"{L.name} 镜头{s.idx:02d} 字号 {size:.1f}px < {lo}px")
            if bx0 < x0 or bx1 > x1 or by0 < y0 or by1 > y1:
                probs.append(f"{L.name} 镜头{s.idx:02d} 主卡越出安全区 ({bx0:.0f},{by0:.0f})-({bx1:.0f},{by1:.0f})")
    return probs


def layout_sizes() -> dict:
    return {L.name: {f"{s.idx:02d}": round(D.main_card_bounds(L, s.text, s.source)[4], 1) for s in story.SHOTS}
            for L in (D.VERTICAL,)}


def ffprobe(path: Path) -> dict:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "stream=codec_type,codec_name,width,height,r_frame_rate,pix_fmt,sample_rate,channels,nb_frames,duration"
                        ":format=duration", "-of", "json", str(path)], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def blackdetect(path: Path) -> str:
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", str(path), "-vf", "blackdetect=d=0.1:pix_th=0.02", "-an",
                        "-f", "null", "-"], capture_output=True, text=True)
    return "\n".join(l for l in r.stderr.splitlines() if "blackdetect" in l)


def extract(path: Path, frames: dict, dst: Path):
    dst.mkdir(parents=True, exist_ok=True)
    for name, f in frames.items():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-vf", f"select=eq(n\\,{f})", "-vframes", "1",
                        str(dst / f"{name}_f{f:04d}.png")], check=True)


def av_offsets(fx: np.ndarray, tl: TL.Timeline) -> list[tuple]:
    """在独立音效轨上测每个音效事件的实际起音帧（1 ms 包络对数斜率最大点），与画面事件帧比较。"""
    out = []
    m = np.abs(fx).max(axis=1)
    k = 48
    for e in tl.events:
        if not e.sfx:
            continue
        i = e.frame * M.SPF
        a, b = max(0, i - 3 * M.SPF), min(len(m), i + 3 * M.SPF)
        env = np.maximum.reduceat(m[a:b], np.arange(0, b - a, k)) + 1e-7
        d = np.diff(np.log(env))
        j = int(np.argmax(d)) + 1
        f = (a + j * k) // M.SPF
        out.append((e.shot, e.name, e.frame, f, f - e.frame))
    return out


# ---------------------------------------------------------------- 主流程

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--bgm")
    ap.add_argument("--out", default=str(ROOT / "out" / "rest_guilt"))
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--skip-video", action="store_true")
    ap.add_argument("--only", choices=["vertical"], default="vertical",
                    help="当前分镜（深夜卧室版）只为竖屏设计，横屏未适配")
    args = ap.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    report = {"已渲染": [], "已核验": [], "未完成": [], "说明": []}

    bgm = find_bgm(args.bgm)
    tl, analysis, music_x, info = None, None, None, None
    if bgm is None or not bgm.exists():
        report["未完成"].append("未找到 bgm.m4a：配乐、实际卡点表与最终混音均未完成；未使用任何替代配乐。")
    else:
        try:
            info = music.probe(str(bgm))
            music_x = music.decode(str(bgm))
            analysis = music.analyze(music_x, info)
            tl = TL.calibrate(analysis)
            (out / "music_analysis.json").write_text(json.dumps(
                {k: v for k, v in analysis.items()}, ensure_ascii=False, indent=1), encoding="utf-8")
            report["已核验"].append(f"原曲：{json.dumps(analysis['summary'], ensure_ascii=False)}")
        except music.MusicTooShort as ex:
            report["未完成"].append(f"原曲不足：{ex}。未循环、变速或换曲，成片状态为待配乐。")
        except RuntimeError as ex:
            report["未完成"].append(f"原曲无法解码：{ex}。成片状态为待配乐。")
    final = tl is not None
    if tl is None:
        tl = TL.baseline()
    report["说明"] += tl.notes
    bad = tl.check_reading()
    (report["未完成"] if bad else report["已核验"]).append(
        f"阅读窗口：" + ("；".join(bad) if bad else f"{len(story.SHOTS)} 镜稳定窗全部满足预算（max(2, 汉字/4.5)，重要句 ≥3 秒，研究段与署名 ≥4.8 秒）"))
    lay = check_layout()
    (report["未完成"] if lay else report["已核验"]).append(
        "版式（静态计算，按实际字体测宽）：" + ("；".join(lay) if lay else "竖屏主卡均在安全区内，主字与来源卡字号不低于下限") + f"；字号 {layout_sizes()}")

    tl.save(out / "timeline.json")
    write_texts(out, tl)
    write_cues(out, tl, analysis["segment"]["start"] if analysis else None)
    metrics = write_sfx_library(out)
    report["已渲染"].append(f"七类合成音效素材（48 kHz / 24 bit）：{out / 'sfx_samples'}")
    report["已核验"].append("音效客观指标（未试听）：" + json.dumps(metrics, ensure_ascii=False))
    layouts = [L for L in (D.VERTICAL, D.HORIZONTAL) if args.only in (None, L.name)]
    if args.only:
        report["说明"].append(f"按要求只生成 {args.only} 版本，另一版本未渲染。")
    for L in layouts:
        render.cover(L, str(out / f"cover_{L.name}.png"))
        report["已渲染"].append(f"封面 {L.W}×{L.H}：cover_{L.name}.png")

    audio_path = None
    if final:
        seg, tail_note = M.music_segment(music_x, analysis["segment"], len(music_x) / M.SR, tl.total_frames * M.SPF)
        report["说明"].append("曲尾处理：" + tail_note)
        res = M.build(seg, tl)
        tl.save(out / "timeline.json")
        write_cues(out, tl, analysis["segment"]["start"], analysis["onsets"])
        for k in ("bgm", "sfx", "mix"):
            M.write24(out / f"{k}.wav", res[k])
        audio_path = str(out / "mix.wav")
        report["已渲染"].append("音轨 bgm.wav / sfx.wav / mix.wav（48 kHz、24 bit、同起点同长度）")
        report["已核验"].append("混音实测：" + json.dumps(res["report"], ensure_ascii=False))
        offs = av_offsets(res["sfx"], tl)
        worst = max((abs(o[4]) for o in offs), default=0)
        (report["已核验"] if worst <= 1 else report["未完成"]).append(
            f"音画起音偏差：{len(offs)} 个音效事件，最大 {worst} 帧（明细见 av_offsets.json）")
        (out / "av_offsets.json").write_text(json.dumps(offs, ensure_ascii=False), encoding="utf-8")
        bt = [tl.downbeats[min(range(len(tl.downbeats)), key=lambda k: abs(tl.downbeats[k] - f))] for f in tl.bounds[1:-1]]
        dev = [abs(f - d) for f, d in zip(tl.bounds[1:-1], bt)]
        on = analysis["onsets"]
        cut_str = [max([o["strength"] for o in on if abs(o["t"] - f / FPS) <= 0.045] or [0]) for f in tl.bounds[1:-1]]
        (report["已核验"] if max(dev) == 0 else report["未完成"]).append(
            f"切点：{len(dev)} 个镜头切点与小节强拍帧的最大偏差 {max(dev)} 帧；"
            f"切点处原曲起音强度 {', '.join(f'{x:.2f}' for x in cut_str)}（0 表示该强拍无明显起音）")
        report["已核验"].append(f"逐拍画面动作：{len(tl.beats)} 拍（传送带步进 / 时钟冒号 / 主卡金色节点），"
                               f"{len(tl.downbeats)} 个小节强拍（舞台轻推）")
        report["未完成"].append("未经人工试听（含手机 / 小扬声器条件）；卡点与混音仅有信号分析依据。")

    if not args.skip_video:
        for L in layouts:
            name = f"rest_guilt_{L.name}.mp4" if final else f"preview_{L.name}_noaudio.mp4"
            p = out / name
            render.render(Film(L, tl), str(p), audio_path, args.workers)
            pr = ffprobe(p)
            report["已渲染"].append(f"{name}")
            report["已核验"].append(f"ffprobe {name}：{json.dumps(pr, ensure_ascii=False)}")
            bd = blackdetect(p)
            report["已核验" if not bd else "说明"].append(f"黑帧检测 {name}：{bd or '无 ≥0.1 秒黑段'}")
            b = tl.bounds
            frames = {"first": 0, "research_authors": b[7] - 20, "research_answer": b[10] - 20,
                      "reflection": b[15] - 20, "ending": b[17] - 20,
                      "last": tl.total_frames - 1}
            extract(p, frames, out / "checks" / L.name)
            report["已核验"].append(f"抽帧（实际解码）：checks/{L.name}/ " + ", ".join(f"{k}@{v}" for k, v in frames.items()))
        if not final:
            report["未完成"].append("当前 MP4 仅为画面预览（无音频流，时间轴为 90.00 秒叙事基准），不是成片。")

    status = "已完成（待人工试听确认）" if final else "待配乐"
    md = [f"# 交付说明 — 状态：{status}", ""]
    for k in ("已渲染", "已核验", "未完成", "说明"):
        if report[k]:
            md += [f"## {k}", ""] + [f"- {x}" for x in report[k]] + [""]
    (out / "交付说明.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))
    return 0 if final else 2


if __name__ == "__main__":
    sys.exit(main())
