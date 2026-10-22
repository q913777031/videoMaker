# videoMaker

用代码生成短视频：Skia 逐帧绘制动效 + 离线 TTS 配音 + 固定 BGM 自动卡点 + 程序化音效 + FFmpeg 合成。

## 竖屏科普短视频：幸存者偏差（Remotion）

《他连续赢了10次，然后开始教你成功》，约 66 秒，见 [`survivor/`](survivor/README.md)；成片与字幕在 `survivor/deliverables/`。

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

## 科普动画：《为什么人会信星座？》

```bash
python3 zodiac.py out/zodiac            # 竖屏 + 横屏成片、封面、分轨、卡点表、文案
python3 zodiac.py out/zodiac --no-video # 只出音频分轨、封面与文档
```

无旁白、黑金风格，约 92.6 秒（原曲 90 秒处硬截断，最后一击后接约 3 秒混响尾音自然淡出）。

- 卡点：`bgm.detect()` 用 librosa 动态规划节拍跟踪检测逐拍时间、起音强度（全频 / 低频 / 中高频）、小节位置与段落边界；
  `CUES` 中每个动作写一个参考时间，由 `beat()` 吸附到最近的实测拍点（偏差 >0.12 秒直接报错，不伪造）
- 音效：`engine/perc.py` 合成低音鼓、军鼓边击、木块、沙锤、框鼓、低音通鼓、邦戈鼓、拍手、轻柔吊镲；按起音时间提前放置，峰值落在拍点上；
  音乐在该拍已有重底鼓时低音鼓自动换高通版；配乐对重击做 ≤3 dB 的平滑闪避
- 输出（`out/zodiac/`）：`zodiac_portrait_1080x1920.mp4`、`zodiac_landscape_1920x1080.mp4`、`cover_*.png`、
  `bgm_track.wav` / `sfx_track.wav`（两轨相加即限幅前混音）、`cue_sheet.md` / `.csv`、`copy_and_references.md`

## 水墨长卷科普：《重阳节是怎么来的？边看边答题》

```bash
python3 fetch_assets.py            # 字体
python3 -m chongyang.build         # 成片 → out/chongyang/
```

一幅连续平移的水墨长卷讲重阳节：九为阳数、两九相重；九九谐音久久；《西京杂记》的早期记载；桓景登高避灾的传说；
王维诗；糕谐音高；今天的法定老年节。中间 4 道互动题，每题 A/B 两个选项、3 秒倒计时（3、2、1 卡实测拍点），
揭晓时朱砂“对”印砸在拍点上。成片与文案出处在 `videos/chongyang/`，说明见 [`chongyang/README.md`](chongyang/README.md)。

## 水墨长卷科普：《元旦是怎么来的？》《春节是怎么来的？》《元宵节是怎么来的？》《清明节是怎么来的？》《端午节是怎么来的？》

```bash
python3 -m yuandan.build           # 元旦 → out/yuandan/
python3 -m chunjie.build           # 春节 → out/chunjie/
python3 -m yuanxiao.build          # 元宵节 → out/yuanxiao/
python3 -m qingming.build          # 清明节 → out/qingming/
python3 -m duanwu.build            # 端午节 → out/duanwu/
```

与重阳节同一套水墨长卷框架与互动答题（4 题、3 秒倒计时、A/B 选项、拍点揭晓）。元旦：旦字字形、萧子云诗、三正岁首、
秦以十月为岁首、太初历、1912 改用公历、1949 定名、法定放假 1 天。春节：烧竹爆竹、年兽传说、桃符到春联、王安石《元日》、
压岁谐音压祟、1914 定名春节、2024 列入人类非遗。元宵节：元是正月宵是夜、上元与三元、唐代宵禁与“放夜”、辛弃疾《青玉案·元夕》、
元宵滚汤圆包、南宋灯谜、不是法定假日。清明：按太阳位置定日子、天清地明、寒食禁火与介子推传说、旧题杜牧《清明》、
《清明上河图》画汴京、寒食上墓编入五礼、2008 年成为法定假日。端午：端是开头午同五、恶月驱邪、屈原传说与龙舟粽子、
文秀《端午》、艾草菖蒲、角黍、2009 年列入人类非遗。成片、封面、文案与出处在 `videos/<节日拼音>/`。

