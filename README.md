# videoMaker

用代码生成短视频：Skia 逐帧绘制动效 + 离线 TTS 配音 + 固定 BGM 自动卡点 + 程序化音效 + FFmpeg 合成。

## 竖屏科普短视频：幸存者偏差（Remotion）

《他连续赢了10次，然后开始教你成功》，约 66 秒，见 [`survivor/`](survivor/README.md)；成片与字幕在 `survivor/deliverables/`。

## 竖屏短视频：《设计你的人生》

```bash
pip install -r requirements.txt
python3 fetch_assets.py                       # 下载字体、3D Emoji、Kokoro TTS 模型（约 800MB，均不入库）
python3 dyl_short.py out/designing_your_life_short.mp4
```

输出 1080×1920、30fps、约 86 秒的 9:16 竖屏视频，以及同目录下的封面图 `cover.png`。
4 核机器上首次渲染约 6 分钟（含 TTS 合成），之后只改画面时约 5 分钟（旁白有缓存）。

系统依赖：FFmpeg（带 libx264）、`libegl1`（skia-python 需要）。

### 内容结构

斯坦福课程开场 → 重新定义问题 → 三个方法（好时光日志 / 奥德赛计划 / 最小原型）各配真实场景
→ 情绪高潮 → 评论区互动。

### 引擎（`engine/`）

| 模块 | 职责 |
|------|------|
| `gfx.py` | 缓动、字体回退、逐字动画文字（弹出/砸入/上浮）、3D Emoji、对话气泡、电池、粒子、光芒、彩带、故障效果 |
| `audio.py` | ZipVoice / Kokoro 离线 TTS（带缓存）、合成音效（呼啸/冲击/上升/心跳/碎裂等）、闪避混音、-14 LUFS 响度标准化 |
| `bgm.py` | 加载项目 BGM、节拍网格分析（BPM / 强拍 / drop）、视频时间轴上的吸附与配乐截取 |
| `timeline.py` | 场景 / 台词 / 事件模型、按旁白长度与节拍网格自动排时（卡点）、配乐闷音/放开自动化、镜头震动与推拉、转场、逐字点亮字幕、4 进程并行渲染 |

- **音画同步**：每句旁白单独合成，动画与音效都锚定到"某句读到某个词"的时刻（`w(x, 句序号, "关键词")`）。
- **背景音乐**：所有视频统一使用 `music/bgm.m4a`（约 113 BPM），引擎自动分析节拍并卡点：
  - 场景切换落在半小节线上；`Video(..., drop_at="场景名")` 让该场景从小节线开始并与音乐 drop（能量跃升最大处）对齐
  - 每句的重音（boom/impact 落在拍上，其余音效或句首落在半拍上）吸附到最近网格点，最多压缩上一停顿 60% 或推迟一个网格单位
  - 每个强拍有轻微推镜脉冲；`music` 表可让某段配乐闷音（`low`）并在关键词处瞬间放开（`full`）
  - 换 BGM：替换 `music/bgm.m4a`，或传 `Video(..., bgm_path="其他文件")`，节拍会重新分析
- **性能**：平滑背景层以 1/4 分辨率绘制后用 OpenCV 放大，直接写入帧缓冲。
- **配音**：默认用 ZipVoice（零样本、韵律接近真人）。以 Kokoro 合成的一句话作音色提示，不涉及任何真人声音；成片语音识别错误率约 1%。

### 修改内容

- 改旁白或节奏：编辑 `dyl_short.py` 的 `SCENES`，每句是 `Line(文本, 语速倍率, 句后停顿)`，`【】` 标记字幕高亮词
- 调配乐：`dyl_short.py` 的 `MUSIC` 为 `(场景名, 句序号, "low" | "full"[, 关键词])`，`drop_at` 指定与 drop 对齐的场景
- 加音效：在场景的 `events` 里加 `(类型, 句序号, 关键词, 偏移秒)`，类型见 `engine/timeline.py` 的 `EVENT_FX`
- 换音色：`Video(..., voice="zv_001")`（ZipVoice 女声），或 `zv_009`、`zf_001` 等，可选值见 `engine/audio.py` 的 `VOICES`

## 科普动画：《为什么人会信星座？》

```bash
python3 zodiac.py out/zodiac            # 竖屏 + 横屏成片、封面、分轨、卡点表、文案
python3 zodiac.py out/zodiac --no-video # 只出音频分轨、封面与文档
```

