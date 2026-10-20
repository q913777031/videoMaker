import React from 'react';
import {AbsoluteFill} from 'remotion';
import {clamp01, rand} from '../anim';
import {dissolve, fade, hexA, NP, NPF} from './theme';

/**
 * 夜色像素风的舞台层：像素场景（街道 / 房间 / 天台 / 暖光厨房墙）、雪、星、暗角颗粒、景深容器、
 * 左上章节胶囊、底部字幕、糊化交叉容器、横移镜头。
 * 场景在 240×135 的「像素格」里画，用 viewBox 放大到 1920×1080，shapeRendering 保持硬边。
 */

const G = {w: 240, h: 135};

/** 像素格画布：子元素用格坐标画矩形 */
export const PixelCanvas: React.FC<{children: React.ReactNode; style?: React.CSSProperties}> = ({children, style}) => (
  <svg viewBox={`0 0 ${G.w} ${G.h}`} width="100%" height="100%" preserveAspectRatio="xMidYMid slice" shapeRendering="crispEdges" style={{position: 'absolute', inset: 0, ...style}}>
    {children}
  </svg>
);

/** 一排楼的剪影：窗格按 seed 随机亮暖黄，亮窗会极慢地明灭 */
const Skyline: React.FC<{f: number; seed: number; y: number; color: string; lit?: number}> = ({f, seed, y, color, lit = 0.28}) => {
  const out: React.ReactNode[] = [];
  let x = -4;
  let k = 0;
  while (x < G.w + 4) {
    const bw = 14 + Math.floor(rand(seed + k) * 16);
    const bh = 22 + Math.floor(rand(seed + k + 0.3) * 40);
    out.push(<rect key={`b${k}`} x={x} y={y - bh} width={bw} height={bh + 60} fill={color} />);
    for (let wy = y - bh + 4; wy < y - 4; wy += 5) {
      for (let wx = x + 2; wx < x + bw - 2; wx += 4) {
        const s = seed * 7 + wx * 13.1 + wy * 3.7;
        if (rand(s) < lit) {
          const on = rand(s + 1) > 0.15 || Math.sin(f / 70 + s) > 0;
          out.push(<rect key={`w${wx}-${wy}`} x={wx} y={wy} width={2} height={2} fill={NP.warm} opacity={on ? 0.75 : 0.15} />);
        }
      }
    }
    x += bw + 1;
    k++;
  }
  return <g>{out}</g>;
};

/** 星点：深空里零星的小方点，忽明忽暗 */
const Stars: React.FC<{f: number; n?: number; seed?: number; maxY?: number}> = ({f, n = 40, seed = 3, maxY = 60}) => (
  <g>
    {Array.from({length: n}, (_, i) => {
      const s = seed * 100 + i;
      const tw = 0.3 + 0.7 * Math.abs(Math.sin(f / (30 + rand(s + 2) * 50) + i));
      return <rect key={i} x={Math.floor(rand(s) * G.w)} y={Math.floor(rand(s + 1) * maxY)} width={1} height={1} fill="#cfd6ea" opacity={0.6 * tw} />;
    })}
  </g>
);

/**
 * 像素场景背景。kind：street 夜街（楼群 + 路灯 + 斑马线）、room 夜里的房间（窗外城市 + 书桌 + 台灯）、
 * rooftop 天台（栏杆 + 星空 + 月亮）、kitchen 暖光墙（白瓷砖 + 台面，暖光从右侧来）。
 * pan 是镜头横移量（格），用于原片那种缓慢平移。
 */
