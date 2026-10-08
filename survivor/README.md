# 《他连续赢了10次，然后开始教你成功》——幸存者偏差竖屏科普短视频

Remotion + React + TypeScript 制作，1080×1920、30fps，约 66 秒，带离线 TTS 中文配音、程序化配乐和音效。

成片与配套文件在 `deliverables/` 目录：

| 文件 | 内容 |
|------|------|
| `survivor_bias.mp4` | 成片 |
| `cover.png` | 竖屏封面 |
| `keyframes/*.png` | 关键帧预览（开场、筛选、冠军开课、暂停、拉远揭晓、命名、结尾） |
| `subtitles.srt` | SRT 字幕 |
| `narration.md` | 旁白稿和分镜时间轴（按真实配音时长生成） |

## 运行

依赖：Node 18 及以上、Python 3.10 及以上、FFmpeg。

```bash
# 1. 仓库根目录：Python 依赖与离线 TTS 模型（sherpa-onnx：Kokoro v1.1 + ZipVoice + Vocos，不入库）
pip install -r ../requirements.txt
python3 ../fetch_assets.py            # 也会下载上一个项目用到的 emoji，可忽略
# 2. 本目录：字体（Noto Sans CJK SC Bold/Black、得意黑）放到 public/fonts/
mkdir -p public/fonts && cd public/fonts
curl -LO https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/OTF/SimplifiedChinese/NotoSansCJKsc-Bold.otf
curl -LO https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/OTF/SimplifiedChinese/NotoSansCJKsc-Black.otf
# 得意黑：从 https://github.com/atelier-anchor/smiley-sans/releases 的 v2.0.1 压缩包中取出 SmileySans-Oblique.ttf
cd ../..
npm install

# 3. 配音 → 时间轴 → 混音（生成 src/generated/timeline.json、public/mix.wav、deliverables/ 下的字幕和旁白稿）
python3 scripts/build_audio.py              # 没有 TTS 模型时用 --no-voice，成片左上角会标注“未配音预览”

# 4. 预览与导出
npm run studio                               # 浏览器内逐帧预览
npm run render                               # 导出 out/survivor_bias.mp4
npx remotion still src/index.ts Cover out/cover.png
node scripts/stills.mjs out/stills hook:45 reveal:1329   # 批量导出关键帧（名称:帧号）
```

`remotion.config.ts` 优先使用 `/opt/pw-browsers/...` 下预装的 Chromium，也可以用环境变量 `REMOTION_BROWSER` 指定；两者都没有时，由 Remotion 自行下载浏览器。

## 结构

| 文件 | 职责 |
|------|------|
| `scripts/build_audio.py` | 台词表 `LINES` 是唯一的文案来源：逐句合成配音，按真实时长排出场景和事件时刻，再生成配乐、音效、混音和 SRT |
| `src/data.ts` | 1024 名选手的唯一数据源：带种子的随机排列决定冠军、每人在第几轮出局、每轮硬币结果和每人的猜测，并算出每轮结束后的站位 |
| `src/world.ts` | 相机（世界坐标 → 屏幕）、小人和皇冠、领奖台的 Canvas 绘制，以及给定时刻每个人的状态 |
| `src/scenes/*` | 开场、游戏 HUD、冠军开课、暂停取景框、拉远揭晓、命名与结尾、字幕 |

- **确定性**：所有动画只由帧号推出；随机数都用固定种子（mulberry32）。同一帧渲染两次，输出逐字节一致（已用 md5 核对）。
- **数字一致**：计数在“揭晓时刻”跳变，判断某人是否变灰也用同一个时刻；人数恒为 `1024 >> 已揭晓轮数`。
- **退出者不删除**：出局的人走到场外的环带上，位置按出局轮次一圈圈向外排布。镜头每轮收紧，他们就被裁到画面外；反转时镜头拉远，所有人都在原位，冠军始终在原点。
- **取景框**：暂停那一刻把屏幕矩形换算成世界坐标；拉远时，这个框跟着世界一起缩小到冠军身边。

## 科学表述

- 1024→512→…→1 是**教学示意**：程序预设每轮恰好一半猜错。游戏段一直显示“教学示意：每轮按一半晋级”。真实的随机实验里，每轮存活人数会波动，也不保证正好产生一位十连胜者。
- 片中没有给概率公式。如需补充：在公平硬币、各轮独立的前提下，**某个事先指定的人**连续猜对 10 次的概率是 1/1024。这和“1024 人中至少有一人十连胜”的概率不是一回事。
- 结尾强调“经验可以参考”，并提示要比较“做法相同却没成功的人”和“其他可能的解释”，不推出“成功全靠运气”。
- “学姐小林”和她的经验分享是虚构的，没有使用真实人物或统计数据。

## 素材来源

- 配音：[sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) 离线运行的 ZipVoice（零样本 TTS），音色提示用 [Kokoro-82M v1.1](https://huggingface.co/hexgrad/Kokoro-82M)（Apache 2.0）合成的句子：旁白用 zf_001，冠军用 zm_009，不涉及任何真人声音。
- 配乐和音效：全部用 `scripts/build_audio.py` 与 `../engine/audio.py` 通过代码合成（拨弦、贝斯、铺底、硬币声、滑哨、唱片急停等），没有使用外部音频文件。
- 字体：[Noto Sans CJK SC](https://github.com/notofonts/noto-cjk)、[得意黑 Smiley Sans](https://github.com/atelier-anchor/smiley-sans)，均为 SIL Open Font License 1.1。
- 图形：全部为代码绘制的矢量图形。

## 当前限制

- 配音是合成语音，语气比真人平淡；“？”在 ZipVoice 词表中缺失，问句的上扬语调可能不明显。
- 揭晓画面里每人约 16px 高，在手机上能看出是一片人群，但看不清五官。
- 安全区按顶部 180px、底部 300px 和左右 80px 设计，尚未在真实手机的各平台界面上核对。
