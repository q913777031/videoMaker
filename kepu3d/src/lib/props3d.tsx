/** 可复用的 3D 道具：全部由参数（进度、亮度、时间）驱动，不读帧号、不用 useFrame。 */
import React, {useLayoutEffect, useMemo} from 'react';
import * as THREE from 'three';
import {GOLD, IVORY, Points, glow} from './World';
import {V3, clamp, lerp, rng, wobble} from './anim';

const DARK = '#17181C';

export const Gold: React.FC<{lit?: number; rough?: number}> = ({lit = 0, rough = 0.28}) => (
  <meshStandardMaterial color={GOLD} metalness={0.9} roughness={rough} emissive={GOLD} emissiveIntensity={0.05 + lit * 2.4} />
);
export const Ivory: React.FC<{lit?: number}> = ({lit = 0}) => (
  <meshStandardMaterial color="#CBBFA8" metalness={0.1} roughness={0.62} emissive={GOLD} emissiveIntensity={lit * 1.6} />
);
export const Dark: React.FC<{lit?: number}> = ({lit = 0}) => (
  <meshStandardMaterial color={DARK} metalness={0.35} roughness={0.6} emissive={GOLD} emissiveIntensity={lit * 0.8} />
);
export const Glass: React.FC<{opacity?: number; tint?: string}> = ({opacity = 0.18, tint = '#CFE3F2'}) => (
  <meshStandardMaterial color={tint} metalness={0.1} roughness={0.05} transparent opacity={opacity} depthWrite={false}
    side={THREE.DoubleSide} />
);
export const Neon: React.FC<{k?: number; color?: string; opacity?: number}> = ({k = 3, color = GOLD, opacity = 1}) => (
  <meshBasicMaterial color={glow(color, k)} toneMapped={false} transparent={opacity < 1} opacity={opacity} />
);

/** 卡片（投入卡）。 */
export const Card: React.FC<{pos?: V3; rot?: V3; gold?: boolean; lit?: number; s?: number}> = ({
  pos = [0, 0, 0], rot = [0, 0, 0], gold = false, lit = 0, s = 1,
}) => (
  <group position={pos} rotation={rot} scale={s}>
    <mesh>
      <boxGeometry args={[1.0, 0.04, 0.64]} />
      {gold ? <Gold lit={lit} /> : <Ivory lit={lit} />}
    </mesh>
    <mesh position={[0, 0.022, 0]}>
      <boxGeometry args={[0.86, 0.004, 0.5]} />
      <Neon k={0.6 + lit * 3} opacity={gold ? 0.9 : 0.5} />
    </mesh>
  </group>
);

/** 投入堆高塔：n 层厚板交错叠放；sway 摇晃幅度，lit(i) 每层亮度，wire 为线框（“归零”）。 */
export const Tower: React.FC<{
  n: number; T: number; pos?: V3; sway?: number; lit?: (i: number) => number; wire?: number; scale?: number; extra?: number;
}> = ({n, T, pos = [0, 0, 0], sway = 0.4, lit = () => 0, wire = 0, scale = 1, extra = 0}) => {
  const h = 0.26;
  const slabs = [];
  const count = Math.floor(n);
  for (let i = 0; i < count + (extra > 0 ? 1 : 0); i++) {
    const top = i === count;
    const yaw = (i % 2 ? 0.08 : -0.06) + Math.sin(i * 2.3) * 0.05;
    const lean = sway * 0.012 * i * Math.sin(T * 2.1 + i * 0.15);
    const y = top ? count * h + h / 2 + extra : i * h + h / 2;
    const l = clamp(lit(i));
    const kind = i % 3 === 2;
    slabs.push(
      <mesh key={i} position={[lean, y, Math.sin(i * 1.7) * 0.05]} rotation={[0, yaw, lean * 0.15]}>
        <boxGeometry args={[1.5 - (i % 4) * 0.05, h * 0.92, 0.95]} />
        {wire > 0 ? (
          <meshBasicMaterial color={glow(GOLD, 2.2)} wireframe toneMapped={false} transparent opacity={wire} />
        ) : kind ? <Gold lit={l} /> : <Ivory lit={l} />}
      </mesh>,
    );
  }
  return <group position={pos} scale={scale}>{slabs}</group>;
};
export const towerTop = (n: number, scale = 1) => Math.floor(n) * 0.26 * scale;

