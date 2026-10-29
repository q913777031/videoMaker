---
name: video-styles
description: 本仓库所有可用的视频风格与视频形式目录：11 种换皮主题（纸片、水墨、皮影、日漫、粒子、剪纸窗花、浮世绘、敦煌壁画、霓虹赛博、黑板粉笔、像素）和 6 种结构不同的形式（手机屏幕叙事、动态排版、3D 微缩场景、白板手绘、一镜到底长卷、漫画分格）。用户要求“换个风格/换个形式”“出样片对比”“用皮影/日漫/粒子/白板……做某系列”、或问“还有什么风格”时使用。
---

# 视频风格与形式目录

两类东西不要混淆：
- **主题（换皮）**：同一套阿德勒纸片引擎分镜（`adler.core` 的 Shot/Episode），只换背景、元素图层效果、人物画法、字体与整帧后期。构图与镜头语言不变，所以彼此看起来“同质化”。在系列 `build.py` 里一行 `install()` 切换，分镜不用改。
- **形式（换骨）**：构图、镜头语言、叙事载体都不同，需要各自的引擎或分镜写法。

## 一、主题（`themes/`，样片：`python3 -m themes.sample <名>`，基于系统之美 01 两段共 17 秒）

| 名 | 模块 | 要点 | 适合 |
|---|---|---|---|
| 纸片 | `themes.paper` | 引擎原样（兼容 `role=` 参数） | 通用、心理学 |
| 水墨 | `themes.shuimo` → `maoxuan.ink` | 宣纸远山、边缘晕染、毛笔大字、水墨人物（13 种 role 造型） | 国学、历史 |
| 皮影 | `themes.piying` | 烛光幕布、镂空皮件、侧脸、操纵杆 | 历史、寓言 |
| 日漫 | `themes.anime` | 描边平涂、大眼人物、切镜集中线、重拍冲击帧 | 情感、吐槽、星座 |
| 粒子 | `themes.particle` | 舞台粒子化，切镜聚合、重拍炸开；`install(B)` 同时改封面 | 科普、科技 |
| 剪纸窗花 | `themes.jianzhi` | 舞台内容映射为红纸色、镂空花点 | 节日、民俗 |
| 浮世绘 | `themes.ukiyoe` | 和纸、红日、青海波、靛蓝描边 | 日本相关 |
| 敦煌壁画 | `themes.dunhuang` | 土墙斑驳、矿物色、卷草边饰 | 传统文化 |
| 霓虹赛博 | `themes.neon` | 发光轮廓、透视网格、故障撕裂 | AI、科技 |
| 黑板粉笔 | `themes.chalk` | 粉笔质感、黑板擦痕 | 学习方法 |
| 像素 | `themes.pixel` | 8px 像素块、8 级减色、外描边 | 游戏、怀旧 |

人物造型：`Fig(..., role="worker" | "worker_f" | "boss" | "elder" | "sage" | "scholar" | "farmer" | "hero" | "soldier" | "merchant" | "youth" | "woman" | "immortal")`，由 `maoxuan/ink.py` 的水墨人物骨架绘制，皮影、日漫等主题在其上换上色与头部。

写新主题：图层类用 `themes/layer.py`（`make_layer` + `install`），整帧后期类用 `themes/post.py`（`render_layers` 透明底渲染 → 逐像素处理 → 补闪白与淡入淡出）。主题只能影响当前进程，旧系列逐字节不变。

## 二、形式（`styles/`，样片：`python3 -m styles.<名>`，基于 `styles/seg.py` 的 8 小节时间轴）

| 名 | 模块 | 要点 | 量产状态 |
|---|---|---|---|
| 手机屏幕叙事 | `styles.phone` | 整片是一部手机：工作群、系统提示、全屏通知、读书 App、备忘录 | 仅样片 |
| 动态排版 | `styles.kinetic` | 黑底荧光，无人物，文字砸地、翻牌、斜切、伸缩 | 仅样片 |
| 3D 微缩场景 | `styles.miniature3d` + `styles/miniature3d_web/` | three.js 黏土小岛，单相机连续运镜（复用 `ac3d` 的 Playwright 渲染器，约 0.7 秒/帧） | 仅样片 |
| 白板手绘 | `whiteboard/engine.py`（量产）、`styles.whiteboard`（样片） | 手握马克笔按拍点描线写字，相机在大白板上移动 | **已量产**，见 `whiteboard-explainer` skill |
| 一镜到底长卷 | `styles.scroll` | 长卷连续平移、四层视差、场景终态留在卷上 | 仅样片 |
| 漫画分格 | `styles.comic` | 斜切分格逐格推进、拟声字、跨格动作、翻页 | 仅样片 |

把“仅样片”的形式做成整讲：照 `whiteboard/engine.py` 的做法写一个引擎——镜头仍用 `core.Shot(1, 字幕, 标签)` 承载字幕、页眉、音效、闪白、抖动，画面由引擎的 `draw_frame(c, ep, T)` 接管，`install(B)` 里替换 `core.draw_frame`、`core.cover` 与 `B.episode_square`，就能沿用 `--sheet / --verify / --publish` 全套流程与交付格式（含 `--publish` 自动接频道片尾）。不走 `adler/build.py` 的形式，成片放进 `videos/` 后运行 `python3 -m brand.append <目录>` 接片尾。

## 三、出样片的约定

- 同一段内容、同一音轨对比，样片约 17 秒；先 `--stills` 看单帧再渲染视频。
- 发给用户时按编号 + 中文名命名（如 `05_粒子.mp4`），附一张“看点 / 适合题材 / 量产成本”对比表，并指出各自的已知瑕疵。
- 用户选定后再改系列 `build.py` 的 `install()` 并整套重出；不要在用户选定前改动已交付的 `videos/`。
