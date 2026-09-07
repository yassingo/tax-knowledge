"""Test faster-whisper local transcription - works without API."""
from faster_whisper import WhisperModel
import time
import sys

MODEL = sys.argv[1] if len(sys.argv) > 1 else "base"
AUDIO = r"C:\Users\LENOVO\Downloads\SaveClip.App_AQOHULIdGC7T8d6bkTya_oA0hiqoqqgNRFAl42kLQ1SjBJvepHQNN2BJgUb8FUd5ATd5YBMeW3p8ubR5dnheBxHrzxBmoJ6VvCYuC_I.mp4"

print(f"Loading faster-whisper model ({MODEL})...")
start = time.time()
model = WhisperModel(MODEL, device="cpu", compute_type="int8")
print(f"Loaded in {time.time()-start:.1f}s")

print(f"Transcribing {AUDIO}...")
start = time.time()
segments, info = model.transcribe(AUDIO, beam_size=1)
text = " ".join([s.text for s in segments])
elapsed = time.time() - start

print(f"\nTranscribed in {elapsed:.1f}s")
print(f"Language: {info.language}")
print(f"Text: {text}")
