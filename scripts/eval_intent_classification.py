"""
Intent classification evaluation — 10 sample queries for documentation and demos.

Runs the same logic as LangGraph node_classify_intent (keywords first, then optional LLM).

Usage:
  python scripts/eval_intent_classification.py
  python scripts/eval_intent_classification.py --llm   # also test LLM path (needs API key)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config.settings import _load_env_file

_load_env_file()

# Expected intent labels match src/rag/prompts.py INTENT_LABELS
EVAL_CASES: list[tuple[str, str]] = [
    ("Why are my cotton leaves turning yellow?", "pest_disease"),
    ("What is tomato price today?", "market_price"),
    ("When should I irrigate wheat in this heat?", "irrigation"),
    ("How much urea should I apply for paddy?", "input_recommendation"),
    ("Am I eligible for PM-KISAN scheme?", "scheme_information"),
    ("How do I file crop insurance claim?", "insurance"),
    ("Whiteflies and bollworm on cotton plants", "pest_disease"),
    ("Mandi rate for soybean in Indore", "market_price"),
    ("Drip irrigation schedule for chilli", "irrigation"),
    ("Government subsidy scheme for small farmers", "scheme_information"),
]


def classify_query(query: str, *, use_llm: bool = False) -> tuple[str, float, str]:
    """Return (intent, confidence, source) using production classifier logic."""
    from src.graph.intent_classifier import classify_intent

    return classify_intent(query, use_llm=use_llm)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate intent classification accuracy")
    parser.add_argument(
        "--llm",
        action="store_true",
        help="Use LLM when keywords do not match (requires GEMINI_API_KEY or OPENAI_API_KEY)",
    )
    args = parser.parse_args()

    print("=== Intent classification evaluation ===\n")
    print("| # | Sample query | Expected | Actual | OK | Source |")
    print("|---|--------------|----------|--------|----|--------|")

    correct = 0
    for i, (query, expected) in enumerate(EVAL_CASES, start=1):
        actual, conf, source = classify_query(query, use_llm=args.llm)
        ok = actual == expected
        if ok:
            correct += 1
        q_short = query if len(query) <= 42 else query[:39] + "..."
        mark = "yes" if ok else "no"
        print(f"| {i} | {q_short} | `{expected}` | `{actual}` | {mark} | {source} |")

    total = len(EVAL_CASES)
    pct = int(100 * correct / total) if total else 0
    print(f"\n**Score: {correct}/{total} ({pct}%)** — keyword-first classifier (production path).")
    if not args.llm:
        print("Tip: run with --llm to test structured LLM classification on unmatched queries.")
    print("\nCopy the table into project documentation under 'Classification accuracy (sample evaluation)'.")

    if pct < 100:
        sys.exit(0)  # report only; do not fail CI on partial keyword coverage
    print("\nAll sample queries classified as expected.")


if __name__ == "__main__":
    main()
