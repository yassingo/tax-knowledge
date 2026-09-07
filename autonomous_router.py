"""
autonomous_router.py - Background service that auto-routes tasks.
Runs in the background, intercepts user requests, picks the optimal agent.
"""
import os
import json
import re
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

# Task classification
TASK_PATTERNS = {
    "design": {
        "keywords": ["design", "ui", "ux", "pretty", "beautiful", "landing page", 
                    "dashboard", "styling", "css", "html", "beautiful", "modern",
                    "redesign", "ui design", "mockup", "sketch", "wireframe"],
        "quality": 9,
        "model": "fable-5.1",
        "skill": "popular-web-designs",
        "fallback_skill": "claude-design"
    },
    "code": {
        "keywords": ["build", "implement", "code", "function", "class", "api",
                    "add", "create a", "write", "develop", "feature"],
        "quality": 7,
        "model": "smart_route",
        "skill": "cagrex-convex-backend",
        "fallback_skill": "local-vault-cloud-rag"
    },
    "code_review": {
        "keywords": ["review", "refactor", "improve", "optimize", "simplify",
                     "clean up", "best practice", "code quality"],
        "quality": 8,
        "model": "sonnet-5",
        "skill": "ponytail",
        "fallback_skill": "autonomous-self-correcting-loop"
    },
    "bug_fix": {
        "keywords": ["fix", "bug", "broken", "error", "doesn't work", "fails",
                     "crash", "issue", "problem", "debug"],
        "quality": 7,
        "model": "ollama-qwen3-8b",
        "skill": "ponytail",
        "fallback_skill": "systematic-debugging"
    },
    "explanation": {
        "keywords": ["explain", "what does", "how does", "tell me about",
                     "describe", "summary", "overview", "understand"],
        "quality": 6,
        "model": "ollama-qwen3-8b",
        "skill": None,
        "fallback_skill": None
    },
    "document": {
        "keywords": ["document", "write docs", "readme", "comment", "explain code"],
        "quality": 6,
        "model": "ollama-qwen3-8b",
        "skill": "cagrex-ui-design",
        "fallback_skill": None
    },
    "test": {
        "keywords": ["test", "verify", "check", "validate", "test suite"],
        "quality": 7,
        "model": "ollama-qwen3-8b",
        "skill": "test-driven-development",
        "fallback_skill": "ponytail"
    },
    "architecture": {
        "keywords": ["architecture", "system design", "diagram", "structure",
                     "infrastructure", "how is it built"],
        "quality": 8,
        "model": "sonnet-5",
        "skill": "architecture-diagram",
        "fallback_skill": None
    },
    "research": {
        "keywords": ["research", "find", "look up", "what is the best", "compare",
                     "which is better", "should I use"],
        "quality": 7,
        "model": "gemini-3.7-flash",
        "skill": "grounded-citations",
        "fallback_skill": None
    },
    "rag": {
        "keywords": ["rag", "knowledge base", "from my docs", "according to",
                     "based on", "from my pdf", "from my notes"],
        "quality": 8,
        "model": "ollama-qwen3-8b",
        "skill": "brain-tax-rag",
        "fallback_skill": "local-vault-cloud-rag"
    }
}

# Quality signal patterns
QUALITY_SIGNALS = {
    "premium": ["production", "ship", "polish", "beautiful", "perfect", "amazing",
               "best", "premium", "high quality", "design"],
    "standard": ["build", "implement", "create", "add", "fix", "review"],
    "draft": ["draft", "rough", "quick", "just", "simple", "basic", "sketch", "wip"]
}


