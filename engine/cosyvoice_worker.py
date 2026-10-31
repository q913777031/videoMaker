"""CosyVoice3 合成子进程（由 engine/audio.py 的 Narrator 启动，跑在 models/venv_tts 里，主环境不必装 torch）。

协议：stdin 每行一个 JSON 请求 {"text", "mode": "zs"|"ins", "prompt_wav", "prompt_text", "instruct", "speed", "seed", "out"}，
合成后把浮点 wav 写到 out，stdout 回一行 {"ok": true, "sr": 24000} 或 {"ok": false, "err": "..."}。

一次性准备（模型约 4.4GB，放 models/ 下，已被 gitignore）：
  python3 -m venv --system-site-packages models/venv_tts
  models/venv_tts/bin/pip install "transformers==4.52.1" "huggingface-hub<1.0" "diffusers==0.29.0" hyperpyyaml conformer \
      hydra-core inflect x-transformers openai-whisper lightning wetext rich gdown wget pyworld pyarrow
  git clone --depth 1 https://github.com/FunAudioLLM/CosyVoice models/CosyVoice && (cd models/CosyVoice && git submodule update --init --depth 1)
  从 huggingface FunAudioLLM/Fun-CosyVoice3-0.5B-2512 下载到 models/Fun-CosyVoice3-0.5B-2512：
      cosyvoice3.yaml campplus.onnx hift.pt flow.pt speech_tokenizer_v3.onnx CosyVoice-BlankEN/(除 model.safetensors 外的小文件)，
      以及 llm.rl.pt（存成 llm.pt；RL 版读字错误率更低）。
"""

import json
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CODE = ROOT / "models" / "CosyVoice"
CKPT = ROOT / "models" / "Fun-CosyVoice3-0.5B-2512"


def _load():
    sys.path[:0] = [str(CODE), str(CODE / "third_party" / "Matcha-TTS")]
    sys.modules.setdefault("modelscope", types.SimpleNamespace(snapshot_download=lambda *a, **k: a[0]))
    import soundfile as sf
    import torch
    import torchaudio

    def _ta_load(path, *a, **k):              # 新版 torchaudio 读写依赖 torchcodec，这里换成 soundfile
        x, sr = sf.read(str(path), dtype="float32", always_2d=True)
        return torch.from_numpy(x.T.copy()), sr

    torchaudio.load = _ta_load
    torch.set_num_threads(4)
    from transformers import Qwen2Config, Qwen2ForCausalLM

    import cosyvoice.llm.llm as L

    class _Q(Qwen2ForCausalLM):
        @classmethod
        def from_pretrained(cls, p, *a, **k):   # 只按 config 建结构，权重随后由 llm.pt 全量覆盖（省下 1GB 基座下载）
            return Qwen2ForCausalLM(Qwen2Config.from_pretrained(p))

    L.Qwen2ForCausalLM = _Q
    from cosyvoice.cli.cosyvoice import CosyVoice3

    return CosyVoice3(str(CKPT)), torch, sf


def main():
    cv, torch, sf = _load()
    print(json.dumps({"ready": True}), flush=True)
    for line in sys.stdin:
        try:
            q = json.loads(line)
            torch.manual_seed(q.get("seed", 0))
            if q["mode"] == "ins":
                g = cv.inference_instruct2(q["text"], q["instruct"], q["prompt_wav"], stream=False, speed=q.get("speed", 1.0))
            else:
                g = cv.inference_zero_shot(q["text"], "You are a helpful assistant.<|endofprompt|>" + q["prompt_text"],
                                           q["prompt_wav"], stream=False, speed=q.get("speed", 1.0))
            w = torch.cat([j["tts_speech"] for j in g], 1)[0].numpy()
            sf.write(q["out"], w, cv.sample_rate)
            print(json.dumps({"ok": True, "sr": cv.sample_rate}), flush=True)
        except Exception as e:                    # noqa: BLE001 —— 把错误回传给主进程
            print(json.dumps({"ok": False, "err": repr(e)}), flush=True)


if __name__ == "__main__":
    main()