/** 原创中性人物：深色胶囊身体、无面部球形头、领口一道金环。arm 为右臂抬起角度，turn 为朝向。 */
export const Figure: React.FC<{pos?: V3; turn?: number; arm?: number; armL?: number; s?: number; lean?: number; walk?: number}> = ({
  pos = [0, 0, 0], turn = 0, arm = 0, armL = 0, s = 1, lean = 0, walk = 0,
}) => {
  const step = Math.sin(walk * Math.PI * 2) * 0.35;
  return (
    <group position={pos} rotation={[0, turn, 0]} scale={s}>
      <group rotation={[lean, 0, 0]}>
        <mesh position={[0, 0.92, 0]}>
          <capsuleGeometry args={[0.24, 0.5, 6, 16]} />
          <meshStandardMaterial color="#1E2026" roughness={0.55} metalness={0.2} />
        </mesh>
        <mesh position={[0, 1.5, 0]}>
          <sphereGeometry args={[0.19, 24, 18]} />
          <meshStandardMaterial color="#2A2C33" roughness={0.4} metalness={0.25} />
        </mesh>
        <mesh position={[0, 1.27, 0]} rotation={[Math.PI / 2, 0, 0]}>
          <torusGeometry args={[0.13, 0.025, 8, 32]} />
          <Neon k={3} />
        </mesh>
        <group position={[0.3, 1.18, 0]} rotation={[-arm, 0, 0.15]}>
          <mesh position={[0, -0.28, 0]}>
            <capsuleGeometry args={[0.07, 0.42, 4, 8]} />
            <meshStandardMaterial color="#1E2026" roughness={0.55} />
          </mesh>
        </group>
        <group position={[-0.3, 1.18, 0]} rotation={[-armL, 0, -0.15]}>
          <mesh position={[0, -0.28, 0]}>
            <capsuleGeometry args={[0.07, 0.42, 4, 8]} />
            <meshStandardMaterial color="#1E2026" roughness={0.55} />
          </mesh>
        </group>
      </group>
      {[-1, 1].map((sgn) => (
        <group key={sgn} position={[0.11 * sgn, 0.55, 0]} rotation={[step * sgn, 0, 0]}>
          <mesh position={[0, -0.28, 0]}>
            <capsuleGeometry args={[0.085, 0.4, 4, 8]} />
            <meshStandardMaterial color="#15161A" roughness={0.6} />
          </mesh>
        </group>
      ))}
    </group>
  );
};

/** 死胡同的墙：深色厚墙，裂缝透出闪烁的金光。 */
export const Wall: React.FC<{pos?: V3; crack?: number; w?: number; h?: number}> = ({pos = [0, 0, 0], crack = 1, w = 7, h = 5}) => {
  const edges = useMemo(() => new THREE.EdgesGeometry(new THREE.BoxGeometry(w, h, 0.5)), [w, h]);
  const pts: V3[] = [[0, 0.2, 0], [0.25, 0.9, 0], [-0.15, 1.6, 0], [0.3, 2.4, 0], [0.05, 3.1, 0], [0.35, 3.9, 0]];
  return (
    <group position={pos}>
      <mesh position={[0, h / 2, 0]}>
        <boxGeometry args={[w, h, 0.5]} />
        <meshStandardMaterial color="#2A2B31" roughness={0.7} metalness={0.25} />
      </mesh>
      <lineSegments position={[0, h / 2, 0]} geometry={edges}>
        <lineBasicMaterial color={glow(GOLD, 1.2)} toneMapped={false} />
      </lineSegments>
      {pts.slice(1).map((p, i) => {
        const a = pts[i];
        const dx = p[0] - a[0];
        const dy = p[1] - a[1];
        return (
          <mesh key={i} position={[(a[0] + p[0]) / 2, (a[1] + p[1]) / 2, 0.26]} rotation={[0, 0, Math.atan2(dy, dx) - Math.PI / 2]}>
            <boxGeometry args={[0.025, Math.hypot(dx, dy) + 0.02, 0.02]} />
            <Neon k={0.5 + 1.6 * crack} color="#FFE2A8" />
          </mesh>
        );
      })}
    </group>
  );
};

