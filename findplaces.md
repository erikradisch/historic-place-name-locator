# Usage of findplaces. py

note, that before using the findplaces script, you need to produce a place name db with the make-placenamedb script (or download it) and to produce the regional sub dbs through the make-region script. 

## Step 1
import the class placelocator findplaces.py into your python script (make sure that the findplaces.py is in this folder or the import folder is changed accordingly):


```
from findplaces import placelocator
 
```

## Step 2

load your list of place names. It is important, that the following columns are included:
### Original Name
This column represants the original name of the places, you are loking for

### Cleaned name
You may want to clean the name from certain problematic parts like abbreviations for example. If you do not want/need to lean it, the column for cleaned place names and original place names can also be identical.

### historical region
This column is for the regional context of the place name as it was found in the source context.

### assigned historical region
This column contains the regional context, assigned to one of the queries, produced by the make_region.py script. it is important, that the name in this column matches the name of the produced shape file.

### country code
Some cases may not have a historical region, which they can be assigned to but can be assigned to a modern state. This can be very helpfull, if you may not have a shape file with historic boarders. Then you can put into this column coundrycodes (Alpha-2). If more then one country can be assigned, seperate them with a semicolon. For example: "DE;PL" for Germany and Poland.

### count
This column contains information on a number of "hits" from your source. It may be inhabitants, or other numbers. It is rather meaningles for the algorithm. you can put a bank column here.

You do nit need to rename the columns. Your column names are assigned by a config file:
To buld an opject corectly, you need to write a config file first. An example can be found in this folder under config.json.
The config file is practicly a python dictionary with the following variables:
#### "problempaare": 
problempaare specifies pairs of letters, which may be changed in modern spellings. A typical example for German might be th to t for example. If the script does not find a match, and the name does consists of such letters, they are changed to their modern correspondent. This is also submitted as a dictionary. Thus, following the above mentiond example, a dictionary for th-t would be: {th:t}.
#### "new": 
new is a boolean, which specifies, if you want to start the algorithm from the beginning or if you want to proceed. In case of the last, all cases which already produced results in the 3 result folders (folderres,foldermulti and foldernores) are ignored.
#### "setgold":
put this true, if you have a table with manually assigned place names. 
#### "goldstandard_region_name_assigned": 
obsolet same as region_name_assigned
#### "setmetaphone": 
put true, if the algorithm should use metaphone. If false, the Kölner Phonetik is used. It is worth mentioned, that the Kölner Phonetik performed better on German names but not worse (as asumed in the first place) with forreign names - at least not in the cases, which were used so far.
#### "folderres":
specifies the folder for buffering the assigned places.
#### "foldermulti":
specifies the folder for buffering places, which could not be assigned to one but to many places.
#### "foldernores": 
specifies the folder for buffering cases with no results.
#### "folderfscore": 
specifies the folder for fscore results. (only important if goldstandard is set to true)
#### "num_cores": 
specifies the number of cores. Note that the algorithm is memory intensive. 16 gb of ram only allow 2-4 parallel cores.
#### "table_region_name": 
put here the column for the histroical region according to sources.
#### "table_region_name_assigned": 
put here the column of the assigned historical region.
#### "table_place_name_org": 
put here the column with the lace name according to the source.
#### "table_place_country_code": 
put here the countrycode.
#### "table_place_count": 
put here the coulumn with information as described above.
#### "table_place_name_cleaned": 
put here the column of cleaned place names.
#### "search_layers": 
this specifies additional search layers. This could be interesting, If you want to let the algorithm to enlarge the search region step by step. Data is specified as a list with names of sub place name dbs. More then one can by combined by semicolumns like in the following example: ["Deutsches_Reich","Niederbayern;OBEROESTERREICH;SALZBURG","Passau"] In this example, the algorithm starts in the historical context, if nothing was found, it looks in the sub-db called "Passau" than in the sub-dbs of "Niederbayern", "OBEROESTERREICH" and "SALZBURG"
#### "neighborhood": 
if you have additional neighbourhoods and you want to have some of them be used with a lower threshhold, put those neighbourhoods here.
#### "folderregions": 
specifies the places of the sub-dbs.
