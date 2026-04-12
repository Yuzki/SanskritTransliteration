import csv
import importlib.resources
import re
import unicodedata
from functools import lru_cache
from typing import Dict, List, Tuple

# Canonical scheme IDs (column names in CSV)
_CANONICAL_IDS = ("iast", "iso", "ipa", "tf", "kh", "slp1", "csx")

# Case-insensitive alias -> canonical ID mapping
_ALIASES: Dict[str, str] = {
    "iast": "iast",
    "iso": "iso",
    "iso 15919": "iso",
    "iso15919": "iso",
    "ipa": "ipa",
    "tf": "tf",
    "tokunaga-fujii": "tf",
    "tokunagafujii": "tf",
    "kh": "kh",
    "harvard-kyoto": "kh",
    "harvardkyoto": "kh",
    "slp1": "slp1",
    "csx": "csx",
}


def _normalize_scheme(name: str) -> str:
    """Normalize a scheme name to its canonical ID."""
    key = name.strip().lower()
    canonical = _ALIASES.get(key)
    if canonical is None:
        available = ", ".join(
            f"{cid} (aliases: {', '.join(a for a, c in _ALIASES.items() if c == cid and a != cid)})"
            if any(a for a, c in _ALIASES.items() if c == cid and a != cid)
            else cid
            for cid in _CANONICAL_IDS
        )
        raise ValueError(
            f"Unknown transliteration scheme: {name!r}. Available schemes: {available}"
        )
    return canonical


@lru_cache(maxsize=1)
def _load_table() -> Tuple[List[str], List[List[str]]]:
    """Load and cache the CSV table. Returns (header, rows)."""
    with importlib.resources.open_text(
        "SanskritTransliteration",
        "transliteration_table.csv",
        encoding="utf-8",
    ) as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = [[unicodedata.normalize("NFC", cell) for cell in row] for row in reader]
    for cid in _CANONICAL_IDS:
        if cid not in header:
            raise RuntimeError(f"Missing expected column {cid!r} in CSV header")
    return header, rows


def _build_mapping(
    header: List[str],
    rows: List[List[str]],
    src_col: int,
    dst_col: int,
) -> List[Tuple[str, str]]:
    """Build an ordered list of (source_token, dest_token) pairs.

    First-win: if the same source token appears in multiple rows, only the
    first occurrence is kept.  The list is sorted by descending token length
    (then CSV order for ties) so that longer tokens match first.
    """
    seen: dict[str, str] = {}
    order: list[str] = []
    for row in rows:
        src = row[src_col]
        dst = row[dst_col]
        if src and src not in seen:
            seen[src] = dst
            order.append(src)

    # Sort: longest first; ties keep original CSV order
    pairs: List[Tuple[str, str]] = []
    for token in sorted(order, key=lambda t: (-len(t), order.index(t))):
        pairs.append((token, seen[token]))
    return pairs


def transliterate(
    text: str,
    input_method: str,
    output_method: str,
) -> str:
    """Transliterate text from one method to another.

    :param text: The text to transliterate.
    :param input_method: The input method to transliterate from.
    :param output_method: The output method to transliterate to.
    :return: The transliterated text.
    """
    text = unicodedata.normalize("NFC", text)

    src_scheme = _normalize_scheme(input_method)
    dst_scheme = _normalize_scheme(output_method)

    if src_scheme == dst_scheme:
        return text

    header, rows = _load_table()
    src_col = header.index(src_scheme)
    dst_col = header.index(dst_scheme)

    pairs = _build_mapping(header, rows, src_col, dst_col)
    if not pairs:
        return text

    # Build a single regex alternation from all source tokens,
    # escaped so special regex chars are treated as literals.
    pattern = "|".join(re.escape(src) for src, _ in pairs)
    lookup = {src: dst for src, dst in pairs}

    return re.sub(pattern, lambda m: lookup[m.group()], text)


if __name__ == "__main__":
    s = transliterate(
        "agn;im ii;le pur;ohitam",
        "tf",
        "iso",
    )
    print(s)
