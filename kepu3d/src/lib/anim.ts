/** 动画数学：全部是时间（秒）的纯函数，同一时刻永远得到同一画面（Remotion 逐帧渲染要求）。 */

export type V3 = [number, number, number];

export const clamp = (x: number, a = 0, b = 1): number => Math.min(b, Math.max(a, x));
export const prog = (t: number, a: number, d: number): number => (d <= 0 ? (t >= a - 1e-6 ? 1 : 0) : clamp((t - a) / d));
export const easeIn = (x: number): number => x * x * x;
export const easeOut = (x: number): number => 1 - Math.pow(1 - x, 3);
export const easeIO = (x: number): number => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
export const lerp = (a: number, b: number, x: number): number => a + (b - a) * x;
export const mix3 = (a: V3, b: V3, x: number): V3 => [lerp(a[0], b[0], x), lerp(a[1], b[1], x), lerp(a[2], b[2], x)];

/** 撞击脉冲：at 之前为 0，at 帧为 1，之后在 d 秒内按平方衰减到 0。 */
export const pulse = (t: number, at: number, d = 0.4): number => (t < at - 1e-6 ? 0 : Math.pow(1 - clamp((t - at) / d), 2));

/** 落定进度：at 之前 dur 秒内按 ease-in 加速，at 帧恰好到 1（撞击帧是变化最大的一帧）。 */
export const land = (t: number, at: number, dur = 0.5): number => easeIn(prog(t, at - dur, dur));

/** 已发生：t 到达 at 帧后为 true。 */
export const after = (t: number, at: number): boolean => t >= at - 1e-6;

/** 可复现的伪随机数。 */
export const rng = (seed: number) => {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let r = Math.imul(a ^ (a >>> 15), 1 | a);
    r = (r + Math.imul(r ^ (r >>> 7), 61 | r)) ^ r;
    return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
  };
};

/** 平滑噪声（0–1），用于摇晃、呼吸光。 */
export const wobble = (t: number, seed = 0): number =>
  0.5 + 0.25 * Math.sin(t * 1.3 + seed) + 0.15 * Math.sin(t * 2.9 + seed * 1.7) + 0.1 * Math.sin(t * 6.1 + seed * 0.3);

/** 闪烁（0–1）：灯管接触不良式的明灭，按 30fps 帧量化。 */
export const flicker = (t: number, seed = 0, depth = 0.7): number => {
  const f = Math.floor(t * 30);
  const r = rng(f * 7919 + seed * 104729)();
  const dip = r < 0.18 ? depth : r < 0.3 ? depth * 0.4 : 0;
  return 1 - dip;
};
