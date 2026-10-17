/** 3D 舞台公共层：机位、背景、雾、地面金色网格、漂浮金尘、环境反射与后期（泛光、色散、暗角、色调映射）。 */
import React, {createContext, useContext, useLayoutEffect, useMemo, useRef} from 'react';
import * as THREE from 'three';
import {useThree} from '@react-three/fiber';
import {Environment, Lightformer} from '@react-three/drei';
import {Bloom, ChromaticAberration, EffectComposer, ToneMapping, Vignette} from '@react-three/postprocessing';
import {ToneMappingMode} from 'postprocessing';
import {V3, lerp, mix3, rng} from './anim';

export const BG = '#090A0C';
export const GOLD = '#D6B879';
export const IVORY = '#F5F0E8';

/** 全局特效状态：T 为全片秒，hit 为最近一次撞击的脉冲（0–1），frame 为全片帧号，shiftY 为竖屏主体下移比例。 */
export type FX = {T: number; frame: number; hit: number; shiftY: number};
const Ctx = createContext<FX>({T: 0, frame: 0, hit: 0, shiftY: 0});
export const FXProvider = Ctx.Provider;
export const useFX = () => useContext(Ctx);

/** 发光色：toneMapped=false 的材质用，k>1 时进入泛光。 */
export const glow = (hex: string, k: number) => new THREE.Color(hex).multiplyScalar(k);

/**
 * 机位：每帧在 useLayoutEffect 里设置（早于 ThreeCanvas 的逐帧 advance），撞击时叠加确定性震屏。
 * 竖屏时用 setViewOffset 把画面主体整体下移，给上方字幕留出位置。
 */
export const Cam: React.FC<{pos: V3; target: V3; fov?: number; roll?: number; shake?: number}> = ({
  pos, target, fov = 40, roll = 0, shake = 1,
}) => {
  const {camera, size} = useThree();
  const fx = useFX();
  useLayoutEffect(() => {
    const c = camera as THREE.PerspectiveCamera;
    const a = fx.hit * 0.06 * shake;
    const sx = Math.sin(fx.frame * 12.9898) * a;
    const sy = Math.cos(fx.frame * 78.233) * a;
    c.position.set(pos[0] + sx, pos[1] + sy, pos[2]);
    c.up.set(Math.sin(roll), Math.cos(roll), 0);
    c.fov = fov;
    c.near = 0.05;
    c.far = 200;
    c.lookAt(target[0] + sx * 0.5, target[1] + sy * 0.5, target[2]);
    c.setViewOffset(size.width, size.height, 0, -fx.shiftY * size.height, size.width, size.height);
    c.updateProjectionMatrix();
  });
  return null;
};

/** 球坐标机位：从 target 出发，水平角 yaw（0 为 +z 方向）、俯仰角 pitch（正值在上方）、距离 dist。 */
export const view = (target: V3, dist: number, yaw: number, pitch: number): V3 => [
  target[0] + dist * Math.sin(yaw) * Math.cos(pitch),
  target[1] + dist * Math.sin(pitch),
  target[2] + dist * Math.cos(yaw) * Math.cos(pitch),
];

/** 机位插值：t∈[0,d] 从 a 平滑移到 b。 */
export const move = (t: number, d: number, a: V3, b: V3, ease: (x: number) => number = (x) => x * (2 - x)): V3 =>
  mix3(a, b, ease(Math.min(1, Math.max(0, t / d))));

/** 圆形柔光点贴图（金尘、火花共用）。 */
let sprite: THREE.Texture | null = null;
export const dotTexture = () => {
  if (sprite) return sprite;
  const cv = document.createElement('canvas');
  cv.width = cv.height = 64;
  const g = cv.getContext('2d')!;
  const gr = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  gr.addColorStop(0, 'rgba(255,255,255,1)');
  gr.addColorStop(0.35, 'rgba(255,240,210,0.6)');
  gr.addColorStop(1, 'rgba(255,230,180,0)');
  g.fillStyle = gr;
  g.fillRect(0, 0, 64, 64);
  sprite = new THREE.CanvasTexture(cv);
  return sprite;
};

/** 点粒子：positions 由调用方按时间算好（每帧重写缓冲区）。 */
export const Points: React.FC<{data: Float32Array; size?: number; color?: string; k?: number; opacity?: number}> = ({
  data, size = 0.08, color = GOLD, k = 2.2, opacity = 1,
}) => {
  const geo = useMemo(() => new THREE.BufferGeometry(), []);
  const ref = useRef<THREE.Points>(null);
  useLayoutEffect(() => {
    const cur = geo.getAttribute('position') as THREE.BufferAttribute | undefined;
    if (!cur || cur.array.length !== data.length) {
      geo.setAttribute('position', new THREE.BufferAttribute(data.slice(), 3));
    } else {
      (cur.array as Float32Array).set(data);
      cur.needsUpdate = true;
    }
    geo.computeBoundingSphere();
  });
  return (
    <points ref={ref} geometry={geo} frustumCulled={false}>
      <pointsMaterial map={dotTexture()} size={size} color={glow(color, k)} transparent opacity={opacity}
        depthWrite={false} blending={THREE.AdditiveBlending} toneMapped={false} sizeAttenuation />
    </points>
  );
};

