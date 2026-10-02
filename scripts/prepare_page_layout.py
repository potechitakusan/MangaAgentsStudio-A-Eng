"""Place panel coordinates within the project frame without transforming art or lettering; export guides separately."""
from __future__ import annotations

import argparse
import copy
import html
import json
import math
from pathlib import Path
import struct


def number(value, name, *, positive=False):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError(f'{name} must be a finite number.')
    if value < 0 or (positive and value == 0):
        raise ValueError(f'Invalid range for {name}.')
    return value


def canvas_size(value, name):
    if not isinstance(value, dict) or any(type(value.get(key)) is not int or value[key] <= 0
                                          for key in ('width', 'height')):
        raise ValueError(f'{name} width and height must be positive integer pixels.')
    return {key: value[key] for key in ('width', 'height')}


def png_size(path):
    """Read actual dimensions from PNG IHDR without converting or resaving the image."""
    with Path(path).open('rb') as stream:
        header = stream.read(24)
    if len(header) != 24 or header[:16] != b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR':
        raise ValueError('The page image must be a PNG.')
    width, height = struct.unpack('>II', header[16:24])
    return canvas_size({'width': width, 'height': height}, 'Actual generated dimensions')


def uniform_scale(source, target, name):
    if source['width'] * target['height'] != source['height'] * target['width']:
        raise ValueError(f'{name} aspect ratios differ. Decide placement, margins, and cropping, then adjust in a separate step.')
    return target['width'] / source['width']


def resolve_config(config, canvas=None, generated_canvas=None):
    """Scale from reference dimensions each time without modifying the source. Version 1 retains legacy pixel settings."""
    if not isinstance(config, dict) or type(config.get('schemaVersion')) is not int or config['schemaVersion'] not in (1, 2):
        raise ValueError('Page settings schemaVersion must be 1 or 2.')
    version = config['schemaVersion']
    reference = canvas_size(config['referenceCanvas'] if version == 2 else config['canvas'], 'Reference dimensions')
    requested = config.get('generationCanvas')
    if requested is not None:
        requested = canvas_size(requested, 'Requested generation dimensions')
    if generated_canvas is not None:
        generated_canvas = canvas_size(generated_canvas, 'Actual generated dimensions')
    configured = config.get('canvas')
    if configured is not None:
        configured = canvas_size(configured, 'Frame placement dimensions')
    working = canvas if canvas is not None else configured
    if working is None:
        working = generated_canvas if generated_canvas is not None else requested
    if working is None:
        raise ValueError('Frame dimensions are not determined. After generation use --page-image; before generation or for per-panel production use --canvas WIDTH HEIGHT.')
    working = canvas_size(working, 'Frame placement dimensions')
    export = config.get('exportCanvas')
    export = canvas_size(export, 'Final PNG dimensions') if export is not None else copy.deepcopy(working)
    export_scale = uniform_scale(working, export, 'Frame placement and final PNG')
    image_scale = uniform_scale(generated_canvas, working, 'Generated image and frame placement') if generated_canvas is not None else None

    # Validate reference values too; overrides must not hide invalid values.
    base = {key: copy.deepcopy(config[key]) for key in ('basicFrame', 'textSafeArea', 'frameStroke', 'showGuide')}
    validate_config({'schemaVersion': 1, 'canvas': reference, **base})
    sx, sy = (working[key] / reference[key] for key in ('width', 'height'))
    stroke_scale = min(sx, sy)
    effective = {'schemaVersion': 1, 'canvas': working, **base}
    for name in ('basicFrame', 'textSafeArea'):
        effective[name] = {side: value * (sx if side in ('left', 'right') else sy)
                           for side, value in base[name].items()}
    effective['frameStroke'] *= stroke_scale
    fixed = config.get('fixedPixels', {})
    if not isinstance(fixed, dict) or set(fixed) - {'basicFrame', 'textSafeArea', 'frameStroke'}:
        raise ValueError('fixedPixels may specify only frame/text-safe margins or stroke widths.')
    for name in ('basicFrame', 'textSafeArea'):
        if name in fixed:
            if not isinstance(fixed[name], dict) or set(fixed[name]) - {'left', 'top', 'right', 'bottom'}:
                raise ValueError(f'fixedPixels.{name} must use left, top, right, or bottom.')
            effective[name].update(fixed[name])
    if 'frameStroke' in fixed:
        effective['frameStroke'] = fixed['frameStroke']
    effective['guideStroke'] = 3 * stroke_scale
    effective['guideDash'] = [16 * stroke_scale, 10 * stroke_scale]
    validate_config(effective)
    dimensions = {'generationRequested': requested, 'generationActual': generated_canvas,
                  'working': copy.deepcopy(working), 'export': export, 'reference': reference,
                  'generationToWorkingScale': image_scale, 'workingToExportScale': export_scale}
    return effective, dimensions


def validate_config(config):
    if not isinstance(config, dict) or type(config.get('schemaVersion')) is not int or config['schemaVersion'] != 1:
        raise ValueError('Resolved page settings schemaVersion must be 1.')
    width, height = (config['canvas'][key] for key in ('width', 'height'))
    for value in (width, height):
        if type(value) is not int or value <= 0:
            raise ValueError('Page width and height must be positive integer pixels.')
    for name in ('basicFrame', 'textSafeArea'):
        margins = config[name]
        for side in ('left', 'top', 'right', 'bottom'):
            number(margins[side], f'{name}.{side}')
        if margins['left'] + margins['right'] >= width or margins['top'] + margins['bottom'] >= height:
            raise ValueError(f'{name} must enclose a positive area.')
    number(config['frameStroke'], 'frameStroke', positive=True)
    if type(config['showGuide']) is not bool:
        raise ValueError('showGuide must be true or false.')


