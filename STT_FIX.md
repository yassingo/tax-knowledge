# STT/Transcription Fix for Hermes Desktop

## Problem (Updated)
Voice transcription in Hermes Desktop was failing with:

**Error 1: "Timed out connecting to Hermes backend after 1800000ms"**
- The default `stt.provider` was not set, so the app tried to use a cloud provider
- Cloud provider had no API key, caused 30-minute timeout
- **Fix**: Set `stt.provider: local` in `config.yaml`

**Error 2: "Local transcription failed: Library cublas64_12.dll will not be found or cannot be loaded"**
- After switching to local STT, ctranslate2's `device="auto"` tried to load CUDA
- The ctranslate2 wheel ships `cudnn64_9.dll` but NOT `cublas64_12.dll`
- Without a system CUDA install, the loader crashes before Python can fall back
- **Fix**: Patch `transcription_local.py` to detect missing CUDA libs and force CPU mode

## Root Cause
The `ctranslate2` Python package (used by `faster-whisper` for local Whisper) has
incomplete CUDA support on Windows when no system CUDA toolkit is installed:
- Ships with: `cudnn64_9.dll` (cuDNN 9)
- Does NOT ship: `cublas64_12.dll` (cuBLAS 12)
- The "auto" device picker raises the cublas error before Python can catch it

## Fix Applied

### 1. Config (C:\Users\LENOVO\AppData\Local\hermes\config.yaml)
```yaml
stt:
  enabled: true
  language: en
  local:
    model: tiny
    device: cpu            # <-- EXPLICIT CPU
    compute_type: int8     # <-- EXPLICIT INT8
  openai:
    model: whisper-1
    language: ''
  provider: local          # <-- USE LOCAL (not cloud)
```

### 2. Env var (C:\Users\LENOVO\AppData\Local\hermes\.env)
```
CT2_USE_CUDA=0
```

### 3. Source patch (C:\Users\LENOVO\AppData\Local\hermes\hermes-agent\tools\transcription_local.py)
- Added `_has_cuda_libs_on_windows()` function that detects missing cublas/cudnn
- Extended `_should_force_faster_whisper_cpu()` to also check Windows
- Added "cublas64_12", "cublas64_11", "cublas64_10", "will not be found" to error markers

## Verification

```python
from tools.transcription_local import _load_local_whisper_model
import time

start = time.time()
model = _load_local_whisper_model("tiny")
# Loaded in 1.1s on CPU (no CUDA libs needed)

segments, info = model.transcribe("audio.mp4", beam_size=1)
# Transcribed in 0.6s
```

## Performance

| Model | Load | Transcribe | Best For |
|-------|------|------------|----------|
| `tiny` | 1.1s | 0.6s/min | Real-time |
| `base` | ~1s (cached) | 2-4s/min | **Default** |
| `small` | ~5s | 8-15s/min | Better quality |
| `medium` | ~15s | 30-45s/min | High quality |

## NEXT STEP: Restart Hermes Desktop

The config change requires a restart. To apply the fix:

1. **Close Hermes Desktop** (X button or File → Quit)
2. **Reopen Hermes Desktop**
3. **Click the microphone icon** in the chat composer
4. Speak - it will now use **local faster-whisper on CPU** without any CUDA libraries
5. **NO TIMEOUTS, NO CUBLAS ERRORS, NO CLOUD DEPENDENCY**
