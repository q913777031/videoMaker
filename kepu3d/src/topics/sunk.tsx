/**
 * 《项目明明没希望，为什么还舍不得停》3D 分镜：每个镜头 2–4 个卡拍子镜头，画面逐句贴合字幕。
 * 撞击时刻只读 cue（镜头内秒）；落定动作用 land() 收在 cue 帧上，撞击闪光与震屏由 Kepu.tsx 统一叠加。
 */
import React from 'react';
import {Cam, Dust, Floor, GOLD, Sparks, Sweep, glow, move, view} from '../lib/World';
import {
  Arrow, Balance, Balloon, Bin, Book, Calendar, Card, Coin, Figure, Flag, Flow, GlassBox, Gauge, Gold, Hourglass, Lamp,
  Neon, Path, Receipt, Seats, Sheet, SpotCone, Table, Tower, Tube, Wall, towerTop,
} from '../lib/props3d';
import {V3, after, clamp, easeIO, easeIn, easeOut, flicker, land, lerp, prog, pulse, rng, wobble} from '../lib/anim';
import {SP, SceneFn} from '../types';

const Key: React.FC<{pos?: V3; k?: number; rim?: V3; rimK?: number}> = ({pos = [4, 8, 5], k = 1.4, rim = [-4, 3, -4], rimK = 18}) => (
  <>
    <directionalLight position={pos} intensity={k} color="#FFE9C2" />
    <pointLight position={rim} intensity={rimK} distance={20} decay={1.5} color={GOLD} />
  </>
);


/** 背景远处的死墙（贯穿前半段的“没希望”意象）。 */
const DeadEnd: React.FC<{G: number; z?: number; x?: number}> = ({G, z = -9, x = 0}) => (
  <Wall pos={[x, 0, z]} crack={flicker(G, 3, 0.8)} />
);

// ---------------------------------------------------------------- 01 项目明明没希望，／怎么还舍不得停？

const s01a: SceneFn = ({t, d, T, cue, G}) => {
  const top = towerTop(13);
  const y = top + 0.04 + 2.4 * (1 - land(T, cue.hook, 0.3));
  const shake = pulse(T, cue.hook, 0.9);
  return (
    <>
      <Cam pos={view([0, 3.0, 0], lerp(5.8, 4.9, t / d), lerp(0.45, 0.3, t / d), -0.2)} target={[0, 3.0, 0]} fov={50} roll={-0.06} />
      <Key pos={[2, 9, 3]} k={1.8 * flicker(G, 1, 0.5)} />
      <Floor T={G} />
      <Dust T={G} />
      <Sweep T={G} z={-6} period={1.4} k={3} />
      <Tower n={13} T={G} sway={0.8 + 6 * shake} lit={(i) => (i > 9 ? shake : 0)} />
      <Card pos={[0.05, y, 0]} rot={[0.15 * (1 - land(T, cue.hook, 0.3)), 0.4, 0]} gold lit={0.6 + 2 * shake} s={1.2} />
      <Sparks t={T} at={cue.hook} origin={[0, top + 0.1, 0]} n={120} power={3.6} />
      <SpotCone pos={[0, 0, 0]} h={9} r={2.2} />
      <DeadEnd G={G} />
    </>
  );
};

const s01b: SceneFn = ({t, d, T, cue, G}) => {
  const top = towerTop(13);
  const y = top + 0.3 + 4 * (1 - land(T, cue.add, 0.5));
  const shake = pulse(T, cue.add, 0.8);
  return (
    <>
      <Cam pos={move(t, d, [0.9, 2.6, 6.4], [0.6, 2.4, 5.3])} target={[0, 1.4, -4]} fov={50} />
      <Key pos={[6, 7, 4]} />
      <Floor T={G} />
      <Dust T={G} center={[0, 2.5, -3]} />
      <Tower n={13} T={G} pos={[-0.8, 0, 1.5]} sway={0.6 + 5 * shake} />
      <Card pos={[-0.8, after(T, cue.add) ? top + 0.06 : y, 1.5]} rot={[0, 0.7, 0]} gold lit={0.5 + 2 * shake} s={1.1} />
      <Sparks t={T} at={cue.add} origin={[-0.8, top + 0.1, 1.5]} power={3} />
      <Figure pos={[0.35, 0, -0.5]} turn={Math.PI} />
      <Path from={[0.35, 0, -1.2]} to={[0.2, 0, -8.4]} n={10} lit={6} />
      <DeadEnd G={G} />
    </>
  );
};

const s01c: SceneFn = ({t, d, G}) => (
  <>
    <Cam pos={move(t, d, [1.2, 1.3, -3.4], [-0.6, 1.8, -4.3])} target={[0, 2.2, -9]} fov={46} />
    <Key pos={[-3, 6, -2]} k={1.2} rim={[0, 2, -8]} rimK={30 * flicker(G, 5, 0.9)} />
    <Floor T={G} />
    <Dust T={G} center={[0, 2, -7]} spread={[8, 5, 6]} />
    <DeadEnd G={G} />
    <Figure pos={[0.35, 0, -6.4]} turn={Math.PI} s={0.9} />
    <Path from={[0.35, 0, -1]} to={[0.2, 0, -8.6]} n={10} lit={6} />
  </>
);

