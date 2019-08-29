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
The columns type stores information about the type of the place name. Place name types are very problematic. Some gazetteers barely have a differentiation between differen places (In Geonames for example are nearly all places declared as ppl, which stands for populated place). Others do have a classification system, yet as their is no standartization, the classification systems differ greatly. The following is an attempt to unifying all if the different classification systems. The over all attempt is to save as much information as possible. It should be noted, that this is only an attempt for the very specific tast to locate as much historic places as possible. If someone has any suggestions for improovement or critics, this would be moste welcome. Please open an issue. 
The following different place types are available:
#### Metropolis:
As metropolises are understood places which are part of the following types:
Wikidata: 
Q408804;Q1025961;Q1530824;Q1548525;Q1637706;Q1907114;Q200250;Q21518270;Q3931970;Q5119
Geonames (Place rank):  no compareable classes, classification over citysizes. Places with more than 1,000,000 inhabitants are understood as metropoles.
GOV: no compareable classes.
#### Large Citiies:
##### Wikidata: 
Q1549591
##### Geonames (Place rank):  
no compareable classes, classification over citysizes. Places with more than 100,000 and less then 1,000,000 inhabitants are understood as metropoles.
##### GOV: 
no compareable classes.
#### Middle Sized Cities
Middle sized cities do not have any corresponding classtype. They are detemined in geonames as places which have less then 100,000 inhabitants and more then 50,000
#### Cities
A cities are understood places, which are part of the following types:
##### Wikidata:
Q10267336;Q104157;Q1074523;Q1093829;Q1180262;Q1187811;Q12015578;Q12131640;Q123705;Q1266818;Q1269749;Q13218690;Q133442;Q134626;Q1350536;Q13539802;Q1357964;Q13626398;Q1468524;Q1479822;Q148837;Q15063142;Q15063600;Q15063611;Q15078955;Q15092344;Q15105893;Q15127012;Q15127838;Q15219391;Q15219655;Q15221256;Q15221373;Q15253706;Q15273785;Q15584664;Q15661340;Q15715406;Q15830667;Q16830604;Q16858213;Q17135847;Q17278559;Q1739536;Q17457202;Q17468479;Q1768043;Q1968403;Q19833170;Q19886692;Q2089229;Q21010817;Q2264924;Q22865;Q23010647;Q244793;Q252916;Q253019;Q253030;Q2599457;Q2616791;Q2755753;Q2974842;Q2983893;Q2989457;Q3024240;Q3199141;Q3249005;Q32597970;Q3301053;Q3394564;Q3624078;Q3927245;Q3927261;Q3957;Q4057659;Q42744322;Q4389092;Q448801;Q5123999;Q515;Q5571369;Q558330;Q57318;Q5770918;Q582525;Q676050;Q691960;Q702492;Q707813;Q7216840;Q748149;Q820254;Q956214;
##### OSM (place rank): 
16;30
##### OSM (type): 
city;town, suburb
##### GOV: 
51.0;52.0;53.0;54.0;68.0;83.0;93.0;95.0;150.0;218.0;221.0;258.0;
##### Geonames: 
PPLA;PPLA2;PPLA3;PPLA4;PPLCH;PPLG

#### Vilage
As viliges are understood places which are part of the following gesetteer types:

##### Wikidata:
Q1115575;Q12015918;Q13100073;Q1317251;Q1372205;Q1394476;Q14788575;Q1484611;Q1500352;Q1501046;Q15129871;Q15221242;Q15284;Q15303838;Q15411644;Q15630849;Q15632133;Q15647906;Q159313;Q15974307;Q161387;Q16739079;Q1708422;Q17198545;Q17198620;Q17201685;Q17205621;Q17205735;Q17205774;Q17318027;Q17343829;Q17376095;Q17468533;Q1758856;Q1782540;Q1840161;Q1852859;Q18663566;Q18663579;Q188509;Q192601;Q2008050;Q203300;Q2039348;Q20538317;Q2116450;Q2154459;Q21672098;Q23012917;Q23828039;Q2514025;Q2911266;Q2936646;Q3558970;Q3559024;Q378636;Q4632675;Q486972;Q532;Q634099;Q7930612; 
##### OSM (place rank): 
18
##### OSM (type): 
village
##### GOV: 
18.0;40.0;49.0;55.0;65.0;66.0;92.0;120.0;121.0;143.0;144.0;145.0;163.0;169.0;180.0;257.0
##### Geonames: 
PPLF

#### Hamlets

##### Wikidata:
Q1138414;Q11732217;Q1348006;Q5084;Q131596;Q15975450;Q1623243;Q2168991
##### OSM (Place rank): 
no compareable class
##### OSM (types): 
isolated_dwelling; hamlet
##### GOV: 
14.0;69.0

