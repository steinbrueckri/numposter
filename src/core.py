#!/usr/bin/env python3
"""Shared infrastructure for numposter: themes, paper config, mask, LaTeX."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import groupby
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


# =========================
# Configuration
# =========================
@dataclass(frozen=True)
class ColorScheme:
    """All color logic lives here — no branching elsewhere."""

    preamble: str
    min_pct: int
    max_pct: int
    color_template: str

    def color_for(self, value: int, levels: int) -> str:
        level = round(value / 255 * levels)
        pct = self.min_pct + round(level / levels * (self.max_pct - self.min_pct))
        return self.color_template.format(pct=pct)


SCHEMES: dict[str, ColorScheme] = {
    "print": ColorScheme(
        preamble="",
        min_pct=20,
        max_pct=100,
        color_template="black!{pct}",
    ),
    "matrix": ColorScheme(
        preamble=(
            r"\definecolor{fgin}{RGB}{0,230,60}"
            "\n"
            r"\definecolor{fgout}{RGB}{0,70,0}"
            "\n"
            r"\pagecolor{black}"
        ),
        min_pct=0,
        max_pct=100,
        color_template="fgin!{pct}!fgout",
    ),
    "blueprint": ColorScheme(
        preamble=(
            r"\definecolor{bpfg}{RGB}{200,230,255}"
            "\n"
            r"\definecolor{bpbg}{RGB}{40,70,110}"
            "\n"
            r"\pagecolor[RGB]{10,30,60}"
        ),
        min_pct=0,
        max_pct=100,
        color_template="bpfg!{pct}!bpbg",
    ),
    "ember": ColorScheme(
        preamble=(
            r"\definecolor{emberfg}{RGB}{255,180,30}"
            "\n"
            r"\definecolor{emberbg}{RGB}{80,20,0}"
            "\n"
            r"\pagecolor[RGB]{15,5,0}"
        ),
        min_pct=0,
        max_pct=100,
        color_template="emberfg!{pct}!emberbg",
    ),
}


@dataclass(frozen=True)
class PaperConfig:
    width_mm: int = 329
    height_mm: int = 483
    margin_mm: int = 0
    grid_cols: int = 259
    grid_rows: int = 195
    font_size_pt: float = 6.0
    line_height_pt: float = 7.0
    char_width_pt: float = 3.6


BASE_PAPER = PaperConfig()


def scaled_paper(
    *, width_mm: int, height_mm: int, base: PaperConfig = BASE_PAPER
) -> PaperConfig:
    """Scale grid dimensions from the base paper to keep glyph density stable."""
    return PaperConfig(
        width_mm=width_mm,
        height_mm=height_mm,
        margin_mm=base.margin_mm,
        grid_cols=max(1, round(base.grid_cols * width_mm / base.width_mm)),
        grid_rows=max(1, round(base.grid_rows * height_mm / base.height_mm)),
        font_size_pt=base.font_size_pt,
        line_height_pt=base.line_height_pt,
        char_width_pt=base.char_width_pt,
    )


PAPER_FORMATS: dict[str, PaperConfig] = {
    "a3plus": BASE_PAPER,
    "a3": scaled_paper(width_mm=297, height_mm=420),
    "a4": scaled_paper(width_mm=210, height_mm=297),
}


@dataclass(frozen=True)
class PosterConfig:
    """Base config for any poster. Poster-specific params passed via overrides."""

    paper: PaperConfig = PaperConfig()
    scheme: ColorScheme = SCHEMES["print"]
    seed: int = 9
    edge_soften: float = 1.2
    quantize_levels: int = 20
    mask_char: str | None = None
    mask_image: Path | None = None
    mask_image_scale: float = 1.0
    mask_render_scale: int = 10
    mask_glyph_fill: float = 0.95
    output_name: str = "poster"


# =========================
# Font
# =========================
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
FONT_PATH = _PROJECT_ROOT / "fonts" / "FiraMono-Regular.otf"


def load_font(size_px: int) -> ImageFont.FreeTypeFont:
    if not FONT_PATH.exists():
        raise RuntimeError(f"Font not found: {FONT_PATH}\nRun 'just fetch-font' first.")
    return ImageFont.truetype(str(FONT_PATH), size_px)


# =========================
# Mask generation
# =========================
def _render_char_mask(cfg: PosterConfig) -> Image.Image:
    """Render a single-character glyph as grayscale mask."""
    paper = cfg.paper
    scale = cfg.mask_render_scale

    h_px = paper.grid_rows * scale
    aspect = paper.char_width_pt / paper.line_height_pt
    w_px = round(paper.grid_cols * scale * aspect)

    img = Image.new("L", (w_px, h_px), 0)
    draw = ImageDraw.Draw(img)

    max_font_size = int(h_px * cfg.mask_glyph_fill)
    font = load_font(max_font_size)
    bbox = draw.textbbox((0, 0), cfg.mask_char, font=font)
    actual_w = bbox[2] - bbox[0]
    actual_h = bbox[3] - bbox[1]
    fit_scale = min(1.0, (w_px * 0.95) / actual_w, (h_px * 0.95) / actual_h)
    font_size = max(10, int(max_font_size * fit_scale))
    font = load_font(font_size)

    # Centre using actual ink bounds rather than font-metric anchor
    bbox = draw.textbbox((0, 0), cfg.mask_char, font=font)
    x = w_px // 2 - (bbox[0] + bbox[2]) // 2
    y = h_px // 2 - (bbox[1] + bbox[3]) // 2
    draw.text((x, y), cfg.mask_char, fill=255, font=font)

    blur = scale * cfg.edge_soften * aspect
    img = img.filter(ImageFilter.GaussianBlur(radius=blur))
    return img


def _render_image_mask(cfg: PosterConfig) -> Image.Image:
    """Load an image file and convert it to a grayscale mask.

    The image is first scaled to fit (contain) the canvas, then multiplied
    by ``mask_image_scale`` (>1 = larger, cropped at edges).
    """
    from PIL import ImageOps

    paper = cfg.paper
    scale = cfg.mask_render_scale
    h_px = paper.grid_rows * scale
    aspect = paper.char_width_pt / paper.line_height_pt
    w_px = round(paper.grid_cols * scale * aspect)

    src = Image.open(cfg.mask_image).convert("L")

    # Contain: determine size that fits inside canvas
    ratio = min(w_px / src.width, h_px / src.height) * cfg.mask_image_scale
    new_w = round(src.width * ratio)
    new_h = round(src.height * ratio)
    src = src.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # Centre-paste (overflow is clipped naturally)
    img = Image.new("L", (w_px, h_px), 0)
    paste_x = (w_px - new_w) // 2
    paste_y = (h_px - new_h) // 2
    img.paste(src, (paste_x, paste_y))

    img = ImageOps.invert(img)

    blur = scale * cfg.edge_soften * aspect
    img = img.filter(ImageFilter.GaussianBlur(radius=blur))
    return img


def render_mask(cfg: PosterConfig) -> Image.Image:
    if cfg.mask_image is not None:
        raw = _render_image_mask(cfg)
    elif cfg.mask_char:
        raw = _render_char_mask(cfg)
    else:
        raise ValueError("PosterConfig needs either mask_char or mask_image")
    return raw.resize(
        (cfg.paper.grid_cols, cfg.paper.grid_rows), Image.Resampling.LANCZOS
    )


# =========================
# LaTeX output
# =========================
_LATEX_SPECIAL = str.maketrans(
    {
        "\\": r"\textbackslash ",
        "&": r"\&",
        "%": r"\%",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
    }
)


def latex_escape(s: str) -> str:
    return s.translate(_LATEX_SPECIAL)


def _shaded_line(text: str, mask_row: list[int], cfg: PosterConfig) -> str:
    scheme = cfg.scheme

    def _color_key(pair: tuple[str, int]) -> str:
        return scheme.color_for(pair[1], cfg.quantize_levels)

    parts: list[str] = []
    for color, group in groupby(zip(text, mask_row), key=_color_key):
        chars = latex_escape("".join(ch for ch, _ in group))
        parts.append(rf"\textcolor{{{color}}}{{{chars}}}")
    return "".join(parts)


_LATEX_TEMPLATE = r"""\documentclass[final]{{article}}
\usepackage[
  paperwidth={width_mm}mm,
  paperheight={height_mm}mm,
  margin={margin_mm}mm
]{{geometry}}
\usepackage{{fontspec}}
\usepackage{{microtype}}
\usepackage{{xcolor}}{color_preamble}
\setmonofont{{FiraMono-Regular}}[Path=fonts/,Extension=.otf]
\renewcommand{{\familydefault}}{{\ttdefault}}
\setlength{{\parindent}}{{0pt}}
\setlength{{\topskip}}{{0pt}}
\setlength{{\parskip}}{{0pt}}
\pagestyle{{empty}}

\begin{{document}}
\centering
\vspace*{{\stretch{{1}}}}\noindent
\fontsize{{{font_size_pt}}}{{{line_height_pt}}}\selectfont
{body}
\vspace*{{\stretch{{2}}}}
\end{{document}}
"""


def build_latex(lines: list[str], mask: Image.Image, cfg: PosterConfig) -> str:
    px = mask.load()

    body_lines: list[str] = []
    for y, line in enumerate(lines):
        row_mask = [px[x, y] for x in range(mask.width)]
        body_lines.append(_shaded_line(line, row_mask, cfg) + r"\\")

    preamble = cfg.scheme.preamble
    if preamble:
        preamble = "\n" + preamble

    return _LATEX_TEMPLATE.format(
        width_mm=cfg.paper.width_mm,
        height_mm=cfg.paper.height_mm,
        margin_mm=cfg.paper.margin_mm,
        color_preamble=preamble,
        font_size_pt=cfg.paper.font_size_pt,
        line_height_pt=cfg.paper.line_height_pt,
        body="\n".join(body_lines),
    )