def classify_task(user_request: str) -> dict:
    """
    Classify the user's request and pick the optimal model + skill.
    Returns a dict with: task_type, quality, model, skill, fallback_skill, reasoning
    """
    request_lower = user_request.lower()

    # Detect task type by keyword matching
    scores = {}
    for task_type, config in TASK_PATTERNS.items():
        score = sum(1 for kw in config["keywords"] if kw in request_lower)
        if score > 0:
            scores[task_type] = score

    # Pick the best match
    if scores:
        best_task = max(scores, key=scores.get)
        config = TASK_PATTERNS[best_task]
    else:
        # Default: code review
        best_task = "code"
        config = TASK_PATTERNS["code"]

    # Detect quality level
    quality = config["quality"]
    for q_level, signals in QUALITY_SIGNALS.items():
        if any(s in request_lower for s in signals):
            if q_level == "premium" and quality < 9:
                quality = 9
            elif q_level == "draft" and quality > 5:
                quality = 5
            break

    # Pick model based on quality + cost
    model = pick_model(quality, config["model"])

    return {
        "task_type": best_task,
        "quality": quality,
        "model": model,
        "skill": config["skill"],
        "fallback_skill": config["fallback_skill"],
        "reasoning": f"Task '{best_task}' detected (score {scores.get(best_task, 0)}). Quality {quality}/10. Using {model}."
    }


def pick_model(quality: int, preferred: str) -> str:
    """Pick the right model based on quality needs and cost optimization."""
    # High quality tasks get Fable 5.1
    if quality >= 9:
        return "fable-5.1"
    # Medium quality gets standard models
    elif quality >= 7:
        if preferred == "ollama-qwen3-8b":
            return "ollama-qwen3-8b"
        elif preferred == "smart_route":
            return "sonnet-5"
        return preferred if preferred != "smart_route" else "sonnet-5"
    # Low quality uses free models
    else:
        return "ollama-qwen3-8b"


def get_openrouter_key():
    env_path = r"C:\Users\LENOVO\AppData\Local\hermes\.env"
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if 'OPENROUTER_API_KEY' in line and '=' in line and not line.strip().startswith('#'):
                    key = line.split('=', 1)[1].strip()
                    if not key.startswith('sk-or-...'):
                        return key
    return None


def execute_task(user_request: str) -> dict:
    """
    Main entry point. Takes user request, classifies it, runs it, returns result.
    """
    # Classify
    decision = classify_task(user_request)
    print(f"\n[AUTONOMOUS ROUTER] {decision['reasoning']}")
    print(f"  Model: {decision['model']}")
    print(f"  Skill: {decision['skill'] or '(none)'}")

    # Get API key
    api_key = get_openrouter_key()

    if not api_key:
        return {"error": "No OpenRouter API key found", "decision": decision}

    # Execute via OpenRouter
    model_map = {
        "fable-5.1": "anthropic/claude-fable-5.1",
        "sonnet-5": "anthropic/claude-sonnet-5",
        "gpt-5.5-pro": "openai/gpt-5.5-pro",
        "deepseek-v4-pro": "deepseek/deepseek-v4-pro",
        "gemini-3.7-flash": "google/gemini-3.7-flash",
    }
    model_id = model_map.get(decision["model"], "anthropic/claude-fable-5.1")

    # Build the prompt
    skill_prompt = ""
    if decision["skill"]:
        skill_prompt = f"\n[Skill loaded: {decision['skill']}]\n"

    full_prompt = f"""You are a helpful assistant with access to multiple skills.

{skill_prompt}

User request: {user_request}

Please provide a helpful, high-quality response."""

    data = json.dumps({
        "model": model_id,
        "messages": [{"role": "user", "content": full_prompt}],
        "max_tokens": 4000,
        "temperature": 0.7
    }).encode('utf-8')

    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )

    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            data = json.loads(response.read())
            duration = time.time() - start
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            usage = data.get("usage", {})
            return {
                "decision": decision,
                "response": content,
                "duration": duration,
                "tokens": usage.get("total_tokens", 0),
                "cost": usage.get("cost", 0)
            }
    except Exception as e:
        return {"error": str(e), "decision": decision}


# The router will be called by Hermes when the user types anything
def route(user_input: str):
    """
    Main entry point called by Hermes for every user message.
    """
    result = execute_task(user_input)
    if "error" in result:
        return f"[ROUTER ERROR] {result['error']}"
    return result.get("response", "No response")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        request = " ".join(sys.argv[1:])
        result = execute_task(request)
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"\n{'='*60}")
            print(result["response"])
            print(f"{'='*60}")
            print(f"Model: {result['decision']['model']}, Tokens: {result['tokens']}, Cost: ${result['cost']:.4f}")
    else:
        print("Usage: python autonomous_router.py 'your task description'")
