"""解析 chuanxilu/文案/epNN.md：按小节取出旁白句与行尾节奏标注（〔快｜留白0.5〕）。"""

import re
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SPEED = {"快": 1.25, "中": 1.18, "慢": 1.05}
DEFAULT_SPEED = 1.18
DEFAULT_PAUSE = 0.25

_SECTION = re.compile(r"^## 第 (\d+) 节 · (.+?)（", re.M)
_LINE = re.compile(r"^(.+?)\s*〔(.+?)〕\s*$")


@dataclass
class Sentence:
    text: str
    speed: float = DEFAULT_SPEED
    pause: float = DEFAULT_PAUSE
    tags: set[str] = field(default_factory=set)


@dataclass
class Section:
    index: int
    name: str
    sentences: list[Sentence]


def load(ep: str) -> list[Section]:
    """读取一讲文案；只取“**旁白**”到下一个“**”段落之间带节奏标注的行。缺小节或无旁白时抛 ValueError。"""
    md = (ROOT / "文案" / f"{ep}.md").read_text(encoding="utf-8")
    heads = list(_SECTION.finditer(md))
    if not heads:
        raise ValueError(f"{ep}: no sections")
    out = []
    for k, h in enumerate(heads):
        body = md[h.end(): heads[k + 1].start() if k + 1 < len(heads) else len(md)]
        part = body.split("**旁白**", 1)[1].split("**", 1)[0] if "**旁白**" in body else ""
        sents = []
        for raw in part.splitlines():
            m = _LINE.match(raw.strip())
            if not m:
                continue
            s = Sentence(m.group(1).strip())
            for tag in m.group(2).split("｜"):
                tag = tag.strip()
                if tag in SPEED:
                    s.speed = SPEED[tag]
                elif tag.startswith("留白"):
                    s.pause = float(tag[2:])
                else:
                    s.tags.add(tag)
            sents.append(s)
        if not sents:
            raise ValueError(f"{ep} section {h.group(1)}: no narration lines")
        out.append(Section(int(h.group(1)), h.group(2).strip(), sents))
    return out
