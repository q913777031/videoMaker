"""05 琳达问题（白板手绘版）：细节越多，为什么越容易信错？

节奏：14 个场景（2/3…/4 小节），每屏 ≈6.4 秒，画完停 2 秒（慢速讲解版，见 CLAUDE.md「白板手绘节奏」）。
叙事（C 复刻实验）：先认识琳达、读完她的介绍 → 观众先选“哪个更可能”（快快抢答 B）→
drop 揭晓：小圈套在大圈里，多数人选的 B 被红叉 → 亮书（两件都成的机会不会比只成一件高）→
快快只看像不像（代表性）→ 第二个实验：餐具，分开看时 24 件完好的那套出价高，并排一比就反过来 →
身边的例子（方案越写越细越像真的、脑补链条越长越信）→ 三招（拆开一条条问 / 每步连起来算 / 并排比）→ 评论区互动。
书中观点为转述（丹尼尔·卡尼曼《思考，快与慢》第 14–15 章，中译本胡晓姣、李爱民、何梦莹译，中信出版社 2012）；
例子与做法为示意与据书中思路整理的建议。
"""

import skia

from whiteboard import engine as wb
from whiteboard.engine import (BLACK, BLUE, GREEN, RED, Board, P, arrow, book, bubble, check, circle, cross, doc,
                               face, join, rect, stick, underline)

from .common import BOOK, episode, kuai, man

ACC = "#C2603A"
SQUARE_SHOT = 3                 # 场景 4：大圈套小圈，快快指着被红叉的 B

b = Board(size=(3600, 10200))


def J():
    return len(b.shots) - 1


def T(s, x, y, size=72, color=BLACK, k0=0.0, k1=None, sfx=None):
    """在当前镜头写字：写字时长按字数估计（每字约 0.25 拍，至少 0.8 拍）。"""
    k1 = k0 + max(0.8, 0.25 * len(s)) if k1 is None else k1
    b.text(J(), k0, k1, s, x, y, size, color, sfx=sfx)


def L(path, k0, k1, color=BLACK, width=10, sfx=None):
    b.path(J(), k0, k1, path, color, width, sfx=sfx)


def H(k, sfx, gain=0.8, note=""):
    b.hit(J(), k, sfx, gain, note)


def scene(text, tag, view, bars=3, **kw):
    return b.shot(text, tag, view=view, bars=bars, **kw)


# ---------------------------------------------------------------- 本讲画法

def mirror(path, x0) -> skia.Path:
    """以竖线 x = x0 左右翻转（让小人朝左指）。"""
    m = skia.Matrix()
    m.setScale(-1, 1, x0, 0)
    p = skia.Path(path)
    p.transform(m)
    return p


def dishes(x, y, stacks=3, s=1.0, cups=2) -> skia.Path:
    """一套餐具（侧视）：几摞盘子 + 几只杯子。(x, y) 为桌面中点。"""
    parts = []
    gap = 120 * s
    x0 = x - gap * (stacks + cups - 1) / 2
    for i in range(stacks):
        cx = x0 + i * gap
        for n in range(3):
            o = skia.Path()
            yy = y - 14 * s - n * 26 * s
            o.addOval(skia.Rect.MakeXYWH(cx - 50 * s, yy - 10 * s, 100 * s, 20 * s))
            parts.append(o)
    for i in range(cups):
        cx = x0 + (stacks + i) * gap
        parts.append(P((cx - 34 * s, y - 80 * s), (cx - 26 * s, y), (cx + 26 * s, y), (cx + 34 * s, y - 80 * s)))
        hd = skia.Path()
        hd.addArc(skia.Rect.MakeXYWH(cx + 22 * s, y - 64 * s, 34 * s, 40 * s), -90, 180)
        parts.append(hd)
    parts.append(P((x - gap * (stacks + cups) / 2 - 10 * s, y), (x + gap * (stacks + cups) / 2 + 10 * s, y)))
    return join(*parts)


def cracks(pts, s=1.0) -> skia.Path:
    """几道裂纹（小折线），pts 为每道裂纹的起点。"""
    return join(*[P((px, py), (px + 14 * s, py + 16 * s), (px + 4 * s, py + 30 * s), (px + 20 * s, py + 48 * s))
                  for px, py in pts])


