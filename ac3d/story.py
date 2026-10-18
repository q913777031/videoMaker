"""分镜数据：从 storyboard.json 读取（镜头、字幕、按拍动作与音效、出处），构建脚本只读这里。

storyboard.json 结构：
  title / title_short / publish_title / hashtags / series / file_name / refs[] / notes[]
  shots[]: name, bars, tag, transition("ink"|"cut"), scene, camera,
           captions[]: {at, out, text, note}（镜头内拍数；out 为 null 表示到镜头结束）
           cues[]: {name, beat, action, sfx, gain}（sfx 为 null 表示只有画面动作）
"""

import json
from dataclasses import dataclass, field
from pathlib import Path



@dataclass
class Cap:
    at: float
    out: float | None
    text: str
    note: str | None = None


@dataclass
class Shot:
    name: str
    bars: int
    tag: str
    transition: str = "cut"
    note: str = ""
    cues: dict = field(default_factory=dict)       # 动作名 → 镜头内拍数
    sfx: list = field(default_factory=list)        # (动作名, 音色, 增益, 说明)
    caps: list = field(default_factory=list)


def _shot(d: dict) -> Shot:
    cues = {c["name"]: c["beat"] for c in d["cues"]}
    sfx = [(c["name"], c["sfx"], c.get("gain", 1.0), c["action"]) for c in d["cues"] if c.get("sfx")]
    caps = [Cap(c["at"], c.get("out"), c["text"], c.get("note")) for c in d["captions"]]
    return Shot(d["name"], d["bars"], d["tag"], d.get("transition", "cut"), d.get("scene", ""), cues, sfx, caps)


def load(path: Path) -> dict:
    """读取一份 storyboard.json，返回与本模块同名的常量字典（供其他短片复用）。"""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return dict(DATA=data, SERIES=data.get("series", "生活里的物理"), TITLE=data["title"], TITLE_SHORT=data["title_short"],
                PUBLISH_TITLE=data["publish_title"], HASHTAGS=data["hashtags"], FILE_NAME=data.get("file_name", "video"),
                REFS=data.get("refs", []), REFS_SHORT=data.get("refs_short", data.get("refs", [])), NOTES=data.get("notes", []),
                SHOTS=[_shot(x) for x in data["shots"]])


globals().update(load(Path(__file__).resolve().parent / "storyboard.json"))
