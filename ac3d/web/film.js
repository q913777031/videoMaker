// 整片只有一个场景：同一间客厅、同一台相机，镜头之间靠连续运镜衔接（没有硬切）。
// 所有状态都是全片时间 t 的确定函数；需要“累积”的量（风扇转角、粒子流相位、平滑开关）在启动时按 1/60 秒网格预先积分。
import {
  THREE, W, H, TL, cue, clamp01, lerp, easeOut, easeIn, easeInOut, easeOutBack, prog, win, bump, makeCamera, shadowFloor,
} from './engine.js';
import { buildRoom, person, remote, keys, heatDots, MOD, ROOM } from './room.js';

// ---------------------------------------------------------------- DOM 标签层
const uiRoot = document.getElementById('ui');
function el(css, html = '') {
  const e = document.createElement('div');
  Object.assign(e.style, { position: 'absolute', left: '0', top: '0', opacity: '0', whiteSpace: 'nowrap', ...css });
  e.innerHTML = html;
  uiRoot.appendChild(e);
  return e;
}
function place(e, x, y, o, s = 1) {
  e.style.opacity = String(clamp01(o));
  e.style.display = o > 0.002 ? 'block' : 'none';
  e.style.transform = `translate(${x}px, ${y}px) translate(-50%, -50%) scale(${s})`;
}
function html(e, s) { if (e._h !== s) { e.innerHTML = s; e._h = s; } }
const pillCSS = (bg, fg = '#fff') => ({ font: '700 40px NotoSansSC', color: fg, background: bg, padding: '10px 28px',
  borderRadius: '40px', boxShadow: '0 6px 18px rgba(20,30,40,0.18)' });
const pop = (t, t0, d = 0.32) => (t < t0 ? 0 : easeOutBack(prog(t, t0, d), 2.2));

// ---------------------------------------------------------------- 预积分工具
const DT = 1 / 60;
function grid(fn, mode, k = 0.3) {
  const n = Math.ceil((TL.end + 2) / DT) + 2;
  const a = new Float32Array(n);
  let acc = 0;
  for (let i = 0; i < n; i++) {
    const v = fn(i * DT);
    if (mode === 'integ') { a[i] = acc; acc += v * DT; } else { acc = i === 0 ? v : acc + (v - acc) * (1 - Math.exp(-DT / k)); a[i] = acc; }
  }
  return t => { const x = clamp01(t / ((n - 1) * DT)) * (n - 1), i = Math.min(n - 2, Math.floor(x)); return lerp(a[i], a[i + 1], x - i); };
}

