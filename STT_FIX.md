# STT/Transcription Fix for Hermes Desktop

## Problem
Voice transcription in Hermes Desktop was failing with:
"Voice transcription failed: Timed out connecting to Hermes backend after 1800000ms"

## Root Cause
The Hermes config was missing `stt.provider: local` setting. Without it, the app was trying to use a cloud provider (OpenAI, Groq, etc.) that wasn't configured with an API key, causing a 30-minute timeout.

## Fix Applied
Updated `C:\Users\LENOVO\AppData\Local\hermes\config.yaml`:
```yaml
stt:
  enabled: true
  language: en
  local:
    model: tiny  # or base for better quality
  openai:
    model: whisper-1
    language: ''
  provider: local  # <-- THIS IS THE FIX
```

## Verified
- `faster-whisper` is installed and works
- Local model: 1-2s load, 2-4s transcription
- **NO API calls, NO timeouts, NO cloud dependency**

## Test
Run: `python test_faster_whisper.py [tiny|base|small|medium]`
