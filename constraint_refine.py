"""
Experiment 7 - Constraint Specification and Iterative Refinement

Task: Generate a short description of a smartwatch (max 60 words)
      under three constraints:
        1. Exactly 3 bullet points
        2. Each bullet starts with a verb
        3. No use of the word "smart" anywhere

Runs an initial prompt, checks violations with code, then sends a
refined prompt with examples and clearer phrasing.
"""

import os
import re
import textwrap
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# ---------- Setup ----------
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.environ.get("NVIDIA_API_KEY")
if not api_key:
    raise SystemExit("NVIDIA_API_KEY not found. Create a .env file.")

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key,
)

MODEL = "openai/gpt-oss-20b"
TEMPERATURE = 0.5
MAX_TOKENS = 300


# ---------- Prompts ----------
INITIAL_PROMPT = (
    "Describe a smartwatch. Use exactly 3 bullet points. "
    "Each bullet point must start with a verb. "
    "Do not use the word 'smart'. "
    "Keep the total under 60 words."
)

REFINED_PROMPT = (
    "Describe a fitness watch in exactly 3 bullet points.\n"
    "Each bullet MUST begin with a verb (e.g., 'Tracks', 'Displays', 'Lasts').\n"
    "Do NOT use the word 'smart' under any circumstances - not even in the product name.\n"
    "Keep the total under 60 words.\n\n"
    "Example format (do not copy):\n"
    "- Tracks your heart rate.\n"
    "- Displays incoming notifications.\n"
    "- Lasts for two days on a charge.\n\n"
    "Now write your own 3 bullets for a fitness watch:"
)


# ---------- Helpers ----------
def ask_llm(prompt: str) -> str:
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        content = resp.choices[0].message.content
        return (content or "").strip() or "[no content returned]"
    except Exception as e:
        return f"[API error] {type(e).__name__}: {e}"


def check_constraints(response: str) -> dict:
    """Check the three constraints. Returns a dict of findings."""
    lines = [l.strip() for l in response.splitlines() if l.strip()]

    # 1. Exactly 3 bullet points (lines starting with - or *)
    bullets = [l for l in lines if re.match(r"^[-*]\s+", l)]

    # 2. Each bullet starts with a verb - heuristic: first word ends with 's'
    #    (common for third-person verbs like "Tracks", "Displays", "Shows")
    starts_with_verb = []
    for b in bullets:
        text = re.sub(r"^[-*]\s+", "", b)
        first_word = text.split()[0] if text.split() else ""
        starts_with_verb.append(first_word.endswith("s") or first_word.endswith("es"))

    # 3. Word "smart" absent (case-insensitive, whole-word)
    smart_hits = re.findall(r"\bsmart\b", response, flags=re.IGNORECASE)

    # 4. Total word count under 60
    word_count = len(response.split())

    return {
        "bullets": bullets,
        "bullet_count": len(bullets),
        "bullet_count_ok": len(bullets) == 3,
        "starts_with_verb": starts_with_verb,
        "all_start_with_verb": all(starts_with_verb) and len(bullets) > 0,
        "smart_hits": smart_hits,
        "smart_absent": len(smart_hits) == 0,
        "word_count": word_count,
        "word_count_ok": word_count <= 60,
    }


def print_violations(report: dict):
    """Print a human-readable violation report."""
    print("VIOLATION REPORT:")
    print(f"  Bullet count       : {report['bullet_count']} "
          f"({'OK' if report['bullet_count_ok'] else 'VIOLATION - expected 3'})")
    print(f"  Starts with verb   : {report['starts_with_verb']} "
          f"({'OK' if report['all_start_with_verb'] else 'VIOLATION'})")
    print(f"  'smart' occurrences: {report['smart_hits']} "
          f"({'OK' if report['smart_absent'] else 'VIOLATION'})")
    print(f"  Word count         : {report['word_count']} "
          f"({'OK' if report['word_count_ok'] else 'VIOLATION - max 60'})")


def show_block(label: str, prompt: str, response: str, report: dict):
    width = 72
    print("=" * width)
    print(f"  {label}")
    print("=" * width)
    print("PROMPT:")
    print(textwrap.indent(prompt, "  "))
    print()
    print("RESPONSE:")
    print(textwrap.indent(response, "  "))
    print()
    print_violations(report)
    print()


# ---------- Main ----------
if __name__ == "__main__":
    print(f"Model: {MODEL}")
    print(f"Temperature: {TEMPERATURE} | Max tokens: {MAX_TOKENS}")

    # ---- Initial ----
    print("\n>>> Sending INITIAL prompt...")
    initial_resp = ask_llm(INITIAL_PROMPT)
    initial_report = check_constraints(initial_resp)
    show_block("INITIAL PROMPT", INITIAL_PROMPT, initial_resp, initial_report)

    # ---- Refined ----
    print(">>> Sending REFINED prompt...")
    refined_resp = ask_llm(REFINED_PROMPT)
    refined_report = check_constraints(refined_resp)
    show_block("REFINED PROMPT", REFINED_PROMPT, refined_resp, refined_report)

    # ---- Comparison ----
    print("=" * 72)
    print("  BEFORE vs AFTER")
    print("=" * 72)
    print(f"{'Constraint':<28}{'Initial':<18}{'Refined':<18}")
    print("-" * 72)
    print(f"{'Exactly 3 bullets':<28}"
          f"{'PASS' if initial_report['bullet_count_ok'] else 'FAIL':<18}"
          f"{'PASS' if refined_report['bullet_count_ok'] else 'FAIL':<18}")
    print(f"{'Each starts with verb':<28}"
          f"{'PASS' if initial_report['all_start_with_verb'] else 'FAIL':<18}"
          f"{'PASS' if refined_report['all_start_with_verb'] else 'FAIL':<18}")
    print(f"{'No word \"smart\"':<28}"
          f"{'PASS' if initial_report['smart_absent'] else 'FAIL':<18}"
          f"{'PASS' if refined_report['smart_absent'] else 'FAIL':<18}")
    print(f"{'Under 60 words':<28}"
          f"{'PASS' if initial_report['word_count_ok'] else 'FAIL':<18}"
          f"{'PASS' if refined_report['word_count_ok'] else 'FAIL':<18}")
    print("-" * 72)

    init_pass = sum([
        initial_report['bullet_count_ok'],
        initial_report['all_start_with_verb'],
        initial_report['smart_absent'],
        initial_report['word_count_ok'],
    ])
    ref_pass = sum([
        refined_report['bullet_count_ok'],
        refined_report['all_start_with_verb'],
        refined_report['smart_absent'],
        refined_report['word_count_ok'],
    ])
    print(f"\nConstraint adherence: Initial {init_pass}/4 | Refined {ref_pass}/4")

    # ---- Summary ----
    print("\n" + "=" * 72)
    print("  SUMMARY")
    print("=" * 72)
    print("""
Findings:

1. INITIAL PROMPT
   - Plain prose constraints leave room for interpretation
   - The model may include the banned word 'smart' if it appears in
     the product name it invents
   - Bullet format may drift (numbered list instead of dashes, or
     more/fewer than 3 bullets)

2. REFINED PROMPT
   - Renaming the product ("fitness watch") removes the risk of using
     the banned word
   - Providing an explicit example format anchors the style
   - Numbering the constraints and using "MUST" / "Do NOT" makes
     them more emphatic
   - The model's output tends to match the example's structure

3. GENERAL PRINCIPLES
   - Constraints work best when they are specific and unambiguous
   - Examples are more powerful than descriptions
   - If a word is banned, remove reasons to use it (like a name that
     contains the word)
   - Always check compliance programmatically - humans miss violations
""")
