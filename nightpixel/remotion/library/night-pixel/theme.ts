import type React from 'react';
import '../vox/theme';
import {clamp01} from '../anim';

/**
 * 夜色像素风：深藏青夜色里的像素小场景，一处暖光、会发光的方块小角色，加上一张米黄横线信笺写字、红笔批改。
 * 配色只用四类：藏青夜（底）、暖窗黄（唯一光源）、米黄信笺（文字载体）、批改红 / 通过绿（只在信笺上出现）。
 */
export const NP = {
  night: '#171a28', // 主底色：藏青夜
  night2: '#212738', // 远景楼、墙
  deep: '#10111b', // 地面、暗部
  ink: '#070a11', // 暗角最深处
  dusk: '#3f5065', // 冷蓝：玻璃、远处灯
  sky: '#6286ab', // 冷蓝高光
  warm: '#e4c988', // 暖窗黄：窗格、台灯，唯一的暖光源
  warmDeep: '#ac8f65',
  wood: '#8e604d', // 木桌、地板
  woodDark: '#634b3c',
  paper: '#eedebc', // 信笺
  paperEdge: '#d8c9a8',
  paperLine: 'rgba(120,96,60,0.16)', // 信笺横线
  inkText: '#2a2118', // 信笺正文
  inkSoft: '#6b6150', // 信笺抬头小字
  cream: '#d8ccb1', // 标签、字幕
  sub: '#e2e3e6',
  red: '#c9473a', // 红笔批改
  green: '#4f9a5a', // 通过章
  bubbleMe: '#8fd46a', // 聊天窗：我方气泡
  bubbleThem: '#f3f1ec',
  window: '#191d2c', // 聊天窗底
  windowBar: '#11141f',
};

/** 字体：信笺用宋体（衬线、像钢笔字），字幕和标签用粗黑体，等宽数字用系统等宽 */
export const NPF = {
  card: `'Songti SC', 'Noto Serif SC', 'STSong', 'Source Han Serif SC', serif`,
  sub: `'PingFang SC', 'Noto Sans SC', 'Microsoft YaHei', sans-serif`,
  ui: `'PingFang SC', 'Noto Sans SC', sans-serif`,
  mono: `'SF Mono', 'Menlo', 'Consolas', monospace`,
};

/** 像素单位：1920×1080 画布上一个「像素」= 8px（原片 960 宽时约 4px） */
export const PX = 8;

/** 糊化交叉：透明度 + 模糊一起变，约 10 帧完成；信笺 ↔ 场景之间都用它 */
export const dissolve = (f: number, at: number, dur = 10, out?: number, outDur = 10) => {
  const i = clamp01((f - at) / dur);
  const o = out === undefined ? 1 : 1 - clamp01((f - out) / outDur);
  const v = Math.min(i, o);
  return {opacity: v, filter: `blur(${(1 - v) * 12}px)`, v};
};

/** 淡入：字幕、章节标签在画面稳定后 6～8 帧淡入 */
export const fade = (f: number, at: number, dur = 7, out?: number, outDur = 7) => {
  const i = clamp01((f - at) / dur);
  const o = out === undefined ? 1 : 1 - clamp01((f - out) / outDur);
  return Math.min(i, o);
};

/** 写字进度：从 at 起每 per 帧写出一个字，返回已写出的字数（小数部分是正在写的那一笔） */
export const written = (f: number, at: number, n: number, per = 5) => Math.max(0, Math.min(n, (f - at) / per));

/** 景深：前景 / 远景的模糊量（px），原片远景常虚、焦点在角色 */
export const dof = (depth: number) => `blur(${Math.abs(depth) * 6}px)`;

/** 发光：方块角色和光点外面一圈柔光 */
export const bloom = (color: string, r = 24, a = 0.75): React.CSSProperties => ({
  filter: `drop-shadow(0 0 ${r * 0.3}px ${hexA(color, Math.min(1, a))}) drop-shadow(0 0 ${r}px ${hexA(color, a * 0.7)}) drop-shadow(0 0 ${r * 2}px ${hexA(color, a * 0.35)})`,
});

/** #rrggbb + 透明度 → rgba() */
export const hexA = (hex: string, a: number) => {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
};

/**
 * 硬切加速表：传入每段镜头的帧数（原片的接力段是 36 → 27 → 18 帧，越切越快），
 * 返回当前帧落在第几段、段内帧号。
 */
export const cutAt = (t: number, lens: number[]) => {
  let acc = 0;
  for (let i = 0; i < lens.length; i++) {
    if (t < acc + lens[i]) return {i, t: t - acc, len: lens[i]};
    acc += lens[i];
  }
  const last = lens.length - 1;
  return {i: last, t: t - (acc - lens[last]), len: lens[last]};
};
