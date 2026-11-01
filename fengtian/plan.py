"""读取 fengtian/PLAN.md 里各讲的文案代码块：load("02") -> dict(TITLE, KEY, CONCEPT, TAGS, COVER_TITLE, LINES, LINE_MOOD, PINYIN, SCREENS_DRAFT)。"""
import re
from pathlib import Path

PLAN = Path(__file__).with_name("PLAN.md")


def load(nn):
    s = PLAN.read_text(encoding="utf-8")
    m = re.search(rf"^### {nn} .*?^```python\n(.*?)^```", s, re.S | re.M)
    if not m:
        raise KeyError(nn)
    ns = {}
    exec(m.group(1), ns)
    return {k: v for k, v in ns.items() if not k.startswith("__")}


if __name__ == "__main__":
    import sys
    from engine import audio
    from fengtian import voice

    for nn in sys.argv[1:]:
        p = load(nn)
        print(f"== {nn} {p['TITLE']}", flush=True)
        xs = voice.synthesize(p["LINES"], p["LINE_MOOD"], p["PINYIN"], log=sys.stdout)
        print(f"== {nn} done {sum(len(x) for x in xs) / audio.SR:.1f}s", flush=True)
