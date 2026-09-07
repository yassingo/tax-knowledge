"""
smart_router.py - Intelligent agent router for design and code tasks.
Routes requests to the optimal model based on quality, cost, and speed needs.
"""
import os
import sys
import json
import argparse
import urllib.request
import urllib.error
import time
from datetime import datetime

# Model registry with quality/cost/speed ratings
MODELS = {
    "ollama-qwen3-8b": {
        "provider": "ollama",
        "model": "qwen3:8b",
        "endpoint": "http://localhost:11434/api/generate",
        "quality": 7, "cost_per_1k": 0.0, "speed": 6, "context": 8000,
        "best_for": ["code", "general", "drafts", "local"],
    },
    "ollama-qwen2.5-coder": {
        "provider": "ollama", "model": "qwen2.5-coder:latest",
        "endpoint": "http://localhost:11434/api/generate",
        "quality": 6, "cost_per_1k": 0.0, "speed": 8, "context": 8000,
        "best_for": ["code generation", "code review"],
    },
    "ollama-gemma3-4b": {
        "provider": "ollama", "model": "gemma3:4b",
        "endpoint": "http://localhost:11434/api/generate",
        "quality": 5, "cost_per_1k": 0.0, "speed": 9, "context": 8000,
        "best_for": ["drafts", "simple tasks"],
    },
    "ollama-mistral": {
        "provider": "ollama", "model": "mistral:latest",
        "endpoint": "http://localhost:11434/api/generate",
        "quality": 6, "cost_per_1k": 0.0, "speed": 7, "context": 8000,
        "best_for": ["general purpose", "multilingual"],
    },
    "fable-5.1": {
        "provider": "openrouter", "model": "anthropic/claude-fable-5.1",
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "quality": 9, "cost_per_1k": 0.003, "speed": 8, "context": 200000,
        "best_for": ["design", "html", "css", "creative", "premium"],
    },
    "fable-latest": {
        "provider": "openrouter", "model": "anthropic/claude-fable-latest",
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "quality": 9, "cost_per_1k": 0.003, "speed": 7, "context": 200000,
        "best_for": ["latest premium tasks"],
    },
    "fable-batch": {
        "provider": "openrouter", "model": "anthropic/claude-fable-5.1:batch",
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "quality": 9, "cost_per_1k": 0.0015, "speed": 5, "context": 200000,
        "best_for": ["bulk", "non-urgent"],
    },
    "bedrock-fable": {
        "provider": "bedrock", "model": "anthropic.claude-fable-5-1",
        "endpoint": "bedrock",
        "quality": 9, "cost_per_1k": 0.003, "speed": 8, "context": 200000,
        "best_for": ["AWS hosted", "premium quality"],
    },
    "sonnet-5": {
        "provider": "openrouter", "model": "anthropic/claude-sonnet-5",
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "quality": 9, "cost_per_1k": 0.003, "speed": 7, "context": 200000,
        "best_for": ["reasoning", "code", "premium"],
    },
    "gpt-5.5-pro": {
        "provider": "openrouter", "model": "openai/gpt-5.5-pro",
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "quality": 9, "cost_per_1k": 0.0025, "speed": 7, "context": 128000,
        "best_for": ["reasoning", "complex"],
    },
    "deepseek-v4-pro": {
        "provider": "openrouter", "model": "deepseek/deepseek-v4-pro",
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "quality": 8, "cost_per_1k": 0.00014, "speed": 8, "context": 128000,
        "best_for": ["budget", "code", "long context"],
    },
    "qwen3.8-max": {
        "provider": "openrouter", "model": "qwen/qwen3.8-max",
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "quality": 8, "cost_per_1k": 0.0004, "speed": 8, "context": 128000,
        "best_for": ["code", "multilingual", "value"],
    },
    "grok-4.6": {
        "provider": "openrouter", "model": "x-ai/grok-4.6",
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "quality": 8, "cost_per_1k": 0.005, "speed": 8, "context": 131000,
        "best_for": ["real-time", "humor", "unfiltered"],
    },
    "gemini-3.7-flash": {
        "provider": "openrouter", "model": "google/gemini-3.7-flash",
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "quality": 7, "cost_per_1k": 0.000075, "speed": 10, "context": 1000000,
        "best_for": ["fast", "long context", "budget"],
    },
    "minimax-m3-free": {
        "provider": "openrouter", "model": "minimax/minimax-m3:free",
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "quality": 7, "cost_per_1k": 0.0, "speed": 8, "context": 128000,
        "best_for": ["free quality", "general"],
    },
}


def get_openrouter_key():
    env_path = r"C:\Users\LENOVO\AppData\Local\hermes\.env"
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if 'OPENROUTER_API_KEY' in line.upper() and '=' in line and not line.strip().startswith('#'):
                    key = line.split('=', 1)[1].strip()
                    if not key.startswith('sk-or-...'):
                        return key
    return None


def call_ollama(model_name, prompt):
    data = json.dumps({
        "model": model_name, "prompt": prompt, "stream": False,
        "options": {"temperature": 0.7, "num_predict": 2000}
    }).encode('utf-8')
    req = urllib.request.Request(
        "http://localhost:11434/api/generate", data=data,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read())
            return {
                "content": result.get("response", ""),
                "model": model_name, "provider": "ollama", "cost": 0.0,
                "tokens": result.get("eval_count", 0) + result.get("prompt_eval_count", 0)
            }
    except Exception as e:
        return {"error": str(e), "provider": "ollama"}


