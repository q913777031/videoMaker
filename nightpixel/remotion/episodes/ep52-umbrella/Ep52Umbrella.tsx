import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {clamp01, easeInOut, easeOut} from '../../library/anim';
import {ChatWindow, NoteCard, Passerby, PixelPal, PixelUmbrella} from '../../library/night-pixel/props';
import {Blend, ChapterPill, Depth, Drift, NightScene, NPCaption, Snow, Vignette} from '../../library/night-pixel/stage';
import {cutAt, NP, NPF} from '../../library/night-pixel/theme';
import TL from './timeline.json';

/**
 * ep52《一把伞的雪夜》（夜色像素风，无口播，1920×1080，89 秒）。
 * 全片时间表在 timeline.json（由 videoMaker 的 nightpixel/umbrella.py 用 bgm.detect() 实测拍点生成），
 * 这里只按帧号画面；故事、人物都是原创示例。
 */
export const EP52_FRAMES = TL.end;
const C = TL.cues;

/** 只在 [a, b) 内渲染；inBlend / outBlend 为 true 时用 10 帧糊化交叉，否则硬切 */
const Win: React.FC<{f: number; a: number; b: number; inBlend?: boolean; outBlend?: boolean; children: React.ReactNode}> = ({f, a, b, inBlend = true, outBlend = true, children}) => {
  if (f < a - (inBlend ? 10 : 0) || f >= b + (outBlend ? 10 : 0)) return null;
  if (!inBlend && !outBlend) return <AbsoluteFill>{children}</AbsoluteFill>;
  return (
    <Blend f={f} at={inBlend ? a - 10 : a - 1} out={outBlend ? b : b + 999} dur={inBlend ? 10 : 1}>
      {children}
    </Blend>
  );
};

/** 拿着伞的小豆子：伞柄在身体右侧 */
const WithUmbrella: React.FC<{f: number; x: number; y: number; u: number; color: string; face?: 1 | -1; mood?: 'calm' | 'happy' | 'sad' | 'sleepy' | 'wow'; seed?: number}> = ({f, x, y, u, color, face = 1, mood = 'calm', seed = 0}) => (
  <>
    <PixelUmbrella x={x + face * 6 * u} y={y - 4 * u} u={u} tilt={-6 * face} />
    <PixelPal f={f} x={x} y={y} u={u} color={color} face={face} mood={mood} seed={seed} />
  </>
);

const arc = (p: number, a: [number, number], b: [number, number], h = 80): [number, number] => {
  const e = easeInOut(clamp01(p));
  return [a[0] + (b[0] - a[0]) * e, a[1] + (b[1] - a[1]) * e - Math.sin(Math.PI * e) * h];
};

const RELAY = [
  {kind: 'street', no: '第 3 位', who: '夜班护士', a: '#e3d39a', b: '#f2efe6'},
  {kind: 'rooftop', no: '第 4 位', who: '遛狗的大爷', a: '#f2efe6', b: '#cfd3dc'},
  {kind: 'street', no: '第 5 位', who: '接孩子的妈妈', a: '#cfd3dc', b: '#e7b6b0'},
  {kind: 'rooftop', no: '第 6 位', who: '加班的程序员', a: '#e7b6b0', b: '#a9c6b4'},
  {kind: 'street', no: '第 7 位', who: '值夜的保安', a: '#a9c6b4', b: '#b9a3c9'},
  {kind: 'rooftop', no: '第 8 位', who: '迷路的小朋友', a: '#b9a3c9', b: '#f6c9a0'},
] as const;