export const NightScene: React.FC<{f: number; kind: 'street' | 'room' | 'rooftop' | 'kitchen'; pan?: number; seed?: number}> = ({f, kind, pan = 0, seed = 1}) => {
  if (kind === 'street') {
    return (
      <PixelCanvas>
        <rect width={G.w} height={G.h} fill={NP.night} />
        <Stars f={f} seed={seed} maxY={40} />
        <g transform={`translate(${-pan * 0.3} 0)`} style={{filter: 'blur(0.6px)'}}>
          <Skyline f={f} seed={seed + 10} y={88} color={NP.night2} lit={0.22} />
        </g>
        <g transform={`translate(${-pan} 0)`}>
          <rect x={-20} y={88} width={G.w + 60} height={50} fill={NP.deep} />
          <rect x={-20} y={88} width={G.w + 60} height={1} fill={hexA(NP.cream, 0.18)} />
          {Array.from({length: 18}, (_, i) => (
            <rect key={i} x={70 + i * 6} y={98} width={3} height={14} fill="#c9ccd6" opacity={0.75} />
          ))}
          <rect x={30} y={44} width={2} height={44} fill="#3a4152" />
          <rect x={30} y={42} width={8} height={2} fill="#3a4152" />
          <rect x={36} y={44} width={3} height={2} fill={NP.warm} />
          <polygon points="35,46 40,46 58,112 14,112" fill="url(#np-cone)" />
        </g>
        <defs>
          <linearGradient id="np-cone" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor={NP.warm} stopOpacity={0.35} />
            <stop offset="1" stopColor={NP.warm} stopOpacity={0} />
          </linearGradient>
        </defs>
      </PixelCanvas>
    );
  }
  if (kind === 'room') {
    return (
      <PixelCanvas>
        <rect width={G.w} height={G.h} fill={NP.night2} />
        <g transform={`translate(${-pan} 0)`}>
          <rect x={140} y={18} width={70} height={52} fill={NP.ink} />
          <svg x={140} y={18} width={70} height={52} viewBox="0 0 70 52">
            <Stars f={f} n={18} seed={seed + 4} maxY={30} />
            <Skyline f={f} seed={seed + 20} y={52} color="#1a2033" lit={0.3} />
          </svg>
          <rect x={174} y={18} width={2} height={52} fill="#2d3346" />
          <rect x={140} y={43} width={70} height={2} fill="#2d3346" />
          <rect x={138} y={70} width={74} height={3} fill="#2d3346" />
          <rect x={30} y={22} width={14} height={18} fill="#a8463d" opacity={0.8} />
          <rect x={48} y={26} width={12} height={14} fill="#3f7a6a" opacity={0.8} />
          <rect x={0} y={98} width={G.w} height={40} fill={NP.deep} />
          <rect x={40} y={84} width={110} height={4} fill={NP.wood} />
          <rect x={44} y={88} width={3} height={14} fill={NP.woodDark} />
          <rect x={143} y={88} width={3} height={14} fill={NP.woodDark} />
          <rect x={56} y={76} width={2} height={8} fill="#6b6f7c" />
          <rect x={52} y={74} width={10} height={3} fill={NP.warm} />
          <rect x={120} y={78} width={14} height={6} fill="#e9e7e0" />
          <ellipse cx={57} cy={86} rx={46} ry={22} fill="url(#np-lamp)" />
        </g>
        <defs>
          <radialGradient id="np-lamp">
            <stop offset="0" stopColor={NP.warm} stopOpacity={0.42} />
            <stop offset="1" stopColor={NP.warm} stopOpacity={0} />
          </radialGradient>
        </defs>
      </PixelCanvas>
    );
  }
  if (kind === 'rooftop') {
    return (
      <PixelCanvas>
        <rect width={G.w} height={G.h} fill={NP.night} />
        <Stars f={f} n={70} seed={seed + 7} maxY={80} />
        <rect x={190} y={16} width={12} height={12} fill="#e8e6dc" />
        <rect x={188} y={18} width={2} height={8} fill="#e8e6dc" />
        <rect x={202} y={18} width={2} height={8} fill="#e8e6dc" />
        <g transform={`translate(${-pan * 0.3} 0)`} style={{filter: 'blur(0.8px)'}}>
          <Skyline f={f} seed={seed + 30} y={100} color="#1b2132" lit={0.3} />
        </g>
        <g transform={`translate(${-pan} 0)`}>
          <rect x={-20} y={100} width={G.w + 60} height={40} fill={NP.deep} />
          <rect x={-20} y={84} width={G.w + 60} height={2} fill="#3a4152" />
          {Array.from({length: 30}, (_, i) => (
            <rect key={i} x={-10 + i * 9} y={84} width={2} height={16} fill="#3a4152" />
          ))}
        </g>
      </PixelCanvas>
    );
  }
  return (
    <PixelCanvas>
      <rect width={G.w} height={G.h} fill="#d9d2c0" />
      {Array.from({length: 14}, (_, r) =>
        Array.from({length: 26}, (_, c) => <rect key={`${r}-${c}`} x={c * 10 - (r % 2) * 5} y={r * 6} width={9} height={5} fill="#ebe5d6" />),
      )}
      <rect x={0} y={86} width={G.w} height={6} fill={NP.woodDark} />
      <rect x={0} y={92} width={G.w} height={44} fill="#4a382d" />
      <rect x={150} y={70} width={30} height={16} fill="#f2f0ea" />
      <rect x={156} y={76} width={10} height={2} fill={NP.red} />
      <rect x={90} y={80} width={40} height={4} fill="#2b2b2e" />
      <rect x={70} y={81} width={22} height={2} fill="#2b2b2e" />
      <rect x={0} y={0} width={G.w} height={G.h} fill="url(#np-kitchen-warm)" />
      <defs>
        <radialGradient id="np-kitchen-warm" cx="0.62" cy="0.55" r="0.6">
          <stop offset="0" stopColor={NP.warm} stopOpacity={0.35} />
          <stop offset="1" stopColor="#2a1c12" stopOpacity={0.55} />
        </radialGradient>
      </defs>
    </PixelCanvas>
  );
};

