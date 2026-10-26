"""Refresh offline gallery data from the English catalogs without browser access."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def refresh(path, entries):
    content = path.read_text(encoding='utf-8-sig')
    pattern = r'(<script id="catalog-data" type="application/json">).*?(</script>)'
    encoded = json.dumps(entries, ensure_ascii=False).replace('</', '<\\/')
    updated, count = re.subn(pattern, lambda match: match[1]+encoded+match[2], content, flags=re.S)
    if count != 1:
        raise ValueError(f'Expected one embedded catalog in {path.name}.')
    path.write_text(updated, encoding='utf-8', newline='\n')


def main():
    sfx = ROOT/'templates/manga-project/templates/onomatopoeia'
    catalog = json.loads((sfx/'catalog.json').read_text(encoding='utf-8-sig'))
    refresh(sfx/'index.html', [
        {'id': e['id'], 'title': e['text'], 'style': e['style_id'], 'image': e['image']['path'],
         'description': e['meaning_en']+' / '+', '.join(e['tags'])+' / Intensity '+str(e['intensity']),
         'reading': e['reading'], 'repeat': e['repeat']['count'] if e['repeat'] else None}
        for e in catalog['entries']])
    styles = ROOT/'resources/novelai-style-samples'
    refresh(styles/'index.html', json.loads((styles/'catalog.json').read_text(encoding='utf-8-sig'))['samples'])
    pixai = ROOT/'resources/pixai-model-samples'
    if (pixai/'catalog.json').is_file() and (pixai/'index.html').is_file():
        refresh(pixai/'index.html', json.loads((pixai/'catalog.json').read_text(encoding='utf-8-sig'))['samples'])
    print('Refreshed offline asset galleries.')


if __name__ == '__main__':
    main()
