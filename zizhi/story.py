"""《资治通鉴》各讲的通用 42 镜构造器：每讲写成 41 个“节拍”（每个 1 小节）+ 片尾，节拍类型见 BEATS。

段落与第 1 讲一致：钩子 1–8 → 原文 drop 9 → 释义 10–11 → 书中故事 12–28 → 原文点评 29–30 →
当下现象 31–36 → 落到自己 37 → 4 招小建议 38–41 → 互动片尾 42。
每个节拍至少在 2 个实测拍点上有画面事件，字幕 ≤8 字（引擎 read_check 校验）。
"""

from adler import kit as K
from adler.core import Big, Bubble, Card, Counter, Custom, Fig, Icon, Label, Rays, Spark
from sapiens.art import crowd
from scarcity.art import checklist, phone_chat

from . import art as A
from .common import S, episode, outro, pops

G = A.GROUND_Y
THINGS = {"moneybag", "car", "chest"}


def beat(kind, cap="", **p):
    return (kind, cap, p)


def _obj(name, x, y, s, at, color=None, sfx="pop", enter="pop"):
    """kit 图标或 zizhi.art.thing 物件。"""
    if name in THINGS:
        return Custom(A.thing, x=x, y=y, at=at, enter=enter, obj=name, s=s * 1.3, sfx=sfx)
    return Icon(name, x, y, s, color=color or A.CINNABAR, at=at, enter=enter, sfx=sfx)


def _bubble(text, x, y, at, sfx="rim"):
    n = len(text.replace("【", "").replace("】", ""))
    if n > 9 and "，" in text:
        text = text.replace("，", "，|", 1)
        n = max(len(s) for s in text.split("|"))
    size = 46 if n <= 7 else 40 if n <= 9 else 34
    return Bubble(text, x, y, size, at=at, enter="pop", sfx=sfx)


def _who(sp, name):
    st = sp["who"].get(name, {})
    return dict(color=st.get("color", K.OTHER), hair=st.get("hair", "short"))


def _name(name, x, at=0):
    return Label(name, x, G - 395, 32, at=at, fill=A.INKWASH, idle=False)


