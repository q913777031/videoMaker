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
