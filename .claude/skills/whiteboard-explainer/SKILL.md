---
name: whiteboard-explainer
description: 用白板手绘引擎（whiteboard/engine.py）制作整讲 92.6 秒的竖屏读书/知识短视频：一只手握马克笔按音乐拍点描线写字，相机在大白板上平移缩放，没有硬切。含打工人向的叙事结构与口语化文案规则。用户要求“白板手绘”“手绘讲解”“用白板做某本书/某一讲”时使用；范例 xitong/wb01_system.py（系统之美 01）。
---

# 白板手绘讲解（整讲）

范例：`xitong/wb01_system.py`；引擎：`whiteboard/engine.py`；系列入口 `xitong/build.py` 中 `wb.install(B)`。
配乐、卡点、交付格式照 CLAUDE.md（`music/bgm.m4a`、实测拍点、每讲 mp4 + cover.png + 标题与话题.txt + 横屏封面_1080x1080.png）。

## 1. 叙事结构（42 个 1 小节镜头，约 92.6 秒）

| 镜头 | 段落 | 做法 |
|---|---|---|
| 1–6 | 打工人切身问题 | 一个昨天就遇到过的具体场景（换了三份工作烦心事一样、工资涨了存不下钱……），画面讲事实，最后一镜抛出问题 |
| 7–17 | 书中观点 | 先亮书（书名、作者），再用书里的例子或比喻，最后把观点画成一张图 |
| 18–28 | 现实例子 | 3–4 个不同场景各 2 镜（职场、生活、家庭各至少一个），最后拉远把例子连到同一个原因上 |
| 29–41 | 具体做法 | 3–4 条能马上照做的步骤，每条带具体例子（“按工时改成按交付”“跳槽前问三句”），最后拉远看整张白板 |
| 42 | 评论区 | 一个具体问题 + 下一讲片名 |

## 2. 文案规则（字幕与白板上的字）

- 像真人说话：短句、口语、具体名词（工位、工单、外卖、加班到十点），少用抽象词。
- 不用“不是……是……”“不是……而是……”句式，不用反问堆叠，同一个意思只说一次。
- 避开常见 AI 腔：完整禁用句式与词表见 CLAUDE.md「文案用语（强制）」与 `engine/wording.py`，`--sheet` / `--publish` 自动检查，警告必须清零。
- 字幕每条 ≤8 个汉字、不含数字和英文（引擎阅读窗要求）；数字写在白板上。
- 书中观点一律标“书中观点”转述，不加引号当原文；例子与做法在 notes 里注明“示意 / 据书中思路整理”。

## 3. 分镜写法

```python
from whiteboard.engine import Board, stick, face, arrow, rect, node, target, cross, check, clock, hands_at, book, \
    building, desk, doc, scooter, light, podium_list, scribble, underline, spring_path, P, join, RED, BLUE, GREEN, BLACK
b = Board(size=(3600, 8600))                              # 白板尺寸，按内容区块排布
j = b.shot("字幕", "页眉标签", view=(cx, cy, z))          # 新镜头；相机看向白板 (cx, cy)，z≈0.8–0.9 看单块，0.42 看一片，0.235 看全板
b.path(j, 0, 0.8, stick(500, 900), sfx="wood_high")      # 第 0–0.8 拍描出；带音效的项起笔自动吸附到整数拍
b.text(j, 1, 2, "写字", 800, 700, 72, RED, sfx="pop")    # 逐字写出（hand 字体 = 马善政毛笔体）
b.custom(j, 0, 12, fn, sfx="pop")                         # fn(c, k, t) 画动态内容（弹簧、指针），返回笔尖或 None
b.hit(j, 2, "ding")                                       # 单独加音效拍
ep = episode(...); b.attach(ep)                           # 交给系列 episode() 后挂上白板
SQUARE_SHOT = 16                                          # 单讲横屏封面取景镜头
```

- 版面：每个段落占白板一块区域（约 1500×900），区块之间留白；转场靠相机平移（每镜开头 0.45 秒），区块之间可画绿色箭头。
- 每镜至少 2 个整数拍有音效（描线 wood_high、写字 pop、划掉 rim、重点 ding、重击 kick + `shake=[拍]` / `flashes=[拍]`），`--sheet` 警告清零。
- 音乐 drop 在第 9 镜（17.14 秒）：放本讲最有冲击力的动作（如松手、红字砸出）。
- 封面 `cover.png`：取 `cover_shot` 镜头末尾的白板画面 + 毛笔大标题；横屏封面取 `SQUARE_SHOT`。

## 4. 流程

1. 读书核实观点与例子出处（查不到原文就转述并注明）。
2. 写分镜 → `python3 -m <包>.build 01 --sheet`，把联系表切 4 段逐张看：内容是否出画、字是否太小、手是否挡字。
3. 渲染 `python3 -m <包>.build 01`（约 0.08 秒/帧，4 核约 3–4 分钟）→ `--verify` → `--publish`。
4. 抽帧检查成片后提交推送，发成片与封面给用户。