def tag(x, y, w=230, h=100) -> skia.Path:
    """价签：五边形 + 小孔，(x, y) 为中心。"""
    return join(P((x - w / 2, y - h / 2), (x + w / 2 - 40, y - h / 2), (x + w / 2, y), (x + w / 2 - 40, y + h / 2),
                  (x - w / 2, y + h / 2), close=True), circle(x + w / 2 - 38, y, 9))


def slide(x, y, lines, w=300, h=210) -> skia.Path:
    """一页方案：外框 + 若干行字（行越多越细）。"""
    parts = [rect(x, y, w, h, 10), P((x - w / 2 + 30, y - h / 2 + 40), (x + 20, y - h / 2 + 40))]
    for i in range(lines):
        yy = y - h / 2 + 80 + i * 24
        parts.append(P((x - w / 2 + 30, yy), (x + w / 2 - 30 - (i % 3) * 30, yy)))
    return join(*parts)


def phone(x, y, w=110, h=190) -> skia.Path:
    return join(rect(x, y, w, h, 16), P((x - 16, y + h / 2 - 20), (x + 16, y + h / 2 - 20)))


def magnifier(x, y, r=45) -> skia.Path:
    return join(circle(x, y, r), P((x - r * 0.7, y + r * 0.7), (x - r * 1.6, y + r * 1.6)))


def zzz(x, y) -> skia.Path:
    out = []
    for i, sz in enumerate((22, 30, 38)):
        xx, yy = x + i * 40, y - i * 50
        out.append(P((xx - sz / 2, yy - sz / 2), (xx + sz / 2, yy - sz / 2), (xx - sz / 2, yy + sz / 2),
                     (xx + sz / 2, yy + sz / 2)))
    return join(*out)


# ---------------------------------------------------------------- 开局：认识琳达，读她的介绍（场景 1–2）
# 场景 1 为 2 小节（第 0–6 拍画完），场景 2–13 为 3 小节（12 拍：第 0–8 拍逐个画完，最后 4 拍停住），场景 14 为 4 小节。

LINDA = (600, 1250)
CARD = (1280, 1000)
scene("认识一下琳达", "复刻实验 · 先读一段话", (1050, 950, 0.8), bars=2)
L(stick(*LINDA, 0.85, "down", hair=True), 0, 0.9, BLACK, 10, sfx="wood_high")
L(face(*LINDA, 0.85, "smile"), 0.9, 1.0)
L(rect(LINDA[0], 830, 200, 90, 20), 1, 1.6, BLUE, 8, sfx="pop")
T("琳达", LINDA[0], 830, 60, BLUE, k0=1.6, k1=2.4)
L(rect(*CARD, 720, 640, 24), 3, 3.9, BLACK, 9, sfx="wood_low")
T("31岁，单身", CARD[0], 770, 58, k0=4, k1=5.5, sfx="pop")

scene("读完这段介绍", "复刻实验 · 先读一段话", (1200, 1000, 0.85))
T("直率，很聪明", CARD[0], 880, 58, k0=0, k1=1.5, sfx="pop")
T("大学学哲学", CARD[0], 990, 58, k0=2, k1=3.25, sfx="pop")
T("关心歧视和社会公正", CARD[0], 1100, 58, k0=4, k1=6, sfx="pop")
T("参加过反核游行", CARD[0], 1210, 58, k0=6, k1=7.75, sfx="pop")

# ---------------------------------------------------------------- 你先选，再揭晓（场景 3–4）

scene("哪个更可能？", "复刻实验 · 你先选", (2650, 1000, 0.85))
L(join(rect(2650, 650, 920, 150, 20), rect(2650, 870, 920, 150, 20)), 0, 0.9, BLACK, 9, sfx="wood_high")
T("A  银行柜员", 2650, 650, 64, k0=1, k1=2.5, sfx="pop")
T("B  银行柜员＋女权运动", 2650, 870, 58, k0=3, k1=5.25, sfx="pop")
KK3 = (2450, 1480)
L(kuai(*KK3, 0.65, "up"), 6, 6.8, RED, 9, sfx="wood_high")
L(bubble(2800, 1200, 220, 120, -1), 6.8, 7.2, RED, 8)
T("B！", 2800, 1200, 64, RED, k0=7.2, k1=8)

