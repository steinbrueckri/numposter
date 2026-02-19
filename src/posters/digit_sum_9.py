"""Poster: 9 × n → digit sum → 9."""

from __future__ import annotations

import random

from src.posters.base import PosterGenerator


def _digit_sum_chain(n: int) -> list[int]:
    chain = [n]
    while n >= 10:
        n = sum(int(d) for d in str(n))
        chain.append(n)
    return chain


def _format_chain(chain: list[int]) -> str:
    parts = []
    for a, b in zip(chain, chain[1:]):
        parts.append("+".join(str(d) for d in str(a)) + f"={b}")
    return " -> ".join(parts)


def _make_example(seed: int) -> str:
    random.seed(seed)
    n = random.randint(2, 9999)
    product = 9 * n
    chain = _digit_sum_chain(product)
    return f"9x{n}={product} | {_format_chain(chain)} "


def build_text_grid(cols: int, rows: int, seed: int) -> list[str]:
    lines: list[str] = []
    for row in range(rows):
        row_seed = seed * 10_000 + row
        line = _make_example(row_seed)
        while len(line) < cols:
            line += _make_example(row_seed + len(line))
        lines.append(line[:cols])
    return lines


poster_9 = PosterGenerator(
    name="9 – Digit Sum",
    mask_char="9",
    output_name="poster_9",
    build_text_grid=build_text_grid,
    default_seed=9,
)
