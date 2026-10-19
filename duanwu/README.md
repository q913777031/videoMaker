# 水墨长卷科普：《端午节是怎么来的？边看边答题》

```bash
python3 -m duanwu.build                    # 完整成片 → out/duanwu/
python3 -m duanwu.build --stills 3,18      # 静帧 → out/duanwu/stills/
python3 -m duanwu.build --remux            # 只重做混音并换进已渲染成片
node ac3d/render.cjs --page duanwu/web/cover.html --stills out/duanwu/cover 0,1   # 封面：0 = 9:16，1 = 3:4（取上方 1080×1440）
```

与《重阳节》同一套水墨长卷框架（`chongyang/web/scroll.js`：长卷连续平移、两层远山视差与云雾、答题卡、字幕），
本片只有 `storyboard.json`（分镜、字幕、拍点动作与音效、`quiz` 4 道题、出处与核查说明）和 `web/main.js`（各镜小景）。
节庆小景（红梅、木门春联、鞭炮、烟花、日历页、灯笼、红包、铜钱、年兽、篝火、年夜饭）在 `chongyang/web/festive.js`，
封面版式在 `chongyang/web/coverkit.js`，本片 `web/cover.js` 只给标题、印文、钩子句、答题预告与近景装饰。