def place_template(item, source_canvas, config):
    """Transform only frame coordinates proportionally within the base frame; apply the same transform to effect regions."""
    validate_config(config)
    inset = number(source_canvas['frameInset'], 'frameInset')
    source_width = number(source_canvas['width'], 'width', positive=True) - 2 * inset
    source_height = number(source_canvas['height'], 'height', positive=True) - 2 * inset
    if source_width <= 0 or source_height <= 0:
        raise ValueError('Invalid source frame area.')
    frame = config['basicFrame']
    width = config['canvas']['width'] - frame['left'] - frame['right']
    height = config['canvas']['height'] - frame['top'] - frame['bottom']

    def transform(polygon):
        return [[round(frame['left'] + (x - inset) * width / source_width, 6),
                 round(frame['top'] + (y - inset) * height / source_height, 6)] for x, y in polygon]

    placed = copy.deepcopy(item)
    # Do not retain source asset links or source coordinates in transformed data.
    placed.pop('assets', None)
    placed['coordinateSystem'] = {**config['canvas'], 'origin': 'Top left', 'unit': 'px'}
    for panel in placed['panels']:
        panel['polygon'] = transform(panel['polygon'])
    for modifier in placed.get('modifiers', []):
        if 'region' in modifier:
            modifier['region'] = transform(modifier['region'])
    return placed


def svg_start(config, title):
    width, height = (config['canvas'][key] for key in ('width', 'height'))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}"><title>{html.escape(title)}</title>')


def polygon_svg(polygon, **attributes):
    points = ' '.join(f'{x:g},{y:g}' for x, y in polygon)
    attrs = ' '.join(f'{key.replace("_", "-")}="{html.escape(str(value), quote=True)}"' for key, value in attributes.items())
    return f'<polygon points="{points}" {attrs}/>'


def frames_svg(placed, config):
    parts = [svg_start(config, 'Panel frames'), '<g id="panels">']
    for panel in placed['panels']:
        parts.append(polygon_svg(panel['polygon'], id=panel['id'], fill='none', stroke='#000',
                                 stroke_width=config['frameStroke'], stroke_linejoin='miter'))
    return ''.join(parts) + '</g></svg>'


def guide_svg(placed, config):
    stroke = config.get('guideStroke', 3)
    dash = ' '.join(f'{value:g}' for value in config.get('guideDash', [16, 10]))
    parts = [svg_start(config, 'Review-only base frame and text-safe area'),
             f'<g id="guides" fill="none" stroke-width="{stroke:g}" stroke-dasharray="{dash}">']
    for name, color in (('basicFrame', '#087ac1'), ('textSafeArea', '#b04490')):
        margin = config[name]
        width = config['canvas']['width'] - margin['left'] - margin['right']
        height = config['canvas']['height'] - margin['top'] - margin['bottom']
        parts.append(f'<rect id="{name}" x="{margin["left"]}" y="{margin["top"]}" width="{width}" height="{height}" stroke="{color}"/>')
    for modifier in placed.get('modifiers', []):
        if 'region' in modifier:
            parts.append(polygon_svg(modifier['region'], stroke='#a85e27'))
    return ''.join(parts) + '</g></svg>'


def prepare(catalog, template_id, config, output, show_guide=None, *, canvas=None, page_image=None):
    config, dimensions = resolve_config(config, canvas, png_size(page_image) if page_image is not None else None)
    candidates = [item for item in catalog['templates'] if item['id'] == template_id]
    if len(candidates) != 1:
        raise ValueError('Template ID is missing or duplicated.')
    placed = place_template(candidates[0], catalog['canvas'], config)
    enabled = config['showGuide'] if show_guide is None else show_guide
    # Use a new output folder to avoid mixing existing guides and working assets.
    output = Path(output)
    if output.exists():
        raise ValueError('Output already exists. Specify a new folder.')
    record = {'schemaVersion': 2, 'page': copy.deepcopy(config), 'dimensions': dimensions, 'template': placed,
              'files': {'frames': 'frames.svg', 'guide': 'guide.svg' if enabled else None}}
    record['page']['showGuide'] = enabled
    output.mkdir(parents=True)
    (output / 'frames.svg').write_text(frames_svg(placed, config), encoding='utf-8')
    if enabled:
        (output / 'guide.svg').write_text(guide_svg(placed, config), encoding='utf-8')
    (output / 'layout.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', default='config/page-layout.json', help='Project page settings')
    parser.add_argument('--catalog', default='templates/panel-templates/catalog.json', help='Bundled catalog')
    parser.add_argument('--template', required=True, help='Selected panel-frame ID')
    parser.add_argument('--output', required=True, help='New output folder')
    parser.add_argument('--page-image', help='Generated full-page PNG; use header dimensions to size frame placement')
    parser.add_argument('--canvas', nargs=2, type=int, metavar=('WIDTH', 'HEIGHT'),
                        help='Frame width and height for preliminary layouts, per-panel production, or explicit resizing')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--guide', action='store_true', dest='guide', help='Export review guides as separate files')
    group.add_argument('--no-guide', action='store_false', dest='guide', help='Do not export guides')
    parser.set_defaults(guide=None)
    args = parser.parse_args()
    try:
        config = json.loads(Path(args.config).read_text(encoding='utf-8-sig'))
        catalog = json.loads(Path(args.catalog).read_text(encoding='utf-8-sig'))
        canvas = dict(zip(('width', 'height'), args.canvas)) if args.canvas is not None else None
        record = prepare(catalog, args.template, config, args.output, args.guide, canvas=canvas, page_image=args.page_image)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f'Cannot create page layout: {error}\n')
    print(json.dumps({'template': args.template, 'dimensions': record['dimensions'], 'files': record['files']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
