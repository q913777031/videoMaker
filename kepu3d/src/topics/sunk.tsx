/**
 * 《电影烂到想走，为什么还坐着看完》3D 分镜：每个镜头 2–4 个卡拍子镜头，画面逐句写出字幕里的东西
 * （电影票与票价、烂片银幕、钟、锁死的钱箱、出口灯牌、季票座位、天平上的两小时……），关键词用场景内文字牌点出。
 * 撞击时刻只读 cue（镜头内秒）；落定动作用 land() 收在 cue 帧上，撞击闪光与震屏由 Kepu.tsx 统一叠加。
 */
import React from 'react';
import {Cam, Dust, Floor, GOLD, Sparks, Sweep, move, view} from '../lib/World';
import {
  Balance, Balloon, Bin, Book, Bubble, Clock, Coin, ExitSign, Figure, Flow, GlassBox, Gauge, Hourglass, Label, Lockbox,
  Neon, NightSky, Path, Receipt, Seat, Seats, Screen, Sheet, Sitter, SpotCone, Ticket, Tube,
} from '../lib/props3d';
import {V3, after, easeIO, easeOut, flicker, land, lerp, prog, pulse, rng, wobble} from '../lib/anim';
import {SceneFn} from '../types';

const Key: React.FC<{pos?: V3; k?: number; rim?: V3; rimK?: number}> = ({pos = [4, 8, 5], k = 1.4, rim = [-4, 3, -4], rimK = 18}) => (
  <>
    <directionalLight position={pos} intensity={k} color="#FFE9C2" />
    <pointLight position={rim} intensity={rimK} distance={20} decay={1.5} color={GOLD} />
  </>
);

const BAD = '★☆☆☆☆';
const ME: V3 = [0, 0.25, 1.1];

/** 影院：银幕（烂片）+ 4 排座椅 + 侧墙出口灯牌；主角坐在第 2 排正中。 */
const Hall: React.FC<{G: number; content?: string; sub?: string; noise?: number; exitK?: number; me?: boolean; slump?: number; meRot?: number}> = ({
  G, content = BAD, sub = '剧情卡住了', noise = 0.6, exitK = 0.5, me = true, slump = 0.3, meRot = 0,
}) => (
  <>
    <Screen pos={[0, 3.4, -8]} w={7.5} content={content} sub={sub} noise={noise} T={G} />
    <pointLight position={[0, 3, -6]} intensity={22} distance={18} decay={1.4} color="#C9D6E2" />
    {Array.from({length: 4}, (_, r) => Array.from({length: 7}, (_, c) => (
      <Seat key={`${r}-${c}`} pos={[(c - 3) * 0.85, r * 0.25, r * 1.1]} />
    )))}
    {Array.from({length: 4}, (_, r) => (
      <mesh key={r} position={[0, r * 0.25 - 0.13, r * 1.1]}>
        <boxGeometry args={[6.4, 0.26, 1.1]} />
        <meshStandardMaterial color="#141518" roughness={0.8} />
      </mesh>
    ))}
    {me && <Sitter pos={ME} rotY={meRot} slump={slump} />}
    <ExitSign pos={[3.6, 3.0, -3]} rotY={-Math.PI / 2} k={exitK} />
  </>
);

// ---------------------------------------------------------------- 01 电影烂到想走，／为什么还坐着看完？

const s01a: SceneFn = ({t, d, T, cue, G}) => {
  const k = land(T, cue.hook, 0.3);
  const p = pulse(T, cue.hook, 0.8);
  return (
    <>
      <Cam pos={view([0, 0.7, 0], lerp(2.6, 2.1, t / d), lerp(0.35, 0.2, t / d), 0.62)} target={[0, 0.85, -0.6]} fov={50} roll={-0.05} />
      <Key pos={[2, 6, 4]} k={1.2} />
      <Floor T={G} grid={0.1} />
      <Dust T={G} />
      <Screen pos={[0, 3.6, -8]} w={7.5} content={BAD} sub="剧情卡住了" noise={0.7} T={G} />
      <pointLight position={[0, 3, -5]} intensity={18} distance={14} color="#C9D6E2" />
      <Seat pos={[-0.8, 0, 0]} />
      <Seat pos={[0.85, 0, 0]} />
      <mesh position={[0, 0.47, 0]}>
        <boxGeometry args={[1.0, 0.06, 0.6]} />
        <meshStandardMaterial color="#2A2B31" metalness={0.5} roughness={0.4} />
      </mesh>
      <Ticket pos={[0.02, 0.5 + 1.6 * (1 - k), 0.0]} rot={[0.5 * (1 - k), 0.25 + 1.2 * (1 - k), 0.3 * (1 - k)]} s={0.62} lit={0.6 * p} />
      <Sparks t={T} at={cue.hook} origin={[0.02, 0.55, 0.0]} n={110} power={2.4} />
    </>
  );
};

const s01b: SceneFn = ({t, d, T, cue, G}) => {
  const s = 0.15 + 0.85 * land(T, cue.yawn, 0.4);
  const p = pulse(T, cue.yawn, 0.7);
  return (
    <>
      <Cam pos={move(t, d, [1.0, 3.8, 5.4], [0.7, 3.6, 4.6])} target={[0, 1.4, -5]} fov={50} />
      <Key pos={[3, 6, 6]} k={0.9} />
      <Floor T={G} grid={0.08} />
      <Dust T={G} center={[0, 2.5, -3]} />
      <Hall G={G} noise={0.6 + 1.4 * p} slump={s} sub={after(T, cue.yawn) ? '……' : '剧情卡住了'} />
    </>
  );
};

const s01c: SceneFn = ({t, d, G}) => (
  <>
    <Cam pos={move(t, d, [-0.9, 1.7, 2.9], [-0.5, 1.75, 2.4])} target={[3.6, 2.6, -2.6]} fov={48} />
    <Key pos={[0, 6, 4]} k={0.8} rim={[3, 3, -2]} rimK={25} />
    <Floor T={G} grid={0.08} />
    <Dust T={G} center={[2, 2.5, -1]} />
    <Hall G={G} exitK={flicker(G, 4, 0.6)} meRot={-0.7} slump={0.5} />
    <Label text="想走" pos={[2.6, 2.1, -2.2]} rot={[0, -1.2, 0]} h={0.36} k={1.6} />
  </>
);

