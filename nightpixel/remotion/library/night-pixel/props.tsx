import React from 'react';
import {clamp01, easeOut, easeOutBack, rand} from '../anim';
import {bloom, fade, hexA, NP, NPF, written} from './theme';

/**
 * 夜色像素风的实物和道具：发光的像素小豆子角色、接力光点、横线信笺（写字 + 钢笔尖 + 红笔批改 + 雪落改标点）、
 * 通过章、深色聊天窗。坐标都是 1920×1080 画布上的像素。
 */

// ---------------------------------------------------------------- 角色

type Mood = 'calm' | 'happy' | 'sad' | 'sleepy' | 'wow';

/**
 * 像素小豆子：圆角豆形身体 + 头顶一片小芽 + 2×2 大眼（带高光）+ 腮红，自己会发光。
 * (x, y) 是脚底中点，u 是一个像素格的大小；bob 每 16 帧上下 1 格，blink 每 90 帧眨一次眼。
 */
export const PixelPal: React.FC<{f: number; x: number; y: number; u?: number; color?: string; mood?: Mood; glow?: number; face?: 1 | -1; seed?: number; sprout?: boolean}> = ({
  f,
  x,
  y,
  u = 8,
  color = '#f2efe6',
  mood = 'calm',
  glow = 1,
  face = 1,
  seed = 0,
  sprout = true,
}) => {
  const W = 14;
  const H = 13;
  const bob = Math.floor(((f + seed * 7) / 16) % 2);
  const blink = (f + seed * 23) % 90 < 4;
  const shade = shadeOf(color, 0.82);
  // 豆形：每行的左右缩进（格）
  const rows = [5, 3, 2, 1, 1, 0, 0, 0, 0, 0, 1, 1, 3];
  const px: React.ReactNode[] = [];
  rows.forEach((ind, r) => px.push(<rect key={`r${r}`} x={ind} y={r} width={W - ind * 2} height={1} fill={r > 9 ? shade : color} />));
  const ex = face === 1 ? [4, 8] : [3, 7];
  const eyeY = mood === 'sleepy' ? 6 : 5;
  ex.forEach((e, i) => {
    if (blink || mood === 'sleepy') px.push(<rect key={`e${i}`} x={e} y={eyeY + 1} width={2} height={1} fill={NP.inkText} />);
    else if (mood === 'happy') {
      px.push(<rect key={`e${i}a`} x={e} y={eyeY + 1} width={1} height={1} fill={NP.inkText} />);
      px.push(<rect key={`e${i}b`} x={e + 1} y={eyeY} width={1} height={1} fill={NP.inkText} />);
    } else {
      px.push(<rect key={`e${i}`} x={e} y={eyeY} width={2} height={mood === 'wow' ? 3 : 2} fill={NP.inkText} />);
      px.push(<rect key={`h${i}`} x={e} y={eyeY} width={1} height={1} fill="#ffffff" />);
    }
  });
  px.push(<rect key="bl" x={ex[0] - 2} y={8} width={2} height={1} fill="#e79a9a" opacity={0.85} />);
  px.push(<rect key="br" x={ex[1] + 2} y={8} width={2} height={1} fill="#e79a9a" opacity={0.85} />);
  if (mood === 'sad') px.push(<rect key="tear" x={ex[0]} y={eyeY + 2} width={1} height={2} fill={NP.sky} />);
  if (mood === 'wow') px.push(<rect key="m" x={6} y={9} width={2} height={2} fill={NP.inkText} />);
  if (sprout) {
    px.push(<rect key="s1" x={7} y={-2} width={1} height={2} fill="#5f9a54" />);
    px.push(<rect key="s2" x={8} y={-3} width={2} height={1} fill="#7cbf6a" />);
    px.push(<rect key="s3" x={5} y={-2} width={2} height={1} fill="#7cbf6a" />);
  }
  px.push(<rect key="f1" x={3} y={13} width={2} height={1} fill={shadeOf(color, 0.6)} />);
  px.push(<rect key="f2" x={9} y={13} width={2} height={1} fill={shadeOf(color, 0.6)} />);
  return (
    <div style={{position: 'absolute', left: x - (W * u) / 2, top: y - (H + 1) * u - bob * u, width: W * u, height: (H + 4) * u, ...(glow > 0 ? bloom(color, 46 * glow, glow) : {})}}>
      <svg viewBox={`0 -3 ${W} ${H + 4}`} width={W * u} height={(H + 4) * u} shapeRendering="crispEdges" style={{overflow: 'visible'}}>
        {px}
      </svg>
    </div>
  );
};

