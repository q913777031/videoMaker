# MBTI 科普 10 讲（无旁白竖屏科普动画）

与阿德勒 10 讲共用同一套引擎（`adler/core.py` 时间轴、渲染、混音与文档输出，`adler/kit.py` 纸片剪影元件），
本目录只放本系列的分集脚本、专用元件 `kit_mbti.py` 和构建入口。卡点规则、镜头写法、元素参数见 `adler/README.md`。

```bash
python3 fetch_assets.py              # 只需其中的字体
python3 -m mbti.build                # 渲染全部 10 期到 out/mbti/epXX/
python3 -m mbti.build 03 07          # 只渲染指定期
python3 -m mbti.build 03 --sheet     # 逐镜联系表 out/mbti/stills/sheet_ep03.png
python3 -m mbti.build 03 --still 17.5
python3 -m mbti.build --verify       # 核验成片，写 out/mbti/核验.md
python3 -m mbti.build --publish      # 复制成片、封面、卡点表、文案与出处到 videos/mbti/
```

每期 1080×1920、30fps、92.6 秒，配乐 `music/bgm.m4a`，第 8 小节 drop 落版概念名。
系列名、文件名前缀通过 `Episode(series="MBTI 科普", file_prefix="MBTI")` 传入（阿德勒系列用默认值）。

| 期 | 概念 | 标题 |
|----|------|------|
| 01 | 四个字母 | 那四个字母，到底是谁发明的？ |
| 02 | 外向与内向 | 内向的人，就是不爱说话吗？ |
| 03 | 实感与直觉 | 看同一幅画，你先注意到什么？ |
| 04 | 思考与情感 | 讲道理的人，就没有感情吗？ |
| 05 | 判断与知觉 | 做计划的人，一定更自律吗？ |
| 06 | 16型 | 16 种人格，是怎么拼出来的？ |
| 07 | 网络测试 | 你测的，真的是 MBTI 吗？ |
| 08 | 巴纳姆效应 | 为什么人格测试，总觉得说得准？ |
| 09 | 科学争议 | MBTI，到底科学吗？ |
| 10 | 正确使用 | 四个字母，是标签还是语言？ |

## 专用元件（`kit_mbti.py`）

| 函数 | 用途 |
|------|------|
| `tile` / `code` | 字母牌 / 一排四字母，八个字母各有固定配色（`DIM`） |
| `scale_bar` | 偏好量尺：两端字母，滑块位置 -1…1 |
| `bell` | 单峰分布曲线，可画中线切分与直方柱 |
| `battery` | 电量（E/I 的充电隐喻） |
| `quiz` / `report` | 测试题卡 / 人格报告纸（逐行高亮、打勾） |
| `tag` / `stamp` / `book` / `signature` | 胸牌、年份印章、书、签名笔迹 |
| `appear` / `pulse` / `wiggle` | 按拍弹出进度、按拍弹跳、量尺滑块犹豫后停下 |

事实出处与表述取舍见 `事实核查.md`。