const s01d: SceneFn = ({t, d, G}) => (
  <>
    <Cam pos={[0.6 + t * 0.3, 10.5, 5.2 - t * 0.4]} target={[0, 0, -2.2]} fov={50} />
    <Key pos={[0, 10, 2]} k={1.0} />
    <Floor T={G} grid={0.08} />
    <Dust T={G} center={[0, 3, -2]} />
    <Hall G={G} exitK={0.8} slump={1} />
    <Flow T={G} pts={[[0, 1, 1.1], [2.2, 1.6, -0.8], [3.5, 3, -3]]} speed={0.45} n={90} />
  </>
);

// ---------------------------------------------------------------- 02 票花了八十块，／现在走就白花了。

const s02a: SceneFn = ({t, d, G}) => (
  <>
    <Cam pos={view([0, 0.8, 0], lerp(3.9, 3.3, t / d), lerp(-0.25, 0.2, t / d), 0.85)} target={[0, 0.8, 0]} fov={50} />
    <Key pos={[2, 7, 3]} k={1.6} />
    <Floor T={G} />
    <Dust T={G} />
    <Sweep T={G} z={-4} period={1.5} />
    <Ticket pos={[0, 0.8, 0]} rot={[0, 0, 0]} price="" s={1} />
  </>
);

const s02b: SceneFn = ({t, d, T, cue, G}) => {
  const k = land(T, cue.price, 0.45);
  const on = after(T, cue.price);
  const p = pulse(T, cue.price, 0.8);
  return (
    <>
      <Cam pos={view([0, 0.8, 0.1], lerp(3.6, 3.1, t / d), 0.15, 0.95)} target={[0, 0.8, 0.1]} fov={50} />
      <Key pos={[2, 7, 3]} k={1.6} />
      <Floor T={G} />
      <Dust T={G} />
      <Ticket pos={[0, 0.8, 0]} price={on ? '¥80' : ''} lit={0.4 * p} />
      <group position={[-0.25, 0.85 + (on ? 0.6 * prog(T, cue.price + 0.15, 0.4) : 2.4 * (1 - k)), 0.18]}>
        <mesh position={[0, 0.25, 0]}>
          <cylinderGeometry args={[0.22, 0.26, 0.5, 32]} />
          <meshStandardMaterial color="#2A1E14" roughness={0.5} />
        </mesh>
        <mesh position={[0, 0.65, 0]}>
          <sphereGeometry args={[0.2, 24, 16]} />
          <meshStandardMaterial color={GOLD} metalness={0.9} roughness={0.25} />
        </mesh>
      </group>
      {on && <Label text="¥80" pos={[0.55, 1.0 + 0.15 * easeOut(prog(T, cue.price, 0.6)), 0.55]} rot={[-0.9, 0, 0]} h={0.3} k={1.4 + 2 * p} />}
      <Sparks t={T} at={cue.price} origin={[-0.25, 0.85, 0.18]} n={80} power={2} />
    </>
  );
};

const s02c: SceneFn = ({t, d, G}) => {
  const r = rng(9);
  return (
    <>
      <Cam pos={view([0, 1.2, 0], lerp(4.2, 3.5, t / d), 0.3 + t * 0.25, 0.3)} target={[0, 1.2, 0]} fov={50} />
      <Key pos={[2, 7, 4]} k={1.3} />
      <Floor T={G} />
      <Dust T={G} />
      <Ticket pos={[0, 1.2, 0]} rot={[Math.PI / 2 - 0.25, 0, 0]} />
      {Array.from({length: 14}, (_, i) => {
        const a = r() * Math.PI * 2;
        const u = (t * 0.55 + i / 14) % 1;
        const dist = 0.6 + u * 3.2;
        return <Coin key={i} pos={[Math.cos(a) * dist, 1.2 + Math.sin(a) * dist * 0.7, -u * 2]} rot={[t * 5 + i, 0.4, i]} s={1 - u * 0.6} />;
      })}
      <Label text="白花了？" pos={[0, 0.45, 0.4]} h={0.28} k={1.2 + 0.4 * Math.sin(G * 6)} />
    </>
  );
};

// ---------------------------------------------------------------- 03 于是又熬了一小时，／搭进去一整个晚上。

const s03a: SceneFn = ({t, d, G}) => (
  <>
    <Cam pos={view([0, 1.6, 0], lerp(4.6, 3.9, t / d), lerp(-0.3, -0.1, t / d), 0.05)} target={[0, 1.6, 0]} fov={50} roll={0.04} />
    <Key pos={[2, 6, 6]} k={1.5} />
    <Floor T={G} />
    <Dust T={G} />
    <Clock min={(t / d) * 45} pos={[0, 1.6, 0]} />
    <Sweep T={G} z={-3} period={1.2} />
  </>
);

const s03b: SceneFn = ({t, d, T, cue, G}) => {
  const k = land(T, cue.hour, cue.hour - (T - t));
  const on = after(T, cue.hour);
  const p = pulse(T, cue.hour, 0.8);
  return (
    <>
      <Cam pos={view([0, 1.6, 0], lerp(4.4, 3.8, t / d), lerp(0.45, 0.3, t / d), 0.12)} target={[0, 1.6, 0]} fov={50} />
      <Key pos={[3, 6, 6]} k={1.5} />
      <Floor T={G} />
      <Dust T={G} />
      <Clock min={lerp(45, 60, k)} pos={[0, 1.6, 0]} lit={p} />
      {on && <Label text="+1 小时" pos={[0, 1.0 + 0.1 * easeOut(prog(T, cue.hour, 0.5)), 0.3]} h={0.3} color="#9A6B1F" k={1 + 0.6 * p} />}
      <Sparks t={T} at={cue.hour} origin={[0, 2.5, 0.2]} n={90} power={2.2} />
    </>
  );
};

const s03c: SceneFn = ({t, d, G}) => (
  <>
    <Cam pos={move(t, d, [0.6, 1.2, 9], [0.4, 1.8, 7.6])} target={[0, 3.6, -6]} fov={50} />
    <Key pos={[0, 6, 6]} k={0.7} />
    <NightSky T={G} pos={[0, 0, -16]} moonY={9 - t * 0.8} />
    <Floor T={G} grid={0.06} />
    <mesh position={[0, 2, -4]}>
      <boxGeometry args={[6, 4, 3]} />
      <meshStandardMaterial color="#1A1B20" roughness={0.6} />
    </mesh>
    <Label text="影 院" pos={[0, 3.4, -2.48]} h={0.45} k={1.8 * flicker(G, 6, 0.4)} />
    {Array.from({length: 6}, (_, i) => (
      <mesh key={i} position={[-2.2 + i * 0.88, 1.5, -2.48]}>
        <planeGeometry args={[0.5, 0.7]} />
        <Neon k={0.6 + 0.6 * wobble(G * 2, i)} color="#FFE2A8" />
      </mesh>
    ))}
    <Label text="晚上 21:00 → 22:00" pos={[0, 5.3, -3]} h={0.26} k={1.1} font="KepuSans" />
  </>
);