const shadeOf = (hex: string, k: number) => {
  const n = parseInt(hex.slice(1), 16);
  const c = (v: number) => Math.round(v * k).toString(16).padStart(2, '0');
  return `#${c((n >> 16) & 255)}${c((n >> 8) & 255)}${c(n & 255)}`;
};

/** 接力光点：从 a 飞到 b（at 起 dur 帧，先快后慢），带一条渐隐的拖尾；到达后在 b 处轻轻一闪 */
export const LightOrb: React.FC<{f: number; at: number; dur?: number; a: [number, number]; b: [number, number]; color?: string; arc?: number}> = ({f, at, dur = 20, a, b, color = NP.warm, arc = 40}) => {
  const t = (f - at) / dur;
  if (t < 0 || t > 1.6) return null;
  const pos = (p: number): [number, number] => {
    const e = easeOut(clamp01(p));
    return [a[0] + (b[0] - a[0]) * e, a[1] + (b[1] - a[1]) * e - Math.sin(Math.PI * e) * arc];
  };
  const head = pos(t);
  const flash = t > 1 ? 1 - (t - 1) / 0.6 : 0;
  return (
    <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0, pointerEvents: 'none', ...bloom(color, 26, 0.9)}}>
      {Array.from({length: 8}, (_, i) => {
        const p = pos(t - i * 0.05);
        return t - i * 0.05 > 0 && t <= 1.05 ? <rect key={i} x={p[0] - 6 + i} y={p[1] - 6 + i} width={12 - i * 1.4} height={12 - i * 1.4} fill={color} opacity={0.9 - i * 0.11} /> : null;
      })}
      {t <= 1 ? <rect x={head[0] - 8} y={head[1] - 8} width={16} height={16} fill="#fff6dc" /> : null}
      {flash > 0 ? <circle cx={b[0]} cy={b[1]} r={20 + (1 - flash) * 40} fill="none" stroke={color} strokeWidth={4} opacity={flash} /> : null}
    </svg>
  );
};

// ---------------------------------------------------------------- 信笺

/** 一稿：text 从 at 起逐字写出；marks 是要红圈的字序号，strikeAt 起红线划掉整行，note 是红笔批注 */
export type Draft = {text: string; at: number; per?: number; marks?: number[]; markAt?: number; strikeAt?: number; note?: string; noteAt?: number};

/**
 * 横线信笺：米黄纸 + 淡横线 + 微旋转 + 柔投影；抬头一行小字，正文按稿逐字写出，写字处有一支钢笔尖。
 * drafts 依次替换（上一稿 6 帧淡出），可红圈、划掉、红笔批注；stamp 是右下角的通过章；
 * swap 是招牌动作「雪落标点」：一片雪落在第 index 个字上，at 那一帧它变成 to。
 */
export const NoteCard: React.FC<{
  f: number;
  at: number;
  header?: string;
  drafts: Draft[];
  w?: number;
  h?: number;
  x?: number;
  y?: number;
  size?: number;
  rot?: number;
  align?: 'left' | 'center';
  stamp?: {text: string; at: number};
  swap?: {index: number; to: string; at: number; fall?: number};
}> = ({f, at, header, drafts, w = 1280, h = 460, x = 320, y = 200, size = 100, rot = -0.8, align = 'left', stamp, swap}) => {
  const enter = clamp01((f - at) / 10);
  if (enter <= 0) return null;
  let k = 0;
  drafts.forEach((d, i) => {
    if (f >= d.at) k = i;
  });
  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y + (1 - easeOut(enter)) * 30,
        width: w,
        height: h,
        opacity: enter,
        transform: `rotate(${rot}deg)`,
        background: `linear-gradient(180deg, #f3e5c4 0%, ${NP.paper} 40%, #e6d6b4 100%)`,
        borderRadius: 6,
        boxShadow: '0 30px 60px rgba(0,0,0,0.55), 0 4px 10px rgba(0,0,0,0.35), inset 0 0 40px rgba(150,120,70,0.18)',
        overflow: 'hidden',
      }}
    >
      <div style={{position: 'absolute', inset: 0, backgroundImage: `repeating-linear-gradient(180deg, rgba(0,0,0,0) 0 43px, ${NP.paperLine} 43px 45px)`}} />
      {header ? (
        <>
          <div style={{position: 'absolute', left: 0, right: 0, top: 38, textAlign: 'center', fontFamily: NPF.card, fontSize: 40, color: NP.inkSoft, letterSpacing: 3}}>{header}</div>
          <div style={{position: 'absolute', left: 60, right: 60, top: 104, height: 2, background: 'rgba(110,90,60,0.22)'}} />
        </>
      ) : null}
      {drafts.map((d, i) => {
        if (i > k || (i < k && f > drafts[k].at + 6)) return null;
        const alpha = i < k ? 1 - clamp01((f - drafts[k].at) / 6) : 1;
        return <DraftLine key={i} f={f} d={d} size={size} alpha={alpha} align={align} top={header ? 130 : 0} h={header ? h - 130 : h} swap={i === drafts.length - 1 ? swap : undefined} pen={i === k} />;
      })}
      {stamp ? <PassStamp f={f} at={stamp.at} text={stamp.text} /> : null}
    </div>
  );
};