无旁白、黑金风格，约 92.6 秒（原曲 90 秒处硬截断，最后一击后接约 3 秒混响尾音自然淡出）。

- 卡点：`bgm.detect()` 用 librosa 动态规划节拍跟踪检测逐拍时间、起音强度（全频 / 低频 / 中高频）、小节位置与段落边界；
  `CUES` 中每个动作写一个参考时间，由 `beat()` 吸附到最近的实测拍点（偏差 >0.12 秒直接报错，不伪造）
- 音效：`engine/perc.py` 合成低音鼓、军鼓边击、木块、沙锤、框鼓、低音通鼓、邦戈鼓、拍手、轻柔吊镲；按起音时间提前放置，峰值落在拍点上；
  音乐在该拍已有重底鼓时低音鼓自动换高通版；配乐对重击做 ≤3 dB 的平滑闪避
- 输出（`out/zodiac/`）：`zodiac_portrait_1080x1920.mp4`、`zodiac_landscape_1920x1080.mp4`、`cover_*.png`、
  `bgm_track.wav` / `sfx_track.wav`（两轨相加即限幅前混音）、`cue_sheet.md` / `.csv`、`copy_and_references.md`

## 无声知识短视频（认知偏差系列 04–08）

```bash
pip install -r requirements.txt
python3 fetch_assets.py            # 字体（其余资源只有配音版需要）
python3 make_videos.py             # 渲染全部 5 期到 videos/；也可指定期号：python3 make_videos.py 06 07
python3 make_docs.py               # 生成 videos/脚本与核查.md
```

输出 1080×1920、30fps、约 95–105 秒的 9:16 竖屏 MP4，**无音轨**；屏幕字幕即口播文案，后续配音可直接照读。
4 核机器上每期约 2 分钟。系统依赖：FFmpeg（带 libx264）、`libegl1`。

| 期号 | 主题 | 模块 |
|------|------|------|
| 04 | 可得性偏差 | `explainer/ep04_availability.py` |
| 05 | 基率忽视 | `explainer/ep05_base_rate.py` |
| 06 | 小数定律误区 | `explainer/ep06_small_numbers.py` |
| 07 | 均值回归 | `explainer/ep07_regression.py` |
| 08 | 相关不等于因果 | `explainer/ep08_correlation.py` |

- 风格：米白纸张底、墨色手绘轮廓（描边带约 7 次/秒的抖动）、暖金光、少量红蓝强调；所有数字、曲线、人物均为教学示意，已在画面左上角标注。
- `explainer/engine.py`：镜头/字幕排时（按字数）、绘图原语、转场、并行渲染与 FFmpeg 编码；`props.py`：角色、气泡、图标；`factory.py`：传送带、检测门、点阵、饼图、天平。
- 字幕文案里 `【】` 标红，`|` 为手动换行；每条字幕不得超过两行（超出时渲染前会打印警告）。
- 逐镜检查：`python3 make_stills.py 05 2.0` 导出各镜头静帧，`python3 make_sheet.py 05 0 6` 拼联系表。

## 无声竖屏科普：《生活没变，怎么一刷手机就落后了？》（社会比较）

`social_comparison/index.html` 是一个单文件 Canvas 动画，可以直接用浏览器打开，不依赖外部资源。播放控件放在画幅外，支持播放/暂停（空格）、重播、拖动进度和逐帧查看（← →）。按 R 进入录制模式隐藏控件，按 Esc 退出。也可以用 `?t=秒数` 打开到指定时刻，用 `?record=1&autoplay` 直接进入录制模式并开始播放。

```bash
node social_comparison/render.cjs out/social_comparison.mp4   # 逐帧导出无声 MP4（H.264 / yuv420p / 30fps / 无音频轨）
node social_comparison/render.cjs --audit                      # 检查每张文字卡的稳定显示时长、字速和安全区
```

依赖 Playwright（使用本机已有的 Chromium）和带 libx264 的 FFmpeg。分镜表与资料来源见 `social_comparison/STORYBOARD.md`。

## 竖屏短视频：《走出洞穴的人，为什么先想回头？》（梵高笔触风格）

```bash
python3 cave_short.py out/cave_allegory.mp4                 # 成片 + cover.png / cover_clean.png
python3 cave_short.py out/cave_allegory.mp4 --still 31 57   # 只渲染指定秒数的单帧，检查画面
```

