# 夜色像素风（Remotion）

画面在 [weilanx-claude-videos](https://github.com/Azure12355/weilanx-claude-videos) 工程里渲染，这里放这些：

- `kit.py`：各期通用的拍点时间表（`Plan`）与混音封装（`finish`）。
- `denial.py`：ep53《我们为什么假装不会死》的时间表与混音（`--plan` / `--mix`，用法同下）。

- `umbrella.py`：ep52《一把伞的雪夜》的时间表与混音。`--plan <episode目录>` 用 `engine/bgm.py` 的 `detect()` 测 `music/bgm.m4a` 的实测拍点，把所有画面节点和音效吸附到拍点上，写出 `timeline.json`；`--mix <无声成片> <输出目录> <episode目录>` 用 `engine/perc.py` 合成打击乐（起音峰值对齐撞击帧），混音、归一响度、限真峰值，重编码为 yuv420p 成片并写卡点表与核验。
- `remotion/`：放进 weilanx 工程的源码快照——`library/night-pixel/`（素材包）、`library/previews/NightPixelDemo.tsx`、`episodes/ep52-umbrella/`、`tests/night-pixel.test.ts`、`styles/夜色像素风/`（风格配方卡），`Root.tsx.diff` 是注册 `library-night-pixel` 和 `ep52-umbrella` 的改动。

重做一遍：

```bash
# 1. 把 remotion/ 下的文件按目录放进 weilanx-claude-videos 的 src/ 、tests/library/ 、styles/我的风格/，并应用 Root.tsx.diff
python3 -m nightpixel.umbrella --plan <weilanx>/src/episodes/ep52-umbrella
# 2. 在 weilanx 工程里渲染无声成片
npx remotion render src/index.ts ep52-umbrella silent.mp4 --muted
# 3. 回到本仓库混音
python3 -m nightpixel.umbrella --mix silent.mp4 out/umbrella <weilanx>/src/episodes/ep52-umbrella
```