/** 地上的进度路径：n 块地砖从 z0 铺向 z1，前 lit 块亮起。 */
export const Path: React.FC<{n?: number; from?: V3; to?: V3; lit?: number; w?: number}> = ({
  n = 12, from = [0, 0, 0], to = [0, 0, -10], lit = 0, w = 1.1,
}) => (
  <group>
    {Array.from({length: n}, (_, i) => {
      const u = (i + 0.5) / n;
      const p: V3 = [lerp(from[0], to[0], u), 0.02, lerp(from[2], to[2], u)];
      const l = clamp(lit - i);
      const len = Math.hypot(to[0] - from[0], to[2] - from[2]) / n;
      return (
        <mesh key={i} position={p} rotation={[0, Math.atan2(to[0] - from[0], to[2] - from[2]), 0]}>
          <boxGeometry args={[w, 0.04, len * 0.82]} />
          {l > 0 ? <Neon k={0.8 + 2.4 * l} /> : <Dark />}
        </mesh>
      );
    })}
  </group>
);

/** 沙漏：上半沙量 1-fill，下半沙堆 fill，中间流沙粒子。flip=true 时上下颠倒（重新开始）。 */
export const Hourglass: React.FC<{T: number; fill: number; pos?: V3; s?: number; rot?: number; flow?: boolean}> = ({
  T, fill, pos = [0, 0, 0], s = 1, rot = 0, flow = true,
}) => {
  const n = 70;
  const base = useMemo(() => {
    const r = rng(5);
    return Array.from({length: n}, () => [r(), r()]);
  }, []);
  const data = new Float32Array(n * 3);
  base.forEach(([a, b], i) => {
    const u = (a + T * 1.4) % 1;
    data[i * 3] = (b - 0.5) * 0.04;
    data[i * 3 + 1] = 1.25 - u * 1.05;
    data[i * 3 + 2] = (a - 0.5) * 0.04;
  });
  const f = clamp(fill);
  return (
    <group position={pos} scale={s} rotation={[0, 0, rot]}>
      {[0, 2.5].map((y) => (
        <mesh key={y} position={[0, y, 0]}>
          <cylinderGeometry args={[0.85, 0.85, 0.12, 40]} />
          <Gold />
        </mesh>
      ))}
      {[-1, 1].map((sx) => [-1, 1].map((sz) => (
        <mesh key={`${sx}${sz}`} position={[0.7 * sx, 1.25, 0.7 * sz]}>
          <cylinderGeometry args={[0.035, 0.035, 2.5, 8]} />
          <Gold />
        </mesh>
      )))}
      <mesh position={[0, 1.875, 0]}>
        <coneGeometry args={[0.62, 1.15, 40, 1, true]} />
        <Glass />
      </mesh>
      <mesh position={[0, 0.625, 0]} rotation={[Math.PI, 0, 0]}>
        <coneGeometry args={[0.62, 1.15, 40, 1, true]} />
        <Glass />
      </mesh>
      {1 - f > 0.02 && (
        <mesh position={[0, 1.3 + 0.5 * (1 - f) * 0.9, 0]} rotation={[Math.PI, 0, 0]} scale={[1 - f * 0.85, 1 - f * 0.9, 1 - f * 0.85]}>
          <coneGeometry args={[0.5, 0.95, 32]} />
          <meshStandardMaterial color="#E8C987" emissive={GOLD} emissiveIntensity={0.5} roughness={0.8} />
        </mesh>
      )}
      <mesh position={[0, 0.06 + 0.4 * f, 0]} scale={[0.4 + 0.6 * f, Math.max(0.05, f), 0.4 + 0.6 * f]}>
        <coneGeometry args={[0.55, 0.8, 32]} />
        <meshStandardMaterial color="#E8C987" emissive={GOLD} emissiveIntensity={0.5} roughness={0.8} />
      </mesh>
      {flow && <Points data={data} size={0.05} k={3} />}
    </group>
  );
};

