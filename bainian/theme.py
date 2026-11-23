"""《百年孤独》每讲一个样式（字段同 fengtian/theme.py 的 THEMES，由 fengtian.theme.finish 补齐派生色）。

马孔多的颜色：土坯墙的赭红、杏仁树的绿、黄蝴蝶与黄花雨的黄、加勒比海的蓝、羊皮卷的牛皮色、雨季的灰。
相邻两讲纸色、纹理、主题色、页眉、开场钩子、转场都不同（纹理都用 fengtian/theme.py board_bg 里现成的）。
"""
from fengtian import theme as FT

THEMES = {
    "01": dict(name="牛皮纸赭红", acc="#A3381E", paper="#E6CFA6", pattern="kraft", pat="#B99A6B",
               header="stamp", hook="bn_pigtail", move="pullpush", move_s=1.4),
    "02": dict(name="淡蓝点阵", acc="#1F4E8C", paper="#E2EAF2", pattern="dots", pat="#9FB1C6",
               header="tab", hook="bn_forget", move="pan", move_s=1.35),
    "03": dict(name="淡粉信纸", acc="#7A1F4A", paper="#F8E6E4", pattern="ruled", pat="#E8B9B5", margin=None,
               header="circle", hook="bn_push", move="swing", move_s=1.3),
    "04": dict(name="墨绿黑板", acc="#F2C94C", paper="#22382F", pattern="chalk", pat="#FFFFFF", dark=True,
               header="bar", hook="bn_crowd", move="tilt", move_s=1.4),
    "05": dict(name="杏黄方格", acc="#1E5F74", paper="#F6E7C8", pattern="grid", pat="#E0C48E", grid=90,
               header="pill", hook="bn_again", move="drop", move_s=1.3),
    "06": dict(name="宣纸赭石", acc="#8C4A16", paper="#F3ECDD", pattern="xuan", pat="#BFA67C",
               header="stamp", hook="bn_fog", move="arc", move_s=1.45),
    "07": dict(name="淡绿方眼", acc="#B8860B", paper="#E4EFE2", pattern="graph", pat="#A9C9A5", grid=44,
               header="circle", hook="bn_control", move="pullpush", move_s=1.35),
    "08": dict(name="绢本藕荷", acc="#6A3D8C", paper="#F1E8EE", pattern="silk", pat="#B79AB0",
               header="tab", hook="bn_eyes", move="swing", move_s=1.3),
    "09": dict(name="雨季石墨", acc="#7FC8E8", paper="#272B33", pattern="dots", pat="#5A6372", grid=80, dark=True,
               header="bar", hook="bn_nothing", move="wipe", move_s=1.05),
    "10": dict(name="羊皮卷", acc="#8E2A1C", paper="#EFDDB8", pattern="xuan", pat="#B89766",
               header="stamp", hook="bn_written", move="tilt", move_s=1.4),
}


def get(nn):
    return FT.finish(dict(THEMES[nn]))
