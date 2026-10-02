"""Typeset balloons, dialogue, in-world text, and frames on transparent layers and check readability.

Artwork (generated images/assets) remains unchanged. Write transparent PNGs, review PNGs, and check JSON to a separate folder.
Checks identify possible corrections; numerical results alone do not establish readability.
Requires Python 3.10+ and Pillow. Fonts are not bundled; use an explicit font or an installed font.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import textwrap
import unicodedata
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

SCHEMA_VERSION = 1
MAX_PIXELS = 64_000_000
INK = '#1f1a1c'

# Characters rotated 90 degrees only in explicit legacy Japanese vertical mode.
ROTATE = set('ー－―‐—–〜～…‥（）()「」『』【】〔〕［］[]｛｝{}〈〉《》＜＞<>＝=→←')
# Punctuation shifted upper-right only in vertical mode.
PUNCT_SHIFT = set('、。，．,.')
SMALL_KANA = set('ぁぃぅぇぉっゃゅょゎゕゖァィゥェォッャュョヮヵヶㇰㇱㇲㇳㇴㇵㇶㇷㇸㇹㇺㇻㇼㇽㇾㇿ')
# Characters disallowed at the start of legacy Japanese vertical columns.
NO_LINE_START = set('、。，．,.」』）)】〕］}〉》ーぁぃぅぇぉっゃゅょゎァィゥェォッャュョヮヵヶ！？!?…‥')
# Tate-chu-yoko: up to two ASCII digits, or two question/exclamation marks.
TCY = re.compile(r'[0-9]{1,2}|[!?！？]{2}')
KIND_WITH_TAIL = {'speech', 'whisper', 'shout'}
KINDS = KIND_WITH_TAIL | {'flash', 'narration', 'monologue'}
LEVELS = ('error', 'warning', 'info')


# ---------------------------------------------------------------- Input/output

def bounded_path(root: Path, value: str) -> Path:
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Path is outside the specified root: ' + value)
    return path


def font_candidates(root: Path) -> list[Path]:
    """Search project assets/fonts, then installed fonts. Do not persist absolute paths."""
    found = sorted((root / 'assets' / 'fonts').glob('*.[ot]t[fc]')) if (root / 'assets' / 'fonts').is_dir() else []
    windir = os.environ.get('WINDIR') or os.environ.get('SystemRoot')
    names = []
    if windir:
        fonts = Path(windir) / 'Fonts'
        names += [fonts / n for n in ('arial.ttf', 'calibri.ttf', 'segoeui.ttf', 'BIZ-UDGothicR.ttc', 'YuGothM.ttc', 'meiryo.ttc', 'NotoSansJP-VF.ttf', 'msgothic.ttc')]
    names += [Path('/System/Library/Fonts') / n for n in ('ヒラギノ角ゴシック W5.ttc', 'ヒラギノ角ゴシック W4.ttc', 'Hiragino Sans GB.ttc')]
    names += [Path('/usr/share/fonts') / n for n in ('opentype/noto/NotoSansCJK-Regular.ttc', 'noto-cjk/NotoSansCJK-Regular.ttc',
                                                    'google-noto-cjk/NotoSansCJK-Regular.ttc', 'truetype/fonts-japanese-gothic.ttf')]
    latin = [Path('/System/Library/Fonts/Supplemental/Arial.ttf'),
             Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
             Path('/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf')]
    return found + [p for p in latin + names if p.is_file()]


class Fonts:
    def __init__(self, root: Path, spec_font: str | None):
        if spec_font:
            path = Path(spec_font)
            path = path if path.is_absolute() else bounded_path(root, spec_font)
            if not path.is_file():
                raise FileNotFoundError('Specified font does not exist: ' + spec_font)
            self.path = path
        else:
            candidates = font_candidates(root)
            if not candidates:
                raise FileNotFoundError('No font found. Specify a project font with text.font.')
            self.path = candidates[0]
        self.cache: dict[tuple[int, bool], ImageFont.FreeTypeFont] = {}

    def get(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        key = (max(4, int(round(size))), bold)
        if key not in self.cache:
            font = ImageFont.truetype(str(self.path), key[0])
            try:  # Use readable variable-font weight; retain defaults if unsupported.
                axes = font.get_variation_axes()
                if axes:
                    weight = 700 if bold else 500
                    font.set_variation_by_axes([weight if a.get('name') in (b'Weight', 'Weight') else a['default'] for a in axes])
            except Exception:
                pass
            self.cache[key] = font
        return self.cache[key]

    def missing(self, ch: str, size: int = 32) -> bool:
        """Detect missing glyphs by comparison with the replacement glyph."""
        font = self.get(size)
        try:
            probe = bytes(font.getmask(ch))
            notdef = bytes(font.getmask('\U0010FFFD'))
        except Exception:
            return False
        return bool(probe) and probe == notdef and ch not in ' 　'


# ---------------------------------------------------------------- Text layout

def to_cells(line: str) -> list[str]:
    """Legacy vertical cells combine tate-chu-yoko and widen single punctuation marks."""
    cells, i = [], 0
    while i < len(line):
        m = TCY.match(line, i)
        if m and (len(m.group()) == 2 or m.group().isdigit()):
            cells.append(m.group()); i = m.end(); continue
        ch = line[i]
        cells.append({'!': '！', '?': '？'}.get(ch, ch)); i += 1
    return cells


def wrap(text: str, max_cells: int | None, direction: str = 'horizontal') -> tuple[list[list[str]], bool]:
    """Wrap English at word boundaries; preserve punctuation and explicit newlines.

    Long words remain intact and are reported by the line-length check. Explicit
    vertical mode retains the legacy Japanese cell/kinsoku behavior.
    """
    if max_cells is not None and (not isinstance(max_cells, int) or max_cells < 1):
        raise ValueError('max_chars must be a positive integer or null.')
    if direction == 'horizontal':
        lines, wrapped = [], False
        for raw in text.split('\n'):
            pieces = textwrap.wrap(raw, width=max_cells, break_long_words=False,
                                   break_on_hyphens=False, replace_whitespace=False) if max_cells else [raw]
            pieces = pieces or ['']
            wrapped = wrapped or len(pieces) > 1
            lines.extend(list(part) for part in pieces)
        return lines, wrapped
    columns, wrapped = [], False
    for raw in text.split('\n'):
        cells = to_cells(raw)
        if not max_cells or len(cells) <= max_cells:
            columns.append(cells); continue
        wrapped = True
        while len(cells) > max_cells:
            cut = max_cells
            while cut < len(cells) and cells[cut] in NO_LINE_START:  # Hanging punctuation
                cut += 1
            columns.append(cells[:cut]); cells = cells[cut:]
        if cells:
            columns.append(cells)
    return columns, wrapped


def text_metrics(columns: list[list[str]], size: float, direction: str, font=None) -> dict:
    char_pitch, col_pitch = size * 1.08, size * 1.55
    n = max(1, len(columns)); longest = max([len(c) for c in columns] or [1])
    if direction == 'horizontal':
        width = max((font.getlength(''.join(c)) for c in columns), default=0) if font else longest * size * 0.65
        height = max((font.getbbox(''.join(c) or 'Ag')[3] - font.getbbox(''.join(c) or 'Ag')[1] for c in columns), default=size) if font else size
        return dict(width=max(1.0, width), height=(n - 1) * size * 1.5 + height, char_pitch=size * 0.65, col_pitch=size * 1.5, line_height=height)
    return dict(width=(n - 1) * col_pitch + size, height=(longest - 1) * char_pitch + size, char_pitch=char_pitch, col_pitch=col_pitch)


def count_chars(text: str) -> int:
    return sum(1 for ch in text if ch not in '\n\r \t　')


# ---------------------------------------------------------------- Shapes

def ellipse_points(cx, cy, rx, ry, n=72):
    return [(cx + rx * math.cos(2 * math.pi * k / n), cy + ry * math.sin(2 * math.pi * k / n)) for k in range(n)]


def point_in_polygon(x, y, poly) -> bool:
    inside, j = False, len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]; xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-9) + xi:
            inside = not inside
        j = i
    return inside


def segments_cross(a, b, c, d) -> bool:
    def orient(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    o1, o2, o3, o4 = orient(a, b, c), orient(a, b, d), orient(c, d, a), orient(c, d, b)
    return o1 * o2 < 0 and o3 * o4 < 0


def shape_overlaps_rect(shape, rect) -> bool:
    """Approximate balloon-outline/rectangle overlap using sampled points."""
    x0, y0, x1, y1 = rect
    if any(x0 <= x <= x1 and y0 <= y <= y1 for x, y in shape):
        return True
    for i in range(9):
        for j in range(9):
            if point_in_polygon(x0 + (x1 - x0) * i / 8, y0 + (y1 - y0) * j / 8, shape):
                return True
    return False


def shapes_overlap(a, b) -> bool:
    return any(point_in_polygon(x, y, b) for x, y in a) or any(point_in_polygon(x, y, a) for x, y in b)


class Balloon:
    """Calculate balloon dimensions, outline, and tail once for both rendering and checks."""

    def __init__(self, entry: dict, defaults: dict, keep_out: list | None = None):
        self.entry = entry
        self.keep_out = [tuple(map(float, k['box'])) for k in (keep_out or [])
                         if k.get('panel') is None or str(k.get('panel')) == str(entry.get('panel'))]
        self.id = str(entry.get('id') or '')
        self.kind = entry.get('kind', 'speech')
        self.text = entry.get('text', '')
        self.size = float(entry.get('size') or defaults['size'])
        self.direction = entry.get('direction', defaults.get('direction', 'horizontal'))
        if self.direction not in ('horizontal', 'vertical'):
            raise ValueError('direction must be horizontal or vertical.')
        limit = entry.get('max_chars', defaults.get('max_chars', 10 if self.direction == 'vertical' else 26))
        self.columns, self.auto_wrapped = wrap(self.text, limit, self.direction)
        fonts = defaults.get('fonts')
        font = fonts.get(self.size, self.kind in ('shout', 'flash')) if fonts else None
        m = text_metrics(self.columns, self.size, self.direction, font)
        self.metrics = m
        cx, cy = map(float, entry['center'])
        self.cx, self.cy = cx, cy
        pad = self.size * float(entry.get('padding', 0.7))
        if self.kind in ('narration',):
            self.rx, self.ry = m['width'] / 2 + pad, m['height'] / 2 + pad
            self.outline = [(cx - self.rx, cy - self.ry), (cx + self.rx, cy - self.ry), (cx + self.rx, cy + self.ry), (cx - self.rx, cy + self.ry)]
        elif self.kind == 'monologue':
            self.rx, self.ry = m['width'] / 2 + self.size * 0.3, m['height'] / 2 + self.size * 0.3
            self.outline = [(cx - self.rx, cy - self.ry), (cx + self.rx, cy - self.ry), (cx + self.rx, cy + self.ry), (cx - self.rx, cy + self.ry)]
        else:
            # Radii keep text corners inside the ellipse (1/a²+1/b² approximately 1), avoiding overly narrow balloons.
            a, b = 1.55, 1.3
            self.rx, self.ry = (m['width'] / 2 + pad * 0.6) * a, (m['height'] / 2 + pad * 0.6) * b
            spike = 1.2 if self.kind in ('shout', 'flash') else 1.0
            self.outline = ellipse_points(cx, cy, self.rx * spike, self.ry * spike)
        self.text_box = (cx - m['width'] / 2, cy - m['height'] / 2, cx + m['width'] / 2, cy + m['height'] / 2)
        self.tail = self._tail(entry)

    def _tail(self, entry):
        target = entry.get('tail')
        if self.kind not in KIND_WITH_TAIL or not isinstance(target, (list, tuple)):
            return None
        tx, ty = map(float, target)
        dx, dy = tx - self.cx, ty - self.cy
        dist = math.hypot(dx, dy)
        if dist < 1:
            return None
        ang = math.atan2(dy / self.ry, dx / self.rx)  # Ellipse parameter angle
        edge = (self.cx + self.rx * math.cos(ang), self.cy + self.ry * math.sin(ang))
        edge_dist = math.hypot(edge[0] - self.cx, edge[1] - self.cy)
        remain = max(0.0, dist - edge_dist)
        if entry.get('tail_exact'):
            length = remain
        else:  # Stop short of the speaker's mouth.
            length = min(max(remain - self.size * 0.6, self.size * 0.8), self.size * 2.4)
        ux, uy = dx / dist, dy / dist
        if not entry.get('tail_exact'):
            # If the target lies in a protected face/object region, stop before its edge.
            for x0, y0, x1, y1 in self.keep_out:
                if x0 <= tx <= x1 and y0 <= ty <= y1:
                    enter = 0.0
                    for o, u, lo, hi in ((edge[0], ux, x0, x1), (edge[1], uy, y0, y1)):
                        if abs(u) > 1e-9:
                            enter = max(enter, min((lo - o) / u, (hi - o) / u))
                    length = min(length, max(self.size * 0.5, enter - self.size * 0.3))
        tip = (edge[0] + ux * length, edge[1] + uy * length)
        spread = min(0.32, (self.size * 0.55) / max(1.0, min(self.rx, self.ry)))
        base = [(self.cx + self.rx * 0.8 * math.cos(ang + s), self.cy + self.ry * 0.8 * math.sin(ang + s)) for s in (-spread, spread)]
        return dict(tip=tip, base=base, target=(tx, ty), edge=edge)

    def shape_points(self):
        pts = list(self.outline)
        if self.tail:
            pts += [self.tail['tip']]
        return pts

    def bbox(self):
        xs = [p[0] for p in self.shape_points()]; ys = [p[1] for p in self.shape_points()]
        return (min(xs), min(ys), max(xs), max(ys))


# ---------------------------------------------------------------- Rendering

def draw_glyph(layer: Image.Image, fonts: Fonts, cell: str, cx: float, cy: float, size: float, fill, bold=False, halo=0):
    """Draw one legacy vertical cell at (cx, cy), with vertical rotation and positioning."""
    font = fonts.get(size, bold)
    box = int(size * 2.2)
    tile = Image.new('RGBA', (box, box), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile)
    if len(cell) >= 2:  # Tate-chu-yoko
        f = fonts.get(size * min(1.0, 1.0 / (0.62 * len(cell))), bold)
        d.text((box / 2, box / 2), cell, font=f, fill=fill, anchor='mm', stroke_width=halo, stroke_fill='white')
    else:
        d.text((box / 2, box / 2), cell, font=font, fill=fill, anchor='mm', stroke_width=halo, stroke_fill='white')
    if len(cell) == 1 and cell in ROTATE:
        tile = tile.rotate(-90, resample=Image.Resampling.BICUBIC)
    ox, oy = 0.0, 0.0
    if cell in PUNCT_SHIFT:
        ox, oy = size * 0.55, -size * 0.55
    elif cell in SMALL_KANA:
        ox, oy = size * 0.1, -size * 0.1
    layer.alpha_composite(tile, (int(round(cx - box / 2 + ox)), int(round(cy - box / 2 + oy))))


def draw_text_block(layer, fonts, columns, box, size, metrics, direction='horizontal', fill=INK, bold=False, halo=0):
    x0, y0, x1, y1 = box
    if direction == 'horizontal':
        draw = ImageDraw.Draw(layer)
        font = fonts.get(size, bold)
        for r, cells in enumerate(columns):
            line = ''.join(cells)
            if line:
                bounds = font.getbbox(line)
                draw.text(((x0 + x1) / 2, y0 + r * metrics['col_pitch'] - bounds[1]),
                          line, font=font, fill=fill, anchor='ma', stroke_width=halo, stroke_fill='white')
        return
    # Legacy vertical mode: first column at right, all columns top-aligned.
    for c, cells in enumerate(columns):
        x = x1 - size / 2 - c * metrics['col_pitch']
        for r, cell in enumerate(cells):
            draw_glyph(layer, fonts, cell, x, y0 + size / 2 + r * metrics['char_pitch'], size, fill, bold, halo)


def outline_mask(mask: Image.Image, width: int) -> Image.Image:
    grown = mask.filter(ImageFilter.MaxFilter(width * 2 + 1))
    return ImageChops.subtract(grown, mask)


def draw_balloon(shapes: Image.Image, b: Balloon, stroke: int):
    kind = b.kind
    if kind == 'monologue':
        return
    margin = int(stroke * 4 + b.size * 2)
    x0, y0, x1, y1 = [int(v) for v in b.bbox()]
    ox, oy = x0 - margin, y0 - margin
    w, h = x1 - x0 + margin * 2, y1 - y0 + margin * 2
    mask = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(mask)
    local = lambda pts: [(x - ox, y - oy) for x, y in pts]
    if kind == 'narration':
        d.rectangle((b.cx - b.rx - ox, b.cy - b.ry - oy, b.cx + b.rx - ox, b.cy + b.ry - oy), fill=255)
    elif kind == 'shout':
        n = max(14, int((b.rx + b.ry) / (b.size * 0.9)))
        pts = []
        for k in range(n * 2):
            t = math.pi * k / n
            r = 1.2 if k % 2 == 0 else 0.98
            pts.append((b.cx + b.rx * r * math.cos(t), b.cy + b.ry * r * math.sin(t)))
        d.polygon(local(pts), fill=255)
    else:
        d.ellipse((b.cx - b.rx - ox, b.cy - b.ry - oy, b.cx + b.rx - ox, b.cy + b.ry - oy), fill=255)
    if b.tail:
        d.polygon(local([b.tail['base'][0], b.tail['tip'], b.tail['base'][1]]), fill=255)
    layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    white = Image.new('RGBA', (w, h), (255, 255, 255, 255))
    layer.paste(white, (0, 0), mask)
    if kind == 'flash':
        # Flash balloon: radial lines outside the white body.
        ld = ImageDraw.Draw(layer)
        n = max(40, int((b.rx + b.ry) / 3))
        for k in range(n):
            t = 2 * math.pi * k / n
            jitter = 0.08 * math.sin(k * 7.3) + 0.06 * math.cos(k * 3.1)
            r0, r1 = 1.02, 1.28 + jitter
            p0 = (b.cx + b.rx * r0 * math.cos(t) - ox, b.cy + b.ry * r0 * math.sin(t) - oy)
            p1 = (b.cx + b.rx * r1 * math.cos(t) - ox, b.cy + b.ry * r1 * math.sin(t) - oy)
            ld.line([p0, p1], fill=INK, width=max(1, stroke // 2))
    else:
        ring = outline_mask(mask, stroke)
        if kind == 'whisper':  # Dashed outline
            dash = Image.new('L', (w, h), 0)
            dd = ImageDraw.Draw(dash)
            step = max(6, int(b.size * 0.5))
            for k in range(0, w + h, step * 2):
                dd.line([(k, 0), (k - h, h)], fill=255, width=step)
            ring = ImageChops.multiply(ring, dash)
        layer.paste(Image.new('RGBA', (w, h), INK), (0, 0), ring)
    shapes.alpha_composite(layer, (ox, oy))


def draw_insert(layer, fonts, ins: dict, default_size: float, problems: list):
    """Draw an in-world paper, screen, or sign insert with horizontal text."""
    x0, y0, x1, y1 = map(float, ins['box'])
    w, h = int(x1 - x0), int(y1 - y0)
    style = ins.get('style', 'paper')
    colors = {'paper': ('#fbf8f0', '#8a8378', INK), 'screen': ('#1d2733', '#0b1017', '#e9f1f7'), 'sign': ('#ffffff', INK, INK)}
    bg, line, ink = colors.get(style, colors['paper'])
    card = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    radius = int(min(w, h) * (0.06 if style == 'screen' else 0.015))
    d.rounded_rectangle((1, 1, w - 2, h - 2), radius=radius, fill=bg, outline=line, width=max(2, int(min(w, h) * 0.008)))
    title, lines = ins.get('title', ''), list(ins.get('lines', []))
    size = float(ins.get('size') or default_size * 0.8)
    rows = ([title] if title else []) + lines
    longest = max([len(r) for r in rows] or [1])
    fit = min(size, (w * 0.86) / max(1, longest), (h * 0.86) / max(1, len(rows) * 1.6))
    if fit < size * 0.6:
        problems.append(issue('warning', 'INSERT_TEXT_SMALL', ins.get('id'), f'In-world text reduced to {fit:.0f}px to fit. Review wording, line count, or box size.'))
    y = h * 0.07 + fit * 0.6
    if title:
        d.text((w / 2, y), title, font=fonts.get(fit * 1.05, True), fill=ink, anchor='mm')
        y += fit * 1.7
        if style == 'paper':
            d.line((w * 0.06, y - fit * 0.7, w * 0.94, y - fit * 0.7), fill=line, width=1)
    for text in lines:
        d.text((w * 0.08, y), text, font=fonts.get(fit), fill=ink, anchor='lm')
        if style == 'paper':
            d.line((w * 0.06, y + fit * 0.75, w * 0.94, y + fit * 0.75), fill='#d9d2c6', width=1)
        y += fit * 1.6
    angle = float(ins.get('rotation', 0))
    if angle:
        card = card.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    layer.alpha_composite(card, (int(round((x0 + x1) / 2 - card.width / 2)), int(round((y0 + y1) / 2 - card.height / 2))))


# ---------------------------------------------------------------- Load settings and check

def issue(level, code, target, message):
    return dict(level=level, code=code, target=target, message_ja=message)


def load_page(spec: dict, root: Path) -> dict:
    """Read page dimensions, panels, text-safe area, and strokes from the spec or layout.json."""
    page = dict(size=None, panels=[], safe=None, stroke=None)
    if spec.get('layout'):
        layout = json.loads(bounded_path(root, spec['layout']).read_text(encoding='utf-8-sig'))
        working = layout['dimensions']['working']
        page['size'] = (int(round(working['width'])), int(round(working['height'])))
        margins = layout['page'].get('textSafeArea')
        if margins:
            page['safe'] = (margins['left'], margins['top'], page['size'][0] - margins['right'], page['size'][1] - margins['bottom'])
        page['stroke'] = layout['page'].get('frameStroke')
        page['panels'] = [dict(id=p['id'], order=p['order'], polygon=[tuple(v) for v in p['polygon']]) for p in layout['template']['panels']]
    if spec.get('page', {}).get('size'):
        page['size'] = tuple(int(v) for v in spec['page']['size'])
    if spec.get('page', {}).get('text_safe_area'):
        page['safe'] = tuple(spec['page']['text_safe_area'])
    if spec.get('panels'):
        page['panels'] = [dict(id=str(p.get('id', i)), order=int(p.get('order', i)), polygon=[tuple(v) for v in p['polygon']])
                          for i, p in enumerate(spec['panels'], 1)]
    if not page['size'] or any(v <= 0 for v in page['size']) or page['size'][0] * page['size'][1] > MAX_PIXELS:
        raise ValueError('Missing or invalid page dimensions. Specify layout or page.size.')
    if page['stroke'] is None:
        page['stroke'] = spec.get('page', {}).get('frame_stroke') or max(2.0, min(page['size']) * 0.005)
    return page


def find_panel(page, ref):
    for p in page['panels']:
        if ref is not None and (ref == p['order'] or str(ref) == str(p['id'])):
            return p
    return None


def check(spec: dict, page: dict, balloons: list[Balloon], fonts: Fonts | None) -> list[dict]:
    out = []
    checks = spec.get('checks', {})
    display_width = float(checks.get('display_width', 720))
    min_px = float(checks.get('min_display_px', 11))
    max_column = int(checks.get('max_column_cells', 42))
    keep_out = spec.get('keep_out', [])
    no_keep_out = {str(k): v for k, v in spec.get('no_keep_out', {}).items()}
    groups: dict[str, list[Balloon]] = {}
    seen_ids = set()
    for b in balloons:
        if not b.id or b.id in seen_ids:
            out.append(issue('error', 'BALLOON_ID', b.id, 'Balloon id is empty or duplicated.'))
        seen_ids.add(b.id)
        groups.setdefault(str(b.entry.get('group') or b.id), []).append(b)
        panel = find_panel(page, b.entry.get('panel'))
        if b.kind not in KINDS:
            out.append(issue('error', 'KIND', b.id, f'Unsupported kind: {b.kind}'))
        if page['panels'] and panel is None:
            out.append(issue('error', 'PANEL', b.id, 'Panel does not exist. Specify its reading-order number or id.'))
        if checks.get('punctuation_mode') == 'ja-manga' and ('。' in b.text or '．' in b.text):
            out.append(issue('error', 'PUNCT_PERIOD', b.id, 'Legacy Japanese punctuation mode disallows Japanese full stops in dialogue/narration.'))
        if b.kind in KIND_WITH_TAIL and not b.tail:
            reason = b.entry.get('no_tail_reason')
            out.append(issue('info' if reason else 'warning', 'NO_TAIL', b.id,
                             f'No tail (reason: {reason})' if reason else 'No tail. Point tail toward the speaker, or give no_tail_reason for off-panel speech or another exception.'))
        if b.tail and panel and not point_in_polygon(*b.tail['tip'], panel['polygon']):
            out.append(issue('warning', 'TAIL_OUTSIDE', b.id, 'Tail tip is outside the panel.'))
        if b.auto_wrapped:
            out.append(issue('warning', 'AUTO_WRAP', b.id, 'Text wrapped automatically. Inspect phrasing; use \\n for deliberate line breaks.'))
        if any(len(c) > max_column for c in b.columns):
            out.append(issue('warning', 'LONG_COLUMN', b.id, f'A line exceeds {max_column} characters. Consider a break, split, or rewording.'))
        shown = b.size * display_width / page['size'][0]
        if shown < min_px:
            out.append(issue('warning', 'SMALL_TEXT', b.id, f'At display width {display_width:.0f}px, text is about {shown:.1f}px, below the {min_px:.0f}px guideline.'))
        if b.direction == 'vertical' and re.search(r'[A-Za-z]', b.text):
            out.append(issue('warning', 'LATIN_IN_VERTICAL', b.id, 'Latin letters in vertical text. Review wording or layout.'))
        if fonts:
            missing = sorted({ch for ch in b.text if ch not in '\n' and fonts.missing(ch)})
            if missing:
                out.append(issue('error', 'MISSING_GLYPH', b.id, 'Missing font glyphs: ' + ''.join(missing)))
        if panel and not b.entry.get('allow_overflow') and not all(point_in_polygon(x, y, panel['polygon']) for x, y in b.outline):
            out.append(issue('warning', 'OUT_OF_PANEL', b.id, 'Overflows the panel. For deliberate overflow set allow_overflow: true.'))
        if page['safe']:
            sx0, sy0, sx1, sy1 = page['safe']
            if any(not (sx0 <= x <= sx1 and sy0 <= y <= sy1) for x, y in b.outline):
                out.append(issue('warning', 'OUT_OF_SAFE_AREA', b.id, 'Outside the text-safe area.'))
        for k in keep_out:
            if str(k.get('panel')) == str(b.entry.get('panel')) or k.get('panel') is None:
                label = k.get('label', 'Protected artwork region')
                if shape_overlaps_rect(b.outline, k['box']):
                    out.append(issue('error', 'KEEP_OUT', b.id, f'Overlaps "{label}".'))
                elif b.tail and k['box'][0] <= b.tail['tip'][0] <= k['box'][2] and k['box'][1] <= b.tail['tip'][1] <= k['box'][3]:
                    out.append(issue('warning', 'TAIL_INTO_KEEP_OUT', b.id, f'Tail tip enters "{label}". Stop short of the mouth.'))
    # Legacy Japanese punctuation: linked balloons count as one.
    for key, members in (groups.items() if checks.get('punctuation_mode') == 'ja-manga' else []):
        total = sum(count_chars(m.text.replace('、', '').replace('，', '')) for m in members)
        if any('、' in m.text or '，' in m.text for m in members):
            if total < 20:
                out.append(issue('error', 'PUNCT_COMMA', key, f'Japanese comma in {total} characters excluding commas; legacy mode requires at least 20.'))
            else:
                out.append(issue('info', 'PUNCT_COMMA_CHECK', key, f'Japanese comma in {total} characters. In legacy mode, verify that the break is needed.'))
    # Reading order, overlap, and crossing tails within a panel.
    by_panel: dict[str, list[Balloon]] = {}
    for b in balloons:
        by_panel.setdefault(str(b.entry.get('panel')), []).append(b)
    for ref, members in by_panel.items():
        orders = [m.entry.get('order') for m in members]
        if len(set(orders)) != len(orders) or any(not isinstance(o, int) for o in orders):
            out.append(issue('error', 'ORDER', f'panel {ref}', 'Assign distinct integer order values to balloons in a panel.'))
            continue
        members = sorted(members, key=lambda m: m.entry['order'])
        for i, a in enumerate(members):
            for c in members[i + 1:]:
                ab, cb = a.bbox(), c.bbox()
                if c.cx < a.cx - (ab[2] - ab[0]) * 0.25 and cb[1] < ab[1] - a.size * 0.5:
                    out.append(issue('warning', 'READ_ORDER', c.id, f'Intended after {a.id}, but its upper-left position may attract the reader first.'))
                same_group = a.entry.get('group') and a.entry.get('group') == c.entry.get('group')
                if not same_group and shapes_overlap(a.outline, c.outline):
                    out.append(issue('warning', 'BALLOON_OVERLAP', c.id, f'Overlaps {a.id}. Use the same group for connected balloons.'))
                if a.tail and c.tail and segments_cross((a.cx, a.cy), a.tail['tip'], (c.cx, c.cy), c.tail['tip']):
                    out.append(issue('warning', 'TAIL_CROSS', c.id, f'Tail crosses {a.id}. Review character placement or speaking order.'))
        if ref not in no_keep_out and not any(str(k.get('panel')) == ref for k in keep_out) and ref != 'None':
            out.append(issue('warning', 'KEEP_OUT_MISSING', f'panel {ref}',
                             'Face, hand, and important-prop regions are unspecified. Inspect the image and set keep_out, or explain none in no_keep_out.'))
    return out


def mark_image(image: Image.Image, spec: dict, page: dict, balloons: list[Balloon], fonts: Fonts) -> Image.Image:
    """Review overlay of protected regions, panel numbers, and balloon order. Do not publish."""
    marked = image.convert('RGBA').copy()
    md = ImageDraw.Draw(marked)
    width = marked.size[0]
    label_font = fonts.get(max(14, width * 0.018), True)
    for k in spec.get('keep_out', []):
        md.rectangle(k['box'], outline='#e0245e', width=3)
        md.text((k['box'][0] + 4, k['box'][1] + 2), k.get('label', ''), font=fonts.get(max(12, width * 0.012)), fill='#e0245e')
    for p in page['panels']:
        xs = [v[0] for v in p['polygon']]; ys = [v[1] for v in p['polygon']]
        md.text((max(xs) - 8, min(ys) + 6), f'Panel {p["order"]}', font=label_font, fill='#1565c0', anchor='ra')
    for b in balloons:
        md.text((b.bbox()[2], b.bbox()[1]), str(b.entry.get('order', '?')), font=label_font, fill='#2e7d32', anchor='la')
        if b.tail:
            md.line([b.tail['tip'], b.tail['target']], fill='#2e7d32', width=2)
    return marked


def review_images(page_png: Path, spec: dict, root: Path, out_dir: Path, stem: str) -> dict[str, Path]:
    """Create display-width and annotated review images from the completed page including artwork."""
    page = load_page(spec, root)
    fonts = Fonts(root, spec.get('text', {}).get('font'))
    size = float(spec.get('text', {}).get('size') or round(page['size'][0] * 0.028))
    defaults = dict(size=size, max_chars=spec.get('text', {}).get('max_chars', 26),
                    direction=spec.get('text', {}).get('direction', 'horizontal'), fonts=fonts)
    balloons = [Balloon(e, defaults, spec.get('keep_out', [])) for e in spec.get('balloons', [])]
    with Image.open(page_png) as opened:
        final = opened.convert('RGBA')
    display_width = int(spec.get('checks', {}).get('display_width', 720))
    display = out_dir / f'{stem}-display.png'
    check = out_dir / f'{stem}-check-overlay.png'
    final.convert('RGB').resize((display_width, int(round(final.size[1] * display_width / final.size[0]))),
                                Image.Resampling.LANCZOS).save(display)
    mark_image(final, spec, page, balloons, fonts).convert('RGB').save(check)
    return {'display': display, 'check_overlay': check}


def render(spec: dict, root: Path, out_dir: Path, background: str | None, draw_frames: bool):
    page = load_page(spec, root)
    text_cfg = spec.get('text', {})
    fonts = Fonts(root, text_cfg.get('font'))
    size = page['size']
    defaults = dict(size=float(text_cfg.get('size') or round(size[0] * 0.028)), max_chars=text_cfg.get('max_chars', 26),
                    direction=text_cfg.get('direction', 'horizontal'), fonts=fonts)
    balloons = [Balloon(e, defaults, spec.get('keep_out', [])) for e in spec.get('balloons', [])]
    problems = check(spec, page, balloons, fonts)
    stroke = max(2, int(round(page['stroke'] * 0.4)))

    frames = Image.new('RGBA', size, (0, 0, 0, 0))
    if draw_frames and page['panels']:
        if spec.get('frame_gutter_white', True):
            # Cover page margins and gutters with white, hiding artwork extending outside panels.
            gutter = Image.new('L', size, 255)
            gd = ImageDraw.Draw(gutter)
            for p in page['panels']:
                gd.polygon(p['polygon'], fill=0)
            frames.paste(Image.new('RGBA', size, 'white'), (0, 0), gutter)
        fd = ImageDraw.Draw(frames)
        for p in page['panels']:
            fd.line(p['polygon'] + [p['polygon'][0]], fill=INK, width=max(1, int(round(page['stroke']))), joint='curve')
    inserts = Image.new('RGBA', size, (0, 0, 0, 0))
    for ins in spec.get('inserts', []):
        draw_insert(inserts, fonts, ins, defaults['size'], problems)
    shapes = Image.new('RGBA', size, (0, 0, 0, 0))
    text = Image.new('RGBA', size, (0, 0, 0, 0))
    for b in balloons:
        draw_balloon(shapes, b, stroke)
        bold = b.kind in ('shout', 'flash')
        halo = max(2, int(b.size * 0.12)) if b.kind == 'monologue' else 0
        draw_text_block(text, fonts, b.columns, b.text_box, b.size, b.metrics, b.direction,
                        b.entry.get('color', INK), bold, halo)

    if background:
        with Image.open(bounded_path(root, background)) as opened:
            base = opened.convert('RGBA')
        if base.size != size:
            raise ValueError(f'Background dimensions {base.size} do not match page dimensions {size}.')
    else:
        base = Image.new('RGBA', size, 'white')
    preview = base.copy()
    for layer in (inserts, frames, shapes, text):
        preview.alpha_composite(layer)

    marked = mark_image(preview, spec, page, balloons, fonts)

    out_dir.mkdir(parents=True, exist_ok=True)
    files = {'frames': 'frames.png', 'inserts': 'inserts.png', 'balloons': 'balloons.png', 'text': 'text.png',
             'preview': 'preview.png', 'display': 'preview-display.png', 'check_overlay': 'check-overlay.png'}
    if draw_frames and page['panels']:
        frames.save(out_dir / files['frames'])
    if spec.get('inserts'):
        inserts.save(out_dir / files['inserts'])
    shapes.save(out_dir / files['balloons'])
    text.save(out_dir / files['text'])
    preview.convert('RGB').save(out_dir / files['preview'])
    display_width = int(spec.get('checks', {}).get('display_width', 720))
    scale = display_width / size[0]
    preview.convert('RGB').resize((display_width, int(round(size[1] * scale))), Image.Resampling.LANCZOS).save(out_dir / files['display'])
    marked.convert('RGB').save(out_dir / files['check_overlay'])

    rel = lambda name: (out_dir / name).relative_to(root).as_posix()
    overlays = []
    for key, label in (('inserts', 'Inserts (in-world text)'), ('frames', 'Panel frames'), ('balloons', 'Balloons'), ('text', 'Text (raster)')):
        if (out_dir / files[key]).exists():
            overlays.append(dict(name=label, source=rel(files[key]), position=[0, 0]))
    summary = {lv: sum(1 for p in problems if p['level'] == lv) for lv in LEVELS}
    report = dict(
        schema_version=SCHEMA_VERSION,
        page_size=list(size),
        font_file=fonts.path.name,
        balloons=[dict(id=b.id, panel=b.entry.get('panel'), order=b.entry.get('order'), speaker=b.entry.get('speaker'),
                       kind=b.kind, text=b.text, chars=count_chars(b.text), columns=[''.join(c) for c in b.columns],
                       bbox=[round(v, 1) for v in b.bbox()], tail=bool(b.tail)) for b in balloons],
        summary=summary,
        issues=problems,
        outputs={k: rel(v) for k, v in files.items() if (out_dir / v).exists()},
        overlays_for_export_composed_psd=overlays,
        note_ja=('Checks identify possible corrections. Open preview-display.png and inspect order, speakers, and overlap with faces/hands. check-overlay.png is for review only, never publication.'
                 if background else
                 'Checks identify possible corrections. The preview, preview-display, and check-overlay in this folder contain only typesetting, without artwork. '
                 'Inspect face/hand overlap on the completed page with artwork (page-NN-display.png and page-NN-check-overlay.png in the version folder for novelai_batch.py build; '
                 'for standalone use, specify --background).'),
    )
    (out_dir / 'check.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--spec', required=True, help='Typesetting JSON relative to the project root')
    ap.add_argument('--output', required=True, help='Output folder; use a new folder each time')
    ap.add_argument('--background', help='Page image beneath the review overlay (same dimensions as the page)')
    ap.add_argument('--root', default='.')
    ap.add_argument('--no-frames', action='store_true', help='Do not draw frames when the artwork already includes them')
    ap.add_argument('--overwrite', action='store_true')
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    try:
        spec = json.loads(bounded_path(root, args.spec).read_text(encoding='utf-8-sig'))
        if spec.get('schema_version') != SCHEMA_VERSION:
            raise ValueError('schema_version must be 1.')
        out_dir = bounded_path(root, args.output)
        if out_dir.exists() and any(out_dir.iterdir()) and not args.overwrite:
            raise FileExistsError('Output folder is not empty. Use a new folder or --overwrite.')
        report = render(spec, root, out_dir, args.background, not args.no_frames)
    except (ValueError, KeyError, TypeError, FileNotFoundError, FileExistsError) as exc:
        print(json.dumps(dict(ok=False, error=f'{type(exc).__name__}: {exc}'), ensure_ascii=False))
        return 2
    print(json.dumps(dict(ok=report['summary']['error'] == 0, summary=report['summary'],
                          check=(Path(args.output) / 'check.json').as_posix()), ensure_ascii=False))
    for p in report['issues']:
        if p['level'] != 'info':
            print(f"[{p['level']}] {p['code']} {p['target']}: {p['message_ja']}")
    return 1 if report['summary']['error'] else 0


if __name__ == '__main__':
    sys.exit(main())
