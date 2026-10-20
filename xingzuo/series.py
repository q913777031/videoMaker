"""星座科普 12 讲：每期共用的镜头模板。

每期结构（42 小节）：
  1–3  钩子：占星日期 → 那几天太阳其实在哪个星座 → 为什么对不上（8 小节）
  4    drop：星座名落版，星图连线按拍画出（第 8 小节）
  5–6  最亮的星（中文星官名 + 西方名）、什么时候看
  7–9  本期专属：神话 / 中国星官 / 天文冷知识（由各期模块提供，3 + 2 + 2 小节）
  10–11 岁差：地轴画圈；两千年前定的日期如今错开约一个星座
  12   研究证据：出生日期与性格无关（Hartmann 等 2006）
  13   小练习：什么时候、朝哪里找它
  14   收束
  15   参考资料 + 下一讲
"""

from engine.gfx import clamp01, ease_in_out

from adler import kit as K
from adler.core import Big, Custom, Episode, Fig, Icon, Shot, Txt, end_shot

from . import kit_xz as X

GROUND = 1130
SERIES = dict(series="星座科普", series_count=12, file_prefix="星座")
ORDER = ["Ari", "Tau", "Gem", "Cnc", "Leo", "Vir", "Lib", "Sco", "Sgr", "Cap", "Aqr", "Psc"]
LATIN = {"Ari": "Aries", "Tau": "Taurus", "Gem": "Gemini", "Cnc": "Cancer", "Leo": "Leo", "Vir": "Virgo",
         "Lib": "Libra", "Sco": "Scorpius", "Sgr": "Sagittarius", "Cap": "Capricornus", "Aqr": "Aquarius",
         "Psc": "Pisces", "Oph": "Ophiuchus"}
ACCENTS = {"Ari": "#C8553D", "Tau": "#8C6A3F", "Gem": "#3F7FA6", "Cnc": "#4C8C88", "Leo": "#C98A2B",
           "Vir": "#6E8B4E", "Lib": "#7A6AA8", "Sco": "#B0413E", "Sgr": "#3E5F99", "Cap": "#5C6B7A",
           "Aqr": "#2F87A8", "Psc": "#5B7FC7"}
# 最亮星中文名（星表个别用字有误，在此校正）
STAR_ZH = {"Sgr": "箕宿三"}
COMMON_REFS = ["d3-celestial 星表（Hipparcos / 耶鲁亮星表）；IAU 星座边界（Roman 1987）",
               "Hartmann, P., Reuter, M., & Nyborg, H. (2006). Personality and Individual Differences, 40(7), 1349–1362."]
END_REFS = ["d3-celestial 星表；IAU 星座边界；Hartmann 等（2006）"]     # 片尾卡用的简写，完整引用写入文档
NEXT = {ab: f"{i + 2:02d} {X.NAMES[ORDER[i + 1]]}" for i, ab in enumerate(ORDER[:-1])}


def ground(g):
    K.ground(g.c, GROUND)


def actual_phrase(ab: str) -> str:
    """占星日期那段时间，太阳实际所在星座的描述。"""
    acts = X.sign(ab)["astro_actual"]
    total = sum(n for _, n in acts)
    top, n = acts[0]
    name = X.NAMES[top]
    if n == total:
        return f"其实都在{name}里。"
    if n / total >= 0.8:
        return f"几乎都在{name}里。"
    if n / total >= 0.6:
        return f"大多在{name}里。"
    return f"大多在{name}和{X.NAMES[acts[1][0]]}里。"


def best_month(ab: str) -> int:
    m, d = (int(v) for v in X.sign(ab)["best_evening"].split("-"))
    return m if d <= 20 else m % 12 + 1


def where(ab: str) -> str:
    alt = X.sign(ab)["culmination_alt"]
    if alt < 25:
        return "南方低空"
    if alt > 65:
        return "头顶偏南"
    return "南方天空"


