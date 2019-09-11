import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import shutil
import pandas as pd
from joblib import Parallel, delayed
import subprocess
from shapely.geometry import shape
from shapely.geometry import asPoint
import fiona
from pathlib import Path
import os
import decimal
import numpy as np
import sys
import geopandas as gpd
from geopandas.tools import sjoin
import numpy as np
from shapely.geometry import Point
from pandas import Series
def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False



class Region_maker:
    def make_regions(self,laender):

        print(laender)
        res_intersection = sjoin(self.geo_df,self.shapefiles[laender], how='inner',op='within')
        print('geoauswahl erstellt. Größe des Auswahldf:',len(res_intersection))
        testlist=list(self.shapefiles[laender])
        if 'ID' in testlist:
            testlist.remove('ID')
        testlist.remove('geometry')
        try:
            testlist.remove('NAME')
        except:
            print('No Column "NAME" in SHAPEFILE, splitting will be skipt.')
        res_intersection.drop(testlist, axis=1, inplace=True)
        try:
        	res_intersection.drop(['index_right'], axis=1, inplace=True)
        except:
        	print('index_right nicht vorhanden.')
        res_intersection.to_pickle(os.path.join(self.destinationfolder, laender + '.p'))
        res_intersection.to_csv(os.path.join(self.destinationfolder, str(laender).replace('/', '') + '.csv'), sep='\t', encoding='utf-8')
        print(res_intersection.columns)
        if 'NAME' in self.shapefiles[laender].columns:
            res_intersection.dropna(axis=0, subset=['NAME'], inplace=True)
            res_intersection.reset_index
            #print(auswahl.columns)
            #auswahl.rename(columns = {'geometry2':'geometry'}, inplace = True)
            #print(auswahl.columns)
            #d = dict(tuple(df.groupby('Name')))
            for land in self.shapefiles[laender].itertuples():
                print('zu bearbeitende region: ',land.NAME, 'Durchlauf:',land[0])
                auswahlreg = res_intersection[res_intersection.NAME==land.NAME]
                try:
                	auswahlreg.drop(['index_right'], axis=1, inplace=True)
                except:
                	print('kein Index right zum löschen, hier.')
                auswahlreg.reset_index
                myfile2 = os.path.join(self.destinationfolder, str(land.NAME).replace('/', '') + '.p')
                my_file=Path(myfile2)
                print('cols:',res_intersection.columns)
                print(len(auswahlreg))
                myfile2 = os.path.join(self.destinationfolder, str(land.NAME).replace('/', '') + '.p')
                my_file=Path(myfile2)
                if my_file.is_file():
                    auswahl2 = pd.read_pickle(myfile2)
                    os.remove(myfile2)
                    if len(auswahlreg.columns) != len(auswahl2.columns):
                        print(auswahlreg.columns, len(auswahlreg))
                        print(auswahl2.columns, len(auswahl2))
                    print('Länge Auswahl vor append: ',len(auswahlreg))
                    auswahlreg = pd.concat([auswahlreg, auswahl2])
                    print('Länge Auswahl nach append: ', len(auswahlreg))
                    try:
                        auswahlreg.drop_duplicates(subset=['ID','neuername','Kodierung'],keep='first', inplace=True)
                    except:
                        print('Fehler!!',auswahlreg)
                    res_intersection.drop(['Name'], axis=1, inplace=True)

                    print('Länge Auswahl nach drop_duplicates: ', len(auswahlreg))
                auswahlreg.to_pickle(myfile2)
    def __init__(self,shapefiles,destinationfolder,placedb,num_cores):
        datei2 = os.path.join(placedb)
        self.shapefiles=shapefiles
        self.geo_df = pd.read_pickle(os.path.join(datei2,'../placenamedb2.p'))
        ortsdb = pd.read_pickle(os.path.join(datei2,'../placenamedb.p'))
        self.geo_df = self.geo_df.merge(ortsdb, on='ID', how='inner')
        self.destinationfolder=destinationfolder


        self.num_cores=num_cores
        Parallel(n_jobs=self.num_cores)(delayed(self.make_regions)(region) for region in self.shapefiles)