/** 台历：底座 + 纸叠，最上面的纸页按 rate 张/秒向后翻。 */
export const Calendar: React.FC<{T: number; rate?: number; pos?: V3; s?: number; lit?: number}> = ({
  T, rate = 3, pos = [0, 0, 0], s = 1, lit = 0,
}) => {
  const ph = (T * rate) % 1;
  const pages = [ph, (ph + 0.5) % 1];
  return (
    <group position={pos} scale={s}>
      <mesh position={[0, 0.15, 0]}>
        <boxGeometry args={[2.2, 0.3, 1.6]} />
        <Dark />
      </mesh>
      <mesh position={[0, 0.5, -0.05]}>
        <boxGeometry args={[2.0, 0.4, 1.4]} />
        <Ivory lit={lit} />
      </mesh>
      <mesh position={[0, 0.72, -0.75]} rotation={[0, 0, Math.PI / 2]}>
        <cylinderGeometry args={[0.05, 0.05, 2.1, 12]} />
        <Gold lit={0.3} />
      </mesh>
      {pages.map((p, i) => (
        <group key={i} position={[0, 0.72, -0.75]} rotation={[-Math.PI * p * 1.05, 0, 0]}>
          <mesh position={[0, 0, 0.7]}>
            <boxGeometry args={[1.98, 0.01, 1.38]} />
            <meshStandardMaterial color={IVORY} roughness={0.6} side={THREE.DoubleSide} transparent opacity={1 - p * 0.6} />
          </mesh>
        </group>
      ))}
      <mesh position={[0, 0.721, 0.0]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[0.25, 0.32, 40]} />
        <Neon k={1.5 + lit * 3} />
      </mesh>
    </group>
  );
};

/** 金币。 */
export const Coin: React.FC<{pos: V3; rot?: V3; s?: number}> = ({pos, rot = [0, 0, 0], s = 1}) => (
  <mesh position={pos} rotation={rot} scale={s}>
    <cylinderGeometry args={[0.2, 0.2, 0.05, 28]} />
    <Gold lit={0.15} />
  </mesh>
);

/** 书：open 0 合上、1 摊开；光从书页间溢出。 */
export const Book: React.FC<{open: number; pos?: V3; s?: number; light?: number}> = ({open, pos = [0, 0, 0], s = 1, light = 0}) => {
  const a = clamp(open) * (Math.PI / 2 - 0.08);
  return (
    <group position={pos} scale={s}>
      <group rotation={[0, 0, a]}>
        <mesh position={[-0.75, 0.04, 0]}>
          <boxGeometry args={[1.5, 0.06, 2]} />
          <Gold lit={0.1} />
        </mesh>
        <mesh position={[-0.72, 0.12, 0]}>
          <boxGeometry args={[1.42, 0.12, 1.9]} />
          <Ivory lit={light * 0.15} />
        </mesh>
      </group>
      <group rotation={[0, 0, -a]}>
        <mesh position={[0.75, 0.04, 0]}>
          <boxGeometry args={[1.5, 0.06, 2]} />
          <Gold lit={0.1} />
        </mesh>
        <mesh position={[0.72, 0.12, 0]}>
          <boxGeometry args={[1.42, 0.12, 1.9]} />
          <Ivory lit={light * 0.15} />
        </mesh>
      </group>
      {light > 0 && (
        <mesh position={[0, 1.6, 0]}>
          <cylinderGeometry args={[1.6, 0.3, 3.2, 32, 1, true]} />
          <meshBasicMaterial color={glow('#FFE2A8', 1.5)} transparent opacity={0.08 * light} toneMapped={false}
            blending={THREE.AdditiveBlending} depthWrite={false} side={THREE.DoubleSide} />
        </mesh>
      )}
    </group>
  );
};

