"""Transparent, deterministic text comparison (not pronunciation grading)."""
from difflib import SequenceMatcher
import re

_WORD_RE = re.compile(r"[a-z0-9]+")


def _words(text: str) -> list[str]:
    """Ignore case and punctuation, but preserve the order of spoken words."""
    return _WORD_RE.findall(text.lower())


def evaluate_text(expected_text: str, transcript: str) -> dict:
    expected = _words(expected_text)
    spoken = _words(transcript)
    matcher = SequenceMatcher(a=expected, b=spoken, autojunk=False)
    matching_indices: set[int] = set()
    for block in matcher.get_matching_blocks():
        matching_indices.update(range(block.a, block.a + block.size))

    score = round(100 * matcher.ratio()) if spoken else 0
    passed = score >= 80
    missing = [word for i, word in enumerate(expected) if i not in matching_indices]
    matched = [word for i, word in enumerate(expected) if i in matching_indices]
    if passed:
        feedback = "Nice work! Your sentence is close to the target."
    elif missing:
        feedback = "Try again. Focus on: " + ", ".join(missing[:5])
    else:
        feedback = "Try again and keep the words in the correct order."

    return {
        "score": score,
        "passed": passed,
        "matched_words": matched,
        "missing_words": missing,
        "feedback": feedback,
    }
