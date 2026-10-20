import {describe, expect, it} from 'vitest';
import {cutAt, dissolve, fade, hexA, written} from '../../src/library/night-pixel/theme';

describe('夜色像素风 night-pixel', () => {
  it('糊化交叉 10 帧完成，进出对称', () => {
    expect(dissolve(0, 10).v).toBe(0);
    expect(dissolve(20, 10).v).toBe(1);
    expect(dissolve(15, 10).v).toBeCloseTo(0.5, 5);
    expect(dissolve(35, 10, 10, 30).v).toBeCloseTo(0.5, 5);
  });

  it('写字每 5 帧一个字，不超过总字数', () => {
    expect(written(0, 10, 6)).toBe(0);
    expect(written(20, 10, 6)).toBe(2);
    expect(written(999, 10, 6)).toBe(6);
  });

  it('加速硬切表：36 → 27 → 18 帧依次落段', () => {
    const lens = [36, 27, 18];
    expect(cutAt(0, lens)).toEqual({i: 0, t: 0, len: 36});
    expect(cutAt(36, lens).i).toBe(1);
    expect(cutAt(63, lens)).toEqual({i: 2, t: 0, len: 18});
    expect(cutAt(200, lens).i).toBe(2);
  });

  it('淡入与颜色工具', () => {
    expect(fade(3, 0, 6)).toBeCloseTo(0.5, 5);
    expect(hexA('#e4c988', 0.5)).toBe('rgba(228,201,136,0.5)');
  });
});
