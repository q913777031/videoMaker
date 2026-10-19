// 重阳节封面：古松、菊花、茱萸，答题预告取第 1 题。
import { W, pine, chrysanthemum, zhuyu } from './ink.js';
import { runCover } from './coverkit.js';

runCover({
  title: '重阳', seal: '九月初九', hook: '为什么叫“重阳”？', opts: ['太阳', '阳数“九”'],
  sprites: () => ({ pine: pine(3), chry: chrysanthemum(5), zhuyu: zhuyu(7, 0.9) }),
  decorate(g, H, v, SP) {                               // 近景：左下古松、右下菊花、右上茱萸
    g.drawImage(SP.pine, -120, H - SP.pine.height * 1.25 - (v ? 40 : 160), SP.pine.width * 1.25, SP.pine.height * 1.25);
    g.drawImage(SP.chry, W - 420, H - SP.chry.height * 1.35 - (v ? 0 : 60), SP.chry.width * 1.35, SP.chry.height * 1.35);
    g.save(); g.translate(W + 30, -40); g.rotate(Math.PI * 0.85);
    g.drawImage(SP.zhuyu, -SP.zhuyu.width / 2, -SP.zhuyu.height, SP.zhuyu.width, SP.zhuyu.height); g.restore();
  },
});
