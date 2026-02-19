"""Poster: Primes – distribution (sieve of Eratosthenes / prime gaps)."""

from __future__ import annotations

from src.posters.base import PosterGenerator


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    for d in range(2, int(n**0.5) + 1):
        if n % d == 0:
            return False
    return True


def _prime_stream(start: int = 2):
    """Yield primes starting from start."""
    n = start
    while True:
        if _is_prime(n):
            yield n
        n += 1


def build_text_grid(cols: int, rows: int, seed: int) -> list[str]:
    """Fill grid with prime numbers and gaps."""
    lines: list[str] = []
    gen = _prime_stream(seed)
    for _ in range(rows):
        line_parts: list[str] = []
        while sum(len(p) for p in line_parts) < cols:
            p = next(gen)
            line_parts.append(str(p) + " ")
        line = "".join(line_parts)[:cols]
        lines.append(line)
    return lines


poster_primes = PosterGenerator(
    name="Primes – Distribution",
    mask_char="÷",
    output_name="poster_primes",
    build_text_grid=build_text_grid,
    default_seed=2,
)
