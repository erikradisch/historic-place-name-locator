
# Creation of regional place name queries - how to

This walk through describes, how to produce regional files of the place name db. If one might ask, if it was not possible to query this while the search process: There are two reasons, why I did not do that. 1. A spatial join is very high perforemens costs. It is better to do the spatial join only once. 2. The search algorithm is paralelized to use as much perforemence power as possible. However, the python library joblib, which I used, does create a copy of every variable used by the process. With other words, the hole place name db would be copied at the beginning of the process. To prevent this in most of the cases, only the stored regional queries are loaded at the begining. The hole place name database follows only in case, nothing was found. If someone can come up with a better solution, please, feal free to contribute.

The following steps are required to create regional database queries:

## First:

```
shapeone = gpd.read_file('LOCATIONOFYOURSHAPEFILE'))
shapeone.rename(columns = {'COLUMNOFINTEREST':'NAME'}, inplace = True)
```
Replace LOCATIONOFYOURSHAPEFILE with the location of the shape file, which you want to load.
Peplace COLUMNOFINTEREST with the column in which the regions are sezified, you are interested in. You can also specify a column, which contains metaregions, that is, which combines more than one line. For example:
In a shapefile, one can find a column for countries and one for districs:

| Country | District |
| --- | --- |
| Country1 | District1 |
| Country1 | District2 |

If you would specify District, a file would be produced for District1 and anorther one for District2. If you would specify the column for Country, The Regions of District1 and District2 would be combined to one file. 

## Second:

Combine the shapefiles, from which you would like to create regional place name db queries in one dictionary.

```
shapefiledic={}
shapefiledic['NAMEOFHISTORICREGION1'] = shapeone
shapefiledic['NAMEOFHISTORICREGION2'] = shapetwo
```