export function createFilm() {
  const S = Object.fromEntries(TL.shots.map(s => [s.name, s.t0]));
  const E = Object.fromEntries(TL.shots.map(s => [s.name, s.t1]));
  const c = n => cue(n);
  const OUT_T = 35;

  // ---------------------------------------------------------------- 状态（全片时间的函数）
  const presses = ['hook.remote_up', 'off.press', 'restart.press', 'toggle.t1', 'toggle.t2', 'toggle.t3', 'toggle.protect', 'fixed.off'].map(c);
  function acOn(t) {
    if (t < c('off.press')) return 1;
    if (t < c('restart.press')) return 0;
    if (t < c('toggle.t1')) return 1;
    if (t < c('toggle.t2')) return 0;
    if (t < c('toggle.t3')) return 1;
    if (t < c('toggle.protect')) return 0;
    if (t < c('fixed.off')) return 1;
    return 0;
  }
  const protecting = t => t >= c('toggle.t2') && t < S.fixed && acOn(t);
  function running(t) {                                  // 压缩机实际在转
    if (!acOn(t) || protecting(t)) return 0;
    if (t >= c('fixed.stop') && t < c('fixed.off')) return 0;
    return 1;
  }
  function boost(t) {                                    // 重开后的满负荷程度 0–1
    const r = c('restart.press');
    if (t < r) return 0;
    return clamp01(1 - (t - (c('restart.stored') + 1.2)) / 5);
  }
  function roomT(t) {
    const o = c('off.press'), r = c('restart.press');
    if (t < o) return 26;
    const peak = 26 + 6.8 * (1 - Math.exp(-(Math.min(t, r) - o) / 4));
    if (t < r) return peak;
    const fo = c('fixed.off');
    if (t < fo) return 26 + (peak - 26) * Math.exp(-(t - r) / 2.6);
    return 26 + 6.8 * (1 - Math.exp(-(t - fo) / 4));
  }
  const power = grid(t => (running(t) ? 0.45 + 0.55 * boost(t) : acOn(t) ? 0.05 : 0), 'smooth', 0.22);
  const fanAng = grid(t => (running(t) ? (1.1 + 1.6 * boost(t)) * Math.PI * 2 : 0), 'integ');
  const fanSpin = grid(t => running(t), 'smooth', 0.6);
  const pumpPhase = grid(t => 0.13 + 0.1 * boost(t), 'integ');
  const pumpDens = grid(t => running(t) * (0.55 + 0.45 * boost(t)), 'smooth', 0.5);
  const coldK = grid(t => running(t) ? 1 : 0, 'smooth', 0.45);
  const louverK = grid(t => acOn(t), 'smooth', 0.25);

  // ---------------------------------------------------------------- 场景
  const scene = new THREE.Scene();
  const camera = makeCamera(40);
  scene.add(new THREE.HemisphereLight('#FFFFFF', '#B7C0C8', 1.15));
  const key = new THREE.DirectionalLight('#FFF6EA', 2.1);
  key.position.set(5, 11, 9);
  key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  Object.assign(key.shadow.camera, { left: -7, right: 7, top: 7, bottom: -7, near: 1, far: 40 });
  key.shadow.bias = -0.0004;
  key.shadow.normalBias = 0.02;
  key.shadow.radius = 4;
  scene.add(key);
  const fill = new THREE.DirectionalLight('#DCE8F5', 0.6);
  fill.position.set(-8, 5, 6);
  scene.add(fill);
  const floor = shadowFloor(60, 0.16);
  floor.position.y = -0.28;
  scene.add(floor);

  const R = buildRoom();
  scene.add(R.group);
  const man = person();
  scene.add(man);
  const rmt = remote();
  scene.add(rmt);
  const ky = keys();
  ky.position.set(0, -0.02, 0.03);
  man.userData.handL.add(ky);

  const { w, d, h } = ROOM;
  const Zb = -d / 2;
  const win_ = R.window;
  const inflow = heatDots(280, { seed: 3 });
  const pump = heatDots(140, { seed: 7, r: 0.04 });
  const stored = heatDots(90, { seed: 13, r: 0.04, color: MOD.heat2 });
  scene.add(inflow, pump, stored);
  const intake = new THREE.Vector3(1.45, 2.55, Zb + 0.3);
  const fanC = new THREE.Vector3().copy(R.outdoor.position).add(new THREE.Vector3(-0.12, 0.31, 0.2));

  function inflowPath(u, s) {
    const side = s[1] < 0.5 ? 'back' : s[1] < 0.8 ? 'left' : 'right';
    const a = (s[2] * 7.31) % 1, b = (s[3] * 3.77) % 1;
    const go = easeOut(u) * 1.5;
    if (side === 'back') {
      let x = -2.9 + a * 5.8, y = 0.25 + b * 2.6;
      if (s[3] < 0.5) { x = lerp(win_.x0 + 0.1, win_.x1 - 0.1, a); y = lerp(win_.y0 + 0.1, win_.y1 - 0.1, b * 2 % 1); }
      return [x + Math.sin(u * 6 + a * 9) * 0.06, y + Math.sin(u * 5 + b * 7) * 0.08 - u * 0.15, Zb - 0.2 + go];
    }
    if (side === 'left') {
      const z = -2.3 + a * 4.6, y = 0.25 + b * 2.6;
      return [-w / 2 - 0.2 + go, y + Math.sin(u * 5 + a * 7) * 0.08, z + Math.sin(u * 6 + b * 9) * 0.06];
    }
    let z = -2.3 + a * 2.7;
    const y = 0.25 + b * 2.6;
    return [w / 2 + 0.2 - go * 0.9, y + Math.sin(u * 5 + a * 7) * 0.08, z];
  }
  const _v = new THREE.Vector3();
  function pumpPath(u, s) {
    if (u < 0.34) {
      const k = easeIn(u / 0.34);
      const p0 = [-2.2 + s[2] * 4.2, 0.4 + s[3] * 1.8, -1.6 + s[1] * 3.2];
      return [lerp(p0[0], intake.x, k), lerp(p0[1], intake.y, k), lerp(p0[2], intake.z, k)];
    }
    if (u < 0.82) {
      R.pipeCurve.getPointAt(clamp01((u - 0.34) / 0.48), _v);
      return [_v.x, _v.y + 0.02, _v.z + 0.05];
    }
    const k = (u - 0.82) / 0.18;
    return [fanC.x + (s[2] - 0.5) * 0.5 * k, fanC.y + (s[3] - 0.4) * 0.5 * k, fanC.z + 0.05 + k * 1.2];
  }
  function storedPath(u, s) {
    const fromSofa = s[1] < 0.4;
    const p0 = fromSofa ? [-2.6 + s[2] * 0.8, 0.3 + s[3] * 0.5, -0.6 + s[0] * 2] :
      s[1] < 0.75 ? [-2.9 + s[2] * 5.8, 0.3 + s[3] * 2.5, Zb + 0.02] : [-w / 2 + 0.02, 0.3 + s[3] * 2.5, -2.3 + s[2] * 4.6];
    const k = easeInOut(u);
    return [lerp(p0[0], intake.x, k), lerp(p0[1], intake.y, k) + Math.sin(u * Math.PI) * 0.5, lerp(p0[2], intake.z, k)];
  }

  // ---------------------------------------------------------------- 人物动作
  const P0 = [2.25, 1.02], POUT = [3.75, 1.05];
  const leaveA = c('off.leave'), backA = S.restart + 0.05, backB = c('restart.press') - 0.15;
  const leave2 = c('fixed.off') + 0.7;
  function personState(t) {
    let x = P0[0], z = P0[1], yaw = -0.45, walk = 0, amp = 0, vis = true;
    const turn = easeInOut(prog(t, c('hook.look_ac') - 0.1, 0.6));
    yaw = lerp(-0.45, -2.75, turn);
    const walkSeg = (t0, t1, a, b, yw) => {
      const k = prog(t, t0, t1 - t0);
      x = lerp(a[0], b[0], easeInOut(k)); z = lerp(a[1], b[1], easeInOut(k));
      yaw = yw; walk = (t - t0) * 3.2; amp = Math.sin(Math.PI * k) > 0 ? Math.min(1, Math.sin(Math.PI * k) * 3) : 0;
    };
    if (t >= leaveA && t < backA) {
      if (t < leaveA + 0.3) yaw = lerp(-2.75, -Math.PI * 1.5, easeInOut(prog(t, leaveA, 0.3)));
      else if (t < leaveA + 2.0) walkSeg(leaveA + 0.3, leaveA + 2.0, P0, POUT, -Math.PI * 1.5);
      else vis = false;
    } else if (t >= backA && t < backB + 0.5) {
      if (t < backB) walkSeg(backA, backB, POUT, P0, -Math.PI / 2);
      else yaw = lerp(-Math.PI / 2, -2.75, easeInOut(prog(t, backB, 0.3)));
    } else if (t >= leave2) {
      if (t < leave2 + 0.3) yaw = lerp(-2.75, -Math.PI * 1.5, easeInOut(prog(t, leave2, 0.3)));
      else if (t < leave2 + 2.0) walkSeg(leave2 + 0.3, leave2 + 2.0, P0, POUT, -Math.PI * 1.5);
      else vis = false;
    }
    let aR = 0.15;
    for (const p of presses) aR = Math.max(aR, 1.25 * win(t, p - 0.45, p + 0.7, 0.3, 0.3));
    if (t >= c('hook.remote_up') - 0.45 && t < S.question + 0.5) aR = 1.25;
    let aL = 0.1 + 0.9 * win(t, c('hook.keys') - 0.3, c('hook.keys') + 1.2, 0.25, 0.35);
    return { x, z, yaw, walk, amp, aR, aL, vis };
  }
  function doorAngle(t) {
    const open = (a, b) => win(t, a, b, 0.35, 0.45);
    return 1.3 * Math.max(open(leaveA + 0.1, leaveA + 2.4), open(backA - 0.4, backB + 0.6), open(leave2 + 0.1, leave2 + 2.4));
  }

  // ---------------------------------------------------------------- 遥控器（在手里 ↔ 浮到画面中央）
  const hero = new THREE.Vector3(1.32, 1.95, 3.25);
  const heroQ = new THREE.Quaternion().setFromEuler(new THREE.Euler(-0.08, -0.12, 0.0));
  const handOff = new THREE.Vector3(0, -0.03, 0.05);
  const handQoff = new THREE.Quaternion().setFromEuler(new THREE.Euler(-Math.PI / 2, 0, 0));
  const _q = new THREE.Quaternion(), _p = new THREE.Vector3();
  function placeRemote(t) {
    man.updateMatrixWorld(true);
    man.userData.handR.getWorldPosition(_p);
    man.userData.handR.getWorldQuaternion(_q);
    _p.add(handOff.clone().applyQuaternion(_q));
    _q.multiply(handQoff);
    const k = easeInOut(prog(t, c('question.float'), 1.0)) * (1 - easeInOut(prog(t, c('heat.drop') - 0.15, 0.6)));
    rmt.position.lerpVectors(_p, hero, k);
    rmt.quaternion.slerpQuaternions(_q, heroQ, k);
    rmt.scale.setScalar(lerp(1, 1.6, k));
    let press = 0, ir = 0;
    for (const p of presses) { press = Math.max(press, win(t, p - 0.06, p + 0.18, 0.05, 0.1)); ir = Math.max(ir, win(t, p, p + 0.25, 0.01, 0.1)); }
    rmt.userData.button.position.z = 0.011 - 0.004 * press;
    rmt.userData.ir.visible = ir > 0.2;
    rmt.visible = man.visible || k > 0.01;
  }

  // ---------------------------------------------------------------- 电视画面
  const tvc = R.tv.userData.ctx, tvW = 1280, tvH = 720;
  function bar(g, x, base, wdt, hgt, color, label, value) {
    g.fillStyle = color;
    g.beginPath(); g.roundRect(x, base - hgt, wdt, Math.max(hgt, 1), [16, 16, 0, 0]); g.fill();
    g.fillStyle = '#E8EEF4'; g.font = '700 46px NotoSansSC'; g.textAlign = 'center'; g.textBaseline = 'top';
    g.fillText(label, x + wdt / 2, base + 18);
    if (value && hgt > 40) { g.fillStyle = '#FFFFFF'; g.font = '700 60px NotoSansSC'; g.textBaseline = 'bottom'; g.fillText(value, x + wdt / 2, base - hgt - 12); }
  }
  function drawTV(t) {
    const g = tvc;
    const on = win(t, S.short - 0.6, E.long + 0.2, 0.6, 0.6);
    g.fillStyle = '#0E1318'; g.fillRect(0, 0, tvW, tvH);
    if (on <= 0) {
      const rf = g.createLinearGradient(0, 0, tvW, tvH);
      rf.addColorStop(0, 'rgba(255,255,255,0.10)'); rf.addColorStop(0.45, 'rgba(255,255,255,0.02)'); rf.addColorStop(1, 'rgba(255,255,255,0.06)');
      g.fillStyle = rf; g.fillRect(0, 0, tvW, tvH);
      R.tv.userData.tex.needsUpdate = true;
      return;
    }
    g.globalAlpha = on;
    const bgG = g.createLinearGradient(0, 0, 0, tvH);
    bgG.addColorStop(0, '#1C2733'); bgG.addColorStop(1, '#101820');
    g.fillStyle = bgG; g.fillRect(0, 0, tvW, tvH);
    const A = 1 - prog(t, c('short.daikin') - 0.3, 0.3), B = Math.min(prog(t, c('short.daikin'), 0.3), 1 - prog(t, E.short - 0.3, 0.3));
    const C = prog(t, S.long, 0.3);
    const base = 560;
    if (A > 0 && t < E.short) {
      g.globalAlpha = on * A;
      g.fillStyle = '#FFFFFF'; g.font = '700 50px NotoSansSC'; g.textAlign = 'center'; g.textBaseline = 'top';
      g.fillText('45 分钟耗电（单台变频空调实测）', tvW / 2, 40);
      const k1 = easeOutBack(prog(t, c('short.bar_on') - 0.18, 0.36), 1.4), k2 = easeOutBack(prog(t, c('short.bar_off') - 0.18, 0.36), 1.4);
      const full = 330;
      bar(g, 270, base, 260, full * 0.445 / 0.456 * k1, MOD.cool, '一直开', k1 > 0.6 ? '0.445 度' : '');
      bar(g, 750, base, 260, full * k2, MOD.heat, '关 10 分钟', k2 > 0.6 ? '0.456 度' : '');
      g.strokeStyle = 'rgba(255,255,255,0.35)'; g.lineWidth = 4;
      g.beginPath(); g.moveTo(180, base); g.lineTo(1100, base); g.stroke();
      const ke = easeOutBack(prog(t, c('short.equal') - 0.12, 0.3), 2.5);
      if (ke > 0) {
        g.save(); g.translate(640, 380); g.scale(ke, ke);
        g.fillStyle = '#FFFFFF'; g.font = '700 150px NotoSansSC'; g.textAlign = 'center'; g.textBaseline = 'middle';
        g.fillText('≈', 0, 0); g.restore();
      }
      g.fillStyle = 'rgba(232,238,244,0.6)'; g.font = '500 30px NotoSansSC'; g.textAlign = 'right'; g.textBaseline = 'bottom';
      g.fillText('国网江苏电科院 · 澎湃新闻 2019', tvW - 40, tvH - 22);
    }
    if (B > 0) {
      g.globalAlpha = on * B;
      const kb = easeOutBack(prog(t, c('short.daikin') - 0.1, 0.4), 1.6);
      g.save(); g.translate(300, 330); g.scale(kb, kb);
      g.fillStyle = '#FFC94A';
      g.beginPath(); g.arc(0, 0, 80, 0, Math.PI * 2); g.fill();
      g.strokeStyle = '#FFC94A'; g.lineWidth = 16; g.lineCap = 'round';
      for (let i = 0; i < 8; i++) { const a = i / 8 * Math.PI * 2 + t * 0.4; g.beginPath(); g.moveTo(Math.cos(a) * 112, Math.sin(a) * 112); g.lineTo(Math.cos(a) * 150, Math.sin(a) * 150); g.stroke(); }
      g.restore();
      g.fillStyle = '#FFFFFF'; g.textAlign = 'left'; g.textBaseline = 'middle';
      g.font = '700 64px NotoSansSC'; g.fillText('白天外出', 520, 230);
      g.font = '700 64px NotoSansSC'; g.fillText('约 30 分钟', 520, 320);
      g.fillStyle = '#7CC4FF'; g.font = '700 74px NotoSansSC'; g.fillText('开着更省', 520, 440);
      g.fillStyle = 'rgba(232,238,244,0.6)'; g.font = '500 30px NotoSansSC'; g.textAlign = 'right'; g.textBaseline = 'bottom';
      g.fillText('大金空调 · 大阪实测', tvW - 40, tvH - 22);
    }
    if (C > 0) {
      g.globalAlpha = on * C;
      g.fillStyle = '#FFFFFF'; g.font = '700 50px NotoSansSC'; g.textAlign = 'center'; g.textBaseline = 'top';
      g.fillText('离开几个小时', tvW / 2, 40);
      const kg = easeInOut(prog(t, c('long.bars') - 0.4, 3.2));
      const hOn = lerp(120, 360, kg), hOff = lerp(110, 150, kg);
      bar(g, 270, base, 260, hOn * easeOut(prog(t, S.long, 0.6)), MOD.cool, '一直开', '');
      bar(g, 750, base, 260, hOff * easeOut(prog(t, S.long, 0.6)), MOD.heat, '关掉', '');
      g.strokeStyle = 'rgba(255,255,255,0.35)'; g.lineWidth = 4;
      g.beginPath(); g.moveTo(180, base); g.lineTo(1100, base); g.stroke();
      g.fillStyle = 'rgba(232,238,244,0.6)'; g.font = '500 30px NotoSansSC'; g.textAlign = 'right'; g.textBaseline = 'bottom';
      g.fillText('示意，不是实测数值', tvW - 40, tvH - 22);
    }
    g.globalAlpha = 1;
    R.tv.userData.tex.needsUpdate = true;
  }

  // ---------------------------------------------------------------- 相机路径（全片时间关键帧）
  const K = (t, pos, look, fov = 40) => ({ t, pos, look, fov });
  const wide = [-1.35, 1.15, -0.2];
  const keys_ = [
    K(0, [1.9, 2.0, 8.2], [1.5, 1.45, -0.2], 40),
    K(c('hook.look_ac') - 0.2, [1.7, 2.05, 7.4], [1.5, 1.6, -0.4]),
    K(E.hook - 0.3, [1.4, 2.1, 6.2], [1.45, 2.05, -1.0]),
    K(S.question + 1.0, [1.3, 2.0, 4.45], hero.toArray()),
    K(c('heat.drop') - 0.05, [1.3, 2.0, 4.3], hero.toArray()),
    K(c('heat.drop') + 1.7, [-1.55, 6.6, 13.6], wide, 56),
    K(E.heat - 0.6, [-1.15, 6.4, 13.3], wide, 56),
    K(S.acon + 1.6, [-1.55, 5.2, 12.6], [-1.35, 1.25, -0.2], 56),
    K(E.acon - 0.5, [-1.35, 5.4, 12.9], [-1.35, 1.25, -0.2], 56),
    K(S.off + 1.4, [-1.15, 6.0, 13.4], [-1.25, 1.15, -0.2], 56),
    K(E.off - 0.4, [-1.25, 5.6, 12.8], [-1.25, 1.2, -0.2], 56),
    K(S.restart + 1.6, [-1.35, 5.3, 12.7], [-1.35, 1.25, -0.3], 56),
    K(E.restart - 0.5, [-1.45, 5.5, 13.0], [-1.35, 1.2, -0.3], 56),
    K(S.short + 1.8, [1.4, 1.45, 3.75], [1.4, 1.4, Zb]),
    K(E.short - 0.3, [1.4, 1.42, 3.45], [1.4, 1.4, Zb]),
    K(S.long + 1.3, [0.95, 1.6, 4.4], [0.95, 1.55, Zb]),
    K(E.long - 0.3, [0.95, 1.6, 4.2], [0.95, 1.55, Zb]),
    K(S.toggle + 1.3, [1.3, 2.25, 2.05], [1.45, 2.4, Zb]),
    K(E.toggle - 0.3, [1.3, 2.25, 1.85], [1.45, 2.4, Zb]),
    K(S.fixed + 1.6, [-1.55, 5.2, 12.6], [-1.35, 1.25, -0.2], 56),
    K(E.fixed - 0.4, [-1.35, 5.4, 12.9], [-1.35, 1.25, -0.2], 56),
    K(S.conclusion + 1.5, [-1.2, 7.6, 15.0], [-1.2, 2.5, -0.3], 56),
    K(S.credits + 0.6, [-1.2, 8.6, 17.0], [-1.2, 3.0, -0.3], 56),
    K(TL.end, [-1.2, 9.4, 18.8], [-1.2, 3.3, -0.3], 56),
  ];
  function moveCam(t) {
    let i = 0;
    while (i < keys_.length - 2 && t > keys_[i + 1].t) i++;
    const a = keys_[i], b = keys_[i + 1];
    const k = easeInOut(prog(t, a.t, b.t - a.t));
    camera.position.set(...a.pos.map((v, j) => lerp(v, b.pos[j], k)));
    camera.lookAt(...a.look.map((v, j) => lerp(v, b.look[j], k)));
    const fov = lerp(a.fov, b.fov, k);
    if (camera.fov !== fov) { camera.fov = fov; camera.updateProjectionMatrix(); }
    camera.updateMatrixWorld();
  }
  const _s = new THREE.Vector3();
  const scr = (x, y, z) => { _s.set(x, y, z).project(camera); return [(_s.x + 1) / 2 * W, (1 - _s.y) / 2 * H]; };

  // ---------------------------------------------------------------- 标签
  const outPill = el(pillCSS(MOD.hot));
  const inPill = el(pillCSS(MOD.cool));
  const deltaPill = el({ font: '700 44px NotoSansSC', color: MOD.ink, background: '#FFFFFF', padding: '10px 30px', borderRadius: '40px',
    border: `4px solid ${MOD.heat}`, boxShadow: '0 6px 18px rgba(20,30,40,0.16)' });
  const optOn = el({ ...pillCSS(MOD.cool), font: '700 52px NotoSansSC', padding: '18px 34px', borderRadius: '24px' }, '一直开');
  const optOff = el({ ...pillCSS(MOD.heat), font: '700 52px NotoSansSC', padding: '18px 34px', borderRadius: '24px' }, '关掉');
  const qmark = el({ font: '900 150px NotoSansSC', color: MOD.ink, textShadow: '0 6px 20px rgba(255,255,255,0.9)' }, '?');
  const hud = el({ width: '560px', height: '96px', background: 'rgba(255,255,255,0.92)', borderRadius: '24px',
    boxShadow: '0 8px 24px rgba(20,30,40,0.14)' },
  `<div style="position:absolute;left:30px;top:24px;font:700 38px NotoSansSC;color:${MOD.ink}">空调耗电</div>
   <div style="position:absolute;left:220px;top:36px;width:300px;height:26px;border-radius:13px;background:#E3E8ED;overflow:hidden">
   <div class="f" style="height:100%;width:0;border-radius:13px"></div></div>`);
  const hudFill = hud.querySelector('.f');
  const protect = el({ ...pillCSS('#FFFFFF', MOD.ink), border: `4px solid ${MOD.hot}`, font: '700 42px NotoSansSC' }, '重启保护 约 3 分钟');
  const compTag = el(pillCSS(MOD.ok));
  const fixedTag = el(pillCSS('#FFFFFF', MOD.ink), '定频空调');
  const summary = el({ width: '860px', background: 'rgba(255,255,255,0.95)', borderRadius: '32px', padding: '34px 0',
    boxShadow: '0 12px 32px rgba(20,30,40,0.16)' });
  const ROWS = [['离开半小时内', '开着', MOD.cool], ['离开几个小时', '关掉', MOD.heat], ['定频空调', '离开就关', MOD.heat]];
  summary.innerHTML = ROWS.map(([a, b, col], i) => `<div class="r" style="display:flex;justify-content:space-between;align-items:center;
    margin:0 48px;padding:20px 0;${i ? 'border-top:2px solid #E6EAEE;' : ''}font:700 50px NotoSansSC;color:${MOD.ink}">
    <span>${a}</span><span style="color:#fff;background:${col};padding:6px 28px;border-radius:30px">${b}</span></div>`).join('');
  const rows = [...summary.querySelectorAll('.r')];
  const refs = el({ width: '880px', background: 'rgba(255,255,255,0.95)', borderRadius: '32px', padding: '38px 50px', boxSizing: 'border-box',
    whiteSpace: 'normal', boxShadow: '0 12px 32px rgba(20,30,40,0.16)' },
  `<div style="font:700 46px NotoSansSC;color:${MOD.ink};margin-bottom:18px">依据与出处</div>` +
    (TL.refs || []).map(r => `<div style="font:500 32px NotoSansSC;color:${MOD.ink2};line-height:50px">· ${r}</div>`).join(''));

  function drawLabels(t) {
    const rT = roomT(t);
    const lab = win(t, c('heat.drop') + 0.25, E.off + 0.6, 0.01, 0.5) + win(t, c('restart.press'), E.restart + 0.3, 0.3, 0.5);
    const [ox, oy] = scr(-1.4, 3.45, Zb - 0.3);
    place(outPill, ox, oy, lab, pop(t, c('heat.drop') + 0.25) || 1);
    html(outPill, `室外 ${OUT_T}°C`);
    const [ix, iy] = scr(0.4, 1.75, 0.5);
    place(inPill, ix, iy, lab, pop(t, c('heat.drop') + 0.32) || 1);
    html(inPill, `室内 ${Math.round(rT)}°C`);
    inPill.style.background = rT > 28.5 ? MOD.heat : MOD.cool;
    const dk = win(t, c('heat.delta'), E.heat + 0.2, 0.01, 0.5) + win(t, c('off.delta'), E.off + 0.3, 0.01, 0.5);
    const dpop = t < E.heat + 1 ? pop(t, c('heat.delta')) : pop(t, c('off.delta'));
    const [dx, dy] = scr(-0.7, 2.75, -1.2);
    place(deltaPill, dx, dy, dk, dpop * (1 + 0.12 * bump(t, c('off.delta'), 5)));
    html(deltaPill, `温差 ${Math.round(OUT_T - rT)}°C`);

    const q = Math.min(1, 1 - prog(t, c('heat.drop') - 0.5, 0.4));
    const [hx, hy] = scr(hero.x, hero.y, hero.z);
    place(optOn, hx - 330, hy + 20, q * clamp01(pop(t, c('question.opt_on')) * 2), pop(t, c('question.opt_on')));
    place(optOff, hx + 330, hy + 20, q * clamp01(pop(t, c('question.opt_off')) * 2), pop(t, c('question.opt_off')));
    place(qmark, hx, hy - 330, q * clamp01(pop(t, c('question.ask')) * 2), pop(t, c('question.ask')));

    const hk = win(t, c('acon.pump') - 0.3, E.off + 0.2, 0.4, 0.5) + win(t, c('restart.press') - 0.4, E.restart, 0.3, 0.5)
      + win(t, c('fixed.run') + 0.3, E.fixed, 0.4, 0.5);
    place(hud, W / 2, 352, hk);
    const pw = power(t);
    hudFill.style.width = `${Math.round(clamp01(pw) * 100)}%`;
    hudFill.style.background = pw > 0.75 ? MOD.hot : pw > 0.3 ? MOD.heat : MOD.ok;

    const [px, py] = scr(1.45, 2.95, Zb + 0.2);
    place(protect, px, py - 30, win(t, c('toggle.protect'), E.toggle + 0.2, 0.01, 0.4), pop(t, c('toggle.protect')));
    const [cx, cy] = scr(R.outdoor.position.x, 1.1, R.outdoor.position.z);
    const runNow = running(t);
    html(compTag, runNow ? '压缩机 运转' : '压缩机 停');
    compTag.style.background = runNow ? MOD.ok : '#8A96A3';
    const ck = win(t, c('fixed.run'), c('fixed.off') - 0.2, 0.01, 0.3);
    place(compTag, cx, cy, ck, t < c('fixed.stop') ? pop(t, c('fixed.run')) : pop(t, c('fixed.stop')));
    const [fx, fy] = scr(1.45, 3.05, Zb + 0.2);
    place(fixedTag, fx, fy, win(t, S.fixed + 0.6, c('fixed.off'), 0.4, 0.3));

    const sk = win(t, c('conclusion.summary'), E.conclusion + 0.1, 0.01, 0.4);
    place(summary, W / 2, 560, sk, 0.9 + 0.1 * pop(t, c('conclusion.summary')));
    rows.forEach((r, i) => { r.style.opacity = String(0.25 + 0.75 * easeOut(prog(t, c('conclusion.rows') - 1.2 + i * 0.55, 0.35))); });
    const rk = prog(t, c('credits.refs') - 0.1, 0.5);
    place(refs, W / 2, 760, rk, 1 + 0.035 * bump(t, c('credits.final'), 6) * Math.cos((t - c('credits.final')) * 24));
  }

  // ---------------------------------------------------------------- 每帧
  function update(lt, t) {
    moveCam(t);
    const st = personState(t);
    man.visible = st.vis;
    man.position.set(st.x, 0, st.z);
    man.rotation.y = st.yaw;
    man.userData.pose({ walk: st.walk, amp: st.amp, aR: st.aR, aL: st.aL });
    R.doorPivot.rotation.y = doorAngle(t);
    placeRemote(t);

    const on = acOn(t);
    const txt = !on ? '' : protecting(t) ? '保护中' : `${Math.round(Math.max(26, roomT(t)))}°`;
    R.indoor.userData.set(louverK(t), txt, on);
    R.cold.userData.set(coldK(t) * (1 - 0.85 * win(t, S.short - 0.4, E.long + 0.4, 0.6, 0.8)), t);
    R.outdoor.userData.fan.rotation.z = -fanAng(t);
    void fanSpin;

    const dT = OUT_T - roomT(t);
    const inK = prog(t, c('heat.drop') - 0.1, 0.5) * (1 - win(t, S.short - 0.4, E.toggle + 0.6, 0.6, 0.8));
    inflow.userData.update(t, clamp01(dT / 9) * 0.95 * inK, inflowPath, 0.26, 0.15);
    pump.userData.update(pumpPhase(t), pumpDens(t) * prog(t, c('acon.pump') - 0.3, 0.6) * (1 - win(t, S.short - 0.4, E.toggle + 0.6, 0.6, 0.8)), pumpPath, 1, 0.06);
    const sd = win(t, c('restart.stored') - 0.2, E.restart + 0.5, 0.5, 1.2);
    stored.userData.update(t, sd * 0.95, storedPath, 0.32, 0.15);
    const glowK = 0.55 * win(t, c('restart.stored') - 0.1, E.restart + 0.3, 0.3, 1.5);
    R.wallMat.emissiveIntensity = glowK * 0.5;
    R.sofaMat.emissiveIntensity = glowK;
    R.clock.userData.set(2.25 + 3 * easeInOut(prog(t, c('long.clock'), 3.6)));
    drawTV(t);
    drawLabels(t);
  }
  update(0, 0);
  return { scene, camera, update };
}