BIG, SMALL = (2480, 2450, 430), (2480, 2620, 200)
KK4 = (3120, 2900)
scene("多数人选了后一个", "揭晓 · 小圈在大圈里", (2650, 2400, 0.85), shake=[0, 7], flashes=[0])
L(circle(*BIG), 0, 0.9, BLACK, 11, sfx="kick")
T("A 银行柜员", BIG[0], 2140, 70, k0=1, k1=2.5, sfx="pop")
L(circle(*SMALL), 3, 3.8, BLUE, 10, sfx="wood_high")
T("B＋女权运动", SMALL[0], SMALL[1], 56, BLUE, k0=4, k1=5.25, sfx="pop")
L(mirror(kuai(*KK4, 0.6, "point"), KK4[0]), 5, 5.8, RED, 9, sfx="wood_high")
T("多数人选它", 3110, 2450, 56, RED, k0=5.8, k1=6.9)
L(cross(SMALL[0], SMALL[1], 150), 7, 7.9, RED, 16, sfx="kick")

# ---------------------------------------------------------------- 书中观点（场景 5–6）

scene("多个条件，更难成", "思考，快与慢 · 书中观点", (1000, 2400, 0.85))
L(book(750, 2200, 380, 250), 0, 0.9, BLACK, 9, sfx="wood_low")
T("思考，快与慢", 750, 1960, 60, GREEN, k0=1, k1=2.5, sfx="pop")
L(kuai(1180, 2420, 0.65, "up"), 3, 3.8, RED, 9, sfx="wood_high")
L(man(1420, 2420, 0.65, "down"), 4, 4.8, BLUE, 9, sfx="wood_high")
T("两件都成 ≤ 只成一件", 1000, 2680, 72, RED, k0=5, k1=7.25, sfx="ding")
L(underline(660, 1340, 2750), 7.3, 8, RED, 8)

LI6, FR6, KK6 = (600, 4000), (1400, 3700), (1000, 4330)
scene("快快只看像不像", "书中观点 · 像不像", (1000, 3800, 0.85))
L(stick(*LI6, 0.7, "down", hair=True), 0, 0.9, BLACK, 9, sfx="wood_high")
T("琳达", LI6[0], 4070, 54, k0=1, k1=1.8, sfx="pop")
L(join(rect(*FR6, 300, 400, 12), stick(FR6[0], 3860, 0.5, "up", hair=True)), 2, 2.9, BLACK, 9, sfx="wood_high")
T("女权运动", FR6[0], 3970, 54, k0=3, k1=4, sfx="pop")
L(kuai(*KK6, 0.6, "up"), 4, 4.8, RED, 9, sfx="wood_high")
L(join(arrow((800, 3720), (1220, 3720), 0, 36), arrow((1220, 3720), (800, 3720), 0, 36)), 5, 5.7, RED, 8, sfx="pop")
T("像！", 1000, 3560, 90, RED, k0=6, k1=6.8, sfx="ding")
L(check(1150, 3560, 45), 7, 7.6, RED, 10, sfx="rim")

# ---------------------------------------------------------------- 书中实验：餐具（场景 7–8）

S1, S2 = (2330, 3900), (2970, 3900)
scene("多几件，反而便宜", "书中实验 · 两套餐具", (2650, 3800, 0.85))
L(join(rect(S1[0], 3800, 580, 620, 20), dishes(*S1, 3, 0.85, 1)), 0, 0.9, BLACK, 8, sfx="wood_high")
T("24件，全好", S1[0], 4160, 52, k0=1, k1=2.25, sfx="pop")
L(join(rect(S2[0], 3800, 580, 620, 20), dishes(*S2, 3, 0.85, 1)), 3, 3.9, BLACK, 8, sfx="wood_high")
L(cracks([(S2[0] - 220, 3835), (S2[0] - 110, 3810), (S2[0] + 115, 3835)], 0.9), 4, 4.6, RED, 7, sfx="rim")
T("40件，有几件破", S2[0], 4160, 50, k0=5, k1=6.75, sfx="pop")
L(tag(S1[0], 3600), 6.75, 7, RED, 7)
T("出价高", S1[0] - 15, 3600, 52, RED, k0=7, k1=7.8, sfx="ding")

