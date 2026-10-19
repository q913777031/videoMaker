// 端午节封面：龙舟、粽子串、艾草、香囊，答题预告取第 1 题。
import { W } from '../../chongyang/web/ink.js';
import { dragonBoat, zongzi, herbBundle, sachet } from '../../chongyang/web/festive.js';
import { runCover } from '../../chongyang/web/coverkit.js';

runCover({
  title: '端午', seal: '五月初五', hook: '端午的“端”是什么意思？', opts: ['开头', '端正'],
  sprites: () => ({}),
  decorate(g, H, v) {                                   // 近景：右上粽子串与香囊、左下艾草、底部龙舟
    g.strokeStyle = '#2A2622'; g.lineWidth = 3; g.beginPath(); g.moveTo(W - 120, 0); g.lineTo(W - 120, 330); g.stroke();
    for (let i = 0; i < 3; i++) zongzi(g, W - 120 + (i % 2 ? 24 : -24), 90 + i * 95, 0.8, i % 2 ? 0.3 : -0.3);
    sachet(g, W - 250, 0, 0.3, 0.8);
    herbBundle(g, 10, H + (v ? 60 : -100), 1.1, 'ai', 5);
    dragonBoat(g, W - 280, H - (v ? 10 : 190), 0.6, 0.65, -1, 2);
  },
});
