"""逐镜导出静帧用于检查：python3 make_stills.py 04 [秒数偏移]"""
import importlib, os, sys
from explainer.engine import still

MODS = {"04": "ep04_availability", "05": "ep05_base_rate", "06": "ep06_small_numbers",
        "07": "ep07_regression", "08": "ep08_correlation"}

if __name__ == "__main__":
    k = sys.argv[1]
    off = float(sys.argv[2]) if len(sys.argv) > 2 else 1.6
    ep = importlib.import_module("explainer." + MODS[k]).build()
    print(f"总时长 {ep.total:.1f}s  字数 {ep.chars()}  镜头 {len(ep.shots)}")
    S = "out/stills/"
    os.makedirs(S, exist_ok=True)
    for i, s in enumerate(ep.shots):
        T = min(s.start + off, s.end - 0.05)
        still(ep, T, f"{S}s{k}_{i:02d}.png")
        print(i, f"{s.start:.1f}-{s.end:.1f}", s.tag)
