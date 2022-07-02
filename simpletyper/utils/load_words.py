import random
from pathlib import Path

WORD_LIST_PATH = Path(__file__).parents[1].resolve() / "words"


def load_words(file: str, limit: int) -> str:
    with open(WORD_LIST_PATH / file) as f:
        words = random.choices(f.read().split("\n"), k=limit)
        return (" ".join(words)).strip()
