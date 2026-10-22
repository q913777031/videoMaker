"""CosyVoice 3 合成进程（在 CosyVoice 专用虚拟环境中运行，不 import 本仓库其他模块）。

python cosy_worker.py JOBS.json OUT_DIR VOICE_DIR INSTRUCT SEEDS
JOBS 为 [{"key", "text"}]；每句每个种子输出 OUT_DIR/<key>_<seed>.wav，已存在则跳过。
声音特征从 VOICE_DIR/prompt.wav + prompt.txt 提取一次后复用（零样本克隆，保留录音的语音 token）。
"""

import json
import os
import sys
import time
from pathlib import Path

COSY = Path(os.environ.get("COSYVOICE_DIR", "/home/user/tts_eval/CosyVoice"))
sys.path += [str(COSY), str(COSY / "third_party" / "Matcha-TTS")]

import torch  # noqa: E402
import torchaudio  # noqa: E402
from cosyvoice.cli.cosyvoice import AutoModel  # noqa: E402
from cosyvoice.utils.common import set_all_random_seed  # noqa: E402


def main():
    jobs = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    out, voice, instruct = Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4]
    seeds = [int(s) for s in sys.argv[5].split(",")]
    todo = [(j, s) for j in jobs for s in seeds if not (out / f"{j['key']}_{s}.wav").exists()]
    print(f"todo {len(todo)}", flush=True)
    if not todo:
        return
    torch.set_num_threads(os.cpu_count() or 4)
    m = AutoModel(model_dir=str(COSY / "pretrained_models" / "Fun-CosyVoice3-0.5B"))
    prompt = instruct + (voice / "prompt.txt").read_text(encoding="utf-8").strip()
    m.add_zero_shot_spk(prompt, str(voice / "prompt.wav"), "spk")
    out.mkdir(parents=True, exist_ok=True)
    for n, (j, seed) in enumerate(todo, 1):
        t = time.time()
        set_all_random_seed(seed)
        wav = torch.cat([x["tts_speech"] for x in m.inference_zero_shot(j["synth"], "", "", zero_shot_spk_id="spk",
                                                                       stream=False)], dim=1)
        tmp = out / f".{j['key']}_{seed}.wav"
        torchaudio.save(str(tmp), wav, m.sample_rate)
        tmp.rename(out / f"{j['key']}_{seed}.wav")
        print(f"done {n}/{len(todo)} {j['key']} seed={seed} {wav.shape[1] / m.sample_rate:.1f}s "
              f"in {time.time() - t:.0f}s", flush=True)


if __name__ == "__main__":
    main()