/** 纸页（论文）。 */
export const Sheet: React.FC<{pos: V3; rot?: V3; lit?: number; s?: number}> = ({pos, rot = [0, 0, 0], lit = 0, s = 1}) => (
  <group position={pos} rotation={rot} scale={s}>
    <mesh>
      <boxGeometry args={[0.8, 0.01, 1.1]} />
      <Ivory lit={lit} />
    </mesh>
    {[0.3, 0.15, 0, -0.15, -0.3].map((z) => (
      <mesh key={z} position={[-0.05, 0.007, z]}>
        <boxGeometry args={[0.55, 0.002, 0.03]} />
        <meshStandardMaterial color="#9A8B6C" />
      </mesh>
    ))}
  </group>
);

/** 剧场座椅：rows × cols，按 litOrder 前 lit 个座位亮起。 */
export const Seats: React.FC<{rows?: number; cols?: number; lit: number; pos?: V3}> = ({rows = 6, cols = 11, lit, pos = [0, 0, 0]}) => {
  const order = useMemo(() => {
    const r = rng(11);
    return Array.from({length: rows * cols}, (_, i) => [i, r()] as const).sort((a, b) => a[1] - b[1]).map((x) => x[0]);
  }, [rows, cols]);
  const rank = useMemo(() => {
    const m = new Array(rows * cols).fill(0);
    order.forEach((idx, k) => (m[idx] = k));
    return m;
  }, [order, rows, cols]);
  return (
    <group position={pos}>
      {Array.from({length: rows * cols}, (_, i) => {
        const r = Math.floor(i / cols);
        const c = i % cols;
        const x = (c - (cols - 1) / 2) * 0.72;
        const z = r * 0.9;
        const y = r * 0.28;
        const on = clamp(lit - rank[i]);
        return (
          <group key={i} position={[x, y, z]}>
            <mesh position={[0, 0.25, 0]}>
              <boxGeometry args={[0.6, 0.12, 0.5]} />
              {on > 0 ? <Neon k={0.6 + 2.6 * on} /> : <Dark />}
            </mesh>
            <mesh position={[0, 0.55, 0.24]}>
              <boxGeometry args={[0.6, 0.55, 0.08]} />
              {on > 0 ? <Gold lit={on} /> : <Dark />}
            </mesh>
          </group>
        );
      })}
    </group>
  );
};

/** 玻璃罩：透明立方体 + 发光金边。 */
export const GlassBox: React.FC<{pos?: V3; size?: V3; edge?: number}> = ({pos = [0, 0, 0], size = [2, 2, 2], edge = 2.5}) => {
  const geo = useMemo(() => new THREE.EdgesGeometry(new THREE.BoxGeometry(...size)), [size[0], size[1], size[2]]);
  return (
    <group position={pos}>
      <mesh>
        <boxGeometry args={size} />
        <Glass opacity={0.12} tint="#FFF1D2" />
      </mesh>
      <lineSegments geometry={geo}>
        <lineBasicMaterial color={glow(GOLD, edge)} toneMapped={false} />
      </lineSegments>
    </group>
  );
};

/** 账单纸带：从出纸口沿地面波浪式流出，长度 len。 */
export const Receipt: React.FC<{T: number; len: number; pos?: V3}> = ({T, len, pos = [0, 0, 0]}) => {
  const seg = 0.25;
  const n = Math.max(0, Math.floor(len / seg));
  return (
    <group position={pos}>
      <mesh position={[0, 0.5, 0]}>
        <boxGeometry args={[1.4, 1, 0.8]} />
        <Gold lit={0.2} />
      </mesh>
      <mesh position={[0, 0.82, 0.41]}>
        <boxGeometry args={[1.0, 0.05, 0.02]} />
        <Neon k={3} />
      </mesh>
      {Array.from({length: n}, (_, i) => {
        const z = 0.45 + i * seg;
        const y = 0.8 - Math.min(0.78, i * 0.12) + Math.max(0, Math.sin(i * 0.7 - T * 5)) * 0.08 * Math.min(1, i / 4);
        return (
          <mesh key={i} position={[Math.sin(i * 0.35 - T * 2) * 0.12, y, z]} rotation={[i < 6 ? 0.6 : 0, 0, 0]}>
            <boxGeometry args={[0.9, 0.01, seg * 1.02]} />
            <meshStandardMaterial color={IVORY} roughness={0.7} emissive={GOLD} emissiveIntensity={i % 4 === 0 ? 0.6 : 0.05} />
          </mesh>
        );
      })}
    </group>
  );
};

