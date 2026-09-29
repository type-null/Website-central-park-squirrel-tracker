"""One-time baseline: original Django map template opened directly, offline."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
source=root/'map/templates/map/map.html'
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=True)
    page=browser.new_page()
    external=[]; errors=[]
    page.route('http://**/*',lambda route:route.abort())
    page.route('https://**/*',lambda route:route.abort())
    page.on('request',lambda request:external.append(request.url) if request.url.startswith(('http://','https://')) else None)
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.goto(source.as_uri())
    result={'baseline':'Original 2019 Django map template opened directly with external network blocked','external_requests':external,'javascript_errors':errors,'visible_markers':page.locator('.leaflet-marker-icon').count(),'page_text':page.locator('body').inner_text()}
    (root/'docs/qa/legacy-baseline.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    browser.close()
