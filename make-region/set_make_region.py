import shutil
import os
from make_region import Region_maker
import geopandas as gpd

ordner='/media/snjuk/DATA/Projekt_zwetcomp/regionenOrtsdb_neu/'
shapeorigion='/media/snjuk/DATA/Projekt_zwetcomp/'
try:
      shutil.rmtree(cwd + '/' + ordner)
except:
    print('Ordner nicht vorhanden.')
try:
    os.makedirs(ordner)
except:
    print('Ordner vorhanden.')
dr_regionen = gpd.read_file(os.path.join(shapeorigion,'deutschesreich/dr-regionen.geojson'))
dr_regionen.rename(columns = {'REG_NAME':'NAME'}, inplace = True)
russland = gpd.read_file(os.path.join(shapeorigion,'Russia/russia.geojson'))
russland.rename(columns = {'NameENG':'NAME'}, inplace = True)
russland_uezdy = gpd.read_file(os.path.join(shapeorigion,'Russia/russia_uezdy.geojson'))
russland_uezdy.rename(columns = {'Gub_ID':'NAME'}, inplace = True)
astrakhan = gpd.read_file(os.path.join(shapeorigion,'Russia/astrakhan.geojson'))
astrakhan.rename(columns = {'Name':'NAME'}, inplace = True)
Preussen = gpd.read_file(os.path.join(shapeorigion,'deutschesreich/preussen-prov.geojson'))
Preussen.rename(columns = {'PROV_NAME':'NAME'}, inplace = True)
Deutsches_Reich = gpd.read_file(os.path.join(shapeorigion,'deutschesreich/dr-staat.geojson'))
Deutsches_Reich.rename(columns = {'STAAT_NAME':'NAME'}, inplace = True)
usa = gpd.read_file(os.path.join(shapeorigion,'usa/usa.geojson'))
usa.rename(columns = {'NAME':'Namelang','STUSPS':'NAME'}, inplace = True)
eu=gpd.read_file(os.path.join(shapeorigion,'euro/euro.geojson'))
bundeslaender = gpd.read_file(os.path.join(shapeorigion,'deutschesreich/dl-laender.geojson'))
bundeslaender.rename(columns = {'GEN':'NAME'}, inplace = True)
passau = gpd.read_file(os.path.join(shapeorigion,'deutschesreich/passau.geojson'))
passau.rename(columns = {'REG_NAME':'NAME'}, inplace = True)
pfarreien = gpd.read_file(os.path.join(shapeorigion,'deutschesreich/pfarreien.geojson'))
pfarreien.rename(columns = {'PFARREI':'NAME'}, inplace = True)
kreise = gpd.read_file(os.path.join(shapeorigion,'GermanEmpire/1900.geojson'))
kreise.rename(columns = {'NAME':'NAME'}, inplace = True)
kakanien= gpd.read_file(os.path.join(shapeorigion,'kakanien/kuk.geojson'))
kakanien.rename(columns = {'NAME':'NAME'}, inplace = True)
kakanien2= gpd.read_file(os.path.join(shapeorigion,'kakanien/kuk.geojson'))
kakanien2.rename(columns = {'NAME':'NAME2'}, inplace = True)
kakanien2.rename(columns = {'LAND':'NAME'}, inplace = True)
rus2002= gpd.read_file(os.path.join(shapeorigion,'2002/output2.geojson'))
ussr= gpd.read_file(os.path.join(shapeorigion,'ussr2.geojson'))
#india=gpd.read_file(os.path.join(shapeorigion,'India.geojson'))
#india.rename(columns = {'STATE':'NAME'}, inplace = True)
rus2002nostr=rus2002[rus2002['name_adm1']=='']
rus2002nostr2=rus2002[rus2002['name_adm2']=='']
rus2002=rus2002[~rus2002.index.isin(rus2002nostr.index)]
rus2002=rus2002[~rus2002.index.isin(rus2002nostr2.index)]
rus2002.dropna(axis=0, subset=['name_adm1'], inplace=True)
rus2002.dropna(axis=0, subset=['name_adm2'], inplace=True)
rus2002['region']=rus2002['name_adm1']+' '+rus2002['name_adm2']
rus2002.dropna(axis=0, subset=['geometry'], inplace=True)
rusreg=rus2002.groupby(['region']).count()
rusreg.to_csv('rusreg.csv', sep='\t')

rus2002b=rus2002.copy(deep=True)
rus2002.rename(columns = {'name_adm1':'NAME'}, inplace = True)
rus2002b.rename(columns = {'region':'NAME'}, inplace = True)

print('shapefiles eingelesen')

kaiserreich={}
#kaiserreich['Russland'] = russland
#kaiserreich['Russland_uezdy'] = russland_uezdy
#kaiserreich['usa'] = usa
#kaiserreich['Astrakhan'] = astrakhan
#kaiserreich['Russland2002'] = rus2002
#kaiserreich['Russland2002b'] = rus2002b
#kaiserreich['dr_regionen'] = dr_regionen
#kaiserreich['Deutsches_Reich'] = Deutsches_Reich
#kaiserreich['Preussen'] = Preussen
#kaiserreich['bundeslaender'] = bundeslaender
#kaiserreich['pfarreien'] = pfarreien
#kaiserreich['kreise'] = kreise
#kaiserreich['eu']=eu
kaiserreich['ussr']=ussr

kaiserreich['kuk'] = kakanien
kaiserreich['kuk2'] = kakanien2
Region_maker(kaiserreich,ordner,'/media/snjuk/DATA/Projekt_zwetcomp/',1)
