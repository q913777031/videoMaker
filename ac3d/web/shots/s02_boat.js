// 镜 2 boat：屋子落进橙色热潮成了漏船；热潮上涨；两根竹标弹出（木鱼）；第一颗热珠渗出；板缝一齐张开蓄力。
import { THREE, PAL, camKeys, cue, prog, easeOut, easeIn, easeInOut, clamp01, lerp, pulse, inkSplash, toScreen } from '../engine.js';
import { boatScene, boatRig, tagLabel, followPt, FRONT } from './boatkit.js';

export function boat({ ui }) {
  const W = boatScene();
  const rig = boatRig(W.scene, { wheel: false, roof: true });
  const drip = new THREE.Mesh(new THREE.SphereGeometry(0.17, 20, 12), new THREE.MeshStandardMaterial({ color: '#FF8A3D', emissive: '#C8501E', emissiveIntensity: 0.6 }));
  W.scene.add(drip);
  tagLabel(ui, 'out', '船外水位 = 室外温度', PAL.ochre);
  tagLabel(ui, 'in', '船内水位 = 室内温度', PAL.cinnabar);
  const t0 = cue('boat.house_to_boat'), tSea = cue('boat.sea_rise'), tPole = cue('boat.level_poles');
  const tDrip = cue('boat.first_drip'), tStrain = cue('boat.seam_strain');
  const key = W.scene.children.find(o => o.isDirectionalLight);
  const inner = -1.6;
  return {
    scene: W.scene, camera: W.camera,
    update(lt, t) {
      camKeys(W.camera, lt, [{ t: 0, pos: [-4, 9, 20], look: [0, -0.5, -3], fov: 36 }, { t: 2.4, pos: FRONT.pos, look: FRONT.look, fov: FRONT.fov },
        { t: 6.4, pos: [1.0, 2.2, 22], look: [0.2, -1.0, -2.5], fov: 34 }, { t: 8.5, pos: [-1.0, 0.6, 15], look: [-1.4, -1.3, -2.5], fov: 32 }]);
      // 屋子落进水面并晃两下；瓦顶抬起淡出
      const fall = easeIn(prog(t, t0 - 0.05, 0.55));
      const bob = pulse(t, t0 + 0.5, 3.5, 7) * 0.22;
      rig.root.position.y = lerp(6, 0, fall) + bob;
      rig.root.rotation.z = pulse(t, t0 + 0.5, 3, 6) * 0.04;
      if (rig.boat.userData.roof) rig.boat.userData.roof.position.y = rig.boat.userData.top + 3.0 + 6 * easeInOut(prog(t, t0 + 0.8, 1.6));
      // 热潮：第 4 拍从船底涨到船帮约三分之二
      const sea = lerp(-2.4, 0.15, easeInOut(prog(t, tSea, 1.6)));
      W.tick(t, sea);
      const strain = easeInOut(prog(t, tStrain - 0.1, 0.3));
      rig.set(t, { outer: sea, inner, strength: t > tStrain ? 0.12 * strain : 0 });
      rig.boat.scale.x = 1 - 0.03 * strain;
      // 第一颗热珠：挂在左舷一条板缝口颤动
      const s = rig.boat.userData.seams[2];
      const dk = easeOut(prog(t, tDrip, 0.4));
      drip.visible = t > tDrip;
      drip.position.set(s.x + 0.12, s.y - 0.12 + Math.sin(t * 16) * 0.02, -0.15);
      drip.scale.setScalar(Math.max(0.01, dk));
      key.intensity = lerp(2.5, 1.5, easeInOut(prog(t, tStrain - 0.6, 0.6)));
      // 第 8 拍两条水位线标签弹出
      const lo = easeOut(prog(t, tPole, 0.3)) * (1 - prog(lt, 7.8, 0.4));
      followPt(ui, 'out', W.camera, [-3.3, sea + 0.55, 0], lo);
      followPt(ui, 'in', W.camera, [0, inner + 0.5, 0], lo);
    },
    fx(g, lt, t) {
      const [x, y] = toScreen(rig.root, W.camera, [0, -1, 0]);
      inkSplash(g, x, y, t - t0 - 0.5, 260, PAL.ink, 21, 0.8);
    },
  };
}