柏拉图《理想国》洞穴寓言，1080×1920、30fps、约 75 秒。方案（口播、分镜、出处核对）见 `plans/cave_allegory_75s.md`。
4 核机器上渲染约 15 分钟，成片约 110MB（码率上限 12Mbps；笔触细节多，码率再低会糊）。

- **画面**：`cave_draw.py` 用 Skia 绘制每个镜头的底稿（构图、光色、人物），`engine/paint.py` 把底稿转成梵高式厚涂短笔触。
  笔触方向由两部分混合：沿轮廓的切向（结构张量），以及场景给定的流场（漩涡、光源同心环、火焰上升、水面横向）。
  三层笔触（大 / 中 / 细节）用 `drawAtlas` 一次绘制，每 2 帧重画一次（15fps 手绘节奏），并带轻微"沸腾"抖动。
- **字幕**：思源宋体，单行不超过 13 字，按 30fps 叠加。第 10、11 镜分别标注「书中原意 · 转述」「创作者联想」，片尾注明出处。
- **声音**：ZipVoice 旁白（语速 0.75）。环境音全部程序化合成：火、风、滴水、铁链、溪流、鸟鸣等，洞内声音加混响。
  配乐分三段：大提琴长音 → 出洞时抽空 0.5 秒 → 钢琴单音加弦乐，结尾停在一个长音上。

## 无声科普竖屏：《为什么你刷短视频停不下来？》

```bash
python3 fetch_assets.py                      # 只需其中的思源黑体
python3 scroll_short.py out/scroll_short.mp4 # 成片 + 竖版/横版封面
python3 scroll_short.py --still 30 61.5      # 只渲染指定时刻的单帧，用于检查
```

黑金风格、动画主导：手机第一视角开场 → 历史 → 理论 → 推荐 → 方法。
画面带辉光、扫光、光条、光球、扩散光环、微尘和镜头推拉，每 3 秒内至少一次动画事件。
1080×1920、30fps、97 秒（含 6 秒参考资料），**不含音频流**，4 核渲染约 3 分钟。
屏幕文案、分镜表、事实清单与参考资料见 `docs/scroll_short/`，成片与封面在 `docs/scroll_short/media/`。

## 竖屏无声版：《轮盘连开十次黑，下一把押红吗？》（赌徒谬误）

```bash
python3 fetch_assets.py                       # 只需其中的字体
python3 gf_short.py out/gamblers_fallacy_silent.mp4
```

按 `scripts/gamblers_fallacy.md` 的 14 镜分镜固定排时，输出 1080×1920、30fps、108 秒的无音轨视频，
同目录生成 `gamblers_fallacy_silent.srt`（口播字幕，按每秒约 4.6 字估算时间，供后期配音对位）和封面 `cover.png`。

- 只烧录分镜表"屏幕文字"一栏的标题、数字与标注，不烧录口播字幕；配音、配乐、音效均留给后期
- 画面全部矢量绘制（轮盘、记分灯、筹码、硬币、天平、抽奖机），不依赖 Emoji 与 TTS 模型
- 排时用 `Video.layout_fixed(场景时长)`，渲染用 `Video.render(..., silent=True)`

## 心理科普：《为什么一到晚上，就觉得自己的人生不行了》

```bash
python3 fetch_assets.py          # 只需字体（思源宋体/黑体），无 TTS
python3 night_short.py           # 自动查找 ./bgm.m4a；缺失时只输出“待配乐预览”
```

90 秒、30fps，横竖屏独立排版（1080×1920 上下递进 / 1920×1080 左文右景），无旁白；黑金 2.5D 纸卡、原创中性人物、七类合成打击乐音效。
4 核机器两版合计约 4 分钟。代码在 `night/`：

| 模块 | 职责 |
|------|------|
| `config.py` | 画幅排版、配色、15 镜分镜、主字幕原文、候选音效事件 |
| `scenes.py` | 15 个镜头的场景绘制；所有撞击动作读事件时刻表，校准后自动跟随 |
| `draw.py` | 纸卡与柔和阴影、透视桌面、城市剪影、台灯、原创人物骨架 |
| `sfx.py` | 低音鼓 / 军鼓边击 / 木块 / 沙锤 / 框鼓与低音通鼓 / 邦戈鼓 / 轻柔吊镲 原创合成 |
| `music.py` | 原曲解码、谱通量起音、局部速度候选、90 秒片段选择、事件贴拍、避让混音、-16 LUFS / -1 dBTP 母带 |
| `render.py` | 时间轴、字幕与角标、匹配转场、多进程渲染、封面 |

