# 越想赶紧解决，为什么越容易走错？

无声竖屏心理学科普短片：1080×1920、30 fps、60.000 秒（1800 帧）、H.264 yuv420p、**不含音频轨道**。

```bash
python3 fetch_assets.py          # 只需其中的 Noto CJK 字体（assets/fonts/）
python3 -m doubt.render out/doubt
```

产物：`out/doubt/越想赶紧解决越容易走错.mp4`、`cover.png`（第 3 秒画面）、`timeline_check.txt`（阅读预算核验）。
交付件在 `videos/doubt/`。全部画面为原创矢量图形，用 Skia 逐帧绘制；不使用随机数，任意帧可单独复现：
`python3 -m doubt.render out/doubt --frame 42.5`。

## 分镜

| 时间 | 主文案 | 画面动作（地图承载信息） |
|---|---|---|
| 0–6 | 越想赶紧解决，为什么越容易走错？（首帧完整） | 登山者站在岔路口：左侧地图牌（两条路线模糊），右侧山路不断变暗；他抬手迟疑地指向暗路 |
| 6–12 | 一群人迷路了。又累，又急，营地还没找到。 | 两名同伴从左侧走进、步子变慢，停在地图牌前；营地标记在地图远端闪烁 |
| 12–18 | 他们最想要的，是赶紧选一条路。 | 地图放大成主画面，两条路线仍模糊；领队指向下山方向，起点亮出箭头，其余人随之出发 |
| 18–24 | 决定做了，大家松了一口气。 | 金色路线迅速亮起，小队标记沿线移动；天际短暂回暖、队伍轻快前进 |
| 24–30 | 可走了很久，才发现：方向错了。 | 地图拉远：路线越走越远，营地留在另一侧；队伍停下，标记与营地之间出现虚线距离 |
| 30–36 | 急着结束不安，不等于找到了答案。 | 路线停住，标注“确定的路线”，与远处营地同屏；领队回头 |
| 36–42 | 先把直觉，当成一个需要验证的假设。 | 金线退回岔路口，起点箭头变虚线；放大镜聚焦岔路口，等高线细节显露；领队取出地图 |
| 42–48 | 问自己：什么迹象说明我可能错了？ | 地图上出现山脊与从湖流向下游的河流，提示“发现偏差”；领队在看图与看地形之间来回核对 |
| 48–54 | 停下来核对，有时也是在前进。 | 小队回到更高处，远山显露、视野打开；地图展开，试了两条选项被打叉，第三条更安全的路径亮起 |
| 54–60 | 你现在需要答案，还是需要先看清问题？ + 来源：Hidden Brain / Bobby Parmar | 回到开场构图，同一个登山者站在岔路口；这次面向地图牌观察（地图已带地形信息、尚未选路），停在观察动作上 |

小字“根据播客故事改编 · 情境演绎”在 6–54 秒常驻。地图与路线是视觉比喻，不是大脑结构或研究数据。

## 阅读预算（`timeline_check.txt` 实算）

每张卡入场 0.35 秒、出场 0.40 秒（首卡首帧即完整、末卡停到片尾），稳定阅读 = 出场开始 − 完全显示。
要求 = max(2 秒, 汉字数 ÷ 4.5, 分镜下限)。10 张卡稳定 5.25–5.65 秒，全部满足；来源字稳定 5.35 秒（≥4）。
卡片首尾相接于 6 秒整数倍，无空洞、无重叠，终点 60.000 秒。

## 事实依据与改动

依据：Hidden Brain，《You 2.0: Trusting Your Doubt》，嘉宾 Bobby Parmar，2026 年 1 月 26 日，
<https://www.hiddenbrain.org/podcast/you-2-0-trusting-your-doubt/>（制作时联网核对过官方页面与逐字稿）。

- 怀俄明徒步：队伍要找湖边营地，“tired and confused”；他说 “I think we should move down the mountain”；事后发现 “the lake was above us the whole time”；反思 “it was easier to keep moving than it was to admit that I was wrong”。
- 巴塔哥尼亚徒步：“hike back up the mountain so we could get a better view”，“tried out multiple different options until we found one that we felt was safest”。
- “把直觉当假设”：逐字稿中出自 Parmar 讲述的一项军事研究里经验丰富的将领（“treat their intuition not as a decision, but as a hypothesis”），片中作为延伸建议呈现，不归为登山故事，也不写成嘉宾原话。
- **改动**：原分镜第 2 卡“天快黑了”在逐字稿中没有对应（只提到要找当晚扎营的湖），已改为“营地还没找到。”，字数与阅读时间不变。
