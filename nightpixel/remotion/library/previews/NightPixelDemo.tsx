import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {ChatWindow, LightOrb, NoteCard, Passerby, PixelPal} from '../night-pixel/props';
import {Blend, ChapterPill, Depth, Drift, NightScene, NPCaption, Snow, Vignette} from '../night-pixel/stage';
import {cutAt, NP, NPF} from '../night-pixel/theme';

/**
 * 夜色像素风素材一览（1920×1080，40 秒）：每 150 帧一场，场与场之间 10 帧糊化交叉，
 * 第 5 场内部演示加速硬切（36 → 27 → 18 → 12 帧）。示例题目是「便利店夜班的交接本」，文案都是自己编的。
 */
const LEN = 150;
export const NIGHT_PIXEL_DEMO_FRAMES = LEN * 8;

const at = (i: number) => i * LEN;

/** 接力段：每段换一个场景，左边的小豆子把光点递给右边 */
const RELAY: {kind: 'street' | 'room' | 'rooftop' | 'kitchen'; a: string; b: string; no: string}[] = [
  {kind: 'street', a: '#f2efe6', b: '#e7b6b0', no: '第 4 位'},
  {kind: 'room', a: '#e7b6b0', b: '#a9c6b4', no: '第 5 位'},
  {kind: 'rooftop', a: '#a9c6b4', b: '#b9a3c9', no: '第 6 位'},
  {kind: 'kitchen', a: '#b9a3c9', b: '#e3d39a', no: '第 7 位'},
  {kind: 'street', a: '#e3d39a', b: '#cfd3dc', no: '第 8 位'},
  {kind: 'room', a: '#cfd3dc', b: '#f2efe6', no: '第 9 位'},
  {kind: 'rooftop', a: '#f2efe6', b: '#e7b6b0', no: '第 10 位'},
];
const RELAY_CUTS = [36, 27, 27, 18, 18, 12, 12];

