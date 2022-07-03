import random
from pathlib import Path

WORD_LIST_PATH = Path(__file__).parents[1].resolve() / "words"


def load_words(file: str, limit: int) -> str:
    with open(WORD_LIST_PATH / file) as general_list, open(
        WORD_LIST_PATH / "commonly_misspelled"
    ) as commonly_misspelled, open(WORD_LIST_PATH / "most_common1000") as most_common:
        general_list_words = general_list.read().strip().split("\n")
        commonly_misspelled_words = commonly_misspelled.read().strip().split("\n")
        most_common_words = most_common.read().strip().split("\n")
        all_words = general_list_words + commonly_misspelled_words + most_common_words
        weights = (
            (len(general_list_words) * [20])
            + (len(commonly_misspelled_words) * [10])
            + (len(most_common_words) * [50])
        )
        words = random.choices(
            all_words,
            weights=weights,
            k=limit,
        )
        return (" ".join(words)).strip()