// ---------------------------------------------------------------- 04 钱已经花出去了，／走不走都回不来。

const COINS = (() => {
  const r = rng(41);
  return Array.from({length: 12}, () => [r(), r()]);
})();

const s04a: SceneFn = ({t, d, T, cue, G}) => {
  const k = land(T, cue.lock, 0.4);
  const p = pulse(T, cue.lock, 0.8);
  const on = after(T, cue.lock);
  return (
    <>
      <Cam pos={view([0, 1.2, 0], lerp(5.0, 4.3, t / d), lerp(0.4, 0.25, t / d), 0.28)} target={[0, 1.2, 0]} fov={50} />
      <Key pos={[3, 7, 5]} k={1.6} />
      <Floor T={G} />
      <Dust T={G} />
      <Lockbox locked={k} lit={p} />
      {!on && COINS.map(([a, b], i) => {
        const u = (T * 0.8 + a) % 1;
        return <Coin key={i} pos={[(b - 0.5) * 0.3, 1.45 + (1 - u) * 3.2, 0]} rot={[Math.PI / 2, 0, u * 9]} />;
      })}
      <Sparks t={T} at={cue.lock} origin={[0, 1.0, 0.7]} n={100} power={2.4} />
    </>
  );
};

const s04b: SceneFn = ({t, d, G}) => (
  <>
    <Cam pos={move(t, d, [-3.4, 1.8, 3.0], [-2.8, 1.7, 2.4])} target={[0.4, 1.0, 0]} fov={50} />
    <Key pos={[2, 7, 5]} k={1.5} />
    <Floor T={G} />
    <Dust T={G} />
    <Lockbox locked={1} />
    <GlassBox pos={[0, 1.1, 0]} size={[2.2, 2.2, 1.8]} />
    <Figure pos={[-1.8, 0, 0.3]} turn={Math.PI / 2} arm={1.3 + 0.08 * Math.sin(G * 5)} />
    <Label text="回不来" pos={[0, 1.7, 1.0]} rot={[0, -0.6, 0]} h={0.3} k={1.5} />
  </>
);

const s04c: SceneFn = ({t, d, G}) => {
  const sink = easeIO(t / d);
  return (
    <>
      <Cam pos={view([0, 0.4, 0], lerp(4.8, 4.0, t / d), 0.2, 0.42)} target={[0, 0.4, 0]} fov={50} />
      <Key pos={[2, 7, 5]} k={1.4} />
      <Floor T={G} grid={0.05} />
      <Dust T={G} />
      <Lockbox locked={1} pos={[0, -1.5 * sink, 0]} />
      {[0, 1, 2].map((i) => {
        const u = (t * 0.9 + i / 3) % 1;
        return (
          <mesh key={i} position={[0, 0.02, 0]} rotation={[-Math.PI / 2, 0, 0]} scale={1 + u * 2.4}>
            <ringGeometry args={[0.95, 1, 64]} />
            <meshBasicMaterial color={GOLD} transparent opacity={0.8 * (1 - u)} toneMapped={false} />
          </mesh>
        );
      })}
    </>
  );
};

// ---------------------------------------------------------------- 05 坐着不走的理由，／是电影，还是票钱？

const s05a: SceneFn = ({t, d, T, cue, G}) => {
  const lit = after(T, cue.halt) ? 1 - 0.4 * prog(T, cue.halt, 1) : 0.15;
  return (
    <>
      <Cam pos={move(t, d, [0.3, 2.4, 9.2], [0.1, 2.3, 8.2])} target={[0, 2.3, 0]} fov={50} />
      <Key pos={[2, 6, 6]} k={1.2} />
      <Floor T={G} />
      <Dust T={G} />
      <Screen pos={[0, 3.5, -0.5]} w={2.6} content={BAD} noise={0.4} T={G} glowK={0.6 + lit} />
      <Label text="电影" pos={[0, 2.65, -0.4]} h={0.32} k={0.5 + 2 * lit} />
      <Sitter pos={[-0.9, 0, 0.6]} rotY={Math.PI + 0.3} slump={0.4} s={0.6} />
      <Ticket pos={[0, 0.9, 1.6]} rot={[Math.PI / 2 - 0.3, 0, 0]} s={0.7} lit={0.3 * lit} />
      <Label text="票钱" pos={[0, 0.3, 2.0]} h={0.3} k={0.5 + 2 * lit} />
    </>
  );
};

const s05b: SceneFn = ({t, d, G}) => (
  <>
    <Cam pos={move(t, d, [0.8, 3.4, 3.2], [0.4, 3.5, 2.4])} target={[0, 3.6, -0.5]} fov={50} />
    <Key pos={[2, 6, 6]} k={1.0} />
    <Floor T={G} />
    <Dust T={G} center={[0, 3, 0]} />
    <Screen pos={[0, 3.6, -0.5]} w={3.2} content={BAD} sub="还要一小时" noise={0.9} T={G} />
    <Label text="电影：不好看" pos={[0, 3.0, -0.35]} h={0.22} k={1.6} />
  </>
);

const s05c: SceneFn = ({t, d, G}) => (
  <>
    <Cam pos={view([0, 1.0, 0], lerp(3.6, 3.0, t / d), -0.4 + t * 0.3, 0.55)} target={[0, 1.0, 0]} fov={50} />
    <Key pos={[2, 7, 4]} k={1.6} />
    <Floor T={G} />
    <Dust T={G} />
    <Ticket pos={[0, 1.0, 0]} lit={0.3 + 0.2 * Math.sin(G * 5)} />
    <Label text="票钱：已经花了" pos={[0, 0.45, 0.75]} rot={[-0.5, 0, 0]} h={0.2} k={1.6} />
  </>
);

// ---------------------------------------------------------------- 06 1985年论文：／投入越多越想坚持。