export const Ep52Umbrella: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{background: NP.ink, fontFamily: NPF.sub}}>
      {/* 1 开场聊天窗 */}
      <Win f={f} a={0} b={C.s2}>
        <ChatWindow
          f={f}
          at={0}
          title="失物招领群"
          bubbles={[
            {side: 'them', label: '便利店店员', text: '门口有把旧伞，谁要用就拿走。', at: C.chat_b1},
            {side: 'them', label: '路人', text: '用完放哪？', at: C.chat_b2},
            {side: 'them', label: '便利店店员', text: '放回来就行。', at: C.chat_b3},
          ]}
          typing={[C.typing, C.s2]}
          typingLabel="有人 正在输入"
        />
        <NPCaption f={f} at={C.cap1} text="雪下大了，便利店门口多了一把旧伞。" y={980} out={C.s2 - 8} />
      </Win>

      {/* 2 伞柄上的卡 */}
      <Win f={f} a={C.s2} b={C.s3} outBlend={false}>
        <Depth depth={0.9} dim={0.45}>
          <NightScene f={f} kind="street" seed={9} />
        </Depth>
        <Snow f={f} n={40} strength={0.7} />
        <NoteCard f={f - C.s2} at={0} header="伞柄上挂着一张卡" drafts={[{text: '借你。雪停了再还。', at: C.card1_write - C.s2}]} />
        <NPCaption f={f} at={C.cap2} text="卡上只有一句话。" />
      </Win>

      {/* 3 drop：学生把伞递给骑手 */}
      <Win f={f} a={C.s3} b={C.s4} inBlend={false}>
        {(() => {
          const t = f - C.s3;
          const stu: [number, number] = [760, 900];
          const rx = 1720 - 520 * easeOut(clamp01((f - C.rider_in) / (C.pass1 - C.rider_in)));
          const p = (f - C.pass1) / (C.pass1_end - C.pass1);
          const passed = p >= 1;
          const um = arc(p, [stu[0] + 84, stu[1] - 32], [rx - 84, 900 - 32]);
          return (
            <>
              <Drift t={t} len={C.s4 - C.s3} dx={-50} zoom={0.02}>
                <NightScene f={f} kind="street" pan={t * 0.03} seed={2} />
                <Passerby f={f} x={260} y={950} u={11} seed={7} />
                <PixelPal f={f} x={stu[0]} y={stu[1]} u={14} color="#e3d39a" mood={passed ? 'happy' : 'calm'} />
                <PixelPal f={f} x={rx} y={900} u={14} color="#9fb8d0" face={-1} mood={passed ? 'wow' : 'sad'} seed={4} />
                {p < 0 ? <PixelUmbrella x={stu[0] + 84} y={stu[1] - 32} u={14} tilt={-6} /> : <PixelUmbrella x={passed ? rx - 84 : um[0]} y={passed ? 900 - 32 : um[1]} u={14} tilt={passed ? 6 : -6 + 12 * clamp01(p)} />}
              </Drift>
              <Snow f={f} />
              <Vignette />
              <ChapterPill f={f} at={C.s3} no="第 1 位" who="赶末班车的学生" out={C.pass1_end} />
              <ChapterPill f={f} at={C.pass1_end} no="第 2 位" who="外卖骑手" />
              <NPCaption f={f} at={C.s3 + 8} text="第一个拿走它的，是赶末班车的学生。" out={C.cap3b - 6} />
              <NPCaption f={f} at={C.cap3b} text="她把伞，递给了没带伞的骑手。" />
            </>
          );
        })()}
      </Win>

      {/* 4 骑手写卡：红笔批改、重写、盖章 */}
      <Win f={f} a={C.s4} b={C.s5} outBlend={false}>
        <Depth depth={0.9} dim={0.45}>
          <NightScene f={f} kind="street" seed={2} />
        </Depth>
        <Snow f={f} n={40} strength={0.7} />
        <NoteCard
          f={f - C.s4}
          at={0}
          header="卡上第 2 行"
          size={84}
          drafts={[
            {text: '伞我先用，明早就还。', at: C.card2_write - C.s4, per: 4, marks: [5, 6, 7, 8], markAt: C.card2_mark - C.s4, note: '雪还没停', noteAt: C.card2_note - C.s4, strikeAt: C.card2_strike - C.s4},
            {text: '伞我先用，交给下一位。', at: C.card2_redo - C.s4, per: 4},
          ]}
          stamp={{text: '接力', at: C.card2_stamp - C.s4}}
        />
        <NPCaption f={f} at={C.cap4} text="他想了想，改了半句。" />
      </Win>

      {/* 5 接力：加速硬切 */}
      {f >= C.s5 && f < C.s6 + 10
        ? (() => {
            const t = Math.min(f - C.s5, C.s6 - C.s5 - 1);
            const c = cutAt(t, TL.relay.map((r) => r.len));
            const r = RELAY[c.i];
            const gy = r.kind === 'rooftop' ? 860 : 900;
            const a: [number, number] = [620, gy];
            const b: [number, number] = [1300, gy];
            const p = (c.t - c.len * 0.2) / (c.len * 0.45);
            const um = arc(p, [a[0] + 78, gy - 30], [b[0] - 78, gy - 30], 70);
            return (
              <Blend f={f} at={C.s5 - 1} out={C.s6} dur={1}>
                <Drift t={c.t} len={c.len} dx={-28} zoom={0.014}>
                  <NightScene f={f} kind={r.kind} seed={c.i + 3} pan={c.t * 0.05} />
                  <PixelPal f={f} x={a[0]} y={a[1]} u={13} color={r.a} seed={c.i} mood={p >= 1 ? 'happy' : 'calm'} />
                  <PixelPal f={f} x={b[0]} y={b[1]} u={13} color={r.b} face={-1} seed={c.i + 5} mood={p >= 1 ? 'happy' : 'sad'} />
                  {p < 0 ? <PixelUmbrella x={a[0] + 78} y={gy - 30} u={13} tilt={-6} /> : <PixelUmbrella x={p >= 1 ? b[0] - 78 : um[0]} y={p >= 1 ? gy - 30 : um[1]} u={13} tilt={p >= 1 ? 6 : -6 + 12 * clamp01(p)} />}
                </Drift>
                <Snow f={f} n={50} />
                <Vignette />
                <ChapterPill f={c.t} at={-4} no={r.no} who={r.who} />
              </Blend>
            );
          })()
        : null}

      {/* 6 高潮：雪落在「还」上，变成「传」 */}
      <Win f={f} a={C.s6} b={C.s7}>
        {(() => {
          const dim = clamp01((f - (C.swap - 21)) / 18) * (1 - clamp01((f - C.swap) / 10));
          return (
            <>
              <Depth depth={0.9} dim={0.5 + 0.2 * dim}>
                <NightScene f={f} kind="rooftop" seed={5} />
              </Depth>
              <Snow f={f} n={50} />
              <NoteCard f={f - C.s6} at={0} drafts={[{text: '借你。雪停了再还。', at: -999}]} align="center" size={116} h={340} y={300} swap={{index: 7, to: '传', at: C.swap - C.s6, fall: 30}} />
              <NPCaption f={f} at={C.cap6} text="雪没停。卡上的字，变了一个。" />
            </>
          );
        })()}
      </Win>

      {/* 7 伞继续往前走 */}
      <Win f={f} a={C.s7} b={C.s8}>
        {(() => {
          const t = f - C.s7;
          const x = 260 + 1400 * clamp01(t / (C.s8 - C.s7 + 10));
          return (
            <>
              <NightScene f={f} kind="street" seed={11} pan={t * 0.06} />
              <WithUmbrella f={f} x={x} y={900} u={12} color="#f6c9a0" mood="happy" seed={9} />
              <Snow f={f} n={90} />
              <Vignette />
              <NPCaption f={f} at={C.s7 + 8} text="伞还在往前走。" />
            </>
          );
        })()}
      </Win>

      {/* 8 第二天早上 */}
      <Win f={f} a={C.s8} b={C.s9}>
        <Drift t={f - C.s8} len={C.s9 - C.s8} dx={-30} zoom={0.02}>
          <NightScene f={f} kind="kitchen" />
          <PixelPal f={f} x={760} y={830} u={14} color="#cfd3dc" mood="sleepy" seed={2} />
        </Drift>
        <Vignette strength={0.6} />
        <ChapterPill f={f} at={C.s8} no="第二天" who="早上七点" />
        <NPCaption f={f} at={C.cap8} text="第二天早上，伞没有回来。" />
      </Win>

      {/* 9 卡的背面：三行 */}
      <Win f={f} a={C.s9} b={C.s10}>
        <Depth depth={0.9} dim={0.5}>
          <NightScene f={f} kind="room" seed={4} />
        </Depth>
        {[
          {a: C.s9, b: C.s9b, h: '卡的背面 · 第 4 位', t: '伞骨有点歪，我修好了。'},
          {a: C.s9b, b: C.s9c, h: '卡的背面 · 第 6 位', t: '替我谢谢第一位。'},
          {a: C.s9c, b: C.s10, h: '卡的背面 · 第 8 位', t: '下一位，别淋着。'},
        ].map((c, i) =>
          f >= c.a - 10 && f < c.b + 10 ? (
            <Blend key={i} f={f} at={c.a - 10} out={c.b}>
              <NoteCard f={f - c.a} at={-10} header={c.h} drafts={[{text: c.t, at: 6, per: 4}]} />
            </Blend>
          ) : null,
        )}
        <NPCaption f={f} at={C.cap9} text="卡的背面，写满了陌生人的字。" />
      </Win>

      {/* 10 收尾聊天窗 */}
      <Win f={f} a={C.s10} b={C.s11}>
        <ChatWindow
          f={f - C.s10}
          at={0}
          title="失物招领群"
          bubbles={[
            {side: 'them', label: '便利店店员', text: '那把伞还没回来。', at: C.end_b1 - C.s10},
            {side: 'them', label: '陌生人', text: '在我这，雪还没停。', at: C.end_b2 - C.s10},
            {side: 'me', text: '那就别还了，传下去。', at: C.end_b3 - C.s10},
          ]}
        />
        <NPCaption f={f} at={C.cap10} text="有些东西不用还，传下去就好。" y={980} />
      </Win>

      {/* 11 片尾题字 */}
      <Win f={f} a={C.s11} b={TL.end + 20}>
        <Snow f={f} n={60} strength={0.8} />
        <div style={{position: 'absolute', left: 0, right: 0, top: 420, textAlign: 'center', fontFamily: NPF.card, fontSize: 120, color: NP.cream, letterSpacing: 16, textShadow: `0 0 40px rgba(228,201,136,0.35)`}}>
          一把伞的雪夜
        </div>
        <PixelUmbrella x={960} y={380} u={10} />
        <AbsoluteFill style={{background: '#000', opacity: clamp01((f - (TL.end - 40)) / 36)}} />
      </Win>
    </AbsoluteFill>
  );
};
