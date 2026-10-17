// 镜 1 hook：烈日下的国风房间，泥人撑伞握遥控器要出门；两派小泥人举旗争论，旗杆相撞（梆子）。
import { THREE, PAL, lights, makeCamera, camKeys, at, cue, P, prog, easeOut, easeInOut, clamp01, lerp, canvasTex, pulse, shake, inkSplash, toScreen } from '../engine.js';
import { chineseRoom, acIndoor, coldAir, remote, thermometer, clayFigure } from '../props.js';

export function flag(text, color, fg = '#F7EDE3') {
  const g = new THREE.Group();
  const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 3.4, 10), new THREE.MeshStandardMaterial({ color: PAL.wood, roughness: 0.6 }));
  pole.position.y = 1.7;
  pole.castShadow = true;
  g.add(pole);
  const tex = canvasTex(256, 512, (c) => {
    c.fillStyle = color; c.fillRect(0, 0, 256, 512);
    c.fillStyle = fg; c.font = '120px "MaShanZheng"'; c.textAlign = 'center'; c.textBaseline = 'middle';
    const ch = [...text];
    ch.forEach((x, i) => c.fillText(x, 128, 256 + (i - (ch.length - 1) / 2) * 128));
  });
  const cloth = new THREE.Mesh(new THREE.PlaneGeometry(0.9, 1.8, 8, 1), new THREE.MeshStandardMaterial({ map: tex, side: THREE.DoubleSide, roughness: 0.85 }));
  cloth.position.set(0.47, 2.45, 0);
  cloth.castShadow = true;
  g.add(cloth);
  g.userData = {
    cloth,
    wave(t, k = 1) {
      const pos = cloth.geometry.attributes.position;
      for (let i = 0; i < pos.count; i++) {
        const x = pos.getX(i);
        pos.setZ(i, Math.sin(t * 5 + x * 4) * 0.08 * (x + 0.45) * k);
      }
      pos.needsUpdate = true;
    },
  };
  return g;
}

export function umbrella(color = '#C9483A') {
  const g = new THREE.Group();
  const canopy = new THREE.Mesh(new THREE.ConeGeometry(1.15, 0.5, 16, 1, true), new THREE.MeshStandardMaterial({ color, roughness: 0.7, side: THREE.DoubleSide }));
  canopy.position.y = 1.5;
  canopy.castShadow = true;
  g.add(canopy);
  for (let i = 0; i < 16; i++) {
    const rib = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, 1.26, 4), new THREE.MeshStandardMaterial({ color: '#7A4A30' }));
    const a = i * Math.PI * 2 / 16;
    rib.position.set(Math.cos(a) * 0.57, 1.5, Math.sin(a) * 0.57);
    rib.rotation.set(Math.sin(a) * 1.15, 0, -Math.cos(a) * 1.15);
    g.add(rib);
  }
  const shaft = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 1.8, 8), new THREE.MeshStandardMaterial({ color: '#7A4A30' }));
  shaft.position.y = 0.85;
  g.add(shaft);
  return g;
}