const SHEETS = Array.from({length: 9}, (_, i) => i);

const s06a: SceneFn = ({t, d, T, cue, G}) => {
  const k = land(T, cue.merge, 1.6);
  const on = after(T, cue.merge);
  const p = pulse(T, cue.merge, 0.9);
  return (
    <>
      <Cam pos={move(t, d, [0, 3.4, 6.4], [0.3, 2.8, 5.0])} target={[0, 1, 0]} fov={50} />
      <Key pos={[2, 8, 5]} />
      <Floor T={G} />
      <Dust T={G} />
      <Sweep T={G} z={-5} period={2.2} />
      {!on && SHEETS.map((i) => {
        const a = (i / SHEETS.length) * Math.PI * 2 + T * 2.4 * (1 + k);
        const r = 2.6 * (1 - k);
        return <Sheet key={i} pos={[Math.cos(a) * r, 1 + Math.sin(a * 2 + i) * 0.6 * (1 - k), Math.sin(a) * r]} rot={[0.4, -a, 0.2]} />;
      })}
      {on && <Book open={0} pos={[0, 0.2, 0]} s={1 + 0.25 * p} />}
      {on && <Label text="1985" pos={[0, 2.5 + 0.2 * easeOut(prog(T, cue.merge, 0.5)), 0]} h={0.55} k={1.5 + 2 * p} font="KepuSans" />}
      <Sparks t={T} at={cue.merge} origin={[0, 0.8, 0]} power={3.2} />
    </>
  );
};

const s06b: SceneFn = ({t, d, G}) => {
  const open = easeOut(prog(t, 0, 1.3));
  return (
    <>
      <Cam pos={view([0, 0.7, 0], lerp(4.8, 3.9, t / d), lerp(0.5, 0.3, t / d), 0.55)} target={[0, 0.7, 0]} fov={50} />
      <Key pos={[3, 6, 4]} k={1.2} />
      <pointLight position={[0, 1.2, 0]} intensity={24 * open} distance={8} color="#FFE2A8" />
      <Floor T={G} />
      <Dust T={G} n={340} />
      <Book open={open} pos={[0, 0.2, 0]} light={open} />
      <Label text="Arkes & Blumer, 1985" pos={[0, 1.55, -0.4]} h={0.16} k={1.4} font="KepuSans" opacity={open} />
    </>
  );
};

const s06c: SceneFn = ({t, d, G}) => (
  <>
    <Cam pos={view([0, 2.0, 0], lerp(6.6, 5.8, t / d), 0.15, 0.1)} target={[0, 2.0, 0]} fov={50} />
    <Key pos={[2, 7, 5]} k={1.4} />
    <Floor T={G} />
    <Dust T={G} />
    {[0, 1, 2, 3, 4].map((i) => (
      <mesh key={i} position={[-1.0 + i * 0.5, 0.3 + i * 0.35, 0]}>
        <boxGeometry args={[0.4, 0.6 + i * 0.7, 0.4]} />
        <Neon k={0.5 + 0.5 * i * Math.min(1, t / d + 0.3)} />
      </mesh>
    ))}
    <Label text="投入越多 →" pos={[0, 0.25, 0.7]} h={0.24} k={1.3} />
    <Label text="越想坚持" pos={[0.3, 3.45, 0.3]} h={0.26} k={1.8} />
  </>
);

// ---------------------------------------------------------------- 07 剧院季票买得越贵，／之后去看的场次越多。

const Theater: React.FC<{G: number; lit: number}> = ({G, lit}) => (
  <>
    <Seats lit={lit} rows={8} cols={7} pos={[0, 0, 0.5]} />
    <mesh position={[0, 0.3, -2.2]}>
      <boxGeometry args={[9, 0.6, 2.6]} />
      <meshStandardMaterial color="#1A1412" roughness={0.6} />
    </mesh>
    <mesh position={[0, 3.2, -3.6]}>
      <planeGeometry args={[9, 5]} />
      <meshStandardMaterial color="#3A0F12" roughness={0.8} emissive="#5A1A16" emissiveIntensity={0.25} />
    </mesh>
    <SpotCone pos={[Math.sin(G * 1.2) * 2.5, 0.6, -2.2]} h={7} r={1.4} k={1.2} />
  </>
);

const s07a: SceneFn = ({t, d, T, cue, G}) => {
  const on = after(T, cue.cheap);
  return (
    <>
      <Cam pos={move(t, d, [0.3, 2.4, -3.6], [0.8, 2.6, -3.0])} target={[0, 1.0, 3.5]} fov={52} />
      <Key pos={[0, 8, -6]} k={1.2} rim={[0, 4, 6]} rimK={14} />
      <Floor T={G} grid={0.12} />
      <Dust T={G} center={[0, 2, 2]} />
      <Theater G={G} lit={on ? 7 : 0} />
      <Ticket pos={[0.5, 1.9, -1.9]} rot={[-1.2, Math.PI + 0.2 * Math.sin(t * 2), 0]} s={0.55} title="剧院季票" price="折扣价" />
      {on && <Label text="去的场次：少" pos={[0, 1.6, 1.2]} rot={[0, Math.PI, 0]} h={0.26} k={1.6} />}
    </>
  );
};

const s07b: SceneFn = ({t, d, T, cue, G}) => {
  const on = after(T, cue.full);
  const p = pulse(T, cue.full, 0.6);
  return (
    <>
      <Cam pos={move(t, d, [4.8, 3.2, 0.0], [4.0, 2.9, 1.0])} target={[0, 1, 2.8]} fov={50} />
      <Key pos={[6, 8, 0]} k={1.2} />
      <Floor T={G} grid={0.12} />
      <Dust T={G} center={[0, 2, 2]} />
      <Theater G={G} lit={on ? 44 : 7} />
      <Ticket pos={[2.3, 2.5, 1.4]} rot={[-1.3, -Math.PI / 2 + 0.2 * Math.sin(t * 2.6), 0]} s={0.6} title="剧院季票" price="原价" lit={0.8 * p} />
      {on && <Label text="去的场次：多" pos={[1.2, 2.2, 2.6]} rot={[0, Math.PI / 2, 0]} h={0.3} k={1.6 + 2 * p} />}
      <Sparks t={T} at={cue.full} origin={[0, 1.4, 2.4]} n={110} power={3.4} />
    </>
  );
};

