"""把频道片尾（brand/outro.mp4）接到视频末尾。

- 任意分辨率：片尾按源视频尺寸等比缩放、黑边补齐；无音轨的源视频自动补静音再拼接。
- 不重复：brand/outro_applied.json 记录已接过片尾的交付文件（相对路径 → 接好后的 sha1），文件未变就跳过。

用法：
    python3 -m brand.append videos/xitong            # 处理目录下所有 mp4（递归）
    python3 -m brand.append some.mp4 --force          # 指定文件，强制重接（源文件必须是没接过片尾的版本）
在代码里：from brand.append import append_outro; append_outro(path)   # 原地替换
"""

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTRO = ROOT / "brand" / "outro.mp4"
MANIFEST = ROOT / "brand" / "outro_applied.json"


def _sha1(p: Path) -> str:
    h = hashlib.sha1()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _probe(p: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height",
                          "-show_entries", "format=duration", "-of", "json", str(p)], capture_output=True, text=True)
    info = json.loads(out.stdout)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    has_audio = any(s["codec_type"] == "audio" for s in info["streams"])
    return dict(w=v["width"], h=v["height"], audio=has_audio, dur=float(info["format"]["duration"]))


def _load():
    return json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}


def _save(m):
    MANIFEST.write_text(json.dumps(m, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")


def _key(p: Path) -> str:
    try:
        return str(p.resolve().relative_to(ROOT))
    except ValueError:
        return str(p.resolve())


def already(p: Path) -> bool:
    m = _load()
    return m.get(_key(p)) == _sha1(p)


def append_outro(p, force: bool = False) -> bool:
    """原地给 p 接上片尾；已接过则跳过并返回 False。"""
    p = Path(p)
    if not force and already(p):
        return False
    src = _probe(p)
    w, h = src["w"], src["h"]
    vf_out = f"[1:v]scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:black,fps=30,setsar=1,format=yuv420p[v1]"
    inputs = ["-i", str(p), "-i", str(OUTRO)]
    if src["audio"]:
        a0 = "[0:a]aresample=44100,aformat=channel_layouts=stereo[a0]"
    else:
        inputs += ["-f", "lavfi", "-t", f"{src['dur']:.3f}", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"]
        a0 = "[2:a]aresample=44100[a0]"
    fc = ";".join([
        "[0:v]fps=30,setsar=1,format=yuv420p[v0]", a0, vf_out,
        "[1:a]aresample=44100,aformat=channel_layouts=stereo[a1]",
        "[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]",
    ])
    with tempfile.TemporaryDirectory(dir=p.parent) as tmp:
        out = Path(tmp) / p.name
        cmd = ["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
               "-c:v", "libx264", "-preset", "fast", "-crf", "21", "-maxrate", "12M", "-bufsize", "24M",
               "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)]
        subprocess.run(cmd, check=True)
        new = _probe(out)
        outro_dur = _probe(OUTRO)["dur"]
        if abs(new["dur"] - (src["dur"] + outro_dur)) > 0.25:
            raise RuntimeError(f"{p}: 拼接后时长 {new['dur']:.2f}s，应为 {src['dur'] + outro_dur:.2f}s")
        out.replace(p)
    m = _load()
    m[_key(p)] = _sha1(p)
    _save(m)
    return True


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    force = "--force" in sys.argv
    files = []
    for a in args:
        q = Path(a)
        files += sorted(q.rglob("*.mp4")) if q.is_dir() else [q]
    for f in files:
        done = append_outro(f, force)
        print(("接好 " if done else "已有 ") + str(f), flush=True)


if __name__ == "__main__":
    main()
