# 明朝皇帝系列（无旁白竖屏历史动画）

每期一位皇帝，从朱元璋开始。结构：问题钩子开头（8 小节）→ 第 8 小节 drop 落版皇帝名 → 按《明史》时间线讲生平 → 结尾两镜高光。
叙事节奏参考当年明月《明朝那些事儿》，史实以《明史》为准，不引用原书文字。与其他系列共用引擎（`adler/core.py`、`adler/kit.py`）。

```bash
python3 -m mingchao.build 01 --sheet     # 逐镜联系表
python3 -m mingchao.build 01             # 渲染到 out/mingchao/ep01/
python3 -m mingchao.build --verify
python3 -m mingchao.build --publish      # 复制到 videos/mingchao/
```

| 期 | 皇帝 | 标题 |
|----|------|------|
| 01 | 朱元璋 | 一个连父母都埋不起的穷孩子，怎么当上了皇帝？ |