const s07c: SceneFn = ({t, d, T, cue, G}) => (
  <>
    <Cam pos={move(t, d, [-1.0, 7.0, -4.5], [1.4, 6.2, -3.6])} target={[0, 0.5, 3]} fov={50} />
    <Key pos={[0, 10, -4]} k={1.2} />
    <Floor T={G} grid={0.12} />
    <Dust T={G} center={[0, 2, 2]} />
    <Theater G={G} lit={after(T, cue.full) ? 44 : 7} />
    <Label text="付得越多，去得越多" pos={[0, 2.6, 3]} rot={[-0.9, Math.PI, 0]} h={0.36} k={1.6} />
  </>
);

// ---------------------------------------------------------------- 08 这叫沉没成本效应：／为过去的投入买单。

const Pedestal: React.FC<{plate?: number}> = ({plate = 0.4}) => (
  <>
    <mesh position={[0, 0.15, 0]}>
      <cylinderGeometry args={[1.6, 1.75, 0.3, 64]} />
      <meshStandardMaterial color="#15161A" metalness={0.6} roughness={0.3} />
    </mesh>
    <mesh position={[0, 0.31, 0]} rotation={[-Math.PI / 2, 0, 0]}>
      <ringGeometry args={[1.5, 1.58, 64]} />
      <Neon k={2.4} />
    </mesh>
    <Label text="沉没成本效应" pos={[0, 0.16, 1.77]} h={0.17} k={0.6 + 2.4 * plate} />
  </>
);

const s08a: SceneFn = ({t, G}) => (
  <>
    <Cam pos={view([0, 1.4, 0], 5.2, -0.4 + t * 0.5, 0.12)} target={[0, 1.3, 0]} fov={50} />
    <Key pos={[0, 9, 2]} k={1.6} />
    <Floor T={G} />
    <Dust T={G} />
    <Pedestal plate={0.2} />
    <Ticket pos={[0, 1.35, 0]} rot={[Math.PI / 2, G * 0.8, 0]} s={0.9} />
    <SpotCone pos={[0, 0.3, 0]} h={8} r={1.9} k={1.6} />
  </>
);

const s08b: SceneFn = ({t, d, T, cue, G}) => {
  const k = land(T, cue.name, 0.5);
  const on = after(T, cue.name);
  const p = pulse(T, cue.name, 0.8);
  const H = 2.6;
  return (
    <>
      <Cam pos={view([0, 1.3, 0], lerp(5.6, 4.8, t / d), lerp(0.25, 0.1, t / d), 0.1)} target={[0, 1.4, 0]} fov={50} />
      <Key pos={[3, 9, 4]} k={1.6} />
      <Floor T={G} />
      <Dust T={G} />
      <Pedestal plate={on ? 1 : 0.15} />
      <Ticket pos={[0, 1.35, 0]} rot={[Math.PI / 2, G * 0.8, 0]} s={0.9} lit={0.5 * p} />
      <GlassBox pos={[0, 0.32 + H / 2 + (on ? 0 : 6 * (1 - k)), 0]} size={[2.4, H, 2.4]} edge={2 + 3 * p} />
      <Sparks t={T} at={cue.name} origin={[0, 0.4, 0]} n={120} power={2.8} />
    </>
  );
};

const s08c: SceneFn = ({t, d, G}) => (
  <>
    <Cam pos={move(t, d, [1.0, 1.1, 7.0], [0.6, 0.9, 5.6])} target={[0, 0.7, 1.5]} fov={50} />
    <Key pos={[3, 8, 6]} k={1.6} />
    <Floor T={G} />
    <Dust T={G} />
    <Pedestal plate={1} />
    <Ticket pos={[0, 1.35, 0]} rot={[Math.PI / 2, G * 0.8, 0]} s={0.9} />
    <GlassBox pos={[0, 0.32 + 1.3, 0]} size={[2.4, 2.6, 2.4]} />
    <Receipt T={G} len={1.2 + 4.8 * easeOut(t / d)} pos={[0, 0, 1.9]} />
    <Label text="为过去买单" pos={[0, 0.2, 3.4]} rot={[-0.6, 0, 0]} h={0.26} k={1.6} />
  </>
);

// ---------------------------------------------------------------- 09 作者认为：／人们不想显得在浪费。

const WasteBin: React.FC = () => (
  <>
    <Bin pos={[1.3, 0, 0]} />
    <Label text="浪费" pos={[1.3, 0.6, 0.62]} h={0.24} k={1.4} />
  </>
);

const s09a: SceneFn = ({t, d, T, cue, G}) => {
  const arm = 1.35 * easeOut(prog(T, cue.reach - 0.25, 0.5));
  return (
    <>
      <Cam pos={move(t, d, [-3.4, 1.9, 2.8], [-2.9, 1.7, 2.3])} target={[0.6, 1.2, 0]} fov={50} />
      <Key pos={[2, 8, 5]} />
      <Floor T={G} />
      <Dust T={G} />
      <WasteBin />
      <Ticket pos={[1.3, 2.0 + Math.sin(G * 3) * 0.1, 0]} rot={[Math.PI / 2 - 0.3, -0.9 + Math.sin(G) * 0.2, 0]} s={0.55} />
      <Figure pos={[-0.9, 0, 0]} turn={Math.PI / 2} arm={arm} />
    </>
  );
};

const s09b: SceneFn = ({t, d, T, cue, G}) => {
  const k = land(T, cue.block, 0.4);
  const on = after(T, cue.block);
  const back = easeOut(prog(T, cue.block, 0.8));
  const p = pulse(T, cue.block, 0.6);
  return (
    <>
      <Cam pos={move(t, d, [3.6, 1.8, 2.4], [3.0, 1.6, 1.9])} target={[-0.2, 1.2, 0]} fov={50} />
      <Key pos={[4, 8, 3]} />
      <Floor T={G} />
      <Dust T={G} />
      <WasteBin />
      <Ticket pos={[lerp(1.3, 0.1, back), 2.0 + Math.sin(G * 3) * 0.1, 0]} rot={[Math.PI / 2 - 0.3, 0.9, 0]} s={0.55} lit={0.5 * p} />
      <mesh position={[0.65, 1.2 + (on ? 0 : 3.5 * (1 - k)), 0]}>
        <boxGeometry args={[0.06, 2.4, 1.6]} />
        <meshStandardMaterial color="#FFF1D2" transparent opacity={0.25} emissive={GOLD} emissiveIntensity={0.15 + 1.2 * p} />
      </mesh>
      <Figure pos={[-0.9, 0, 0]} turn={Math.PI / 2} arm={1.35} armL={1.0 * back} />
      <Sparks t={T} at={cue.block} origin={[0.65, 0.1, 0]} n={70} power={2.4} />
    </>
  );
};

