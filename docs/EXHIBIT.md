# Central Park Field Notes

This repository preserves the original 2019 Django course project and its original `test.csv`. The new exhibit is a read-only, static presentation of that saved data. It does not require Django, Google App Engine, a database, an API, or an HTTP server.

## Export and open

Run from this repository:

```sh
python3 scripts/build_site.py
```

Open `site/index.html` directly. Everything needed to display and interact with the exhibit is inside `site/`: HTML, CSS, classic JavaScript, local fonts, data, and the geographic boundary. The complete `site/` directory is kept in this repository and published by its own GitHub Pages workflow. The exhibit uses relative paths and remains portable in folders containing spaces and Unicode.

The output folder is generated and ready to commit; the `/site` ignore rule from the old Django template has been removed. Edit `exhibit/index.html`, `exhibit/assets/exhibit.css`, or `exhibit/assets/exhibit.js`, then export again. The builder converts the CSV into a classic data script; there is no runtime `fetch`, CDN, JavaScript module, live map tile, or third-party request. `export-report.json` records the source checksum and row/date counts. Existing output can only be replaced when it carries this exporter’s ownership marker.

This is an archival exhibit. GitHub Pages rebuilds on repository pushes, but no scheduled data refresh, scraping, or collection of new sightings is configured. The original files remain available for historical reference; their original server links are historical, not dependencies of the new exhibit.

## Publish this repository on GitHub Pages

The public URL will be **https://type-null.github.io/Website-central-park-squirrel-tracker/**. This setup has been prepared and tested locally; **it has not been deployed**.

1. Commit and push `site/`, `exhibit/`, `scripts/`, `tests/`, and `.github/workflows/pages.yml` along with the documentation and ignore-file changes to this repository. Keep the original `test.csv` and project source.
2. In this repository on GitHub, open **Settings → Pages → Build and deployment** and set **Source** to **GitHub Actions**.
3. Push to the repository’s `master` or `main` branch, or open **Actions → Publish squirrel exhibit → Run workflow**. The workflow builds `site/` from the repository’s saved sources, verifies the result, uploads only `site/`, and deploys it to Pages. Later source changes follow the same automatic process.
4. Once the deployment succeeds, embed or link the public URL from the blog article. The embed automatically serves the current deployment; a local screenshot fallback in the article remains available offline. Loading the independently hosted app requires a connection. The app itself remains independently downloadable and usable offline from `site/index.html`.

[GitHub Pages supports a free public static project site](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages). No custom server, paid host, database, or API account is required. The GitHub Actions workflow uses the official checkout, Pages configuration, artifact upload, and Pages deployment actions; see [GitHub’s custom Pages workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) and [publishing-source settings](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).

The workflow builds from committed `exhibit/`, `scripts/`, and `test.csv` before checking and publishing `site/`. Fonts and the geographic boundary are saved under `exhibit/assets/`; a fresh checkout needs no sibling repository, download, dependency installation, or network access to build. Committed source changes publish automatically even if the previously generated `site/` is stale. For local preview and a current ready-to-open copy, run both commands and include the changed `site/` files in the commit:

```sh
python3 scripts/build_site.py
python3 scripts/check_site.py
```

`check_site.py` rejects stale source copies, incomplete or altered generated census data, missing assets, external runtime URLs, root-relative paths that break project-site URLs, and paths escaping the static package. The workflow runs the builder, stdlib tests, and this check before uploading. Changing this repository updates this project URL and any blog embed using it; the blog’s screenshot and explanatory prose only change when you choose to edit them. No cross-repository copy or synchronization mechanism is needed.

## Data and provenance

