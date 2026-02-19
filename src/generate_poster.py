#!/usr/bin/env python3
"""CLI to generate numposter .tex files for various mathematical patterns."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.core import SCHEMES
from src.posters import POSTERS


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
    args = parser.parse_args()

    poster_names = list(POSTERS) if args.poster == "all" else [args.poster]
    scheme_names = list(SCHEMES) if args.scheme == "all" else [args.scheme]

    generated: list[Path] = []
    for poster_name in poster_names:
        gen = POSTERS[poster_name]
        for scheme_name in scheme_names:
            out = gen.generate(scheme_name=scheme_name)
            generated.append(out)
            cfg = gen.make_config(scheme_name)
            page = cfg.page
            print(
                f"✔ wrote {out} "
                f"(A3+ {page.width_mm}x{page.height_mm}mm, "
                f"grid {page.grid_cols}x{page.grid_rows}, "
                f"poster={poster_name}, scheme={scheme_name})"
            )

    # Write list for justfile so only these files get compiled
    list_file = Path("build") / ".generated"
    list_file.parent.mkdir(exist_ok=True)
    list_file.write_text("\n".join(str(p) for p in generated), encoding="utf-8")


if __name__ == "__main__":
    main()
