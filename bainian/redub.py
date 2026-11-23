"""《百年孤独》配音：python3 -m bainian.redub 01 02 …（须持有 TTS 锁，见 bainian/build.py 说明）

只合成并写入 .cache/tts，不渲染：正文按屏连读（fengtian.voice.synthesize，平淡叙述），再合成开场钩子句（逐字发声起点、
一顿一顿地切开，fengtian.hooks.prepare）。每讲的分屏取自分镜模块里的 SCREENS（静态解析，不执行模块），
模块还没写时取 PLAN.md 的 SCREENS_DRAFT（分镜须保持同样分组）。
"""
import ast
import sys
from pathlib import Path

from engine import audio
from fengtian import voice
from bainian import hooks as BH  # noqa: F401  注册本系列的开场钩子文字
from bainian import plan
from bainian import theme as BT

HERE = Path(__file__).parent


def screens(nn):
    f = next(HERE.glob(f"ep{nn}_*.py"), None)
    if f is not None:
        for node in ast.parse(f.read_text(encoding="utf-8")).body:
            if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "SCREENS" for t in node.targets):
                return [sc[0] for sc in ast.literal_eval(node.value)]
    return [sc[0] for sc in plan.load(nn)["SCREENS_DRAFT"]]


if __name__ == "__main__":
    from fengtian import hooks
    for nn in sys.argv[1:]:
        p = plan.load(nn)
        gs = [g for g in screens(nn) if g]
        print(f"== {nn} {len(p['LINES'])} 句 {len(gs)} 屏", flush=True)
        xs = voice.synthesize(p["LINES"], None, p["PINYIN"], groups=gs, log=sys.stdout)
        print(f"== {nn} lines {sum(len(x) for x in xs) / audio.SR:.1f}s", flush=True)
        hk = BT.get(nn)["hook"]
        h = hooks.prepare(hk)
        print(f"== {nn} hook {h['voice']} {h['dur']:.2f}s", flush=True)
        print(f"== {nn} done", flush=True)
