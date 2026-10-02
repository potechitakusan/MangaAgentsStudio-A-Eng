"""Render panel geometry and numbered previews with Pillow, without a browser."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / 'templates/manga-project/templates/panel-templates'


def font(size):
    for name in ('arial.ttf', 'DejaVuSans.ttf'):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)


def render(item, canvas, guide=False):
    scale = canvas.get('pngScale', 2)
    image = Image.new('RGBA', (int(canvas['width'] * scale), int(canvas['height'] * scale)),
                      '#f6f4ee' if guide else (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    palette = ['#e8edf4', '#f2efe9', '#edf4eb', '#f4ebeb']
    stroke = max(1, round(canvas.get('frameStroke', 5) * scale))
    for panel in item['panels']:
        polygon = [(round(x * scale), round(y * scale)) for x, y in panel['polygon']]
        if guide:
            draw.polygon(polygon, fill=palette[(panel['row'] - 1) % len(palette)])
        draw.line(polygon + polygon[:1], fill='#111111' if guide else '#000000', width=stroke, joint='curve')
    if guide:
        for modifier in item.get('modifiers', []):
            if modifier['type'] != 'character-breakout':
                continue
            overlay = Image.new('RGBA', image.size)
            region = [(round(x * scale), round(y * scale)) for x, y in modifier['region']]
            layer_draw = ImageDraw.Draw(overlay)
            layer_draw.polygon(region, fill=(206, 135, 73, 51))
            layer_draw.line(region + region[:1], fill='#a85e27', width=round(4 * scale))
            image = Image.alpha_composite(image, overlay)
            draw = ImageDraw.Draw(image)
            center = sum(x for x, _ in region) / len(region)
            draw.text((center, 750 * scale), 'Character\nbreakout', font=font(round(22 * scale)),
                      fill='#8a491e', anchor='mm', align='center')
        for panel in item['panels']:
            x = sum(v[0] for v in panel['polygon']) / len(panel['polygon']) * scale
            y = sum(v[1] for v in panel['polygon']) / len(panel['polygon']) * scale
            radius = 30 * scale
            draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill='#213c37')
            draw.text((x, y), str(panel['order']), font=font(round(32 * scale)), fill='white', anchor='mm')
    return image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path, nargs='?', default=DEFAULT)
    parser.add_argument('--all', action='store_true', help='Regenerate existing images too.')
    args = parser.parse_args()
    data = json.loads((args.directory / 'catalog.json').read_text(encoding='utf-8-sig'))
    count = 0
    for item in data['templates']:
        for guide, key in ((False, 'transparentPng'), (True, 'previewPng')):
            target = args.directory / item['assets'][key]
            if target.exists() and not args.all:
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            render(item, data['canvas'], guide).save(target, format='PNG')
            count += 1
    print(json.dumps({'templates': len(data['templates']), 'renderedImages': count}))


if __name__ == '__main__':
    main()
