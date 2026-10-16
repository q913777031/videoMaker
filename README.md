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

## 横屏无声版

```bash
python3 dyl_video.py out/designing_your_life.mp4
```

Pillow 绘制的 1920×1080、约 43 秒讲解动画（使用系统文泉驿字体）。

## 第三方资源许可

- [Fluent Emoji](https://github.com/microsoft/fluentui-emoji)：MIT License，© Microsoft
- [得意黑 Smiley Sans](https://github.com/atelier-anchor/smiley-sans)、[Noto Sans CJK](https://github.com/notofonts/noto-cjk)：SIL Open Font License 1.1
- [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M)：Apache 2.0，通过 [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) 运行