## 中国风读书系列：《传习录》（本人克隆声旁白 + 水墨逐笔书法）

```bash
chuanxilu/setup_cosyvoice.sh                 # 一次性：CosyVoice 3 独立环境 + 语音识别模型（需放行 huggingface.co 等）
python3 -m chuanxilu.voice ep01              # 旁白：本人录音（voices/me_new/，不入库）零样本克隆，拼音回写校验，念错换种子重合成
python3 -m chuanxilu.build ep01 --sheet      # 估算排时的逐镜联系表（不需旁白）
python3 -m chuanxilu.build ep01              # 成片 → out/chuanxilu/ep01/
```

1080×1920、30fps，每讲 4–6 分钟。文案先行：`chuanxilu/文案/epNN.md` 每句行尾带节奏标注（〔快｜慢｜留白0.8〕），直接驱动合成语速与停顿；
写作规范见项目 skill `chuanxilu-copywriting`，出处核查见 `chuanxilu/事实核查.md`。
画面为宣纸水墨：Make Me a Hanzi 笔顺数据驱动的逐笔书法（`hanzi.py`）、远山云雾、朱砂印、竖排原文卡、古今双线人物（`ink.py` / `art.py`）；
排时与卡点沿用 `engine/timeline.py`（配乐 `music/bgm.m4a`，drop 落在开场标题），打击乐为 `engine/perc.py` 的堂鼓、大鼓、大锣、梆子、木鱼、编钟。
成片、封面、标题与话题在 `videos/chuanxilu/`。

| 讲 | 概念 | 片名 |
|----|------|------|
| 01 | 心即理 | 道理都懂，为什么还是过不好？ |

## 西方心理学风格科普：《弗洛伊德：你没发现的那部分自己》

```bash
python3 -m freud.build             # → out/freud/
```

维也纳画廊长卷：大马士革墙纸、鎏金画框、铜版画排线，衬线字体与酒红点缀；无互动答题，92.6 秒。内容：潜意识与冰山比喻（后人比喻）、
本我/自我/超我与“骑手和马”、防御机制、口误与梦、自由联想，以及可证伪性质疑与现代心理学的修正。成片、封面、卡点表、文案与出处在 `videos/freud/`。

## 3D 科普：《出门一会儿，空调关不关？》

```bash
python3 fetch_assets.py            # 字体
(cd ac3d && npm install)           # three.js
python3 -m ac3d.build              # 成片 → out/ac3d/（4 核约 40 分钟）
```

真 3D（three.js 程序化建模，Playwright 无头 Chromium 软件 WebGL 逐帧渲染），1080×1920、30fps、92.6 秒。
整片是同一间现代客厅的剖面（白色分体空调室内机、阳台上的室外机、电视、沙发），只有一台相机连续运镜，没有硬切；
每句字幕都对应画面里的具体动作：热粒子从墙和窗钻进屋、空调把热顺着管路搬到室外机、关机后室温读数上涨、
重开时耗电条冲顶、电视上播实测柱状图、遥控器连按触发“保护中”、定频机室外机自己启停。
配乐为 `music/bgm.m4a`，镜头边界与 29 个打击乐音效（`engine/perc.py`：低音鼓、军鼓边击、低音通鼓、拍手、木块、沙锤）落在实测拍点上。
事实依据见 [`ac3d/事实清单.md`](ac3d/事实清单.md)；成片、卡点表、文案与出处在 `videos/ac3d/`。引擎说明见 [`ac3d/README.md`](ac3d/README.md)。

## 系列科普动画：阿德勒心理学 10 讲

```bash
python3 fetch_assets.py              # 只需其中的字体
python3 -m adler.build               # 渲染全部 10 期到 out/adler/epXX/；也可指定期号：python3 -m adler.build 03 07
python3 -m adler.build 03 --sheet    # 逐镜联系表，检查画面
```

无旁白、纸片剪影风格，每期 1080×1920、30fps、92.6 秒；配乐统一为 `music/bgm.m4a`，镜头边界与全部打击乐音效都落在 `bgm.detect()` 的实测拍点上，
第 8 小节（17.14 秒，音乐 drop）落版每期的概念名。成片、封面、卡点表与逐期“文案与出处”在 `videos/adler/`。