const s09c: SceneFn = ({t, d, G}) => (
  <>
    <Cam pos={view([0, 1.4, 0], 4.2, 0.3 + t * 0.3, 0.1)} target={[0, 1.4, 0]} fov={50} />
    <Key pos={[0, 8, 3]} k={1.6} />
    <Floor T={G} />
    <Dust T={G} />
    <Figure pos={[0, 0, 0]} arm={1.2} armL={1.2} />
    <Ticket pos={[0, 1.2, 0.45]} rot={[Math.PI / 2, 0, 0]} s={0.45} lit={0.4 + 0.2 * Math.sin(G * 6)} />
    <Label text="不能浪费" pos={[0, 2.25, 0]} h={0.3} k={1.5} />
  </>
);

// ---------------------------------------------------------------- 10 投入过的人，／还会高估成功的可能。

const s10a: SceneFn = ({t, d, T, cue, G}) => {
  const before = 0.38 + 0.03 * Math.sin(G * 20);
  const v = after(T, cue.inflate) ? 0.97 + 0.04 * Math.sin((T - cue.inflate) * 18) * Math.exp(-(T - cue.inflate) * 3) : lerp(before, 0.97, land(T, cue.inflate, 0.35));
  return (
    <>
      <Cam pos={move(t, d, [0, 2.0, 6.4], [0.4, 1.8, 5.4])} target={[0, 1.3, 0]} fov={50} />
      <Key pos={[2, 7, 6]} />
      <Floor T={G} />
      <Dust T={G} />
      <Gauge value={v} pos={[0, 0.7, 0]} s={0.85} />
      <Label text="后半场会好看？" pos={[0, 2.15, 0]} h={0.26} k={1.5} />
      <Sparks t={T} at={cue.inflate} origin={[1.3, 0.8, 0.2]} n={70} power={2.2} />
    </>
  );
};

const s10b: SceneFn = ({t, d, G}) => {
  const up = easeIO(t / d);
  return (
    <>
      <Cam pos={[1.4, lerp(0.8, 2.8, up), lerp(3.8, 3.4, up)]} target={[0, lerp(0.9, 2.7, up), 0]} fov={50} />
      <Key pos={[3, 7, 5]} />
      <Floor T={G} />
      <Dust T={G} />
      <Tube level={0.62 + 0.32 * easeOut(t / d)} real={0.42} />
      <Label text="以为的" pos={[0, 3.05, 0.65]} h={0.2} k={1.6} />
      <Label text="实际的" pos={[0, 1.15, 0.65]} h={0.2} color="#F5F0E8" k={1.1} />
      <Sweep T={G} z={-4} period={1.8} />
    </>
  );
};

const s10c: SceneFn = ({t, d, G}) => (
  <>
    <Cam pos={move(t, d, [1.6, 1.4, 4.6], [1.2, 1.6, 3.8])} target={[0, 1.3, 0]} fov={50} />
    <Key pos={[3, 7, 5]} />
    <Floor T={G} />
    <Dust T={G} />
    <Balloon size={0.6 + 0.3 * easeOut(t / d)} pos={[-0.2, 0.9, -0.6]} T={G} />
    <mesh position={[0.5, 0.3, 1.4]}>
      <sphereGeometry args={[0.3, 32, 24]} />
      <meshStandardMaterial color="#3A3C44" roughness={0.5} metalness={0.3} />
    </mesh>
    <Label text="期待" pos={[-0.2, 1.9, 0.6]} h={0.3} color="#2A2420" k={1} />
    <Label text="实际" pos={[0.5, 0.85, 1.4]} h={0.18} color="#F5F0E8" k={1.1} />
  </>
);

// ---------------------------------------------------------------- 11 假如票是免费的，／你还会坐下去吗？

const s11a: SceneFn = ({t, d, T, cue, G}) => {
  const k = land(T, cue.reset, 0.6);
  const on = after(T, cue.reset);
  const p = pulse(T, cue.reset, 0.8);
  return (
    <>
      <Cam pos={view([0, 1.4, 0], lerp(4.0, 3.4, t / d), 0.1, 0.12)} target={[0, 1.4, 0]} fov={50} />
      <Key pos={[2, 7, 6]} k={1.5} />
      <Floor T={G} />
      <Dust T={G} />
      <Ticket pos={[0, 1.4, 0]} rot={[Math.PI / 2, on ? 0 : Math.PI * 2 * k, 0]} price={on ? '¥0' : '¥80'} lit={0.6 * p} />
      {on && <Label text="免费" pos={[0, 2.45 + 0.2 * easeOut(prog(T, cue.reset, 0.5)), 0]} h={0.45} k={1.6 + 2 * p} />}
      <Sparks t={T} at={cue.reset} origin={[0, 1.4, 0.2]} n={120} power={2.8} />
    </>
  );
};

const s11b: SceneFn = ({t, d, G}) => (
  <>
    <Cam pos={move(t, d, [1.2, 2.3, 5.0], [0.8, 2.1, 4.2])} target={[0, 1.7, -4]} fov={50} />
    <Key pos={[3, 6, 6]} k={0.9} />
    <Floor T={G} grid={0.08} />
    <Dust T={G} center={[0, 2.5, -2]} />
    <Hall G={G} slump={0.6} />
    <Ticket pos={[0.9, 1.7, 1.2]} rot={[Math.PI / 2, -0.4 + 0.2 * Math.sin(G * 2), 0]} s={0.45} price="¥0" lit={0.3} />
    <Label text="还坐吗？" pos={[0.9, 1.15, 1.4]} h={0.22} k={1.5} />
  </>
);

const s11c: SceneFn = ({t, d, G}) => (
  <>
    <Cam pos={view([0, 1.2, 0], lerp(3.0, 2.5, t / d), -0.3 + t * 0.2, 0.2)} target={[0, 1.2, 0]} fov={50} />
    <Key pos={[2, 6, 3]} k={1.4} />
    <Floor T={G} grid={0.3} />
    <Dust T={G} n={300} />
    <Ticket pos={[0, 1.2, 0]} rot={[Math.PI / 2, 0, 0.1]} price="¥0" lit={0.2 + 0.15 * Math.sin(G * 5)} />
    <Sweep T={G} z={-3} period={1.0} />
  </>
);

