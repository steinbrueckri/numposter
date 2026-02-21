"""Base protocol and utilities for poster generators."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from src.core import PaperConfig, PosterConfig, SCHEMES, build_latex, render_mask


@dataclass(frozen=True)
class PosterGenerator:
    """Descriptor for a poster type: text builder + config factory."""

    name: str
    output_name: str
    build_text_grid: "TextGridBuilder"
    mask_char: str | None = None
    default_seed: int = 9
    mask_image: Path | None = None
    mask_image_scale: float = 1.0

    def make_config(
        self,
        scheme_name: str,
        seed: int | None = None,
        paper: PaperConfig | None = None,
    ) -> PosterConfig:
        return PosterConfig(
            paper=paper if paper is not None else PaperConfig(),
            scheme=SCHEMES[scheme_name],
            seed=seed if seed is not None else self.default_seed,
            mask_char=self.mask_char,
            mask_image=self.mask_image,
            mask_image_scale=self.mask_image_scale,
            output_name=self.output_name,
        )

    def generate(
        self,
        scheme_name: str,
        seed: int | None = None,
        paper: PaperConfig | None = None,
        paper_key: str = "a3plus",
        out_dir: Path = Path("build"),
    ) -> Path:
        cfg = self.make_config(scheme_name, seed, paper)
        lines = self.build_text_grid(
            cfg.paper.grid_cols, cfg.paper.grid_rows, cfg.seed
        )
        mask = render_mask(cfg)
        tex = build_latex(lines, mask, cfg)

        out_dir.mkdir(exist_ok=True)
        out = out_dir / f"{self.output_name}_{scheme_name}_{paper_key}.tex"
        out.write_text(tex, encoding="utf-8")
        return out


class TextGridBuilder(Protocol):
    def __call__(self, cols: int, rows: int, seed: int) -> list[str]: ...