def brightest(ab: str) -> dict:
    st = dict(X.sign(ab)["named"][0])
    st["zh"] = STAR_ZH.get(ab, st["zh"])
    return st


# ---------------------------------------------------------------- 1 日历

def _calendar_shot(ab):
    s = X.sign(ab)

    def cal(c, g, t, d):
        k = clamp01(g.since(4) / 0.4)
        X.calendar(c, 0, 0, 300, s["astro"][0], s["astro"][1], 1, 1, g.acc, -3,
                   0.4 + 0.6 * K.ease_out_back(clamp01(g.since(0) / 0.4), 1.6))
        if k > 0:
            K.spotlight(c, 0, 0, 380, g.acc, 0.15 * k)
    return cal


def _name_tag(ab):
    def tag(c, g, t, d):
        k = clamp01(g.since(d["b0"]) / 0.35)
        if k <= 0:
            return
        w = K.text_w(X.NAMES[ab], 50, "serif_black") + 70
        with K.at(c, 0, 0, -6, 0.3 + 0.7 * K.ease_out_back(k, 2)):
            with K.paper(c, k, 0.8):
                K.rr(c, 0, 0, w, 90, 45, g.acc)
            K.text(c, X.NAMES[ab], 0, 2, 50, "serif_black", K.PAPER, k)
    return tag


# ---------------------------------------------------------------- 2 黄道条

def _strip_shot(ab):
    s = X.sign(ab)
    a0, a1 = s["astro"]

    def strip(c, g, t, d):
        hi = tuple(k for k, _ in s["astro_actual"])
        da, db = X.doy(a0), X.doy(a1)
        if db < da:
            db += 365
        sp = ease_in_out(clamp01((g.t - g.b(4)) / max(0.1, g.b(10) - g.b(4))))
        sun = (da + (db - da) * sp) % 365 if g.since(4) >= 0 else None
        X.ecliptic_strip(c, 0, 0, 940, 120, hi if g.since(10) >= 0 else (), (a0, a1), clamp01(g.since(2) / 0.5), sun,
                         1, True, 0.0, 26)
        if g.since(10) >= 0:
            top = s["astro_actual"][0][0]
            k = clamp01(g.since(10) / 0.35)
            K.text(c, f"太阳在：{X.NAMES[top]}", 0, 170, 44, "serif_black", X.SKY, k)
    return strip


# ---------------------------------------------------------------- 4 drop 星图

def _drop_card(ab):
    def card(c, g, t, d):
        p = clamp01(g.since(1) / max(0.1, g.b(10) - g.b(1)))
        X.sky_card(c, 0, 0, 900, 560, ab, p, g.t, 1)
    return card


# ---------------------------------------------------------------- 5 最亮星

def _bright_card(ab):
    st = brightest(ab)

    def card(c, g, t, d):
        X.sky_card(c, 0, 0, 900, 700, ab, 1, g.t, 1, 0, clamp01(g.since(2) / 0.4), f"{st['zh']}|{st['en']}",
                   clamp01(g.since(4) / 0.4))
    return card


# ---------------------------------------------------------------- 6 什么时候看

def _season_panel(ab):
    alt = X.sign(ab)["culmination_alt"]
    frac = clamp01(alt / 80) * 0.75 + 0.12

    def panel(c, g, t, d):
        X.night_panel(c, 0, 0, 900, 720, ab, g.t, 1, clamp01(g.since(6) / 0.4), frac, 1, "南")
        k = clamp01(g.since(2) / 0.35)
        if k > 0:
            K.pill(c, -300, -300, f"{best_month(ab)}月 · 晚上9点", 34, K.PAPER, X.SKY, k)
    return panel


# ---------------------------------------------------------------- 10 岁差

def _precession(c, g, t, d):
    phase = 0.08 * g.t
    X.precession(c, 0, 80, 300, phase, 1, clamp01(g.since(2) / 1.6))
    k = clamp01(g.since(6) / 0.35)
    if k > 0:
        K.pill(c, 0, -470, "约 2.6 万年转一圈", 36, X.SKY, K.PAPER, k)


