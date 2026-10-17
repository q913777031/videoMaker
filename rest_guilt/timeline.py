"""时间轴：按小节网格排镜头，事件以拍计并贴到原曲实测起音上。

校准规则（拿到真实原曲后）：
1. 由起音拟合恒定速度网格（拍长、首个小节强拍）；镜头切点 = 小节强拍（第 1 镜从第 0 帧开始，最后一镜延续到曲终）；
2. 事件的网格时刻 ±45 ms 内若有实测起音，吸附到该起音并记录强度；
   strong 事件需要强度 ≥ 0.6，否则降为柔和动作并取消音效；soft 事件无起音时降 4 dB；
3. 每拍、每个小节强拍都写入 beats / downbeats，供画面做逐拍的小动作；
4. 重算阅读窗口，不满足预算的写入 notes。
"""

import json
from dataclasses import asdict, dataclass, field

from . import story
from .story import FPS

ENTER = 0.4
EXIT = 0.4
FIRST_READY = 0.2
SNAP = 0.045


@dataclass
class EvT:
    shot: int
    name: str
    frame: int
    sfx: str | None
    gain_db: float
    mode: str  # strong / soft / none
    source: str
    music_time: float | None = None
    strength: float | None = None
    method: str = "名义网格，未按原曲校准"
    confidence: str = "未确认"
    mix_note: str = ""
    grid_time: float | None = None


@dataclass
class Timeline:
    total_frames: int
    bounds: list[int]
    events: list[EvT]
    beats: list[int] = field(default_factory=list)
    downbeats: list[int] = field(default_factory=list)
    beat_len: float = story.NOMINAL_BEAT
    calibrated: bool = False
    music: dict = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    @property
    def total(self) -> float:
        return self.total_frames / FPS

    def shot_range(self, i: int) -> tuple[int, int]:
        return self.bounds[i - 1], self.bounds[i]

    def ev(self, shot: int, name: str) -> float:
        """事件相对所在镜头开始的秒数。"""
        for e in self.events:
            if e.shot == shot and e.name == name:
                return (e.frame - self.bounds[shot - 1]) / FPS
        raise KeyError(f"{shot}:{name}")

    def read_window(self, i: int) -> tuple[float, float]:
        a, b = self.shot_range(i)
        lead = FIRST_READY if i == 1 else ENTER
        return a / FPS + lead, b / FPS - EXIT

    def check_reading(self) -> list[str]:
        bad = []
        for s in story.SHOTS:
            a, b = self.read_window(s.idx)
            if b - a + 1e-6 < story.read_budget(s):
                bad.append(f"镜头{s.idx:02d} 稳定窗 {b - a:.2f}s < 预算 {story.read_budget(s):.2f}s")
        return bad

    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, ensure_ascii=False, indent=1)

    @staticmethod
    def load(path) -> "Timeline":
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        d["events"] = [EvT(**e) for e in d["events"]]
        return Timeline(**d)


def _build(T: float, first_down: float, total: float, onsets: list | None, method: str) -> Timeline:
    total_frames = round(total * FPS)
    bar = 4 * T
    starts, acc = [], 0
    for s in story.SHOTS:
        starts.append(first_down + acc * bar)
        acc += s.bars
    bounds = [0] + [round(t * FPS) for t in starts[1:]] + [total_frames]
    tl = Timeline(total_frames, bounds, [], beat_len=T, calibrated=onsets is not None)
    n_beats = int((total - first_down) / T) + 1
    grid = [first_down + k * T for k in range(n_beats) if first_down + k * T < total]
    tl.beats = [round(t * FPS) for t in grid]
    tl.downbeats = [round(t * FPS) for k, t in enumerate(grid) if k % 4 == 0]
    for s, st0 in zip(story.SHOTS, starts):
        for e in s.events:
            gt = st0 + e.beat * T
            ev = EvT(s.idx, e.name, round(gt * FPS), e.sfx, e.gain_db, e.tier, "", method=method,
                     grid_time=round(gt, 4))
            if onsets is None:
                ev.mode, ev.source = "none", "名义网格（候选）"
            else:
                near = [o for o in onsets if abs(o["t"] - gt) <= SNAP]
                o = max(near, key=lambda o: o["strength"] - abs(o["t"] - gt) * 5) if near else None
                need = 0.6 if e.tier == "strong" else 0.0
                if e.tier == "strong" and not (o and o["strength"] >= need):
                    # 强拍上没有强重音：顺延到 3 拍内落在八分音符网格上的最强起音
                    later = [q for q in onsets if gt < q["t"] <= gt + 3 * T + SNAP and q["strength"] >= need
                             and abs(((q["t"] - gt) / (T / 2) - round((q["t"] - gt) / (T / 2))) * T / 2) < 0.025]
                    if later:
                        o = max(later, key=lambda q: q["strength"])
                        ev.mix_note = f"强拍处无强重音，撞击顺延 {(o['t'] - gt) / T:.1f} 拍到原曲强起音"
                if o and o["strength"] >= max(need, 0.15):
                    ev.frame = round(o["t"] * FPS)
                    ev.music_time = round(o["t"], 4)
                    ev.strength = o["strength"]
                    ev.source = "小节网格 + 吸附原曲起音"
                    ev.confidence = "高" if o["strength"] >= 0.6 else "中"
                else:
                    ev.mode = "soft"
                    ev.source = "网格位置附近无足够起音，改为柔和动作"
                    if e.sfx and e.tier == "strong":
                        ev.sfx = None
                        ev.mix_note = "未找到强重音，取消该处音效，不硬造强拍"
                    elif e.sfx:
                        ev.gain_db -= 4.0
                        ev.mix_note = "该拍无明显起音，音效降 4 dB"
            ev.frame = max(ev.frame, bounds[s.idx - 1])
            tl.events.append(ev)
    bad = tl.check_reading()
    if bad:
        tl.notes.append("阅读窗口不足：" + "；".join(bad))
    return tl


def baseline(total: float = story.BASE_TOTAL) -> Timeline:
    """无原曲时的名义网格（拍长取 story.NOMINAL_BEAT），所有事件标记为未确认。"""
    tl = _build(story.NOMINAL_BEAT, 0.1, total, None, "名义网格，未按原曲校准")
    tl.notes.append("未读取原曲：镜头与事件按名义节拍网格排布，非卡点结果。")
    return tl


def calibrate(analysis: dict) -> Timeline:
    g = analysis["grid"]
    L = analysis["segment"]["length"]
    tl = _build(g["beat"], g["first_downbeat"], L,
                analysis["onsets"], analysis["method"] + "；恒定速度网格拟合")
    tl.music = analysis["summary"]
    used = sum(s.bars for s in story.SHOTS)
    tl.notes.append(f"节拍网格：{g['bpm']} BPM（拍长 {g['beat'] * 1000:.1f} ms），首个小节强拍 {g['first_downbeat']:.3f} s；"
                    f"强起音落在拍上 {g['strong_on_beat']}、落在八分音符上 {g['strong_on_eighth']}，中位偏差 {g['median_abs_dev_ms']} ms。"
                    f"镜头 1—{len(story.SHOTS) - 1} 共 {used} 小节，切点全部在小节强拍。")
    return tl
