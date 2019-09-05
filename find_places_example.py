from findplaces import placelocator
import pandas as pd
import geopandas as gpd
import numpy as np
#datei = 'Orte-Register_bereinigt2.csv'
datei = '2018_Gold_GenDB_all2.csv'
pd.options.display.max_columns = 999
pd.set_option('expand_frame_repr', False)

print(datei)
dfplaces = pd.read_csv(datei,  header=0, index_col=0 , sep=',', decimal=',')

regions = gpd.read_file('GERMANEMPIRE.shp')

dfplaces['code']=np.nan
geo_region = gpd.read_file('GERMANEMPIRE.shp')

placelocator(dfplaces, regions,geo_region, 'config.json')