const DraftLine: React.FC<{f: number; d: Draft; size: number; alpha: number; align: 'left' | 'center'; top: number; h: number; swap?: {index: number; to: string; at: number; fall?: number}; pen: boolean}> = ({
  f,
  d,
  size,
  alpha,
  align,
  top,
  h,
  swap,
  pen,
}) => {
  const chars = [...d.text];
  const n = written(f, d.at, chars.length, d.per ?? 5);
  const shown = Math.floor(n);
  const writing = n < chars.length;
  const strike = d.strikeAt === undefined ? 0 : clamp01((f - d.strikeAt) / 8);
  const note = d.noteAt === undefined ? 0 : fade(f, d.noteAt, 6);
  return (
    <div style={{position: 'absolute', left: 90, right: 90, top, height: h, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: align === 'center' ? 'center' : 'flex-start', opacity: alpha}}>
      <div style={{position: 'relative', fontFamily: NPF.card, fontSize: size, color: NP.inkText, letterSpacing: size * 0.06, whiteSpace: 'nowrap', lineHeight: 1.2}}>
        {chars.map((c, i) => {
          if (i > shown) return null;
          const a = i < shown ? 1 : n - shown;
          const isSwap = swap && i === swap.index;
          const ch = isSwap && f >= swap.at ? swap.to : c === ' ' ? '\u00a0' : c;
          const mark = d.marks?.includes(i) ? clamp01((f - (d.markAt ?? 0) - d.marks.indexOf(i) * 6) / 8) : 0;
          return (
            <span key={i} style={{position: 'relative', display: 'inline-block', opacity: a}}>
              {ch}
              {mark > 0 ? <RedRing p={mark} size={size} /> : null}
              {isSwap ? <FallingFlake f={f} at={swap.at} fall={swap.fall ?? 40} size={size} /> : null}
            </span>
          );
        })}
        {pen && writing && n > 0.01 ? <PenNib size={size} f={f} /> : null}
        {strike > 0 ? <div style={{position: 'absolute', left: -6, top: '54%', height: 5, width: `calc(${strike * 100}% + 12px)`, background: NP.red, borderRadius: 3, opacity: 0.9}} /> : null}
      </div>
      {d.note ? (
        <div style={{marginTop: 18, opacity: note, display: 'flex', alignItems: 'center', gap: 12, fontFamily: NPF.card, fontSize: 30, color: NP.red}}>
          <svg width={26} height={26} viewBox="0 0 26 26">
            <path d="M4 4 L22 22 M22 4 L4 22" stroke={NP.red} strokeWidth={4} strokeLinecap="round" />
          </svg>
          {d.note}
        </div>
      ) : null}
    </div>
  );
};

/** 钢笔尖：斜着停在正在写的那个字的右上方，随笔画轻微抖动 */
const PenNib: React.FC<{size: number; f: number}> = ({size, f}) => (
  <span style={{position: 'relative', display: 'inline-block', width: 0}}>
    <svg width={size * 0.5} height={size * 0.7} viewBox="0 0 20 28" style={{position: 'absolute', left: -size * 0.5 + Math.sin(f * 1.7) * 2, top: -size * 0.95 - size * 0.1 + Math.cos(f * 2.3) * 2}}>
      <path d="M17 1 L19 3 L5 24 L2 26 L3 22 Z" fill="#2a2118" />
      <path d="M17 1 L19 3 L16 7 L13 5 Z" fill="#d9b25a" />
    </svg>
  </span>
);

