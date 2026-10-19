# 3D 科普短片：《出门一会儿，空调关不关？》

```bash
python3 fetch_assets.py                     # 字体
(cd ac3d && npm install)                    # three.js
python3 -m ac3d.build                       # 完整成片 → out/ac3d/
python3 -m ac3d.build --stills 3.2,17.5     # 静帧 → out/ac3d/stills/
python3 -m ac3d.build --audio               # 只出音频分轨与卡点表
python3 ac3d/sheet.py 联系表.png 帧1.png 帧2.png …   # 静帧拼联系表
```

1080×1920、30fps、92.6 秒；配乐为 `music/bgm.m4a`，按 `bgm.detect()` 实测拍点卡点；打击乐为 `engine/perc.py` 合成
（低音鼓、军鼓边击、低音通鼓、拍手、木块、沙锤）。three.js 在无头 Chromium 中用软件 WebGL（SwiftShader）逐帧渲染，4 核约 0.3–0.8 秒/帧。

## 结构

| 文件 | 职责 |
|------|------|
| `storyboard.json` | 分镜唯一数据源：镜头小节数、角标、字幕（拍数）、动作与音效（拍数）、出处与核查说明 |
| `story.py` | 读取 storyboard.json |
| `build.py` | 实测拍点 → `web/timeline.json`；配乐 + 音效混音（-14 LUFS）；调用渲染器；混流；卡点表、文案与出处、核验 |
| `render.cjs` | Playwright 逐帧截图（本地静态服务器加载页面），4 个页面并行，分段编码后拼接 |
| `web/engine.js` | 渲染器、材质与几何体工具、缓动、时间轴与 `cue()` |
| `web/room.js` | 客厅剖面与道具：室内机、室外机、电视（画布屏幕）、挂钟、人物、遥控器、钥匙、热粒子、冷气带 |
| `web/film.js` | 整片唯一场景：状态（开关机、压缩机、室温、耗电）、人物动作、遥控器、电视画面、相机关键帧、DOM 标签 |
| `web/main.js` | 页眉、角标、字幕与小字、首尾淡入淡出 |

## 约定

- 整片只有一个场景和一台相机，镜头之间靠连续运镜衔接，不做硬切；相机关键帧写在 `film.js` 的 `keys_`（全片秒数）。
- 所有画面是全片时间 `t` 的纯函数（多页面并行渲染、任意跳帧）；需要累积的量（风扇转角、粒子流相位、平滑开关）
  在启动时按 1/60 秒网格预积分（`grid()`）。
- 动作时刻取自时间轴：`cue('镜头名.动作名')` 返回全片秒数（来自 storyboard 的拍数，整数拍即实测拍点）。
  带音效的动作，画面撞击要落在 cue 那一帧（弹出、按键、柱子落定）。
- 版式：页眉 y 160–290；耗电条 y≈352；字幕白底板 y 1330–1520，小字 y≈1576；关键 3D 内容放在 y 330–1300。