/** 垃圾桶：开口圆桶 + 金边。 */
export const Bin: React.FC<{pos?: V3; s?: number}> = ({pos = [0, 0, 0], s = 1}) => (
  <group position={pos} scale={s}>
    <mesh position={[0, 0.6, 0]}>
      <cylinderGeometry args={[0.6, 0.48, 1.2, 32, 1, true]} />
      <meshStandardMaterial color="#202228" metalness={0.6} roughness={0.35} side={THREE.DoubleSide} />
    </mesh>
    <mesh position={[0, 1.2, 0]} rotation={[Math.PI / 2, 0, 0]}>
      <torusGeometry args={[0.6, 0.03, 8, 40]} />
      <Neon k={2} />
    </mesh>
  </group>
);

/** 玻璃管液位：level 为金色液面高度（0–1），real 为虚线真实刻度位置。 */
export const Tube: React.FC<{level: number; real: number; pos?: V3; h?: number}> = ({level, real, pos = [0, 0, 0], h = 3.2}) => (
  <group position={pos}>
    <mesh position={[0, h / 2, 0]}>
      <cylinderGeometry args={[0.45, 0.45, h, 40, 1, true]} />
      <Glass opacity={0.2} />
    </mesh>
    <mesh position={[0, (h * clamp(level)) / 2, 0]} scale={[1, Math.max(0.001, clamp(level)), 1]}>
      <cylinderGeometry args={[0.4, 0.4, h, 40]} />
      <meshStandardMaterial color={GOLD} emissive={GOLD} emissiveIntensity={0.45} transparent opacity={0.85} roughness={0.2} metalness={0.6} />
    </mesh>
    {Array.from({length: 14}, (_, i) => {
      const a = (i / 14) * Math.PI * 2;
      return (
        <mesh key={i} position={[Math.cos(a) * 0.52, h * real, Math.sin(a) * 0.52]} rotation={[0, -a, 0]}>
          <boxGeometry args={[0.04, 0.04, 0.12]} />
          <Neon k={2.5} color={IVORY} />
        </mesh>
      );
    })}
    <mesh position={[0, 0.05, 0]}>
      <cylinderGeometry args={[0.6, 0.6, 0.1, 40]} />
      <Gold />
    </mesh>
  </group>
);

/** 半圆仪表：value 0–1 指针位置。 */
export const Gauge: React.FC<{value: number; pos?: V3; s?: number}> = ({value, pos = [0, 0, 0], s = 1}) => {
  const a = Math.PI * (1 - clamp(value, -0.05, 1.08));
  return (
    <group position={pos} scale={s}>
      {Array.from({length: 18}, (_, i) => {
        const u = i / 17;
        const ang = Math.PI * (1 - u);
        const on = u <= value + 0.02;
        return (
          <mesh key={i} position={[Math.cos(ang) * 1.6, Math.sin(ang) * 1.6, 0]} rotation={[0, 0, ang - Math.PI / 2]}>
            <boxGeometry args={[0.16, 0.36, 0.08]} />
            {on ? <Neon k={0.8 + 2.4 * u} /> : <Dark />}
          </mesh>
        );
      })}
      <group rotation={[0, 0, a - Math.PI / 2]}>
        <mesh position={[0, 0.7, 0.08]}>
          <boxGeometry args={[0.07, 1.4, 0.05]} />
          <Neon k={3} color={IVORY} />
        </mesh>
      </group>
      <mesh position={[0, 0, 0.08]}>
        <cylinderGeometry args={[0.16, 0.16, 0.1, 24]} />
        <Gold />
      </mesh>
    </group>
  );
};