const s01d: SceneFn = ({t, d, G}) => (
  <>
    <Cam pos={[0.6 + t * 0.4, 13.5, 1.6 - t * 0.5]} target={[0, 0, -3.6]} fov={50} />
    <Key pos={[0, 12, 2]} k={1.8} />
    <Floor T={G} />
    <Dust T={G} center={[0, 3, -3]} />
    <Tower n={14} T={G} pos={[0, 0, 1]} />
    <Figure pos={[0, 0, -0.6]} turn={Math.PI} />
    <Path from={[0, 0, -1.2]} to={[0, 0, -8.4]} n={10} lit={6} />
    <Flow T={G} pts={[[0, 0.1, -1.2], [0.4, 0.1, -4.5], [0, 0.1, -8.5]]} speed={0.5} />
    <DeadEnd G={G} />
  </>
);

// ---------------------------------------------------------------- 02 已经投了三个月，／现在停就全白费了。

const s02a: SceneFn = ({t, d, G}) => (
  <>
    <Cam pos={view([0, 0.6, 0], lerp(4.6, 3.8, t / d), lerp(0.6, 0.35, t / d), 0.55)} target={[0, 0.6, 0]} fov={50} roll={0.05} />
    <Key pos={[3, 6, 4]} />
    <Floor T={G} />
    <Dust T={G} />
    <Sweep T={G} z={-5} period={1.6} />
    <Calendar T={t} rate={6} lit={0.1} />
  </>
);

const s02b: SceneFn = ({t, d, T, cue, G}) => {
  const on = after(T, cue.clock);
  const p = pulse(T, cue.clock, 0.8);
  const ring = prog(T, cue.clock, 0.9);
  return (
    <>
      <Cam pos={view([0, 1.9, 0], 7.2, 0.2 + t * 0.4, 0.06)} target={[0, 1.9, 0]} fov={50} />
      <Key k={1.6} />
      <Floor T={G} />
      <Dust T={G} />
      <Tower n={14} T={G} sway={0.6 + 3 * p} lit={(i) => (on ? (i % 3 === 2 ? 1 : 0.45) * (0.6 + 0.4 * p) : 0)} />
      {on && (
        <mesh position={[0, 0.05, 0]} rotation={[-Math.PI / 2, 0, 0]} scale={0.5 + ring * 5}>
          <ringGeometry args={[0.92, 1, 64]} />
          <meshBasicMaterial color={glow(GOLD, 3)} transparent opacity={1 - ring} toneMapped={false} />
        </mesh>
      )}
      <Sparks t={T} at={cue.clock} origin={[0, 2, 0]} n={80} power={2.6} />
    </>
  );
};

const s02c: SceneFn = ({t, d, G}) => (
  <>
    <Cam pos={view([0, 1.25, 0], lerp(4.4, 3.5, t / d), lerp(0.1, 0.3, t / d), 0.08)} target={[0, 1.25, 0]} fov={50} />
    <Key pos={[3, 5, 4]} k={1.8} rim={[-2, 2, -3]} rimK={25} />
    <Floor T={G} />
    <Dust T={G} />
    <Hourglass T={G} fill={0.6 + 0.25 * (t / d)} />
    <Tower n={14} T={G} pos={[1.6, 0, -6]} lit={(i) => (i % 3 === 2 ? 0.8 : 0.3)} />
  </>
);

// ---------------------------------------------------------------- 03 于是又加了一周，／再加一点预算。

const COINS = (() => {
  const r = rng(41);
  return Array.from({length: 26}, () => [r(), r(), r(), r()]);
})();

const s03a: SceneFn = ({t, d, G}) => {
  const top = towerTop(14);
  return (
    <>
      <Cam pos={view([0, top - 0.3, 0], lerp(4.2, 3.6, t / d), lerp(0.5, 0.3, t / d), -0.35)} target={[0, top - 0.3, 0]} fov={50} />
      <Key pos={[2, 9, 4]} />
      <Floor T={G} />
      <Dust T={G} />
      <Tower n={14} T={G} />
      {COINS.map(([a, b, c, e], i) => {
        const u = (t * 0.9 + a) % 1;
        const y = top + 0.1 + (1 - u * u) * 5;
        return <Coin key={i} pos={[(b - 0.5) * 1.2, y, (c - 0.5) * 0.8]} rot={[t * 6 + e * 6, 0, t * 4 + a * 6]} />;
      })}
      {Array.from({length: Math.floor(4 + t * 4)}, (_, i) => (
        <Coin key={`p${i}`} pos={[Math.sin(i * 2.4) * 0.3, top + 0.03 + i * 0.05, Math.cos(i * 2.4) * 0.2]} />
      ))}
    </>
  );
};

