
import sys
import os
sys.path.insert(0, r"C:\Users\LENOVO\AppData\Local\hermes\hermes-agent")
from tools.transcription_local import _load_local_whisper_model
import time

print("=== Local Whisper Test (CPU mode, no CUDA libs) ===")
start = time.time()
model = _load_local_whisper_model("tiny")
print(f"Loaded in {time.time()-start:.1f}s")

audio = r"C:\Users\LENOVO\Downloads\SaveClip.App_AQOHULIdGC7T8d6bkTya_oA0hiqoqqgNRFAl42kLQ1SjBJvepHQNN2BJgUb8FUd5ATd5YBMeW3p8ubR5dnheBxHrzxBmoJ6VvCYuC_I.mp4"
print(f"\nTranscribing: {os.path.basename(audio)}...")
start = time.time()
segments, info = model.transcribe(audio, beam_size=1)
text = " ".join([s.text for s in segments])
print(f"Transcribed in {time.time()-start:.1f}s")
print(f"Language: {info.language}")
print(f"Text: {text}")
print("\n[SUCCESS] Local transcription works without CUDA libs!")
