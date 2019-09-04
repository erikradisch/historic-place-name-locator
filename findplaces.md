# Usage of find_places. py

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


