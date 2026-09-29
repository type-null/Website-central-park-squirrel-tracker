"""Regression tests for the actual archived census and hostile source values."""
import csv
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
from pathlib import Path
import tempfile
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('build_site', ROOT / 'scripts/build_site.py')
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)
sys.path.insert(0, str(ROOT / 'scripts'))
from check_site import check_site


class ExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = exporter.read_census(ROOT / 'test.csv')
        with (ROOT / 'test.csv').open(newline='') as handle:
            reader = csv.DictReader(handle)
            cls.headers = reader.fieldnames
            cls.row = next(reader)

    def fixture(self, changes):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        path = Path(temporary.name) / 'test.csv'
        with path.open('w', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=self.headers)
            writer.writeheader()
            writer.writerow(self.row | changes)
        return path

    def test_real_census_preserves_rows_and_duplicate_ids(self):
        self.assertEqual(len(self.records), 3023)
        self.assertEqual(len({r['key'] for r in self.records}), 3023)
        self.assertEqual(len({r['id'] for r in self.records}), 3018)
        self.assertEqual(sum(r['id'] == '37E-PM-1006-03' for r in self.records), 2)

    def test_actual_dates_unknowns_and_booleans(self):
        self.assertEqual(min(r['date'] for r in self.records), '2018-10-06')
        self.assertEqual(max(r['date'] for r in self.records), '2018-10-20')
        self.assertEqual(len({r['date'] for r in self.records}), 11)
        self.assertEqual(sum(r['age'] == 'Unknown' for r in self.records), 125)
        self.assertEqual(sum(r['fur'] == 'Unknown' for r in self.records), 55)
        self.assertEqual(sum(r['location'] == 'Unknown' for r in self.records), 64)
        self.assertEqual(sum(r['behaviors']['Foraging'] for r in self.records), 1435)
        self.assertIs(self.records[0]['behaviors']['Running'], False)

    def test_quoted_unicode_notes_are_preserved(self):
        record = exporter.read_census(self.fixture({'Other Activities': 'a comma, a "quote"\nand squirrel → tree', 'Running': ''}))[0]
        self.assertEqual(record['notes']['Other Activities'], 'a comma, a "quote"\nand squirrel → tree')
        self.assertIsNone(record['behaviors']['Running'])

    def test_script_breakout_and_separators_are_escaped(self):
        payload = {'note': '</script><script>alert("x")</script>&\u2028\u2029'}
        result = exporter.script_json(payload)
        self.assertNotIn('<', result)
        self.assertNotIn('&', result)
        self.assertNotIn('\u2028', result)
        self.assertEqual(json.loads(result), payload)

    def test_invalid_coordinates_dates_and_flags_fail_with_row(self):
        for changes in ({'X': 'NaN'}, {'Y': 'Infinity'}, {'X': '0'}, {'Y': ''}, {'Date': '10322018'}, {'Running': 'maybe'}, {'Shift': 'XX'}, {'Age': 'imaginary'}):
            with self.subTest(changes=changes), self.assertRaisesRegex(ValueError, 'Row 2:'):
                exporter.read_census(self.fixture(changes))

    def test_leading_zero_date_and_unknown_age(self):
        record = exporter.read_census(self.fixture({'Date': '01022018', 'Age': '?'}))[0]
        self.assertEqual(record['date'], '2018-01-02')
        self.assertEqual(record['age'], 'Unknown')

    def test_export_is_portable_and_preserves_original_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / '档案 with spaces'
            report = exporter.export(ROOT / 'test.csv', output)
            self.assertEqual((output / 'census-original.csv').read_bytes(), (ROOT / 'test.csv').read_bytes())
            self.assertEqual(report['source_sha256'], hashlib.sha256((ROOT / 'test.csv').read_bytes()).hexdigest())
            self.assertTrue((output / 'index.html').is_file())
            self.assertTrue((output / 'assets/park-boundary.js').is_file())
            self.assertTrue((output / 'assets/Lato-OFL.txt').is_file())
            first = (output / 'census-data.js').read_bytes()
            exporter.export(ROOT / 'test.csv', output)
            self.assertEqual(first, (output / 'census-data.js').read_bytes())

    def test_export_rejects_unowned_directory_and_bad_source_before_replacement(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'keep'
            output.mkdir()
            (output / 'important.txt').write_text('preserve')
            with self.assertRaisesRegex(ValueError, 'ownership marker'):
                exporter.export(ROOT / 'test.csv', output)
            self.assertEqual((output / 'important.txt').read_text(), 'preserve')
            with self.assertRaisesRegex(ValueError, 'Row 2:'):
                exporter.export(self.fixture({'X': 'NaN'}), output)
            self.assertTrue((output / 'important.txt').exists())

    def test_static_artifact_is_complete_and_missing_assets_fail(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'site'
            exporter.export(ROOT / 'test.csv', output)
            result = check_site(output)
            self.assertEqual(result['sightings'], 3023)
            self.assertEqual(result['files'], 14)
            self.assertGreater(result['local_references'], 8)
            (output / 'assets/lato-400-latin.woff2').unlink()
            with self.assertRaisesRegex(ValueError, 'inventory'):
                check_site(output)
            font = output / 'assets/lato-400-latin.woff2'
            font.symlink_to(ROOT / 'exhibit/assets/lato-400-latin.woff2')
            with self.assertRaisesRegex(ValueError, 'links'):
                check_site(output)
            font.unlink()
            os.link(output / 'assets/lato-700-latin.woff2', font)
            with self.assertRaisesRegex(ValueError, 'links'):
                check_site(output)

    def test_static_artifact_stale_content_and_data_fail(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'site'
            exporter.export(ROOT / 'test.csv', output)
            css = output / 'assets/exhibit.css'
            css.write_text(css.read_text() + '\n/* unexpected edit */')
            with self.assertRaisesRegex(ValueError, 'Stale artifact'):
                check_site(output)
            exporter.export(ROOT / 'test.csv', output)
            (output / 'census-data.js').write_text('window.SQUIRREL_CENSUS=[];\n')
            with self.assertRaisesRegex(ValueError, 'stale or incomplete'):
                check_site(output)

    def test_fresh_checkout_builds_source_changes_without_network(self):
        with tempfile.TemporaryDirectory() as temporary:
            temporary = Path(temporary)
            checkout = temporary / '松鼠 fresh checkout'
            for name in ('scripts', 'exhibit'):
                shutil.copytree(ROOT / name, checkout / name, ignore=shutil.ignore_patterns('__pycache__'))
            shutil.copyfile(ROOT / 'test.csv', checkout / 'test.csv')
            self.assertFalse((checkout / 'site').exists())
            css = checkout / 'exhibit/assets/exhibit.css'
            css.write_text(css.read_text() + '\n/* source-change regression */\n')
            js = checkout / 'exhibit/assets/exhibit.js'
            js.write_text(js.read_text() + '\n/* source-change regression */\n')
            with (checkout / 'test.csv').open(newline='') as handle:
                rows = list(csv.DictReader(handle))
            rows[0]['Other Activities'] = 'Source-change regression: a preserved note.'
            with (checkout / 'test.csv').open('w', newline='') as handle:
                writer = csv.DictWriter(handle, fieldnames=self.headers)
                writer.writeheader()
                writer.writerows(rows)
            guard = temporary / 'network-guard'
            guard.mkdir()
            (guard / 'sitecustomize.py').write_text('import socket\ndef blocked(*args, **kwargs):\n    raise RuntimeError("Build must not access the network")\nsocket.socket = blocked\nsocket.create_connection = blocked\n')
            environment = os.environ | {'PYTHONPATH': str(guard), 'PYTHONDONTWRITEBYTECODE': '1'}
            for script in ('build_site.py', 'check_site.py'):
                result = subprocess.run([sys.executable, '-B', str(checkout / 'scripts' / script)], cwd=temporary, env=environment, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual((checkout / 'site/assets/exhibit.css').read_bytes(), css.read_bytes())
            self.assertEqual((checkout / 'site/assets/exhibit.js').read_bytes(), js.read_bytes())
            self.assertIn('Source-change regression: a preserved note.', (checkout / 'site/census-data.js').read_text())
            self.assertEqual((checkout / 'site/census-original.csv').read_bytes(), (checkout / 'test.csv').read_bytes())
            self.assertEqual(json.loads((checkout / 'site/export-report.json').read_text())['records'], 3023)

    def test_raw_height_sentinel_and_zero_remain_distinct(self):
        false_record = exporter.read_census(self.fixture({'Above Ground Sighter Measurement': 'FALSE'}))[0]
        zero_record = exporter.read_census(self.fixture({'Above Ground Sighter Measurement': '0'}))[0]
        self.assertEqual(false_record['notes']['Above Ground Sighter Measurement'], 'FALSE')
        self.assertEqual(zero_record['notes']['Above Ground Sighter Measurement'], '0')


if __name__ == '__main__':
    unittest.main()