交付物与核验报告输出到 `out/night/`（`DELIVERY.md` 说明哪些已渲染、已核验、未完成）。

## 竖屏无声版：《机会成本》

```bash
python3 fetch_assets.py                # 只需其中的字体（含思源宋体）
python3 oc_short.py out/opportunity_cost_silent.mp4
python3 oc_short.py --stills out/stills 1 30.5 60   # 导出指定秒数的关键帧
```

按 [`scripts/opportunity_cost.md`](scripts/opportunity_cost.md) 的 14 镜分镜绘制，1080×1920、30fps、103 秒，无音轨，口播以字幕呈现。
角色与道具全部用 Skia 程序化手绘（米白纸张肌理 + 抖动墨线 + 胶片颗粒），4 核约 3 分钟。
改字幕或节奏：编辑 `NARRATION`（每镜口播与起止时间）和 `SHOTS`（镜头时间与转场）；画面动作用 `cue(镜号, "关键词")` 锚定到字幕念到该词的时刻。

## 无旁白科普动画：《你不是在休息，你是在为休息感到内疚》

```bash
python3 fetch_assets.py                                  # 只需字体
python3 -m rest_guilt.build --bgm path/to/bgm.m4a        # 完整成片（也会自动查找 ./bgm.m4a、assets/bgm.m4a）
python3 -m rest_guilt.build                              # 未提供原曲：只出无音频流的画面预览与素材，状态"待配乐"
```

输出到 `out/rest_guilt/`：1080×1920 与 1920×1080 两套独立排版（30 fps，H.264 / yuv420p，AAC），
两种比例封面，`bgm.wav` / `sfx.wav` / `mix.wav`（48 kHz / 24 bit，同起点同长度），`卡点表.csv`、`逐屏文案.txt`、
`参考资料.txt`、`timeline.json`、七类音效素材 `sfx_samples/`、抽帧 `checks/` 与 `交付说明.md`。4 核机器约 10 分钟。

- **只用原曲**：原曲缺失、无法解码或短于 87 秒时不出带配乐的成片，不循环、不变速、不换曲（退出码 2）。
- **卡点**：谱通量粗检 + 短窗谱通量精修（2 ms 步长）、局部速度、动态规划节拍候选、段落新颖度选段；
  镜头边界在 ±0.4 秒内贴起音，关键撞击需要强度 ≥ 0.6 的起音，找不到就改为柔和动作并取消音效。
  画面动作与音效都从同一个事件帧开始，所以音画起音天然同帧；`av_offsets.json` 在独立音效轨上复测。
- **混音**：音效按局部音乐电平放置，原曲低频已强时减弱或取消低鼓；10/80/300 ms 余弦避让 2 dB；
  以 -16 LUFS-I / ≤ -1 dBTP 为起始目标，真峰值超标时降整体增益，不用限幅与削波。
- **数据源**：分镜、主卡、角标、候选音效都在 `rest_guilt/story.py`；改文字后构建会重新核算阅读窗口与安全区。

## 横屏版

```bash
python3 dyl_video.py out/designing_your_life.mp4
```

Pillow 绘制的 1920×1080、约 44 秒讲解动画（使用系统文泉驿字体），配同一首 BGM：场景时长吸附到半小节，「好时光日志」对上音乐 drop。

## 第三方资源许可

- [Fluent Emoji](https://github.com/microsoft/fluentui-emoji)：MIT License，© Microsoft
- [得意黑 Smiley Sans](https://github.com/atelier-anchor/smiley-sans)、[Noto Sans / Serif CJK](https://github.com/notofonts/noto-cjk)：SIL Open Font License 1.1
- [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M)：Apache 2.0，通过 [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) 运行

## 静音竖屏短视频：逻辑训练（三人·三城·三种运动）

```bash
python3 fetch_assets.py                         # 只需其中的思源黑体字体
python3 logic/verify_logic.py                   # 制作前核验：36 种组合仅 1 个解 + 反证
python3 logic/logic_short.py out/logic_short.mp4
```

输出 1080×1920、30fps、90 秒、**无音频轨**的解题动画，以及封面 `out/logic_cover.png`。4 核机器约 1 分钟。
完整制作方案（开头、字幕脚本、分镜、动效清单、核验说明）见 `logic/production_plan.md`。
