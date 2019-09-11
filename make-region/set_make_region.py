import shutil
import os
from make_region import Region_maker
import geopandas as gpd

ordner='../regionenOrtsdb/'
shapeorigion='FOLDERFORSHAPEFILES'
try:
      shutil.rmtree(cwd + '/' + ordner)
except:
    print('Ordner nicht vorhanden.')
try:
    os.makedirs(ordner)
except:
    print('Ordner vorhanden.')
german_empire=gpd.read_file(os.path.join(shapeorigion,'deutschesreich/dr-regionen.geojson'))
german_empire.rename(columns = {'REG_NAME':'NAME'}, inplace = True)
russia = gpd.read_file(os.path.join(shapeorigion,'Russia/russia.geojson'))
russia.rename(columns = {'NameENG':'NAME'}, inplace = True)
print('shapefiles eingelesen')

shapefiles={}
shapefiles['german_empire']=german_empire

shapefiles['russia'] = russia
Region_maker(shapefiles,ordner,'/media/snjuk/DATA/Projekt_zwetcomp/',1)
