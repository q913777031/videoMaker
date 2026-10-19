// 春节封面：红灯笼、鞭炮、红梅，答题预告取第 1 题。
import { W } from '../../chongyang/web/ink.js';
import { plum, lantern, firecrackers } from '../../chongyang/web/festive.js';
import { runCover } from '../../chongyang/web/coverkit.js';

runCover({
  title: '春节', seal: '正月初一', hook: '最早的“爆竹”是什么？', opts: ['纸卷火药', '烧竹子'],
  sprites: () => ({ plum: plum(3) }),
  decorate(g, H, v, SP) {                               // 近景：右上一对红灯笼、左下鞭炮串、右下红梅
    lantern(g, W - 90, -40, 0.85, 1, 0.4, 1);
    lantern(g, W - 250, -90, 0.7, 1, 1.1, 2);
    firecrackers(g, 60, H - (v ? 600 : 820), 0.6, 8, 1.0);
    g.save(); g.translate(W + 40, H - (v ? 330 : 560)); g.scale(-1.1, 1.1); g.drawImage(SP.plum, 0, 0); g.restore();
  },
});
