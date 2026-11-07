"""整季重配旁白（平淡叙述、同屏连读）：python3 -m fengtian.redub 01 02 …

只合成并写入 .cache/tts，不渲染。每讲的分屏取自分镜模块里的 SCREENS（静态解析，不执行模块）。
"""
import ast
import sys
from pathlib import Path

from engine import audio
from fengtian import plan, voice

HERE = Path(__file__).parent


def screens(nn):
    f = next(HERE.glob(f"ep{nn}_*.py"))
    for node in ast.parse(f.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "SCREENS" for t in node.targets):
            return [sc[0] for sc in ast.literal_eval(node.value)]
    raise KeyError(f"{f.name} 没有 SCREENS")


def lines(nn):
    if nn == "01":
        f = HERE / "ep01_andon.py"
        tree = ast.parse(f.read_text(encoding="utf-8"))
        val = {t.id: n.value for n in tree.body if isinstance(n, ast.Assign) for t in n.targets if hasattr(t, "id")}
        return ast.literal_eval(val["LINES"]), ast.literal_eval(val["PINYIN"])
    p = plan.load(nn)
    return p["LINES"], p["PINYIN"]


if __name__ == "__main__":
    for nn in sys.argv[1:]:
        ls, py = lines(nn)
        gs = [g for g in screens(nn) if g]
        print(f"== {nn} {len(ls)} 句 {len(gs)} 屏", flush=True)
        xs = voice.synthesize(ls, None, py, groups=gs, log=sys.stdout)
        print(f"== {nn} done {sum(len(x) for x in xs) / audio.SR:.1f}s", flush=True)
