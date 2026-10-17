// 自检：任一时刻 计数 = 未变灰人数；冠军始终是同一人；每轮恰好淘汰一半
import { CHAMPION, N, ROUNDS, aliveAfter, elimRound, pos, remainingAt, roundsDone } from "../src/data";
import { TL } from "../src/timeline";
import { isOut } from "../src/world";

let errors = 0;
for (let r = 1; r <= ROUNDS; r++) {
  let out = 0;
  for (let id = 0; id < N; id++) if (elimRound[id] === r) out++;
  if (out !== aliveAfter(r)) { console.error(`round ${r}: eliminated ${out}`); errors++; }
}
if (elimRound[CHAMPION] !== 0) errors++;
if (Math.hypot(pos[ROUNDS][2 * CHAMPION], pos[ROUNDS][2 * CHAMPION + 1]) > 1e-6) { console.error("champion not at origin"); errors++; }
let checked = 0;
for (let f = Math.ceil(TL.scenes.setup[0] * 30); f < TL.duration * 30; f++) {
  const t = f / 30;
  let alive = 0;
  for (let id = 0; id < N; id++) if (!isOut(id, t)) alive++;
  if (alive !== remainingAt(t)) { console.error(`frame ${f}: alive ${alive} != counter ${remainingAt(t)}`); errors++; }
  if (isOut(CHAMPION, t)) { console.error(`frame ${f}: champion out`); errors++; }
  checked++;
}
console.log(`checked ${checked} frames, rounds done at end = ${roundsDone(TL.duration)}, champion id = ${CHAMPION}, errors = ${errors}`);
process.exit(errors ? 1 : 0);
