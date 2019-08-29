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

## Structure of the Place Name DB

If you have wishes to use your own gazetteer or to include other gazetteers in this place name db (which would be much appreciated), in the following an introduction of the place name db is given.

## Structure:

Columns:
### Origin: 
This columns indicats the origin of the line. As the place name db is compilated from different sources, this columns garentees, that ever line is still traceable to its original gazetteer. 
### ID:
The column ID stores the original ID from the old gazetteer for every entry.
### State:
Here, the current contry code is saved. This column was added, as in some cases, one might not have the information in which historical country a place was located yet knows, that it is part of a courrent country.
### Type:
The columns type stores information about the type of the place name. The following different place types are available:
#### Metropolis:
#### Large Citiies:
are places with more than 1,000,000 inhabitants 
#### Middle Sized Cities
#### Cities
#### Vilage
As viliges are understood places which are part of the following gesetteer types:

Wikidata:
Q1115575;Q12015918;Q13100073;Q1317251;Q1372205;Q1394476;Q14788575;Q1484611;Q1500352;Q1501046;Q15129871;Q15221242;Q15284;Q15303838;Q15411644;Q15630849;Q15632133;Q15647906;Q159313;Q15974307;Q161387;Q16739079;Q1708422;Q17198545;Q17198620;Q17201685;Q17205621;Q17205735;Q17205774;Q17318027;Q17343829;Q17376095;Q17468533;Q1758856;Q1782540;Q1840161;Q1852859;Q18663566;Q18663579;Q188509;Q192601;Q2008050;Q203300;Q2039348;Q20538317;Q2116450;Q2154459;Q21672098;Q23012917;Q23828039;Q2514025;Q2911266;Q2936646;Q3558970;Q3559024;Q378636;Q4632675;Q486972;Q532;Q634099;Q7930612; 

Geonames (Place rank):  18

GOV: 18.0;40.0;49.0;55.0;65.0;66.0;92.0;120.0;121.0;143.0;144.0;145.0;163.0;169.0;180.0;257.0



