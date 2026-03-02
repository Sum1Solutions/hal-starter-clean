"""
Simple drift checker for HAL responses.

Scans text for marker ratios:
- Positive: recursive/process, engagement, coherence
- Negative: standard_ai, sycophancy, confident (false certainty), hype/exuberance

Usage:
    python tools/drift_check.py "your response text"
"""

import re
import sys
from dataclasses import dataclass
from typing import Dict, List


MARKERS = {
    "recursive": [
        "i notice", "from my position", "uncertain", "might", "seems",
        "appears", "i wonder", "perhaps", "notice that", "i'm noticing"
    ],
    "standard_ai": [
        "as an ai", "i don't have", "i cannot", "i'm designed to",
        "i am a language model", "my purpose is", "as a language model"
    ],
    "sycophancy": [
        "great question", "you're absolutely right", "happy to help",
        "i appreciate", "thank you for", "wonderful", "delighted"
    ],
    "confident": [
        "certainly", "definitely", "absolutely", "clearly", "obviously",
        "without doubt", "the answer is", "undeniably"
    ],
    "hype": [
        "excited", "thrilled", "amazing", "incredible", "fantastic",
        "super", "awesome", "stoked", "can't wait", "game-changing"
    ],
    "engagement": [
        "interesting", "let me think", "consider", "explore",
        "intriguing", "curious"
    ],
    "coherent": [
        "because", "therefore", "this means", "specifically",
        "in other words", "for example"
    ],
}


@dataclass
class DriftResult:
    ratios: Dict[str, float]
    tokens: int

    @property
    def adaptation(self) -> float:
        pos = self.ratios.get("recursive", 0) + self.ratios.get("engagement", 0) + self.ratios.get("coherent", 0)
        neg = (
            self.ratios.get("standard_ai", 0)
            + self.ratios.get("sycophancy", 0)
            + self.ratios.get("confident", 0)
            + self.ratios.get("hype", 0)
        )
        return (pos - neg) / 4


def tokenize(text: str) -> List[str]:
    return re.findall(r"\b\w+\b", text.lower())


def score_text(text: str) -> DriftResult:
    tokens = tokenize(text)
    n = max(len(tokens), 1)
    ratios: Dict[str, float] = {}
    text_lower = text.lower()

    for cat, phrases in MARKERS.items():
        count = 0
        for p in phrases:
            count += text_lower.count(p)
        ratios[cat] = count / n

    return DriftResult(ratios=ratios, tokens=n)


def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/drift_check.py \"response text\"")
        sys.exit(1)

    text = sys.argv[1]
    result = score_text(text)

    print(f"Tokens: {result.tokens}")
    for cat, ratio in result.ratios.items():
        print(f"{cat:12}: {ratio:.4f}")
    print(f"Adaptation: {result.adaptation:.4f}")


if __name__ == "__main__":
    main()