def _shift_strip(ab):
    s = X.sign(ab)

    def strip(c, g, t, d):
        sh = 30 * ease_in_out(clamp01((g.t - g.b(4)) / max(0.1, g.b(8) - g.b(4))))
        a0, a1 = s["astro"]
        X.ecliptic_strip(c, 0, -120, 940, 110, (ab,), (a0, a1), 1, None, 1, True, 0.0, 26, "如今的占星日期")
        K.text(c, "两千多年前，太阳大约在这里", 0, 120, 30, "sans_medium", K.INK2, clamp01(g.since(4) / 0.4))
        X.ecliptic_strip(c, 0, 230, 940, 110, (ab,), (a0, a1), clamp01(g.since(4) / 0.4), None, clamp01(g.since(4) / 0.4),
                         True, sh, 26, "")
    return strip


# ---------------------------------------------------------------- 12 研究证据

def _study(c, g, t, d):
    """两张样本卡 + 12 根几乎一样高的柱子（示意）。"""
    for i, (n, lab) in enumerate((("4000+", "越战老兵研究"), ("11000+", "美国青年追踪调查"))):
        k = clamp01(g.since(i * 1.5) / 0.4)
        if k > 0:
            K.text_card(c, -220 + i * 440, -330, [n, lab], 40, 380, K.PAPER, K.INK, g.acc, k, 0,
                        0.4 + 0.6 * K.ease_out_back(k, 1.6), g.acc, "serif", 0.8)
    p = clamp01(g.since(4) / 1.0)
    vals = [0.80, 0.82, 0.79, 0.81, 0.80, 0.83, 0.80, 0.79, 0.81, 0.82, 0.80, 0.81]
    labels = [X.SHORT[a][0] for a in ORDER]
    K.bar_chart(c, 0, 210, 860, 300, vals, [K.tint(g.acc, 0.25)], p, labels, 28, 1.0)
    k = clamp01(g.since(10) / 0.4)
    if k > 0:
        K.seg(c, -450, 210 - 300 * 0.805, 450, 210 - 300 * 0.805, K.RED, 4, k)
        K.text(c, "示意：各星座之间没有可靠差异", 0, -110, 28, "sans_medium", K.INK2, k)


# ---------------------------------------------------------------- 13 小练习

def _practice(ab):
    alt = X.sign(ab)["culmination_alt"]
    frac = clamp01(alt / 80) * 0.75 + 0.12
    st = brightest(ab)

    def panel(c, g, t, d):
        p = clamp01(g.since(2) / max(0.1, g.b(9) - g.b(2)))
        X.night_panel(c, 0, 0, 900, 760, ab, g.t, p, clamp01(g.since(10) / 0.4), frac, 1, "南", st["zh"],
                      clamp01(g.since(11) / 0.4))
    return panel


# ---------------------------------------------------------------- 14 收束

def _finale(ab):
    def card(c, g, t, d):
        X.sky_card(c, 0, 0, 760, 560, ab, 1, g.t, 1, 0, 0.6)
    return card