D1, D2 = (2400, 5250), (2950, 5250)
scene("并排一比，就反了", "书中实验 · 放在一起比", (2650, 5200, 0.85))
T("放在一起", 2650, 4760, 64, k0=0, k1=1, sfx="pop")
L(join(dishes(*D1, 2, 0.75, 1), dishes(*D2, 3, 0.75, 1), P((2080, 5250), (3220, 5250)),
       cracks([(D2[0] - 170, 5185)], 0.8)), 1, 1.9, BLACK, 8, sfx="wood_high")
T("24件", D1[0], 5340, 52, k0=2, k1=2.8, sfx="pop")
T("40件", D2[0], 5340, 52, k0=3, k1=3.8, sfx="pop")
L(tag(D2[0], 4970), 4, 4.3, RED, 7, sfx="ding")
T("出价高", D2[0] - 15, 4970, 52, RED, k0=4.3, k1=5.1)
T("好的那些，它全都有", 2650, 5560, 58, k0=6, k1=8, sfx="pop")

# ---------------------------------------------------------------- 身边的例子（场景 9–10，示意）

scene("步骤越多，越像真的", "例子 · 一份方案", (1000, 5200, 0.85))
L(slide(640, 4950, 1), 0, 0.9, BLACK, 8, sfx="wood_high")
L(slide(1000, 5000, 3), 1, 1.9, BLACK, 8, sfx="pop")
L(slide(1360, 5050, 5), 2, 2.9, BLACK, 8, sfx="pop")
KK9 = (760, 5660)
L(kuai(*KK9, 0.6, "up"), 3, 3.8, RED, 9, sfx="wood_high")
L(face(*KK9, 0.6, "smile"), 3.8, 4)
L(bubble(1180, 5420, 300, 120, -1), 4, 4.5, RED, 8, sfx="pop")
T("就它了！", 1180, 5420, 56, RED, k0=4.5, k1=5.5)
T("写得越细，越信", 1000, 4720, 60, k0=6, k1=7.75, sfx="ding")

scene("脑补得越全，越信", "例子 · 脑补", (1000, 6600, 0.85))
L(phone(560, 6260), 0, 0.9, BLACK, 8, sfx="wood_high")
T("他没回消息", 1050, 6260, 60, k0=1, k1=2.25, sfx="pop")
L(arrow((1050, 6320), (1050, 6480), 0, 30), 2.3, 2.9, BLACK, 6)
T("对我有意见", 1050, 6570, 66, k0=3, k1=4.25, sfx="pop")
L(arrow((1050, 6640), (1050, 6830), 0, 40), 4.3, 4.9, RED, 16)
T("他要跳槽了", 1050, 6940, 84, RED, k0=5, k1=6.25, sfx="kick")
L(kuai(500, 7110, 0.55, "shrug"), 7, 7.8, RED, 9, sfx="wood_high")

# ---------------------------------------------------------------- 三招（场景 11–13，据书中思路整理）

scene("拆开，一条条问", "第一招 · 拆开问", (2650, 6600, 0.85))
T("① 每条单独成立吗？", 2650, 6200, 68, BLUE, k0=0, k1=2, sfx="pop")
T("没回消息", 2520, 6430, 60, k0=2, k1=3, sfx="pop")
L(check(2860, 6430, 40), 3, 3.6, GREEN, 10, sfx="ding")
T("对我有意见", 2520, 6660, 60, k0=4, k1=5.25, sfx="pop")
T("？", 2900, 6660, 70, RED, k0=5.3, k1=6.1)
T("要跳槽", 2520, 6890, 60, k0=6, k1=6.8, sfx="pop")
T("？", 2900, 6890, 70, RED, k0=7, k1=7.8, sfx="rim")
L(join(P((2200, 6545), (3100, 6545)), P((2200, 6775), (3100, 6775))), 6.8, 7, BLACK, 4)

STEPS = [2170 + i * 240 for i in range(5)]
scene("每步都要成", "第二招 · 连起来算", (2650, 8000, 0.85))
T("② 连起来算", 2650, 7600, 70, BLUE, k0=0, k1=1.5, sfx="pop")
L(join(*[rect(x, 7860, 190, 120, 14) for x in STEPS]), 2, 2.9, BLACK, 8, sfx="wood_high")
L(join(*[check(x, 7860, 32) for x in STEPS]), 3, 3.9, GREEN, 8, sfx="ding")
T("每一步 90%", 2650, 8040, 60, k0=4, k1=5.25, sfx="pop")
T("五步连起来 ≈ 59%", 2650, 8270, 76, RED, k0=6, k1=8, sfx="kick")

