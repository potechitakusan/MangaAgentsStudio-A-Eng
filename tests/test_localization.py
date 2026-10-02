"""Regression coverage for US reading order, English lettering, and source updates."""
from pathlib import Path
import hashlib
import json
import sys
import temp_workspace as tempfile
import unittest
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT/'templates/manga-project/scripts'))
from scripts import localization_sync as sync
from scripts import process_checker as checker
import typeset_manga as tm


class LocalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.assets = ROOT/'templates/manga-project/templates'
        cls.catalog = json.loads((cls.assets/'panel-templates/catalog.json').read_text(encoding='utf-8'))

    def test_every_layout_reads_left_to_right_by_row(self):
        self.assertEqual(len(self.catalog['templates']), 79)
        for item in self.catalog['templates']:
            with self.subTest(template=item['id']):
                by_row = {}
                for p in item['panels']:
                    by_row.setdefault(p['row'], []).append(p)
                self.assertEqual([p['row'] for p in item['panels']], sorted(p['row'] for p in item['panels']))
                for panels in by_row.values():
                    centers = [sum(x for x,_ in p['polygon'])/len(p['polygon']) for p in panels]
                    self.assertEqual(centers, sorted(centers))
                for mod in item['modifiers']:
                    if mod['type'] == 'character-breakout':
                        panel = item['panels'][mod['sourcePanelOrder']-1]
                        cx = sum(x for x,_ in panel['polygon'])/4
                        self.assertEqual(cx > 500, mod['side'] == 'right')

    def test_timing_panel_size_follows_english_reading_direction(self):
        for name, reverse in [('grow',False),('shrink',True)]:
            item=next(t for t in self.catalog['templates'] if t['id']=='FX-time-'+name)
            widths=[max(x for x,y in p['polygon'])-min(x for x,y in p['polygon']) for p in item['panels'] if p['row']==2]
            self.assertEqual(widths,sorted(widths,reverse=reverse))

    def test_english_wrap_preserves_words_punctuation_and_manual_lines(self):
        lines, wrapped = tm.wrap('Wait, is it ready?\nYes! Let us go.', 12)
        self.assertTrue(wrapped)
        result=[''.join(line) for line in lines]
        self.assertEqual(' '.join(result), 'Wait, is it ready? Yes! Let us go.')
        self.assertNotIn('！',''.join(result))
        self.assertTrue(all(len(line)<=12 for line in result))
        b=tm.Balloon({'id':'en','panel':1,'order':1,'kind':'speech','text':'A complete sentence.','center':[300,150],'tail':[300,250]}, {'size':24}, [])
        self.assertEqual(b.direction,'horizontal')
        page={'size':[600,400],'panels':[],'safe':None}
        issues=tm.check({'balloons':[b.entry]},page,[b],None)
        self.assertFalse(any(i['code'].startswith('PUNCT_') for i in issues))

    def test_legacy_requirement_aliases_do_not_weaken_validation(self):
        rule={'id':'proc-check','level':'強く指示','instruction':'Review the script',
              'checkpoint':'script-complete','scope':'project','condition':'After script changes',
              'completionCriteria':'A review file exists','carryForward':True,'enforcement':'agents',
              'decision':'相談済み','decisionNote':'User requested it'}
        result=checker.validate_registry({'schemaVersion':1,'requirements':[rule]})
        self.assertEqual(result['requirements'][0]['level'],'strong-instruction')
        self.assertEqual(result['requirements'][0]['decision'],'discussed')
        self.assertEqual(rule['level'],'強く指示')
        rule['enforcement']='report'
        with self.assertRaises(ValueError):
            checker.validate_registry({'schemaVersion':1,'requirements':[rule]})

    def test_source_delta_reports_add_modify_delete_without_writing(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'.work') as name:
            root=Path(name)
            (root/'changed.md').write_text('new',encoding='utf-8')
            (root/'added.md').write_text('added',encoding='utf-8')
            (root/'.work').mkdir();(root/'.work/private.md').write_text('private',encoding='utf-8')
            before={p.relative_to(root).as_posix():p.read_bytes() for p in root.rglob('*') if p.is_file()}
            baseline={'files':[{'path':'changed.md','sha256':hashlib.sha256(b'old').hexdigest()},
                               {'path':'removed.md','sha256':hashlib.sha256(b'removed').hexdigest()}]}
            result=sync.compare(baseline,sync.inventory(root))
            self.assertEqual(result['counts'],{'added':1,'modified':1,'deleted':1})
            self.assertEqual(before,{p.relative_to(root).as_posix():p.read_bytes() for p in root.rglob('*') if p.is_file()})

    def test_english_sfx_catalog_matches_actual_assets(self):
        root=self.assets/'onomatopoeia'
        data=json.loads((root/'catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(len(data['entries']),114)
        for e in data['entries']:
            with self.subTest(id=e['id']):
                p=root/e['image']['path']
                self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),e['image']['sha256'])
                self.assertTrue(e['text'].isascii())
                self.assertTrue((root/e['source_svg']).is_file())
                with Image.open(p) as im:
                    self.assertEqual(list(im.size),[e['image']['width'],e['image']['height']])
                    red,green,blue,alpha=im.convert('RGBA').split()
                    self.assertLess(alpha.getextrema()[0],255)
                    self.assertIsNone(ImageChops.difference(red,green).getbbox())
                    self.assertIsNone(ImageChops.difference(red,blue).getbbox())


if __name__=='__main__':
    unittest.main()
