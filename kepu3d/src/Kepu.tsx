/** 主合成：按全片帧号找到镜头与子镜头，渲染对应 3D 场景，叠加切镜闪光、撞击闪光、字幕、角标、来源卡与混音。 */
import React, {useEffect, useState} from 'react';
import {AbsoluteFill, Audio, continueRender, delayRender, staticFile, useCurrentFrame} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import {FXProvider, World} from './lib/World';
import {easeOut, prog, pulse} from './lib/anim';
import {KepuProps, ShotT, SP, SceneFn} from './types';
import {SUNK} from './topics/sunk';

const TOPICS: Record<string, Record<number, SceneFn[]>> = {sunk: SUNK};
const BG = '#090A0C';
const GOLD = '#D6B879';
const WHITE = '#F5F0E8';
const TEXT_IN = 0.4;
const TEXT_OUT = 0.4;

let fontsReady: Promise<void> | null = null;
const loadFonts = () => {
  if (!fontsReady) {
    const faces = [
      new FontFace('KepuSerif', `url(${staticFile('fonts/NotoSerifCJKsc-Bold.otf')})`),
      new FontFace('KepuSerifSemi', `url(${staticFile('fonts/NotoSerifCJKsc-SemiBold.otf')})`),
      new FontFace('KepuSans', `url(${staticFile('fonts/NotoSansCJKsc-Medium.otf')})`),
    ];
    fontsReady = Promise.all(faces.map((f) => f.load().then((x) => {
      document.fonts.add(x);
    }))).then(() => undefined);
  }
  return fontsReady;
};

/** 字体加载完成前不挂载 3D 画布：场景里的文字贴图要用同一套字体绘制。 */
const useFonts = () => {
  const [ready, setReady] = useState(false);
  const [handle] = useState(() => {
    const h = delayRender('fonts');
    loadFonts().then(() => setReady(true)).catch((e) => {
      throw e;
    });
    return h;
  });
  // 画布挂载（其内部已登记自己的 delayRender）之后再放行字体等待
  useEffect(() => {
    if (ready) continueRender(handle);
  }, [ready, handle]);
  return ready;
};

/** 把一行字幕按关键词切成 [文本, 是否高亮] 片段。 */
const split = (line: string, keys: string[]): [string, boolean][] => {
  const out: [string, boolean][] = [];
  let rest = line;
  while (rest) {
    let best = -1;
    let key = '';
    for (const k of keys) {
      const i = rest.indexOf(k);
      if (i >= 0 && (best < 0 || i < best)) {
        best = i;
        key = k;
      }
    }
    if (best < 0) {
      out.push([rest, false]);
      break;
    }
    if (best > 0) out.push([rest.slice(0, best), false]);
    out.push([key, true]);
    rest = rest.slice(best + key.length);
  }
  return out;
};

const textAlpha = (sh: ShotT, T: number, first: boolean) => {
  const aIn = first ? 1 : easeOut(prog(T, 0, TEXT_IN));
  const aOut = sh.credit ? 1 : 1 - prog(T, sh.dur - TEXT_OUT, TEXT_OUT);
  return aIn * aOut;
};

