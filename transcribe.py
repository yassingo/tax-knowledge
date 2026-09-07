"""
transcribe.py - Local audio/video transcription using OpenAI Whisper.

Uses the transformers library's Whisper implementation to transcribe audio
files locally - no API calls, no cloud dependency.

Usage:
    python transcribe.py path/to/audio.mp3
    python transcribe.py path/to/video.mp4 --model base
    python transcribe.py path/to/audio.wav --output transcript.txt
    python transcribe.py path/to/audio.mp3 --format srt  # SubRip subtitles

Models (smaller = faster but less accurate):
    tiny     - 39M params,  ~1GB RAM, fastest
    base     - 74M params,  ~1GB RAM, good
    small    - 244M params, ~2GB RAM, better
    medium   - 769M params, ~5GB RAM, very good
    large-v3 - 1550M params, ~10GB RAM, best (needs GPU)

Default: base (good balance of speed and accuracy for 6GB VRAM box)
"""
import sys
import os
import argparse
import subprocess
import json
import time
from pathlib import Path

# Suppress noisy warnings
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

def check_ffmpeg():
    """Check ffmpeg is available (required by Whisper for most audio formats)."""
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def format_timestamp_srt(seconds):
    """Format seconds to SRT timestamp: HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def format_timestamp_vtt(seconds):
    """Format seconds to WebVTT timestamp: HH:MM:SS.mmm"""
    return format_timestamp_srt(seconds).replace(",", ".")


def transcribe(audio_path: str, model_name: str = "base", output_format: str = "txt",
               language: str = None, task: str = "transcribe"):
    """
    Transcribe an audio/video file using local Whisper.
    
    Args:
        audio_path: Path to audio/video file (mp3, wav, mp4, m4a, etc.)
        model_name: Whisper model size (tiny/base/small/medium/large-v3)
        output_format: txt, srt, vtt, json
        language: Force language (e.g., 'en', 'es') or None for auto-detect
        task: 'transcribe' or 'translate' (translate to English)
    
    Returns:
        dict with 'text', 'segments', 'language' keys
    """
    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    # Check ffmpeg
    if not check_ffmpeg():
        print("⚠️  WARNING: ffmpeg not found in PATH.")
        print("    Whisper needs ffmpeg for most audio/video formats.")
        print("    Install: winget install Gyan.FFmpeg")
        print()
    
    print(f"[1/4] Loading Whisper model: {model_name}")
    print(f"      (first run downloads ~1GB; subsequent runs use cache)")
    
    from transformers import pipeline
    
    # Use the new transformers pipeline for ASR
    device = "cuda:0" if _has_cuda() else "cpu"
    print(f"      Using device: {device}")
    
    pipe = pipeline(
        "automatic-speech-recognition",
        model=f"openai/whisper-{model_name}",
        device=device,
        chunk_length_s=30,  # Process in 30s chunks
    )
    
    print(f"\n[2/4] Transcribing: {audio_path.name}")
    print(f"      File size: {audio_path.stat().st_size / 1024 / 1024:.1f} MB")
    start = time.time()
    
    # Transcribe
    result = pipe(
        str(audio_path),
        generate_kwargs={
            "language": language,
            "task": task,
        },
        return_timestamps=True,  # Get word/segment timestamps
    )
    
    elapsed = time.time() - start
    print(f"      Done in {elapsed:.1f}s")
    
    # Print preview
    text_preview = result["text"][:200] + "..." if len(result["text"]) > 200 else result["text"]
    print(f"\n[3/4] Transcript preview:")
    print(f"      {text_preview}")
    
    # Save output
    print(f"\n[4/4] Saving output...")
    output_path = _save_output(audio_path, result, output_format, model_name, elapsed)
    print(f"      Saved to: {output_path}")
    
    return result


def _has_cuda():
    """Check if CUDA/GPU is available."""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


def _save_output(audio_path: Path, result: dict, output_format: str,
                 model_name: str, elapsed: float) -> Path:
    """Save transcription in the requested format."""
    
    base_name = audio_path.stem
    output_dir = audio_path.parent
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    
    if output_format == "txt":
        output_path = output_dir / f"{base_name}_transcript_{timestamp}.txt"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# Transcript: {audio_path.name}\n")
            f.write(f"# Model: whisper-{model_name}\n")
            f.write(f"# Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Duration: {elapsed:.1f}s transcription time\n")
            f.write("=" * 70 + "\n\n")
            f.write(result["text"])
    elif output_format == "srt":
        output_path = output_dir / f"{base_name}_subtitles_{timestamp}.srt"
        with open(output_path, "w", encoding="utf-8") as f:
            for i, chunk in enumerate(result.get("chunks", []), 1):
                start_ts = chunk["timestamp"][0] or 0
                end_ts = chunk["timestamp"][1] or (start_ts + 5)
                f.write(f"{i}\n")
                f.write(f"{format_timestamp_srt(start_ts)} --> {format_timestamp_srt(end_ts)}\n")
                f.write(f"{chunk['text'].strip()}\n\n")
    elif output_format == "vtt":
        output_path = output_dir / f"{base_name}_subtitles_{timestamp}.vtt"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("WEBVTT\n\n")
            for chunk in result.get("chunks", []):
                start_ts = chunk["timestamp"][0] or 0
                end_ts = chunk["timestamp"][1] or (start_ts + 5)
                f.write(f"{format_timestamp_vtt(start_ts)} --> {format_timestamp_vtt(end_ts)}\n")
                f.write(f"{chunk['text'].strip()}\n\n")
    elif output_format == "json":
        output_path = output_dir / f"{base_name}_transcript_{timestamp}.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({
                "file": str(audio_path),
                "model": f"whisper-{model_name}",
                "transcription_time": elapsed,
                "text": result["text"],
                "chunks": [
                    {
                        "text": chunk["text"],
                        "start": chunk["timestamp"][0],
                        "end": chunk["timestamp"][1]
                    }
                    for chunk in result.get("chunks", [])
                ]
            }, f, indent=2, ensure_ascii=False)
    else:
        raise ValueError(f"Unknown format: {output_format}")
    
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Local audio/video transcription using OpenAI Whisper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python transcribe.py recording.mp3
  python transcribe.py interview.wav --model small --format srt
  python transcribe.py lecture.mp4 --model base --language en
  python transcribe.py podcast.m4a --format vtt
        """
    )
    parser.add_argument("audio", help="Path to audio/video file")
    parser.add_argument("--model", "-m", default="base",
                       choices=["tiny", "base", "small", "medium", "large-v3"],
                       help="Whisper model size (default: base)")
    parser.add_argument("--output", "-o", default="txt",
                       choices=["txt", "srt", "vtt", "json"],
                       help="Output format (default: txt)")
    parser.add_argument("--language", "-l", default=None,
                       help="Force language (e.g., en, es, fr) or auto-detect")
    parser.add_argument("--task", "-t", default="transcribe",
                       choices=["transcribe", "translate"],
                       help="transcribe or translate to English")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("LOCAL TRANSCRIPTION - OpenAI Whisper")
    print("=" * 70)
    
    try:
        transcribe(
            args.audio,
            model_name=args.model,
            output_format=args.output,
            language=args.language,
            task=args.task,
        )
        print("\n✅ Done!")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