| 期 | 概念 | 片名 |
|----|------|------|
| 01 | 目的论 | 过去，真的决定了现在的你吗？ |
| 02 | 自卑感 | 觉得自己不如别人，是坏事吗？ |
| 03 | 自卑情结 | “要不是因为……，我早就……” |
| 04 | 追求优越 | 你一直在和谁比赛？ |
| 05 | 人生课题 | 为什么烦恼，总和人有关？ |
| 06 | 课题分离 | 别人怎么看你，是谁的课题？ |
| 07 | 鼓励 | 为什么“你真棒”，不一定是最好的夸奖？ |
| 08 | 早期记忆 | 你最早的记忆，藏着什么？ |
| 09 | 出生顺序 | 老大懂事、老幺任性，是真的吗？ |
| 10 | 共同体感觉 | 人在什么时候，会觉得自己有价值？ |

- 每镜右上角标注内容性质：阿德勒原著 / 大意、岸见一郎阐释（《被讨厌的勇气》中的表述）、研究证据、常见误解、小练习等；
  “课题分离”“一切烦恼都是人际关系的烦恼”等岸见一郎的说法不署名阿德勒。逐条出处见 [`adler/事实核查.md`](adler/事实核查.md)。
- 引擎与写法见 [`adler/README.md`](adler/README.md)：`core.py`（实测拍点时间轴、声明式元素、混音与输出）、`kit.py`（纸片人物、图标、气泡等元件）、`epXX_*.py`（各期分镜）。

## 系列科普动画：荣格心理学 10 讲

```bash
python3 -m jung.build                # 渲染全部 10 期到 out/jung/epXX/；也可指定期号：python3 -m jung.build 04 09
python3 -m jung.build 04 --sheet     # 逐镜联系表
python3 -m jung.build --verify       # 核验成片
python3 -m jung.build --publish      # 交付到 videos/jung/
```

复用阿德勒系列引擎（`adler/core.py` 的 `SERIES`、`adler/build.py` 的 `PKG / OUT / MODS` 参数化），荣格专用元件在 `jung/art.py`
（曼陀罗、意识层次、面具、阴影、功能罗盘、秒表、梦中的房子、日月）。无互动答题，每期 92.6 秒，卡点规则同阿德勒系列。

| 期 | 概念 | 片名 |
|----|------|------|
| 01 | 集体无意识 | 为什么不同地方的神话这么像？ |
| 02 | 原型 | 为什么故事总有那几种人？ |
| 03 | 人格面具 | 你每天戴着哪张脸？ |
| 04 | 阴影 | 你最讨厌的人，像不像你？ |
| 05 | 阿尼玛与阿尼姆斯 | 你心里的“另一半” |
| 06 | 内倾与外倾 | 聚会后，你是累还是兴奋？ |
| 07 | 四种功能 | 你先想，还是先感受？ |
| 08 | 情结 | 为什么一句话就能把你点着？ |
| 09 | 梦的补偿 | 梦在跟你说什么？ |
| 10 | 自性化 | 怎样成为完整的自己？ |

- 每镜右上角标注内容性质：荣格原著 · 大意、荣格自述、研究证据、常见质疑、当代理解等；MBTI 注明为迈尔斯与布里格斯所编，
  并给出重测不稳定的研究；集体无意识、释梦、自性化等难以实证之处在片中单列“常见质疑”。逐期出处见各期“文案与出处”。

## 系列科普动画：马斯洛心理学 10 讲

```bash
python3 -m maslow.build              # 渲染全部 10 期到 out/maslow/epXX/；也可指定期号
python3 -m maslow.build 08 --sheet   # 逐镜联系表
python3 -m maslow.build --verify     # 核验成片
python3 -m maslow.build --publish    # 交付到 videos/maslow/
```

复用阿德勒系列引擎，马斯洛专用元件在 `maslow/art.py`（需求层次的台阶与金字塔两种画法、满足度条、山峰、鲸鱼、饭碗、成长的芽）。
无互动答题，每期 92.6 秒，卡点规则同阿德勒系列。