/** 天平：tilt 为横梁倾角（正值右低），左右托盘内容由 children 提供。 */
export const Balance: React.FC<{tilt: number; pos?: V3; left?: React.ReactNode; right?: React.ReactNode}> = ({
  tilt, pos = [0, 0, 0], left, right,
}) => {
  const L = 1.7;
  const dyL = Math.sin(tilt) * L;
  return (
    <group position={pos}>
      <mesh position={[0, 0.06, 0]}>
        <cylinderGeometry args={[0.7, 0.8, 0.12, 40]} />
        <Gold />
      </mesh>
      <mesh position={[0, 1.4, 0]}>
        <cylinderGeometry args={[0.06, 0.08, 2.7, 16]} />
        <Gold />
      </mesh>
      <mesh position={[0, 2.75, 0]} rotation={[0, 0, -tilt]}>
        <boxGeometry args={[L * 2 + 0.2, 0.08, 0.12]} />
        <Gold lit={0.2} />
      </mesh>
      {[-1, 1].map((sgn) => {
        const x = Math.cos(tilt) * L * sgn;
        const y = 2.75 - dyL * sgn;
        return (
          <group key={sgn} position={[x, y, 0]}>
            <mesh position={[0, -0.5, 0]}>
              <cylinderGeometry args={[0.01, 0.01, 1, 4]} />
              <Neon k={1.5} />
            </mesh>
            <mesh position={[0, -1, 0]}>
              <cylinderGeometry args={[0.65, 0.5, 0.08, 40]} />
              <Gold />
            </mesh>
            <group position={[0, -0.95, 0]}>{sgn < 0 ? left : right}</group>
          </group>
        );
      })}
    </group>
  );
};

/** 吊灯：灯罩 + 灯泡 + 体积光锥 + 点光源，power 0–1。 */
export const Lamp: React.FC<{power: number; pos?: V3}> = ({power, pos = [0, 4, 0]}) => (
  <group position={pos}>
    <mesh position={[0, 1.5, 0]}>
      <cylinderGeometry args={[0.01, 0.01, 3, 4]} />
      <meshStandardMaterial color="#333" />
    </mesh>
    <mesh>
      <coneGeometry args={[0.6, 0.5, 32, 1, true]} />
      <meshStandardMaterial color="#1E2026" metalness={0.7} roughness={0.3} side={THREE.DoubleSide} />
    </mesh>
    <mesh position={[0, -0.18, 0]}>
      <sphereGeometry args={[0.16, 20, 16]} />
      <Neon k={0.4 + 5 * power} color="#FFE7B0" />
    </mesh>
    <mesh position={[0, -2.2, 0]}>
      <cylinderGeometry args={[0.45, 2.4, 4, 40, 1, true]} />
      <meshBasicMaterial color={glow('#FFE2A8', 1.2)} transparent opacity={0.1 * power} toneMapped={false}
        blending={THREE.AdditiveBlending} depthWrite={false} side={THREE.DoubleSide} />
    </mesh>
    <pointLight position={[0, -0.4, 0]} intensity={40 * power} distance={12} decay={1.6} color="#FFE2B0" />
  </group>
);

/** 方桌。 */
export const Table: React.FC<{pos?: V3}> = ({pos = [0, 0, 0]}) => (
  <group position={pos}>
    <mesh position={[0, 0.85, 0]}>
      <boxGeometry args={[2.2, 0.08, 1.3]} />
      <meshStandardMaterial color="#2A2420" roughness={0.5} metalness={0.2} />
    </mesh>
    {[[-1, -1], [1, -1], [-1, 1], [1, 1]].map(([x, z]) => (
      <mesh key={`${x}${z}`} position={[x * 0.95, 0.42, z * 0.55]}>
        <boxGeometry args={[0.07, 0.84, 0.07]} />
        <meshStandardMaterial color="#1A1614" />
      </mesh>
    ))}
  </group>
);

/** 地面箭头。 */
export const Arrow: React.FC<{pos?: V3; rotY?: number; lit?: number; s?: number}> = ({pos = [0, 0, 0], rotY = 0, lit = 1, s = 1}) => (
  <group position={pos} rotation={[0, rotY, 0]} scale={s}>
    <mesh position={[0, 0.05, 0.4]}>
      <boxGeometry args={[0.35, 0.06, 1.3]} />
      <Neon k={0.5 + 3 * lit} />
    </mesh>
    <mesh position={[0, 0.05, -0.55]} rotation={[-Math.PI / 2, 0, 0]}>
      <coneGeometry args={[0.55, 0.8, 3]} />
      <Neon k={0.5 + 3 * lit} />
    </mesh>
  </group>
);

