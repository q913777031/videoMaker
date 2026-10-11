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

## 横屏无声版

```bash
python3 dyl_video.py out/designing_your_life.mp4
```

Pillow 绘制的 1920×1080、约 43 秒讲解动画（使用系统文泉驿字体）。

## 第三方资源许可

- [Fluent Emoji](https://github.com/microsoft/fluentui-emoji)：MIT License，© Microsoft
- [得意黑 Smiley Sans](https://github.com/atelier-anchor/smiley-sans)、[Noto Sans CJK](https://github.com/notofonts/noto-cjk)：SIL Open Font License 1.1
- [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M)：Apache 2.0，通过 [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) 运行
