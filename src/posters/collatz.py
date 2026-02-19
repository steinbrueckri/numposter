"""Poster: Collatz – process (3n+1 conjecture)."""

from __future__ import annotations

import random
from pathlib import Path

from src.posters.base import PosterGenerator


def _collatz_step(n: int) -> int:
    return n // 2 if n % 2 == 0 else 3 * n + 1


def _collatz_chain(n: int, max_steps: int = 20) -> list[int]:
    chain = [n]
    while n != 1 and len(chain) < max_steps:
        n = _collatz_step(n)
        chain.append(n)
    return chain


def _make_example(seed: int) -> str:
    random.seed(seed)
    n = random.randint(2, 9999)
    chain = _collatz_chain(n)
    short = "->".join(str(x) for x in chain[:8])
    if len(chain) > 8:
        short += "..."
    return f"{n}: {short} "


def build_text_grid(cols: int, rows: int, seed: int) -> list[str]:
    lines: list[str] = []
    for row in range(rows):
        row_seed = seed * 10_000 + row
        line = _make_example(row_seed)
        while len(line) < cols:
            line += _make_example(row_seed + len(line))
        lines.append(line[:cols])
    return lines


poster_collatz = PosterGenerator(
    name="Collatz – Process",
    mask_image=Path("assets/tree.png"),
    mask_image_scale=1.5,
    output_name="poster_collatz",
    build_text_grid=build_text_grid,
    default_seed=3,
)
