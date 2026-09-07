"""
test_pipeline.py - Test suite for the tax RAG pipeline.
Validates ingestion, retrieval, and answer generation.
"""
import subprocess
import os
import sys
import time
import re
from datetime import datetime

PYTHON = r"C:\Users\LENOVO\tag-rag\venv\Scripts\python.exe"
SCRIPT = r"C:\Users\LENOVO\tag-rag\ask_tax.py"
INDEX_DIR = r"C:\Users\LENOVO\tag-rag\index"

TESTS = [
    {
        "name": "Index files exist",
        "check": lambda: os.path.exists(os.path.join(INDEX_DIR, "tax.index"))
                       and os.path.exists(os.path.join(INDEX_DIR, "docs.json")),
    },
    {
        "name": "Standard deduction question",
        "question": "What is the standard deduction for single filers?",
        "expect_keywords": ["standard", "deduction"],
        "min_length": 50,
    },
    {
        "name": "Filing status question",
        "question": "What are the filing status options?",
        "expect_keywords": ["filing", "status"],
        "min_length": 50,
    },
    {
        "name": "Dependents question",
        "question": "Who can I claim as a dependent?",
        "expect_keywords": ["dependent"],
        "min_length": 50,
    },
]


def log(msg: str):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)


def run_test(test):
    name = test["name"]
    log(f"Test: {name}")
    if "check" in test:
        try:
            passed = test["check"]()
            log(f"  Result: {'✅ PASS' if passed else '❌ FAIL'}")
            return passed
        except Exception as e:
            log(f"  Result: ❌ ERROR: {e}")
            return False
    question = test.get("question")
    if not question:
        log(f"  Result: ❌ No question defined")
        return False
    try:
        result = subprocess.run(
            [PYTHON, SCRIPT, question],
            capture_output=True, text=True, timeout=300
        )
        output = result.stdout
    except subprocess.TimeoutExpired:
        log(f"  Result: ❌ TIMEOUT")
        return False
    except Exception as e:
        log(f"  Result: ❌ ERROR: {e}")
        return False

    # Check min length
    if len(output) < test.get("min_length", 30):
        log(f"  Result: ❌ Output too short ({len(output)} chars)")
        return False

    # Check expected keywords (case-insensitive substring match)
    keywords = test.get("expect_keywords", [])
    if keywords:
        output_lower = output.lower()
        missing = [k for k in keywords if k.lower() not in output_lower]
        if missing:
            log(f"  Result: ❌ Missing keywords: {missing}")
            return False

    log(f"  Result: ✅ PASS (output: {len(output)} chars)")
    return True


def main():
    log("=" * 60)
    log("TAX RAG PIPELINE TEST SUITE")
    log("=" * 60)

    results = []
    for test in TESTS:
        passed = run_test(test)
        results.append((test["name"], passed))
        time.sleep(1)

    log("=" * 60)
    log("RESULTS:")
    for name, passed in results:
        log(f"  {'✅' if passed else '❌'} {name}")

    total = len(results)
    passed_count = sum(1 for _, p in results if p)
    log(f"\n{passed_count}/{total} tests passed")

    if passed_count == total:
        log("🎯 ALL TESTS PASSED!")
        return 0
    else:
        log(f"⚠️ {total - passed_count} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
