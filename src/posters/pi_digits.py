"""Poster: π – digits."""

from __future__ import annotations

from mpmath import mp

from src.posters.base import PosterGenerator

# Arbitrary-precision π via mpmath (Chudnovsky algorithm)
mp.dps = 50_000
_PI_DIGITS = str(mp.pi).replace(".", "")


def build_text_grid(cols: int, rows: int, seed: int) -> list[str]:
    """Fill grid with digits of pi (one char per mask pixel)."""
    pi = _PI_DIGITS
    n = len(pi)
    total = cols * rows
    # Take exactly total chars from pi, wrapping as needed
    chars: list[str] = []
    pos = seed % n
    for _ in range(total):
        chars.append(pi[pos])
        pos = (pos + 1) % n
    # Split into rows of exactly cols chars
    return ["".join(chars[i : i + cols]) for i in range(0, total, cols)]


poster_pi = PosterGenerator(
    name="π – Digits",
    mask_char="π",
    output_name="poster_pi",
    build_text_grid=build_text_grid,
    default_seed=0,
)
