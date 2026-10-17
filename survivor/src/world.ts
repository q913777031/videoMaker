import { backOut, bounceOut, easeInOut, easeOut, hash01, lerp, prog } from "./anim";
import {
  CHAMPION,
  GAP,
  N,
  PHASE,
  ROUNDS,
  WORLD_RADIUS,
  activeIn,
  elimRound,
  guessHeads,
  pos,
  resultTime,
  survivorRadius,
} from "./data";
import { TL } from "./timeline";

/** 色板：深蓝底、米白人物、金色冠军、低饱和灰色退出者 */
export const C = {
  bg: "#0C1A38",
  bg2: "#15295A",
  cream: "#F4EAD5",
  gold: "#F5C04A",
  goldDeep: "#C8902A",
  grey: "#5A647E",
  greyHead: "#6A7490",
  ink: "#16203D",
};

export const W = 1080;
export const H = 1920;
/** 世界原点在屏幕上的默认位置 */
export const CX = 540;
export const CY = 1000;

/** 相机：世界坐标 (cx, cy) 位于屏幕 (CX, CY)，s 为每个世界单位对应的像素数 */
export type Cam = { cx: number; cy: number; s: number };
export const toScreen = (cam: Cam, x: number, y: number): [number, number] => [
  CX + (x - cam.cx) * cam.s,
  CY + (y - cam.cy) * cam.s,
];
export const toWorld = (cam: Cam, sx: number, sy: number): [number, number] => [
  (sx - CX) / cam.s + cam.cx,
  (sy - CY) / cam.s + cam.cy,
];

const ev = TL.events;
const sc = TL.scenes;
const FIT_W = 880;
/** 让第 r 轮后的幸存者恰好占满画面宽度的缩放 */
const fit = (r: number) => (r === 0 ? FIT_W / 32.6 : Math.min(430, FIT_W / (2 * (survivorRadius(r) + 0.75))));
export const FIT_ALL = FIT_W / (2 * (WORLD_RADIUS + 0.6));
export const GURU_CAM: Cam = { cx: 0, cy: -0.2, s: 680 };
const HOOK_CAM: Cam = { cx: 0, cy: -0.25, s: 600 };
const MID_S = 78;

/** 在对数空间插值缩放，镜头推拉速度在视觉上更均匀 */
const zoomLerp = (a: number, b: number, t: number) => Math.exp(lerp(Math.log(a), Math.log(b), t));

export const camera = (t: number): Cam => {
  if (t < sc.hook[1]) return HOOK_CAM;
  if (t < sc.rounds[0] + 0.1) {
    const p = easeInOut(prog(t, sc.setup[0] + 0.1, sc.setup[0] + 2.6));
    return { cx: 0, cy: 0, s: zoomLerp(150, fit(0), p) };
  }
  if (t < sc.guru[0]) {
    let s = fit(0);
    for (let r = 1; r <= ROUNDS; r++) {
      const [st, d] = ev.rounds[r - 1];
      const p = easeInOut(prog(t, st + PHASE.move[0] * d, st + PHASE.move[1] * d));
      if (p > 0) s = zoomLerp(fit(r - 1), fit(r), p);
    }
    return { cx: 0, cy: 0, s };
  }
  if (t < ev.zoom1[0]) {
    const p = easeInOut(prog(t, sc.guru[0], sc.guru[0] + 0.9));
    return { cx: 0, cy: lerp(0, GURU_CAM.cy, p), s: zoomLerp(fit(ROUNDS), GURU_CAM.s, p) };
  }
  const p1 = easeInOut(prog(t, ev.zoom1[0], ev.zoom1[1]));
  const p2 = easeInOut(prog(t, ev.zoom2[0], ev.zoom2[1]));
  if (p2 <= 0) return { cx: 0, cy: lerp(GURU_CAM.cy, -0.05, p1), s: zoomLerp(GURU_CAM.s, MID_S, p1) };
  return { cx: 0, cy: lerp(-0.05, 0, p2), s: zoomLerp(MID_S, FIT_ALL, p2) };
};

