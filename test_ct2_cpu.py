
import os
os.environ["CT2_USE_CUDA"] = "0"
try:
    from faster_whisper import WhisperModel
    print("Loading with CPU only...")
    model = WhisperModel("tiny", device="cpu", compute_type="int8")
    print("SUCCESS: model loaded on CPU")
    import time
    start = time.time()
    segments, info = model.transcribe(r"C:\Users\LENOVO\Downloads\SaveClip.App_AQOHULIdGC7T8d6bkTya_oA0hiqoqqgNRFAl42kLQ1SjBJvepHQNN2BJgUb8FUd5ATd5YBMeW3p8ubR5dnheBxHrzxBmoJ6VvCYuC_I.mp4", beam_size=1)
    text = " ".join([s.text for s in segments])
    print(f"Transcribed in {time.time()-start:.1f}s: {text}")
except Exception as e:
    print(f"FAILED: {e}")