| 期 | 概念 | 片名 |
|----|------|------|
| 01 | 需求层次 | 人到底想要什么？ |
| 02 | 匮乏与成长 | 为什么有的需要满足了就停？ |
| 03 | 安全需要 | 为什么人一不安就想抓紧？ |
| 04 | 归属与爱 | 为什么一个人待久了会难受？ |
| 05 | 尊重需要 | 为什么我们那么在乎被认可？ |
| 06 | 自我实现 | 活成自己的人是什么样？ |
| 07 | 高峰体验 | 你有过忘了时间的时刻吗？ |
| 08 | 金字塔误读 | 马斯洛画过金字塔吗？ |
| 09 | 约拿情结 | 为什么我们害怕变得更好？ |
| 10 | 自我超越 | 自我实现之后，还有什么？ |

- 08 讲专门澄清：金字塔图不是马斯洛画的（Bridgman 等 2019 追溯到 McDermid 1960）、层次不必逐层填满、顺序可以倒置、
  晚年另有“自我超越”。研究证据（明尼苏达饥饿实验、哈洛代理母亲实验、Tay & Diener 2011 等）与“常见质疑”单独标注。

## 读书科普系列：《动物为什么吃不胖》8 讲

```bash
python3 -m nutrition.build              # 渲染全部 8 讲到 out/nutrition/epXX/
python3 -m nutrition.build 05 --sheet   # 逐镜联系表
python3 -m nutrition.build --verify     # 核验成片
python3 -m nutrition.build --publish    # 交付到 videos/nutrition/
```

依据劳本海默、辛普森《动物为什么吃不胖？》（Eat Like the Animals，范雪竹译，后浪 / 贵州人民出版社，2023）。复用阿德勒纸片引擎，
专用元件在 `nutrition/art.py`：贯穿全系列的「营养几何图」（碳水 × 蛋白质坐标、目标点、食物轨道、补偿路径），以及原创的蝗虫、黏菌、猫、狒狒、
大猩猩、小鼠、摩门蟋蟀剪影。每讲 92.6 秒，卡点规则同阿德勒系列。

| 讲 | 概念 | 片名 |
|----|------|------|
| 01 | 营养目标 | 一只蝗虫，凭什么知道该吃多少？ |
| 02 | 营养几何 | 一张图，看懂你到底吃了什么 |
| 03 | 五种食欲 | 为什么吃饱了还想来点咸的？ |
| 04 | 动物也会配餐 | 黏菌没有大脑，却会挑食 |
| 05 | 蛋白质杠杆 | 为什么低蛋白饮食让人停不下嘴？ |
| 06 | 蛋白质的代价 | 那多吃蛋白质不就好了？ |
| 07 | 超加工食品 | 是零食把蛋白质冲淡了吗？ |
| 08 | 像动物一样吃 | 把动物的智慧带回餐桌 |

- 书中观点标「原书 · 大意」，一手研究标「研究证据」（Gosby 2011、Solon-Biet 2014、Dussutour 2010、Simpson 2006 摩门蟋蟀、
  Rothman 2011 大猩猩、Martínez Steele 2018、Hall 2019 等）；相关性研究、补偿不完全、动物实验外推等局限列为「常见质疑」。
  每讲注明「不构成饮食或医疗建议」。

## 读书科普系列：《稀缺》8 讲（光效 + 钩子 + 上班族日常版）

```bash
python3 -m scarcity.build              # 渲染全部 8 讲到 out/scarcity/epXX/
python3 -m scarcity.build 02 --sheet   # 逐镜联系表
python3 -m scarcity.build --verify     # 核验成片
python3 -m scarcity.build --publish    # 交付到 videos/scarcity/（成片、封面、标题与话题；合集图与 1080×1080 封面）
```

依据穆来纳森、沙菲尔《稀缺：我们是如何陷入贫穷与忙碌的》（Scarcity, 2013），按原书章节拆成 8 讲。每讲用 20–40 岁上班族的日常场景开场，
第 2 镜一句话点明主题，drop 处概念落版。复用阿德勒纸片引擎与光效层 `adler/fx.py`（`Pops` 文字逐个弹出、`Big` 光束/扫光/星光、
`Glow`、`Rays`、`Spark`、`Counter`，镜头级 `punch` / `flashes` / `shake`），新增音色 `pop`、`ding`。制作规则见 `.claude/skills/paper-explainer-video/SKILL.md`。