/** 冻结期间的动画时钟：暂停时人物的眨眼、摆动全部定格 */
export const animClock = (t: number) => (t >= ev.freeze && t < ev.zoom1[0] ? ev.freeze : t);

// ---------------------------------------------------------------- 小人

export type PersonStyle = {
  body: string;
  head: string;
  alpha?: number;
  /** 0 = 手臂自然下垂，越大越往外上方抬起（弧度） */
  armL?: number;
  armR?: number;
  /** 眼睛看向的方向（单位向量） */
  look?: [number, number];
  blink?: boolean;
  mouth?: number;
  sad?: boolean;
};

/**
 * 统一的矢量小人：(x, y) 为身体中心，u 为每世界单位像素（人高约 0.84u）。
 * 按像素尺寸自动降低细节，保证 1024 人同屏时依然清楚且绘制开销低。
 */
export const drawPerson = (ctx: CanvasRenderingContext2D, x: number, y: number, u: number, st: PersonStyle) => {
  ctx.globalAlpha = st.alpha ?? 1;
  const headR = 0.17 * u;
  const hx = x;
  const hy = y - 0.22 * u;
  // 身体
  ctx.fillStyle = st.body;
  const bw = 0.38 * u;
  const top = y - 0.06 * u;
  const bot = y + 0.37 * u;
  const rr = Math.min(0.16 * u, bw / 2);
  ctx.beginPath();
  ctx.moveTo(x - bw / 2, bot);
  ctx.lineTo(x - bw / 2, top + rr);
  ctx.quadraticCurveTo(x - bw / 2, top, x - bw / 2 + rr, top);
  ctx.lineTo(x + bw / 2 - rr, top);
  ctx.quadraticCurveTo(x + bw / 2, top, x + bw / 2, top + rr);
  ctx.lineTo(x + bw / 2, bot);
  ctx.closePath();
  ctx.fill();
  // 手臂
  if (u > 26) {
    ctx.strokeStyle = st.body;
    ctx.lineCap = "round";
    ctx.lineWidth = 0.075 * u;
    for (const side of [-1, 1]) {
      const a = (side < 0 ? st.armL : st.armR) ?? 0.3;
      const sx = x + side * (bw / 2 - 0.02 * u);
      const sy = top + 0.08 * u;
      const len = 0.24 * u;
      ctx.beginPath();
      ctx.moveTo(sx, sy);
      ctx.lineTo(sx + side * Math.sin(a) * len, sy + Math.cos(a) * len);
      ctx.stroke();
    }
  }
  // 头
  ctx.fillStyle = st.head;
  ctx.beginPath();
  ctx.arc(hx, hy, headR, 0, Math.PI * 2);
  ctx.fill();
  // 五官
  if (u > 16) {
    const [lx, ly] = st.look ?? [0, 0];
    const ex = 0.065 * u;
    const ey = hy - 0.005 * u + (st.sad ? 0.02 * u : 0);
    const er = Math.max(0.9, 0.028 * u);
    ctx.fillStyle = C.ink;
    for (const side of [-1, 1]) {
      const px = hx + side * ex + lx * 0.03 * u;
      const py = ey + ly * 0.025 * u;
      ctx.beginPath();
      if (st.blink) ctx.ellipse(px, py, er, er * 0.18, 0, 0, Math.PI * 2);
      else ctx.arc(px, py, er, 0, Math.PI * 2);
      ctx.fill();
    }
    if (u > 60) {
      ctx.strokeStyle = C.ink;
      ctx.lineWidth = 0.022 * u;
      ctx.lineCap = "round";
      const my = hy + 0.075 * u;
      const m = st.mouth ?? 0;
      if (m > 0.05) {
        ctx.beginPath();
        ctx.ellipse(hx, my + 0.01 * u, 0.04 * u, 0.012 * u + 0.035 * u * m, 0, 0, Math.PI * 2);
        ctx.fillStyle = C.ink;
        ctx.fill();
      } else {
        ctx.beginPath();
        if (st.sad) ctx.arc(hx, my + 0.05 * u, 0.045 * u, 1.15 * Math.PI, 1.85 * Math.PI);
        else ctx.arc(hx, my - 0.02 * u, 0.05 * u, 0.2 * Math.PI, 0.8 * Math.PI);
        ctx.stroke();
      }
    }
  }
  ctx.globalAlpha = 1;
};