/** 漂浮金尘：缓慢上升并横向流动，营造空气感。 */
export const Dust: React.FC<{T: number; n?: number; center?: V3; spread?: V3; speed?: number}> = ({
  T, n = 260, center = [0, 2.5, 0], spread = [14, 7, 16], speed = 0.18,
}) => {
  const base = useMemo(() => {
    const r = rng(17);
    return Array.from({length: n}, () => [r(), r(), r(), r()]);
  }, [n]);
  const data = new Float32Array(n * 3);
  base.forEach(([a, b, c, ph], i) => {
    const y = ((b + T * speed * (0.5 + ph)) % 1) - 0.5;
    data[i * 3] = center[0] + (a - 0.5) * spread[0] + Math.sin(T * 0.6 + ph * 9) * 0.25;
    data[i * 3 + 1] = center[1] + y * spread[1];
    data[i * 3 + 2] = center[2] + (c - 0.5) * spread[2] + Math.cos(T * 0.4 + ph * 7) * 0.25;
  });
  return <Points data={data} size={0.07} k={1.6} opacity={0.75} />;
};

/** 火花迸射：at 时刻从 origin 向四周飞散，受重力下落并衰减。 */
export const Sparks: React.FC<{t: number; at: number; origin: V3; n?: number; power?: number; seed?: number}> = ({
  t, at, origin, n = 90, power = 3.2, seed = 3,
}) => {
  const vel = useMemo(() => {
    const r = rng(seed);
    return Array.from({length: n}, () => {
      const th = r() * Math.PI * 2;
      const up = 0.2 + r() * 0.9;
      const sp = power * (0.35 + r());
      return [Math.cos(th) * sp, up * sp, Math.sin(th) * sp];
    });
  }, [n, power, seed]);
  const age = t - at;
  if (age < -1e-6 || age > 1.2) return null;
  const data = new Float32Array(n * 3);
  vel.forEach(([vx, vy, vz], i) => {
    data[i * 3] = origin[0] + vx * age;
    data[i * 3 + 1] = origin[1] + vy * age - 4.9 * age * age;
    data[i * 3 + 2] = origin[2] + vz * age;
  });
  return <Points data={data} size={0.11} k={3.5} opacity={Math.max(0, 1 - age / 1.2)} />;
};

/** 地面：深色微反光地板 + 缓慢流动的金色网格。 */
export const Floor: React.FC<{T: number; y?: number; flow?: number; grid?: number}> = ({T, y = 0, flow = 0.5, grid = 0.22}) => {
  const off = (T * flow) % 1;
  return (
    <group position={[0, y, 0]}>
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[120, 120]} />
        <meshStandardMaterial color="#0C0D10" roughness={0.45} metalness={0.6} />
      </mesh>
      {grid > 0 && (
        <gridHelper args={[60, 60, GOLD, GOLD]} position={[0, 0.003, off]}
          onUpdate={(g: THREE.GridHelper) => {
            const m = g.material as THREE.LineBasicMaterial;
            m.transparent = true;
            m.opacity = grid;
            m.depthWrite = false;
          }} />
      )}
    </group>
  );
};

/** 扫光：一道发光光带在背景上横扫（周期 period 秒）。 */
export const Sweep: React.FC<{T: number; z?: number; y?: number; width?: number; period?: number; k?: number; tilt?: number}> = ({
  T, z = -8, y = 3, width = 30, period = 3.2, k = 2.2, tilt = 0.5,
}) => {
  const x = lerp(-width / 2, width / 2, (T % period) / period);
  return (
    <mesh position={[x, y, z]} rotation={[0, 0, tilt]}>
      <planeGeometry args={[0.18, 30]} />
      <meshBasicMaterial color={glow('#FFE2A8', k)} transparent opacity={0.55} toneMapped={false}
        blending={THREE.AdditiveBlending} depthWrite={false} />
    </mesh>
  );
};

/** 公共环境与后期。所有场景都包在里面。 */
export const World: React.FC<{children: React.ReactNode; fog?: [number, number]; bloom?: number}> = ({
  children, fog = [8, 32], bloom = 0.95,
}) => {
  const fx = useFX();
  const ca = useRef<any>(null);
  useLayoutEffect(() => {
    if (ca.current) ca.current.offset.set(0.004 * fx.hit, 0.0025 * fx.hit);
  });
  return (
    <>
      <color attach="background" args={[BG]} />
      <fog attach="fog" args={[BG, fog[0], fog[1]]} />
      <ambientLight intensity={0.16} />
      <hemisphereLight args={['#FFE7B0', '#07080A', 0.3]} />
      <Environment resolution={128} frames={1}>
        <Lightformer form="rect" intensity={1.6} color="#FFE7B0" position={[0, 6, -6]} scale={[12, 2, 1]} />
        <Lightformer form="rect" intensity={1.5} color="#D6B879" position={[-7, 2, 2]} rotation-y={Math.PI / 2} scale={[8, 3, 1]} />
        <Lightformer form="ring" intensity={2} color="#FFF4DD" position={[6, 4, 4]} scale={3} />
      </Environment>
      {children}
      <EffectComposer multisampling={4} enableNormalPass={false}>
        <Bloom intensity={bloom} luminanceThreshold={0.8} luminanceSmoothing={0.25} mipmapBlur />
        <ChromaticAberration ref={ca} offset={new THREE.Vector2(0, 0)} radialModulation={false} modulationOffset={0} />
        <ToneMapping mode={ToneMappingMode.ACES_FILMIC} />
        <Vignette darkness={0.72} offset={0.28} />
      </EffectComposer>
    </>
  );
};
