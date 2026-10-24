"""真人录制的句子：把上传的录音按语音识别自动对到文案句子上，存为 voices/<音色>/lines/<句子哈希>.wav，成片直接使用（不再合成）。

python3 -m chuanxilu.recorded ep01 --script [wym|me_new]   # 打印该音色的录音稿（编号 + 句子）
python3 -m chuanxilu.recorded ep01 <上传目录> [--voice wym|me_new]   # 识别、匹配、入库，打印匹配表

匹配规则：每个录音文件转 16k 单声道做识别，与候选句子逐一比对拼音错字率，取最低者；错字率 > 0.35 的文件标为“未匹配”，不入库。
一个文件里只能录一句；同一句多条录音时保留错字率最低的一条。
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from engine import audio, gfx

from . import script, voice

AUDIO_EXT = {".wav", ".m4a", ".mp3", ".aac", ".flac", ".ogg", ".mp4"}


def candidates(ep: str, v: str) -> list[str]:
    out = []
    for sec in script.load(ep):
        for s in sec.sentences:
            if (voice.role_voice(s.tags) or voice.VOICE) == v:
                out.append(gfx.plain(s.text))
    return list(dict.fromkeys(out))


def print_script(ep: str, v: str):
    for i, t in enumerate(candidates(ep, v), 1):
        print(f"{i:02d}. {t}")


def ingest(ep: str, src: Path, v: str):
    texts = candidates(ep, v)
    pys = {t: voice._pinyin(t) for t in texts}
    asr = voice._asr()
    best: dict[str, tuple[float, Path, str]] = {}
    unmatched = []
    for f in sorted(p for p in src.iterdir() if p.suffix.lower() in AUDIO_EXT):
        with tempfile.TemporaryDirectory() as tmp:
            wav = Path(tmp) / "x.wav"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(f), "-ac", "1", "-ar", "16000", str(wav)], check=True)
            y = voice._load16k(wav)
        s = asr.create_stream()
        s.accept_waveform(16000, y)
        asr.decode_stream(s)
        hyp = voice._pinyin(s.result.text)
        t, e = min(((t, voice._cer(pys[t], hyp)) for t in texts), key=lambda x: x[1])
        if e > 0.35:
            unmatched.append((f.name, s.result.text))
            continue
        if t not in best or e < best[t][0]:
            best[t] = (e, f, s.result.text)
    dst = audio.VOICE_DIR / v / "lines"
    dst.mkdir(parents=True, exist_ok=True)
    for t, (e, f, hyp) in best.items():
        out = dst / f"{audio.cosy_key(t)}.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(f), "-ac", "1", "-ar", str(audio.SR), str(out)], check=True)
        print(f"[{e:.2f}] {f.name} → {t}\n        识别：{hyp}")
    print(f"\n入库 {len(best)} 句 → {dst}")
    missing = [t for t in texts if t not in best]
    if missing:
        print(f"未录（{len(missing)} 句，将用合成）：")
        for t in missing:
            print("  -", t)
    if unmatched:
        print("未匹配到任何句子的文件：")
        for name, hyp in unmatched:
            print(f"  - {name}  识别：{hyp}")


if __name__ == "__main__":
    ep = sys.argv[1]
    if "--script" in sys.argv:
        i = sys.argv.index("--script")
        print_script(ep, sys.argv[i + 1] if i + 1 < len(sys.argv) else "wym")
    else:
        v = sys.argv[sys.argv.index("--voice") + 1] if "--voice" in sys.argv else "wym"
        ingest(ep, Path(sys.argv[2]), v)
