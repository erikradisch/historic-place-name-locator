# historic-place-name-locator
an algorithm, which locates historic place names under consideration of historic boundaries and spelling variation

The solution consists of different sup programs.

A first algorithm (make-place-name-db) builds up a pandas data frame from several different place name gazetteers (geonames, GOV, wikidata, openstreetmap)

A second algorithm splits this database up into sub-databases according to historic boundaries (provided by shape files)

The third algorithms does the actually place name allocation. It loads a csv with the place names ans information to their historic context and does the geogrounding of the place names.

Readmes to the functioning of the algorithms can be found in the corresponding subfolders.
