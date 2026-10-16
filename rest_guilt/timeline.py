"""时间轴：叙事基准（未校准）与按原曲分析结果校准后的镜头边界、事件帧。

校准规则（只在拿到真实原曲分析后执行）：
1. 总长 = 选定原曲片段长度（87—93 秒），先按比例缩放基准边界；
2. 每条内部边界在 ±0.4 秒内寻找强度 ≥ 0.5 的起音，按 强度 - 距离惩罚 取最优，找不到保持原位；
3. 事件在其窗口内找起音：strong 需 ≥ 0.6，soft 需 ≥ 0.3（普通拍点也可）；找不到时
   strong 降为柔和动作并取消音效，soft 保持基准时刻、不加强调；
4. 每次移动后重算阅读窗口，不满足 story.read_budget 时回退该移动。
"""

import json
from dataclasses import asdict, dataclass, field

from . import story
from .story import FPS

ENTER = 0.4
EXIT = 0.4
FIRST_READY = 0.2
BOUNDARY_SHIFT = 0.4


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
    method: str = "叙事基准，未按原曲校准"
    confidence: str = "未确认"
    mix_note: str = ""


@dataclass
class Timeline:
    total_frames: int
    bounds: list[int]  # 16 个边界帧：bounds[i] 为第 i+1 镜开始
    events: list[EvT]
    beats: list[int] = field(default_factory=list)
    calibrated: bool = False
    music: dict = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    @property
    def total(self) -> float:
        return self.total_frames / FPS

    def shot_range(self, i: int) -> tuple[int, int]:
        """第 i 镜（1 起）的 [开始帧, 结束帧)。"""
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
        """返回不满足阅读预算的镜头说明；空列表表示全部满足。"""
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


def baseline() -> Timeline:
    """90.00 秒叙事基准：每镜 6 秒，事件取分镜中的基准时刻；全部标记为未确认。"""
    n = len(story.SHOTS)
    bounds = [round(i * story.SHOT_LEN * FPS) for i in range(n + 1)]
    evs = []
    for s in story.SHOTS:
        for e in s.events:
            evs.append(EvT(s.idx, e.name, bounds[s.idx - 1] + round(e.at * FPS), e.sfx, e.gain_db,
                           "none", "叙事基准（候选）"))
    return Timeline(bounds[-1], bounds, evs,
                    notes=["时间轴为 90.00 秒叙事基准，未读取原曲，所有音效位置均为候选，非卡点结果。"])


def calibrate(analysis: dict) -> Timeline:
    """按原曲分析结果生成校准时间轴。analysis 由 music.analyze 产生（时间相对选定片段起点）。"""
    L = analysis["segment"]["length"]
    total_frames = round(L * FPS)
    onsets = [(o["t"], o["strength"]) for o in analysis["onsets"]]
    scale = L / story.BASE_TOTAL
    n = len(story.SHOTS)
    bounds = [round(i * story.SHOT_LEN * scale * FPS) for i in range(n + 1)]
    bounds[-1] = total_frames
    tl = Timeline(total_frames, bounds, [], calibrated=True, music=analysis["summary"])
    if abs(L - story.BASE_TOTAL) > 1e-3:
        tl.notes.append(f"总长按原曲乐句改为 {L:.2f} 秒（{total_frames} 帧），基准边界按 {scale:.4f} 等比缩放。")
    if tl.check_reading():
        tl.notes.append("等比缩放后阅读窗口不足：" + "；".join(tl.check_reading()))

    for k in range(1, n):
        base = bounds[k] / FPS
        cands = [(st - abs(t - base) / BOUNDARY_SHIFT * 0.3, t, st) for t, st in onsets
                 if abs(t - base) <= BOUNDARY_SHIFT and st >= 0.5]
        if not cands:
            continue
        _, t, st = max(cands)
        old = bounds[k]
        bounds[k] = round(t * FPS)
        if bounds[k] <= bounds[k - 1] or bounds[k] >= bounds[k + 1] or tl.check_reading():
            bounds[k] = old
        else:
            tl.notes.append(f"边界 {k:02d}|{k + 1:02d} 由 {old / FPS:.2f}s 移至原曲起音 {t:.3f}s（强度 {st:.2f}）。")

    used: set[int] = set()
    for s in story.SHOTS:
        a = bounds[s.idx - 1]
        b = bounds[s.idx]
        shot_scale = (b - a) / (story.SHOT_LEN * FPS)
        prev_frame = a - 1
        for e in s.events:
            base_f = a + round(e.at * shot_scale * FPS)
            lo = a / FPS + e.win[0] * shot_scale
            hi = min(a / FPS + e.win[1] * shot_scale, b / FPS - 0.3)
            need = 0.6 if e.tier == "strong" else 0.3
            cands = [(st, t) for t, st in onsets if lo <= t <= hi and st >= need
                     and round(t * FPS) > prev_frame and round(t * FPS) not in used]
            ev = EvT(s.idx, e.name, base_f, e.sfx, e.gain_db, e.tier, "", method=analysis["method"])
            if cands:
                if e.tier == "strong":
                    st, t = max(cands)
                else:
                    st, t = min(cands, key=lambda c: abs(c[1] - base_f / FPS) - 0.3 * c[0])
                ev.frame = round(t * FPS)
                ev.music_time = round(analysis["segment"]["start"] + t, 4)
                ev.strength = round(st, 3)
                ev.source = "原曲起音"
                ev.confidence = "高" if st >= 0.6 else "中"
            else:
                ev.frame = max(base_f, prev_frame + 1)
                ev.mode = "soft"
                ev.source = "窗口内无合适重音，按基准时刻做柔和动作"
                ev.confidence = "未确认"
                if e.sfx and e.tier == "strong":
                    ev.mix_note = "未找到强重音，取消该处音效，不硬造强拍"
                    ev.sfx = None
                elif e.sfx:
                    ev.gain_db -= 4.0
                    ev.mix_note = "无对应起音，音效降 4 dB 作柔和点缀"
            prev_frame = ev.frame
            used.add(ev.frame)
            tl.events.append(ev)
    tl.bounds = bounds
    tl.beats = sorted({round(t * FPS) for t in analysis.get("beats", [])})
    bad = tl.check_reading()
    if bad:
        tl.notes.append("校准后仍有阅读窗口不足：" + "；".join(bad))
    return tl