/** 皇冠：(x, y) 为底边中心 */
export const drawCrown = (ctx: CanvasRenderingContext2D, x: number, y: number, u: number) => {
  const w = 0.36 * u;
  const h = 0.2 * u;
  ctx.fillStyle = C.gold;
  ctx.strokeStyle = C.goldDeep;
  ctx.lineWidth = Math.max(1, 0.015 * u);
  ctx.beginPath();
  ctx.moveTo(x - w / 2, y);
  ctx.lineTo(x - w / 2, y - h * 0.75);
  ctx.lineTo(x - w / 4, y - h * 0.35);
  ctx.lineTo(x, y - h);
  ctx.lineTo(x + w / 4, y - h * 0.35);
  ctx.lineTo(x + w / 2, y - h * 0.75);
  ctx.lineTo(x + w / 2, y);
  ctx.closePath();
  ctx.fill();
  ctx.stroke();
  ctx.fillStyle = "#FFF4CF";
  for (const k of [-0.5, 0, 0.5]) {
    ctx.beginPath();
    ctx.arc(x + k * w * 0.5, y - h * 0.18, 0.022 * u, 0, Math.PI * 2);
    ctx.fill();
  }
};

/** 领奖台：(x, y) 为台面中心 */
export const drawPodium = (ctx: CanvasRenderingContext2D, x: number, y: number, u: number) => {
  const w = 1.15 * u;
  const h = 0.75 * u;
  const g = ctx.createLinearGradient(x, y, x, y + h);
  g.addColorStop(0, C.gold);
  g.addColorStop(1, C.goldDeep);
  ctx.fillStyle = g;
  ctx.fillRect(x - w / 2, y, w, h);
  ctx.fillStyle = "#FFE29A";
  ctx.fillRect(x - w / 2, y, w, 0.06 * u);
  // 台面上的五角星
  ctx.fillStyle = "#FFF4CF";
  ctx.beginPath();
  for (let k = 0; k < 10; k++) {
    const r = (k % 2 ? 0.07 : 0.16) * u;
    const a = -Math.PI / 2 + (k * Math.PI) / 5;
    ctx.lineTo(x + r * Math.cos(a), y + 0.36 * u + r * Math.sin(a));
  }
  ctx.closePath();
  ctx.fill();
};

// ---------------------------------------------------------------- 时间 → 每人状态

/** 开场方阵中每人出现的时刻：由中心向外扩散 */
const appearAt = new Float32Array(N);
{
  let maxD = 0;
  for (let id = 0; id < N; id++) maxD = Math.max(maxD, Math.hypot(pos[0][2 * id], pos[0][2 * id + 1]));
  for (let id = 0; id < N; id++) {
    const d = Math.hypot(pos[0][2 * id], pos[0][2 * id + 1]) / maxD;
    appearAt[id] = sc.setup[0] + 0.15 + d * 2.1 + hash01(id) * 0.08;
  }
}
const appearSorted = Float32Array.from(appearAt).sort();
/** t 时刻开场方阵中已出现的人数（与画面同源） */
export const appearedCount = (t: number) => {
  let lo = 0;
  let hi = N;
  while (lo < hi) {
    const m = (lo + hi) >> 1;
    if (appearSorted[m] <= t) lo = m + 1;
    else hi = m;
  }
  return lo;
};

