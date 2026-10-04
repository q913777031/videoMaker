"""下载视频渲染所需的外部资源：字体、Fluent 3D Emoji、离线 TTS 模型。

已存在的文件会跳过；任一资源下载失败时以非零码退出并列出失败项。
用法：python3 fetch_assets.py
"""

import io
import sys
import tarfile
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FONT_DIR = ROOT / "assets" / "fonts"
EMOJI_DIR = ROOT / "assets" / "emoji"
MODEL_DIR = ROOT / "models"

FLUENT = "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/"
NOTO = "https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/OTF/SimplifiedChinese/"
SMILEY = "https://github.com/atelier-anchor/smiley-sans/releases/download/v2.0.1/smiley-sans-v2.0.1.zip"
KOKORO = "https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/kokoro-multi-lang-v1_0.tar.bz2"

# Fluent Emoji 目录名；带肤色的 emoji 使用 Default（黄色）版本
EMOJI = [
    "Hundred points", "Smiling face with tear", "Smiling face with smiling eyes", "Pensive face",
    "Face exhaling", "Dotted line face", "Face with spiral eyes", "Melting face", "Thinking face",
    "Astonished face", "Star-struck", "Relieved face", "Smiling face with sunglasses",
    "Grinning face with big eyes", "Books", "Graduation cap", "Office building", "Briefcase", "House",
    "Ring", "Chart increasing", "Check mark button", "Cross mark", "Mobile phone", "Alarm clock",
    "Crescent moon", "Thought balloon", "Speech balloon", "Memo", "Light bulb", "Sparkles",
    "Glowing star", "Sunrise", "Compass", "Battery", "Low battery", "High voltage",
    "Magnifying glass tilted left", "Test tube", "Steaming bowl", "Hot beverage", "Money with wings",
    "Balance scale", "Seedling", "Sunflower", "Rocket", "Red heart", "Star", "Party popper",
    "Classical building", "Stop sign", "Open book", "Artist palette", "Pencil", "Metro", "Fire",
    "Page facing up", "Spiral calendar", "National park", "Night with stars", "Bar chart",
    "Speaking head", "Bullseye", "Shushing face",
]
EMOJI_SKIN = [
    "Student", "Office worker", "Person in bed", "Person standing", "Teacher", "Cook", "Thumbs up",
    "Clapping hands", "Man office worker", "Person running", "Person raising hand",
    "Person in lotus position", "Backhand index pointing down", "Person tipping hand", "Person with crown",
]


def emoji_file(name: str) -> str:
    """Fluent 目录名到本地文件名的映射，例如 "Star-struck" → "star_struck.png"。"""
    return name.lower().replace(" ", "_").replace("-", "_") + ".png"


def get(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=600) as r:
        return r.read()


def fluent_urls(name: str, skin: bool) -> list[str]:
    """按 Fluent 仓库的命名习惯生成候选 URL（连字符有保留与替换两种写法）。"""
    folder = urllib.parse.quote(name)
    stems = {name.lower().replace(" ", "_"), name.lower().replace(" ", "_").replace("-", "_")}
    if skin:
        return [f"{FLUENT}{folder}/Default/3D/{s}_3d_default.png" for s in stems]
    return [f"{FLUENT}{folder}/3D/{s}_3d.png" for s in stems]


def fetch_emoji(failed: list[str]):
    EMOJI_DIR.mkdir(parents=True, exist_ok=True)
    for name, skin in [(n, False) for n in EMOJI] + [(n, True) for n in EMOJI_SKIN]:
        dst = EMOJI_DIR / emoji_file(name)
        if dst.exists():
            continue
        for url in fluent_urls(name, skin):
            try:
                dst.write_bytes(get(url))
                break
            except Exception:
                continue
        else:
            failed.append(f"emoji: {name}")


def fetch_fonts(failed: list[str]):
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    for f in ("NotoSansCJKsc-Black.otf", "NotoSansCJKsc-Bold.otf"):
        dst = FONT_DIR / f
        if not dst.exists():
            try:
                dst.write_bytes(get(NOTO + f))
            except Exception as ex:
                failed.append(f"font: {f} ({ex})")
    dst = FONT_DIR / "SmileySans-Oblique.ttf"
    if not dst.exists():
        try:
            with zipfile.ZipFile(io.BytesIO(get(SMILEY))) as z:
                dst.write_bytes(z.read("SmileySans-Oblique.ttf"))
        except Exception as ex:
            failed.append(f"font: SmileySans ({ex})")


def fetch_model(failed: list[str]):
    if (MODEL_DIR / "kokoro-multi-lang-v1_0" / "model.onnx").exists():
        return
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(KOKORO, timeout=1800) as r:
            with tarfile.open(fileobj=r, mode="r|bz2") as tar:
                tar.extractall(MODEL_DIR)
    except Exception as ex:
        failed.append(f"model: kokoro ({ex})")


def main():
    failed: list[str] = []
    fetch_fonts(failed)
    fetch_emoji(failed)
    fetch_model(failed)
    if failed:
        print("failed:\n  " + "\n  ".join(failed))
        sys.exit(1)
    print("all assets ready")


if __name__ == "__main__":
    main()
