"""文案用语检查：发布的视频（字幕、画面文字、标题、封面字、合集简介）排除常见 AI 腔句式与套话。

规则写在 CLAUDE.md「文案用语（强制）」；adler.core.read_check 与 adler.build.publish 会调用 check()，
命中即在 --sheet / --publish 输出警告，警告必须清零。
"""

import re

# 句式（正则）
PATTERNS = [
    (r"不是[^。！？\n]{0,14}?[，,、]?\s*(而)?是", "不是……（而）是……"),
    (r"不只是|不仅仅是|不仅是[^。！？\n]{0,14}更是", "不只是／不仅……更是……"),
    (r"与其说[^。！？\n]{0,14}不如说", "与其说……不如说……"),
    (r"首先[^。！？\n]*其次", "首先……其次……"),
    (r"你(有没有|是否)(想过|发现)", "你有没有想过／发现"),
    (r"(很多|大多数|\d+%的)人(都)?不知道", "很多人不知道"),
    (r"让我们", "让我们……"),
]

# 套话词表
WORDS = [
    "本质上", "本质", "底层逻辑", "赋能", "闭环", "维度", "抓手", "颗粒度", "说白了", "真相是", "其实", "值得注意的是",
    "换句话说", "深度", "全方位", "一起来看看", "揭秘", "干货", "宝藏", "炸裂", "不得不说", "毫无疑问", "归根结底",
    "由此可见", "总而言之", "综上所述", "颠覆认知", "认知升级", "秒懂", "一文读懂", "一张图看懂", "重塑", "解锁", "助力",
    "打造", "聚焦", "破局", "进阶", "无疑", "至关重要", "不可或缺", "深刻", "关键在于", "核心在于", "毋庸置疑",
]


def check(text: str) -> list[str]:
    """返回命中的句式或套话（去重，按出现顺序）。"""
    if not text:
        return []
    hits = []
    for pat, name in PATTERNS:
        if re.search(pat, text):
            hits.append(name)
    for w in WORDS:
        if w in text and not any(w in h for h in hits):
            hits.append(w)
    return hits


def episode_texts(ep) -> list[tuple[str, str]]:
    """一讲里所有会上屏或发布的文字：(位置, 文字)。"""
    out = [("片名", ep.title), ("封面字", ep.cover_title.replace("|", "")), ("封面副题", ep.cover_sub or "")]
    for i, s in enumerate(ep.shots):
        out.append((f"镜头{i + 1}字幕", s.text))
        for el in s.els:
            p = el.props
            if "text" in p and isinstance(p["text"], str):
                out.append((f"镜头{i + 1}画面字", p["text"]))
            if "lines" in p:
                out.append((f"镜头{i + 1}卡片", "".join(p["lines"])))
            if "words" in p:
                out.append((f"镜头{i + 1}弹字", "".join(w for w, _ in p["words"])))
    board = getattr(ep, "board", None)
    if board is not None:
        for it in board.items:
            if it["kind"] == "text":
                out.append((f"镜头{it['j'] + 1}白板字", it["s"]))
    return [(k, gfx_plain(v)) for k, v in out if v]


def gfx_plain(s: str) -> str:
    return s.replace("【", "").replace("】", "")


def episode_warnings(ep) -> list[str]:
    warns = []
    for where, text in episode_texts(ep):
        hits = check(text)
        if hits:
            warns.append(f"{where}“{text}”含 AI 腔用语：{'、'.join(hits)}")
    return warns
