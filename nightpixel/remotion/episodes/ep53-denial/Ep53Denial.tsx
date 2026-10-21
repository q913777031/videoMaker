import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {clamp01} from '../../library/anim';
import {ChatWindow, LightOrb, NoteCard, Passerby, PixelPal, PixelProp} from '../../library/night-pixel/props';
import {Blend, ChapterPill, Depth, Drift, NightScene, NPCaption, Snow, Vignette} from '../../library/night-pixel/stage';
import {cutAt, NP, NPF} from '../../library/night-pixel/theme';
import TL from './timeline.json';

/**
 * ep53《我们为什么假装不会死》（夜色像素风，无口播，1920×1080，89 秒），依据欧内斯特·贝克尔《拒斥死亡》（1973）。
 * 全片时间表在 timeline.json（由 videoMaker 的 nightpixel/denial.py 用 bgm.detect() 实测拍点生成）。
 */
export const EP53_FRAMES = TL.end;
const C = TL.cues;

/** 只在 [a, b) 内渲染；inBlend / outBlend 为 true 时用 10 帧糊化交叉，否则硬切 */
const Win: React.FC<{f: number; a: number; b: number; inBlend?: boolean; outBlend?: boolean; children: React.ReactNode}> = ({f, a, b, inBlend = true, outBlend = true, children}) => {
  if (f < a - (inBlend ? 10 : 0) || f >= b + (outBlend ? 10 : 0)) return null;
  return (
    <Blend f={f} at={inBlend ? a - 10 : a - 1} out={outBlend ? b : b + 999} dur={inBlend ? 10 : 1}>
      {children}
    </Blend>
  );
};

const PROJECTS = [
  {kind: 'street', prop: 'book', who: '写下作品', color: '#e7b6b0'},
  {kind: 'rooftop', prop: 'house', who: '建起房子', color: '#cfd3dc'},
  {kind: 'street', prop: 'tablet', who: '刻下名字', color: '#a9c6b4'},
  {kind: 'rooftop', prop: 'trophy', who: '赢得荣誉', color: '#e3d39a'},
  {kind: 'street', prop: 'star', who: '相信永恒', color: '#b9a3c9'},
  {kind: 'rooftop', prop: 'book', who: '留给孩子', color: '#f6c9a0'},
] as const;