export const Kepu: React.FC<KepuProps> = (p) => {
  const ready = useFonts();
  const cur = useCurrentFrame();
  const frame = p.cover ? Math.round((p.cover.at ?? 0.5) * p.fps) : cur;
  const fps = p.fps;
  const F = (s: number) => Math.round(s * fps);
  const sub = p.subshots.find((s) => frame >= F(s.start) && frame < F(s.end)) ?? p.subshots[p.subshots.length - 1];
  const shot = p.shots.find((s) => s.no === sub.shot)!;
  const first = shot.no === p.shots[0].no;
  const G = frame / fps;
  const T = (frame - F(shot.start)) / fps;
  const t = (frame - F(sub.start)) / fps;
  const scenes = TOPICS[p.slug]?.[shot.no] ?? [];
  const Scene = scenes.length ? scenes[sub.k % scenes.length] : null;
  const sp: SP = {t, d: sub.end - sub.start, T, D: shot.dur, cue: shot.cue, k: sub.k, G};

  // 撞击脉冲（画面闪光 + 色散 + 震屏）与切镜脉冲（冲击缩放 + 轻闪）
  const hit = Math.max(0, ...p.hits.filter((h) => !h.soft).map((h) => pulse(frame, F(h.t), 7)));
  const soft = Math.max(0, ...p.hits.filter((h) => h.soft).map((h) => pulse(frame, F(h.t), 6)));
  const cut = pulse(frame, F(sub.start), 6) * (F(sub.start) > 0 ? 1 : 0);
  const punch = 1 + 0.07 * cut + 0.05 * hit;
  const vertical = p.layout.name === 'vertical';
  const L = p.layout;
  const a = p.cover ? 0 : textAlpha(shot, T, first);

  return (
    <AbsoluteFill style={{backgroundColor: BG}}>
      <AbsoluteFill style={{transform: `scale(${punch})`}}>
        {ready && <ThreeCanvas width={p.width} height={p.height} gl={{antialias: false, powerPreference: 'high-performance'}}
          camera={{fov: 40, position: [0, 2, 8]}}>
          <FXProvider value={{T: G, frame, hit, shiftY: vertical ? 0.1 : 0}}>
            <World>{Scene ? <Scene {...sp} /> : null}</World>
          </FXProvider>
        </ThreeCanvas>}
      </AbsoluteFill>
      <AbsoluteFill style={{background: `radial-gradient(circle at 50% 58%, rgba(255,226,168,${0.5 * hit}) 0%, rgba(214,184,121,${0.28 * hit}) 35%, rgba(0,0,0,0) 75%)`}} />
      <AbsoluteFill style={{backgroundColor: `rgba(255,240,210,${0.22 * cut + 0.12 * soft})`}} />
      <AbsoluteFill style={{
        background: vertical
          ? 'linear-gradient(180deg, rgba(9,10,12,0.9) 0px, rgba(9,10,12,0.7) 400px, rgba(9,10,12,0) 680px)'
          : 'linear-gradient(90deg, rgba(9,10,12,0.9) 0px, rgba(9,10,12,0.75) 620px, rgba(9,10,12,0) 1000px)',
      }} />
      {p.cover ? <Cover p={p} /> : (
        <>
          <Tag text={shot.tag} a={a} L={L} />
          {shot.credit ? <Credit sh={shot} T={T} p={p} /> : <Caption sh={shot} T={T} a={a} first={first} p={p} />}
        </>
      )}
      {!p.cover && p.audio ? <Audio src={staticFile(p.audio)} /> : null}
    </AbsoluteFill>
  );
};

const Tag: React.FC<{text: string; a: number; L: KepuProps['layout']}> = ({text, a, L}) => (
  <div style={{
    position: 'absolute', left: L.tag_x, top: L.tag_y - L.tag_size * 0.8, height: L.tag_size * 1.6,
    padding: `0 ${L.tag_size * 0.55}px`, borderRadius: L.tag_size, border: `1.6px solid ${GOLD}`,
    background: 'rgba(0,0,0,0.45)', color: GOLD, fontFamily: 'KepuSans', fontSize: L.tag_size,
    lineHeight: `${L.tag_size * 1.6 - 3}px`, opacity: a, whiteSpace: 'nowrap',
  }}>{text}</div>
);

