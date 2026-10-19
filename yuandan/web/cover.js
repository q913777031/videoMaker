// 元旦封面：红梅、古松、飘雪，答题预告取第 1 题。
import { W, rng, pine } from '../../chongyang/web/ink.js';
import { plum } from '../../chongyang/web/festive.js';
import { runCover } from '../../chongyang/web/coverkit.js';

runCover({
  title: '元旦', seal: '一月一日', hook: '古代的元旦不在 1 月 1 日？', opts: ['太阳刚升起', '一天结束'],
  sprites: () => ({ pine: pine(5), plum: plum(3), plum2: plum(11) }),
  decorate(g, H, v, SP) {                               // 近景：左下古松、右上与右下红梅、飘雪
    g.drawImage(SP.pine, -120, H - SP.pine.height * 1.25 - (v ? 40 : 160), SP.pine.width * 1.25, SP.pine.height * 1.25);
    g.save(); g.translate(W + 20, 60); g.scale(-1, 1); g.drawImage(SP.plum, 0, 0); g.restore();
    g.save(); g.translate(W + 40, H - (v ? 330 : 560)); g.scale(-1.1, 1.1); g.drawImage(SP.plum2, 0, 0); g.restore();
    const r = rng(9);
    for (let i = 0; i < 120; i++) {
      const x = r() * W, y = r() * H, s = 2 + r() * 5;
      g.fillStyle = 'rgba(255,255,255,0.95)'; g.beginPath(); g.arc(x, y, s, 0, Math.PI * 2); g.fill();
      g.strokeStyle = 'rgba(120,110,100,0.25)'; g.lineWidth = 1; g.stroke();
    }
  },
});
