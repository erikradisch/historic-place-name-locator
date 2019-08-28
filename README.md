# historic-place-name-locator
an algorithm, which locates historic place names under consideration of historic boundaries and spelling variation

The solution consists of different sup programs.

A first algorithm (make-place-name-db) builds up a pandas data frame from several different place name gazeteers (geonames, GOV, wikidata, openstreetmap)

A second algorithm splits this database up into supdatabases according to historic boundaries (provided by shape files)

The third algorithms does the actuall place name allocation. It loads a csv with the place names ans information to their historic context and does the geogrounding of the place names.

Readmes to the functioning of thise algorithms can be found in the corresponding supfolders.

