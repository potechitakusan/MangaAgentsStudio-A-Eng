"""Interpolate transparent monochrome asset luminance between two colors. Requires only Pillow."""

from __future__ import annotations

import argparse
from io import BytesIO
import os
from pathlib import Path
import re
import tempfile
from typing import Sequence

from PIL import Image, ImageChops


def parse_color(value: str) -> tuple[int, int, int]:
    """Accept only #RRGGBB; no color names, shorthand, or alpha."""
    if not isinstance(value, str) or re.fullmatch(r"#[0-9a-fA-F]{6}", value) is None:
        raise ValueError("Specify colors as six ASCII hexadecimal digits in #RRGGBB format.")
    return tuple(int(value[index:index + 2], 16) for index in (1, 3, 5))


def _colors(
    ink_color: str | None, white_color: str | None, monochrome: bool
) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    ink = (0, 0, 0) if ink_color is None else parse_color(ink_color)
    white = (255, 255, 255) if white_color is None else parse_color(white_color)
    # Monochrome takes precedence, but invalid colors are still rejected.
    return ((0, 0, 0), (255, 255, 255)) if monochrome else (ink, white)


def recolor_image(
    image: Image.Image,
    *,
    ink_color: str | None = None,
    white_color: str | None = None,
    monochrome: bool = False,
) -> Image.Image:
    """Return a new RGBA image without changing input or inheriting metadata.

    Visible pixels (alpha > 0) must have exactly R=G=B.
    Reject fully opaque images, multiple frames, and modes not losslessly convertible to 8-bit RGBA.
    Each RGB component corresponds to round((ink * (255-L) + white * L) / 255).
    Preserve every alpha value and RGB values of fully transparent pixels.
    """
    ink, white = _colors(ink_color, white_color, monochrome)
    if getattr(image, "n_frames", 1) != 1:
        raise ValueError("Multiple frames are unsupported. Specify one still image.")
    if image.mode not in {"1", "L", "LA", "P", "PA", "RGB", "RGBA"}:
        raise ValueError("Input must be an 8-bit RGB, grayscale, or palette image.")
    converted = image.convert("RGBA")
    # Do not transfer input attributes, including EXIF cache, into the new image.
    rgba = Image.frombytes("RGBA", converted.size, converted.tobytes())
    red, green, blue, alpha = rgba.split()
    if alpha.getextrema()[0] == 255:
        raise ValueError("Fully opaque assets are unsupported. Use an asset with a transparent background.")
    visible = alpha.point([0] + [255] * 255)
    difference = ImageChops.lighter(
        ImageChops.difference(red, green), ImageChops.difference(red, blue)
    )
    if ImageChops.multiply(difference, visible).getbbox() is not None:
        raise ValueError("Visible pixels contain non-monochrome colors. Use R=G=B assets.")
    if ink == (0, 0, 0) and white == (255, 255, 255):
        return rgba
    channels = [
        red.point([(start * (255 - level) + end * level + 127) // 255
                   for level in range(256)])
        for start, end in zip(ink, white)
    ]
    result = Image.merge("RGBA", (*channels, alpha))
    # Exclude hidden RGB in transparent areas from interpolation and preserve original values.
    result.paste(rgba, (0, 0), ImageChops.invert(visible))
    return result


def _check_output(source: Path, target: Path, overwrite: bool) -> None:
    if source.resolve() == target.resolve() or (
        target.exists() and source.samefile(target)
    ):
        raise ValueError("Output cannot overwrite the input file, including through links.")
    if target.exists() and not target.is_file():
        raise ValueError("Specify an output filename.")
    if os.path.lexists(target) and not overwrite:
        raise FileExistsError("Output already exists. Specify --overwrite to replace it.")


def recolor_file(
    input_path: str | os.PathLike[str],
    output_path: str | os.PathLike[str] | None = None,
    *,
    ink_color: str | None = None,
    white_color: str | None = None,
    monochrome: bool = False,
    overwrite: bool = False,
) -> Path:
    """Validate, recolor, and return destination; unchanged with no output returns the absolute input path.

    Output is PNG or lossless WebP only. Always reject identical input/output files.
    Even unchanged output is re-encoded from pixels without copying input metadata.
    """
    _colors(ink_color, white_color, monochrome)
    source = Path(input_path).resolve(strict=True)
    target = Path(output_path).absolute() if output_path is not None else None
    if target is None and not monochrome and (ink_color is not None or white_color is not None):
        raise ValueError("Recoloring requires --output.")
    if target is not None:
        if target.suffix.lower() not in {".png", ".webp"}:
            raise ValueError("Output format must be .png or .webp.")
        _check_output(source, target, overwrite)
    with Image.open(source) as image:
        result = recolor_image(
            image, ink_color=ink_color, white_color=white_color, monochrome=monochrome
        )
    if target is None:
        return source

    # On encoding failure, leave existing output and output folders untouched.
    with BytesIO() as buffer:
        if target.suffix.lower() == ".png":
            result.save(buffer, format="PNG")
        else:
            result.save(buffer, format="WEBP", lossless=True, exact=True, method=6)
        encoded = buffer.getvalue()
    _check_output(source, target, overwrite)
    target.parent.mkdir(parents=True, exist_ok=True)
    if not overwrite:
        # Exclusive creation also protects files created after preflight checks.
        with target.open("xb") as stream:
            stream.write(encoded)
    else:
        # For overwrite, replace only after successful writing to protect existing output.
        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(dir=target.parent, prefix=".recolor-", delete=False) as stream:
                temporary_path = Path(stream.name)
                stream.write(encoded)
            _check_output(source, target, overwrite)
            os.replace(temporary_path, target)
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
    return target.resolve()


def main(argv: Sequence[str] | None = None) -> int:
    """CLI: 0 on success; 2 for input or save errors."""
    parser = argparse.ArgumentParser(
        description="Recolor transparent monochrome assets using two colors and save as PNG or lossless WebP.",
        epilog="Visible pixels require R=G=B. No fully opaque images, multiple frames, color names, or alpha colors.",
    )
    parser.add_argument("--input", required=True, type=Path, help="Input transparent monochrome image")
    parser.add_argument("--output", type=Path, help="Derived .png/.webp output; optional when unchanged")
    parser.add_argument("--ink-color", metavar="#RRGGBB", help="Color for black areas (default black)")
    parser.add_argument("--white-color", metavar="#RRGGBB", help="Color for white areas (default white)")
    parser.add_argument("--monochrome", action="store_true", help="Preserve original pixels, overriding color choices")
    parser.add_argument("--overwrite", action="store_true", help="Allow overwriting existing derived output")
    args = parser.parse_args(argv)
    try:
        path = recolor_file(
            args.input, args.output, ink_color=args.ink_color, white_color=args.white_color,
            monochrome=args.monochrome, overwrite=args.overwrite,
        )
    except (OSError, ValueError, Image.DecompressionBombError) as exc:
        parser.exit(2, f"Error: {exc}\n")
    print(f"Saved to: {path}" if args.output is not None else f"Use original asset:{path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
