# videoMaker

用代码生成讲解类视频：Pillow 逐帧绘制，FFmpeg 编码为 MP4。

## 依赖

- Python 3.10+、`pip install -r requirements.txt`
- FFmpeg（需带 libx264）
- 中文字体：默认使用文泉驿正黑 `/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc`，可在 `dyl_video.py` 的 `FONT_PATH` 修改

## 生成

```bash
python3 dyl_video.py out/designing_your_life.mp4
```

输出 1920×1080、30fps、约 43 秒的《设计你的人生》讲解动画（无声）。

## 修改内容

每个场景是 `SCENES` 中的一个 `Scene(时长, 绘制函数)`，绘制函数接收 `(draw, t)`，`t` 为场景内秒数。
增删场景或改文案只需修改对应函数与 `SCENES` 列表。

## 竖屏短视频版（配音 + 背景音乐 + 字幕）

```bash
# 下载离线中文 TTS 模型（约 170MB，已在 .gitignore 中忽略）
mkdir -p models && curl -L https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-melo-tts-zh_en.tar.bz2 | tar xj -C models
python3 dyl_short.py out/designing_your_life_short.mp4
```

输出 1080×1920、30fps 的 9:16 竖屏视频：

- **配音**：sherpa-onnx + MeloTTS 离线逐句合成，模型路径可用环境变量 `DYL_TTS_MODEL` 覆盖，语速见 `TTS_SPEED`
- **同步**：场景时长由旁白长度决定，动画入场与句子开始时间对齐，字幕按句精确显示
- **背景音乐**：代码合成（C-Am-F-G 和弦 + 琶音），无版权问题；有人声时自动压低
- **安全区**：右侧和底部为短视频平台的按钮与标题留白

改旁白：修改 `SCENES` 中每个场景的 `lines`；动画通过 `cue(i)` 取第 i 句的开始时间。
