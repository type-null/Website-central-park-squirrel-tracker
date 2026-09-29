#!/usr/bin/env python3
"""Validate the checked-in Pages artifact and its relative offline dependencies."""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from build_site import ROOT, read_census, script_json


def check_site(site=ROOT / 'site'):
    site = Path(site).resolve()
    source = ROOT / 'exhibit'
    expected = {p.relative_to(source) for p in source.rglob('*') if p.is_file()}
    actual = {p.relative_to(site) for p in site.rglob('*') if p.is_file()}
    generated = {Path(name) for name in ('census-data.js', 'census-original.csv', 'export-report.json', 'assets/park-boundary.js')}
    if actual != expected | generated:
        raise ValueError(f'Site file inventory differs: missing={sorted(map(str, (expected | generated) - actual))}, unexpected={sorted(map(str, actual - expected - generated))}')
    for relative in actual:
        if (site / relative).is_symlink() or (site / relative).stat().st_nlink > 1:
            raise ValueError(f'Symbolic and hard links are not valid Pages assets: {relative}')
    for relative in expected:
        if (site / relative).read_bytes() != (source / relative).read_bytes():
            raise ValueError(f'Stale artifact: {relative}; run python3 scripts/build_site.py')
    raw = (ROOT / 'test.csv').read_bytes()
    records = read_census(ROOT / 'test.csv')
    if (site / 'census-original.csv').read_bytes() != raw:
        raise ValueError('Exported census differs from the preserved source')
    if (site / 'census-data.js').read_text() != 'window.SQUIRREL_CENSUS=' + script_json(records) + ';\n':
        raise ValueError('Generated observation data is stale or incomplete')
    boundary = json.loads((source / 'assets/central-park-boundary.geojson').read_text())
    if (site / 'assets/park-boundary.js').read_text() != 'window.PARK_BOUNDARY=' + script_json(boundary) + ';\n':
        raise ValueError('Generated geographic boundary differs from the local source')
    report = json.loads((site / 'export-report.json').read_text())
    if report.get('generator') != 'central-park-squirrel-exhibit' or report.get('source_sha256') != hashlib.sha256(raw).hexdigest() or report.get('records') != len(records):
        raise ValueError('Export report does not describe this source census')
    references = []

    def local_reference(value, containing, external_link=False):
        parsed = urlsplit(value)
        if parsed.scheme or parsed.netloc:
            if external_link and parsed.scheme in ('http', 'https'):
                return
            raise ValueError(f'External runtime dependency in {containing.name}: {value}')
        if parsed.path.startswith('/'):
            raise ValueError(f'Root-relative URL breaks project Pages/offline portability: {value}')
        destination = (containing.parent / unquote(parsed.path)).resolve() if parsed.path else containing
        if not destination.is_relative_to(site) or not destination.is_file():
            raise ValueError(f'Missing or escaping local asset: {value}')
        references.append(value)

    class PageLinks(HTMLParser):
        def handle_starttag(self, tag, pairs):
            attributes = dict(pairs)
            if tag == 'script' and attributes.get('type') == 'module':
                raise ValueError('The archive must use classic scripts to open directly offline')
            for key in ('src', 'href'):
                if key in attributes:
                    local_reference(attributes[key], site / 'index.html', external_link=tag == 'a')

    PageLinks().feed((site / 'index.html').read_text())
    for path in site.rglob('*.css'):
        for value in re.findall(r'url\(\s*[\'"]?([^\)\'"\s]+)', path.read_text()):
            local_reference(value, path)
    return {'files': len(actual), 'sightings': len(records), 'local_references': len(references), 'bytes': sum((site / name).stat().st_size for name in actual)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site', type=Path, default=ROOT / 'site')
    args = parser.parse_args()
    try:
        result = check_site(args.site)
    except (ValueError, OSError) as error:
        parser.exit(1, f'Site check failed: {error}\n')
    print(f"Verified {result['sightings']:,} sightings, {result['files']} files, {result['local_references']} local references, {result['bytes']:,} bytes.")
