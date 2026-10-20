"""03 人格面具：你每天戴着哪张脸？"""

from engine.gfx import clamp01, ease_out

from adler import kit as K
from adler.core import Big, Bubble, Card, Custom, Episode, Fig, Icon, Label, Shot, Txt, end_shot

from . import art as A

ACC = A.TEAL
GROUND = A.GROUND_Y
REFS = ["Jung, C. G. (1928). The Relations between the Ego and the Unconscious. In Two Essays on Analytical Psychology, CW 7.",
        "Jung, C. G. (1959). The Archetypes and the Collective Unconscious, CW 9i."]


def masked(c, g, el_t, d):
    """人物与举在脸前的面具；d['off'] 为面具挪开的程度（0 戴着，1 放下）。"""
    off = d.get("off", 0)
    K.figure(c, 0, 0, 340, "stand", d.get("color", K.HERO), K.SKIN, 1, 1, d.get("mood", "calm"), "short")
    A.mask(c, 40 + 160 * off, -300 + 120 * off, 120, K.PAPER, d.get("mmood", "smile"), 1, -10 * off, handle=True)


def build() -> Episode:
    shots = [
        Shot(3, "上班一个样|回家又是一个样", "情境演绎", [
            Fig(300, GROUND, 340, at=0, pose="stand", mood="smile", hair="short", prop=None,
                moves=[(6, dict(pose="relax", mood="calm"))]),
            Icon("brief", 300, 960, 110, color=K.DARK, at=0, enter="pop", out=6),
            Icon("house", 800, 880, 260, color=K.HERO, at=4, sfx="wood_low", note="回到家"),
        ], draw=A.ground, hits=[(6, "rim", 0.8, "放下公文包，换成放松的样子")], note="同一个人：上班的笑脸与回家的放松"),
        Shot(3, "见老板、见朋友、见家人|你是同一个人吗？", "情境演绎", [
            Bubble("您说得对", 230, 700, 38, at=0, sfx="wood_high"),
            Bubble("哈哈走起", 540, 640, 38, at=2, sfx="wood_high", gain=0.85),
            Bubble("别管我", 850, 700, 38, at=4, sfx="wood_high", gain=0.75),
            Fig(540, GROUND, 320, at=0, enter="none", pose="shrug", mood="worried", hair="short"),
        ], draw=A.ground, note="同一个人对不同的人说出不同的话"),
        Shot(2, "荣格把这层外壳|叫作——", "荣格的视角", [
            Custom(lambda c, g, t, d: A.mask(c, 0, 0, 240, K.PAPER, "flat", clamp01(t / 0.5)), x=540, y=760, at=0),
        ], text_beat=0, hits=[(4, "rim", 0.8, "面具浮现")], note="一张空白面具浮现"),
        Shot(4, "为了适应社会|戴上的那张脸", "荣格原著 · 大意", [
            Big("人格面具", 540, 600, 150, at=0, sfx="kick", sub="Persona", note="概念落版（音乐 drop）"),
            Custom(lambda c, g, t, d: A.mask(c, 0, 0, 200, K.PAPER, "smile"), x=540, y=940, at=2, enter="pop", sfx="wood_low"),
        ], note="drop 处“人格面具”砸下"),
        Shot(4, "Persona 原指|古代演员戴的面具", "词源", [
            Custom(lambda c, g, t, d: A.mask(c, 0, 0, 220, K.PAPER, "smile", 1, -8), x=360, y=760, at=0, sfx="wood_low"),
            Custom(lambda c, g, t, d: A.mask(c, 0, 0, 220, K.mix(K.INK3, K.PAPER, 0.5), "flat", 1, 8), x=720, y=760, at=2,
                   sfx="wood_low"),
            Txt("拉丁语 persona：戏剧面具", 540, 1060, 34, at=4, font="sans_medium", color=K.INK2),
        ], note="两张戏剧面具；小字说明拉丁语词源"),
        Shot(4, "面具不是虚伪|它帮我们和人相处", "荣格的视角", [
            Custom(masked, x=340, y=GROUND, at=0, enter="rise"),
            Fig(760, GROUND, 330, at=2, color=K.OTHER2, pose="give", mood="smile", face=-1, sfx="clap", note="对方回应"),
        ], draw=A.ground, note="戴面具的人与他人友好交流"),
        Shot(4, "问题在于：|把面具当成了自己", "常见误区", [
            Custom(masked, x=340, y=GROUND, at=0, enter="none", mood="flat"),
            Icon("mirror", 780, 820, 260, color=ACC, at=2, sfx="wood_low", note="镜子"),
            Custom(lambda c, g, t, d: A.mask(c, 0, 0, 110, K.PAPER, "smile", clamp01(t / 0.4), handle=False), x=780, y=800,
                   at=6, sfx="rim", note="镜中只剩面具"),
        ], draw=A.ground, note="照镜子时，镜子里只剩下面具"),
        Shot(2, "只剩头衔和角色|就会觉得空", "常见误区", [
            Card("经理 · 好妈妈 · 学霸", 540, 760, 44, at=0, rot=-2, sfx="wood_low"),
        ], text_beat=0, note="一张写满头衔的卡"),
        Shot(2, "荣格称之为|与面具“认同”", "荣格原著 · 大意", [
            Label("identification with the persona", 540, 760, 34, at=0, fill=ACC, sfx="wood_high"),
        ], text_beat=0, note="术语卡"),
        Shot(3, "面具戴得太牢|下班也摘不下来", "情境演绎", [
            Custom(masked, x=540, y=GROUND, at=0, enter="rise", mood="worried"),
            Icon("house", 860, 880, 220, color=K.HERO, at=2, sfx="wood_low"),
        ], draw=A.ground, hits=[(6, "rim", 0.7, "试图摘下面具")], note="回到家仍然戴着面具"),
        Shot(3, "试试：|一天里放下几次面具", "小练习", [
            Custom(lambda c, g, t, d: masked(c, g, t, dict(d, off=ease_out(clamp01(g.since(4) / 0.6)), mood="smile")),
                   x=540, y=GROUND, at=0, enter="none"),
        ], draw=A.ground, hits=[(4, "clap", 0.8, "面具放下")], note="面具慢慢放下，露出放松的脸"),
        Shot(2, "在信任的人面前|做回真实的样子", "小练习", [
            Fig(380, GROUND, 320, at=0, pose="hug", mood="happy", hair="short"),
            Fig(700, GROUND, 320, at=0, pose="hug", mood="happy", color=K.OTHER3, face=-1, hair="bun"),
        ], draw=A.ground, text_beat=0, hits=[(4, "wood_high", 0.7, "拥抱")], note="两人拥抱"),
        Shot(2, "面具可以有|别忘了面具后面的人", "荣格的视角", [
            Custom(lambda c, g, t, d: A.mask(c, 0, 0, 180, K.PAPER, "smile", 1, -14), x=380, y=760, at=0),
            Fig(700, GROUND, 320, at=0, pose="stand", mood="smile", hair="short"),
        ], draw=A.ground, text_beat=0, note="面具在左，真实的人在右"),
        Shot(2, "下一讲：|面具背后，被藏起来的“阴影”", "下一讲", [
            Custom(lambda c, g, t, d: A.shadow_self(c, 0, 0, 300, ease_out(clamp01(t / 1)), 1), x=540, y=GROUND, at=0),
            Fig(540, GROUND, 300, at=0, enter="none", pose="stand", mood="calm", hair="short"),
        ], draw=A.ground, text_beat=0, hits=[(4, "tom", 0.7, "影子拉长")], note="预告第 04 讲：阴影"),
        end_shot(REFS, "04 阴影：你最讨厌的人，像不像你？"),
    ]
    return Episode(3, "persona", "人格面具", "你每天戴着哪张脸？", ACC, shots, refs=REFS,
                   publish_title="你每天戴着哪张脸？｜荣格心理学03 人格面具",
                   hashtags="#荣格 #心理学 #人格面具 #persona",
                   cover_title="你每天戴着|【哪张脸】？", cover_sub="荣格的人格面具", cover_shot=5, cover_t=5.0,
                   notes=["人格面具见《分析心理学两论》中《自我与无意识的关系》（1928），荣格指出 persona 是个人与社会之间的妥协。",
                          "“与面具认同”（identification with the persona）的危险出自同一文。"]).build()
