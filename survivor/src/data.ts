import { rng } from "./anim";
import { TL } from "./timeline";

/**
 * 1024 名选手的唯一数据源：身份、淘汰轮次、每轮猜测与站位。
 * 画面中的人数、轮次、灰色/亮色状态、字幕数字都从这里推出，避免互相矛盾。
 *
 * 教学示意：每轮“恰好一半”猜错，这是为讲解而预设的理想化序列，不是真实随机实验的结果。
 */
export const N = 1024;
export const ROUNDS = 10;
/** 第 r 轮结束后剩余人数（r = 0 表示开赛前） */
export const aliveAfter = (r: number) => N >> r;

const R = rng(20261008);
const shuffle = <T,>(a: T[]): T[] => {
  const b = a.slice();
  for (let i = b.length - 1; i > 0; i--) {
    const j = Math.floor(R() * (i + 1));
    [b[i], b[j]] = [b[j], b[i]];
  }
  return b;
};

/** order[0] 是冠军；名次 rank 越靠后越早出局 */
const order = shuffle([...Array(N).keys()]);
export const CHAMPION = order[0];
const rankOf = new Int32Array(N);
order.forEach((id, k) => (rankOf[id] = k));

/** 出局轮次：1—10；冠军为 0（从未出局） */
export const elimRound = new Int8Array(N);
for (let id = 0; id < N; id++) {
  const k = rankOf[id];
  elimRound[id] = k === 0 ? 0 : ROUNDS - Math.floor(Math.log2(k));
}

/** 每轮硬币结果：true = 正面 */
export const coinHeads: boolean[] = [...Array(ROUNDS)].map(() => R() < 0.5);

/** 第 r 轮（1 起）某人是否仍在场上 */
export const activeIn = (id: number, r: number) => elimRound[id] === 0 || elimRound[id] >= r;
/** 第 r 轮某人的猜测：猜错者正是本轮出局者，因此每轮恰好一半猜错 */
export const guessHeads = (id: number, r: number) => (elimRound[id] === r ? !coinHeads[r - 1] : coinHeads[r - 1]);

// ---------------------------------------------------------------- 站位

/** 向日葵排布间距（世界单位，1 ≈ 一人身位） */
export const SPACING = 0.6;
/** 场内幸存者与场外退出者之间的空隙 */
export const GAP = 2.4;
const PHI = Math.PI * (3 - Math.sqrt(5));
const innerSlot = (k: number): [number, number] => {
  const r = SPACING * Math.sqrt(k);
  return [r * Math.cos(k * PHI), r * Math.sin(k * PHI)];
};
const outerSlot = (k: number): [number, number] => {
  const r = SPACING * Math.sqrt(k) + GAP;
  return [r * Math.cos(k * PHI), r * Math.sin(k * PHI)];
};
/** 第 r 轮后幸存者所占圆盘半径 */
export const survivorRadius = (r: number) => SPACING * Math.sqrt(Math.max(aliveAfter(r) - 1, 0));
export const WORLD_RADIUS = SPACING * Math.sqrt(N - 1) + GAP;

/** 贪心最近空位分配：让每个人走最近的路，避免整片人群互相穿插 */
const assign = (ids: number[], from: Float32Array, slots: [number, number][], out: Float32Array, outward: boolean) => {
  const taken = new Uint8Array(slots.length);
  const sorted = ids.slice().sort((a, b) => {
    const da = Math.hypot(from[2 * a], from[2 * a + 1]);
    const db = Math.hypot(from[2 * b], from[2 * b + 1]);
    return outward ? db - da : da - db;
  });
  for (const id of sorted) {
    const x = from[2 * id];
    const y = from[2 * id + 1];
    let best = -1;
    let bd = Infinity;
    for (let k = 0; k < slots.length; k++) {
      if (taken[k]) continue;
      const d = (slots[k][0] - x) ** 2 + (slots[k][1] - y) ** 2;
      if (d < bd) {
        bd = d;
        best = k;
      }
    }
    taken[best] = 1;
    out[2 * id] = slots[best][0];
    out[2 * id + 1] = slots[best][1];
  }
};

/** pos[r]：第 r 轮结束后每个人的位置；pos[0] 为开赛时 32×32 方阵 */
export const pos: Float32Array[] = [];
{
  const grid = new Float32Array(2 * N);
  const cells = shuffle([...Array(N).keys()]);
  for (let id = 0; id < N; id++) {
    const c = cells[id];
    grid[2 * id] = (c % 32) - 15.5;
    grid[2 * id + 1] = Math.floor(c / 32) - 15.5;
  }
  pos.push(grid);
  for (let r = 1; r <= ROUNDS; r++) {
    const prev = pos[r - 1];
    const next = prev.slice();
    const survivors: number[] = [];
    const losers: number[] = [];
    for (let id = 0; id < N; id++) {
      if (!activeIn(id, r)) continue;
      (elimRound[id] === r ? losers : survivors).push(id);
    }
    const n = aliveAfter(r);
    assign(survivors, prev, [...Array(n).keys()].map(innerSlot), next, false);
    assign(losers, prev, [...Array(n).keys()].map((k) => outerSlot(n + k)), next, true);
    pos.push(next);
  }
}

// ---------------------------------------------------------------- 按时间求状态

const ROUND_T = TL.events.rounds;
/** 一轮内各阶段占比：亮出猜测 → 抛硬币 → 揭晓（猜错者变灰、计数变化） → 退场与收拢 */
export const PHASE = { guess: [0.0, 0.14], flip: [0.12, 0.45], result: 0.5, move: [0.56, 0.96] } as const;

/** 第 r 轮揭晓时刻（秒） */
export const resultTime = (r: number) => ROUND_T[r - 1][0] + PHASE.result * ROUND_T[r - 1][1];

/** t 时刻已揭晓的轮数（0—10） */
export const roundsDone = (t: number) => {
  let k = 0;
  for (let r = 1; r <= ROUNDS; r++) if (t >= resultTime(r)) k = r;
  return k;
};

/** t 时刻正在进行（或最近开始）的轮次，开赛前为 0 */
export const currentRound = (t: number) => {
  let k = 0;
  for (let r = 1; r <= ROUNDS; r++) if (t >= ROUND_T[r - 1][0]) k = r;
  return k;
};

/** t 时刻场上剩余人数：与灰色人数严格同步（同一个揭晓时刻） */
export const remainingAt = (t: number) => aliveAfter(roundsDone(t));
