#!/bin/bash
# 搭建 CosyVoice 3 独立环境（Python 3.10，CPU 版 PyTorch）与语音识别模型；新容器里运行一次即可。
# 需要网络放行：huggingface.co、download.pytorch.org、github.com、pypi.org
set -euo pipefail
BASE=${TTS_EVAL:-/home/user/tts_eval}
REPO=$(cd "$(dirname "$0")/.." && pwd)
mkdir -p "$BASE" && cd "$BASE"
[ -d CosyVoice ] || git clone --recursive https://github.com/FunAudioLLM/CosyVoice.git
[ -d cv ] || uv venv -p 3.10 cv
uv pip install -p cv/bin/python torch==2.3.1 torchaudio==2.3.1 --index-url https://download.pytorch.org/whl/cpu
grep -v -E "^--|deepspeed|onnxruntime-gpu|tensorrt|torch|gradio|fastapi|uvicorn|grpcio|tensorboard|openai-whisper|^#" \
  CosyVoice/requirements.txt > cv_req.txt
echo "onnxruntime==1.18.0" >> cv_req.txt
uv pip install -p cv/bin/python -r cv_req.txt huggingface_hub lightning==2.2.4 "setuptools<70" wheel
uv pip install -p cv/bin/python --no-build-isolation openai-whisper==20231117
cv/bin/python - <<'EOF'
from huggingface_hub import snapshot_download
snapshot_download("FunAudioLLM/Fun-CosyVoice3-0.5B-2512", local_dir="CosyVoice/pretrained_models/Fun-CosyVoice3-0.5B",
                  ignore_patterns=["llm.rl.pt", "flow.decoder.estimator.fp32.onnx", "speech_tokenizer_v3.batch.onnx"])
EOF
ASR=sherpa-onnx-paraformer-zh-small-2024-03-09
if [ ! -d "$REPO/models/$ASR" ]; then
  mkdir -p "$REPO/models"
  curl -sSL "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/$ASR.tar.bz2" | tar xj -C "$REPO/models"
fi
pip install -q pypinyin
echo "CosyVoice ready: COSY_PYTHON=$BASE/cv/bin/python COSYVOICE_DIR=$BASE/CosyVoice"