const s03b: SceneFn = ({t, d, T, cue, G}) => {
  const top = towerTop(14);
  const k = land(T, cue.more, 0.5);
  const on = after(T, cue.more);
  const p = pulse(T, cue.more, 0.8);
  return (
    <>
      <Cam pos={view([0, 2.3, -1.5], lerp(7.6, 6.6, t / d), lerp(0.55, 0.4, t / d), 0.12)} target={[0, 2.3, -1.5]} fov={50} />
      <Key pos={[5, 8, 5]} />
      <Floor T={G} />
      <Dust T={G} />
      <Tower n={14} T={G} sway={0.5 + 5 * p} />
      <Card pos={[-0.1, top + 0.06 + (on ? 0 : 4.5 * (1 - k)), 0.1]} rot={[0, 0.3, 0]} gold lit={0.4 + 2 * p} />
      <Card pos={[0.1, top + 0.11 + (on ? 0 : 5.5 * (1 - k)), -0.1]} rot={[0, -0.5, 0]} lit={0.3 + 1.5 * p} />
      <Sparks t={T} at={cue.more} origin={[0, top + 0.1, 0]} power={3} />
      <Path from={[0, 0, -1.2]} to={[0, 0, -8.4]} n={10} lit={on ? 8 : 6} />
      <DeadEnd G={G} />
    </>
  );
};

const s03c: SceneFn = ({t, d, G}) => (
  <>
    <Cam pos={move(t, d, [0.7, 0.5, -0.8], [0.5, 0.6, -4.0])} target={[0, 1.5, -9.2]} fov={50} />
    <Key pos={[2, 6, 0]} k={1.4} rim={[0, 2, -8]} rimK={30 * flicker(G, 9, 0.9)} />
    <Floor T={G} flow={1.2} />
    <Dust T={G} center={[0, 1.5, -5]} />
    <Path from={[0, 0, -1.2]} to={[0, 0, -8.4]} n={10} lit={8 + 0.4 * Math.sin(G * 8)} />
    <Flow T={G} pts={[[0, 0.1, -1], [0, 0.1, -5], [0, 0.1, -8.5]]} speed={0.8} />
    <DeadEnd G={G} />
  </>
);

// ---------------------------------------------------------------- 04 投入越多，／越难开口说放弃。

const s04a: SceneFn = ({t, d, T, cue, G}) => {
  const grown = 9 + Math.floor(9 * easeIn(prog(T, 0, cue.tower - 0.5)));
  const top = towerTop(grown);
  const k = land(T, cue.tower, 0.45);
  const on = after(T, cue.tower);
  const p = pulse(T, cue.tower, 1.0);
  const tilt = easeIO(t / d);
  return (
    <>
      <Cam pos={[2.2, lerp(0.9, 3.0, tilt), 6.4]} target={[0, lerp(1.6, 4.6, tilt), 0]} fov={50} />
      <Key pos={[3, 10, 4]} />
      <Floor T={G} />
      <Dust T={G} center={[0, 4, 0]} spread={[12, 9, 12]} />
      <Tower n={on ? grown + 1 : grown} T={G} sway={0.5 + 4 * p} lit={(i) => (i >= grown ? p * 2 : 0)} />
      {!on && (
        <mesh position={[0, top + 0.13 + 5 * (1 - k), 0]} rotation={[0, 0.2, 0]}>
          <boxGeometry args={[1.5, 0.24, 0.95]} />
          <Gold lit={0.6} />
        </mesh>
      )}
      <Sparks t={T} at={cue.tower} origin={[0, top + 0.1, 0]} n={130} power={3.6} />
      <Figure pos={[1.3, 0, 2.2]} s={0.9} turn={-0.6} />
    </>
  );
};

const s04b: SceneFn = ({t, d, G}) => {
  const len = 3 + 4 * easeOut(t / d);
  return (
    <>
      <Cam pos={move(t, d, [0.5, 0.8, 4.6], [0.3, 0.75, 3.8])} target={[0, 3.0, -3]} fov={50} />
      <directionalLight position={[0, 8, -10]} intensity={1.2} color="#FFE9C2" />
      <pointLight position={[0, 5, -6.5]} intensity={80} distance={20} decay={1.4} color="#FFD58A" />
      <mesh position={[0, 4, -7.5]}>
        <circleGeometry args={[3.2, 48]} />
        <Neon k={2.6} color="#FFE2A8" />
      </mesh>
      <Floor T={G} />
      <Dust T={G} center={[0, 3, -2]} />
      <Tower n={18} T={G} pos={[0, 0, -3]} scale={1.4} sway={0.3} />
      <mesh position={[0, 0.01, -3 + len / 2]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[2.4, len]} />
        <meshBasicMaterial color="#000000" transparent opacity={0.75} depthWrite={false} />
      </mesh>
      <Figure pos={[0, 0, 1.2]} turn={Math.PI} s={0.85} lean={0.15} />
    </>
  );
};

const s04c: SceneFn = ({t, d, G}) => (
  <>
    <Cam pos={view([0.5, 1.9, 0], lerp(3.7, 3.0, t / d), 0.45, 0.05)} target={[0.5, 1.9, 0]} fov={50} roll={-0.04} />
    <Key pos={[3, 6, 5]} k={2} />
    <Floor T={G} />
    <Dust T={G} />
    <Flag T={G} sink={0.35 * easeIn(t / d)} />
    <Tower n={18} T={G} pos={[-1.6, 0, -4.5]} scale={1.2} />
  </>
);