const Caption: React.FC<{sh: ShotT; T: number; a: number; first: boolean; p: KepuProps}> = ({sh, T, a, first, p}) => {
  const L = p.layout;
  const vertical = L.name === 'vertical';
  const y0 = vertical ? L.text_y : L.text_y - ((sh.lines.length - 1) * L.text_line_gap) / 2;
  return (
    <>
      <div style={{
        position: 'absolute', height: 3, background: GOLD, opacity: a,
        left: vertical ? L.text_x - 35 : L.text_x, width: 70, top: y0 - L.text_size * 1.12,
      }} />
      {sh.lines.map((ln, i) => {
        const x = first ? 1 : easeOut(prog(T, 0.08 * i, TEXT_IN - 0.08 * i));
        const dx = (1 - x) * (i % 2 === 0 ? -40 : 40);
        const dy = (1 - x) * 30;
        return (
          <div key={i} style={{
            position: 'absolute', top: y0 + i * L.text_line_gap - L.text_size * 0.62 + dy,
            left: vertical ? L.text_x - 520 + dx : L.text_x + dx, width: vertical ? 1040 : 1700,
            textAlign: vertical ? 'center' : 'left', fontFamily: 'KepuSerif', fontSize: L.text_size,
            lineHeight: `${L.text_size * 1.24}px`, color: WHITE, opacity: a * (T < TEXT_IN ? x : 1),
            textShadow: '0 4px 18px rgba(0,0,0,0.85), 0 0 2px rgba(0,0,0,0.9)', whiteSpace: 'nowrap',
          }}>{split(ln, sh.keys ?? []).map(([s, hi], j) => (
            <span key={j} style={hi ? {color: GOLD, textShadow: '0 0 18px rgba(214,184,121,0.55), 0 4px 18px rgba(0,0,0,0.85)'} : undefined}>{s}</span>
          ))}</div>
        );
      })}
    </>
  );
};

const Credit: React.FC<{sh: ShotT; T: number; p: KepuProps}> = ({sh, T, p}) => {
  const L = p.layout;
  const at = Object.values(sh.cue)[0] ?? TEXT_IN;
  const k = at > 0 ? Math.pow(prog(T, 0, at), 3) : 1;
  const cy = p.height / 2 - (L.name === 'vertical' ? 60 : 0);
  return (
    <div style={{
      position: 'absolute', left: '50%', top: cy + 30 * (1 - k), transform: 'translate(-50%, -50%)',
      padding: `${L.ref_size * 0.9}px ${L.ref_size * 1.2}px`, borderRadius: 14, background: 'rgba(18,19,23,0.92)',
      boxShadow: `0 0 0 1.6px rgba(214,184,121,0.8) inset, 0 18px 44px rgba(0,0,0,0.7)`, opacity: k, textAlign: 'center',
    }}>
      {sh.lines.map((ln, i) => (
        <div key={i} style={{fontFamily: 'KepuSerif', fontSize: L.ref_size, lineHeight: `${L.ref_size * 1.45}px`,
          color: i ? WHITE : GOLD, whiteSpace: 'nowrap'}}>{ln}</div>
      ))}
    </div>
  );
};

const Cover: React.FC<{p: KepuProps}> = ({p}) => {
  const c = p.cover!;
  const vertical = p.layout.name === 'vertical';
  const size = vertical ? 118 : 104;
  return (
    <div style={{position: 'absolute', left: vertical ? 0 : 120, top: vertical ? 330 - size * 0.62 : 350 - size * 0.62,
      width: vertical ? p.width : 1500, textAlign: vertical ? 'center' : 'left'}}>
      {c.title.map((ln, i) => (
        <div key={i} style={{fontFamily: 'KepuSerif', fontSize: size, lineHeight: `${vertical ? 150 : 138}px`, color: WHITE,
          textShadow: '0 6px 24px rgba(0,0,0,0.85)'}}>{ln}</div>
      ))}
      <div style={{height: 3, width: 100, background: GOLD, margin: vertical ? '28px auto 30px' : '28px 0 30px'}} />
      <div style={{fontFamily: 'KepuSerifSemi', fontSize: vertical ? 62 : 56, color: GOLD}}>{c.subtitle}</div>
    </div>
  );
};