/** t 时刻第 id 人的世界坐标 */
export const personPos = (id: number, t: number): [number, number] => {
  if (t < sc.setup[0]) return [pos[ROUNDS][2 * id], pos[ROUNDS][2 * id + 1]];
  let p = pos[0];
  let x = p[2 * id];
  let y = p[2 * id + 1];
  for (let r = 1; r <= ROUNDS; r++) {
    const [st, d] = ev.rounds[r - 1];
    const k = easeInOut(prog(t, st + PHASE.move[0] * d, st + PHASE.move[1] * d));
    if (k <= 0) break;
    p = pos[r];
    x = lerp(x, p[2 * id], k);
    y = lerp(y, p[2 * id + 1], k);
  }
  return [x, y];
};

/** 是否已出局（变灰）；开场“先展示赢家”使用最终状态 */
export const isOut = (id: number, t: number) => {
  const e = elimRound[id];
  if (e === 0) return false;
  if (t < sc.setup[0]) return true;
  return t >= resultTime(e);
};

export const championGold = (t: number) => t < sc.setup[0] || t >= sc.guru[0];

/** 冠军是否正在说话（嘴部动画） */
const championTalking = (t: number) => TL.lines.some((l) => l.speaker === "c" && t >= l.start && t <= l.end);

const championArms = (t: number): [number, number] => {
  if (t < sc.hook[1]) return [0.35, 2.5];
  if (t < sc.guru[0]) return [0.3, 0.3];
  let l = 0.35;
  let r = 0.35;
  ev.secrets.forEach((s, i) => {
    const up = easeOut(prog(t, s - 0.1, s + 0.2)) * (1 - easeInOut(prog(t, s + 0.9, s + 1.3)));
    if (i === 0) l = lerp(l, 2.3, up);
    if (i === 1) r = lerp(r, 2.3, up);
  });
  const g = prog(t, ev.secrets[2] + 0.35, ev.secrets[2] + 0.6) * (1 - prog(t, ev.absurd + 0.6, ev.absurd + 0.9));
  if (g > 0) {
    const wig = Math.sin(t * 28) * 0.25;
    l = lerp(l, 1.7 + wig, g);
    r = lerp(r, 1.7 - wig, g);
  }
  return [l, r];
};

/** 关键退出者：揭晓时冒出“我也……”想法的人（由数据确定性挑选） */
export const BUBBLE_PEOPLE: { id: number; text: string }[] = (() => {
  const want: [number, number, string][] = [
    [-145, 15, "我也相信自己"],
    [-38, 16, "我也坚持判断"],
    [22, 14, "我手感也不错"],
    [95, 15, "我也相信自己"],
    [165, 14, "我也坚持判断"],
  ];
  return want.map(([deg, rad, text]) => {
    const tx = rad * Math.cos((deg * Math.PI) / 180);
    const ty = rad * Math.sin((deg * Math.PI) / 180);
    let best = 0;
    let bd = Infinity;
    for (let id = 0; id < N; id++) {
      if (id === CHAMPION) continue;
      const d = (pos[ROUNDS][2 * id] - tx) ** 2 + (pos[ROUNDS][2 * id + 1] - ty) ** 2;
      if (d < bd) {
        bd = d;
        best = id;
      }
    }
    return { id: best, text };
  });
})();
const bubbleSet = new Set(BUBBLE_PEOPLE.map((b) => b.id));