// ---------------------------------------------------------------- 05 继续做的理由，／是未来，还是过去？

const Crossroad: React.FC<{G: number; lit: number; turn?: number}> = ({G, lit, turn = 0}) => (
  <>
    <Tower n={12} T={G} pos={[0, 0, 3.4]} lit={(i) => (i % 3 === 2 ? lit : lit * 0.4)} />
    <Figure pos={[0, 0, 0]} turn={turn} />
    <Path from={[0, 0, 2.6]} to={[0, 0, 0.6]} n={3} lit={lit * 3} />
    <Path from={[0, 0, -0.6]} to={[0, 0, -9]} n={10} lit={lit * 10} />
    <Arrow pos={[0, 0, -2.4]} lit={lit} s={1.2} />
  </>
);

const s05a: SceneFn = ({t, d, T, cue, G}) => {
  const lit = after(T, cue.halt) ? 1 - 0.4 * prog(T, cue.halt, 1) : 0.1;
  return (
    <>
      <Cam pos={move(t, d, [1.0, 11, 4.5], [0.6, 11.5, 3.6])} target={[0, 0, -1.5]} fov={50} />
      <Key pos={[0, 10, 2]} />
      <Floor T={G} />
      <Dust T={G} />
      <Crossroad G={G} lit={lit} />
    </>
  );
};

const s05b: SceneFn = ({t, d, G}) => (
  <>
    <Cam pos={move(t, d, [0.5, 1.8, -1.8], [0.35, 1.7, -1.1])} target={[0, 1.9, 3.4]} fov={50} />
    <Key pos={[0, 6, 6]} k={1.6} rim={[0, 3, 5]} rimK={30} />
    <Floor T={G} />
    <Dust T={G} center={[0, 2, 3]} />
    <Crossroad G={G} lit={0.6 + 0.4 * wobble(G * 3, 1)} turn={Math.PI} />
  </>
);

const s05c: SceneFn = ({t, d, G}) => (
  <>
    <Cam pos={move(t, d, [0.35, 0.5, 1.4], [0.2, 0.6, -0.4])} target={[0, 0.9, -12]} fov={50} />
    <Key pos={[0, 6, -4]} k={1.4} />
    <mesh position={[0, 1.4, -24]}>
      <circleGeometry args={[4, 48]} />
      <Neon k={2.2} color="#FFE2A8" />
    </mesh>
    <Floor T={G} flow={1.4} />
    <Dust T={G} center={[0, 1.5, -6]} />
    <Path from={[0, 0, -0.6]} to={[0, 0, -16]} n={14} lit={14} />
    <Flow T={G} pts={[[0, 0.15, -0.5], [0.3, 0.2, -8], [0, 0.4, -18]]} speed={0.6} n={220} />
    <Arrow pos={[0, 0, -2.4]} lit={0.7 + 0.3 * Math.sin(G * 9)} s={1.2} />
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
      <Sparks t={T} at={cue.merge} origin={[0, 0.5, 0]} power={3.2} />
    </>
  );
};

const s06b: SceneFn = ({t, d, G}) => {
  const open = easeOut(prog(t, 0, 1.3));
  return (
    <>
      <Cam pos={view([0, 0.5, 0], lerp(4.8, 3.9, t / d), lerp(0.5, 0.3, t / d), 0.6)} target={[0, 0.5, 0]} fov={50} />
      <Key pos={[3, 6, 4]} k={1.4} />
      <pointLight position={[0, 1.2, 0]} intensity={30 * open} distance={8} color="#FFE2A8" />
      <Floor T={G} />
      <Dust T={G} n={340} />
      <Book open={open} pos={[0, 0.2, 0]} light={open} />
    </>
  );
};

const s06c: SceneFn = ({t, d, G}) => {
  const flip = (t * 1.8) % 1;
  return (
    <>
      <Cam pos={move(t, d, [0.2, 5.6, 0.6], [0.05, 4.4, 0.4])} target={[0, 0.3, 0]} fov={50} roll={Math.PI / 2 + 0.15} />
      <Key pos={[0, 8, 2]} k={1.8} />
      <pointLight position={[0, 1.2, 0]} intensity={30} distance={8} color="#FFE2A8" />
      <Floor T={G} />
      <Dust T={G} />
      <Book open={1} pos={[0, 0.2, 0]} light={0.7} />
      <group position={[0, 0.42, 0]} rotation={[0, 0, Math.PI * flip]}>
        <Sheet pos={[0.75, 0, 0]} rot={[0, 0, 0]} s={1.6} lit={0.3} />
      </group>
    </>
  );
};

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

const s07a: SceneFn = ({t, d, T, cue, G}) => (
  <>
    <Cam pos={move(t, d, [0.3, 2.4, -3.6], [0.8, 2.6, -3.0])} target={[0, 1.0, 3.5]} fov={52} />
    <Key pos={[0, 8, -6]} k={1.4} rim={[0, 4, 6]} rimK={14} />
    <Floor T={G} grid={0.12} />
    <Dust T={G} center={[0, 2, 2]} />
    <Theater G={G} lit={after(T, cue.cheap) ? 7 : 0} />
    <Card pos={[0.55, 1.9, -2.0]} rot={[1.2, t * 1.5, 0.2]} s={0.55} />
  </>
);

