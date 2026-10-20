"""13 番外 · 蛇夫座：太阳经过的第 13 个星座。

不走 series.episode 模板（蛇夫座没有占星日期），钩子与机制镜头单独写，星图、最亮星、观看时间、小练习复用模板。
"""

import math

import skia

from engine.gfx import clamp01, ease_in_out, ease_out

from adler import kit as K
from adler.core import Big, Custom, Episode, Fig, Icon, Label, Shot, end_shot

from . import kit_xz as X
from . import series as S

AB = "Oph"
ACC = "#3E8E6E"
GROUND = S.GROUND
SER = X.DATA["serpens"]
REFS = ["奥维德《岁时记》、海吉努斯《天文的诗篇》（阿斯克勒庇俄斯）",
        "NASA Space Place（2016）；NASA 2020 年 7 月澄清：没有修改黄道星座",
        "d3-celestial 星表；IAU 星座边界（1930）"]


# ---------------------------------------------------------------- 1 十二个标签

def twelve_tags(c, g, t, d):
    """十二个星座名牌按拍排成一圈，第 10 拍中间冒出一个“？”。"""
    for i, ab in enumerate(S.ORDER):
        k = clamp01(g.since(i * 0.5) / 0.3)
        if k <= 0:
            continue
        a = -math.pi / 2 + i * math.pi / 6
        x, y = 330 * math.cos(a), 190 * math.sin(a)
        w = K.text_w(X.SHORT[ab], 34, "serif_black") + 36
        with K.at(c, x, y, 0, 0.3 + 0.7 * K.ease_out_back(k, 1.8)):
            K.rr(c, 0, 0, w, 60, 30, S.ACCENTS[ab], k)
            K.text(c, X.SHORT[ab], 0, 2, 34, "serif_black", K.PAPER, k)


# ---------------------------------------------------------------- 2 / 5 黄道条

def strip_oph(c, g, t, d):
    """黄道星座条：太阳从 11 月 20 日走到 12 月 22 日，第 6 拍起蛇夫座变成红色并放大标注。"""
    sp = ease_in_out(clamp01((g.t - g.b(2)) / max(0.1, g.b(10) - g.b(2))))
    a, b = X.doy("11-20"), X.doy("12-22")
    sun = a + (b - a) * sp if g.since(2) >= 0 else None
    X.ecliptic_strip(c, 0, 0, 940, 120, ("Oph",) if g.since(6) >= 0 else (), None, 0, sun, 1, True, 0.0, 26)
    k = clamp01(g.since(6) / 0.35)
    if k > 0:
        oa, ob, n = X.DATA["sun"]["Oph"]
        x = -470 + (X.doy(oa) + n / 2) * 940 / 365
        K.arrow(c, (x - 160, -230), (x - 10, -80), K.RED, 8, k, k, 0.2, 26)
        K.text(c, "蛇夫座", x - 220, -260, 52, "serif_black", K.RED, k)


