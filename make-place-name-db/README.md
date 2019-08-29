# Make Place Name DB

The compilation of the place name db is a rather complex and extensive process. If one would like to skip this steps, a precompiled version can be found [here](www.urltocloud.com).

After cloning the repository, you need to provide the program with the raw gazetteers, which are used:

### GOV
The GOV gazetteer can be found [here](http://www.genealogy.net/gov/minigov/gov-data-names_current.zip). Unzip the file, put its location in the config file.

### Geonames
For Geonames, you need the [basic gazetteer](http://download.geonames.org/export/dump/allCountries.zip) and the list of [alternate names](http://download.geonames.org/export/dump/alternateNames.zip)

### Open Street Map
The utalization of openstreetmap was made possible by [this project](https://github.com/OSMNames/OSMNames). A dump of the data produced by this project can be found [here](https://github.com/geometalab/OSMNames/releases/download/v2.0/planet-latest_geonames.tsv.gz).

### Wikidata
The implementation of wikidata is so far one of the most chellenging. I wrote a [litle algorithm](), which should do the extraction over the official sparqlendpoint, however, the query is timed out by the endpoint as a consequence of the huge amount of data requested. I was forced to build my own wikidata server and rise the time out to handle this problem. If anyone finds a mistake in my sparql-query, help or hints are most appreciated. If you managed to build up your own place name gazetteer from wikidata, you need tu run the programme [wikidatatype] to assign the place types, which are used inside the programme. If you would like to use a prebuild version of the wikidata-gazetteer, it can be found [here]().

### Volga German Place Names
I also added a little gazetteer of Volga German place names compiled of data from [this website](https://www.google.com/maps/d/u/0/viewer?mid=1Sz-Sn4I1F-iqS2sNeeTPZ6-Jd8I&z=5&ll=44.713047094979764%2C45.57531150000011), because, they are mostly absent of all the other gazetteers. 

Structure of the Place Name DB

If you have wishes to use your own gazetteer or to include other gazetteers in this place name db (which would be much appreciated), in the following an introduction of the place name db is given.

