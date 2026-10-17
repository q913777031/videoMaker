// 镜 3 seep（drop）：板缝被冲开、热流喷进船舱（大鼓）；船外再涨（堂鼓）射流变粗；回落后射流变细；随温差脉动。
import { THREE, PAL, camKeys, cue, prog, easeOut, easeInOut, clamp01, lerp, pulse, shake, inkSplash, toScreen } from '../engine.js';
import { boatScene, boatRig, tagLabel, follow, followPt, FRONT } from './boatkit.js';

/** 朱色温差标尺：一根竖杆连接船内与船外水位，长度即温差。 */
export function diffBar() {
  const g = new THREE.Group();
  const bar = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.09, 1, 14), new THREE.MeshStandardMaterial({ color: PAL.cinnabar, emissive: PAL.cinnabar, emissiveIntensity: 0.3 }));
  const capA = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.07, 0.07), bar.material);
  const capB = capA.clone();
  g.add(bar, capA, capB);
  g.userData = {
    set(lo, hi) {
      const h = Math.max(0.02, hi - lo);
      bar.scale.y = h;
      bar.position.y = lo + h / 2;
      capA.position.y = lo;
      capB.position.y = hi;
    },
    mid: () => bar.position,
  };
  return g;
}

export function seep({ ui }) {
  const W = boatScene();
  const rig = boatRig(W.scene, { wheel: false, roof: false });
  const bar = diffBar();
  bar.position.set(-2.9, 0, 0.35);
  W.scene.add(bar);
  tagLabel(ui, 'diff', '温差', PAL.cinnabar);
  const tBurst = cue('seep.seams_burst'), tHigh = cue('seep.sea_higher'), tLow = cue('seep.sea_lower'), tPulse = cue('seep.jets_pulse');
  const inner = -1.6;
  return {
    scene: W.scene, camera: W.camera,
    update(lt, t) {
      const orbit = easeInOut(prog(t, tLow, 2.6)) * 0.42;
      const back = easeOut(prog(t, tBurst, 1.2));
      const R = lerp(15, 25, back), ang = -0.05 - orbit;
      camKeys(W.camera, 0, [{ t: 0, pos: [Math.sin(ang) * R, lerp(1.0, 3.2, back), Math.cos(ang) * R], look: [0.2, -1.1, -2.5], fov: 34 }]);
      shake(W.camera, t, tBurst, 0.35);
      shake(W.camera, t, tHigh, 0.12);
      let outer = 0.15;
      outer = lerp(outer, 0.6, easeOut(prog(t, tHigh - 0.15, 0.3)));
      outer = lerp(outer, -1.15, easeInOut(prog(t, tLow, 1.0)));
      W.tick(t, outer);
      let strength = clamp01((outer - inner) / 2.0) * easeOut(prog(t, tBurst - 0.03, 0.12));
      if (t > tPulse) strength *= 1 + 0.45 * Math.max(0, Math.sin((t - tPulse) * Math.PI * 1.9)) * (1 - clamp01((t - tPulse - 1.1) / 0.4));
      rig.set(t, { outer, inner, strength });
      bar.userData.set(inner, outer + 0.06 * Math.max(0, pulse(t, tHigh, 7, 18)));
      followPt(ui, 'diff', W.camera, [-3.9, (inner + outer) / 2, 0.35], clamp01((t - tBurst - 0.6) / 0.4));
    },
    fx(g, lt, t) {
      const [x, y] = toScreen(rig.root, W.camera, [0, -0.8, 0]);
      inkSplash(g, x, y, t - tBurst, 420, PAL.ink, 31, 0.9);
      inkSplash(g, x + 60, y - 30, t - tBurst - 0.04, 300, PAL.cinnabar, 33, 0.8);
    },
  };
}
