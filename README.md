# videoMaker

用代码生成短视频：Skia 逐帧绘制动效 + 离线 TTS 配音 + 程序化配乐与音效 + FFmpeg 合成。

## 竖屏短视频：《设计你的人生》

```bash
pip install -r requirements.txt
python3 fetch_assets.py                       # 下载字体、3D Emoji、Kokoro TTS 模型（约 800MB，均不入库）
python3 dyl_short.py out/designing_your_life_short.mp4
```

输出 1080×1920、30fps、约 82 秒的 9:16 竖屏视频，以及同目录下的封面图 `cover.png`。
4 核机器上首次渲染约 6 分钟（含 TTS 合成），之后只改画面时约 5 分钟（旁白有缓存）。

系统依赖：FFmpeg（带 libx264）、`libegl1`（skia-python 需要）。

### 内容结构

斯坦福课程开场 → 重新定义问题 → 三个方法（好时光日志 / 奥德赛计划 / 最小原型）各配真实场景
→ 情绪高潮 → 评论区互动。

### 引擎（`engine/`）

| 模块 | 职责 |
|------|------|
| `gfx.py` | 缓动、字体回退、逐字动画文字（弹出/砸入/上浮）、3D Emoji、对话气泡、电池、粒子、光芒、彩带、故障效果 |
| `audio.py` | ZipVoice / Kokoro 离线 TTS（带缓存）、合成音效（呼啸/冲击/上升/心跳/碎裂等）、配乐（忧伤钢琴 → 流行电子 → 间奏 → 尾声）、闪避混音、-14 LUFS 响度标准化 |
| `timeline.py` | 场景 / 台词 / 事件模型、按旁白长度自动排时、镜头震动与推拉、转场、逐字点亮字幕、4 进程并行渲染 |

- **音画同步**：每句旁白单独合成，动画与音效都锚定到"某句读到某个词"的时刻（`w(x, 句序号, "关键词")`）。
- **性能**：平滑背景层以 1/4 分辨率绘制后用 OpenCV 放大，直接写入帧缓冲。
- **配音**：默认用 ZipVoice（零样本、韵律接近真人）。以 Kokoro 合成的一句话作音色提示，不涉及任何真人声音；成片语音识别错误率约 1%。

### 修改内容

- 改旁白或节奏：编辑 `dyl_short.py` 的 `SCENES`，每句是 `Line(文本, 语速倍率, 句后停顿)`，`【】` 标记字幕高亮词
- 加音效：在场景的 `events` 里加 `(类型, 句序号, 关键词, 偏移秒)`，类型见 `engine/timeline.py` 的 `EVENT_FX`
- 换音色：`Video(..., voice="zv_001")`（ZipVoice 女声），或 `zv_009`、`zf_001` 等，可选值见 `engine/audio.py` 的 `VOICES`

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

## 横屏无声版

```bash
python3 dyl_video.py out/designing_your_life.mp4
```

Pillow 绘制的 1920×1080、约 43 秒讲解动画（使用系统文泉驿字体）。

## 第三方资源许可

- [Fluent Emoji](https://github.com/microsoft/fluentui-emoji)：MIT License，© Microsoft
- [得意黑 Smiley Sans](https://github.com/atelier-anchor/smiley-sans)、[Noto Sans CJK](https://github.com/notofonts/noto-cjk)：SIL Open Font License 1.1
- [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M)：Apache 2.0，通过 [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) 运行