| 讲 | 概念 | 片名 | 开场情境 / 研究 |
|----|------|------|------|
| 01 | 稀缺心态 | 为什么一着急，就丢三落四？ | 快迟到忘带工牌 / Radel 2012 饥饿与食物词 |
| 02 | 专注红利 | 为什么deadline前一晚，效率最高？ | 最后一晚写完 PPT / Shah 2012 |
| 03 | 管窥 | 为什么一忙起来，连妈妈的消息都忘了回？ | 未读消息 / 明尼苏达饥饿实验 |
| 04 | 带宽税 | 为什么一有心事，就容易犯低级错误？ | 月底还款走神 / Mani 2013、Carvalho 2016 |
| 05 | 借未来 | 为什么越缺，越想“先借一下”？ | 分期消费 / Shah 2012 |
| 06 | 稀缺陷阱 | 为什么总在“救火”，永远忙不完？ | 日程被补救任务填满 / Karlan 2019 |
| 07 | 余闲 | 为什么日程排满，一点意外就崩？ | 临时会议打乱日程 / St. John's 医院 |
| 08 | 跳出稀缺 | 别靠意志力，靠设计 | 待办漏项 / Karlan 2016 提醒、Shah 2015 |

## 读书科普系列：《亲密关系》10 讲（光效 + 钩子 + 恋爱日常版）

```bash
python3 -m intimacy.build              # 渲染全部 10 讲到 out/intimacy/epXX/
python3 -m intimacy.build --publish    # 交付到 videos/intimacy/（成片、封面、标题与话题；合集图与 1080×1080 封面）
```

依据罗兰·米勒《亲密关系》，按章节拆成 10 讲，沿用 `sapiens/common.py` 的留存骨架镜头模板；专用元件在 `intimacy/art.py`
（宿舍楼、斯滕伯格爱情三角、四格回应）。

| 讲 | 概念 | 片名 | 研究与质疑 |
|----|------|------|------|
| 01 | 归属需要 | 为什么一个人待久了，会莫名难受？ | Holt-Lunstad 2010（148 项研究）；相关非因果 |
| 02 | 接近性 | 为什么总会喜欢上身边的人？ | Festinger 1950 宿舍、Moreland & Beach 1992；初始印象差时反效果 |
| 03 | 相似性 | 互补的人，真的更合适吗？ | Montoya 2008（313 项研究） |
| 04 | 归因 | 他迟到一次，你就觉得他不在乎你？ | Bradbury & Fincham 1990；因果方向 |
| 05 | 四骑士 | 为什么一吵架，就越说越僵？ | Gottman；“90% 预测离婚”难以复现 |
| 06 | 投资模型 | 为什么明明不满意，却还不分手？ | Le & Agnew 2003（52 项研究） |
| 07 | 激情之爱 | 热恋期一过，就没感觉了吗？ | Acevedo & Aron 2009（25 项研究、6070 人） |
| 08 | 依恋 | 为什么有人一谈恋爱，就患得患失？ | Hazan & Shaver 1987；依恋是连续维度 |
| 09 | 嫉妒 | 为什么他给别人点个赞，你就难受？ | Muise 2009（308 人）；后续效应小 |
| 10 | 积极回应 | 对方报喜时，你只回了句“哦”？ | Gable 2004；自我报告 |

## 读书科普系列：《人类简史》10 讲（光效 + 钩子 + 上班族日常版）

```bash
python3 -m sapiens.build              # 渲染全部 10 讲到 out/sapiens/epXX/
python3 -m sapiens.build 03 --sheet   # 逐镜联系表
python3 -m sapiens.build --verify     # 核验成片
python3 -m sapiens.build --publish    # 交付到 videos/sapiens/（成片、封面、标题与话题；合集图与 1080×1080 封面）
```

依据赫拉利《人类简史：从动物到上帝》（Sapiens, 2014），按全书四部分拆成 10 讲，沿用《稀缺》的留存骨架与光效层；
固定段落的镜头模板在 `sapiens/common.py`（钩子、点题、drop、金句、重击、质疑、小练习），专用元件在 `sapiens/art.py`
（麦田、货币演变、手机余额、汉谟拉比石碑与独立宣言、留白地图、泡沫、时间轴、两条上升曲线）。

