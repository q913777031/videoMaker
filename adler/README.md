# 阿德勒心理学 10 讲（无旁白竖屏科普动画）

```bash
python3 fetch_assets.py              # 只需其中的字体
python3 -m adler.build               # 渲染全部 10 期到 out/adler/epXX/
python3 -m adler.build 03 07         # 只渲染指定期
python3 -m adler.build 03 --sheet    # 逐镜联系表 out/adler/stills/sheet_ep03.png（每镜取退场前的完整画面）
python3 -m adler.build 03 --still 17.5   # 单帧
python3 -m adler.build 03 --no-video     # 只出分轨、封面与文档
```

每期 1080×1920、30fps、92.6 秒，配乐统一为 `music/bgm.m4a`；4 核机器每期约 4 分钟。
输出：`阿德勒XX_概念.mp4`、`cover.png`、`bgm_track.wav` / `sfx_track.wav`、`cue_sheet.csv`（每个音效的实测拍序号、重音值与音画偏差帧数）、`文案与出处.md`。

## 卡点规则

- 时间轴建立在 `bgm.detect()` 的实测拍点上（`core.BEATS`，结果按 BGM 内容哈希缓存在 `.cache/adler_beats.json`）。
- 镜头长度以小节（4 个实测拍点）计，每期 42 小节，正好到原曲最后一击；原曲在 90 秒处硬截断，之后接约 3 秒混响尾音。
- 镜头边界应覆盖原曲段落边界小节 8 / 20 / 24 / 34 / 38 / 40（第 8 小节 = 17.14 秒的 drop，每期在这里落版概念名）。
- 元素入场、关键帧、音效都写“镜头内第 k 拍”。带音效的动作必须是整数拍（取实测拍点时间），否则构建时报错；
  小数拍只用于无音效的画面动作（在相邻实测拍点间插值）。
- 入场方式分两类：`pop / rise / fade / grow / draw / slam / unfold / none` 从该拍开始运动（起音即撞击）；
  `drop / slide_l / slide_r / slide_u` 在该拍落定，不能放在镜头第 0 拍。
- 音效用 `engine/perc.py` 合成，按起音峰值提前放置；原曲该拍已有重底鼓时低音鼓自动换高通版本。

## 写一期

每期一个模块 `adler/epXX_*.py`，`build()` 返回 `Episode`。镜头 `Shot(小节数, 字幕, 角标, 元素列表, ...)`：

| 参数 | 说明 |
|------|------|
| `text` | 主字幕，`|` 换行，`【】` 高亮（荧光笔底色）；每行不超过约 12 个汉字，最多 2 行 |
| `tag` | 右上角角标：`情境演绎` / `机制示意` / `阿德勒原著` / `阿德勒原著 · 大意` / `岸见一郎阐释` / `研究证据` / `常见误解` / `小练习` |
| `els` | 声明式元素：`Fig` 人物、`Icon` 图标、`Card` 文字卡、`Bubble` 气泡、`Arrow` 箭头、`Label` 标签、`Big` 大字、`Txt` 小字、`Custom` 自定义 |
| `draw` / `over` | `draw(g)` 画在元素之下、`over(g)` 画在元素之上；`g.t` 为镜头内秒数，`g.b(k)` 第 k 拍时刻，`g.p(k, dur)` 从第 k 拍起的进度 |
| `hits` | 额外音效 `(拍, 音色, 增益, 说明)` |
| `text_beat` | 字幕出现的拍（默认 1） |
| `cut` | 与上一镜硬切（上一镜不退场），用于人物位置连续的镜头 |

元素公共参数：`at` 入场拍、`out` 退场拍、`enter` 入场方式、`sfx` 入场音效、`note` 动作说明（写入卡点表）、
`moves=[(拍, {属性: 值, "sfx": 音色, "note": 说明})]` 关键帧（0.45 秒缓动；人物改 `x` 时自动迈步）。
人物姿势见 `kit.POSES`，表情 `mood`：calm / smile / happy / sad / worried / open / surprised / flat / angry。

构建时会检查：总小节数、段落边界、音效拍是否为整数、落定型入场是否越过镜头起点；`--sheet` 同时打印字幕阅读窗警告
（稳定显示 ≥ max(2 秒, 汉字数 / 4.5)，含数字或英文另加 1 秒，研究卡至少 4.5 秒）。
