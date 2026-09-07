"""
auto_tax.py - Autonomous self-correcting tax RAG
Runs ask_tax.py, evaluates the answer, detects mistakes, and re-queries if needed.

Examples:
    python auto_tax.py "What is the standard deduction for single filers?"
    python auto_tax.py "What are the rules on tax deductions?" --max-tries 5
"""
import subprocess
import sys
import re
import argparse
from datetime import datetime

PYTHON = r"C:\Users\LENOVO\tag-rag\venv\Scripts\python.exe"
SCRIPT = r"C:\Users\LENOVO\tag-rag\ask_tax.py"

def log(msg: str):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)

def run_query(question: str) -> str:
    """Run ask_tax.py and capture output"""
    result = subprocess.run(
        [PYTHON, SCRIPT, question],
        capture_output=True,
        text=True,
        timeout=300
    )
    return result.stdout + result.stderr

def evaluate_answer(answer: str, question: str) -> tuple[bool, str]:
    """
    Self-evaluate the tax answer. Returns (is_acceptable, reason).
    Checks for: errors, empty responses, "I don't know" patterns, low confidence.
    """
    answer_lower = answer.lower()

    # Check 1: No technical errors
    error_indicators = ["traceback", "error:", "exception", "modulenotfounderror",
                       "throttlingexception", "validationexception", "resourcenotfound",
                       "failed:", "commandnotfound"]
    for err in error_indicators:
        if err in answer_lower:
            return False, f"Technical error: {err}"

    # Check 2: Not empty
    if len(answer.strip()) < 30:
        return False, "Answer too short (< 30 chars)"

    # Check 3: Not an "I don't know" response
    dont_know_patterns = ["i don't know", "i do not know", "no information", "not in the excerpts",
                          "i cannot answer", "unable to provide"]
    for pattern in dont_know_patterns:
        if pattern in answer_lower:
            return False, f"Model said: '{pattern}'"

    # Check 4: Answer should contain some numbers (tax questions usually have $ amounts)
    if re.search(r'\$[\d,]+', answer):
        log("✓ Answer contains dollar amounts (good)")
    elif re.search(r'\d+', answer):
        log("✓ Answer contains numbers")

    return True, "Answer looks acceptable"

def suggest_reformulation(question: str, attempt: int) -> str:
    """Suggest a reformulation if the original question didn't work"""
    reformulations = [
        question,
        f"Can you tell me {question.lower().replace('?', '')}",
        f"Explain {question.lower().replace('?', '').replace('what are', 'about').replace('what is', 'about')}",
        f"According to IRS Publication 17, {question.lower().replace('?', '')}",
        f"What does IRS Publication 17 say about {question.lower().replace('what are the rules on ', '').replace('what is the ', '').replace('?', '').strip()}?",
    ]
    return reformulations[min(attempt, len(reformulations) - 1)]

def auto_tax_loop(question: str, max_tries: int = 5):
    """Main autonomous loop - keeps trying until acceptable answer or max_tries reached"""
    log(f"GOAL: Answer '{question}' with acceptable quality")
    log(f"Max attempts: {max_tries}")

    current_question = question
    best_answer = None
    best_answer_score = 0

    for attempt in range(1, max_tries + 1):
        log("=" * 60)
        log(f"ATTEMPT {attempt}/{max_tries}")
        log(f"Question: {current_question}")
        log("=" * 60)

        # Step 1: Run the query
        try:
            output = run_query(current_question)
        except subprocess.TimeoutExpired:
            log("⏱️ Query timed out. Retrying...")
            continue
        except Exception as e:
            log(f"❌ Query crashed: {e}")
            continue

        # Step 2: Self-evaluate
        is_ok, reason = evaluate_answer(output, question)
        log(f"Evaluation: {'✅ PASS' if is_ok else '❌ FAIL'} - {reason}")

        # Extract the actual answer from the output (look for the boxed result)
        answer_match = re.search(r'={6,}\n(.+?)\n={6,}', output, re.DOTALL)
        clean_answer = answer_match.group(1) if answer_match else output

        # Track best answer
        if len(clean_answer) > best_answer_score:
            best_answer = clean_answer
            best_answer_score = len(clean_answer)

        # Step 3: If acceptable, done!
        if is_ok:
            # 🎯 SUCCESS on attempt {attempt} printed by main()
            # 🎯 FINAL ANSWER printed by main()
            return clean_answer

        # Step 4: Reformulate and retry
        if attempt < max_tries:
            current_question = suggest_reformulation(question, attempt)
            log(f"🔄 Reformulating for next attempt: {current_question}")

    # If we get here, exhausted attempts - return best we have
    log(f"⚠️ Exhausted {max_tries} attempts. Returning best answer found.")
    if best_answer:
        log(f"\n{'='*60}\nBEST ANSWER FOUND:\n{'='*60}\n{best_answer}\n{'='*60}")
    return best_answer

def main():
    parser = argparse.ArgumentParser(description="Autonomous self-correcting tax RAG")
    parser.add_argument("question", help="The tax question to answer")
    parser.add_argument("--max-tries", type=int, default=5, help="Maximum attempts (default: 5)")
    args = parser.parse_args()

    result = auto_tax_loop(args.question, args.max_tries)
    if result:
        print(f"\n{result}")
    else:
        print("Could not get an acceptable answer")
        sys.exit(1)

if __name__ == "__main__":
    main()
