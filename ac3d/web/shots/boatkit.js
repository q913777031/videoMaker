// 漏船镜头的公共布景（鱼缸剖面视角）：船长沿 -z、在 z=0 横切，正面露出船外热潮、船板与船内水的截面。
// 世界坐标：船心截面在 (x, 0, 0)；船外水位（世界 y）约 -1.6～0.6；船底 y=-2.5，船帮 y=0.7。
import { THREE, PAL, lights, makeCamera, at, inkMountainsTex, cloud3d, clamp01, lerp, toScreen, canvasTex } from '../engine.js';
import { mountainBackdrop, clayFigure } from '../props.js';
import { heatSea, cutBoat, cutJets, dragonWheel, coinPier } from '../world.js';

/** 一条完整的剖面漏船（船 + 射流 + 可选水车），放在世界坐标 x。 */
export function boatRig(scene, { x = 0, z = 0, B = 4.0, sail = null, wheel = true, roof = false, ac = true, seaW = 9 } = {}) {
  const root = new THREE.Group();
  root.position.set(x, 0, z);
  scene.add(root);
  const boat = cutBoat({ B, sail, roof, ac, seaW });
  root.add(boat);
  const jets = cutJets(boat);
  let wh = null;
  if (wheel) {
    wh = dragonWheel({ len: 5.0, angle: 0.8 });
    wh.position.set(-B / 2 + 0.55, boat.userData.bottom + 0.35, -1.6);
    boat.add(wh);
  }
  return {
    root, boat, jets, wheel: wh,
    /** outer/inner：船外、船内水位（世界 y）；pump：链条位移；flow：倾泻；soak：船板吸热；warm：船内水温；strength 覆盖射流强度 */
    set(t, { outer = 0.2, inner = -1.6, pump = 0, flow = 0, blur = 0, soak = 0, warm = null, strength = null } = {}) {
      boat.userData.set({ outer, inner, soak, warm });
      const diff = clamp01((outer - inner) / 2.0);
      jets.userData.update(t, strength === null ? diff : strength, outer, inner);
      if (wh) wh.userData.update(pump, flow, blur);
    },
    /** 船内 / 船外水位线在屏幕上的位置（用于标签） */
    levelAnchor(level, side = -1) {
      const o = new THREE.Object3D();
      return [side * (B / 2 + 2.2), level, 0];
    },
  };
}

export function boatScene({ sunX = 8, mountains = 6, fov = 34 } = {}) {
  const scene = new THREE.Scene();
  scene.fog = new THREE.Fog(PAL.paper, 40, 90);
  lights(scene, { key: [6, 12, 14], intensity: 2.5, shadow: 16, hemi: 1.05 });
  const sea = heatSea({ size: 160 });
  sea.position.z = -110;
  scene.add(sea);
  const mtn = mountainBackdrop(inkMountainsTex(mountains, { tint: '#4A4440' }), 150, 60);
  mtn.position.set(0, 14, -95);
  scene.add(mtn);
  const sun = new THREE.Mesh(new THREE.CircleGeometry(4.2, 48), new THREE.MeshBasicMaterial({ color: '#D9482B', fog: false }));
  sun.position.set(sunX, 26, -92);
  scene.add(sun);
  const clouds = [cloud3d(1.6), cloud3d(1.1)];
  at(clouds[0], -11, 9, -30);
  at(clouds[1], 10, 7.5, -24);
  clouds.forEach(c => scene.add(c));
  const camera = makeCamera(fov);
  return {
    scene, camera, sea, sun, clouds,
    tick(t, level = 0.2) {
      sea.userData.set(level, t);
      clouds[0].position.x = -11 + Math.sin(t * 0.15) * 1.5;
      clouds[1].position.x = 10 + Math.sin(t * 0.12 + 1) * 1.2;
    },
  };
}

/** 标准机位：正对剖面、略俯视。 */
export const FRONT = { pos: [1.2, 2.6, 24], look: [0.2, -1.0, -2.5], fov: 34 };

/** 跟随 3D 位置的小标签（DOM）。 */
export function tagLabel(ui, id, text, color = PAL.ink) {
  ui.add(id, text, { font: '700 30px NotoSansSC', color, background: 'rgba(248,242,231,0.92)', padding: '6px 16px',
    borderRadius: '22px', border: `3px solid ${color}`, whiteSpace: 'nowrap', opacity: 0 });
}
const _o = new THREE.Object3D();
export function followPt(ui, id, camera, p, o) {
  _o.position.set(...p);
  _o.updateMatrixWorld();
  const [x, y] = toScreen(_o, camera);
  ui.set(id, { o, x, y });
}
export function follow(ui, id, obj, camera, offset, o) {
  const [x, y] = toScreen(obj, camera, offset);
  ui.set(id, { o, x, y });
}

export function figureOnStone(scene, { x = -5.2, z = -1.5, ry = 0.5, color = PAL.azure, hat = 'bun', s = 0.8, top = 0.9 } = {}) {
  const stone = new THREE.Mesh(new THREE.CylinderGeometry(0.9, 1.15, 6, 9), new THREE.MeshStandardMaterial({ color: '#8E8A80', roughness: 0.9 }));
  stone.position.set(x, top - 3, z);
  stone.castShadow = stone.receiveShadow = true;
  scene.add(stone);
  const fig = clayFigure({ color, hat, s });
  fig.position.set(x, top, z);
  fig.rotation.y = ry;
  scene.add(fig);
  return { stone, fig };
}

export function pierAt(scene, x, z, { top = 0.9, max = 34, seed = 3, ghost = false } = {}) {
  const p = coinPier({ max, seed, ghost });
  p.position.set(x, top, z);
  p.children[0].scale.y = 4;                // 石柱直通水底
  p.children[0].position.y = -2.8;
  scene.add(p);
  return p;
}

export { coinPier, canvasTex, lerp, clamp01 };
