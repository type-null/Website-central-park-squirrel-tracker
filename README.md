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
