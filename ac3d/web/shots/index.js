// 镜头注册：名字与 storyboard.json 的 shots[].name 一致。
import { THREE, makeCamera } from '../engine.js';
import { hook } from './s01_hook.js';
import { boat } from './s02_boat.js';
import { seep } from './s03_seep.js';
import { pump, off, restart } from './s04_06_pump.js';
import { balance, jiangsu, threshold } from './s07_09_evidence.js';
import { longaway, toggle, surge, fixed, conclusion, credits } from './s10_15_end.js';

function todo() {
  return { scene: new THREE.Scene(), camera: makeCamera(40), update() {} };
}

export const SHOT_FACTORIES = {
  hook,
  boat, seep, pump, off, restart, balance, jiangsu, threshold,
  longaway, toggle, surge, fixed, conclusion, credits,
};
