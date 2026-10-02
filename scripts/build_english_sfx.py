"""Render the English SFX catalog from original geometric letter strokes (Pillow)."""
from __future__ import annotations
import argparse
import hashlib
import html
import json
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / 'templates/manga-project/templates/onomatopoeia'
# Original geometric uppercase alphabet. Each stroke is a polyline in a 6x10 cell.
# No font file, traced artwork, or generated Japanese image is used.
GLYPHS = {
 'A': [[(0,10),(3,0),(6,10)],[(1,6),(5,6)]],
 'B': [[(0,10),(0,0),(4,0),(6,2),(4,5),(0,5)],[(4,5),(6,7),(6,8),(4,10),(0,10)]],
 'C': [[(6,1),(4,0),(1,0),(0,2),(0,8),(1,10),(4,10),(6,9)]],
 'D': [[(0,10),(0,0),(3,0),(6,3),(6,7),(3,10),(0,10)]],
 'E': [[(6,0),(0,0),(0,10),(6,10)],[(0,5),(5,5)]],
 'F': [[(6,0),(0,0),(0,10)],[(0,5),(5,5)]],
 'G': [[(6,2),(4,0),(1,0),(0,2),(0,8),(2,10),(6,10),(6,5),(3,5)]],
 'H': [[(0,0),(0,10)],[(6,0),(6,10)],[(0,5),(6,5)]],
 'I': [[(0,0),(6,0)],[(3,0),(3,10)],[(0,10),(6,10)]],
 'J': [[(0,0),(6,0),(6,8),(4,10),(1,10),(0,8)]],
 'K': [[(0,0),(0,10)],[(6,0),(0,6)],[(2,4),(6,10)]],
 'L': [[(0,0),(0,10),(6,10)]],
 'M': [[(0,10),(0,0),(3,5),(6,0),(6,10)]],
 'N': [[(0,10),(0,0),(6,10),(6,0)]],
 'O': [[(2,0),(4,0),(6,2),(6,8),(4,10),(2,10),(0,8),(0,2),(2,0)]],
 'P': [[(0,10),(0,0),(4,0),(6,2),(6,3),(4,5),(0,5)]],
 'Q': [[(2,0),(4,0),(6,2),(6,7),(4,10),(2,10),(0,8),(0,2),(2,0)],[(4,7),(7,11)]],
 'R': [[(0,10),(0,0),(4,0),(6,2),(6,3),(4,5),(0,5)],[(3,5),(6,10)]],
 'S': [[(6,1),(4,0),(1,0),(0,2),(1,4),(5,6),(6,8),(5,10),(1,10),(0,9)]],
 'T': [[(0,0),(6,0)],[(3,0),(3,10)]],
 'U': [[(0,0),(0,8),(2,10),(4,10),(6,8),(6,0)]],
 'V': [[(0,0),(3,10),(6,0)]],
 'W': [[(0,0),(1,10),(3,5),(5,10),(6,0)]],
 'X': [[(0,0),(6,10)],[(6,0),(0,10)]],
 'Y': [[(0,0),(3,5),(6,0)],[(3,5),(3,10)]],
 'Z': [[(0,0),(6,0),(0,10),(6,10)]],
 '!': [[(3,0),(3,6)],[(3,9),(3,10)]],
 '-': [[(1,5),(5,5)]],
 '.': [[(3,9),(3,10)]],
}


def geometry(text, style):
    strokes = []
    cursor = 24
    unit = 16
    for index, char in enumerate(text.upper()):
        if char == ' ':
            cursor += 64
            continue
        if char not in GLYPHS:
            raise ValueError(f'Unsupported lettering character: {char!r}')
        for stroke in GLYPHS[char]:
            points = []
            for x, y in stroke:
                slant = (10-y) * 3 if style != 'block' else 0
                bounce = (-5 if index % 2 else 5) if style == 'burst' else 0
                points.append((cursor + x*unit + slant, 34 + y*unit + bounce))
            strokes.append(points)
        cursor += 135
    return cursor + 24, 240, strokes


def render(text, style):
    width, height, strokes = geometry(text, style)
    scale = 2
    image = Image.new('RGBA', (width*scale, height*scale))
    draw = ImageDraw.Draw(image)
    # White outline gives readable letters over dark artwork; all channels stay grayscale.
    for color, weight in [('white', 27), ('black', 18 if style == 'block' else 16)]:
        for stroke in strokes:
            pts = [(round(x*scale), round(y*scale)) for x,y in stroke]
            draw.line(pts, fill=color, width=weight*scale, joint='curve')
    if style == 'drybrush':
        for i, stroke in enumerate(strokes):
            if len(stroke) > 1 and i % 3 == 0:
                x,y = stroke[0]
                draw.line([(int(x*scale),int(y*scale)),(int((x+6)*scale),int((y+14)*scale))],
                          fill='white',width=2*scale)
    return image.resize((width,height),Image.Resampling.LANCZOS), strokes


def build(folder):
    catalog_path = folder / 'catalog.json'
    catalog = json.loads(catalog_path.read_text(encoding='utf-8-sig'))
    (folder/'svg').mkdir(exist_ok=True)
    for entry in catalog['entries']:
        image, strokes = render(entry['text'], entry['style_id'])
        path = folder / entry['image']['path']
        path.parent.mkdir(parents=True,exist_ok=True)
        image.save(path,format='WEBP',lossless=True,exact=True,method=6)
        raw = path.read_bytes()
        entry['image'].update(width=image.width,height=image.height,bytes=len(raw),
                              sha256=hashlib.sha256(raw).hexdigest(),format='webp',alpha=True,lossless_encoding=True)
        svg_path = f"svg/{entry['id']}.svg"
        entry['source_svg'] = svg_path
        parts=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {image.width} {image.height}" role="img" aria-label="{html.escape(entry["text"])}"><title>{html.escape(entry["text"])}</title>']
        for color, weight in [('white',27),('black',18 if entry['style_id']=='block' else 16)]:
            for stroke in strokes:
                points=' '.join(f'{x},{y}' for x,y in stroke)
                parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="{weight}" stroke-linejoin="round"/>')
        if entry['style_id']=='drybrush':
            for i,stroke in enumerate(strokes):
                if len(stroke)>1 and i%3==0:
                    x,y=stroke[0]
                    parts.append(f'<path d="M{x},{y} l6,14" stroke="white" stroke-width="2"/>')
        parts.append('</svg>')
        (folder/svg_path).write_text(''.join(parts)+'\n',encoding='utf-8',newline='\n')
    catalog_path.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'englishSoundEffects':len(catalog['entries'])}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory',type=Path,default=DEFAULT)
    build(parser.parse_args().directory)