const s07b: SceneFn = ({t, d, T, cue, G}) => (
  <>
    <Cam pos={move(t, d, [4.8, 3.2, 0.0], [4.0, 2.9, 1.0])} target={[0, 1, 2.8]} fov={50} />
    <Key pos={[6, 8, 0]} k={1.4} />
    <Floor T={G} grid={0.12} />
    <Dust T={G} center={[0, 2, 2]} />
    <Theater G={G} lit={after(T, cue.full) ? 44 : 7} />
    <Card pos={[2.4, 2.4, 1.2]} rot={[1.3, t * 2.6, 0.3]} gold lit={0.6 + 2 * pulse(T, cue.full, 0.6)} s={0.7} />
    <Sparks t={T} at={cue.full} origin={[0, 1.4, 2.4]} n={110} power={3.4} />
  </>
);

const s07c: SceneFn = ({t, d, T, cue, G}) => (
  <>
    <Cam pos={move(t, d, [-1.0, 7.0, -4.5], [1.4, 6.2, -3.6])} target={[0, 0.5, 3]} fov={50} />
    <Key pos={[0, 10, -4]} k={1.4} />
    <Floor T={G} grid={0.12} />
    <Dust T={G} center={[0, 2, 2]} />
    <Theater G={G} lit={after(T, cue.full) ? 44 : 7} />
  </>
);

// ---------------------------------------------------------------- 08 这叫沉没成本效应：／为过去的投入买单。

const Pedestal: React.FC = () => (
  <>
    <mesh position={[0, 0.15, 0]}>
      <cylinderGeometry args={[1.6, 1.75, 0.3, 64]} />
      <meshStandardMaterial color="#15161A" metalness={0.6} roughness={0.3} />
    </mesh>
    <mesh position={[0, 0.31, 0]} rotation={[-Math.PI / 2, 0, 0]}>
      <ringGeometry args={[1.5, 1.58, 64]} />
      <Neon k={2.4} />
    </mesh>
  </>
);

const s08a: SceneFn = ({t, G}) => (
  <>
    <Cam pos={view([0, 1.7, 0], 5.8, -0.4 + t * 0.7, 0.1)} target={[0, 1.7, 0]} fov={50} />
    <Key pos={[0, 9, 2]} k={2} />
    <Floor T={G} />
    <Dust T={G} />
    <Pedestal />
    <group position={[0, 0.3, 0]} rotation={[0, G * 0.8, 0]}>
      <Tower n={12} T={G} scale={0.85} sway={0.2} />
    </group>
    <SpotCone pos={[0, 0.3, 0]} h={8} r={1.9} k={1.6} />
  </>
);

const s08b: SceneFn = ({t, d, T, cue, G}) => {
  const k = land(T, cue.name, 0.5);
  const on = after(T, cue.name);
  const H = 3.6;
  return (
    <>
      <Cam pos={view([0, 1.9, 0], lerp(6.2, 5.4, t / d), lerp(0.7, 0.55, t / d), 0.08)} target={[0, 1.9, 0]} fov={50} />
      <Key pos={[3, 9, 4]} k={2} />
      <Floor T={G} />
      <Dust T={G} />
      <Pedestal />
      <group position={[0, 0.3, 0]} rotation={[0, G * 0.8, 0]}>
        <Tower n={12} T={G} scale={0.85} sway={0.2 + 3 * pulse(T, cue.name, 0.6)} />
      </group>
      <GlassBox pos={[0, 0.32 + H / 2 + (on ? 0 : 6 * (1 - k)), 0]} size={[2.6, H, 2.6]} edge={2 + 3 * pulse(T, cue.name, 0.8)} />
      <Sparks t={T} at={cue.name} origin={[0, 0.4, 0]} n={120} power={2.8} />
    </>
  );
};

const s08c: SceneFn = ({t, d, G}) => (
  <>
    <Cam pos={move(t, d, [1.0, 1.1, 7.0], [0.6, 0.9, 5.6])} target={[0, 0.7, 1.5]} fov={50} />
    <Key pos={[3, 8, 6]} k={1.8} />
    <Floor T={G} />
    <Dust T={G} />
    <Pedestal />
    <group position={[0, 0.3, 0]} rotation={[0, G * 0.8, 0]}>
      <Tower n={12} T={G} scale={0.85} sway={0.2} />
    </group>
    <GlassBox pos={[0, 0.32 + 1.8, 0]} size={[2.6, 3.6, 2.6]} />
    <Receipt T={G} len={1.2 + 4.8 * easeOut(t / d)} pos={[0, 0, 1.9]} />
  </>
);

// ---------------------------------------------------------------- 09 作者认为：／人们不想显得在浪费。

