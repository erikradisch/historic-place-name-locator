# Make Place Name DB

The compilation of the place name db is a rather complex and extensive process. If one would like to skip this steps, a precompiled version can be found [here](www.urltocloud.com).

After cloning the repository, you need to provide the program with the raw gazetteers, which are used:

## GOV
The GOV gazetteer can be found [here](http://www.genealogy.net/gov/minigov/gov-data-names_current.zip). Unzip the file, put its location in the config file.

## Geonames
For Geonames, you need the [basic gazetteer](http://download.geonames.org/export/dump/allCountries.zip) and the list of [alternate names](http://download.geonames.org/export/dump/alternateNames.zip)

## Open Street Map
The utalization of openstreetmap was made possible by [this project](https://github.com/OSMNames/OSMNames). A dump of the data produced by this project can be found [here](https://github.com/geometalab/OSMNames/releases/download/v2.0/planet-latest_geonames.tsv.gz).
