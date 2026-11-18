"""《资治通鉴》系列入口：白板手绘 + AI 旁白，竖屏 2:3（1080×1620），复用《丰田模式》的渲染与交付（fengtian/build.py）。

用法（同丰田）：
    FT_DRAFT_TTS=1 python3 -m zizhi.build 01 --sheet   # 排版草稿：只读配音缓存，缺的用占位音频（不起 IndexTTS2）
    flock <TTS 锁> python3 -m zizhi.redub 01             # 拿锁合成本讲配音（正文按屏连读 + 开场钩子句），只写缓存
    python3 -m zizhi.build 01 --sheet                    # 真实配音的关键帧检查图与排期表（out/zizhi/ep01/）
    python3 -m zizhi.build 01 --publish                  # 渲染并交付到 videos/zizhi/01_<概念>/（接片尾、封面、横屏封面、标题与话题）
    python3 -m zizhi.series                              # 系列层：合集.png、横屏封面_1080x1080.png、合集简介.txt

安全区、舞台、页眉、字幕条、混音（开场只留砸字音效）、封面版式都与丰田相同；本文件只把分镜包、输出目录、讲目换成本系列的。
"""
from fengtian import build as B

B.PKG = "zizhi"
B.OUT = B.ROOT / "out" / "zizhi"
B.VIDEOS = B.ROOT / "videos" / "zizhi"
B.MODS = {"01": "ep01_caide", "02": "ep02_lixin", "03": "ep03_zhishang", "04": "ep04_jiangxiang", "05": "ep05_yuefa", "06": "ep06_sanburu", "07": "ep07_xiaogui", "08": "ep08_fenshu", "09": "ep09_sangu", "10": "ep10_quanxue", "11": "ep11_youzhi", "12": "ep12_toubian", "13": "ep13_yongren", "14": "ep14_jianting", "15": "ep15_renjing"}
MODS = B.MODS

if __name__ == "__main__":
    B.main()