export function hook({ ui }) {
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(PAL.paper);
  lights(scene, { key: [-6, 9, 9], intensity: 2.7, shadow: 10 });
  const room = chineseRoom({ w: 13, depth: 9 });
  scene.add(room);
  room.userData.win.position.set(-2.2, 4.6, -4.44);
  // 窗外红日：在月洞窗里缓缓上升
  const sun = new THREE.Mesh(new THREE.CircleGeometry(0.42, 40), new THREE.MeshBasicMaterial({ color: '#D9482B' }));
  sun.position.set(-1.5, 4.0, -4.43);
  scene.add(sun);
  const ac = acIndoor({ w: 2.6, h: 0.78, d: 0.6 });
  at(ac, 2.4, 6.4, -4.1);
  scene.add(ac);
  const air = coldAir({ n: 6, len: 2.6, spread: 2.0 });
  at(air, 2.4, 5.95, -3.75);
  scene.add(air);
  const th = thermometer({ h: 2.2 });
  at(th, 4.6, 1.2, -4.2, 0, 0.75);
  scene.add(th);
  const hero = clayFigure({ color: PAL.azure, hat: 'bun', s: 0.95 });
  at(hero, 0.9, 0, -0.6, -0.15);
  scene.add(hero);
  const umb = umbrella();
  umb.position.set(0, -0.2, 0);
  umb.rotation.z = 0.15;
  umb.scale.setScalar(0.75);
  hero.userData.armL.add(umb);
  umb.position.set(0, -0.9, 0.15);
  const rc = remote();
  rc.scale.setScalar(0.32);
  rc.position.set(0, -0.92, 0.12);
  rc.rotation.x = -0.4;
  hero.userData.armR.add(rc);
  const fly = remote();                      // 被旗杆弹飞的遥控器（与手里的那只互换）
  fly.scale.setScalar(0.34);
  fly.visible = false;
  scene.add(fly);
  const left = clayFigure({ color: PAL.cinnabar, s: 0.62 });
  const right = clayFigure({ color: PAL.ink2, hat: 'douli', s: 0.62 });
  const fL = flag('随手关', PAL.cinnabar);
  const fR = flag('别关', PAL.ink, '#F2E4C4');
  left.userData.armR.add(fL);
  right.userData.armL.add(fR);
  fL.position.set(0, -0.7, 0.1);
  fR.position.set(0, -0.7, 0.1);
  fR.userData.cloth.position.x = -0.47;
  scene.add(left, right);
  const camera = makeCamera(40);
  const tPop = cue('hook.debate_pop'), tClash = cue('hook.flags_clash'), tRemote = cue('hook.remote_tilt');
  return {
    scene, camera,
    update(lt, t) {
      camKeys(camera, lt, [{ t: 0, pos: [-1.2, 3.4, 23], look: [0.2, 1.6, 0] }, { t: 4.3, pos: [0.2, 3.0, 18.5], look: [0.4, 1.5, 0] },
        { t: 8.6, pos: [0.5, 2.9, 17.5], look: [0.5, 1.4, 0] }]);
      if (t > tClash) camera.position.x += Math.sin((t - tClash) * 9) * 0.12 * Math.exp(-(t - tClash) * 3);
      shake(camera, t, tClash, 0.1);
      sun.position.y = 4.0 + 0.5 * easeOut(prog(t, cue('hook.sun_glow'), 3));
      ac.userData.set(1, '26°', true);
      air.userData.set(1, t);
      th.userData.set(0.6 + 0.18 * easeOut(prog(t, cue('hook.sun_glow'), 1.5)));
      // 主角：撑伞站立，第 4 拍抬起遥控器
      const up = easeOut(prog(t, tRemote, 0.5));
      hero.userData.pose({ armL: 0.9, armR: lerp(0.2, 1.25, up), nod: -0.05 * up });
      rc.userData.button.material.emissive = new THREE.Color(PAL.cinnabar);
      rc.userData.button.material.emissiveIntensity = t > tRemote && t < tRemote + 0.35 ? 1.2 : 0;
      // 两派小泥人：第 8 拍沿弧线弹入
      for (const [fig, side, fl] of [[left, -1, fL], [right, 1, fR]]) {
        const k = prog(t, tPop - 0.5, 0.5);
        const x = lerp(side * 7.5, side * 1.75, easeOut(k));
        fig.position.set(x, Math.sin(Math.PI * k) * 1.4 + Math.max(0, pulse(t, tPop, 9, 20)) * 0.1, 2.6);
        fig.visible = t > tPop - 0.5;
        fig.rotation.y = -side * 0.5;
        const clash = easeInOut(prog(t, tClash - 0.35, 0.35));
        fig.userData.pose({ armR: side < 0 ? 0.5 : 0, armL: side > 0 ? 0.5 : 0, walk: k * 2, amp: k < 1 ? 1 : 0 });
        fl.rotation.x = 0.5;                       // 抵消抬臂，让旗杆竖直
        fl.rotation.z = side * lerp(0, 0.42, clash) - side * 0.1 * pulse(t, tClash, 6, 16);
        fl.userData.wave(t, 1);
      }
      // 遥控器在相撞拍被弹到空中转半圈悬住
      const fk = prog(t, tClash, 0.6);
      rc.visible = t < tClash;
      fly.visible = t >= tClash;
      if (fly.visible) {
        hero.updateWorldMatrix(true, true);
        fly.position.set(lerp(1.4, 0.4, fk), lerp(2.2, 4.0, easeOut(fk)) + Math.sin(t * 2) * 0.05, 1.2);
        fly.rotation.set(0.3, 0, Math.PI * easeOut(fk));
      }
    },
    fx(g, lt, t) {
      const [x, y] = toScreen(left, camera, [0, 3.1, 0]);
      inkSplash(g, 540, y - 40, t - tClash, 110, PAL.ink, 11, 0.7);
    },
  };
}
