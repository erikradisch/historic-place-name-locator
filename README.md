# historic-place-name-locator
an algorithm, which locates historic place names under consideration of historic boundaries and spelling variation.

The solution consists of different sub-programs.

A first algorithm (make-place-name-db in the corresponding sub-folder) builds up a pandas data frame from several different place name gazetteers (geonames, GOV, wikidata, openstreetmap)

A second algorithm (make-region in the corresponding sub-folder) splits this database up into sub-databases according to historic boundaries (provided by shape files)

The third algorithm does the actually place name allocation. It loads a csv with the place names and information to their historic context and does the geogrounding of the place names. It can be found in this folder. See findplaces.md for further instructions.