| 讲 | 概念 | 片名 | 开场情境 / 证据与质疑 |
|----|------|------|------|
| 01 | 虚构的故事 | 为什么你为公司拼命，却从没见过“它”？ | 工牌与同事 / 标致公司；McBrearty & Brooks 2000 |
| 02 | 八卦 | 为什么同事的八卦，总是停不下来？ | 摸鱼小群 / 邓巴数 150；Lindenfors 2021 |
| 03 | 农业革命 | 为什么越努力，日子反而越累？ | 加班换房贷 / Cohen & Armelagos 1984；Marciniak 2021 |
| 04 | 奢侈品陷阱 | 为什么涨了工资，还是不够花？ | 离不开的手机外卖 / 邮件例子；Brickman 1978 |
| 05 | 想象的秩序 | 为什么名校、大厂，能让人一眼高看？ | 简历标签 / 汉谟拉比法典 vs 独立宣言 |
| 06 | 金钱 | 为什么手机里一串数字，能买到一切？ | 工资到账 / 英格兰银行 2014（97% 为存款） |
| 07 | 信用 | 为什么敢背 30 年房贷？ | 房贷合同 / 密西西比泡沫 1719–1720 |
| 08 | 承认无知 | 为什么敢说“我不知道”的人，进步最快？ | 会上没人敢问 / 约 1525 年留白地图、哥伦布 |
| 09 | 幸福 | 为什么日子越过越好，你却没更快乐？ | 比爸妈那代 / Kahneman & Deaton 2010、Killingsworth 2021/2023 |
| 10 | 从动物到上帝 | 人类越来越强，为什么越来越焦虑？ | AI 与外卖 / 三场革命、结尾之问；Hallpike 书评 |

## 夜色像素风：《我们为什么假装不会死》

依据欧内斯特·贝克尔《拒斥死亡》（1973）：聊天窗「深夜树洞」开场 → 信笺写下书的主张 → drop 硬切到「办法一：不去想」→ 红笔批改「我不怕死」→
「不朽方案」6 刀加速硬切 → 最大低频重拍上雪落把「死亡，是终点。」改成「？」→ 恐惧管理理论与 1989 年法官保释金实验 → 2022 年 Many Labs 4 未能复现。
1920×1080，89 秒，时间表与混音见 `nightpixel/denial.py`（通用工具 `nightpixel/kit.py`），成片、封面、卡点表、文案在 `videos/denial/`。

## 夜色像素风：《一把伞的雪夜》

蒸馏参考视频得到的「夜色像素风」第一期：藏青雪夜像素场景 + 发光小角色 + 米黄信笺钢笔写字、红笔批改、绿章通过；
音乐 drop 硬切进故事，接力段 4/4/3/3/2/2 拍加速硬切，最大低频重拍上一片雪把「还」改成「传」。1920×1080，89 秒，
时间表与混音见 [`nightpixel/`](nightpixel/README.md)，成片、封面、卡点表、文案在 `videos/umbrella/`。

## 系列科普动画：罗杰斯心理学 10 讲

```bash
python3 -m rogers.build              # 渲染全部 10 期到 out/rogers/epXX/；也可指定期号
python3 -m rogers.build 06 --sheet   # 逐镜联系表
python3 -m rogers.build --verify     # 核验成片
python3 -m rogers.build --publish    # 交付到 videos/rogers/
```

复用阿德勒系列引擎，罗杰斯专用元件在 `rogers/art.py`（面对面的两把椅子、地窖里朝光发芽的土豆、自我与经验的两圆、
真实自我与理想自我、带价签的爱心、耳朵、脚印、录音机）。无互动答题，每期 92.6 秒，卡点规则同阿德勒系列。