def make(kind, cap, p, sp, tag):
    acc = sp["acc"]
    tag = p.get("tag", tag)
    if kind == "q3":
        xs = (270, 540, 810)
        return S(cap, tag, [_obj(n, xs[i], 740, 190, i, c) for i, (n, c) in enumerate(p["items"])], punch=0.025,
                 flashes=[0])
    if kind == "ask":
        return S(cap, tag, [Custom(crowd, x=540, y=G, at=0, enter="fade", n=6, s=250, spread=820),
                            Custom(A.magnifier, x=540, y=640, at=0, enter="pop", r=130, blur_at=2, sfx="wood_high"),
                            Icon("question", 760, 470, 100, color=K.RED, at=2, sfx="rim")])
    if kind == "objs":
        (a, ca), (b, cb) = p["items"]
        return S(cap, tag, [_obj(a, 300, 760, 220, 0, ca), _obj(b, 790, 760, 220, 2, cb), Spark(790, 760, at=2)])
    if kind == "obj":
        return S(cap, tag, [_obj(p["name"], 540, 760, 260, 0, p.get("color"), sfx="kick"), Spark(540, 720, at=0),
                            Icon("question", 760, 520, 90, color=K.RED, at=2, sfx="rim")], shake=[0])
    if kind == "nope":
        xs = (230, 540, 850)
        els = [_obj(n, xs[i], 760, 170, 0, c, sfx=None, enter="none") for i, (n, c) in enumerate(p["items"])]
        els += [Icon("cross", xs[i], 760, 150, color=K.RED, at=i + 1, sfx="rim") for i in range(3)]
        return S("全都不是", tag, els)
    if kind == "answer":
        return pops(p["words"], tag, size=p.get("size", 150), flash=1, extra=[Rays(540, 780, 620, at=1, alpha=0.2)])
    if kind == "chest":
        return S("看到最后", "先留个钩子", [
            Custom(A.thing, x=540, y=820, at=0, enter="pop", obj="chest", s=360, label=p["label"], sfx="wood_low"),
            Icon("key", 820, 520, 120, color=K.GOLD, at=2, sfx="ding"), Spark(820, 520, at=2)])
    if kind == "book":
        return S(cap or "资治通鉴一句话", "资治通鉴", [
            Icon("book", 540, 470, 150, color=acc, at=0, sfx="wood_low"),
            Custom(A.bamboo, x=540, y=860, at=0, enter="none", text="资治通鉴", n=8, h=430, w=64, b0=1, step=0.5)],
                 hits=[(1, "wood_high", 0.8, "竹简展开"), (2, "shaker", 0.7, "写字")])
    if kind == "drop":
        q = p["quote"]
        size = min(130.0, 880 / max(1, len(q)))
        return S("", "原文", [Big(q, 540, 720, size, at=0, sfx="kick", sub=p["src"], sub_size=38, rays=True, glow=True,
                                 shine=True, spark=True, note="drop：原文落版"), Spark(540, 720, at=2, sfx="ding")],
                 punch=0.035, flashes=[0], shake=[0])
    if kind == "icons":
        items = p["items"]
        n = len(items)
        xs = {1: (540,), 2: (310, 770), 3: (220, 540, 860)}[n]
        sz = {1: 260, 2: 210, 3: 170}[n]
        els = []
        for i, it in enumerate(items):
            name, col, lab = it
            els.append(_obj(name, xs[i], 740, sz, i, col))
            if lab:
                els.append(Label(lab, xs[i], 740 + sz * 0.75 + 30, 38 if n < 3 else 32, at=i, fill=col or acc, idle=False))
        if n == 1:
            els.append(Spark(540, 740, at=2, sfx="ding"))
        return S(cap, tag, els)
    if kind == "row":
        return S(cap, tag, [Custom(A.icon_row, x=540, y=760, at=0, enter="none", icon=p.get("icon", "house"),
                                   n=p.get("n", 10), color=acc)],
                 hits=[(i, "pop", 0.8, "计数") for i in range(4)])
    if kind == "crack":
        return S(cap, tag, [Custom(A.crack_char, x=540, y=740, at=0, enter="pop", text=p["text"], s=380, split=2,
                                   sfx="wood_low")], hits=[(2, "rim", 1.0, "裂开")], shake=[2])
    if kind == "map":
        labels = p.get("labels", [])
        pos = [(-120, -60), (130, -100), (-70, 110), (160, 90)]
        return S(cap, tag, [Custom(A.scroll_map, x=540, y=780, at=0, enter="fade", b0=0, b1=1, step=0.5, title=p["title"],
                                   labels=[(lab, *pos[i]) for i, lab in enumerate(labels)])],
                 hits=[(0, "wood_low", 0.8, "卷轴"), (1, "pop", 0.8, "标注"), (2, "wood_high", 0.6, "标注")])
    if kind == "fig":
        w = p["who"]
        els = [Fig(540, G, 340, at=0, pose=p.get("pose", "proud"), mood=p.get("mood", "calm"), **_who(sp, w)),
               _name(w, 540)]
        for i, lab in enumerate(p.get("labels", [])[:2]):
            els.append(Label(lab, (280, 800)[i], 560, 40, at=i + 1, sfx="pop", fill=(acc, K.GOLD)[i]))
        els.append(Spark(540, 600, at=3, sfx="ding"))
        return S(cap, tag, els, draw=A.ground)
    if kind == "say":
        w = p["who"]
        x = p.get("x", 360)
        f = Fig(x, G, 330, at=0, pose=p.get("pose", "point"), mood=p.get("mood", "calm"), **_who(sp, w),
                moves=[(1, dict(pose=p["pose1"], mood=p.get("mood1", p.get("mood", "calm")), dur=0.25))]
                if p.get("pose1") else [])
        bx = 740 if x < 540 else 340
        return S(cap, tag, [f, _name(w, x), _bubble(p["text"], bx, 560, 1), Spark(bx, 560, at=1)], draw=A.ground)
    if kind == "talk":
        (a, ta), (b, tb) = p["a"], p["b"]
        return S(cap, tag, [Fig(300, G, 320, at=0, pose="point", mood="calm", **_who(sp, a)), _name(a, 300),
                            Fig(780, G, 320, at=0, pose="stand", mood="calm", face=-1, **_who(sp, b)), _name(b, 780),
                            _bubble(ta, 300, 560, 1), _bubble(tb, 780, 560, 2, sfx="wood_high")], draw=A.ground)
    if kind == "react":
        w = p["who"]
        els = [Fig(540, G, 340, at=0, pose=p.get("p0", "stand"), mood=p.get("m0", "calm"), **_who(sp, w),
                   moves=[(2, dict(pose=p.get("p1", "fist"), mood=p.get("m1", "angry"), dur=0.25, sfx="kick"))]),
               _name(w, 540)]
        if p.get("icon"):
            els += [_obj(p["icon"], 820, 520, 120, 1, p.get("color", acc)), Spark(820, 520, at=1)]
        return S(cap, tag, els, draw=A.ground, shake=[2] if p.get("shake", True) else [])
    if kind == "crowd":
        ic, col = p.get("icon", "question"), p.get("color", K.RED)
        return S(cap, tag, [Custom(crowd, x=540, y=G, at=0, enter="fade", n=6, s=250, spread=820),
                            Icon(ic, 300, 560, 90, color=col, at=1, sfx="wood_high"),
                            Icon(ic, 540, 500, 110, color=col, at=2, sfx="wood_high"),
                            Icon(ic, 780, 560, 90, color=col, at=3, sfx="wood_high")])
    if kind == "count":
        els = [Counter(p.get("v0", 0), p["v1"], 540, 800, 260, at=0, land=2, suffix=p.get("suffix", ""),
                       sub=p.get("sub"), fmt=p.get("fmt", "{:.0f}"))]
        if p.get("icon"):
            els += [_obj(p["icon"], 540, 480, 150, 3, p.get("color", K.GOLD), sfx="ding"), Spark(540, 480, at=3)]
        return S(cap, tag, els, hits=[(0, "shaker", 0.8, "滚动")])
    if kind == "big":
        return S(cap, tag, [Big(p["word"], 540, 720, p.get("size", 260), at=0, sfx="kick", sub=p.get("sub"), sub_size=50,
                                rays=True, glow=True, shine=True, spark=True), Spark(540, 720, at=2, sfx="ding")],
                 punch=0.03, flashes=[0], shake=[0])
    if kind == "flags":
        items = p["items"]
        xs = {2: (360, 720), 3: (270, 540, 810), 4: (200, 420, 660, 880)}[len(items)]
        its = [(ch, xs[i], 0, b, brk, tilt) for i, (ch, b, brk, tilt) in enumerate(items)]
        hits = [(b, "pop", 0.8, ch) for ch, b, _, _ in items]
        hits += [(brk, "kick", 0.9, f"{ch}旗折断") for ch, _, brk, _ in items if brk is not None]
        hits += [(t, "rim", 0.9, f"{ch}旗调转") for ch, _, _, t in items if t is not None]
        seen, uniq = set(), []
        for h in hits:
            if h[0] not in seen:
                seen.add(h[0])
                uniq.append(h)
        els = [Custom(A.flags, x=0, y=1060, at=0, enter="none", s=320, items=its)]
        if p.get("say"):
            els.append(_bubble(p["say"], p.get("sx", 800), 420, p.get("sb", 3)))
        return S(cap, tag, els, hits=uniq, shake=[b for _, _, b, _ in items if b is not None][:1])
    if kind == "pops":
        extra = [Icon(p["icon"], 540, 470, 110, color=p.get("color", K.RED), at=3, sfx="rim")] if p.get("icon") else []
        return pops(p["words"], tag, size=p.get("size", 120), flash=p.get("flash", 1), extra=extra)
    if kind == "brush":
        return S(cap, p.get("tag", "原文"), [
            Label(p["label"], 540, 400, 44, at=0, sfx="wood_low"),
            Custom(A.brush_text, x=540, y=820, at=0, enter="none", text=p["text"], size=min(110, 700 // len(p["text"])),
                   b0=0, step=0.4)], hits=[(2, "wood_high", 0.8, "落笔")])
    if kind == "cards":
        good = p.get("good", 1)
        xs = (290, 790)
        els = [Card(p["a"], 290, 760, 40, at=0, sfx="pop"), Card(p["b"], 790, 760, 40, at=1, sfx="pop")]
        els += [Icon("check", xs[good], 540, 100, color=K.GREEN, at=2, sfx="ding"),
                Icon("cross", xs[1 - good], 540, 100, color=K.RED, at=3, sfx="rim")]
        return S(cap, tag, els)
    if kind == "chat":
        return S(cap, tag, [Custom(phone_chat, x=540, y=780, at=0, enter="pop", w=480, h=700, who=p["who"],
                                   msgs=[(i, m) for i, m in enumerate(p["msgs"])], unread=False)],
                 hits=[(0, "wood_high", 0.8, "消息"), (1, "wood_low", 0.6, "消息"), (2, "wood_low", 0.6, "消息"),
                       (3, "wood_low", 0.6, "消息")])
    if kind == "check":
        return S(cap, tag, [Custom(checklist, x=540, y=780, at=0, enter="pop", w=620, title=p["title"],
                                   items=[(t, True) for t in p["items"]], b0=1, step=1)],
                 hits=[(0, "wood_high", 0.8, "清单"), (1, "ding", 0.7, "打勾"), (2, "ding", 0.7, "打勾"),
                       (3, "ding", 0.8, "打勾")])
    if kind == "form":
        rows = p["rows"]
        return S(cap, tag, [Custom(A.form, x=540, y=780, at=0, enter="pop", title=p["title"], rows=rows,
                                   skip=len(rows) - 1, skip_at=len(rows) - 1)],
                 hits=[(i, "ding", 0.7, "审核") for i in range(len(rows) - 1)] + [(len(rows) - 1, "rim", 1.0, "跳过")])
    if kind == "stack":
        return S(cap, "落到自己", [Custom(A.stack, x=540, y=800, at=0, enter="fade", top=1, items=p["items"])],
                 hits=[(0, "wood_low", 0.8, "排序"), (1, "kick", 1.0, "置顶")], flashes=[1], shake=[1])
    if kind == "pit":
        return S(cap, tag, [Custom(A.pit, x=540, y=900, at=0, enter="fade", fall=1, label=p["label"])],
                 hits=[(0, "wood_low", 0.8, "坑"), (1, "tom", 0.8, "掉坑"), (2, "tom", 0.8, "掉坑")])
    if kind == "home":
        return S(cap, tag, [Custom(A.crack_floor, x=540, y=900, at=0, enter="fade", b=1)],
                 hits=[(0, "wood_low", 0.8, "家"), (1, "rim", 1.0, "裂开")], shake=[1])
    if kind == "pole":
        mv = p.get("move")
        hits = [(0, "wood_low", 0.8, "立木")] + ([(mv, "wood_high", 0.9, "扛起"), (mv + 2, "ding", 0.9, "到北门")]
                                                 if mv is not None else [(2, "wood_high", 0.7, "三丈木")])
        return S(cap, tag, [Custom(A.pole, x=540, y=830, at=0, enter="fade", move=mv)], hits=hits)
    if kind == "awl":
        return S(cap, tag, [Custom(A.awl_bag, x=540, y=860, at=0, enter="pop", poke=p.get("poke", 99), sfx="wood_low")],
                 hits=[(p.get("poke", 2), "rim", 1.0, "锥尖冒出")] if p.get("poke") is not None else
                 [(2, "wood_high", 0.7, "锥")])
    if kind == "letters":
        b = p.get("burn")
        return S(cap, tag, [Custom(A.letters, x=540, y=780, at=0, enter="pop", burn=b, sfx="wood_low")],
                 hits=[(b, "kick", 0.9, "焚信"), (b + 1, "shaker", 0.6, "火")] if b is not None else
                 [(2, "wood_high", 0.7, "书信")], flashes=[b] if b is not None else [])
    raise ValueError(f"unknown beat kind: {kind}")


def tag_for(i, sp):
    if i < 8:
        return "灵魂拷问"
    if i < 11:
        return "原文"
    if i < 28:
        return sp["story_tag"]
    if i < 30:
        return "原文"
    if i < 36:
        return "当下 · 现象"
    if i == 36:
        return "落到自己"
    return f"{sp['chest']} · 小建议"


def build_episode(sp, next_title):
    beats = sp["beats"]
    if len(beats) != 41:
        raise ValueError(f"ep{sp['no']:02d}: {len(beats)} beats, need 41")
    shots = [make(k, cap, p, sp, tag_for(i, sp)) for i, (k, cap, p) in enumerate(beats)]
    shots.append(outro(sp["question"], next_title, f"收藏这4招，{sp['outro']}"))
    return episode(sp["no"], sp["key"], sp["concept"], sp["title"], sp["acc"], shots, [sp["ref"]], sp["cover"], 8,
                   sp["notes"], tags=sp.get("tags", ""))
