#!/usr/bin/env python3
"""Export the archived census as a portable, offline static exhibit (stdlib only)."""
import argparse
import csv
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BOOL_FIELDS = ('Running', 'Chasing', 'Climbing', 'Eating', 'Foraging', 'Kuks', 'Quaas', 'Moans', 'Tail flags', 'Tail twitches', 'Approaches', 'Indifferent', 'Runs from')
TEXT_FIELDS = ('Highlight Fur Color', 'Color notes', 'Specific Location', 'Other Activities', 'Other Interactions', 'Above Ground Sighter Measurement')
REQUIRED = ('X', 'Y', 'Unique Squirrel ID', 'Date', 'Shift', 'Age', 'Primary Fur Color', 'Location', 'Hectare') + BOOL_FIELDS + TEXT_FIELDS


def parse_bool(value, row, field):
    value = value.strip().lower()
    if value == 'true':
        return True
    if value == 'false':
        return False
    if not value:
        return None
    raise ValueError(f'Row {row}: invalid {field} boolean {value!r}')


def read_census(path):
    records = []
    with Path(path).open(newline='', encoding='utf-8-sig') as handle:
        reader = csv.DictReader(handle)
        missing = set(REQUIRED) - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f'Missing CSV columns: {", ".join(sorted(missing))}')
        for rownum, row in enumerate(reader, 2):
            if None in row or any(row[key] is None for key in REQUIRED):
                raise ValueError(f'Row {rownum}: malformed CSV field count')
            try:
                lon, lat = float(row['X']), float(row['Y'])
                if not (math.isfinite(lon) and math.isfinite(lat) and -74.1 <= lon <= -73.8 and 40.6 <= lat <= 41.0):
                    raise ValueError('coordinates outside the expected NYC study area')
                raw_date = row['Date'].strip()
                if len(raw_date) != 8 or not raw_date.isascii() or not raw_date.isdigit():
                    raise ValueError('date must use eight digits in MMDDYYYY format')
                date = datetime.strptime(raw_date, '%m%d%Y').date().isoformat()
            except ValueError as error:
                raise ValueError(f'Row {rownum}: {error}') from error
            identifier = row['Unique Squirrel ID'].strip()
            if not identifier:
                raise ValueError(f'Row {rownum}: missing squirrel ID')
            shift = row['Shift'].strip()
            if shift not in ('AM', 'PM'):
                raise ValueError(f'Row {rownum}: invalid shift {shift!r}')
            def category(key, allowed):
                value = row[key].strip()
                if value in ('', '?', 'Unknown', 'unknown'):
                    return 'Unknown'
                if value not in allowed:
                    raise ValueError(f'Row {rownum}: unexpected {key} {value!r}')
                return value
            records.append({
                'key': rownum - 2, 'id': identifier, 'lon': lon, 'lat': lat,
                'date': date, 'shift': shift, 'hectare': row['Hectare'].strip(),
                'age': category('Age', ('Adult', 'Juvenile')),
                'fur': category('Primary Fur Color', ('Gray', 'Cinnamon', 'Black')),
                'location': category('Location', ('Ground Plane', 'Above Ground')),
                'behaviors': {key: parse_bool(row[key], rownum, key) for key in BOOL_FIELDS},
                'notes': {key: row[key].strip() for key in TEXT_FIELDS if row[key].strip()},
            })
    if not records:
        raise ValueError('The census has no sightings')
    return records


def script_json(value):
    # Safe even if this script is later inlined in an HTML document.
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')


def export(source=ROOT / 'test.csv', output=ROOT / 'site'):
    source, output = Path(source).resolve(), Path(output).resolve()
    records = read_census(source)  # Validate before touching an existing export.
    if output == ROOT or ROOT.is_relative_to(output) or source.is_relative_to(output) or output.is_relative_to(ROOT / 'exhibit'):
        raise ValueError('Output must be a dedicated export directory outside the source tree')
    marker = output / 'export-report.json'
    if output.exists() and any(output.iterdir()):
        try:
            owned = json.loads(marker.read_text())['generator'] == 'central-park-squirrel-exhibit'
        except (OSError, ValueError, KeyError):
            owned = False
        if not owned:
            raise ValueError('Refusing to replace a nonempty directory without this exporter’s ownership marker')
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent, prefix='squirrel-export-') as temporary:
        stage = Path(temporary) / 'site'
        shutil.copytree(ROOT / 'exhibit', stage)
        boundary = json.loads((stage / 'assets/central-park-boundary.geojson').read_text())
        (stage / 'assets/park-boundary.js').write_text('window.PARK_BOUNDARY=' + script_json(boundary) + ';\n', encoding='utf-8')
        (stage / 'census-data.js').write_text('window.SQUIRREL_CENSUS=' + script_json(records) + ';\n', encoding='utf-8')
        shutil.copyfile(source, stage / 'census-original.csv')
        report = {'generator': 'central-park-squirrel-exhibit', 'format': 1, 'records': len(records),
                  'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                  'first_date': min(r['date'] for r in records), 'last_date': max(r['date'] for r in records),
                  'unique_ids': len({r['id'] for r in records}), 'runtime': 'offline static HTML; no server required'}
        (stage / 'export-report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        if output.exists():
            shutil.rmtree(output)
        shutil.move(str(stage), output)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT / 'test.csv')
    parser.add_argument('--output', type=Path, default=ROOT / 'site')
    args = parser.parse_args()
    try:
        result = export(args.source, args.output)
    except (ValueError, OSError) as error:
        parser.exit(1, f'Export failed: {error}\n')
    print(f"Exported {result['records']:,} sightings to {args.output}/index.html")
