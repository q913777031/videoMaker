"""读取 zizhi/PLAN.md 里各讲的文案代码块：load("01") -> dict(NO, KEY, CONCEPT, TITLE, TAGS, COVER_TITLE, LINES, LINE_MOOD, PINYIN, SCREENS_DRAFT)。"""
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
