"""Poster: 11 – alternating sum of digits (divisibility rule)."""

from __future__ import annotations

import random

from src.posters.base import PosterGenerator


def _alternating_sum(n: int) -> int:
    """Alternating sum: d0 - d1 + d2 - d3 + ..."""
    digits = [int(d) for d in str(n)]
    return sum(d * (-1) ** i for i, d in enumerate(digits))


def _make_example(seed: int) -> str:
    random.seed(seed)
    n = random.randint(11, 99999)
    alt = _alternating_sum(n)
    div = "Y" if alt % 11 == 0 else "N"
    return f"11|{n}? alt={alt} {div} "


def build_text_grid(cols: int, rows: int, seed: int) -> list[str]:
    lines: list[str] = []
    for row in range(rows):
        row_seed = seed * 10_000 + row
        line = _make_example(row_seed)
        while len(line) < cols:
            line += _make_example(row_seed + len(line))
        lines.append(line[:cols])
    return lines


poster_11 = PosterGenerator(
    name="11 – Alternating Sum",
    mask_char="11",
    output_name="poster_11",
    build_text_grid=build_text_grid,
    default_seed=11,
)