const s09a: SceneFn = ({t, d, T, cue, G}) => {
  const arm = 1.35 * easeOut(prog(T, cue.reach - 0.25, 0.5));
  return (
    <>
      <Cam pos={move(t, d, [-3.4, 1.9, 2.8], [-2.9, 1.7, 2.3])} target={[0.6, 1.2, 0]} fov={50} />
      <Key pos={[2, 8, 5]} />
      <Floor T={G} />
      <Dust T={G} />
      <Bin pos={[1.3, 0, 0]} />
      <Card pos={[1.3, 2.0 + Math.sin(G * 3) * 0.1, 0]} rot={[0.3, G, 0.2]} gold lit={0.5} s={0.7} />
      <Figure pos={[-0.9, 0, 0]} turn={Math.PI / 2} arm={arm} />
    </>
  );
};

const s09b: SceneFn = ({t, d, T, cue, G}) => {
  const k = land(T, cue.block, 0.4);
  const on = after(T, cue.block);
  const back = easeOut(prog(T, cue.block, 0.8));
  return (
    <>
      <Cam pos={move(t, d, [3.6, 1.8, 2.4], [3.0, 1.6, 1.9])} target={[-0.2, 1.2, 0]} fov={50} />
      <Key pos={[4, 8, 3]} />
      <Floor T={G} />
      <Dust T={G} />
      <Bin pos={[1.3, 0, 0]} />
      <Card pos={[lerp(1.3, 0.1, back), 2.0 + Math.sin(G * 3) * 0.1, 0]} rot={[0.3, G, 0.2]} gold lit={0.5 + 2 * pulse(T, cue.block, 0.6)} s={0.7} />
      <mesh position={[0.65, 1.2 + (on ? 0 : 3.5 * (1 - k)), 0]}>
        <boxGeometry args={[0.06, 2.4, 1.6]} />
        <meshStandardMaterial color="#FFF1D2" transparent opacity={0.25} emissive={GOLD} emissiveIntensity={0.15 + 1.2 * pulse(T, cue.block, 0.6)} />
      </mesh>
      <Figure pos={[-0.9, 0, 0]} turn={Math.PI / 2} arm={1.35} armL={1.0 * back} />
      <Sparks t={T} at={cue.block} origin={[0.65, 0.1, 0]} n={70} power={2.4} />
    </>
  );
};

const s09c: SceneFn = ({t, d, G}) => (
  <>
    <Cam pos={view([0, 1.4, 0], 4.6, 2.0 + t * 0.35, 0.06)} target={[0, 1.4, 0]} fov={50} />
    <Key pos={[0, 8, 3]} k={1.8} />
    <Floor T={G} />
    <Dust T={G} />
    <Tower n={10} T={G} pos={[0, 0, -0.6]} lit={(i) => (i === 9 ? 0.6 + 0.4 * Math.sin(G * 6) : 0)} />
    <Figure pos={[0, 0, 0.55]} turn={Math.PI} arm={1.6} armL={1.6} lean={-0.1} />
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
      <Sparks t={T} at={cue.inflate} origin={[1.3, 0.8, 0.2]} n={70} power={2.2} />
    </>
  );
};

