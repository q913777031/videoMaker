import { THREE, PAL, lights, makeCamera, camKeys, at, shadowFloor, inkMountainsTex, easeOut, prog, clamp01 } from '../engine.js';
import { clayFigure, chineseRoom, acIndoor, mountainBackdrop } from '../props.js';

export function room({ ui }) {
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(PAL.paper);
  lights(scene, { key: [5, 10, 9], intensity: 2.6, shadow: 10 });
  const r = chineseRoom({ w: 14, depth: 10 });
  scene.add(r);
  const ac = acIndoor();
  at(ac, 2.5, 5.8, -4.6);
  scene.add(ac);
  const a = clayFigure({ color: PAL.azure, hat: 'bun' });
  at(a, -1.5, 0, 0, 0.4, 1.2);
  const b = clayFigure({ color: PAL.cinnabar });
  at(b, 2.2, 0, 1, -0.5, 1.2);
  scene.add(a, b);
  ui.brushText('title', '开还是关', { top: '640px' });
  ui.sealStamp('seal', '省电', { top: '980px' });
  const camera = makeCamera(34);
  return {
    scene, camera,
    update(lt) {
      camKeys(camera, lt, [{ t: 0, pos: [0, 4.6, 24], look: [0, 3.4, 0] }]);
      a.userData.pose({ walk: lt * 2, amp: 1 });
      b.userData.pose({ armR: 1.6, nod: 0.15 });
      ui.brush('title', clamp01(lt / 2));
      ui.stamp('seal', lt - 3, { x: 0, y: 0 });
    },
  };
}
export function voidStage() {
  const scene = new THREE.Scene();
  return { scene, camera: makeCamera(35), update() {} };
}
