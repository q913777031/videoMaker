// 清明节封面：烟雨、垂柳、燕子、风筝，答题预告取第 1 题。
import { W } from '../../chongyang/web/ink.js';
import { willow, swallow, kite, rain, moon } from '../../chongyang/web/festive.js';
import { runCover } from '../../chongyang/web/coverkit.js';

runCover({
  title: '清明', seal: '四月初', hook: '清明的日子是怎么定的？', opts: ['农历日期', '太阳位置'],
  sprites: () => ({}),
  sky: (g, x, y) => moon(g, x, y, 150, 0.7),             // 烟雨里的淡日
  decorate(g, H, v) {                                   // 近景：左下垂柳、右上燕子、右下风筝、全屏细雨
    willow(g, 20, H + (v ? 140 : 0), 1.3, 1.25, 4);
    swallow(g, W - 300, v ? 140 : 170, 0.2, 1.4, 0);
    swallow(g, W - 170, v ? 220 : 260, 0.5, 1.1, 1);
    kite(g, W - 140, H - (v ? 330 : 560), 0.4, W - 60, H, 0.9);
    rain(g, 0.37, 0.9, W, H);
  },
});