MAN13 = (1000, 8540)
scene("摆在一起再挑", "第三招 · 并排比", (1000, 8000, 0.85))
T("③ 并排比", 1000, 7600, 70, BLUE, k0=0, k1=1.25, sfx="pop")
L(doc(680, 7900, 300, 340, 5), 2, 2.9, BLACK, 8, sfx="wood_high")
L(doc(1320, 7900, 300, 340, 3), 3, 3.9, BLACK, 8, sfx="wood_high")
L(man(*MAN13, 0.55, "hold"), 4, 4.9, BLUE, 9, sfx="wood_high")
L(magnifier(MAN13[0] + 110, 8340, 40), 5, 5.6, BLUE, 8, sfx="ding")
T("放一起，再挑", 1000, 8170, 60, k0=6, k1=7.5, sfx="pop")

# ---------------------------------------------------------------- 片尾（场景 14，4 小节）：先拉远看全板，再推到评论区

FAR = (1800, 5000, 0.18)
END = (1800, 9420, 0.8)
scene("评论区聊聊", "评论区见", FAR, bars=4)
b.move(J(), 4, END, dur=1.1)
H(0, "cymbal", 0.5)
H(2, "ding")
L(rect(1800, 9330, 1100, 300, 30), 4, 4.9, BLACK, 8, sfx="wood_high")
L(kuai(1300, 9900, 0.6, "up"), 5, 5.8, RED, 9, sfx="pop")
T("你第一下选的哪个？", 1800, 9290, 76, RED, k0=6, k1=8, sfx="pop")
L(join(man(2300, 9900, 0.6, "down"), face(2300, 9900, 0.6, "smile")), 9, 9.8, BLUE, 9, sfx="wood_low")
T("下一讲：被骂完就变好，真是骂的功劳？", 1800, 9420, 44, k0=10, k1=14, sfx="wood_high")
b.hit(J(), 16, "kick", 0.55, "原曲最后一击")


def build():
    ep = episode(5, "linda", "琳达问题", "细节越多，为什么越容易信错？", ACC, b.shots,
                 [f"{BOOK}第14章 猜一下，汤姆的专业是什么？（Tom W's Specialty）（转述）",
                  f"{BOOK}第15章 琳达问题的社会效应（Linda: Less Is More）（转述）",
                  "中译本：胡晓姣、李爱民、何梦莹译，中信出版社 2012"],
                 "细节越多|越容易【信错】", SQUARE_SHOT,
                 ["书中观点均为转述：琳达问题中，多数人认为“银行柜员且参加女权运动”比“银行柜员”更可能，违背了概率的基本"
                  "规则——两个条件同时成立的可能性不会高于其中一个条件成立（第 15 章）；系统1 按“像不像”（代表性）判断，"
                  "细节越贴近刻板印象越显得可信（第 14–15 章）。上屏均为转述，不是逐字引文。",
                  "琳达的介绍（31 岁、单身、直率、很聪明、学哲学、关心歧视与社会公正、参加过反核游行）为书中实验材料，"
                  "白板上为节选转述；“31 岁”为书中数据。",
                  "餐具实验（奚恺元）：单独评价时，24 件完好的一套出价高于含破损的 40 件一套；放在一起比较时结果反过来，"
                  "书中称“少即是多”（第 15 章）。“24 件”“40 件”为书中数据；白板未写具体价格；“好的那些，它全都有”为通俗化转述。",
                  "大圈套小圈的图为对书中观点的通俗化示意；快快、慢慢为本系列对系统1、系统2 的拟人化示意。",
                  "方案越写越细、“他没回消息 → 对我有意见 → 他要跳槽了”的脑补链条为现实场景示意，不指向任何具体公司或个人。",
                  "三招（拆开一条条问、每步连起来算、并排比）为据书中思路整理的建议；五步各 90%、连起来约 59%"
                  "（0.9 的五次方 ≈ 0.59）为示意计算，不是书中数据。"],
                 tags="#判断 #概率")
    return b.attach(ep)