export const Ep53Denial: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{background: NP.ink, fontFamily: NPF.sub}}>
      {/* 1 开场聊天窗 */}
      <Win f={f} a={0} b={C.s2}>
        <ChatWindow
          f={f}
          at={0}
          title="深夜树洞"
          bubbles={[
            {side: 'them', label: '匿名 A', text: '如果明天是最后一天，你会做什么？', at: C.chat_b1},
            {side: 'them', label: '匿名 B', text: '去见想见的人。', at: C.chat_b2},
            {side: 'them', label: '匿名 C', text: '……没敢想过。', at: C.chat_b3},
          ]}
          typing={[C.typing, C.s2]}
          typingLabel="有人 正在输入"
        />
        <NPCaption f={f} at={C.cap1} text="很少有人，愿意认真想这个问题。" y={980} out={C.s2 - 8} />
      </Win>

      {/* 2 书的主张 */}
      <Win f={f} a={C.s2} b={C.s3} outBlend={false}>
        <Depth depth={0.9} dim={0.5}>
          <NightScene f={f} kind="room" seed={6} />
        </Depth>
        <NoteCard f={f - C.s2} at={0} header="1973 年，一本书这样说" size={76} drafts={[{text: '我们很多努力，都在躲着死亡。', at: C.card1_write - C.s2, per: 4}]} />
        <div style={{position: 'absolute', left: 0, right: 0, top: 720, textAlign: 'center', fontFamily: NPF.card, fontSize: 32, color: NP.cream, opacity: clamp01((f - C.cap2) / 8)}}>
          欧内斯特·贝克尔《拒斥死亡》· 次年获普利策奖
        </div>
        <NPCaption f={f} at={C.cap2} text="这本书叫《拒斥死亡》。" />
      </Win>

      {/* 3 drop：办法一，不去想 */}
      <Win f={f} a={C.s3} b={C.s4} inBlend={false}>
        {(() => {
          const t = f - C.s3;
          const x = 380 + 900 * clamp01(t / (C.s4 - C.s3));
          return (
            <>
              <Drift t={t} len={C.s4 - C.s3} dx={-40} zoom={0.02}>
                <NightScene f={f} kind="street" pan={t * 0.05} seed={3} />
                <Passerby f={f} x={1500 - t * 3} y={950} u={11} seed={5} />
                <Passerby f={f} x={200 + t * 2} y={960} u={10} seed={8} />
                <PixelPal f={f} x={x} y={900} u={14} color="#cfd3dc" mood="calm" />
              </Drift>
              <Snow f={f} />
              <Vignette />
              <ChapterPill f={f} at={C.s3} no="办法一" who="不去想" />
              <NPCaption f={f} at={C.s3 + 8} text="最常见的办法：假装它不存在。" out={C.cap3b - 6} />
              <NPCaption f={f} at={C.cap3b} text="忙起来，就顾不上想了。" />
            </>
          );
        })()}
      </Win>

      {/* 4 心里话：红笔批改 */}
      <Win f={f} a={C.s4} b={C.s5} outBlend={false}>
        <Depth depth={0.9} dim={0.5}>
          <NightScene f={f} kind="street" seed={3} />
        </Depth>
        <Snow f={f} n={40} strength={0.7} />
        <NoteCard
          f={f - C.s4}
          at={0}
          header="写一句心里话"
          drafts={[
            {text: '我不怕死。', at: C.card2_write - C.s4, marks: [2, 3], markAt: C.card2_mark - C.s4, note: '嘴硬', noteAt: C.card2_note - C.s4, strikeAt: C.card2_strike - C.s4},
            {text: '我只是，不敢去想。', at: C.card2_redo - C.s4, per: 4},
          ]}
          stamp={{text: '说了实话', at: C.card2_stamp - C.s4}}
        />
        <NPCaption f={f} at={C.cap4} text="贝克尔把这种回避，叫作“否认”。" />
      </Win>

      {/* 5 办法二：不朽方案（加速硬切） */}
      {f >= C.s5 && f < C.s6 + 10
        ? (() => {
            const t = Math.min(f - C.s5, C.s6 - C.s5 - 1);
            const c = cutAt(t, TL.relay.map((r) => r.len));
            const r = PROJECTS[c.i];
            const gy = r.kind === 'rooftop' ? 860 : 900;
            return (
              <Blend f={f} at={C.s5 - 1} out={C.s6} dur={1}>
                <Drift t={c.t} len={c.len} dx={-28} zoom={0.014}>
                  <NightScene f={f} kind={r.kind} seed={c.i + 4} pan={c.t * 0.05} />
                  <PixelPal f={f} x={760} y={gy} u={13} color={r.color} seed={c.i} mood={c.t > c.len * 0.5 ? 'happy' : 'calm'} />
                  <PixelProp kind={r.prop} x={1040} y={gy} u={11} />
                  <LightOrb f={c.t} at={Math.round(c.len * 0.25)} dur={Math.max(8, c.len * 0.5)} a={[1040, gy - 160]} b={[1180, 260]} arc={20} />
                </Drift>
                <Snow f={f} n={50} />
                <Vignette />
                <ChapterPill f={c.t} at={-4} no="不朽方案" who={r.who} />
                <NPCaption f={f} at={C.s5 + 6} text="办法二：做点比自己活得更久的事。" />
              </Blend>
            );
          })()
        : null}

      {/* 6 高潮：雪落在句号上 */}
      <Win f={f} a={C.s6} b={C.s7}>
        {(() => {
          const dim = clamp01((f - (C.swap - 21)) / 18) * (1 - clamp01((f - C.swap) / 10));
          return (
            <>
              <Depth depth={0.9} dim={0.5 + 0.2 * dim}>
                <NightScene f={f} kind="rooftop" seed={7} />
              </Depth>
              <Snow f={f} n={50} />
              <NoteCard f={f - C.s6} at={0} drafts={[{text: '死亡，是终点。', at: -999}]} align="center" size={124} h={340} y={300} swap={{index: 6, to: '？', at: C.swap - C.s6, fall: 30}} />
              <NPCaption f={f} at={C.cap6} text="贝克尔说：正因为会结束，人才拼命寻找意义。" />
            </>
          );
        })()}
      </Win>

      {/* 7 文化是一项不朽工程 */}
      <Win f={f} a={C.s7} b={C.s8}>
        <Drift t={f - C.s7} len={C.s8 - C.s7} dx={-40} zoom={0.02}>
          <NightScene f={f} kind="street" seed={12} pan={(f - C.s7) * 0.06} />
          {(['book', 'house', 'trophy'] as const).map((k, i) => (
            <React.Fragment key={k}>
              <PixelPal f={f} x={360 + i * 520} y={900} u={11} color={['#e7b6b0', '#cfd3dc', '#e3d39a'][i]} seed={i + 2} mood="happy" />
              <PixelProp kind={k} x={480 + i * 520} y={900} u={9} />
            </React.Fragment>
          ))}
        </Drift>
        <Snow f={f} n={80} />
        <Vignette />
        <NPCaption f={f} at={C.s7 + 8} text="他甚至认为：整个文化，都像一项“不朽工程”。" />
      </Win>

      {/* 8 恐惧管理理论 */}
      <Win f={f} a={C.s8} b={C.s9}>
        <Drift t={f - C.s8} len={C.s9 - C.s8} dx={-30} zoom={0.02}>
          <NightScene f={f} kind="room" seed={9} />
          <PixelPal f={f} x={760} y={792} u={13} color="#cfd3dc" mood="calm" seed={3} />
          <PixelProp kind="book" x={920} y={676} u={7} glow={0.4} />
        </Drift>
        <Vignette />
        <ChapterPill f={f} at={C.s8} no="1986" who="恐惧管理理论" />
        <NPCaption f={f} at={C.cap8} text="后来，三位心理学家把这本书变成了实验。" />
      </Win>

      {/* 9 实验与重复实验 */}
      <Win f={f} a={C.s9} b={C.s10}>
        <Depth depth={0.9} dim={0.5}>
          <NightScene f={f} kind="room" seed={9} />
        </Depth>
        {[
          {a: C.s9, b: C.s9b, h: '实验 · 1989', t: '想到死亡之后，罚得更重了。', size: 84},
          {a: C.s9b, b: C.s9c, h: '平均保释金', t: '455 美元 vs 50 美元', size: 92},
          {a: C.s9c, b: C.s10, h: '大型重复实验 · 2022', t: '21 个实验室，没能复现。', size: 88, note: '效应可能被高估了'},
        ].map((c, i) =>
          f >= c.a - 10 && f < c.b + 10 ? (
            <Blend key={i} f={f} at={c.a - 10} out={c.b}>
              <NoteCard f={f - c.a} at={-10} header={c.h} size={c.size} drafts={[{text: c.t, at: 6, per: 3, ...(c.note ? {note: c.note, noteAt: C.s9c_stamp - C.s9c} : {})}]} />
            </Blend>
          ) : null,
        )}
        <NPCaption f={f} at={C.cap9} text="被提醒想到死亡的法官，给出的保释金高了很多。" out={C.s9c - 6} />
        <NPCaption f={f} at={C.s9c + 6} text="可后来的大型重复实验，没能复现这个结果。" />
      </Win>

      {/* 10 收尾聊天窗 */}
      <Win f={f} a={C.s10} b={C.s11}>
        <ChatWindow
          f={f - C.s10}
          at={0}
          title="深夜树洞"
          bubbles={[
            {side: 'them', label: '匿名 A', text: '那我们该怎么办？', at: C.end_b1 - C.s10},
            {side: 'them', label: '匿名 C', text: '也许，不用假装不怕。', at: C.end_b2 - C.s10},
            {side: 'me', text: '把怕，变成好好活的理由。', at: C.end_b3 - C.s10},
          ]}
        />
        <NPCaption f={f} at={C.cap10} text="承认会结束，才更知道要怎么活。" y={980} />
      </Win>

      {/* 11 片尾题字 */}
      <Win f={f} a={C.s11} b={TL.end + 20}>
        <Snow f={f} n={60} strength={0.8} />
        <div style={{position: 'absolute', left: 0, right: 0, top: 400, textAlign: 'center', fontFamily: NPF.card, fontSize: 104, color: NP.cream, letterSpacing: 10, textShadow: '0 0 40px rgba(228,201,136,0.35)'}}>
          我们为什么假装不会死
        </div>
        <div style={{position: 'absolute', left: 0, right: 0, top: 580, textAlign: 'center', fontFamily: NPF.card, fontSize: 34, color: NP.cream, opacity: 0.75}}>
          参考：欧内斯特·贝克尔《拒斥死亡》（1973）
        </div>
        <PixelProp kind="star" x={960} y={360} u={8} />
        <AbsoluteFill style={{background: '#000', opacity: clamp01((f - (TL.end - 40)) / 36)}} />
      </Win>
    </AbsoluteFill>
  );
};