/** 在给定画布上绘制整座“世界”：场地、1024 人、猜测标记、领奖台、皇冠、聚光灯 */
export const drawWorld = (ctx: CanvasRenderingContext2D, t: number, cam: Cam) => {
  ctx.clearRect(0, 0, W, H);
  const ta = animClock(t);
  const u = cam.s;
  const inRounds = t >= sc.setup[0] && t < sc.guru[0];

  // 场地边界：场内（亮）与场外（灰）的分界线
  if (t >= ev.rounds[0][0] && t < sc.guru[0] + 0.5) {
    let ringR = 23.5;
    for (let r = 1; r <= ROUNDS; r++) {
      const [st, d] = ev.rounds[r - 1];
      const k = easeInOut(prog(t, st + PHASE.move[0] * d, st + PHASE.move[1] * d));
      if (k <= 0) break;
      ringR = lerp(ringR, survivorRadius(r) + GAP / 2, k);
    }
    const a = prog(t, ev.rounds[0][0], ev.rounds[0][0] + 0.6) * (1 - prog(t, sc.guru[0], sc.guru[0] + 0.5));
    const [ox, oy] = toScreen(cam, 0, 0);
    ctx.save();
    ctx.globalAlpha = 0.32 * a;
    ctx.strokeStyle = C.cream;
    ctx.setLineDash([14, 12]);
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.arc(ox, oy, ringR * u, 0, Math.PI * 2);
    ctx.stroke();
    ctx.restore();
  }

  const showPodium = t < sc.setup[0] || t >= ev.podium;
  const podiumRise = t < sc.setup[0] ? 0 : 1 - easeOut(prog(t, ev.podium, ev.podium + 0.5));

  // 先画退出者，再画场上的人，冠军最后画
  const cr = currentRoundFor(t);
  const drawOne = (id: number) => {
    const [wx, wy] = personPos(id, t);
    const [sx, sy0] = toScreen(cam, wx, wy);
    const margin = u * 0.8;
    if (sx < -margin || sx > W + margin || sy0 < -margin || sy0 > H + margin) return;
    const h = hash01(id);
    let scale = 1;
    if (t >= sc.setup[0] && t < sc.setup[0] + 3) {
      const k = prog(t, appearAt[id], appearAt[id] + 0.28);
      if (k <= 0) return;
      scale = backOut(k);
    }
    const out = isOut(id, t);
    const champ = id === CHAMPION;
    const gold = champ && championGold(t);
    let sy = sy0;
    // 待机摆动
    const bob = Math.sin((ta * 1.6 + h) * Math.PI * 2) * 0.012 * u;
    sy += out ? bob * 0.4 : bob;
    // 刚出局时的一缩
    if (out && elimRound[id] > 0 && t >= sc.setup[0]) {
      const k = prog(t, resultTime(elimRound[id]), resultTime(elimRound[id]) + 0.25);
      scale *= 1 - 0.12 * Math.sin(k * Math.PI) - 0.06 * k;
    }
    const blink = (ta + h * 4) % 3.7 < 0.12;
    let look: [number, number] = [0, 0];
    if (out) {
      const d = Math.hypot(wx, wy) || 1;
      look = [-wx / d, -wy / d];
    }
    const talking = champ && championTalking(ta);
    const [armL, armR] = champ ? championArms(ta) : [0.3, 0.3];
    let alpha = 1;
    if (out) alpha = bubbleSet.has(id) && t >= ev.bubbles ? 1 : 0.92;
    drawPerson(ctx, sx, sy, u * scale, {
      body: gold ? C.gold : out ? C.grey : C.cream,
      head: gold ? "#FFD772" : out ? C.greyHead : "#FFF6E6",
      alpha,
      armL,
      armR,
      look,
      blink,
      sad: out && u > 40,
      mouth: talking ? 0.5 + 0.5 * Math.sin(ta * Math.PI * 2 * 6) : 0,
    });
    // 猜测标记：实心金点 = 猜正面，空心圈 = 猜反面
    if (inRounds && cr > 0 && activeIn(id, cr)) {
      const [st, d] = ev.rounds[cr - 1];
      const lp = (t - st) / d;
      if (lp >= 0.02 && lp < 0.6) {
        const k = backOut(prog(lp, 0.02, 0.1)) * (1 - prog(lp, 0.54, 0.6));
        const r = Math.max(2.4, 0.11 * u) * k;
        const dy = sy - 0.62 * u * scale;
        const wrong = out;
        ctx.globalAlpha = wrong ? 0.55 : 1;
        if (guessHeads(id, cr)) {
          ctx.fillStyle = wrong ? C.grey : C.gold;
          ctx.beginPath();
          ctx.arc(sx, dy, r, 0, Math.PI * 2);
          ctx.fill();
        } else {
          ctx.strokeStyle = wrong ? C.grey : C.cream;
          ctx.lineWidth = Math.max(1.4, r * 0.38);
          ctx.beginPath();
          ctx.arc(sx, dy, r * 0.85, 0, Math.PI * 2);
          ctx.stroke();
        }
        ctx.globalAlpha = 1;
      }
    }
  };

  for (let pass = 0; pass < 2; pass++) {
    for (let id = 0; id < N; id++) {
      if (id === CHAMPION) continue;
      if (isOut(id, t) === (pass === 0)) drawOne(id);
    }
  }

  // 聚光灯：压暗四周，只照亮冠军
  const dark = spotlightDark(t);
  if (dark > 0) {
    const [ox, oy] = toScreen(cam, 0, 0.05);
    const g = ctx.createRadialGradient(ox, oy, 0.55 * u, ox, oy, 1.6 * u);
    g.addColorStop(0, "rgba(5,9,22,0)");
    g.addColorStop(1, `rgba(5,9,22,${0.78 * dark})`);
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, H);
    // 光柱
    const [tx, ty] = toScreen(cam, 0, -7);
    const [fx, fy] = toScreen(cam, 0, 0.45);
    const lg = ctx.createLinearGradient(tx, ty, fx, fy);
    lg.addColorStop(0, `rgba(255,236,180,${0.0 * dark})`);
    lg.addColorStop(1, `rgba(255,236,180,${0.2 * dark})`);
    ctx.fillStyle = lg;
    ctx.beginPath();
    ctx.moveTo(tx - 0.25 * u, ty);
    ctx.lineTo(tx + 0.25 * u, ty);
    ctx.lineTo(fx + 0.75 * u, fy);
    ctx.lineTo(fx - 0.75 * u, fy);
    ctx.closePath();
    ctx.fill();
  }

  // 领奖台、冠军、皇冠
  if (showPodium) {
    const [px, py] = toScreen(cam, 0, 0.37 + podiumRise * 4);
    drawPodium(ctx, px, py, u);
  }
  if (championGold(t)) {
    const [gx, gy] = toScreen(cam, 0, 0);
    const glow = ctx.createRadialGradient(gx, gy, 0, gx, gy, 0.9 * u + 30);
    glow.addColorStop(0, "rgba(245,192,74,0.35)");
    glow.addColorStop(1, "rgba(245,192,74,0)");
    ctx.fillStyle = glow;
    ctx.fillRect(gx - u - 40, gy - u - 40, 2 * u + 80, 2 * u + 80);
  }
  drawOne(CHAMPION);
  if (t >= ev.crown) {
    const k = bounceOut(prog(t, ev.crown, ev.crownLand + 0.25));
    const [cx, cy] = toScreen(cam, 0, -0.38 - (1 - k) * 3);
    const bob = Math.sin((ta * 1.6 + hash01(CHAMPION)) * Math.PI * 2) * 0.012 * u;
    drawCrown(ctx, cx, cy + bob, u);
  }
};

const currentRoundFor = (t: number) => {
  let k = 0;
  for (let r = 1; r <= ROUNDS; r++) if (t >= ev.rounds[r - 1][0]) k = r;
  return k;
};

/** 聚光灯压暗程度：开场与冠军开课时亮起，反转拉远时撤掉，让场外的人显露出来 */
export const spotlightDark = (t: number) => {
  if (t < sc.hook[1]) return 0.55;
  if (t < sc.guru[0]) return 0;
  const on = prog(t, ev.podium, ev.podium + 0.6) * 0.75;
  const off = 1 - prog(t, ev.zoom1[0] + 0.2, ev.zoom1[0] + 1.6);
  return on * off;
};