// ---------------------------------------------------------------- 12 只比较接下来的／两小时值不值。

const MiniScreen: React.FC<{G: number}> = ({G}) => (
  <group position={[0, 0.45, 0]} scale={0.32}>
    <Screen w={3} content={BAD} noise={0.3} T={G} />
  </group>
);
const MiniTime: React.FC<{G: number}> = ({G}) => <Hourglass T={G} fill={0.2} s={0.22} pos={[0, 0.02, 0]} />;

const s12a: SceneFn = ({t, d, T, cue, G}) => {
  const k = land(T, cue.weigh, 0.45);
  const on = after(T, cue.weigh);
  const tilt = on ? lerp(0.12, -0.2, easeOut(prog(T, cue.weigh, 0.5))) + 0.03 * Math.sin((T - cue.weigh) * 9) * Math.exp(-(T - cue.weigh) * 2) : 0.12;
  return (
    <>
      <Cam pos={view([0, 2.0, 0], lerp(8.4, 7.2, t / d), lerp(0.15, 0.05, t / d), 0.05)} target={[0, 2.0, 0]} fov={50} />
      <Key pos={[2, 9, 5]} />
      <Floor T={G} />
      <Dust T={G} />
      <Balance tilt={tilt} left={on ? <MiniTime G={G} /> : null} right={<MiniScreen G={G} />} />
      {!on && (
        <group position={[-1.7, 2.75 + 0.12 * 1.7 - 0.95 + 4.5 * (1 - k), 0]}>
          <MiniTime G={G} />
        </group>
      )}
      <Label text="接下来两小时" pos={[-1.15, 0.6, 0.6]} h={0.15} k={1.6} />
      <Label text="这部电影" pos={[1.3, 0.6, 0.6]} h={0.15} color="#F5F0E8" k={1.1} />
      <Sparks t={T} at={cue.weigh} origin={[-1.7, 2.1, 0]} n={80} power={2.4} />
    </>
  );
};

const s12b: SceneFn = ({t, d, G}) => (
  <>
    <Cam pos={view([0, 1.9, 0], 3.8, -0.7 + t * 0.4, 0.12)} target={[0, 1.9, 0]} fov={50} />
    <Key pos={[0, 8, 4]} k={1.6} />
    <Floor T={G} />
    <Dust T={G} />
    <Balance tilt={-0.2 + 0.015 * Math.sin(G * 3)} left={<MiniTime G={G} />} right={<MiniScreen G={G} />} />
    <Label text="值不值？" pos={[0, 0.7, 0.9]} h={0.26} k={1.6} />
  </>
);

const s12c: SceneFn = ({t, d, G}) => (
  <>
    <Cam pos={move(t, d, [0, 2.6, 5.4], [0, 3.2, 9.0])} target={[0, 2, -1]} fov={50} />
    <Key pos={[0, 8, 5]} k={1.6} />
    <Floor T={G} />
    <Dust T={G} />
    <Balance tilt={-0.2} left={<MiniTime G={G} />} right={<MiniScreen G={G} />} />
    <Ticket pos={[2.6, 1.0, -4]} rot={[Math.PI / 2, -0.5, 0]} s={0.8} lit={0} />
    <Label text="已经花掉的，不上秤" pos={[2.6, 2.0, -4]} h={0.24} color="#F5F0E8" k={0.9 * (1 - 0.5 * (t / d))} />
  </>
);

// ---------------------------------------------------------------- 13 不好意思先走，／可以和同伴商量。

const Pair: React.FC<{G: number; slump?: number}> = ({G, slump = 0.4}) => (
  <>
    <Screen pos={[0, 3.4, -7]} w={7} content={BAD} sub="剧情卡住了" noise={0.6} T={G} />
    <pointLight position={[0, 3, -5]} intensity={18} distance={14} color="#C9D6E2" />
    {[-1, 0, 1, 2].map((i) => <Seat key={i} pos={[i * 0.85 - 0.42, 0, 0]} />)}
    <Sitter pos={[-0.42, 0, 0.0]} rotY={0.25} slump={slump} />
    <Sitter pos={[0.43, 0, 0.0]} rotY={-0.25} slump={slump} />
  </>
);

const s13a: SceneFn = ({t, d, T, cue, G}) => {
  const pop = after(T, cue.talk) ? 1 : 0;
  return (
    <>
      <Cam pos={move(t, d, [1.4, 2.2, 4.6], [1.0, 2.1, 3.9])} target={[0, 1.5, -1]} fov={50} />
      <Key pos={[2, 6, 5]} k={0.8} />
      <Floor T={G} grid={0.08} />
      <Dust T={G} />
      <Pair G={G} />
      <Bubble text="要不走吧？" pos={[-0.45, 2.05, 0.1]} pop={0.8 * pop * (1 + 0.15 * pulse(T, cue.talk, 0.4))} />
    </>
  );
};

const s13b: SceneFn = ({t, d, G}) => (
  <>
    <Cam pos={view([0, 1.4, 0], 4.6, 0.6 - t * 0.35, 0.22)} target={[0, 1.6, 0]} fov={50} />
    <Key pos={[2, 6, 5]} k={0.8} rim={[3, 3, -2]} rimK={20} />
    <Floor T={G} grid={0.08} />
    <Dust T={G} />
    <Pair G={G} slump={0.1} />
    <Bubble text="要不走吧？" pos={[-0.45, 2.05, 0.1]} pop={0.75} />
    <Bubble text="好，走！" pos={[0.55, 2.45, 0.1]} pop={0.75 * easeOut(prog(t, 0.3, 0.35))} flip />
    <ExitSign pos={[3.0, 2.8, -1.5]} rotY={-Math.PI / 2} k={0.8 + 0.2 * Math.sin(G * 6)} />
  </>
);

// ---------------------------------------------------------------- 14 起身离开不是浪费，／是把晚上留给自己。