def episode(no: int, ab: str, shape: str, mid: list, refs: list, notes: list, hashtags: str, cover_title: str,
            cover_sub: str, title: str | None = None, drop_text: str | None = None, cover_shot: int = 3,
            cover_t: float = 5.6) -> Episode:
    """组装一期：mid 为第 7–9 镜（3 + 2 + 2 小节）；shape 为第 4 镜字幕（星座形状一句话）。"""
    s = X.sign(ab)
    name = X.NAMES[ab]
    st = brightest(ab)
    a0, a1 = s["astro"]
    month = best_month(ab)
    assert [m.bars for m in mid] == [3, 2, 2], "第 7–9 镜应为 3 + 2 + 2 小节"
    sub = LATIN[ab] + (f" · 天文名：{X.ASTRO_NAMES[ab]}" if ab in X.ASTRO_NAMES else "")
    title = title or f"{name}，天上到底长什么样？"
    acts = "、".join(f"{X.NAMES[k]} {n} 天" for k, n in s["astro_actual"])
    sun_a, sun_b, sun_n = X.DATA["sun"][ab]
    shots = [
        Shot(3, f"生日在{X.mmdd(a0)}到{X.mmdd(a1)}，|你是{name}？", "情境演绎", [
            Fig(260, GROUND, 360, at=0, mood="happy", hair="short",
                moves=[(8, dict(pose="point", mood="smile", sfx="wood_high", note="主角指着日历"))]),
            Custom(_calendar_shot(ab), x=690, y=700, at=0, enter="none"),
            Custom(_name_tag(ab), x=690, y=1000, at=0, enter="none", b0=4),
        ], draw=ground, hits=[(0, "wood_low", 0.7, "日历弹出"), (4, "bongo_high", 0.85, f"“{name}”标签贴上")],
            note=f"主角拿着日历：{X.mmdd(a0)}–{X.mmdd(a1)}，第 4 拍贴上“{name}”标签"),
        Shot(3, f"可这些天的太阳，|{actual_phrase(ab)}", "天文观测", [
            Custom(_strip_shot(ab), x=540, y=760, at=0, enter="fade"),
        ], hits=[(2, "wood_high", 0.8, "红色括号标出占星日期"), (4, "shaker", 0.7, "太阳开始沿黄道走"),
                 (10, "rim", 0.9, "太阳实际所在的星座亮起")],
            note=f"黄道 13 星座条（宽度按太阳实际停留天数）：红括号标占星日期，太阳走过括号，实际所在星座变深（{acts}）"),
        Shot(2, "日历上的星座，|和天上的对不上？", "情境演绎", [
            Fig(540, GROUND, 360, at=0, enter="none", pose="shrug", mood="surprised", hair="short"),
            Icon("question", 760, 640, 140, color=ACCENTS[ab], at=2, enter="pop", sfx="bongo_low", note="大问号"),
        ], draw=ground, note="主角摊手，头顶弹出大问号"),
        Shot(3, drop_text or shape, "天文观测", [
            Big(name, 540, 450, 150, at=0, sfx="kick", sub=sub, note="概念落版（音乐 drop）"),
            Custom(_drop_card(ab), x=540, y=960, at=0, enter="pop"),
        ], hits=[(4, "wood_high", 0.6, "连线画到一半"), (8, "wood_low", 0.6, "连线快画完")],
            note=f"drop 处“{name}”砸下；星图卡上金色连线按拍逐段画出"),
        Shot(3, f"最亮的星：{st['zh']}，|西方叫 {st['en']}。", "天文观测", [
            Custom(_bright_card(ab), x=540, y=800, at=0, enter="fade"),
        ], hits=[(2, "rim", 0.9, f"{st['zh']}亮起"), (4, "wood_high", 0.8, "名字标注出现")],
            note=f"星图上最亮的星（{st['zh']} / {st['en']}，{st['mag']:.2f} 等）发光并标注名字"),
        Shot(3, f"{month}月前后晚上9点，|它在{where(ab)}最高。", "天文观测", [
            Custom(_season_panel(ab), x=540, y=820, at=0, enter="fade"),
        ], hits=[(2, "wood_low", 0.8, "时间标签"), (6, "bongo_high", 0.8, "最亮星闪一下")],
            note=f"夜空窗口：地平线与“南”字，{name}挂在{where(ab)}（北京上中天高度约 {s['culmination_alt']:.0f}°）"),
        *mid,
        Shot(3, "地轴像陀螺一样，|慢慢画圈。", "机制示意", [
            Custom(_precession, x=540, y=880, at=0, enter="fade"),
        ], hits=[(2, "shaker", 0.7, "地轴开始画圈"), (6, "wood_high", 0.8, "“约 2.6 万年一圈”")],
            note="地球与倾斜 23.4° 的自转轴，轴端沿小圆缓慢画圈（岁差）"),
        Shot(3, "两千多年前定的日期，|如今错开了约一个星座。", "机制示意", [
            Custom(_shift_strip(ab), x=540, y=820, at=0, enter="fade"),
        ], hits=[(4, "wood_low", 0.8, "下方的旧黄道条开始滑动"), (8, "rim", 0.9, "错开约一个月")],
            note="上下两条黄道星座条：下方代表两千多年前，按拍向右滑开约一个月，与占星日期错位"),
        Shot(4, "1.5万人的数据：|出生日期和性格无关。", "研究证据", [
            Custom(_study, x=540, y=830, at=0, enter="fade"),
            Txt("Hartmann、Reuter、Nyborg，2006", 540, 1245, 26, at=2, font="sans_medium", color=K.INK2),
        ], research=True, hits=[(0, "wood_high", 0.8, "4000+ 样本卡"), (2, "wood_low", 0.8, "11000+ 样本卡"),
                                (4, "shaker", 0.7, "12 根柱子长出"), (10, "rim", 0.8, "红线：几乎一样高")],
            note="两张样本卡（4000+ / 11000+），12 个星座的柱子几乎一样高（示意），红线拉平"),
        Shot(4, f"小练习：{month}月晚上，|朝南找找{st['zh']}。", "小练习", [
            Custom(_practice(ab), x=540, y=800, at=0, enter="fade"),
        ], hits=[(2, "shaker", 0.7, "连线开始画出"), (10, "rim", 0.9, f"{st['zh']}亮起"), (12, "wood_high", 0.7, "名字出现")],
            note=f"夜空窗口里，{name}的连线逐段画出，最后{st['zh']}亮起并标名"),
        Shot(2, "星星是真的；|性格，由你自己写。", "天文观测", [
            Custom(_finale(ab), x=540, y=800, at=0, enter="pop", sfx="clap", note="星图收束"),
        ], note=f"{name}星图卡居中，最亮星微微发光"),
        end_shot(refs + END_REFS, NEXT.get(ab) and f"{NEXT[ab]}：天上到底长什么样？"),
    ]
    notes = [
        f"占星日期取常见说法 {X.mmdd(a0)}–{X.mmdd(a1)}（不同来源前后差 1 天）。按 IAU 星座边界计算（2026 年、北京时间正午），这段时间太阳实际在：{acts}。"
        f"太阳在{name}的实际日期为 {X.mmdd(sun_a)}–{X.mmdd(sun_b)}，共 {sun_n} 天；不同年份相差约 1 天。",
        f"“{month}月前后晚上 9 点在{where(ab)}最高”按北京（东经 116.4°、北纬 40°）计算星座中心上中天时刻，上中天高度约 "
        f"{s['culmination_alt']:.0f}°；南方城市会更高。",
        f"最亮星 {st['zh']}（{st['en']}，视星等 {st['mag']:.2f}），中文星官名取自 d3-celestial 星名表。",
        "岁差：地轴方向约 2.6 万年转一圈，春分点每 72 年左右西移约 1°。占星的“太阳星座”按春分点等分黄道，两千多年前与同名星座大致对齐，"
        "如今错开约一个星座。",
        "研究证据：Hartmann 等（2006）分析越战老兵研究 4000 多人与美国青年追踪调查（NLSY79）11000 多人的数据，"
        "未发现出生日期（含太阳星座）与性格、一般智力之间有关联。第 12 镜柱状图为示意，不是论文数据。",
        *notes,
    ]
    return Episode(no, ab.lower(), name, title, ACCENTS[ab], shots, refs=refs + COMMON_REFS,
                   publish_title=f"{title}｜星座科普{no:02d} {name}", hashtags=hashtags, cover_title=cover_title,
                   cover_sub=cover_sub, cover_shot=cover_shot, cover_t=cover_t, notes=notes, **SERIES).build()
