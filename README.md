# Central Park Squirrel Field Notes

A preserved, interactive exhibit of the **2018 Central Park Squirrel Census**, revived from the 2019 course project by **Weihang Ren and Zhongyu Zhang**. Explore all 3,023 saved observations with a geographic map, filters, observer notes, and accessible sighting cards.

```sh
python3 scripts/build_site.py
```

Open **`site/index.html`** directly. The complete exhibit works offline and is ready to publish from this repository’s own GitHub Pages. No installation or server is required to export it; Python 3.9+ and its standard library are sufficient. Edit the files under `exhibit/`, then export again. The original `test.csv` and Django project remain intact.

The ready-to-open `site/` directory is included in version control. After pushing these files to `type-null/Website-central-park-squirrel-tracker`, choose **Settings → Pages → Build and deployment → Source → GitHub Actions**. On every push to `main` or `master`, the included workflow rebuilds from this repository’s local sources, checks the result, and publishes `site/` at:

**https://type-null.github.io/Website-central-park-squirrel-tracker/**

**Prepared locally; not yet deployed.** The main blog can embed this URL with an open-in-new-tab button and a local screenshot fallback. When this repository deploys an update, that embedded URL serves the new version without copying app files into the blog repository. This public static project site fits GitHub Pages’ free hosting model.

See **[docs/EXHIBIT.md](docs/EXHIBIT.md)** for the export workflow, data provenance, interpretation limits, and validation commands. This is a read-only archive: deployment follows repository changes, but there is no scheduled data refresh or collection of new sightings.

---

## Historical project README (2019)

The original documentation below is preserved for context. Its server links and Django instructions describe the historical project, not the static exhibit above.

# IEORE4501 Final Project - Squirrel Tracker


## Server Link
https://tools2019-koh.appspot.com/
## Group Information
Group name: Project Group 42

Section: 2

Group members: Weihang Ren, Zhongyu Zhang

UNIs: [wr2325, zz2690]
## Summary
This is the final project of IEORE4501 Tools for Analytics. Detailed description at [Squirrel Tracker.doc](https://docs.google.com/document/d/1SPv3fMDKiemrR86rD-S9ecvI2npz3PljDzwCfxK2x5g/preview#).
## Features
### 1 Management Commands
#### 1.1 Import
A command that used to import the data from the CSV file. The file path should be specified at the command line after the name of the management command as follows:
```
$ python manage.py import_squirrel_data /path/to/file.csv
```
#### 1.2 Export
A command that can be used to export the data in CSV format. The file path should be specified at the command line after the name of the management command as follows:
```
$ python manage.py export_squirrel_data /path/to/file.csv
```
### 2 Views
#### 2.1 [Map](https://tools2019-koh.appspot.com/map/)
A view that shows a map that displays the location of the squirrel sightings on an OpenStreets map. Located at: /map.
#### 2.2 [Sightings List](https://tools2019-koh.appspot.com/sightings/)
A view that lists all squirrel sightings with links to edit each. Located at: /sightings.
This page also have links to create a new sighting and to access statistics.
#### 2.3 Update and Delete
A view to update a particular sighting. Located at: /sightings/\<unique-squirrel-id\>.
#### 2.4 [Add](https://tools2019-koh.appspot.com/sightings/add/)
A view to create a new sighting. Located at: /sightings/add.
#### 2.5 [Stats](https://tools2019-koh.appspot.com/sightings/stats/)
A view with general stats about the sightings. Located at: /sightings/stats.