export const NightPixelDemo: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{background: NP.night, fontFamily: NPF.sub}}>
      {/* 1 开场聊天窗 */}
      <Blend f={f} at={at(0) - 10} out={at(1)}>
        <AbsoluteFill style={{background: NP.ink}} />
        <ChatWindow
          f={f - at(0)}
          at={0}
          title="夜班交接群"
          bubbles={[
            {side: 'them', label: '店长', text: '今晚会下雪。', at: 14},
            {side: 'me', text: '收到，关东煮多备一锅。', at: 46},
          ]}
          typing={[70, 140]}
          typingLabel="下一位 正在输入"
        />
        <NPCaption f={f - at(0)} at={20} text="便利店的夜班，从一条消息开始。" y={980} />
      </Blend>

      {/* 2 信笺逐字写出 */}
      <Blend f={f} at={at(1)} out={at(2)}>
        <Depth depth={0.9} dim={0.45}>
          <NightScene f={f} kind="room" />
        </Depth>
        <NoteCard f={f - at(1)} at={0} header="交接本 · 第 1 页" drafts={[{text: '记得给晚归的人留灯。', at: 16}]} />
        <NPCaption f={f - at(1)} at={80} text="每个值班的人，都在交接本上留一句。" />
      </Blend>

      {/* 3 红笔批改 → 重写 → 通过章 */}
      <Blend f={f} at={at(2)} out={at(3)}>
        <Depth depth={0.9} dim={0.45}>
          <NightScene f={f} kind="room" />
        </Depth>
        <NoteCard
          f={f - at(2)}
          at={0}
          header="上一页：记得给晚归的人留灯。"
          size={76}
          drafts={[
            {text: '门口那盏灯我会一直帮你开着', at: 8, per: 3, marks: [9, 10], markAt: 56, strikeAt: 74, note: '再短一点', noteAt: 64},
            {text: '门口灯，常亮。', at: 92, per: 4},
          ]}
          stamp={{text: '七字以内', at: 128}}
        />
      </Blend>

      {/* 4 像素街景：章节胶囊 + 雪 + 缓慢横移 */}
      <Blend f={f} at={at(3)} out={at(4)}>
        <Drift t={f - at(3)} len={LEN} dx={-60} zoom={0.025}>
          <NightScene f={f} kind="street" pan={(f - at(3)) * 0.04} seed={2} />
          <Passerby f={f} x={1640} y={940} u={12} seed={4} />
          <PixelPal f={f} x={960} y={900} u={14} color="#e7b6b0" mood="happy" />
        </Drift>
        <Snow f={f} />
        <Vignette />
        <ChapterPill f={f - at(3)} at={0} no="第 3 位" who="晚归的学生" />
        <NPCaption f={f - at(3)} at={14} text="她说，看到这盏灯就不怕了。" />
      </Blend>

      {/* 5 接力：加速硬切 */}
      {f >= at(4) && f < at(5) + 10
        ? (() => {
            const t = Math.min(f - at(4), LEN - 1);
            const c = cutAt(t, RELAY_CUTS);
            const r = RELAY[c.i];
            const ax = 640;
            const bx = 1280;
            const gy = r.kind === 'rooftop' ? 860 : r.kind === 'kitchen' ? 860 : 900;
            return (
              <Blend f={f} at={at(4)} out={at(5)}>
                <Drift t={c.t} len={c.len} dx={-24} zoom={0.012}>
                  <NightScene f={f} kind={r.kind} seed={c.i + 1} />
                  <PixelPal f={f} x={ax} y={gy} u={13} color={r.a} seed={c.i} glow={0.4} />
                  <PixelPal f={f} x={bx} y={gy} u={13} color={r.b} seed={c.i + 3} face={-1} mood={c.t > c.len * 0.6 ? 'happy' : 'calm'} />
                  <LightOrb f={c.t} at={2} dur={Math.max(8, c.len * 0.55)} a={[ax + 90, gy - 100]} b={[bx - 90, gy - 100]} />
                </Drift>
                {r.kind !== 'kitchen' ? <Snow f={f} n={40} /> : null}
                <Vignette />
                <ChapterPill f={c.t} at={-4} no={r.no} />
              </Blend>
            );
          })()
        : null}

      {/* 6 房间 → 信笺浮上来（背景退成景深） */}
      <Blend f={f} at={at(5)} out={at(6)}>
        {(() => {
          const t = f - at(5);
          const up = Math.min(1, Math.max(0, (t - 60) / 12));
          return (
            <>
              <Depth depth={up * 0.9} dim={up * 0.45}>
                <Drift t={t} len={LEN} dx={-30} zoom={0.02}>
                  <NightScene f={f} kind="room" seed={3} />
                  <PixelPal f={f} x={1180} y={860} u={14} color="#cfd3dc" mood="sleepy" />
                </Drift>
                <Vignette />
              </Depth>
              <ChapterPill f={t} at={0} no="第 11 位" who="下夜班的护士" out={60} />
              <NoteCard f={t} at={64} drafts={[{text: '热饮在第二格。', at: 76, per: 4}]} align="center" size={116} h={340} y={300} />
              <NPCaption f={t} at={10} text="她把最后一句写得很短。" out={56} />
            </>
          );
        })()}
      </Blend>

      {/* 7 招牌：雪落标点 */}
      <Blend f={f} at={at(6)} out={at(7)}>
        <Depth depth={0.9} dim={0.5}>
          <NightScene f={f} kind="rooftop" seed={5} />
        </Depth>
        <Snow f={f} n={50} />
        <NoteCard f={f - at(6)} at={0} drafts={[{text: '今晚没人来了。', at: -60}]} align="center" size={124} h={340} y={300} swap={{index: 6, to: '？', at: 84, fall: 50}} />
        <NPCaption f={f - at(6)} at={100} text="雪停在了最后一个字上。" />
      </Blend>

      {/* 8 收尾聊天窗 */}
      <Blend f={f} at={at(7)}>
        <AbsoluteFill style={{background: NP.ink}} />
        <ChatWindow
          f={f - at(7)}
          at={0}
          title="夜班交接群"
          bubbles={[
            {side: 'me', text: '今晚会下雪。', at: 0},
            {side: 'them', label: '早班', text: '交接本写满了，灯还亮着。', at: 30},
          ]}
        />
        <NPCaption f={f - at(7)} at={60} text="哪一句，是写给你的？" y={980} />
      </Blend>
    </AbsoluteFill>
  );
};