/** 白旗：旗面按时间飘动；sink 0–1 时整面旗下沉入地。 */
export const Flag: React.FC<{T: number; pos?: V3; sink?: number}> = ({T, pos = [0, 0, 0], sink = 0}) => {
  const geo = useMemo(() => new THREE.PlaneGeometry(1.4, 0.9, 20, 8), []);
  useLayoutEffect(() => {
    const p = geo.attributes.position as THREE.BufferAttribute;
    for (let i = 0; i < p.count; i++) {
      const x = (i % 21) / 20;
      p.setZ(i, Math.sin(x * 6 - T * 7) * 0.12 * x);
    }
    p.needsUpdate = true;
    geo.computeVertexNormals();
  });
  return (
    <group position={[pos[0], pos[1] - sink * 2.6, pos[2]]}>
      <mesh position={[0, 1.4, 0]}>
        <cylinderGeometry args={[0.03, 0.03, 2.8, 8]} />
        <Gold />
      </mesh>
      <mesh geometry={geo} position={[0.72, 2.3, 0]}>
        <meshStandardMaterial color="#F7F4EE" roughness={0.6} side={THREE.DoubleSide} emissive="#FFFFFF" emissiveIntensity={0.15} />
      </mesh>
    </group>
  );
};

/** 流动光带：粒子沿折线路径从起点流向终点（“流动”特效）。 */
export const Flow: React.FC<{T: number; pts: V3[]; n?: number; speed?: number; on?: number; size?: number}> = ({
  T, pts, n = 160, speed = 0.35, on = 1, size = 0.09,
}) => {
  const curve = useMemo(() => new THREE.CatmullRomCurve3(pts.map((p) => new THREE.Vector3(...p))), [JSON.stringify(pts)]);
  const base = useMemo(() => {
    const r = rng(23);
    return Array.from({length: n}, () => [r(), r(), r()]);
  }, [n]);
  const data = new Float32Array(n * 3);
  const v = new THREE.Vector3();
  base.forEach(([a, b, c], i) => {
    const u = (a + T * speed) % 1;
    curve.getPointAt(Math.min(u, clamp(on)), v);
    data[i * 3] = v.x + (b - 0.5) * 0.35;
    data[i * 3 + 1] = v.y + (c - 0.5) * 0.15 + 0.05;
    data[i * 3 + 2] = v.z + (c - 0.5) * 0.35;
  });
  return <Points data={data} size={size} k={3} />;
};

/** 气球（高估的预期）：金色光滑球体，size 为半径。 */
export const Balloon: React.FC<{size: number; pos?: V3; T: number}> = ({size, pos = [0, 0, 0], T}) => (
  <group position={[pos[0], pos[1] + Math.sin(T * 2) * 0.05, pos[2]]}>
    <mesh position={[0, size, 0]} scale={[1, 1.08, 1]}>
      <sphereGeometry args={[size, 48, 32]} />
      <meshStandardMaterial color={GOLD} metalness={0.85} roughness={0.15} emissive={GOLD} emissiveIntensity={0.25} />
    </mesh>
    <mesh position={[0, -0.6, 0]}>
      <cylinderGeometry args={[0.008, 0.008, 1.2, 4]} />
      <Neon k={1.5} color={IVORY} />
    </mesh>
  </group>
);

/** 立柱聚光：从上方打下的硬光（带体积光锥）。 */
export const SpotCone: React.FC<{pos: V3; h?: number; r?: number; k?: number}> = ({pos, h = 7, r = 1.8, k = 1}) => (
  <mesh position={[pos[0], pos[1] + h / 2, pos[2]]}>
    <cylinderGeometry args={[0.15, r, h, 40, 1, true]} />
    <meshBasicMaterial color={glow('#FFE2A8', 1.1)} transparent opacity={0.035 * k} toneMapped={false}
      blending={THREE.AdditiveBlending} depthWrite={false} side={THREE.DoubleSide} />
  </mesh>
);

export const shimmer = (T: number, seed: number) => 0.6 + 0.4 * wobble(T * 2, seed);
