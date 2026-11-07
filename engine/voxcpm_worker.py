"""VoxCPM 合成子进程（由 engine/audio.py 的 Narrator("vx_…") 启动，跑在 models/venv_tts 的 Python 里，主环境不必装 torch）。

协议：stdin 每行一个 JSON 请求 {"text", "prompt_wav", "prompt_text", "out", "seed", "cfg"?, "steps"?}
合成后把浮点 wav 写到 out，stdout 回一行 {"ok": true, "sr": 44100, "secs": 合成耗时} 或 {"ok": false, "err": "..."}。
启动时先回一行 {"ready": true, "load_secs": …}。

一次性准备（约 2GB，放 models/ 下，已被 gitignore；CPU 推理，float32）：
  models/VoxCPM1.5/：huggingface openbmb/VoxCPM1.5 的 config.json model.safetensors audiovae.pth
      tokenizer.json tokenizer_config.json special_tokens_map.json（Apache-2.0，可商用）
  models/voxcpm_pkg/voxcpm/：PyPI voxcpm==2.0.3 的 wheel 解压出的纯 Python 包（--no-deps；推理要的
      torch torchaudio transformers einops pydantic inflect wetext librosa soundfile 在 venv_tts 里都已有，
      降噪用的 modelscope/funasr 不装、不用）。
  同一套代码也能跑 openbmb/VoxCPM2（2B，约 5GB），把 VX_MODEL 指过去即可。
"""

import json
import os
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CODE = ROOT / "models" / "voxcpm_pkg"
CKPT = Path(os.environ.get("VX_MODEL", ROOT / "models" / "VoxCPM1.5"))
THREADS = int(os.environ.get("VX_THREADS", "4"))


def main():
    t0 = time.perf_counter()
    out_fd = os.dup(1)                         # 模型自己的 print 都改去 stderr，stdout 只留协议行
    os.dup2(2, 1)
    reply = os.fdopen(out_fd, "w", buffering=1)
    sys.path.insert(0, str(CODE))
    import numpy as np
    import soundfile as sf
    import torch

    torch.set_num_threads(THREADS)
    import torchaudio

    def _load(path, *a, **k):                 # 新版 torchaudio.load 要 torchcodec；只读本地 wav，用 soundfile 代替
        x, sr = sf.read(str(path), dtype="float32", always_2d=True)
        return torch.from_numpy(x.T.copy()), sr

    torchaudio.load = _load
    from voxcpm.core import VoxCPM

    tts = VoxCPM(str(CKPT), zipenhancer_model_path=None, enable_denoiser=False, optimize=False, device="cpu")
    sr = tts.tts_model.sample_rate
    reply.write(json.dumps({"ready": True, "load_secs": round(time.perf_counter() - t0, 1)}) + "\n")
    for line in sys.stdin:
        try:
            q = json.loads(line)
            seed = int(q.get("seed", 0))
            torch.manual_seed(seed)
            random.seed(seed)
            np.random.seed(seed % 2 ** 32)
            t = time.perf_counter()
            wav = tts.generate(text=q["text"], prompt_wav_path=q.get("prompt_wav"), prompt_text=q.get("prompt_text"),
                               cfg_value=float(q.get("cfg", 2.0)), inference_timesteps=int(q.get("steps", 10)),
                               normalize=False, denoise=False)
            sf.write(q["out"], np.asarray(wav, np.float32).reshape(-1), sr)
            reply.write(json.dumps({"ok": True, "sr": sr, "secs": round(time.perf_counter() - t, 2)}) + "\n")
        except Exception as e:                    # noqa: BLE001 —— 把错误回传给主进程
            reply.write(json.dumps({"ok": False, "err": repr(e)}) + "\n")


if __name__ == "__main__":
    main()
