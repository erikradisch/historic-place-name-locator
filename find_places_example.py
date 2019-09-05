from findplaces import placelocator
import pandas as pd
import geopandas as gpd
import numpy as np
datei = 'place_sample.csv'
pd.options.display.max_columns = 999
pd.set_option('expand_frame_repr', False)

print(datei)
dfplaces = pd.read_csv(datei,  header=0, index_col=0 , sep='\t', decimal=',')
regions = gpd.read_file('GERMANEMPIRE.shp')
geo_region = gpd.read_file('GERMANEMPIRE.shp')

placelocator(dfplaces, regions,geo_region, 'config.json')
