"""Create PixAI inpainting masks (white = redraw, black = keep original) matching the exact dimensions of a source image. No network communication.

  python -X utf8 scripts/pixai_mask.py --image output/pixai/candidates/p04-01/r001.png --ellipse 300,40,260,180 \
      --out input/pixai/masks/p04-01-ears.png

Specify `--ellipse` and `--rect` as `left,top,width,height` (px); each flag can be repeated. `--blur` feathers the boundary (default 10px).
Also writes `<out>.preview.png` overlaying the mask in red onto the source image for visual verification before sending.
Include generous headroom where new elements will appear (e.g. background above the head for ears) and exclude major shapes you do not want redrawn.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pixai_api as api  # noqa: E402


def box(value: str) -> tuple[int, int, int, int]:
    parts = [int(v) for v in value.split(",")]
    if len(parts) != 4 or parts[2] <= 0 or parts[3] <= 0:
        raise argparse.ArgumentTypeError("Specify 4 integers as left,top,width,height (with positive width and height).")
    return parts[0], parts[1], parts[0] + parts[2], parts[1] + parts[3]


def make_mask(size: tuple[int, int], ellipses, rects, blur: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    for shape in ellipses:
        draw.ellipse(shape, fill=255)
    for shape in rects:
        draw.rectangle(shape, fill=255)
    return mask.filter(ImageFilter.GaussianBlur(blur)) if blur > 0 else mask


def preview(source: Image.Image, mask: Image.Image) -> Image.Image:
    red = Image.new("RGB", source.size, (255, 0, 0))
    return Image.composite(red, source.convert("RGB"), mask.point(lambda v: v * 55 // 100))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Create an inpainting mask (white = redraw)")
    parser.add_argument("--image", required=True, help="Source image (relative path inside the project)")
    parser.add_argument("--ellipse", type=box, action="append", default=[], help="left,top,width,height")
    parser.add_argument("--rect", type=box, action="append", default=[], help="left,top,width,height")
    parser.add_argument("--blur", type=int, default=10, help="Boundary blur radius (px)")
    parser.add_argument("--out", required=True, help="Destination PNG (relative path inside the project)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files with the same name")
    opts = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    try:
        if not opts.ellipse and not opts.rect:
            raise api.ClientError("Specify at least one --ellipse or --rect.")
        out = api.project_path(root, opts.out)
        if out.suffix.lower() != ".png":
            raise api.ClientError("--out must end with .png.")
        check = out.with_name(out.stem + ".preview.png")
        if not opts.force and (out.exists() or check.exists()):
            raise api.ClientError(f"{opts.out} or its preview image already exists. Pass --force to overwrite.")
        with Image.open(api.project_path(root, opts.image)) as source:
            source.load()
            mask = make_mask(source.size, opts.ellipse, opts.rect, opts.blur)
            out.parent.mkdir(parents=True, exist_ok=True)
            mask.save(out)
            preview(source, mask).save(check)
        share = sum(mask.histogram()[128:]) / (mask.width * mask.height)
        print(f"Mask: {opts.out} ({mask.width}x{mask.height}px, white area {share:.0%})")
        print(f"Preview: {check.relative_to(root).as_posix()} (red area will be redrawn)")
        return 0
    except (api.ClientError, OSError) as error:
        print(error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
