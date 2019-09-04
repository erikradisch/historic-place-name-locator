import pandas as pd

osm = pd.read_csv('planet-latest_geonames.tsv', sep='\t' ,dtype={'place_rank':float,'lat':float,'lon':float})
osm[osm.name=='Aachen'].to_csv('aachen.csv', sep='\t')
osm[(osm['place_rank']==30.0)&(osm['class']=='place')].to_csv('amsterdam.csv',sep='\t')
osm.dropna(axis=0, subset=['name'],inplace=True)

#osm[(osm['type']=='administrative')& (osm['place_rank']==30)].to_csv('aachen.csv',sep='\t')
#osm2 =osm[(osm['class']=='place')|(osm['place_rank'].isin([16.0,18.0,20.0,8,30]))]
osm2 =osm[((osm['class']=='place')|(osm['class']=='multiple')|(osm['class']=='boundary'))&(osm['place_rank'].isin([16.0,18.0,20.0,8,30]))]
osm2 =osm2[~osm2['type'].isin(['continent','island','ocean','sea','locality'])]
ny = osm2[(osm2['name'].str.contains('Berlin'))]
ny.to_csv('NY.csv',sep='\t')
print(osm2.groupby(['type']).count())

osm2.to_csv('osm-data.csv' , sep='\t')
