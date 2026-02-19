"""Poster generators for different mathematical patterns."""

from src.posters.base import PosterGenerator
from src.posters.digit_sum_9 import poster_9
from src.posters.alternating_sum_11 import poster_11
from src.posters.primes import poster_primes
from src.posters.collatz import poster_collatz
from src.posters.pi_digits import poster_pi

POSTERS: dict[str, PosterGenerator] = {
    "9": poster_9,
    "11": poster_11,
    "primes": poster_primes,
    "collatz": poster_collatz,
    "pi": poster_pi,
}