| 期 | 概念 | 片名 |
|----|------|------|
| 01 | 来访者中心 | 为什么最好的帮助，是不急着给建议？ |
| 02 | 实现倾向 | 人天生想变好吗？ |
| 03 | 自我概念 | 你心里的“我”，是真的你吗？ |
| 04 | 价值条件 | 为什么总觉得表现好才配被爱？ |
| 05 | 无条件积极关注 | 接纳一个人，等于认同一切吗？ |
| 06 | 共情 | 共情就是“我懂你”吗？ |
| 07 | 真诚一致 | 为什么装出来的好会让人累？ |
| 08 | 积极倾听 | 怎样听，别人才愿意说？ |
| 09 | 充分发挥功能的人 | 好的生活是什么样？ |
| 10 | 关系的力量 | 为什么关系本身就能疗愈？ |

- 研究证据单独标注（Butler & Haigh 1954 Q 分类、Elliott 等 2018 共情元分析、Farber 等 2018、Kolden 等 2018、
  Flückiger 等 2018 咨询联盟等），“充分必要条件”中“充分”未获支持、对人性过于乐观等批评列为“常见质疑”。

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

## 无声竖屏科普：《生活没变，怎么一刷手机就落后了？》（社会比较）

`social_comparison/index.html` 是一个单文件 Canvas 动画，可以直接用浏览器打开，不依赖外部资源。播放控件放在画幅外，支持播放/暂停（空格）、重播、拖动进度和逐帧查看（← →）。按 R 进入录制模式隐藏控件，按 Esc 退出。也可以用 `?t=秒数` 打开到指定时刻，用 `?record=1&autoplay` 直接进入录制模式并开始播放。

```bash
node social_comparison/render.cjs out/social_comparison.mp4   # 逐帧导出无声 MP4（H.264 / yuv420p / 30fps / 无音频轨）
node social_comparison/render.cjs --audit                      # 检查每张文字卡的稳定显示时长、字速和安全区
```

依赖 Playwright（使用本机已有的 Chromium）和带 libx264 的 FFmpeg。分镜表与资料来源见 `social_comparison/STORYBOARD.md`。

## 竖屏短视频：《走出洞穴的人，为什么先想回头？》（梵高笔触风格）

```bash
python3 cave_short.py out/cave_allegory.mp4                 # 成片 + cover.png / cover_clean.png
python3 cave_short.py out/cave_allegory.mp4 --still 31 57   # 只渲染指定秒数的单帧，检查画面
```

柏拉图《理想国》洞穴寓言，1080×1920、30fps、约 75 秒。方案（口播、分镜、出处核对）见 `plans/cave_allegory_75s.md`。
4 核机器上渲染约 15 分钟，成片约 110MB（码率上限 12Mbps；笔触细节多，码率再低会糊）。

- **画面**：`cave_draw.py` 用 Skia 绘制每个镜头的底稿（构图、光色、人物），`engine/paint.py` 把底稿转成梵高式厚涂短笔触。
  笔触方向由两部分混合：沿轮廓的切向（结构张量），以及场景给定的流场（漩涡、光源同心环、火焰上升、水面横向）。
  三层笔触（大 / 中 / 细节）用 `drawAtlas` 一次绘制，每 2 帧重画一次（15fps 手绘节奏），并带轻微"沸腾"抖动。
- **字幕**：思源宋体，单行不超过 13 字，按 30fps 叠加。第 10、11 镜分别标注「书中原意 · 转述」「创作者联想」，片尾注明出处。
- **声音**：ZipVoice 旁白（语速 0.75）。环境音全部程序化合成：火、风、滴水、铁链、溪流、鸟鸣等，洞内声音加混响。
  配乐分三段：大提琴长音 → 出洞时抽空 0.5 秒 → 钢琴单音加弦乐，结尾停在一个长音上。

## 无声科普竖屏：《为什么你刷短视频停不下来？》

```bash
python3 fetch_assets.py                      # 只需其中的思源黑体
python3 scroll_short.py out/scroll_short.mp4 # 成片 + 竖版/横版封面
python3 scroll_short.py --still 30 61.5      # 只渲染指定时刻的单帧，用于检查
```

黑金风格、动画主导：手机第一视角开场 → 历史 → 理论 → 推荐 → 方法。
画面带辉光、扫光、光条、光球、扩散光环、微尘和镜头推拉，每 3 秒内至少一次动画事件。
1080×1920、30fps、97 秒（含 6 秒参考资料），**不含音频流**，4 核渲染约 3 分钟。
屏幕文案、分镜表、事实清单与参考资料见 `docs/scroll_short/`，成片与封面在 `docs/scroll_short/media/`。