def days_compare(c, g, t, d):
    """天蝎 7 天 vs 蛇夫 18 天：两排小太阳按拍一格格点亮。"""
    rows = (("Sco", 7, S.ACCENTS["Sco"], -150), ("Oph", 18, ACC, 120))
    for ab, n, col, y in rows:
        K.text(c, X.NAMES[ab], -430, y, 46, "serif_black", col, 1, "left")
        for i in range(n):
            k = clamp01(g.since(1 + i * (8 / 18)) / 0.25)
            cx = -220 + (i % 9) * 66
            cy = y + (i // 9) * 70 - (35 if n > 9 else 0)
            K.dot(c, cx, cy, 24, K.LINE)
            if k > 0:
                K.dot(c, cx, cy, 24 * (0.4 + 0.6 * K.ease_out_back(k, 2)), K.GOLD)
        kk = clamp01(g.since(10) / 0.35)
        if kk > 0:
            K.pill(c, 440, y, f"{n} 天", 40, col, K.PAPER, kk)


# ---------------------------------------------------------------- 7 医神

def asclepius(c, g, t, d):
    """医神手握一条大蛇；第 6 拍躺着的人坐起来，第 9 拍天上劈下闪电。"""
    K.figure(c, -120, 330, 420, "reach", K.mix(ACC, K.INK, 0.25), mood="calm", hair="short")
    path = skia.Path()
    for i in range(41):
        u = i / 40
        x = -260 + u * 420
        y = -120 + 70 * math.sin(u * 9 + g.t * 2.5) * (0.4 + 0.6 * u)
        (path.moveTo if i == 0 else path.lineTo)(x, y)
    c.drawPath(path, K.paint("#7E9A4E", 1, 26))
    K.dot(c, 168, -120 + 70 * math.sin(9 + g.t * 2.5), 22, "#6E8A40")
    rise = ease_in_out(clamp01(g.since(6) / 0.6))
    K.figure(c, 280, 330, 300, K.blend("crouch", "stand", rise) if rise < 1 else "stand", K.OTHER, mood="surprised"
             if rise > 0.5 else "flat", lift=0.7)
    k = clamp01(g.since(9) / 0.15)
    if 0 < k and g.since(9) < 0.9:
        a = 1 - clamp01((g.since(9) - 0.3) / 0.6)
        pts = [(-60, -520), (-110, -380), (-40, -380), (-130, -200)]
        bolt = skia.Path()
        bolt.moveTo(*pts[0])
        for q in pts[1:]:
            bolt.lineTo(*q)
        c.drawPath(bolt, K.paint(K.GOLD, a, 14))


def rod(c, g, t, d):
    """一根木杖缠一条蛇（单蛇杖），旁边对比双蛇带翅膀的“赫尔墨斯杖”。"""
    def staff(x, snakes, wings, k, label, color):
        if k <= 0:
            return
        with K.fade(c, k):
            K.seg(c, x, -260, x, 260, "#8A6A45", 22)
            for sgn in snakes:
                p = skia.Path()
                for i in range(31):
                    u = i / 30
                    yy = 220 - u * 440
                    xx = x + sgn * 46 * math.sin(u * 3.2 * math.pi)
                    (p.moveTo if i == 0 else p.lineTo)(xx, yy)
                c.drawPath(p, K.paint("#7E9A4E", 1, 16))
            if wings:
                for sgn in (-1, 1):
                    K.poly(c, [(x, -250), (x + sgn * 120, -310), (x + sgn * 90, -250)], K.mix(K.GOLD, K.PAPER, 0.3))
            K.text(c, label, x, 330, 34, "sans_medium", color)

    staff(-170, (1,), False, clamp01(g.since(0) / 0.4), "单蛇杖：医学", ACC)
    staff(190, (1, -1), True, clamp01(g.since(4) / 0.4), "双蛇杖：另有来历", K.INK3)
    k = clamp01(g.since(6) / 0.3)
    if k > 0:
        K.ring(c, -170, 0, 300, K.RED, 7, k, k)


# ---------------------------------------------------------------- 9 巨蛇被切成两段

def serpens(c, g, t, d):
    def extra(c, P):
        k = clamp01(g.since(1) / 0.4)
        for j, feat in enumerate(SER):
            kj = clamp01(g.since(1 + j * 2) / 0.4)
            for seg in feat:
                pts = [P(r, dd) for r, dd in seg]
                for a, b in zip(pts, pts[1:]):
                    K.seg(c, a[0], a[1], a[0] + (b[0] - a[0]) * kj, a[1] + (b[1] - a[1]) * kj, "#9FD08A", 5, k)
                for px, py in pts:
                    K.dot(c, px, py, 5, X.STAR, kj)
            if kj > 0:
                cx = sum(P(r, dd)[0] for seg in feat for r, dd in seg) / sum(len(seg) for seg in feat)
                cy = min(P(r, dd)[1] for seg in feat for r, dd in seg)
                K.text(c, ("蛇头", "蛇尾")[j], cx, cy - 36, 36, "serif_black", "#C9EBB8", kj)
    X.sky_card(c, 0, 0, 940, 760, AB, 1, g.t, 1, margin=250, line_color=X.FAINT, extra=extra)


# ---------------------------------------------------------------- 10 十二等分

def wheel(c, g, t, d):
    """外圈：占星把黄道平均切成 12 份（各 30°）；内圈：天上的星座宽窄不一，还多一个蛇夫座。"""
    R1, R2, R3 = 360, 290, 210
    k_out = clamp01(g.since(0) / 0.6)
    for i, ab in enumerate(S.ORDER):
        a0 = -90 + i * 30
        p = skia.Path()
        p.addArc(skia.Rect.MakeLTRB(-R1, -R1, R1, R1), a0, 30 * k_out)
        c.drawPath(p, K.paint(S.ACCENTS[ab], 0.9, R1 - R2))
        if k_out > 0.9:
            am = math.radians(a0 + 15)
            K.text(c, X.SHORT[ab][0], (R1 + R2) / 2 * math.cos(am), (R1 + R2) / 2 * math.sin(am), 30, "serif_black",
                   K.PAPER, 1)
    k_in = clamp01(g.since(4) / 1.2)
    start = -90 + (X.doy(X.DATA["sun"]["Ari"][0]) - X.doy("03-21")) * 360 / 365
    acc = 0.0
    for ab in X.DATA["order"]:
        n = X.DATA["sun"][ab][2]
        sweep = n * 360 / 365
        drawn = clamp01((k_in * 360 - acc) / sweep)
        if drawn > 0:
            p = skia.Path()
            p.addArc(skia.Rect.MakeLTRB(-R2 + 8, -R2 + 8, R2 - 8, R2 - 8), start + acc, sweep * drawn - 1.5)
            col = K.RED if ab == "Oph" else K.mix(X.SKY, K.PAPER, 0.35)
            c.drawPath(p, K.paint(col, 1, R2 - R3 - 16))
            if drawn >= 1 and sweep > 16:
                am = math.radians(start + acc + sweep / 2)
                K.text(c, X.SHORT[ab][0], (R2 + R3) / 2 * math.cos(am), (R2 + R3) / 2 * math.sin(am), 26,
                       "sans_medium", K.PAPER, 1)
        acc += sweep
    K.text(c, "占星：等分 12 份", 0, -40, 34, "sans_medium", K.INK2, k_out)
    K.text(c, "天上：宽窄不一", 0, 20, 34, "sans_medium", K.RED, clamp01(g.since(4) / 0.4))


# ---------------------------------------------------------------- 11 1930 年边界

def boundaries(c, g, t, d):
    """星图卡上画出虚线“边界框”，第 6 拍盖下 1930 印章，标“全天 88 个星座”。"""
    def extra(c, P):
        k = clamp01(g.since(1) / 1.0)
        pts = [(-135, 14), (-75, 14), (-75, -30), (-135, -30)]
        q = [P(r, dd) for r, dd in pts]
        p = skia.Path()
        p.moveTo(*q[0])
        for v in q[1:] + [q[0]]:
            p.lineTo(*v)
        paint = K.paint("#FFC9B8", 0.9 * k, 4)
        paint.setPathEffect(skia.DashPathEffect.Make([18, 12], 0))
        c.drawPath(p, paint)
    X.sky_card(c, 0, -40, 900, 640, AB, 1, g.t, 1, margin=150, extra=extra)
    k = clamp01(g.since(6) / 0.25)
    if k > 0:
        sc = 1 + 0.6 * (1 - ease_out(k))
        with K.at(c, 300, -300, -12, sc):
            K.rr_stroke(c, 0, 0, 230, 110, 18, K.RED, 9, k)
            K.text(c, "1930", 0, 4, 70, "black", K.RED, k)
    kk = clamp01(g.since(8) / 0.35)
    if kk > 0:
        K.pill(c, 0, 360, "全天 88 个星座，边界从此固定", 34, X.SKY, K.PAPER, kk)


# ---------------------------------------------------------------- 12 NASA 误读

def headline(c, g, t, d):
    """手机上的标题“NASA 新增第 13 星座！”第 4 拍被红叉划掉，第 8 拍下面弹出 NASA 的澄清。"""
    with K.paper(c, 1, 1.1):
        K.rr(c, 0, -60, 520, 520, 50, K.DARK)
    K.rr(c, 0, -60, 480, 480, 34, K.PAPER)
    K.text(c, "热搜", -190, -250, 30, "sans_medium", K.RED, 1, "left")
    K.text(c, "NASA 新增", 0, -140, 56, "serif_black", K.INK)
    K.text(c, "第 13 星座！", 0, -60, 56, "serif_black", K.INK)
    K.rr(c, 0, 60, 380, 16, 8, K.LINE)
    K.rr(c, -40, 100, 300, 16, 8, K.LINE)
    k = clamp01(g.since(4) / 0.3)
    if k > 0:
        K.seg(c, -230, -230, -230 + 460 * k, 120 * k - 230 + 230 * k, K.RED, 14)
        K.seg(c, 230, -230, 230 - 460 * k, 120 * k - 230 + 230 * k, K.RED, 14)
    kk = clamp01(g.since(8) / 0.4)
    if kk > 0:
        K.text_card(c, 0, 350, ["NASA：我们没改黄道星座，", "只是把数学算了一遍。"], 38, 720, K.PAPER, K.INK, ACC, kk, 0,
                    0.4 + 0.6 * K.ease_out_back(kk, 1.6), ACC, "serif", 0.8)


# ---------------------------------------------------------------- 14 天市垣

TIANSHI = ["天市右垣九 梁", "天市右垣十 楚", "天市右垣十一 韩"]


def tianshi(c, g, t, d):
    named = {n["zh"]: n for n in X.sign(AB)["named"]}

    def extra(c, P):
        pts = []
        for i, zh in enumerate(TIANSHI):
            st = named.get(zh)
            if not st:
                continue
            px, py = P(st["ra"], st["dec"])
            pts.append((px, py, zh.split(" ")[1]))
            k = clamp01(g.since(1 + i) / 0.3)
            if k > 0:
                K.spotlight(c, px, py, 70 * k, "#FFE7A8", 0.5 * k)
                K.dot(c, px, py, 9, "#FFFFFF", k)
                K.text(c, zh.split(" ")[1], px + 34, py, 40, "serif_black", "#FFE7A8", k, "left")
        kk = clamp01(g.since(4) / 0.4)
        if kk > 0 and len(pts) > 1:
            for a, b in zip(pts, pts[1:]):
                K.seg(c, a[0], a[1], a[0] + (b[0] - a[0]) * kk, a[1] + (b[1] - a[1]) * kk, "#FF9F80", 7)
    X.sky_card(c, 0, 0, 900, 700, AB, 1, g.t, 1, line_color=X.FAINT, extra=extra)


def build() -> Episode:
    st = S.brightest(AB)
    month = S.best_month(AB)
    oa, ob, on = X.DATA["sun"][AB]
    shots = [
        Shot(3, "星座只有十二个？|太阳可不这么想。", "情境演绎", [
            Custom(twelve_tags, x=540, y=520, at=0, enter="none"),
            Fig(540, GROUND, 330, at=0, mood="smile", hair="short",
                moves=[(10, dict(pose="think", mood="surprised", sfx="rim", note="主角愣住"))]),
            Icon("question", 540, 520, 120, color=ACC, at=10, enter="pop"),
        ], draw=S.ground, hits=[(0, "wood_high", 0.6, "第一个星座名牌"), (3, "wood_low", 0.6, "第七个名牌"),
                                (5, "bongo_high", 0.7, "第十二个名牌")],
            note="十二个星座名牌按拍排成一圈，中间冒出问号"),
        Shot(3, "每年冬天，太阳会穿过|第十三个星座。", "天文观测", [
            Custom(strip_oph, x=540, y=760, at=0, enter="fade"),
        ], hits=[(2, "shaker", 0.7, "太阳沿黄道前进"), (6, "rim", 0.9, "蛇夫座变红并被箭头指出")],
            note="黄道 13 星座条：太阳从 11 月下旬走到 12 月下旬，天蝎与人马之间的蛇夫座变红"),
        Shot(2, "它，叫什么？", "情境演绎", [
            Fig(540, GROUND, 360, at=0, enter="none", pose="shrug", mood="surprised", hair="short"),
            Icon("question", 760, 640, 140, color=ACC, at=2, enter="pop", sfx="bongo_low", note="大问号"),
        ], draw=S.ground, note="主角摊手，头顶弹出大问号"),
        Shot(3, "蛇夫座：|一个人抓着一条大蛇。", "天文观测", [
            Big("蛇夫座", 540, 450, 150, at=0, sfx="kick", sub="Ophiuchus · 黄道第 13 星座", note="概念落版（音乐 drop）"),
            Custom(S._drop_card(AB), x=540, y=960, at=0, enter="pop"),
        ], hits=[(4, "wood_high", 0.6, "连线画到一半"), (8, "wood_low", 0.6, "连线快画完")],
            note="drop 处“蛇夫座”砸下；星图卡上金色连线按拍逐段画出"),
        Shot(3, f"太阳在这里待 {on} 天，|比天蝎座还久。", "天文观测", [
            Custom(days_compare, x=540, y=800, at=0, enter="fade"),
        ], hits=[(1, "wood_high", 0.7, "小太阳开始点亮"), (5, "wood_low", 0.7, "天蝎座 7 天点满"),
                 (9, "bongo_high", 0.8, "蛇夫座 18 天点满"), (10, "rim", 0.9, "天数标签")],
            note=f"两排小太阳：天蝎座 7 格、蛇夫座 {on} 格按拍点亮（{X.mmdd(oa)}–{X.mmdd(ob)}）"),
        Shot(3, f"最亮的星：{st['zh']}，|西方叫 {st['en']}。", "天文观测", [
            Custom(S._bright_card(AB), x=540, y=800, at=0, enter="fade"),
        ], hits=[(2, "rim", 0.9, f"{st['zh']}亮起"), (4, "wood_high", 0.8, "名字标注出现")],
            note=f"星图上最亮的星（{st['zh']} / {st['en']}，{st['mag']:.2f} 等）发光并标注名字"),
        Shot(3, "神话里，他是医神|阿斯克勒庇俄斯。", "希腊神话", [
            Custom(asclepius, x=540, y=800, at=0, enter="fade"),
            Label("能让死者复生", 760, 420, 32, at=6, fill=ACC, sfx="bongo_high", note="躺着的人坐起来"),
        ], hits=[(9, "frame", 0.9, "宙斯的闪电劈下")],
            note="医神手握一条大蛇；第 6 拍躺着的人坐起来，第 9 拍天上劈下闪电"),
        Shot(2, "医学标志上的单蛇杖，|就来自他。", "希腊神话", [
            Custom(rod, x=540, y=820, at=0, enter="fade"),
        ], hits=[(4, "wood_low", 0.7, "双蛇杖出现作对比"), (6, "rim", 0.8, "红圈圈出单蛇杖")], text_beat=0,
            note="左：一根木杖缠一条蛇（阿斯克勒庇俄斯之杖）；右：带翅膀的双蛇杖作对比；红圈圈出单蛇杖"),
        Shot(2, "他手里的巨蛇座，|被他隔成了两半。", "天文观测", [
            Custom(serpens, x=540, y=800, at=0, enter="fade"),
        ], hits=[(1, "wood_high", 0.8, "蛇头亮起"), (3, "wood_low", 0.8, "蛇尾亮起")], text_beat=0,
            note="蛇夫座两侧的巨蛇座蛇头、蛇尾两段先后亮起（全天唯一分成两块的星座）"),
        Shot(3, "占星的十二宫，|是把黄道平分成 12 份。", "机制示意", [
            Custom(wheel, x=540, y=800, at=0, enter="fade"),
        ], hits=[(0, "wood_high", 0.7, "外圈 12 等分"), (4, "shaker", 0.7, "内圈真实星座宽窄不一"),
                 (8, "rim", 0.8, "蛇夫座那一段变红")],
            note="外圈 12 等分（占星）；内圈按太阳实际停留天数画出 13 个星座，蛇夫座为红色"),
        Shot(3, "星座的边界，|1930 年才正式划定。", "天文观测", [
            Custom(boundaries, x=540, y=820, at=0, enter="fade"),
        ], hits=[(1, "shaker", 0.7, "虚线边界画出"), (6, "frame", 0.9, "1930 印章"), (8, "wood_high", 0.7, "88 个星座")],
            note="蛇夫座星图上画出示意边界虚线，盖下“1930”印章：国际天文学联合会定下全天 88 个星座的边界"),
        Shot(4, "“NASA 新增第 13 星座”？|这是误读。", "常见误解", [
            Custom(headline, x=540, y=760, at=0, enter="pop", sfx="wood_high", note="热搜标题出现"),
        ], hits=[(4, "rim", 0.9, "红叉划掉标题"), (8, "bongo_high", 0.8, "NASA 澄清卡")],
            note="手机热搜“NASA 新增第 13 星座！”被红叉划掉，下方弹出 NASA 的澄清"),
        Shot(4, f"小练习：{month}月晚上，|朝南找找{st['zh']}。", "小练习", [
            Custom(S._practice(AB), x=540, y=800, at=0, enter="fade"),
        ], hits=[(2, "shaker", 0.7, "连线开始画出"), (10, "rim", 0.9, f"{st['zh']}亮起"), (12, "wood_high", 0.7, "名字出现")],
            note=f"夜空窗口里，蛇夫座的连线逐段画出，最后{st['zh']}亮起并标名"),
        Shot(2, "在中国星空里，|它是“天市垣”的城墙。", "中国星官", [
            Custom(tianshi, x=540, y=800, at=0, enter="fade"),
        ], hits=[(1, "wood_high", 0.8, "梁"), (2, "wood_low", 0.8, "楚"), (3, "bongo_high", 0.8, "韩")], text_beat=0,
            note="天市右垣九（梁）、十（楚）、十一（韩）按拍亮起并连成一段城墙"),
        end_shot(REFS, None),
    ]
    notes = [
        f"按 IAU 星座边界计算（2026 年、北京时间正午），太阳在蛇夫座 {X.mmdd(oa)}–{X.mmdd(ob)}，共 {on} 天；在天蝎座仅 "
        f"{X.DATA['sun']['Sco'][2]} 天。不同年份相差约 1 天。",
        "黄道十二宫是巴比伦人把黄道等分为 12 份（每份 30°）的历法划分；NASA 2020 年 7 月在社交媒体上澄清，巴比伦人当年就略去了第 13 个星座，"
        "NASA 没有修改黄道星座，2016 年的 Space Place 文章只是按现在的天象“做了算术”。",
        "阿斯克勒庇俄斯是阿波罗之子、医神，传说能使死者复生，被宙斯以雷电击杀后升为蛇夫座；神话版本不一。"
        "单蛇缠绕的“阿斯克勒庇俄斯之杖”是医学标志（世界卫生组织标志即用此杖）；带翅膀的双蛇杖是赫尔墨斯之杖，常被误用为医学标志。",
        "巨蛇座被蛇夫座隔成蛇头、蛇尾两块，是现代 88 星座中唯一分成两块的星座。",
        "IAU 于 1928–1930 年间由德尔波特（Delporte）划定 88 个星座的正式边界；第 11 镜的虚线框为示意，不是实际边界。",
        f"最亮星 {st['zh']}（{st['en']}，视星等 {st['mag']:.2f}）；“{month}月前后晚上 9 点在南方天空最高”按北京计算，"
        f"上中天高度约 {X.sign(AB)['culmination_alt']:.0f}°。",
        "天市右垣九（梁）= 蛇夫座 δ、天市右垣十（楚）= 蛇夫座 ε、天市右垣十一（韩）= 蛇夫座 ζ，中文星官名取自 d3-celestial 星名表。",
    ]
    return Episode(13, "oph", "蛇夫座", "第 13 个星座，为什么没人提？", ACC, shots, refs=REFS + S.COMMON_REFS,
                   publish_title="第 13 个星座，为什么没人提？｜星座科普番外 蛇夫座",
                   hashtags="#蛇夫座 #星座 #第十三星座 #天文 #科普", cover_title="太阳每年都经过的|【第 13 个】星座",
                   cover_sub="番外 · 蛇夫座", cover_shot=5, cover_t=4.6, notes=notes, **S.SERIES).build()