/** 雪：方块雪片缓慢斜落，近处的大且虚，远处的小而实 */
export const Snow: React.FC<{f: number; n?: number; seed?: number; w?: number; h?: number; strength?: number}> = ({f, n = 70, seed = 5, w = 1920, h = 1080, strength = 1}) => (
  <AbsoluteFill style={{pointerEvents: 'none'}}>
    <svg width={w} height={h} style={{position: 'absolute'}}>
      <defs>
        <filter id="np-snow-blur">
          <feGaussianBlur stdDeviation="2.5" />
        </filter>
      </defs>
      {Array.from({length: n}, (_, i) => {
        const s = seed * 100 + i;
        const near = rand(s + 0.5) > 0.82;
        const sp = near ? 2.2 : 0.7 + rand(s + 3) * 0.8;
        const x = (rand(s) * w + f * (0.25 + rand(s + 1) * 0.3) + Math.sin(f / 40 + i) * 6 + w) % w;
        const y = (rand(s + 2) * h + f * sp) % h;
        const sz = near ? 14 : 4 + Math.floor(rand(s + 4) * 3) * 2;
        return <rect key={i} x={x} y={y} width={sz} height={sz} fill="#f2f4fa" opacity={(near ? 0.35 : 0.7) * strength} filter={near ? 'url(#np-snow-blur)' : undefined} />;
      })}
    </svg>
  </AbsoluteFill>
);

/** 暗角 + 细颗粒：四角压到近黑，画面中心留一块亮 */
export const Vignette: React.FC<{strength?: number}> = ({strength = 1}) => (
  <AbsoluteFill style={{pointerEvents: 'none'}}>
    <AbsoluteFill style={{background: `radial-gradient(ellipse 75% 70% at 50% 48%, rgba(0,0,0,0) 50%, rgba(5,7,12,${0.72 * strength}) 100%)`}} />
    <AbsoluteFill style={{mixBlendMode: 'screen', opacity: 0.07}}>
      <svg width="100%" height="100%">
        <filter id="np-grain">
          <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" stitchTiles="stitch" />
        </filter>
        <rect width="100%" height="100%" filter="url(#np-grain)" />
      </svg>
    </AbsoluteFill>
  </AbsoluteFill>
);

/** 景深容器：把一层整体虚化、压暗（depth 0 = 焦点，1 = 很虚）；信笺出现时背后的场景就用它退到后面 */
export const Depth: React.FC<{depth: number; dim?: number; children: React.ReactNode}> = ({depth, dim = 0, children}) => (
  <AbsoluteFill style={{filter: `blur(${depth * 10}px) brightness(${1 - dim})`}}>{children}</AbsoluteFill>
);

/** 横移镜头：t 帧内整体缓慢平移 dx 像素、推近 zoom，原片每个镜头都在轻微地动 */
export const Drift: React.FC<{t: number; len: number; dx?: number; zoom?: number; children: React.ReactNode}> = ({t, len, dx = -40, zoom = 0.02, children}) => {
  const p = clamp01(t / Math.max(1, len));
  return <AbsoluteFill style={{transform: `translateX(${dx * p}px) scale(${1 + zoom * p})`}}>{children}</AbsoluteFill>;
};

/** 糊化交叉的场景容器：at 起 10 帧糊化进入，out 起 10 帧糊化离开 */
export const Blend: React.FC<{f: number; at: number; out?: number; dur?: number; children: React.ReactNode}> = ({f, at, out, dur = 10, children}) => {
  const d = dissolve(f, at, dur, out, dur);
  if (d.v <= 0) return null;
  return <AbsoluteFill style={{opacity: d.opacity, filter: d.filter}}>{children}</AbsoluteFill>;
};

/** 左上章节胶囊：「第 N 位 · 角色」，深色半透明底 + 米色细描边，镜头切入后约 4 帧淡入 */
export const ChapterPill: React.FC<{f: number; at: number; no: string; who?: string; out?: number}> = ({f, at, no, who, out}) => {
  const a = fade(f, at + 4, 8, out);
  return (
    <div
      style={{
        position: 'absolute',
        left: 40,
        top: 30,
        opacity: a,
        padding: '10px 34px',
        borderRadius: 999,
        border: `3px solid ${hexA(NP.cream, 0.55)}`,
        background: 'rgba(10,12,20,0.55)',
        fontFamily: NPF.card,
        fontSize: 44,
        color: NP.cream,
        letterSpacing: 4,
      }}
    >
      {no}
      {who ? <span style={{opacity: 0.9}}>{` · ${who}`}</span> : null}
    </div>
  );
};

/** 底部字幕：白色粗黑体居中，无底条，只带一圈柔和黑影；画面稳定后 6 帧淡入 */
export const NPCaption: React.FC<{f: number; at: number; text: string; out?: number; y?: number}> = ({f, at, text, out, y = 960}) => {
  const a = fade(f, at, 6, out, 6);
  if (a <= 0) return null;
  return (
    <div
      style={{
        position: 'absolute',
        left: 0,
        right: 0,
        top: y,
        textAlign: 'center',
        opacity: a,
        fontFamily: NPF.sub,
        fontWeight: 700,
        fontSize: 52,
        color: NP.sub,
        letterSpacing: 2,
        textShadow: '0 2px 10px rgba(0,0,0,0.85), 0 0 2px rgba(0,0,0,0.9)',
      }}
    >
      {text}
    </div>
  );
};