## 竖屏无声版：《轮盘连开十次黑，下一把押红吗？》（赌徒谬误）

```bash
python3 fetch_assets.py                       # 只需其中的字体
python3 gf_short.py out/gamblers_fallacy_silent.mp4
```

按 `scripts/gamblers_fallacy.md` 的 14 镜分镜固定排时，输出 1080×1920、30fps、108 秒的无音轨视频，
同目录生成 `gamblers_fallacy_silent.srt`（口播字幕，按每秒约 4.6 字估算时间，供后期配音对位）和封面 `cover.png`。

- 只烧录分镜表"屏幕文字"一栏的标题、数字与标注，不烧录口播字幕；配音、配乐、音效均留给后期
- 画面全部矢量绘制（轮盘、记分灯、筹码、硬币、天平、抽奖机），不依赖 Emoji 与 TTS 模型
- 排时用 `Video.layout_fixed(场景时长)`，渲染用 `Video.render(..., silent=True)`

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

## 竖屏无声版：《机会成本》

```bash
python3 fetch_assets.py                # 只需其中的字体（含思源宋体）
python3 oc_short.py out/opportunity_cost_silent.mp4
python3 oc_short.py --stills out/stills 1 30.5 60   # 导出指定秒数的关键帧
```

按 [`scripts/opportunity_cost.md`](scripts/opportunity_cost.md) 的 14 镜分镜绘制，1080×1920、30fps、103 秒，无音轨，口播以字幕呈现。
角色与道具全部用 Skia 程序化手绘（米白纸张肌理 + 抖动墨线 + 胶片颗粒），4 核约 3 分钟。
改字幕或节奏：编辑 `NARRATION`（每镜口播与起止时间）和 `SHOTS`（镜头时间与转场）；画面动作用 `cue(镜号, "关键词")` 锚定到字幕念到该词的时刻。

## 无旁白科普动画：《你不是在休息，你是在为休息感到内疚》

```bash
python3 fetch_assets.py                                  # 只需字体
python3 -m rest_guilt.build --bgm path/to/bgm.m4a        # 完整成片（也会自动查找 ./bgm.m4a、assets/bgm.m4a）
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

## 横屏版

```bash
python3 dyl_video.py out/designing_your_life.mp4
```

Pillow 绘制的 1920×1080、约 44 秒讲解动画（使用系统文泉驿字体），配同一首 BGM：场景时长吸附到半小节，「好时光日志」对上音乐 drop。

## 静音竖屏短视频：逻辑训练（三人·三城·三种运动）

```bash
python3 fetch_assets.py                         # 只需其中的思源黑体字体
python3 logic/verify_logic.py                   # 制作前核验：36 种组合仅 1 个解 + 反证
python3 logic/logic_short.py out/logic_short.mp4
```

输出 1080×1920、30fps、90 秒、**无音频轨**的解题动画，以及封面 `out/logic_cover.png`。4 核机器约 1 分钟。
完整制作方案（开头、字幕脚本、分镜、动效清单、核验说明）见 `logic/production_plan.md`。

## 第三方资源许可

- [Fluent Emoji](https://github.com/microsoft/fluentui-emoji)：MIT License，© Microsoft
- [得意黑 Smiley Sans](https://github.com/atelier-anchor/smiley-sans)、[Noto Sans / Serif CJK](https://github.com/notofonts/noto-cjk)、[马善政毛笔楷书 Ma Shan Zheng](https://github.com/googlefonts/mashanzheng)：SIL Open Font License 1.1
- [three.js](https://github.com/mrdoob/three.js)：MIT License
- [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M)：Apache 2.0，通过 [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) 运行
- 逐笔书法笔画数据：[Make Me a Hanzi](https://github.com/skishore/makemeahanzi) `graphics.txt`（Arphic Public License，源自 Arphic PL KaitiM GB / UKai），由 `fetch_assets.py` 下载到 `assets/hanzi/`，不入库
- [CosyVoice](https://github.com/FunAudioLLM/CosyVoice) / Fun-CosyVoice3-0.5B：Apache 2.0（《传习录》系列旁白，仅克隆作者本人录音）
