"""弗洛伊德《梦的解析》单讲入口：复用《丰田模式》的构建流程（fengtian/build.py：竖屏 2:3 白板手绘 + AI 旁白、安全区、配乐延长卡点、混音、封面、交付）。

用法与 fengtian.build 相同：
    python3 -m mengjie.build 01 --sheet      # 关键帧 + 封面样张（out/mengjie/ep01/）
    python3 -m mengjie.build 01              # 渲染成片
    python3 -m mengjie.build 01 --publish    # 渲染并交付到 videos/mengjie/01_梦的解析/（接频道片尾、封面、标题与话题、横屏封面）
草稿排版（配音没合成完时）：FT_DRAFT_TTS=1 python3 -m mengjie.build 01 --sheet
"""

from fengtian import build as B

B.PKG = "mengjie"
B.OUT = B.ROOT / "out" / "mengjie"
B.VIDEOS = B.ROOT / "videos" / "mengjie"
B.MODS = {"01": "ep01_dream", "02": "ep02_wish", "03": "ep03_disguise", "04": "ep04_material", "05": "ep05_condense",
          "06": "ep06_displace", "07": "ep07_picture", "08": "ep08_revision", "09": "ep09_typical", "10": "ep10_guard",
          "11": "ep11_nightmare", "12": "ep12_irma", "13": "ep13_today"}

if __name__ == "__main__":
    B.main()
