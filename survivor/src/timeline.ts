import raw from "./generated/timeline.json";

/** 一句旁白：sub 中【】包住的是字幕重点词 */
export type Line = { id: string; speaker: "n" | "c"; text: string; sub: string; start: number; end: number };

type Timeline = {
  duration: number;
  voiced: boolean;
  scenes: Record<"hook" | "setup" | "rounds" | "guru" | "freeze" | "reveal" | "name" | "outro", [number, number]>;
  lines: Line[];
  events: {
    stamp: number;
    rules: number;
    rounds: [number, number][];
    podium: number;
    crown: number;
    crownLand: number;
    secrets: number[];
    absurd: number;
    freeze: number;
    viewfinder: number;
    zoom1: [number, number];
    zoom2: [number, number];
    caption: number;
    bubbles: number;
    phone: number;
    term: number;
    others: number;
    reference: number;
    compare: number;
    final: number;
  };
};

/** 由 scripts/build_audio.py 按真实配音时长生成的时间轴（单位：秒），画面与音轨共用 */
export const TL = raw as unknown as Timeline;
export const FPS = 30;
export const W = 1080;
export const H = 1920;
export const DURATION_FRAMES = Math.ceil(TL.duration * FPS);
export const lineById = (id: string): Line => {
  const l = TL.lines.find((x) => x.id === id);
  if (!l) throw new Error(`line not found: ${id}`);
  return l;
};
