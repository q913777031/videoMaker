# videoMaker

用代码生成短视频：Skia 逐帧绘制动效 + 离线 TTS 配音 + 固定 BGM 自动卡点 + 程序化音效 + FFmpeg 合成。

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

## 横屏版

```bash
python3 dyl_video.py out/designing_your_life.mp4
```

Pillow 绘制的 1920×1080、约 44 秒讲解动画（使用系统文泉驿字体），配同一首 BGM：场景时长吸附到半小节，「好时光日志」对上音乐 drop。

## 第三方资源许可

- [Fluent Emoji](https://github.com/microsoft/fluentui-emoji)：MIT License，© Microsoft
- [得意黑 Smiley Sans](https://github.com/atelier-anchor/smiley-sans)、[Noto Sans CJK](https://github.com/notofonts/noto-cjk)：SIL Open Font License 1.1
- [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M)：Apache 2.0，通过 [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) 运行

## 静音竖屏短视频：逻辑训练（三人·三城·三种运动）

```bash
python3 fetch_assets.py                         # 只需其中的思源黑体字体
python3 logic/verify_logic.py                   # 制作前核验：36 种组合仅 1 个解 + 反证
python3 logic/logic_short.py out/logic_short.mp4
```

输出 1080×1920、30fps、90 秒、**无音频轨**的解题动画，以及封面 `out/logic_cover.png`。4 核机器约 1 分钟。
完整制作方案（开头、字幕脚本、分镜、动效清单、核验说明）见 `logic/production_plan.md`。
