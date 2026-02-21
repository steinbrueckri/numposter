#!/usr/bin/env python3
"""CLI to generate numposter .tex files for various mathematical patterns."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.core import PAPER_FORMATS, SCHEMES
from src.posters import POSTERS

PAPER_LABELS = {"a3plus": "A3+", "a3": "A3", "a4": "A4"}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate numposter .tex files for mathematical patterns"
    )
    parser.add_argument(
        "poster",
        nargs="?",
        default="all",
        choices=[*POSTERS, "all"],
        help="poster type (default: all)",
    )
    parser.add_argument(
        "scheme",
        nargs="?",
        default="all",
        choices=[*SCHEMES, "all"],
        help="color scheme (default: all)",
    )
    parser.add_argument(
        "paper",
        nargs="?",
        default="all",
        choices=[*PAPER_FORMATS, "all"],
        help="paper format (default: all)",
    )
    args = parser.parse_args()

    poster_names = list(POSTERS) if args.poster == "all" else [args.poster]
    scheme_names = list(SCHEMES) if args.scheme == "all" else [args.scheme]
    paper_keys = list(PAPER_FORMATS) if args.paper == "all" else [args.paper]

    generated: list[Path] = []
    for poster_name in poster_names:
        gen = POSTERS[poster_name]
        for scheme_name in scheme_names:
            for paper_key in paper_keys:
                paper = PAPER_FORMATS[paper_key]
                out = gen.generate(
                    scheme_name=scheme_name,
                    paper=paper,
                    paper_key=paper_key,
                )
                generated.append(out)
                print(
                    f"✔ wrote {out} "
                    f"({PAPER_LABELS[paper_key]} {paper.width_mm}x{paper.height_mm}mm, "
                    f"grid {paper.grid_cols}x{paper.grid_rows}, "
                    f"poster={poster_name}, scheme={scheme_name})"
                )

    # Write list for justfile so only these files get compiled
    list_file = Path("build") / ".generated"
    list_file.parent.mkdir(exist_ok=True)
    list_file.write_text("\n".join(str(p) for p in generated), encoding="utf-8")


if __name__ == "__main__":
    main()
