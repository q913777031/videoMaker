"""《百年孤独》系列入口：白板手绘 + AI 旁白，竖屏 2:3（1080×1620），复用《丰田模式》的渲染与交付（fengtian/build.py），做法同《资治通鉴》（zizhi/build.py）。

用法：
    FT_DRAFT_TTS=1 python3 -m bainian.build 01 --sheet   # 排版草稿：只读配音缓存，缺的用占位音频（不起 IndexTTS2）
    flock <TTS 锁> python3 -m bainian.redub 01             # 拿锁合成本讲配音（正文按屏连读 + 开场钩子句），只写缓存
    python3 -m bainian.build 01 --sheet                    # 真实配音的关键帧检查图与排期表（out/bainian/ep01/）
    python3 -m bainian.build 01 --publish                  # 渲染并交付到 videos/bainian/01_<概念>/（接片尾、封面、横屏封面、标题与话题）
    python3 -m bainian.series                              # 系列层：合集.png、横屏封面_1080x1080.png、合集简介.txt

安全区、舞台、页眉、字幕条、混音（开场只留砸字音效）、封面版式都与丰田相同；本文件只把分镜包、输出目录、讲目换成本系列的。
"""
from fengtian import build as B

B.PKG = "bainian"
B.OUT = B.ROOT / "out" / "bainian"
B.VIDEOS = B.ROOT / "videos" / "bainian"
B.MODS = {"01": "ep01_ice", "02": "ep02_label", "03": "ep03_bandage", "04": "ep04_chalk", "05": "ep05_names", "06": "ep06_eyes", "07": "ep07_butterfly", "08": "ep08_sheets", "09": "ep09_rain", "10": "ep10_parchment"}
MODS = B.MODS

if __name__ == "__main__":
    B.main()
