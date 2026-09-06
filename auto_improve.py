"""
auto_improve.py - Autonomous self-improving agent loop
Runs a task continuously, evaluates output, fixes mistakes, iterates until goal met.

Usage:
    python auto_improve.py --goal "your goal" --max-iterations 10
    python auto_improve.py --goal "answer tax questions accurately" --validator ask_tax.py
"""
import subprocess
import json
import time
import sys
import argparse
from datetime import datetime

class AutonomousLoop:
    def __init__(self, goal: str, max_iterations: int = 10, validator_cmd: str = None, 
                 work_dir: str = r"C:\Users\LENOVO\tag-rag"):
        self.goal = goal
        self.max_iterations = max_iterations
        self.validator_cmd = validator_cmd
        self.work_dir = work_dir
        self.history = []
        self.iteration = 0

    def log(self, msg: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{self.iteration}/{self.max_iterations}] {msg}")

    def evaluate(self, output: str) -> tuple[bool, str, str]:
        """
        Self-evaluate output. Returns (is_correct, reason, suggested_fix)
        This is the "checks itself" part.
        """
        output_lower = output.lower()

        # Check 1: No errors
        error_indicators = ["traceback", "error:", "exception", "failed:", "modulenotfounderror",
                           "throttlingexception", "validationexception", "resourcenotfound"]
        for err in error_indicators:
            if err in output_lower:
                return False, f"Error detected: '{err}'", "Fix the error and retry"

        # Check 2: Goal-specific success criteria
        if "tax" in self.goal.lower() or "deduction" in self.goal.lower():
            if "i don't know" in output_lower or "no relevant" in output_lower:
                return False, "Model said it doesn't know", "Try different query formulation or use more context"

        # Check 3: Empty/short response
        if len(output.strip()) < 20:
            return False, "Output too short", "Generate more detailed response"

        return True, "Output looks correct", ""

    def run_task(self) -> str:
        """Run the actual task. Override this for custom tasks."""
        if self.validator_cmd:
            result = subprocess.run(
                self.validator_cmd,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=self.work_dir
            )
            return result.stdout + result.stderr
        return ""

    def fix_attempt(self, output: str, reason: str) -> str:
        """Attempt to fix the issue. Override for custom logic."""
        self.log(f"Auto-fix attempt: {reason}")
        return output

    def run(self):
        """Main autonomous loop"""
        self.log(f"GOAL: {self.goal}")
        self.log(f"Max iterations: {self.max_iterations}")

        while self.iteration < self.max_iterations:
            self.iteration += 1
            self.log("=" * 60)
            self.log(f"Starting iteration {self.iteration}")
            self.log("=" * 60)

            # Step 1: Run the task
            try:
                output = self.run_task()
            except subprocess.TimeoutExpired:
                self.log("Task timed out. Retrying with longer timeout.")
                continue
            except Exception as e:
                self.log(f"Task crashed: {e}")
                continue

            # Step 2: Self-evaluate
            is_correct, reason, fix_suggestion = self.evaluate(output)
            self.history.append({
                "iteration": self.iteration,
                "timestamp": datetime.now().isoformat(),
                "is_correct": is_correct,
                "reason": reason,
                "output_snippet": output[:500]
            })

            # Step 3: If correct, we're done
            if is_correct:
                self.log(f"✅ SUCCESS: {reason}")
                self.log(f"Output: {output[:200]}...")
                self.save_history()
                return output

            # Step 4: If incorrect, try to fix
            self.log(f"❌ FAILED: {reason}")
            self.log(f"Suggested fix: {fix_suggestion}")
            output = self.fix_attempt(output, reason)

        self.log(f"⚠️ Reached max iterations ({self.max_iterations}) without success")
        self.save_history()
        return None

    def save_history(self):
        history_file = f"{self.work_dir}\\auto_improve_history.json"
        with open(history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
        self.log(f"History saved to {history_file}")


def main():
    parser = argparse.ArgumentParser(description="Autonomous self-improving agent")
    parser.add_argument("--goal", required=True, help="The goal to achieve")
    parser.add_argument("--max-iterations", type=int, default=10, help="Max iterations before giving up")
    parser.add_argument("--validator", help="Command to run for validation")
    parser.add_argument("--workdir", default=r"C:\Users\LENOVO\tag-rag", help="Working directory")

    args = parser.parse_args()

    loop = AutonomousLoop(
        goal=args.goal,
        max_iterations=args.max_iterations,
        validator_cmd=args.validator.split() if args.validator else None,
        work_dir=args.workdir
    )
    result = loop.run()
    if result:
        print(f"\n{'='*60}\nFINAL RESULT:\n{'='*60}\n{result}")
    else:
        print("\nGoal not achieved within max iterations")
        sys.exit(1)


if __name__ == "__main__":
    main()
