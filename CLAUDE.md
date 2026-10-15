# 项目约定

## 背景音乐（强制）

- 所有视频（包括以后新增的）背景音乐一律用 `music/bgm.m4a`，不另找音乐，也不程序化合成配乐。
- 必须卡点：
  - 基于 `engine/timeline.py` 的视频：直接用 `Video(...)`，节拍网格由引擎自动应用；用 `drop_at="场景名"` 指定哪个场景对上音乐 drop。
  - 不走 `Video` 的脚本：用 `engine/bgm.py` 的 `analyze()` / `Sync`，把场景切换吸附到半小节线上，并用 `Sync.track(总时长)` 截取配乐（参考 `dyl_video.py` 的 `beat_sync`）。
- 只有用户明确要求换歌时才替换 `music/bgm.m4a`；节拍会重新分析，代码不用改。
