"""Run with Playwright and installed Chrome. No HTTP server is used."""
import json
from pathlib import Path
import shutil
import tempfile
import time
import unittest
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'


class ExhibitBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(executable_path=CHROME if Path(CHROME).exists() else None, headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def test_real_archive_filters_details_map_and_portable_layout(self):
        results = []
        qa = ROOT / 'docs/qa'
        qa.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as temporary:
            moved = Path(temporary) / '松鼠 field notes'
            shutil.copytree(ROOT / 'site', moved)
            for width in (1440, 390, 278):
                context = self.browser.new_context(viewport={'width': width, 'height': 950}, reduced_motion='reduce')
                errors, external, failed = [], [], []
                page = context.new_page()
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.on('requestfailed', lambda request: failed.append(request.url))
                page.on('request', lambda request: external.append(request.url) if request.url.startswith(('http://', 'https://')) else None)
                context.route('http://**/*', lambda route: route.abort())
                context.route('https://**/*', lambda route: route.abort())
                start = time.perf_counter()
                page.goto((moved / 'index.html').as_uri())
                page.wait_for_function("document.querySelector('#result-count').textContent === '3,023 of 3,023 sightings'")
                elapsed = round((time.perf_counter() - start) * 1000, 1)
                page.evaluate('document.fonts.ready')
                self.assertEqual(page.locator('.sighting-card').count(), 12)
                self.assertEqual(page.locator('#detail-heading').inner_text(), '39B-PM-1014-05')
                self.assertIn('pretended to bury', page.locator('#detail').inner_text())
                self.assertEqual(page.locator('#summary .stat').nth(1).inner_text(), '1,435\nseen foraging')
                self.assertFalse(page.evaluate('document.documentElement.scrollWidth > innerWidth'))
                page.screenshot(path=str(qa / f'exhibit-{width}.png'), full_page=True)
                page.select_option('#fur', 'Black')
                self.assertEqual(page.locator('#result-count').inner_text(), '103 of 3,023 sightings')
                page.select_option('#activity', 'Foraging')
                expected = page.evaluate("SQUIRREL_CENSUS.filter(r=>r.fur==='Black'&&r.behaviors.Foraging).length")
                self.assertEqual(page.locator('#result-count strong').inner_text(), str(expected))
                page.locator('button[type=reset]').click()
                page.wait_for_function("document.querySelector('#result-count strong').textContent === '3,023'")
                page.select_option('#age', 'Unknown')
                self.assertEqual(page.locator('#result-count strong').inner_text(), '125')
                page.locator('button[type=reset]').click()
                page.fill('#search', '37E-PM-1006-03')
                page.wait_for_function("document.querySelector('#result-count strong').textContent === '2'")
                self.assertEqual(page.locator('.sighting-card').count(), 2)
                first_label = page.locator('.sighting-card').nth(0).get_attribute('aria-label')
                second_label = page.locator('.sighting-card').nth(1).get_attribute('aria-label')
                self.assertNotEqual(first_label, second_label)
                page.locator('.sighting-card').nth(1).focus()
                page.keyboard.press('Enter')
                self.assertIn('appears more than once', page.locator('#detail').inner_text())
                self.assertEqual(page.locator('#detail').evaluate('el=>document.activeElement===el'), True)
                # Search a single sighting, then select its actual projected map location.
                page.fill('#search', '39B-PM-1014-05')
                page.wait_for_function("document.querySelector('#result-count strong').textContent === '1'")
                self.assertIn('1 matching sightings', page.locator('#map').get_attribute('aria-label'))
                page.fill('#search', '<script>no such squirrel</script>')
                page.wait_for_function("document.querySelector('#result-count strong').textContent === '0'")
                self.assertTrue(page.locator('#empty').is_visible())
                self.assertTrue(page.locator('#next').is_disabled())
                self.assertEqual(page.locator('#detail-heading').inner_text(), 'No matching sightings')
                page.locator('button[type=reset]').click()
                page.wait_for_function("document.querySelector('#result-count strong').textContent === '3,023'")
                page.locator('#next').click()
                self.assertEqual(page.locator('#page-label').inner_text(), '2 / 252')
                self.assertEqual(page.locator('#list-range').inner_text(), '13–24 of 3,023 sightings')
                self.assertFalse(page.evaluate('document.documentElement.scrollWidth > innerWidth'))
                # Hit a real census coordinate on the canvas after returning to all rows.
                hit = page.evaluate('''() => {
                    const points = SQUIRREL_CENSUS.map(r=>[r.lon,r.lat]).concat(PARK_BOUNDARY.features.flatMap(f=>f.geometry.coordinates).flat(2));
                    const xs=points.map(p=>p[0]), ys=points.map(p=>p[1]);
                    const x0=Math.min(...xs), x1=Math.max(...xs), y0=Math.min(...ys), y1=Math.max(...ys);
                    const c=Math.cos((y0+y1)/2*Math.PI/180), s=Math.min(545/((x1-x0)*c),580/(y1-y0));
                    const r=SQUIRREL_CENSUS[0], box=document.querySelector('#map').getBoundingClientRect();
                    return {x:(320+(r.lon-(x0+x1)/2)*c*s)/640*box.width,y:(340-(r.lat-(y0+y1)/2)*s)/680*box.height,id:r.id};
                }''')
                page.locator('#map').click(position={'x':hit['x'],'y':hit['y']})
                self.assertEqual(page.locator('#detail-heading').inner_text(), hit['id'])
                self.assertEqual(errors, [])
                self.assertEqual(external, [])
                self.assertEqual(failed, [])
                results.append({'width': width, 'ready_ms': elapsed, 'external_requests': external, 'errors': errors, 'failed_resources': failed, 'overflow': False, 'observations': 3023, 'rendered_cards': 12, 'portable_file_url': True})
                context.close()
        (qa / 'browser-results.json').write_text(json.dumps(results, indent=2) + '\n')

    def test_embed_ready_acknowledges_only_parent_ping(self):
        context = self.browser.new_context()
        errors, external = [], []
        context.route('http://**/*', lambda route: route.abort())
        context.route('https://**/*', lambda route: route.abort())
        page = context.new_page()
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('request', lambda request: external.append(request.url) if request.url.startswith(('http://', 'https://')) else None)
        with tempfile.TemporaryDirectory() as temporary:
            host = Path(temporary) / 'article.html'
            host.write_text('<!doctype html><iframe src="' + (ROOT / 'site/index.html').as_uri() + '"></iframe><script>window.readyEvents=[];addEventListener("message",event=>{if(event.source===document.querySelector("iframe").contentWindow&&event.data?.type==="type-null:embed-ready")readyEvents.push({data:event.data,origin:event.origin});});</script>')
            page.goto(host.as_uri())
            child = page.frames[1]
            child.wait_for_function("document.querySelector('#result-count strong').textContent === '3,023'")
            page.evaluate('''() => {
                const child = document.querySelector('iframe').contentWindow;
                child.postMessage(null, '*');
                child.postMessage({type:'unrelated-message'}, '*');
            }''')
            child.evaluate("window.dispatchEvent(new MessageEvent('message',{source:window,origin:'null',data:{type:'type-null:embed-ping'}}))")
            page.wait_for_timeout(75)
            self.assertEqual(page.evaluate('readyEvents'), [])
            page.evaluate("document.querySelector('iframe').contentWindow.postMessage({type:'type-null:embed-ping'}, '*')")
            page.wait_for_function('readyEvents.length === 1')
            self.assertEqual(page.evaluate('readyEvents'), [{'data': {'type': 'type-null:embed-ready'}, 'origin': 'null'}])
        page.goto((ROOT / 'site/index.html').as_uri())
        page.evaluate('''() => {
            window.readyEvents=[];
            addEventListener('message', event=>{if(event.data?.type==='type-null:embed-ready')readyEvents.push(event.data);});
            window.postMessage({type:'type-null:embed-ping'}, '*');
        }''')
        page.wait_for_timeout(75)
        self.assertEqual(page.evaluate('readyEvents'), [])
        self.assertEqual(errors, [])
        self.assertEqual(external, [])
        context.close()

    def test_no_javascript_preserves_explanation_and_download(self):
        context = self.browser.new_context(java_script_enabled=False, viewport={'width': 278, 'height': 900})
        page = context.new_page()
        page.goto((ROOT / 'site/index.html').as_uri())
        self.assertTrue(page.locator('noscript').is_visible())
        self.assertIn('original census CSV', page.locator('noscript').inner_text())
        self.assertTrue(page.locator('a[download]').first.get_attribute('href') == 'census-original.csv')
        self.assertFalse(page.evaluate('document.documentElement.scrollWidth > innerWidth'))
        context.close()


if __name__ == '__main__':
    unittest.main()
