// 元宵节封面：满月、红灯笼、一碗元宵，答题预告取第 2 题。
import { W } from '../../chongyang/web/ink.js';
import { lantern, moon, tangyuanBowl } from '../../chongyang/web/festive.js';
import { runCover } from '../../chongyang/web/coverkit.js';

runCover({
  title: '元宵', seal: '正月十五', hook: '唐朝元宵节，长安取消了什么？', opts: ['赋税', '宵禁'],
  sprites: () => ({}),
  sky: (g, x, y) => moon(g, x, y, 160, 0.95),
  decorate(g, H, v) {                                   // 近景：满月（替换红日）、右上灯笼、左下一盏灯笼、右下一碗元宵
    lantern(g, W - 90, -40, 0.85, 1, 0.4, 1);
    lantern(g, W - 250, -90, 0.7, 1, 1.1, 2);
    lantern(g, 70, H - (v ? 470 : 720), 0.5, 1, 2.0, 3);
    tangyuanBowl(g, W - 160, H - (v ? 10 : 120), 0.5, 0.75);
  },
});
