/** timeline.json 的结构（由 kepu/three.py 导出；时间均为视频绝对秒，cue 为镜头内秒）。 */
export type ShotT = {no: number; start: number; dur: number; lines: string[]; tag: string; credit: boolean; keys?: string[]; cue: Record<string, number>};
export type SubT = {shot: number; k: number; start: number; end: number; why: string};
export type HitT = {shot: number; key: string; t: number; soft: boolean};
export type LayoutT = {
  name: string; text_size: number; text_line_gap: number; text_x: number; text_y: number; text_align: string;
  ref_size: number; tag_size: number; tag_x: number; tag_y: number;
};
export type KepuProps = {
  slug: string; fps: number; total: number; width: number; height: number; layout: LayoutT;
  shots: ShotT[]; subshots: SubT[]; hits: HitT[]; audio: string;
  cover: {title: string[]; subtitle: string; at?: number} | null;
};

/** 场景参数：t 子镜头内秒、d 子镜头时长、T 镜头内秒、D 镜头时长、cue 镜头内撞击时刻、k 子镜头序号、G 全片秒。 */
export type SP = {t: number; d: number; T: number; D: number; cue: Record<string, number>; k: number; G: number};
export type SceneFn = (p: SP) => JSX.Element;
