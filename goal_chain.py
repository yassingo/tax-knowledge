"""
goal_chain.py - The main autonomous goal loop.
Keeps working on the goal and all sub-problems until they're all resolved.
"""
import subprocess
import sys
import time
import json
from datetime import datetime

PYTHON = r"C:\Users\LENOVO\tag-rag\venv\Scripts\python.exe"
WORKDIR = r"C:\Users\LENOVO\tag-rag"

GOALS = [
    {
        "id": 1,
        "title": "Switch from AWS Bedrock to local Ollama (workaround for quota)",
        "check": lambda: os.path.exists(rf"{WORKDIR}\ask_tax.py") and "ollama" in open(rf"{WORKDIR}\ask_tax.py").read(),
        "fix": "ask_tax.py must use Ollama, not Bedrock",
        "done": True,
    },
    {
        "id": 2,
        "title": "Add conversational memory for multi-turn Q&A",
        "check": None,  # implemented below
        "fix": "ask_tax.py must support --chat mode with history",
        "done": False,
    },
    {
        "id": 3,
        "title": "Add source citations showing which PDF pages were used",
        "check": None,
        "fix": "Output must include [Source: p17.pdf, page X] for each answer",
        "done": False,
    },
    {
        "id": 4,
        "title": "Commit current code to tax-knowledge GitHub repo",
        "check": lambda: os.path.exists(rf"{WORKDIR}\.git"),
        "fix": "Run git init, add, commit, push to github.com/yassingo/tax-knowledge",
        "done": False,
    },
    {
        "id": 5,
        "title": "Add automated test suite for the pipeline",
        "check": lambda: os.path.exists(rf"{WORKDIR}\test_pipeline.py"),
        "fix": "Create test_pipeline.py with at least 3 test questions",
        "done": False,
    },
    {
        "id": 6,
        "title": "Add faster local model option (e.g., mistral:7b or phi3)",
        "check": None,
        "fix": "Document alternative model in ask_tax.py comments",
        "done": True,  # already configurable
    },
    {
        "id": 7,
        "title": "Support ingesting multiple PDFs (not just p17.pdf)",
        "check": None,
        "fix": "ingest.py should glob all *.pdf in vault directory",
        "done": False,
    },
    {
        "id": 8,
        "title": "Add a 'reset to AWS Bedrock' toggle when quota resets",
        "check": None,
        "fix": "ask_tax.py should have --backend {ollama,bedrock} flag",
        "done": False,
    },
]


def log(msg: str):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)


def is_done(goal):
    if goal.get("done"):
        return True
    if goal.get("check") is None:
        return False
    try:
        return goal["check"]()
    except Exception as e:
        log(f"Check error for goal {goal['id']}: {e}")
        return False


def main():
    log("=" * 60)
    log("AUTONOMOUS GOAL CHAIN STARTED")
    log("=" * 60)

    iteration = 0
    max_iterations = 20

    while iteration < max_iterations:
        iteration += 1
        log(f"\n--- ITERATION {iteration} ---")

        # Find next unsolved goal
        next_goal = None
        for g in GOALS:
            if not is_done(g):
                next_goal = g
                break

        if next_goal is None:
            log("🎯 ALL GOALS COMPLETE!")
            return 0

        log(f"Working on: {next_goal['title']}")
        log(f"  Fix needed: {next_goal['fix']}")

        # The actual work happens here - run the fix
        # In a real autonomous system, this would be a Claude/Hermes agent call
        # For now, we signal that work is needed
        log(f"  → Action required: {next_goal['fix']}")
        log(f"  → See the corresponding sub-script or skill")

        # If we can check it, do so
        if next_goal.get("check"):
            time.sleep(2)
            if is_done(next_goal):
                log(f"  ✅ Goal {next_goal['id']} verified complete")
                next_goal["done"] = True
            else:
                log(f"  ❌ Goal {next_goal['id']} still not done")
        else:
            log(f"  ⏳ Manual verification needed for goal {next_goal['id']}")

    log(f"Reached max iterations ({max_iterations}). Stopping.")
    return 1


if __name__ == "__main__":
    import os
    sys.exit(main())
