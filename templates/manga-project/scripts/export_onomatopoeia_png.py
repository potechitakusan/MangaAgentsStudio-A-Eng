"""Export one lightweight template asset as a compatibility PNG inside the project."""
from pathlib import Path
import argparse,json
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];TPL=ROOT/'templates/onomatopoeia'
ap=argparse.ArgumentParser();ap.add_argument('asset_id');ap.add_argument('--output');args=ap.parse_args()
catalog=json.loads((TPL/'catalog.json').read_text(encoding='utf-8'))
entry=next((x for x in catalog['entries'] if x['id']==args.asset_id),None)
if entry is None:raise SystemExit('Asset ID not found. Check catalog.json.')
target=(ROOT/(args.output or f'output/onomatopoeia-exports/{args.asset_id}.png')).resolve();target.relative_to(ROOT)
if target.exists():raise SystemExit('Existing files will not be overwritten. Choose a different output.')
target.parent.mkdir(parents=True,exist_ok=True);Image.open(TPL/entry['image']['path']).convert('RGBA').save(target,optimize=True)
print(target)
