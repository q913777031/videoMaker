# 国风 3D 科普短片：《空调频繁开关省电，还是一直开着省电？》

```bash
python3 fetch_assets.py                     # 字体（含马善政毛笔楷书）
(cd ac3d && npm install)                    # three.js
python3 -m ac3d.build                       # 完整成片 → out/ac3d/
python3 -m ac3d.build --stills 3.2,17.5     # 静帧 → out/ac3d/stills/
python3 -m ac3d.build --stills 20 --only principle   # 只构建指定镜头，启动更快
python3 -m ac3d.build --audio               # 只出音频分轨与卡点表
```

1080×1920、30fps、92.6 秒；配乐为 `music/bgm.m4a`，按 `bgm.detect()` 实测拍点卡点；打击乐为 `engine/perc.py` 合成的中国打击乐
（堂鼓、大鼓、大锣、小锣、铙钹、梆子、木鱼、编钟）。画面是真 3D：three.js 在无头 Chromium 中用软件 WebGL（SwiftShader）逐帧渲染，
4 核机器约 0.3 秒/帧。

## 结构

| 文件 | 职责 |
|------|------|
| `storyboard.json` | 分镜唯一数据源：镜头小节数、角标、转场、字幕（拍数）、动作与音效（拍数）、出处与核查说明 |
| `story.py` | 读取 storyboard.json |
| `build.py` | 实测拍点 → `web/timeline.json`；配乐 + 音效混音（-14 LUFS）；调用渲染器；混流；卡点表、文案与出处、核验 |
| `render.cjs` | Playwright 逐帧截图（本地静态服务器加载页面），4 个页面并行，分段编码后拼接 |
| `web/engine.js` | 渲染器、灯光、材质（陶土 / 漆器 / 金属 / 墨线描边）、画布纹理（水墨远山、祥云、文字）、相机关键帧、震动、泼墨转场 |
| `web/props.js` | 道具库（见下） |
| `web/main.js` | 镜头调度、DOM 字幕与页眉、角标、书法大字、朱砂印章、特效层 |
| `web/shots/*.js` | 每个镜头一个模块：`export function <name>({ ui, info })` 返回 `{ scene, camera, update(lt, t), fx? }` |

## 时间约定

- `update(lt, t)`：`lt` 为镜头内秒数，`t` 为全片秒数。所有画面必须是 `t` 的纯函数（多页面并行渲染、任意跳帧）。
- 动作时刻取自时间轴：`cue('镜头名.动作名')` 返回全片秒数（来自 storyboard 的拍数，整数拍即实测拍点）；
  `P(t, '镜头名.动作名', 时长)` 为从该时刻起的缓动进度；`since(t, name)` 为距该时刻的秒数。
- 带音效的动作，画面撞击要发生在 cue 时刻那一帧（起势动作要提前开始，在 cue 时刻落定 / 撞上）。
- 转场：`transition: "ink"` 时，镜头边界前后各 0.3 秒有泼墨遮挡，拍点上完全遮住。

## 版式安全区（竖屏）

- 页眉：y 160–290（左上系列名与书法标题，右上角标），不放关键画面。
- 字幕：y 1330–1520（主字幕两行），小字在 y≈1262；关键 3D 内容放在 y 330–1250，字幕区可以有背景但不要有需要阅读的东西。
- 底部 y>1550 会被平台界面遮挡，只放地面、背景。

## 道具（`web/props.js`）

`chineseRoom` 国风房间（月洞窗、冰裂纹窗棂）· `moonWindowProp` · `cutawayHouse` 剖面瓦屋（`userData.roof` 可抬起）·
`acIndoor` 空调室内机（`userData.set(导风板开度, 显示文字, 是否开机)`）· `acOutdoor` 室外机（`userData.fan` 转动）· `remote` 遥控器 ·
`thermometer`（`set(0–1)`）· `particles` 热流粒子（`update(t, 密度, 路径函数, 速度)`）· `coldAir` 冷气流（`set(强度, t)`）·
`meter` 电表（`set(转角, 读数)`）· `coin` / `coinStack` 铜钱与钱串柱（`set(枚数)`）· `abacus` 算盘（`set(列, 值, 进度)`）·
`steelyard` 杆秤（`set(倾角, 秤砣位置)`）· `seal` 3D 印章 · `scroll` 卷轴（`set(展开)`）· `plaque` 匾额 ·
`bambooSlips` 竹简（`set(展开)`）· `incense` 香炉线香（`set(燃烧进度, t)`）· `lineChart3D` 3D 折线图（`set(第 i 条, 进度)`）·
`lantern` 灯笼 · `cloud3d` 祥云（engine）· `clayFigure` 泥人（`pose({walk, amp, armL, armR, nod, tilt})`）· `mountainBackdrop` 远山背景板。

DOM 界面（`ui`，镜头私有）：`ui.add(id, html, css)` / `ui.set(id, {o, x, y, s, r, html})`、
`ui.brushText(id, 文字, css)` / `ui.brush(id, k)` 书法大字逐字落笔、`ui.sealStamp(id, 文字, css)` / `ui.stamp(id, dt)` 朱砂印章砸章。