def call_openrouter(model_full, prompt, api_key):
    data = json.dumps({
        "model": model_full,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 4000, "temperature": 0.7
    }).encode('utf-8')
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions", data=data,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read())
            usage = result.get("usage", {})
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            return {
                "content": content, "model": model_full, "provider": "openrouter",
                "cost": usage.get("cost", 0), "tokens": usage.get("total_tokens", 0)
            }
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='ignore')[:300]
        return {"error": f"HTTP {e.code}: {body}", "provider": "openrouter"}


def score_model(info, quality, budget, speed_priority, task_type):
    score = 0
    qdiff = abs(info["quality"] - quality)
    score += (10 - qdiff) * 10
    if budget is not None:
        if info["cost_per_1k"] > budget:
            return -1
        score += max(0, 10 - (info["cost_per_1k"] * 1000)) * 5
    else:
        if info["cost_per_1k"] == 0:
            score += 5
    score += info["speed"] * speed_priority
    if task_type and task_type.lower() in [b.lower() for b in info.get("best_for", [])]:
        score += 20
    return score


def select_model(quality, budget, speed, task_type, prefer_local=False):
    candidates = []
    for name, info in MODELS.items():
        s = score_model(info, quality, budget, speed, task_type)
        if s >= 0:
            candidates.append((name, info, s))
    if not candidates:
        return None, None
    candidates.sort(key=lambda x: -x[2])
    if prefer_local:
        for name, info, _ in candidates:
            if info["provider"] == "ollama":
                return name, info
    return candidates[0][0], candidates[0][1]


def print_models_table():
    print("=" * 110)
    print("AVAILABLE MODELS (sorted by quality, descending)")
    print("=" * 110)
    print(f"  {'Model':<25} {'Provider':<12} {'Quality':<8} {'Cost/1k':<10} {'Speed':<6} {'Context':<10} {'Best For'}")
    print("-" * 110)
    for name, info in sorted(MODELS.items(), key=lambda x: -x[1]["quality"]):
        best_for = ", ".join(info.get("best_for", [])[:3])
        cost = "FREE" if info["cost_per_1k"] == 0 else f"${info['cost_per_1k']:.4f}"
        print(f"  {name:<25} {info['provider']:<12} {info['quality']:<8} {cost:<10} {info['speed']:<6} {info['context']:<10} {best_for}")
    print("=" * 110)


def main():
    parser = argparse.ArgumentParser(description="Smart agent router")
    parser.add_argument("--task", help="Task description")
    parser.add_argument("--quality", type=int, default=8)
    parser.add_argument("--budget", type=float, default=None, help="Max cost per 1k tokens")
    parser.add_argument("--speed", type=int, default=7)
    parser.add_argument("--type", default="general", help="Task type")
    parser.add_argument("--local", action="store_true", help="Prefer local models")
    parser.add_argument("--list", action="store_true", help="List all models")
    parser.add_argument("--auto", action="store_true", help="Auto-detect best model")
    args = parser.parse_args()

    print("=" * 70)
    print("SMART AGENT ROUTER")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    if args.list:
        print_models_table()
        return

    if args.auto:
        quality, budget, speed, task_type, prefer_local = 8, 0.01, 7, "general", False
    else:
        quality = args.quality
        budget = args.budget
        speed = args.speed
        task_type = args.type
        prefer_local = args.local

    print(f"\nRequirements:")
    print(f"  Quality: {quality}/10")
    print(f"  Budget:  {'$' + str(budget) + '/1k tokens' if budget else 'unlimited'}")
    print(f"  Speed:   {speed}/10")
    print(f"  Task:    {task_type}")
    print(f"  Local:   {'yes' if prefer_local else 'no'}")

    name, info = select_model(quality, budget, speed, task_type, prefer_local)
    if not name:
        print("\n[FAIL] No model matches your requirements")
        return

    print(f"\n[SELECTED] {name}")
    print(f"  Quality: {info['quality']}/10, Speed: {info['speed']}/10")
    if info['cost_per_1k'] == 0:
        cost_str = "FREE"
    else:
        cost_str = "$" + str(info['cost_per_1k']) + "/1k tokens"
    print(f"  Cost:    {cost_str}")
    print(f"  Context: {info['context']} tokens")

    if args.task:
        print(f"\n[RUNNING] Task...")
        start = time.time()
        if info["provider"] == "ollama":
            result = call_ollama(info["model"], args.task)
        else:
            api_key = get_openrouter_key()
            if not api_key:
                print("[FAIL] OpenRouter API key not found in .env")
                return
            result = call_openrouter(info["model"], args.task, api_key)
        duration = time.time() - start
        if "error" in result:
            print(f"\n[ERROR] {result['error']}")
        else:
            print(f"\n[RESULT] ({duration:.1f}s, ${result.get('cost', 0):.5f}, {result.get('tokens', 0)} tokens)")
            print("-" * 70)
            print(result.get("content", ""))
            print("-" * 70)


if __name__ == "__main__":
    main()
