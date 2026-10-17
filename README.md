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

## 无旁白科普动画：《你不是在休息，你是在为休息感到内疚》

```bash
python3 fetch_assets.py                                  # 只需字体
python3 -m rest_guilt.build --bgm path/to/bgm.m4a        # 完整成片（默认依次查找 music/bgm.m4a、./bgm.m4a、assets/bgm.m4a）
# 当前分镜（深夜卧室版）只为竖屏设计，默认只出竖屏
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

## 横屏无声版

```bash
python3 dyl_video.py out/designing_your_life.mp4
```

Pillow 绘制的 1920×1080、约 43 秒讲解动画（使用系统文泉驿字体）。

## 第三方资源许可

- [Fluent Emoji](https://github.com/microsoft/fluentui-emoji)：MIT License，© Microsoft
- [得意黑 Smiley Sans](https://github.com/atelier-anchor/smiley-sans)、[Noto Sans CJK](https://github.com/notofonts/noto-cjk)：SIL Open Font License 1.1
- [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M)：Apache 2.0，通过 [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) 运行
