"""水墨长卷科普《端午节是怎么来的？》：复用 ac3d 的构建流程（实测拍点时间轴、配乐 + 打击乐、逐帧渲染、混流核验）。

用法与 ac3d.build 相同：
    python3 -m duanwu.build                 # 完整成片 out/duanwu/
    python3 -m duanwu.build --stills 3,18   # 静帧 out/duanwu/stills/
    python3 -m duanwu.build --audio         # 只出音频分轨与卡点表
"""

from pathlib import Path
from types import SimpleNamespace

from ac3d import build as B
from ac3d.story import load

HERE = Path(__file__).resolve().parent
STORY = SimpleNamespace(**load(HERE / "storyboard.json"))


def main():
    B.run(STORY, HERE / "web", B.ROOT / "out" / "duanwu", "duanwu/web/index.html", extra={"quiz": STORY.DATA["quiz"]})


if __name__ == "__main__":
    main()
