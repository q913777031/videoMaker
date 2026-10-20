# 星座科普 12 讲（无旁白竖屏科普动画）

与阿德勒、MBTI 系列共用同一套引擎（`adler/core.py`、`adler/kit.py`），本目录放分集脚本、星座专用元件 `kit_xz.py`、
每期共用的镜头模板 `series.py` 和构建入口。卡点规则、镜头写法见 `adler/README.md`。

```bash
python3 -m xingzuo.prep_data <d3-celestial/data 目录>   # 只在更新星表时运行，生成 data/zodiac.json
python3 -m xingzuo.build 05 --sheet                      # 逐镜联系表
python3 -m xingzuo.build                                 # 渲染全部 12 期 + 番外蛇夫座（第 13 期）到 out/xingzuo/epXX/
python3 -m xingzuo.build --verify                        # 核验
python3 -m xingzuo.build --publish                       # 复制到 videos/xingzuo/
```

每期 92.6 秒，配乐 `music/bgm.m4a`，第 8 小节 drop 落版星座名。结构见 `series.py` 文件头：
钩子（占星日期 vs 太阳实际所在星座）→ 星图 → 最亮星 → 什么时候看 → 本期专属 3 镜（神话 / 中国星官 / 天文冷知识）
→ 岁差 → 研究证据 → 小练习 → 收束 → 参考资料。

星表来自 d3-celestial（BSD-3-Clause，许可证见 `data/LICENSE.d3-celestial`）；事实出处见 `事实核查.md`。