/** 红笔圈：一笔画出的椭圆，p 为画出进度 */
const RedRing: React.FC<{p: number; size: number}> = ({p, size}) => {
  const L = 3.4 * size;
  return (
    <svg width={size * 1.3} height={size * 1.3} viewBox="0 0 100 100" style={{position: 'absolute', left: -size * 0.1, top: -size * 0.08, overflow: 'visible'}}>
      <ellipse cx={50} cy={48} rx={46} ry={44} fill="none" stroke={NP.red} strokeWidth={5} strokeDasharray={L} strokeDashoffset={L * (1 - p)} transform="rotate(-70 50 48)" />
    </svg>
  );
};

/** 雪片：从字的上方缓缓飘落，at 那一帧落到字上，之后化掉 */
const FallingFlake: React.FC<{f: number; at: number; fall: number; size: number}> = ({f, at, fall, size}) => {
  const t = (f - (at - fall)) / fall;
  if (t < 0 || t > 1.5) return null;
  const e = clamp01(t);
  const melt = t > 1 ? 1 - (t - 1) / 0.5 : 1;
  const s = size * 0.22;
  return (
    <span style={{position: 'absolute', left: size * 0.12 + Math.sin(e * 6) * size * 0.25, top: -size * 2.2 + e * size * 2.5, width: s, height: s, opacity: melt, filter: 'drop-shadow(0 0 6px rgba(255,255,255,0.9))'}}>
      <svg width={s} height={s} viewBox="0 0 10 10" shapeRendering="crispEdges">
        <rect x={4} y={0} width={2} height={10} fill="#ffffff" />
        <rect x={0} y={4} width={10} height={2} fill="#ffffff" />
        <rect x={2} y={2} width={6} height={6} fill="#ffffff" opacity={0.6} />
      </svg>
    </span>
  );
};

/** 通过章：右下角绿色细框小章，从 1.6 倍砸到 1 倍（6 帧），微微倾斜 */
export const PassStamp: React.FC<{f: number; at: number; text: string; right?: number; bottom?: number}> = ({f, at, text, right = 60, bottom = 44}) => {
  const p = clamp01((f - at) / 6);
  if (p <= 0) return null;
  const s = 1.6 - 0.6 * easeOutBack(p);
  return (
    <div
      style={{
        position: 'absolute',
        right,
        bottom,
        transform: `rotate(-8deg) scale(${s})`,
        opacity: Math.min(1, p * 2) * 0.92,
        border: `3px solid ${NP.green}`,
        borderRadius: 6,
        padding: '6px 16px',
        display: 'flex',
        alignItems: 'center',
        gap: 10,
        fontFamily: NPF.card,
        fontWeight: 700,
        fontSize: 38,
        color: NP.green,
        background: 'rgba(79,154,90,0.08)',
      }}
    >
      {text}
      <svg width={26} height={22} viewBox="0 0 26 22">
        <path d="M2 12 L10 20 L24 3" stroke={NP.green} strokeWidth={4} fill="none" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </div>
  );
};

// ---------------------------------------------------------------- 聊天窗

export type Bubble = {side: 'me' | 'them'; text: string; at: number; label?: string};

/**
 * 深色聊天窗：左上三个小圆点 + 居中标题；右侧绿色「我方」气泡、左侧白色「对方」气泡（可带一行小标签），
 * 气泡 6 帧弹出；typing 期间底部显示「正在输入」三个跳动方点。
 */
