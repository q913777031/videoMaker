# videoMaker

用代码生成短视频：Skia 逐帧绘制动效 + 离线 TTS 配音 + 程序化配乐与音效 + FFmpeg 合成。

## 竖屏短视频：《设计你的人生》

```bash
pip install -r requirements.txt
python3 fetch_assets.py                       # 下载字体、3D Emoji、Kokoro TTS 模型（约 400MB，均不入库）
python3 dyl_short.py out/designing_your_life_short.mp4
```

输出 1080×1920、30fps、约 137 秒的 9:16 竖屏视频，以及同目录下的封面图 `cover.png`。
4 核机器上首次渲染约 6 分钟（含 TTS 合成），之后只改画面时约 5 分钟（旁白有缓存）。

系统依赖：FFmpeg（带 libx264）、`libegl1`（skia-python 需要）。

### 内容结构

第二人称代入的情绪叙事：标准答案人生的痛点 → 笑容面具碎裂 → 深夜自问 → 转折遇见斯坦福课程
→ 重新定义问题 → 三个方法（好时光日志 / 奥德赛计划 / 最小原型）各配真实场景 → 情绪高潮 → 评论区互动。

### 引擎（`engine/`）

| 模块 | 职责 |
|------|------|
| `gfx.py` | 缓动、字体回退、逐字动画文字（弹出/砸入/上浮）、3D Emoji、对话气泡、电池、粒子、光芒、彩带、故障效果 |
| `audio.py` | Kokoro 离线 TTS（带缓存）、合成音效（呼啸/冲击/上升/心跳/碎裂等）、配乐（忧伤钢琴 → 流行电子 → 间奏 → 尾声）、闪避混音、-14 LUFS 响度标准化 |
| `timeline.py` | 场景 / 台词 / 事件模型、按旁白长度自动排时、镜头震动与推拉、转场、逐字点亮字幕、4 进程并行渲染 |

- **音画同步**：每句旁白单独合成，动画与音效都锚定到"某句读到某个词"的时刻（`w(x, 句序号, "关键词")`）。
- **性能**：平滑背景层以 1/4 分辨率绘制后用 OpenCV 放大，直接写入帧缓冲。
- **配音**：默认音色 `zm_yunxi`。用语音识别评估候选音色后选定：音高变化约为 MeloTTS 的 2 倍，识别错误率最低。

### 修改内容

- 改旁白或节奏：编辑 `dyl_short.py` 的 `SCENES`，每句是 `Line(文本, 语速倍率, 句后停顿)`，`【】` 标记字幕高亮词
- 加音效：在场景的 `events` 里加 `(类型, 句序号, 关键词, 偏移秒)`，类型见 `engine/timeline.py` 的 `EVENT_FX`
- 换音色：`Video(..., voice="zf_xiaoxiao")`，可选值见 `engine/audio.py` 的 `VOICES`

## 横屏无声版

```bash
python3 dyl_video.py out/designing_your_life.mp4
```

Pillow 绘制的 1920×1080、约 43 秒讲解动画（使用系统文泉驿字体）。

## 第三方资源许可

- [Fluent Emoji](https://github.com/microsoft/fluentui-emoji)：MIT License，© Microsoft
- [得意黑 Smiley Sans](https://github.com/atelier-anchor/smiley-sans)、[Noto Sans CJK](https://github.com/notofonts/noto-cjk)：SIL Open Font License 1.1
- [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M)：Apache 2.0，通过 [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) 运行
