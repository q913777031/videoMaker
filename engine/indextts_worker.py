"""IndexTTS2 合成子进程（由 engine/audio.py 的 Narrator("ix2_…") 启动，跑在 models/venv_tts 里，主环境不必装 torch）。

协议：stdin 每行一个 JSON 请求
  {"text", "spk_wav", "out", "seed",
   "emo_alpha"?, "emo_vector"? [8 个数：喜 怒 哀 惧 厌恶 低落 惊讶 平静], "emo_text"?, "use_emo_text"?, "emo_wav"?,
   "gen"? {temperature, top_p, top_k, num_beams, ...}}
合成后把浮点 wav 写到 out，stdout 回一行 {"ok": true, "sr": 22050, "secs": 合成耗时, "emo_vector"?: 实际所用情绪向量} 或 {"ok": false, "err": "..."}。
启动时先回一行 {"ready": true, "load_secs": …}。

一次性准备（权重约 7.8GB，放 models/ 下，已被 gitignore；CPU 推理，不需要 GPU）：
  git clone --depth 1 https://github.com/index-tts/index-tts models/index-tts
  uv pip install --python models/venv_tts/bin/python json5 munch textstat      # 其余依赖 venv_tts 里已有
  从 huggingface 下载到 models/IndexTTS-2（直连不通时换 hf-mirror.com / ModelScope 同名仓库）：
      IndexTeam/IndexTTS-2：config.yaml bpe.model gpt.pth s2mel.pth feat1.pt feat2.pt wav2vec2bert_stats.pt
          LICENSE*.txt，qwen0.6bemo4-merge/（整个目录，文字描述情绪用）
      hf_cache/w2v-bert-2.0/：facebook/w2v-bert-2.0 的 config.json preprocessor_config.json model.safetensors
      hf_cache/semantic_codec_model.safetensors：amphion/MaskGCT 的 semantic_codec/model.safetensors
      hf_cache/campplus_cn_common.bin：funasr/campplus
      hf_cache/bigvgan/：nvidia/bigvgan_v2_22khz_80band_256x 的 config.json bigvgan_generator.pt
许可：bilibili 模型使用许可协议（models/IndexTTS-2/LICENSE_ZH.txt）。
"""

import json
import os
import random
import sys
import time
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CODE = ROOT / "models" / "index-tts"
CKPT = ROOT / "models" / "IndexTTS-2"
THREADS = int(os.environ.get("IX2_THREADS", "4"))


def _load():
    sys.path.insert(0, str(CODE))
    import transformers

    # modelscope 只被拿来调 AutoModelForCausalLM（加载本地 Qwen 情绪模型），换成 transformers 的同名类，省掉整个包。
    sys.modules.setdefault("modelscope", types.SimpleNamespace(AutoModelForCausalLM=transformers.AutoModelForCausalLM))
    import numpy as np
    import soundfile as sf
    import torch

    torch.set_num_threads(THREADS)
    from indextts.utils import front

    def _load_norm(self):                     # Linux 上默认要 WeTextProcessing（依赖 pynini，py3.13 装不上），改用同源的 wetext
        if self.zh_normalizer is not None and self.en_normalizer is not None:
            return
        from wetext import Normalizer

        self.zh_normalizer = Normalizer(remove_erhua=False, lang="zh", operator="tn")
        self.en_normalizer = Normalizer(lang="en", operator="tn")

    front.TextNormalizer.load = _load_norm
    # 推理只用到 dac.nn.quantize；跳过 dac 包和 dac.nn 的 __init__（它们引入训练用的 descript-audiotools）
    dac = CODE / "indextts" / "s2mel" / "dac"
    for name, path in (("indextts.s2mel.dac", dac), ("indextts.s2mel.dac.nn", dac / "nn")):
        m = types.ModuleType(name)
        m.__path__ = [str(path)]
        sys.modules[name] = m
    from indextts.infer_v2 import IndexTTS2

    h = CKPT / "hf_cache"
    aux = dict(w2v_bert=str(h / "w2v-bert-2.0"), semantic_codec=str(h / "semantic_codec_model.safetensors"),
               campplus=str(h / "campplus_cn_common.bin"), bigvgan=str(h / "bigvgan"))
    tts = IndexTTS2(cfg_path=str(CKPT / "config.yaml"), model_dir=str(CKPT), device="cpu", use_fp16=False,
                    use_qwen_emo=True, aux_paths=aux)
    return tts, torch, np, sf


def main():
    t0 = time.perf_counter()
    out_fd = os.dup(1)                         # 模型自己的 print 都改去 stderr，stdout 只留协议行
    os.dup2(2, 1)
    reply = os.fdopen(out_fd, "w", buffering=1)
    tts, torch, np, sf = _load()
    reply.write(json.dumps({"ready": True, "load_secs": round(time.perf_counter() - t0, 1)}) + "\n")
    for line in sys.stdin:
        try:
            q = json.loads(line)
            seed = int(q.get("seed", 0))
            torch.manual_seed(seed)
            random.seed(seed)
            np.random.seed(seed % 2 ** 32)
            kw = dict(emo_alpha=float(q.get("emo_alpha", 1.0)), use_random=False, verbose=False,
                      interval_silence=int(q.get("interval_silence", 200)))
            vec = q.get("emo_vector")
            if vec is None and (q.get("use_emo_text") or q.get("emo_text")):
                # 文字描述情绪 → Qwen 情绪模型给出 8 维向量（与 use_emo_text=True 走的是同一条路，这里先算出来好回报）
                vec = list(tts.qwen_emo.inference(q.get("emo_text") or q["text"]).values())
            if vec is not None:
                kw["emo_vector"] = [float(v) for v in vec]
            elif q.get("emo_wav"):
                kw["emo_audio_prompt"] = q["emo_wav"]
            kw.update(q.get("gen", {}))
            t = time.perf_counter()
            sr, data = tts.infer(q["spk_wav"], q["text"], None, **kw)
            sf.write(q["out"], np.asarray(data, np.float32).reshape(-1) / 32767.0, sr)
            r = {"ok": True, "sr": sr, "secs": round(time.perf_counter() - t, 2)}
            if vec is not None:
                r["emo_vector"] = [round(float(v), 4) for v in vec]
            reply.write(json.dumps(r) + "\n")
        except Exception as e:                    # noqa: BLE001 —— 把错误回传给主进程
            reply.write(json.dumps({"ok": False, "err": repr(e)}) + "\n")


if __name__ == "__main__":
    main()