export const ChatWindow: React.FC<{f: number; at: number; title: string; bubbles: Bubble[]; typing?: [number, number]; typingLabel?: string; x?: number; y?: number; w?: number; h?: number}> = ({
  f,
  at,
  title,
  bubbles,
  typing,
  typingLabel,
  x = 420,
  y = 60,
  w = 1080,
  h = 820,
}) => {
  const a = fade(f, at, 10);
  if (a <= 0) return null;
  return (
    <div style={{position: 'absolute', left: x, top: y, width: w, height: h, opacity: a, background: NP.window, borderRadius: 18, boxShadow: '0 40px 90px rgba(0,0,0,0.6)', overflow: 'hidden', fontFamily: NPF.ui}}>
      <div style={{height: 64, background: NP.windowBar, display: 'flex', alignItems: 'center', position: 'relative'}}>
        {['#e0605a', '#e2b44a', '#5fbf5a'].map((c, i) => (
          <div key={i} style={{width: 16, height: 16, borderRadius: 8, background: c, marginLeft: i === 0 ? 26 : 10}} />
        ))}
        <div style={{position: 'absolute', left: 0, right: 0, textAlign: 'center', fontSize: 28, color: hexA(NP.cream, 0.85), letterSpacing: 2}}>{title}</div>
      </div>
      <div style={{position: 'absolute', left: 40, right: 40, top: 100, display: 'flex', flexDirection: 'column', gap: 30}}>
        {bubbles.map((b, i) => {
          const p = clamp01((f - b.at) / 6);
          if (p <= 0) return null;
          return (
            <div key={i} style={{alignSelf: b.side === 'me' ? 'flex-end' : 'flex-start', opacity: p, transform: `scale(${0.9 + 0.1 * easeOutBack(p)})`, transformOrigin: b.side === 'me' ? 'right center' : 'left center'}}>
              {b.label ? <div style={{fontSize: 26, color: hexA(NP.cream, 0.8), margin: '0 0 8px 6px', fontWeight: 700}}>{b.label}</div> : null}
              <div style={{background: b.side === 'me' ? NP.bubbleMe : NP.bubbleThem, color: NP.inkText, borderRadius: 14, padding: '16px 26px', fontSize: 40, fontFamily: NPF.card}}>{b.text}</div>
            </div>
          );
        })}
      </div>
      {typing && f >= typing[0] && f < typing[1] ? (
        <div style={{position: 'absolute', left: 50, bottom: 140, display: 'flex', alignItems: 'center', gap: 14, color: hexA(NP.cream, 0.75), fontSize: 30}}>
          {typingLabel}
          {[0, 1, 2].map((i) => (
            <div key={i} style={{width: 12, height: 12, background: NP.cream, transform: `translateY(${Math.sin((f - typing[0]) / 4 - i) * 4}px)`, opacity: 0.8}} />
          ))}
        </div>
      ) : null}
      <div style={{position: 'absolute', left: 30, right: 30, bottom: 30, height: 70, borderRadius: 12, background: '#232838', display: 'flex', alignItems: 'center', justifyContent: 'flex-end', paddingRight: 14}}>
        <div style={{width: 46, height: 46, borderRadius: 23, background: '#4fbf5a', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
          <svg width={20} height={20} viewBox="0 0 20 20">
            <path d="M5 3 L17 10 L5 17 Z" fill="#fff" />
          </svg>
        </div>
      </div>
    </div>
  );
};

/** 行人：给场景补几个虚化的路人小豆子（前景 / 远景），seed 决定颜色 */
export const Passerby: React.FC<{f: number; x: number; y: number; u?: number; seed: number; blur?: number}> = ({f, x, y, u = 7, seed, blur = 4}) => {
  const cols = ['#cfd3dc', '#b9a3c9', '#e7b6b0', '#a9c6b4', '#e3d39a'];
  return (
    <div style={{position: 'absolute', inset: 0, filter: `blur(${blur}px)`, opacity: 0.8}}>
      <PixelPal f={f} x={x} y={y} u={u} color={cols[Math.floor(rand(seed) * cols.length)]} glow={0.2} seed={seed} sprout={false} />
    </div>
  );
};

/**
 * 像素雨伞：阶梯形伞面 + 伞骨分格 + J 形伞柄；(x, y) 是伞柄底端，u 是像素格大小。
 * 雪天场景里可以当「被传递的东西」，伞面顶上会积一点雪（snow 0–1）。
 */
export const PixelUmbrella: React.FC<{x: number; y: number; u?: number; color?: string; snow?: number; tilt?: number; glow?: number}> = ({x, y, u = 8, color = '#c99a4a', snow = 0.6, tilt = 0, glow = 0.5}) => {
  const rows = [
    [6, 8],
    [4, 12],
    [2, 16],
    [1, 18],
    [0, 20],
  ];
  const dark = shadeOf(color, 0.72);
  const px: React.ReactNode[] = [];
  rows.forEach(([x0, w], r) => px.push(<rect key={`c${r}`} x={x0} y={r} width={w} height={1} fill={r === 4 ? dark : color} />));
  [4, 8, 12, 16].forEach((cx, i) => px.push(<rect key={`rib${i}`} x={cx} y={3} width={1} height={2} fill={dark} />));
  if (snow > 0) px.push(<rect key="snow" x={6} y={-1} width={8} height={1} fill="#f2f4fa" opacity={snow} />);
  px.push(<rect key="tip" x={9} y={-2} width={2} height={1} fill={dark} />);
  px.push(<rect key="pole" x={9} y={5} width={2} height={14} fill="#3a3530" />);
  px.push(<rect key="hook1" x={7} y={19} width={4} height={1} fill="#3a3530" />);
  px.push(<rect key="hook2" x={7} y={18} width={1} height={1} fill="#3a3530" />);
  return (
    <div style={{position: 'absolute', left: x - 10 * u, top: y - 22 * u, width: 20 * u, height: 22 * u, transform: `rotate(${tilt}deg)`, transformOrigin: '50% 100%', ...(glow > 0 ? bloom(color, 18 * glow, glow * 0.6) : {})}}>
      <svg viewBox="0 -2 20 22" width={20 * u} height={22 * u} shapeRendering="crispEdges">
        {px}
      </svg>
    </div>
  );
};

/**
 * 像素小道具：book 书、house 小房子、trophy 奖杯、tablet 刻字石板、star 星星。
 * (x, y) 是道具底边中点，u 是像素格大小；glow 给一圈同色柔光（“比人活得久的东西”在暗场里发亮）。
 */
export const PixelProp: React.FC<{kind: 'book' | 'house' | 'trophy' | 'tablet' | 'star'; x: number; y: number; u?: number; glow?: number}> = ({kind, x, y, u = 8, glow = 0.6}) => {
  const W = 14;
  const H = 14;
  const px: React.ReactNode[] = [];
  const r = (k: string, rx: number, ry: number, w: number, h: number, fill: string, o = 1) => px.push(<rect key={k} x={rx} y={ry} width={w} height={h} fill={fill} opacity={o} />);
  let col = NP.warm;
  if (kind === 'book') {
    col = '#d98c6a';
    r('l', 1, 4, 6, 9, '#d98c6a');
    r('r', 7, 4, 6, 9, '#c57a5a');
    r('pl', 2, 5, 4, 7, NP.paper);
    r('pr', 8, 5, 4, 7, NP.paper);
    [6, 8, 10].forEach((yy, i) => {
      r(`t${i}`, 3, yy, 3, 1, NP.inkSoft, 0.6);
      r(`u${i}`, 9, yy, 2, 1, NP.inkSoft, 0.6);
    });
  } else if (kind === 'house') {
    col = '#e4c988';
    [
      [6, 1, 2],
      [5, 2, 4],
      [4, 3, 6],
      [3, 4, 8],
      [2, 5, 10],
    ].forEach(([rx, ry, w], i) => r(`roof${i}`, rx, ry, w, 1, '#a8463d'));
    r('wall', 3, 6, 8, 7, '#d8ccb1');
    r('door', 6, 9, 2, 4, NP.wood);
    r('win', 4, 7, 2, 2, NP.warm);
    r('win2', 8, 7, 2, 2, NP.warm);
  } else if (kind === 'trophy') {
    col = '#e3b34a';
    r('cup', 3, 2, 8, 5, '#e3b34a');
    r('cup2', 4, 7, 6, 1, '#e3b34a');
    r('hl', 1, 3, 2, 2, '#c99a3a');
    r('hr', 11, 3, 2, 2, '#c99a3a');
    r('stem', 6, 8, 2, 3, '#c99a3a');
    r('base', 4, 11, 6, 2, NP.wood);
    r('shine', 4, 3, 1, 3, '#fff2c8', 0.8);
  } else if (kind === 'tablet') {
    col = '#cfd3dc';
    r('top', 4, 1, 6, 1, '#b9bec9');
    r('body', 3, 2, 8, 11, '#b9bec9');
    [4, 6, 8, 10].forEach((yy, i) => r(`line${i}`, 5, yy, 4 - (i % 2), 1, '#6b7080'));
  } else {
    col = '#f3e3a0';
    r('v', 6, 1, 2, 12, '#f3e3a0');
    r('h', 1, 6, 12, 2, '#f3e3a0');
    r('c', 4, 4, 6, 6, '#f3e3a0');
    r('d', 3, 3, 1, 1, '#f3e3a0', 0.6);
    r('d2', 10, 3, 1, 1, '#f3e3a0', 0.6);
    r('d3', 3, 10, 1, 1, '#f3e3a0', 0.6);
    r('d4', 10, 10, 1, 1, '#f3e3a0', 0.6);
  }
  return (
    <div style={{position: 'absolute', left: x - (W * u) / 2, top: y - H * u, width: W * u, height: H * u, ...(glow > 0 ? bloom(col, 30 * glow, glow * 0.7) : {})}}>
      <svg viewBox={`0 0 ${W} ${H}`} width={W * u} height={H * u} shapeRendering="crispEdges">
        {px}
      </svg>
    </div>
  );
};