const s14a: SceneFn = ({t, d, T, cue, G}) => {
  const on = after(T, cue.turn);
  const p = pulse(T, cue.turn, 0.8);
  return (
    <>
      <Cam pos={move(t, d, [-1.6, 2.4, 4.6], [-1.2, 2.2, 3.8])} target={[1.6, 1.6, -1.6]} fov={50} />
      <Key pos={[3, 6, 6]} k={0.9} rim={[3, 3, -2]} rimK={10 + 30 * (on ? 1 : 0)} />
      <Floor T={G} grid={0.08} />
      <Dust T={G} center={[1, 2.5, -1]} />
      <Hall G={G} me={!on} slump={0.7} exitK={on ? 1.2 + p : 0.3} />
      {on && <Figure pos={[0.4, 0.25, 1.1]} turn={-1.9} />}
      {on && <Path from={[1.0, 0.27, 1.1]} to={[3.4, 0.27, -2.6]} n={7} lit={7} w={0.6} />}
      {on && <Flow T={G} pts={[[1.0, 0.4, 1.1], [2.4, 0.5, -0.8], [3.4, 0.6, -2.6]]} speed={0.7} n={110} />}
      <Sparks t={T} at={cue.turn} origin={[0.4, 1.0, 1.1]} n={80} power={2.4} />
    </>
  );
};

const s14b: SceneFn = ({t, d, G}) => {
  const open = easeOut(prog(t, 0.1, 1.2));
  return (
    <>
      <Cam pos={move(t, d, [0.4, 2.2, 6.2], [0.2, 2.1, 4.8])} target={[0, 2.4, -2]} fov={50} />
      <Key pos={[0, 6, 4]} k={0.6} />
      <NightSky T={G} pos={[0, 0, -18]} moonY={7} />
      <Floor T={G} grid={0.06} />
      <Dust T={G} />
      <mesh position={[0, 1.5, -1.2]}>
        <planeGeometry args={[1.6, 3]} />
        <Neon k={0.4 + 1.6 * open} color="#FFE2A8" opacity={open} />
      </mesh>
      <group position={[-0.8, 1.5, -1.15]} rotation={[0, -open * 1.9, 0]}>
        <mesh position={[0.8, 0, 0]}>
          <boxGeometry args={[1.6, 3, 0.1]} />
          <meshStandardMaterial color="#2A2B31" metalness={0.5} roughness={0.4} />
        </mesh>
      </group>
      {[-1, 1].map((sg) => (
        <mesh key={sg} position={[sg * 3.4, 1.5, -1.2]}>
          <boxGeometry args={[5.2, 3.2, 0.2]} />
          <meshStandardMaterial color="#141518" roughness={0.8} />
        </mesh>
      ))}
      <ExitSign pos={[0, 3.25, -1.05]} k={1} />
      <Figure pos={[0, 0, 1.0 - t * 0.6]} turn={Math.PI} walk={t * 1.6} />
    </>
  );
};

const s14c: SceneFn = ({t, d, G}) => {
  const z = -t * 0.9;
  return (
    <>
      <Cam pos={[0.7, 1.7, z + 3.4]} target={[0, 1.6, z - 6]} fov={50} />
      <Key pos={[0, 6, -10]} k={0.8} />
      <NightSky T={G} pos={[0, 0, -26]} moonY={8} />
      <Floor T={G} flow={0} grid={0.1} />
      <Dust T={G} center={[0, 2, z - 4]} />
      <Path from={[0, 0, 2]} to={[0, 0, -20]} n={18} lit={18} />
      <Flow T={G} pts={[[0, 0.15, 2], [0, 0.2, -9], [0, 0.4, -20]]} speed={0.4} n={240} />
      {[[-3, -8], [3.2, -12], [-3.4, -15]].map(([x, zz], i) => (
        <group key={i} position={[x, 0, zz]}>
          <mesh position={[0, 1.4, 0]}>
            <boxGeometry args={[2, 2.8, 2]} />
            <meshStandardMaterial color="#1A1B20" />
          </mesh>
          <mesh position={[x > 0 ? -1.01 : 1.01, 1.6, 0]} rotation={[0, x > 0 ? -Math.PI / 2 : Math.PI / 2, 0]}>
            <planeGeometry args={[0.7, 0.7]} />
            <Neon k={1.6} color="#FFE2A8" />
          </mesh>
        </group>
      ))}
      <Figure pos={[0, 0, z]} turn={Math.PI} walk={t * 1.6} />
      <Label text="晚上，留给自己" pos={[0, 2.8, z - 6]} h={0.34} k={1.7} />
    </>
  );
};

// ---------------------------------------------------------------- 15 参考资料

const s15a: SceneFn = ({t, G}) => (
  <>
    <Cam pos={view([0, 1.5, 0], 6.5, t * 0.15, 0.1)} target={[0, 2.2, -4]} fov={50} />
    <Key k={0.7} />
    <Floor T={G} grid={0.08} />
    <Dust T={G} />
    <Hall G={G} content="完" sub="" noise={0} me={false} exitK={1} />
  </>
);
const s15b: SceneFn = ({t, G}) => (
  <>
    <Cam pos={view([0, 0.6, 0], 6, 0.6 + t * 0.2, 0.35)} target={[0, 0.6, 0]} fov={50} />
    <Key k={1} />
    <Floor T={G} />
    <Dust T={G} />
    <Book open={1} pos={[0, 0.2, 0]} light={0.4} />
  </>
);
const s15c: SceneFn = ({t, G}) => (
  <>
    <Cam pos={[0.5, 2.0, 4 - t * 0.4]} target={[0, 1.4, -8]} fov={50} />
    <Key k={0.8} />
    <NightSky T={G} pos={[0, 0, -22]} moonY={8} />
    <Floor T={G} />
    <Dust T={G} />
    <Path from={[0, 0, 2]} to={[0, 0, -16]} n={14} lit={14} />
    <Flow T={G} pts={[[0, 0.15, 2], [0, 0.2, -7], [0, 0.4, -16]]} speed={0.3} />
  </>
);

export const SUNK: Record<number, SceneFn[]> = {
  1: [s01a, s01b, s01c, s01d],
  2: [s02a, s02b, s02c],
  3: [s03a, s03b, s03c],
  4: [s04a, s04b, s04c],
  5: [s05a, s05b, s05c],
  6: [s06a, s06b, s06c],
  7: [s07a, s07b, s07c],
  8: [s08a, s08b, s08c],
  9: [s09a, s09b, s09c],
  10: [s10a, s10b, s10c],
  11: [s11a, s11b, s11c],
  12: [s12a, s12b, s12c],
  13: [s13a, s13b],
  14: [s14a, s14b, s14c],
  15: [s15a, s15b, s15c],
};