- Original project: **Weihang Ren and Zhongyu Zhang**, Project Group 42, IEORE4501 Tools for Analytics, 2019. The historical README, original Django folders, management commands, and `test.csv` are preserved.
- Census: [2018 Central Park Squirrel Census, NYC Open Data](https://data.cityofnewyork.us/Environment/2018-Central-Park-Squirrel-Census-Squirrel-Data/vfnx-vebw), collected by [The Squirrel Census](https://www.thesquirrelcensus.com/). This exhibit uses the repository’s saved CSV, not a newly fetched or reconstructed version.
- Boundary: [NYC Parks Properties, NYC Open Data](https://data.cityofnewyork.us/Recreation/Parks-Properties/enfh-gkve), Central Park property `M010`, downloaded September 29, 2026 from `https://data.cityofnewyork.us/resource/enfh-gkve.geojson?gispropnum=M010`. The complete three-part MultiPolygon, all rings and 142 vertices, is retained in `exhibit/assets/central-park-boundary.geojson`. SHA-256: `27fab46b8393f7c4211991957382be9a0db7d0a145d9a4b4a60571bbb33027e9`.
- Fonts: local Lato and the Latin subset of Noto Sans JP, copied from the main blog’s local font collection. Both retain their supplied SIL Open Font License files in the exported assets directory.
- The squirrel illustration is original decorative SVG, not an image of an identified census animal. It is hidden from assistive technology and is not used as data.

The map uses the source `X` as longitude and `Y` as latitude, with longitude scaled by the cosine of the study area’s center latitude. North is up. Latitude and longitude grid labels provide context; no paths, lakes, terrain, or neighborhood features are invented. The current administrative property boundary is explicitly labeled as current context, not a reconstruction of the 2018 study boundary. All observations are rendered, including the 29 points just outside that boundary; none are clipped, snapped, or discarded.

## What the data says, and does not say

There are **3,023 source rows and 3,018 distinct recorded IDs**. Five IDs repeat with different coordinates. Every row has its own key and is preserved separately; both the result cards and details display the source row number. The project counts sightings, not unique animals or a measured park population.

The 11 observed dates run from October 6 through October 20, 2018. Fur counts are Gray 2,473; Cinnamon 392; Black 103; Unknown 55. Age is unknown in 125 rows (121 empty strings and four `?` values); location is unknown in 64 rows. Unknowns remain filterable rather than disappearing.

Behavior flags overlap. For example, 1,435 sightings have Foraging checked, and 854 rows have multiple primary activity flags. The summaries show counts, not exclusive slices of a whole. Blank future boolean fields are represented as not recorded, distinct from explicit false. Invalid flags, dates, and nonfinite or implausible NYC coordinates stop the export with a row-specific error.

Observer notes are shown as verbatim attributed observations. Interpretive language such as “pretended to bury a nut” is an observer account, not an independently established explanation. The source does not specify height units in its CSV header; the detail view labels numeric heights accordingly. Ground-height string `FALSE` is preserved in the source data and omitted from the displayed notes; numeric `0` remains visible.

## Validation

```sh
python3 -m unittest discover -s tests -p test_export.py -v
```

The twelve stdlib tests cover actual row counts, repeated IDs, dates, unknown categories, true/false parsing, quoted and Unicode notes, script escaping, malformed coordinates/flags, raw height sentinels, source-byte preservation, deterministic output, ownership-safe replacement, complete Pages artifact inventories, missing assets, stale source/data detection, and a fresh-checkout build with modified CSS, JavaScript, and a census note while network access is blocked.

Browser tests use Playwright with installed Chrome (or Playwright Chromium if Chrome is absent):

```sh
python3 -m unittest discover -s tests -p test_browser.py -v
```

The three browser cases test 1,440, 390, and 278 pixel widths, using a copied directory with spaces and Unicode. They block external HTTP requests and verify the complete census, unknown and intersecting filters, duplicate-ID preservation, no-match recovery, pagination, keyboard selection, actual geographic canvas selection, no-JavaScript explanation/download, and no horizontal overflow. A separate iframe readiness test verifies that only a parent-frame `type-null:embed-ping` receives the fixed `type-null:embed-ready` acknowledgement. Standalone pages, other senders, and unrelated messages receive no response; no census data is transmitted. Screenshots and measurements are written to `docs/qa/`.

The original Django map template, opened directly offline, produces no map markers, attempts six remote stylesheet/script requests, and fails on unevaluated template syntax. This is a static-file compatibility baseline, not a benchmark of the original hosted Django application. The new exhibit renders the complete map and 12 paginated cards with zero external requests, missing resources, or browser errors. Local first-ready measurements are recorded in `docs/qa/browser-results.json`; they are individual runs, not a network performance claim.

The visual review checks the same hierarchy at mobile and desktop: compact identity, one illustrated introduction, filters, a geographic map with a field note, simple summary counts, paginated observations, and provenance. The white surfaces, local typography, restrained borders, blue pill controls, and soft color blocks coordinate with the main blog while the park’s green and cream palette gives the exhibit its own identity.