const s10b: SceneFn = ({t, d, G}) => {
  const up = easeIO(t / d);
  return (
    <>
      <Cam pos={[1.4, lerp(0.8, 2.8, up), lerp(3.6, 3.2, up)]} target={[0, lerp(0.9, 2.7, up), 0]} fov={50} />
      <Key pos={[3, 7, 5]} />
      <Floor T={G} />
      <Dust T={G} />
      <Tube level={0.62 + 0.32 * easeOut(t / d)} real={0.42} />
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
    <Balloon size={0.65 + 0.45 * easeOut(t / d)} pos={[-0.2, 0.9, -0.6]} T={G} />
    <mesh position={[0.5, 0.3, 1.4]}>
      <sphereGeometry args={[0.3, 32, 24]} />
      <meshStandardMaterial color="#3A3C44" roughness={0.5} metalness={0.3} />
    </mesh>
  </>
);

// ---------------------------------------------------------------- 11 假如今天才开始，／你还会选它吗？

const s11a: SceneFn = ({t, d, T, cue, G}) => {
  const on = after(T, cue.reset);
  return (
    <>
      <Cam pos={view([0, 1.9, 0], 6.6, 0.2 + t * 0.3, 0.08)} target={[0, 1.9, 0]} fov={50} />
      <Key pos={[0, 9, 4]} />
      <Floor T={G} />
      <Dust T={G} />
      <Tower n={14} T={G} wire={on ? 1 - 0.5 * prog(T, cue.reset, 1.0) : 0} sway={on ? 0.1 : 0.4} />
      <Sparks t={T} at={cue.reset} origin={[0, 2, 0]} n={150} power={3.2} />
    </>
  );
};

const s11b: SceneFn = ({t, d, G}) => (
  <>
    <Cam pos={move(t, d, [-2.2, 1.6, 4.6], [-1.6, 1.5, 3.8])} target={[0.3, 1.1, -1]} fov={50} />
    <Key pos={[0, 9, 2]} k={1.4} />
    <Floor T={G} grid={0.3} />
    <Dust T={G} />
    <Tower n={14} T={G} pos={[1.5, 0, -6]} wire={0.25} sway={0.1} />
    <Card pos={[0, 1.0, 0]} rot={[Math.PI / 2, G * 0.6, 0]} gold lit={0.25} />
    <SpotCone pos={[0, 0, 0]} h={8} r={1.4} k={1.4} />
    <Figure pos={[-0.7, 0, 1.4]} turn={Math.PI * 0.8} />
  </>
);

const s11c: SceneFn = ({t, d, G}) => (
  <>
    <Cam pos={move(t, d, [0.9, 1.25, 2.2], [0.5, 1.1, 1.6])} target={[0, 1, 0]} fov={50} />
    <Key pos={[2, 6, 3]} k={1.6} />
    <Floor T={G} grid={0.3} />
    <Dust T={G} n={300} />
    <Card pos={[0, 1.0, 0]} rot={[Math.PI / 2, G * 0.6, 0]} gold lit={0.2 + 0.15 * Math.sin(G * 5)} s={0.8} />
    <Sweep T={G} z={-3} period={1.0} />
  </>
);

// ---------------------------------------------------------------- 12 只比较接下来的／代价和收获。

const Cost: React.FC = () => (
  <>
    {[[-0.2, 0.1, 0], [0.2, 0.1, 0.1], [0, 0.3, -0.05]].map((p, i) => (
      <mesh key={i} position={p as V3}>
        <boxGeometry args={[0.32, 0.2, 0.32]} />
        <meshStandardMaterial color="#2A2C33" roughness={0.6} />
      </mesh>
    ))}
  </>
);
const Gain: React.FC<{G: number}> = ({G}) => (
  <>
    {[[-0.2, 0.15, 0], [0.22, 0.15, 0.05], [0, 0.42, 0]].map((p, i) => (
      <mesh key={i} position={p as V3}>
        <sphereGeometry args={[0.15, 24, 16]} />
        <Neon k={1.6 + 1.2 * Math.sin(G * 4 + i)} />
      </mesh>
    ))}
  </>
);

const s12a: SceneFn = ({t, d, T, cue, G}) => {
  const k = land(T, cue.weigh, 0.45);
  const on = after(T, cue.weigh);
  const tilt = on ? lerp(-0.12, 0.2, easeOut(prog(T, cue.weigh, 0.5))) + 0.03 * Math.sin((T - cue.weigh) * 9) * Math.exp(-(T - cue.weigh) * 2) : -0.12;
  return (
    <>
      <Cam pos={view([0, 2.0, 0], lerp(8.4, 7.2, t / d), lerp(0.15, 0.05, t / d), 0.05)} target={[0, 2.0, 0]} fov={50} />
      <Key pos={[2, 9, 5]} />
      <Floor T={G} />
      <Dust T={G} />
      <Balance tilt={tilt} left={<Cost />} right={on ? <Gain G={G} /> : null} />
      {!on && (
        <group position={[1.7, 2.75 + 0.12 * 1.7 - 0.95 + 4.5 * (1 - k), 0]}>
          <Gain G={G} />
        </group>
      )}
      <Sparks t={T} at={cue.weigh} origin={[1.7, 2.1, 0]} n={80} power={2.4} />
    </>
  );
};

const s12b: SceneFn = ({t, d, G}) => (
  <>
    <Cam pos={view([0, 1.9, 0], 3.8, -0.7 + t * 0.4, 0.12)} target={[0, 1.9, 0]} fov={50} />
    <Key pos={[0, 8, 4]} k={1.8} />
    <Floor T={G} />
    <Dust T={G} />
    <Balance tilt={0.2 + 0.015 * Math.sin(G * 3)} left={<Cost />} right={<Gain G={G} />} />
  </>
);

const s12c: SceneFn = ({t, d, G}) => (
  <>
    <Cam pos={move(t, d, [0, 2.6, 5.4], [0, 3.2, 9.0])} target={[0, 2, -1]} fov={50} />
    <Key pos={[0, 8, 5]} k={1.8} />
    <Floor T={G} />
    <Dust T={G} />
    <Balance tilt={0.2} left={<Cost />} right={<Gain G={G} />} />
    <Tower n={14} T={G} pos={[0, 0, -6]} wire={0.6 * (1 - t / d)} sway={0.1} />
  </>
);

// ---------------------------------------------------------------- 13 停下来很难，／可以找人一起复盘。

const Talk: React.FC<{G: number; power: number; arrange: number}> = ({G, power, arrange}) => (
  <>
    <Lamp power={power} pos={[0, 3.6, 0]} />
    <Table />
    <Figure pos={[-1.6, 0, 0]} turn={Math.PI / 2} arm={0.6} />
    <Figure pos={[1.6, 0, 0]} turn={-Math.PI / 2} armL={0.5} />
    {[-0.6, 0, 0.6].map((x, i) => (
      <Card key={i} pos={[lerp((i - 1) * 0.3 + 0.2, x, arrange), 0.92, lerp(0.2 * (i - 1), 0, arrange)]}
        rot={[0, lerp(0.6 * (i - 1), 0, arrange), 0]} s={0.5} gold={i === 1} lit={i === 1 ? power * 0.6 : 0} />
    ))}
  </>
);

const s13a: SceneFn = ({t, d, T, cue, G}) => {
  const power = after(T, cue.lamp) ? 1 : 0.12 + 0.3 * flicker(G, 13, 1);
  return (
    <>
      <Cam pos={move(t, d, [3.6, 2.6, 5.4], [3.0, 2.7, 4.6])} target={[0, 1.3, 0]} fov={50} />
      <ambientLight intensity={0.05} />
      <Floor T={G} grid={0.08} />
      <Dust T={G} />
      <Talk G={G} power={power} arrange={0} />
    </>
  );
};

const s13b: SceneFn = ({t, d, G}) => (
  <>
    <Cam pos={view([0, 1.2, 0], 5.2, 1.4 + t * 0.4, 0.33)} target={[0, 1.2, 0]} fov={50} />
    <Floor T={G} grid={0.08} />
    <Dust T={G} />
    <Talk G={G} power={0.92 + 0.08 * flicker(G, 2, 1)} arrange={easeIO(prog(t, 0.2, 1.4))} />
  </>
);

// ---------------------------------------------------------------- 14 停下不是白费，／是把以后的时间留住。

const s14a: SceneFn = ({t, d, T, cue, G}) => {
  const turn = lerp(Math.PI, 0.3, land(T, cue.turn, 0.6));
  const on = after(T, cue.turn);
  return (
    <>
      <Cam pos={move(t, d, [-1.0, 1.7, 4.8], [-0.7, 1.6, 4.0])} target={[0.4, 1.1, -1]} fov={50} />
      <Key pos={[4, 8, 3]} k={1.6} />
      <Floor T={G} />
      <Dust T={G} />
      <DeadEnd G={G} z={-5} />
      <Figure pos={[0, 0, 0]} turn={turn} />
      <Path from={[0.3, 0, 0.4]} to={[2.4, 0, 7]} n={8} lit={on ? 8 : 0} />
      {on && <Flow T={G} pts={[[0.3, 0.1, 0.4], [1.2, 0.15, 3.5], [2.4, 0.2, 7]]} speed={0.7} />}
      <Sparks t={T} at={cue.turn} origin={[0.8, 0.2, 0]} n={70} power={2.4} />
    </>
  );
};

const s14b: SceneFn = ({t, d, G}) => {
  const flip = easeIO(prog(t, 0, 0.7));
  return (
    <>
      <Cam pos={view([0, 1.25, 0], lerp(4.6, 3.7, t / d), lerp(-0.4, -0.25, t / d), 0.08)} target={[0, 1.25, 0]} fov={50} />
      <Key pos={[2, 7, 5]} k={1.8} rim={[-2, 2, -3]} rimK={25} />
      <Floor T={G} />
      <Dust T={G} />
      <group position={[0, 1.25, 0]} rotation={[0, 0, Math.PI * (1 - flip)]}>
        <Hourglass T={G} fill={0.05 + 0.15 * prog(t, 0.7, d)} pos={[0, -1.25, 0]} flow={flip > 0.98} />
      </group>
    </>
  );
};

const s14c: SceneFn = ({t, d, G}) => {
  const z = -t * 0.9;
  return (
    <>
      <Cam pos={[0.7, 1.7, z + 3.4]} target={[0, 1.1, z - 6]} fov={50} />
      <Key pos={[0, 6, -10]} k={1.4} />
      <mesh position={[0, 2, -26]}>
        <circleGeometry args={[6, 64]} />
        <Neon k={2.4} color="#FFE2A8" />
      </mesh>
      <Floor T={G} flow={0} />
      <Dust T={G} center={[0, 2, z - 4]} />
      <Path from={[0, 0, 2]} to={[0, 0, -20]} n={18} lit={18} />
      <Flow T={G} pts={[[0, 0.15, 2], [0, 0.2, -9], [0, 0.4, -20]]} speed={0.4} n={240} />
      <Figure pos={[0, 0, z]} turn={Math.PI} walk={t * 1.6} />
    </>
  );
};

// ---------------------------------------------------------------- 15 参考资料

const s15a: SceneFn = ({t, G}) => (
  <>
    <Cam pos={view([0, 0.6, 0], 6, t * 0.2, 0.35)} target={[0, 0.6, 0]} fov={50} />
    <Key k={1} />
    <Floor T={G} />
    <Dust T={G} />
    <Book open={1} pos={[0, 0.2, 0]} light={0.4} />
  </>
);
const s15b: SceneFn = ({t, G}) => (
  <>
    <Cam pos={view([0, 1.4, 0], 6.8, 1.6 + t * 0.2, 0.2)} target={[0, 1.4, 0]} fov={50} />
    <Key k={1} />
    <Floor T={G} />
    <Dust T={G} />
    <Tower n={10} T={G} wire={0.4} sway={0.1} />
  </>
);
const s15c: SceneFn = ({t, G}) => (
  <>
    <Cam pos={[0.5, 2.0, 4 - t * 0.4]} target={[0, 1.4, -8]} fov={50} />
    <Key k={1} />
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

