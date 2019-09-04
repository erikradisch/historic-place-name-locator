import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
#import Levenshtein as L
from shapely.ops import cascaded_union
import regex as re
from joblib import Parallel, delayed
import pickle
import folium
import metaphone
import multiprocessing
import os
import shutil
import string
import os
import edlib
import time
from jellyfish._jellyfish import damerau_levenshtein_distance
from jellyfish._jellyfish import jaro_winkler
import kph
import geopandas as gpd
import mplleaflet
from shapely.geometry import Point
from geopandas.tools import sjoin
import math
import gensim
import difflib
import datetime
import json

class placelocator:
    def distance(self,origin, destination):
        lat1, lon1 = origin
        lat2, lon2 = destination
        radius = 6371  # km

        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) \
            * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = radius * c
        return d
    def neuerunde(self,name, staat_oder_region, region, code, namePlace, countBremen, placeindex, kphwert, diacritics,
                  delregnames, first):
        # Modul, dass den eigentlichen Auswahlalgoritmus durchführt.
        def auswahl(name, staat_oder_region, region, code, namePlace, countBremen, placeIndex, kphwert,
                    diacritics, delregnames, first):
            index = np.arange(0, 0)
            loadall = False

            def multisave(auswahldf, placeindex, bundesland):
                testname = str(placeindex) + '.csv'
                if not testname in os.listdir(self.folderres):
                    varbremenwrite(auswahldf, placeindex, 'multi', bundesland)

                    zahl = len(os.listdir(self.foldermulti))
                    auswahldf.to_pickle(self.foldermulti + str(placeindex) + '.p', protocol=2)
                    # multis = pd.concat([multis, auswahldf])
                    # multis.to_csv('multis.csv', sep='\t')
                return [tp, fp, tn, fn]

            # Modul, dass die nicht direkt zuorndbaren Treffer im oben definierten Ordner abspeichert.
            def trefferfilter(auswahldf, placeIndex, minL, name, staat_oder_region, region, code, namePlace,
                              countBremen,
                              kphwert, kphmin, maxJW):
                print('auswahldf')
                print(auswahldf)
                # auswahldf.dropna(axis=0, subset=['longitude'], inplace=True)
                # auswahldf.dropna(axis=0, subset=['latitude'], inplace=True)
                # geometry = [Point(xy) for xy in zip(auswahldf.longitude, auswahldf.latitude)]
                # # test2['geometry'] = Point([test2.longitude, test2.мкм6жвввддlatitude])
                # crs = {'init': 'epsg:4326'}
                # geo_df = gpd.GeoDataFrame(auswahldf, crs=crs, geometry=geometry)
                auswahldf.reset_index(inplace=True, drop=True)
                auswahldf['distanz'] = 0
                # auswahldf.to_csv(str(placeIndex)+'_auswahldf.csv')
                print('                                ---------                        -------')

                for eintrag in auswahldf.itertuples():
                    # print(geo_df.get_value(0, 'geometry').x, geo_df.get_value(0, 'geometry').y, eintrag.geometry.x,
                    #      eintrag.geometry.y)
                    auswahldf.loc[eintrag[0], 'distanz'] = self.distance(
                        (auswahldf.get_value(0, 'geometry').y, auswahldf.get_value(0, 'geometry').x),
                        (eintrag.geometry.y, eintrag.geometry.x))
                # geo_df.loc[eintrag[0],'distanz']=math.acos(math.sin(math.radians(geo_df.get_value(0, 'geometry').y)) * math.sin(
                #                math.radians(eintrag.geometry.y)) + math.cos(
                #                math.radians(geo_df.get_value(0, 'geometry').y)) * math.cos(
                #                math.radians(eintrag.geometry.y)) * math.cos(
                #                math.radians(eintrag.geometry.x) - math.radians(
                #                    eintrag.geometry.x))) * 6371
                # print(geo_df)
                maxdist = auswahldf['distanz'].max()
                if maxdist > 10:
                    homeregion = self.regions[self.regions['PFARREI'].isin(str(self.dfplaces.loc[placeindex, 'region']).split(';'))]
                    if len(homeregion)==0:
                        print("übernehme georegion")
                        homeregion = self.geo_region
                        homeregion.reset_index(inplace=True)
                        print(homeregion)
                        #vereint = homeregion.geometry.unary_union
                        # print(vereint)
                        auswahldf['Distanz'] = auswahldf.geometry.distance(homeregion)
                        # print(geo_df)
                        minDist = auswahldf['Distanz'].min()
                        print('MinDist', minDist)
                        auswahldf = auswahldf[auswahldf['Distanz'] == minDist]
                        print('auswahldf nach mindist:', auswahldf)
                    if len(auswahldf) == 1:
                        print('Durch Wahl des nächsgelegenen Ortes identifiziert:', name, ': ', auswahldf)
                        treffersave(auswahldf, placeIndex, minL, name, staat_oder_region, region,
                                    code, namePlace, countBremen, kphwert, kphmin, maxJW)

                        print(
                            '                                                                 treffer durch Wahl nach geringstem Abstand für: ' + name)
                    else:
                        multisave(auswahldf, placeIndex, region)

                else:
                    print('Alle multiplen Treffer liegen nicht weiter als 10 km auseinander. Wähle ersten Treffer!')
                    auswahldf.reset_index(inplace=True, drop=True)
                    treffersave(auswahldf[0:1], placeIndex, minL, name, staat_oder_region, region,
                                code, namePlace, countBremen, kphwert, kphmin, maxJW)

            def treffersave(auswahldf, placeindex, minL, name, staat_oder_region, region, code, namePlace,
                            countBremen,
                            kphwert, kphmin, MaxJW):
                neuschreiben = False
                if os.path.isfile(self.folderres + str(placeindex) + '.p'):
                    alteserg = pd.read_pickle(self.folderres + str(placeindex) + '.p')
                    #        altesMaxJW = alteserg['jarowinkler'].max()
                    altesminL = alteserg['levenstein'].max()
                    #        if MaxJW > altesMaxJW:
                    if minL < altesminL:
                        neuschreiben = True
                        print('                 Alter Eintrag wird überschrieben, da besseres Match gefunden wurde')
                        if self.setgold:
                            # print('Suche nach bereits erstellten Visualisierungen für', placeindex)
                            for filename in os.listdir('maps/'):
                                print(filename)
                                if str(placeindex) in filename:
                                    os.remove('maps/' + filename)
                                    # print('gelöscht')
                    else:
                        pass
                        # print('Altes MinL:',altesminL,'neues MinL:',minL)

                else:
                    neuschreiben = True
                if neuschreiben:
                    varbremenwrite(auswahldf, placeindex, 'treffer', region)

                    auswahldf.to_pickle(self.folderres + str(placeindex) + '.p', protocol=2)
                # if MaxJW<0.94:
                print('                        ' + name + ' identifiziert als: ' + str(
                    auswahldf['neuername'].tolist()[0]) + ' Gefunden: ' + str(
                    len(os.listdir(self.folderres))) + ' Unsichere Treffer: ' + str(
                    len(os.listdir(self.foldermulti))) + ' Ohne Treffer: ' + str(len(os.listdir(self.foldernores))))
                gesamt = len(os.listdir(self.folderres)) + len(os.listdir(self.foldermulti)) + len(os.listdir(self.foldernores))
                print(gesamt)
                print('                        ' + name + ': Gefunden: ' + str(
                    len(os.listdir(self.folderres)) / gesamt * 100) + '% Unsichere Treffer: ' + str(
                    len(os.listdir(self.foldermulti)) / gesamt * 100) + '% Ohne Treffer: ' + str(
                    len(os.listdir(self.foldernores)) / gesamt * 100) + '%')

                if (MaxJW < 0.96) and (minL > 2 or kphmin > 0) and (region in self.neighborhood):
                    del auswahldf
                    self.neuerunde(name, staat_oder_region, region, code, namePlace, countBremen, placeindex,

                              kphwert, True, True, False)

            def varbremenwrite(auswahldf, placeindex, art, region):
                tp = fp = tn = fn = 0
                if len(auswahldf) == 0:
                    print('leeres DF!!!! Bei: ' + self.dfplaces.loc[placeindex, 'ort'] + ' Bei: ' + art)
                auswahldf.reset_index(inplace=True, drop=True)
                auswahldf[self.table_place_name_org] = self.dfplaces.loc[placeindex, self.table_place_name_cleaned]
                auswahldf[self.table_place_name_cleaned] = self.dfplaces.loc[placeindex, self.table_place_name_cleaned]
                auswahldf[self.table_region_name] = self.dfplaces.loc[placeindex, self.table_region_name]
                auswahldf[self.table_place_country_code] = self.dfplaces.loc[placeindex, self.table_place_country_code]
                auswahldf[self.table_place_count] = self.dfplaces.loc[placeindex, self.table_place_count]
                print('typ', type(auswahldf))
                if self.setgold == True:
                    print(self.dfplaces.loc[placeindex, self.table_place_name_cleaned], ' , ', self.dfplaces.loc[placeindex, self.table_region_name])

                    trefferpia = self.geo_gold[self.geo_gold.index == placeindex]
                    print('Aus Goldstandard ermittelter Treffer für:', self.dfplaces.loc[placeindex, 'ort'], '-', placeindex, '(',
                          type(placeindex), ')')
                    # print(trefferpia)
                    # print(self.geo_gold.get_value(placeindex,'ID'))

                    if len(trefferpia) > 0:
                        auswahldf.reset_index(inplace=True, drop=True)
                        # auswahldf.to_csv(str(placeIndex) + '_auswahldf2.csv')
                        # trefferpia.to_csv(str(placeIndex) + 'trefferpia2.csv')
                        # geometry = [Point(xy) for xy in zip(auswahldf.longitude, auswahldf.latitude)]
                        # crs = {'init': 'epsg:4326'}
                        # geo_auswahl = gpd.GeoDataFrame(auswahldf, crs=crs, geometry=geometry)
                        trefferpia.reset_index(inplace=True, drop=True)
#                        print(trefferpia)
#                        print(auswahldf)
                        trefferpia.loc[0, 'distanzgold'] = self.distance(
                            (auswahldf.get_value(0, 'geometry').y, auswahldf.get_value(0, 'geometry').x),
                            (trefferpia.get_value(0, 'geometry').y, trefferpia.get_value(0, 'geometry').x))
#                        print('geoauswahl.geometry:', auswahldf)
#                        print('trefferpia.geometry:', trefferpia)
                        print('Distanz zwischen Goldstandard und gefundenen Punkt: ', trefferpia.loc[0, 'distanzgold'])
                        print('Ostrsindex=', placeindex)
                        childobjects = []
                        if trefferpia.loc[0, 'distanzgold'] < 25:
                            print('ÜBEREINSTIMMUNG!!!!!!!!!!!!!!!!!!!!!!')
                            tp += 1
                        else:
                            fp += 1
                            pfarreiauswahl = self.regions[self.regions['PFARREI'].isin(str(self.dfplaces.loc[placeindex, 'region']).split(';'))]
                            if len(pfarreiauswahl)==0:
                                print("übernehme georegion")
                                pfarreiauswahl = self.geo_region
                            pfarreiauswahl.reset_index(inplace=True, drop=True)
                            print(name,'!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1',region,self.dfplaces.loc[placeindex, 'region'],len(self.geo_region), pfarreiauswahl)

                            auswahldf.loc[:, 'Distanz'] = auswahldf.geometry.distance(
                                pfarreiauswahl.get_value(0, 'geometry'))
                            auswahldf.loc[:, 'Distanz2'] = auswahldf.geometry.distance(
                                trefferpia.get_value(0, 'geometry'))
                            trefferpia.loc[:, 'Distanz'] = trefferpia.geometry.distance(
                                pfarreiauswahl.get_value(0, 'geometry'))

                            print('Gefunden durch Pia: ', trefferpia.get_value(0, self.table_place_name_cleaned),
                                  'Entfernung zur Region: ',
                                  trefferpia.get_value(0, 'Distanz'))
                            print('Gefunden durch Algorithmus: ', auswahldf.get_value(0, 'neuername'),
                                  'Entfernung zur Region: ', auswahldf.get_value(0, 'Distanz'))
                            print('Distanz untereinander: ', trefferpia.loc[0, 'distanzgold'])
                            print('Aufwahldf spalten:',auswahldf.columns)
                            if 'ID_left' in auswahldf.columns:
                                auswahldf['ID']=auswahldf['ID_left']
                            print(('Goldstandard: ' + str(trefferpia.get_value(0, self.table_place_name_cleaned)) + '\n Algorithmus: ' + str(
                                auswahldf.get_value(0, 'neuername')) + ' Typ: ' + str(
                                auswahldf.get_value(0, 'Kodierung')) + 'ID: ' + str(auswahldf.get_value(0, 'ID'))))

                            # base.suptitle('bold figure suptitle', fontsize=14, fontweight='bold')
                            # mplleaflet.show(fig=base.figure, crs=pfarreiauswahl.crs, tiles='cartodb_positron',
                            #                   path=str(placeindex) + '_' + str(self.dfplaces.loc[placeindex, 'ort']).replace('/','_')+ '_' + str(self.dfplaces.loc[placeindex, self.table_region_name]).replace('/','_') + '.html')
                            # plt.savefig(str(placeindex)+'_'+self.dfplaces.loc[placeindex,'ort']+'.png')
                            curr_map = folium.Map(
                                location=[auswahldf.get_value(0, 'geometry').y, auswahldf.get_value(0, 'geometry').x],
                                tiles='openstreetmap',
                                zoom_start=10)
                            fg = folium.FeatureGroup(name="Treffer")
                            for index, row in auswahldf.iterrows():
                                #print(row)
                                textset = ''
                                textset = 'Index: ' + str(row.index) + ' <br>count: ' + str(
                                    row.count) + ' <br>staat_oder_region: ' + str(
                                    row[self.table_region_name]) + ' <br>OrtBereinigt: ' + str(
                                    row[self.table_place_name_org]) + ' <br>OrtGenDB: ' + str(
                                    row[self.table_place_name_cleaned]) + ' <br>Zugewiesener Ort: ' + str(
                                    row.neuername) + ' <br>Typ: ' + str(row.Kodierung) + ' <br>Herkunft: ' + str(
                                    row.Herkunft) + ' <br>ID: ' + str(row.ID)
                                # textset2=unicode(row['name'], "utf-8")+' - '+unicode(row['Gubernija'], "utf-8")
                                print('Markertext:', textset)
                                fg.add_child(
                                    folium.Marker([row.geometry.y, row.geometry.x], icon=folium.Icon(color='red'),
                                                  popup=textset,
                                                  #                                  icon = folium.features.DivIcon(
                                                  #                                    icon_size=(400, 36),
                                                  #                                    icon_anchor=(0, 0),
                                                  #                                    html='<div style="font-size: 24pt"> <font size="-1">'+textset2+'</font> </div>',
                                                  #           )
                                                  ))
                            for index, row in trefferpia.iterrows():
                                # print(row)
                                textset = ''
                                textset = 'Index: ' + str(row.index) + ' <br>count: ' + str(
                                    row.count) + ' <br>staat_oder_region: ' + str(
                                    row[self.goldstandard_region_name_assigned]) + ' <br>OrtBereinigt: ' + str(
                                    row[self.table_place_name_cleaned]) + ' <br>Ort: ' + str(
                                    row[self.table_place_name_org]) + ' <br>Wo gefunden: ' + str(row[9]) + ' <br>ID: ' + str(
                                    row.ID) + ' <br>Link:  <a href="' + str(row.Link) + '">Link</a> '
                                # textset2=unicode(row['name'], "utf-8")+' - '+unicode(row['Gubernija'], "utf-8")
                                print('Markertext:', textset, row.geometry.y, row.geometry.x)
                                fg.add_child(
                                    folium.Marker([row.geometry.y, row.geometry.x], icon=folium.Icon(color='green'),
                                                  popup=textset,
                                                  #                                  icon = folium.features.DivIcon(
                                                  #                                    icon_size=(400, 36),
                                                  #                         <br>             icon_anchor=(0, 0),
                                                  #                                    html='<div style="font-size: 24pt"> <font size="-1">'+textset2+'</font> </div>',
                                                  #           )
                                                  ))
                            folium.GeoJson(pfarreiauswahl).add_to(fg)
                            curr_map.add_child(fg)
                            # curr_map.save(str(placeindex) + '_' + str(self.dfplaces.loc[placeindex, 'ort']).replace('/', '_') + '_ngef.html')
                            curr_map.save(
                                'maps/' + str(placeindex) + '_' + str(self.dfplaces.loc[placeindex, 'ort']).replace('/',
                                                                                                          '-') + '.html')
                    else:
                        # extra+=1
                        if len(auswahldf) == 1:
                            print('Hier ein Extrafall: ', self.dfplaces.loc[placeindex, 'ort'], placeindex)
                            pfarreiauswahl = self.regions[self.regions['PFARREI'].isin(str(self.dfplaces.loc[placeindex, 'region']).split(';'))]
                            if len(pfarreiauswahl)==0:
                                print("übernehme georegion")
                                pfarreiauswahl = self.geo_region
                            pfarreiauswahl.reset_index(inplace=True, drop=True)
                            print('Region:', self.dfplaces.loc[placeindex, 'region'])
                            print(pfarreiauswahl)

                            pfarreiauswahl.reset_index(inplace=True, drop=True)
                            # fig, ax = plt.subplots(1, figsize=(1200, 1200))
                            # ax.set_aspect('equal')
                            # base = pfarreiauswahl.plot()
                            # geometry = [Point(xy) for xy in zip(auswahldf.longitude, auswahldf.latitude)]
                            # crs = {'init': 'epsg:4326'}
                            # geo_auswahl = gpd.GeoDataFrame(auswahldf, crs=crs, geometry=geometry)
                            # plotauswahl = geo_auswahl.plot(column='neuername', ax=base, color='red', markersize=10, legend=True)

                            # base.set_title('Goldstandard: - Algorithmus: '+geo_auswahl.get_value(0,'neuername')+ ' Typ: '+str(geo_auswahl.get_value(0,'ObjekttypNr'))+'ID: '+str(geo_auswahl.get_value(0,'ID')))
                            print(str(placeindex).replace('.0', '') + '_' + str(self.dfplaces.loc[placeindex, 'ort']).replace('/',
                                                                                                                    '_') + '_' + str(
                                self.dfplaces.loc[placeindex, self.table_region_name]).replace('/', '_') + '.html')
                            # mplleaflet.show(fig=base.figure, crs=pfarreiauswahl.crs, tiles='cartodb_positron',path=str(placeindex).replace('.0','') + '_' + str(self.dfplaces.loc[placeindex, 'ort']).replace('/','_')+ '_' + str(self.dfplaces.loc[placeindex, self.table_region_name]).replace('/','_') + '.html')
                            # plt.savefig(str(placeindex) + '_' + self.dfplaces.loc[placeindex, 'ort'] + '_besser.png')
                            curr_map = folium.Map(
                                location=[auswahldf.get_value(0, 'geometry').y, auswahldf.get_value(0, 'geometry').x],
                                tiles='openstreetmap',
                                zoom_start=10)
                            fg = folium.FeatureGroup(name="Treffer")
                            for index,row in auswahldf.iterrows():
                                # print(row)
                                textset = ''
                                textset = 'Index: ' + str(row.index) + ' <br>count: ' + str(
                                    row.count) + ' <br>staat_oder_region: ' + str(
                                    row[self.goldstandard_region_name_assigned]) + ' <br>OrtBereinigt: ' + str(
                                    row[self.table_place_name_cleaned]) + ' <br>Ort: ' + str(
                                    row[self.table_place_name_org]) + ' <br>Zugewiesener Ort: ' + str(
                                    row.neuername) + ' <br>Typ: ' + str(row.Kodierung) + ' <br>Herkunft: ' + str(
                                    row.Herkunft) + ' <br>ID: ' + str(row.ID)
                                # textset2=unicode(row['name'], "utf-8")+' - '+unicode(row['Gubernija'], "utf-8")
                                print('Markertext:', textset)
                                fg.add_child(
                                    folium.Marker([row.geometry.y, row.geometry.x], icon=folium.Icon(color='red'),
                                                  popup=textset,
                                                  #                                  icon = folium.features.DivIcon(
                                                  #                                    icon_size=(400, 36),
                                                  #                                    icon_anchor=(0, 0),
                                                  #                                    html='<div style="font-size: 24pt"> <font size="-1">'+textset2+'</font> </div>',
                                                  #           )
                                                  ))
                            for row in trefferpia.itertuples():
                                # print(row)
                                textset = ''
                                textset = 'Index: ' + str(row.index) + ' <br>count: ' + str(
                                    row.count) + ' <br>staat_oder_region: ' + str(
                                    row.goldstandard_region_name_assigned) + ' <br>OrtBereinigt: ' + str(
                                    row.OrtBereinigt) + ' <br>Ort: ' + str(
                                    row.ort) + ' <br>Wo gefunden: ' + str(row[9]) + ' <br>ID: ' + str(
                                    row.ID) + ' <br>Link:  <a href="' + str(row.Link) + '">Link</a> '
                                # textset2=unicode(row['name'], "utf-8")+' - '+unicode(row['Gubernija'], "utf-8")
                                print('Markertext:', textset)
                                fg.add_child(
                                    folium.Marker([row, geometry.y, row, geometry.x], icon=folium.Icon(color='green'),
                                                  popup=textset,
                                                  #                                  icon = folium.features.DivIcon(
                                                  #                                    icon_size=(400, 36),
                                                  #                                    icon_anchor=(0, 0),
                                                  #                                    html='<div style="font-size: 24pt"> <font size="-1">'+textset2+'</font> </div>',
                                                  #           )
                                                  ))
                            folium.GeoJson(pfarreiauswahl).add_to(fg)
                            curr_map.add_child(fg)
                            # curr_map.save(str(placeindex) + '_' + str(self.dfplaces.loc[placeindex, 'ort']).replace('/', '_') + '_ngef.html')
                            curr_map.save('maps/' + str(placeindex) + '_' + str(self.dfplaces.loc[placeindex, 'ort']).replace('/',
                                                                                                                    '-') + '_besser.html')
                            fp += 1
                        else:
                            tn += 1
                    wrtiefscore(tp, fp, tn, fn, region, placeindex)

                    # base = world.plot(color='white', edgecolor='black')

                    # In[13]: cities.plot(ax=base, marker='o', color='red', markersize=5);
                    # print(self.geo_gold[self.geo_gold.index==placeindex])

            # Modul, dass die Fälle einzeln in den oben definierten Ordner sichert, die nicht gefunden wurden
            def maxlen(word):
                word = str(word).lower()
                ortsplit = re.split(r'\s|,|\.|/|-|\)|\(|\*|\[|\]', word)
                out = 0
                for word in ortsplit:
                    length = len(word)
                    if length > out:
                        out = length
                return out

            def wortlang(name, wortlaenge):
                return abs(len(name) / len(wortlaenge))

            def abstand(name, levenshteinimputwort):
                ortsplit = re.split(r'\s|,|\.|/|-|\)|\(|\*|\[|\]', name)
                return abs(len(levenshteinimput) - len(ortsplit))

            # Funkton, dass den Durchschnitt der Minimalen Levenshtein-Distanzen der Teilstrings berechnet.
            def jw(name, levenshteinimput):
                ortsplit = re.split(r'\s|,|\.|/|\)|\(|\*|\[|\]', name)
                levenshteinimput = list(filter(None, levenshteinimput))
                ortsplit = list(filter(None, ortsplit))
                jwreihe = []
                for namensteil in levenshteinimput:
                    # print(str(name)+'   -   '+str(levenshteinimput))
                    jarowinkler = -1
                    delpart = ''
                    if len(ortsplit) > 0:
                        for ortsteile in ortsplit:
                            #            print(namensteil,' -- ',ortsteile)
                            if jaro_winkler(namensteil, ortsteile) > jarowinkler:
                                jarowinkler = jaro_winkler(namensteil, ortsteile)
                                delpart = ortsteile
                        #            print(namensteil,delpart,ortsplit)
                        if jarowinkler == 1:
                            ortsplit.remove(delpart)
                        jwreihe.append(jarowinkler)
                    else:
                        jwreihe.append(0.8)
                out = sum(jwreihe) / len(jwreihe)
                return out

            def metaphonerechner(name, levenshteinimput):
                # print(name,levenshteinimput)
                name = re.split(r'\s|,|\.|/|\)|\(|\*|\[|\]', name)
                levenshteinimput = re.split(r'\s|,|\.|/|\)|\(|\*|\[|\]', levenshteinimput)

                metaphoneimput = list(filter(None, levenshteinimput))
                ortsplit = list(filter(None, name))
                # print(ortsplit,metaphoneimput)
                levensteinreihe = []
                #    if (levenshteinimput == ['university', 'vienna', 'vienna', 'austria']) and ('vienna' in ortsplit):
                #        print('jetzt')
                for namensteil in metaphoneimput:
                    levenstein = 100
                    # print(str(name)+'   -   '+str(levenshteinimput))
                    delpart = ''

                    if len(ortsplit) > 0:
                        for ortsteile in ortsplit:
                            # result = edlib.align(namensteil, ortsteile,additionalEqualities=[("c", "k")])
                            # if result["editDistance"] < levenstein:
                            #     levenstein = result["editDistance"]
                            #     delpart=ortsteile
                            # if ortsplit==['bierhütten']:
                            #    print(damerau_levenshtein_distance(namensteil, ortsteile),namensteil, ortsteile)
                            teil1 = metaphone.doublemetaphone(namensteil)
                            teil2 = metaphone.doublemetaphone(ortsteile)
                            ergl = damerau_levenshtein_distance(teil1[0], teil2[0])
                            if teil1[1] != '':
                                erglneu = damerau_levenshtein_distance(teil1[1], teil2[0])
                                if ergl > erglneu:
                                    ergl = erglneu
                            if teil2[1] != '':
                                erglneu = damerau_levenshtein_distance(teil1[0], teil2[1])
                                if ergl > erglneu:
                                    ergl = erglneu
                            if (teil1[1] != '') and (teil2[1] != ''):
                                erglneu = damerau_levenshtein_distance(teil1[1], teil2[1])
                                if ergl > erglneu:
                                    ergl = erglneu
                            if ergl < levenstein:
                                levenstein = ergl
                                delpart = ortsteile
                            # print(teil1,teil2, ergl)
                        # print(delpart)
                        # print(ortsplit)
                        if levenstein == 0:
                            ortsplit.remove(delpart)
                        levensteinreihe.append(levenstein)
                    else:
                        levensteinreihe.append(1)

                out = sum(levensteinreihe) / len(levensteinreihe)
                if ortsplit == ['bierhütten']:
                    print(out, sum(levensteinreihe), len(levensteinreihe))

                return out

            def kphtest(name, kphimput):
                ortsplit = re.split(r'\s|,|\.|/|\)|\(|\*|\[|\]', name)
                kphimput = re.split(r'\s|,|\.|/|\)|\(|\*|\[|\]', kphimput)

                kphimput = list(filter(None, kphimput))
                ortsplit = list(filter(None, ortsplit))
                levensteinreihe = []
                #    if (levenshteinimput == ['university', 'vienna', 'vienna', 'austria']) and ('vienna' in ortsplit):
                #        print('jetzt')
                for namensteil in kphimput:
                    levenstein = 100
                    # print(str(name)+'   -   '+str(levenshteinimput))
                    delpart = ''

                    if len(ortsplit) > 0:
                        for ortsteile in ortsplit:
                            namensteil = kph.encode(namensteil)
                            ortsteile = kph.encode(ortsteile)
                            #            print(namensteil,' -- ',ortsteile)
                            if damerau_levenshtein_distance(namensteil, ortsteile) < levenstein:
                                levenstein = damerau_levenshtein_distance(namensteil, ortsteile)
                                delpart = ortsteile
                        # print(delpart)
                        # print(ortsplit)
                        levensteinreihe.append(levenstein)
                if len(levensteinreihe) > 0:
                    out = sum(levensteinreihe) / len(levensteinreihe)
                else:
                    out = 100
                return out

            def levensteinrechner(name, levenshteinimput):
                ortsplit = re.split(r'\s|,|\.|/|\)|\(|\*|\[|\]', name)
                levenshteinimput = list(filter(None, levenshteinimput))
                ortsplit = list(filter(None, ortsplit))
                levensteinreihe = []
                #    if (levenshteinimput == ['university', 'vienna', 'vienna', 'austria']) and ('vienna' in ortsplit):
                #        print('jetzt')
                for namensteil in levenshteinimput:
                    levenstein = 100
                    # print(str(name)+'   -   '+str(levenshteinimput))
                    delpart = ''

                    if len(ortsplit) > 0:
                        for ortsteile in ortsplit:
                            # result = edlib.align(namensteil, ortsteile,additionalEqualities=[("c", "k")])
                            # if result["editDistance"] < levenstein:
                            #     levenstein = result["editDistance"]
                            #     delpart=ortsteile
                            # if ortsplit==['bierhütten']:
                            #    print(damerau_levenshtein_distance(namensteil, ortsteile),namensteil, ortsteile)
                            ergl = damerau_levenshtein_distance(namensteil, ortsteile)
                            if ergl < levenstein:
                                levenstein = ergl
                                delpart = ortsteile
                        # print(delpart)
                        # print(ortsplit)
                        if levenstein == 0:
                            ortsplit.remove(delpart)
                        levensteinreihe.append(levenstein)
                    else:
                        levensteinreihe.append(1)

                out = sum(levensteinreihe) / len(levensteinreihe)
                if ortsplit == ['bierhütten']:
                    print(out, sum(levensteinreihe), len(levensteinreihe))

                return out

            tp = 0
            fp = 0
            tn = 0
            fn = 0
            if name == 'new york':
                print('hier')
            #        if str(name).find('?')>-1:
            #            if str(region)!='nan':
            #                JWWert=0.9
            #                Levwert=4
            #            else:
            #                JWWert=0.92
            #                Levwert=3
            #        else:
            if str(region) != 'nan':
                JWWert = 0.94
                Levwert = 3
            else:
                JWWert = 0.93
                Levwert = 2
            if namePlace.find('?') > 0:
                JWWert = 0.8

            kphimput = kphwert
            levenshteinimputwort = re.split(r'\s|,|\.|/|-|\)|\(|\*|\[|\]', name)
            levenshteinimput = levenshteinimputwort
            wortlaenge = name
            # Testen, ob Suchfeld begrenzt werden kann. Die geografische Begrenzung der ortsdb erfolgt in make-region
            if str(region) != 'nan':
                print('Einschränkung der Suche für ' + name + '(' + str(kphwert) + ') auf: ' + region)
                bundeslaender = region.split(';')
                index = np.arange(0, 0)
                auswahldf = gpd.GeoDataFrame()
                for bl in bundeslaender:
                    dummy = pd.read_pickle(self.folderregions + bl.strip() + '.p')
                    #                                    index_col=0, sep='\t', header=0,
                    #                                    dtype={'ID':str,'Objekttyp':str,'ObjekttypNr': str, 'Staat': str, 'adm1':str, 'adm2':str,'adm3':str,'adm4':str,'aktueller Name':str,'latitude':float,'ldName':str,'longitude':float,'neuername':str,'kphdist':object})
                    #               print(dummy['kphdist'])
                    #               dummy['kphdist']=dummy['kphdist'].apply(eval)
                    # print(dummy)
                    auswahldf = pd.concat([auswahldf, dummy])
            elif str(code) != 'nan':
                codeliste = code.split(';')
                codeliste = [item.strip() for item in codeliste]
                print('Einschränkung der Suche für ' + name + '(' + str(kphwert) + ') auf: ' + str(codeliste[0:25]))
                auswahldf = pd.read_pickle('ortsdb.p')
                loadall = True

                # auswahldf = pd.read_pickle('ortsdb.p')
                auswahldf = auswahldf[auswahldf['Staat'].isin(codeliste)]
                # auswahldf = pd.read_hdf('ortsdb.h5', 'ortsdb', where='Staat'+str(codeliste))
            else:
                print('Keine Einschränkung der Suche für ' + name + '(' + str(kphwert) + ').')
                auswahldf = pd.read_pickle('ortsdb.p')
                loadall = True

                # auswahldf = pd.read_pickle('ortsdb.p')
                # print(auswahldf.neuername.tolist())
            # print(auswahldf)
            if not diacritics:
                auswahldf.neuername = auswahldf['neuername'].map(gensim.utils.deaccent)
            if len(auswahldf[auswahldf['neuername'] == name]) > 0:
                auswahldf = auswahldf[auswahldf['neuername'] == name]
                print(namePlace, 'filterung nach korrekten Namen:', len(auswahldf))
                minL = kphmin = 0
                maxJW = 1
            else:
                print(namePlace, 'starte diflib')
                auswahldf = auswahldf[auswahldf['neuername'].isin(
                    difflib.get_close_matches(name, auswahldf['neuername'].tolist(), n=100, cutoff=0.2))]
                print(namePlace, 'diflib abgeschlossen,länge danach:', len(auswahldf))
                auswahldf.loc[:, ('wortlaenge')] = auswahldf['neuername'].apply(wortlang, wortlaenge=wortlaenge)
                auswahldf = auswahldf[auswahldf['wortlaenge'] > 0.5]
                maxWL = auswahldf['wortlaenge'].max()
                print('Länge von auswahldf nach Vergleich der Wortlängen für ' + name + ': ' + str(len(auswahldf)))
                if len(auswahldf) != 0:
                    auswahldf.reset_index(inplace=True, drop=True)
                    auswahldf.loc[:, ('ortsteildiff')] = 0
                    auswahldf.loc[:, ('levenstein')] = auswahldf['neuername'].apply(levensteinrechner,
                                                                                    levenshteinimput=levenshteinimput)
                    minL = auswahldf['levenstein'].min()
                    auswahldf = auswahldf.loc[auswahldf['levenstein'] == minL]
                    print(namePlace, 'MinL', minL)
                    # print(auswahldf.sort_values(by='levenstein'))
                    print(namePlace, 'Länge von auswahldf nach levenstein für ' + name + ': ' + str(len(auswahldf)))
                    if not self.setmetphone:
                        # auswahldf.loc[:, ('kphdist')] = auswahldf['neuername'].apply(kphdist)
                        auswahldf.loc[:, ('kphtest')] = auswahldf['neuername'].apply(kphtest, kphimput=name)
                    else:
                        # auswahldf.loc[:, ('doublemetaphone')] = auswahldf['neuername'].apply(doublemetaphoncoding)
                        auswahldf.loc[:, ('kphtest')] = auswahldf['neuername'].apply(metaphonerechner,
                                                                                     levenshteinimput=name)
                    kphmin = auswahldf['kphtest'].min()
                    print(namePlace, 'Ortsnamen vor kph-min von ', name, ': ',
                          str(auswahldf['neuername'].tolist()[0:25]))
                    auswahldf = auswahldf.loc[auswahldf['kphtest'] == kphmin]
                    print(namePlace, 'KPH Min für ', name, ' = ', kphmin, ' Ortschaften: ',
                          str(auswahldf['neuername'].tolist()[0:25]))
                    auswahldf.loc[:, ('jarowinkler')] = auswahldf['neuername'].apply(jw,
                                                                                     levenshteinimput=levenshteinimput)
                    maxJW = auswahldf['jarowinkler'].max()
                    auswahldf = auswahldf.loc[auswahldf['jarowinkler'] == maxJW]
                    print(namePlace, 'Länge von auswahldf nach jarowinkler für ' + name + ': ' + str(len(auswahldf)))
                    auswahldf.loc[:, ('ortsteildiff')] = auswahldf['neuername'].apply(abstand,
                                                                                      levenshteinimputwort=levenshteinimputwort)
                    auswahldf.sort_values(['ortsteildiff'], ascending=True, inplace=True)
                    mindiff = auswahldf['ortsteildiff'].min()
                    auswahldf = auswahldf.loc[auswahldf['ortsteildiff'] == mindiff]
                    # auswahldf = auswahldf.repartition(npartitions=df.npartitions // 100)
                    print(namePlace, 'Länge von auswahldf nach ortsteildiff für ' + name + ': ' + str(len(auswahldf)))
                    auswahldf.reset_index(drop=True, inplace=True)
                    print('Länge von auswahldf für ' + name + ': ' + str(len(auswahldf)), '. Nächstes Wort: ',
                          auswahldf.get_value(0, 'neuername'))
                    print('Für: ' + name + ' maxJW: ' + str(maxJW) + ' MinL: ' + str(minL) + ' MaxWL: ' + str(
                        maxWL) + ' KPHMin: ' + str(kphmin) + '  Länge df: ' + str(len(auswahldf)))
                else:
                    minL = 100
                    kphmin = 100
                    maxJW = 0
            #            if maxJW>JWWert:
            if (minL < Levwert) and ((maxJW > JWWert) or (kphmin == 0)):
                if loadall:
                    # auswahldf.set_index('ID',drop=False, inplace =True)
                    test = pd.read_pickle('ortsdb2.p')
                    print(test)
                    print(auswahldf)
                    auswahldf = test.merge(auswahldf, on='ID', how='inner')
                    print('typ', type(auswahldf))
                if len(auswahldf) == 1:
                    treffersave(auswahldf, placeIndex, minL, name, staat_oder_region, region, code, namePlace,
                                countBremen, kphwert, kphmin, maxJW)
                    return None
                elif len(auswahldf) > 1:
                    if len(auswahldf) > 1:
                        print(namePlace, 'länge vor Typfilterung: ', len(auswahldf))
                        print(auswahldf)
                        # print(auswahldf)
                        # auswahldf =auswahldf[~auswahldf['ObjekttypNr'].isin(noplacesdf['id'])]
                        # print(namePlace,'länge nach Typfilterung non orte: ',len(auswahldf))
                        # print(auswahldf)
                        # print('Alle Treffer für: ',name,': ',auswahldf)
                        # print('--------------------------------------------------------------------------')
                        # ortscodedbeinschraenkung = ortscodedb[ortscodedb['Kodierung'] == 'Grossstadt']
                        grossstadt = auswahldf[auswahldf['Kodierung'] == 'Grossstadt']
                        # print('Großstadt: ',grossstadt)
                        print(namePlace, 'länge nach Typfilterung Gro0stadt: ', len(grossstadt))
                        # ortscodedbeinschraenkung = ortscodedb[ortscodedb['Kodierung'] == 'Große Stadt']
                        bigcity = auswahldf[auswahldf['Kodierung'] == 'Große Stadt']
                        # print('Große Stadt: ',bigcity)
                        print(namePlace, 'länge nach Typfilterung Gro0e Stadt: ', len(bigcity))
                        # ortscodedbeinschraenkung = ortscodedb[ortscodedb['Kodierung'] == 'Mittlere Stadt']
                        mittlecity = auswahldf[auswahldf['Kodierung'] == 'Mittlere Stadt']
                        # print('Mittlere Stadt: ',mittlecity)
                        # ortscodedbeinschraenkung = ortscodedb[ortscodedb['Kodierung'] == 'Stadt']
                        stadt = auswahldf[auswahldf['Kodierung'] == 'Stadt']
                        print(namePlace, 'länge nach Typfilterung Stadt: ', len(stadt))
                        # print('Stadt: ',stadt)
                        # ortscodedbeinschraenkung = ortscodedb[ortscodedb['Kodierung'] == 'Dorf']
                        dorf = auswahldf[auswahldf['Kodierung'] == 'Dorf']
                        print(namePlace, 'länge nach Typfilterung Dorf: ', len(dorf))
                        # print('Dorf: ',dorf)
                        # ortscodedbeinschraenkung = ortscodedb[ortscodedb['Kodierung'] == 'Weiler']
                        weiler = auswahldf[auswahldf['Kodierung'] == 'Weiler']
                        print(namePlace, 'länge nach Typfilterung Dorf ohne Weiler: ', len(weiler))
                        # print('Weiler: ',weiler)
                        if len(grossstadt) > 1:
                            if (minL < 2) and len(auswahldf) > 0:
                                trefferfilter(grossstadt, placeIndex, minL, name, staat_oder_region, region, code,
                                              namePlace,
                                              countBremen, kphwert, kphmin, maxJW)
                            else:
                                return [name, staat_oder_region, region, code, namePlace, countBremen, placeIndex,

                                        kphwert, tp, fp, tn, fn, diacritics, delregnames, first]
                        elif len(grossstadt) == 1:
                            auswahldf = grossstadt
                            print(namePlace, 'Treffer nach Filterung von Großstädten')
                            treffersave(auswahldf, placeIndex, minL, name, staat_oder_region, region, code,
                                        namePlace,
                                        countBremen, kphwert, kphmin, maxJW)
                            print(
                                '                                                                 treffer durch Filterung für: ' + name)
                            return None
                        else:
                            if len(bigcity) > 1:
                                if (minL < 2) and len(auswahldf) > 0:
                                    trefferfilter(bigcity, placeIndex, minL, name, staat_oder_region,
                                                  region, code, namePlace,
                                                  countBremen, kphwert, kphmin, maxJW)
                                else:
                                    return [name, staat_oder_region, region, code, namePlace,
                                            countBremen, placeIndex,

                                            kphwert, diacritics, delregnames, first]
                            elif len(bigcity) == 1:
                                auswahldf = bigcity
                                print(namePlace, 'Treffer nach Filterung von Große Städten')
                                treffersave(auswahldf, placeIndex, minL, name, staat_oder_region, region,
                                            code, namePlace, countBremen, kphwert, kphmin, maxJW)
                                return None
                                print(
                                    '                                                                 treffer durch Filterung für: ' + name)
                            else:
                                if len(mittlecity) > 1:
                                    if (minL < 2) and len(auswahldf) > 0:
                                        trefferfilter(mittlecity, placeIndex, minL, name, staat_oder_region,
                                                      region, code, namePlace,
                                                      countBremen, kphwert, kphmin, maxJW)
                                        return None
                                    else:
                                        return [name, staat_oder_region, region, code, namePlace,
                                                countBremen, placeIndex,
                                                kphwert, diacritics, delregnames, first]
                                elif len(mittlecity) == 1:
                                    auswahldf = mittlecity
                                    print(namePlace, 'Treffer nach Filterung von Große Städten')
                                    treffersave(auswahldf, placeIndex, minL, name, staat_oder_region, region,
                                                code, namePlace, countBremen, kphwert, kphmin, maxJW)
                                    return None
                                    print(
                                        '                                                                 treffer durch Filterung für: ' + name)
                                else:
                                    if len(stadt) > 1:
                                        if (minL < 2) and len(auswahldf) > 0:
                                            trefferfilter(stadt, placeIndex, minL, name, staat_oder_region,
                                                          region, code, namePlace,
                                                          countBremen, kphwert, kphmin, maxJW)
                                            return None
                                        else:
                                            return [name, staat_oder_region, region, code, namePlace,
                                                    countBremen, placeIndex,
                                                    kphwert, diacritics, delregnames, first]

                                    elif len(stadt) == 1:
                                        auswahldf = stadt
                                        print(namePlace, 'Treffer nach Filterung von Städten')
                                        treffersave(stadt, placeIndex, minL, name, staat_oder_region, region,
                                                    code, namePlace, countBremen, kphwert, kphmin, maxJW)
                                        return None
                                        print(
                                            '                                                                 treffer durch Filterung für: ' + name)

                                    else:
                                        if len(dorf) == 1 and (region == self.dfplaces.loc[placeIndex, 'region']):
                                            auswahldf = dorf
                                            print(namePlace, 'Treffer nach Filterung von Dörfer')
                                            treffersave(auswahldf, placeIndex, minL, name, staat_oder_region, region,
                                                        code, namePlace, countBremen, kphwert, kphmin, maxJW)
                                            return None
                                            print(
                                                '                                                                 treffer durch Filterung für: ' + name)
                                        else:
                                            # elif len(dorf) > 1:
                                            #     if (minL < 2) and len(auswahldf) > 0:
                                            #         trefferfilter(auswahldf, placeIndex, minL, name, staat_oder_region,
                                            #                       region, code, namePlace,
                                            #                       countBremen, lettermass, kphwert, kphmin, maxJW)
                                            #         return None
                                            #     else:
                                            #         return [name, staat_oder_region, region, code, namePlace,
                                            #                 countBremen, placeIndex,
                                            #                 lettermass,
                                            #                 kphwert, diacritics, delregnames, first]
                                            #
                                            # else:
                                            #     if len(weiler) > 1:
                                            #         if (minL < 2) and len(auswahldf) > 0:
                                            #             trefferfilter(auswahldf, placeIndex, minL, name, staat_oder_region,
                                            #                           region, code, namePlace, countBremen, lettermass,
                                            #                           kphwert, kphmin, maxJW)
                                            #             return None
                                            #         else:
                                            #             return [name, staat_oder_region, region, code, namePlace,
                                            #                     countBremen, placeIndex,
                                            #                     lettermass,
                                            #                     kphwert, diacritics, delregnames, first]
                                            #
                                            #     elif len(weiler) == 1 and (region == self.dfplaces.loc[placeIndex, 'region']):
                                            #         auswahldf = weiler
                                            #         print(namePlace, 'Treffer nach Filterung von Weiler')
                                            #         treffersave(auswahldf, placeIndex, minL, name, staat_oder_region, region,
                                            #                     code, namePlace, countBremen, lettermass, kphwert, kphmin,
                                            #                     maxJW)
                                            #         return None
                                            #         print(
                                            #             '                                                                 treffer durch Filterung für: ' + name)
                                            #    else:
                                            trefferfilter(auswahldf, placeIndex, minL, name, staat_oder_region,
                                                          region, code,
                                                          namePlace, countBremen, kphwert, kphmin, maxJW)
                                            return None
                                            print('vorzeitiger Suchabbruch wegen n eindeutigen Treffern für: ' + name)

                else:
                    return [name, staat_oder_region, region, code, namePlace,
                            countBremen, placeIndex,
                            kphwert, diacritics, delregnames, first]

            else:
                return [name, staat_oder_region, region, code, namePlace,
                        countBremen, placeIndex,
                        kphwert, diacritics, delregnames, first]

        def wrtiefscore(tp, fp, tn, fn, region, placeindex):
            print('Fscore-Werte:', tp, fp, tn, fn)
            dffscore = pd.DataFrame(index=self.index, columns=['Ortindex', 'TP', 'FP', 'TN', 'FN', 'Staat_oder_Region'])
            if fp + tp + tn + fn > 0:
                if (region != 'Passau') and (str(region) != 'nan') and (
                        str(region) != 'Deutsches_Reich'):
                    dffscore.loc[len(dffscore)] = [placeindex, tp, fp, tn, fn, 'Pfarrei']
                elif str(region) == 'nan':
                    dffscore.loc[len(dffscore)] = [placeindex, tp, fp, tn, fn, 'Welt']
                else:
                    dffscore.loc[len(dffscore)] = [placeindex, tp, fp, tn, fn, region]
                dffscore.to_csv(self.folderfscore + str(placeindex) + '.csv', sep='\t')
                print(dffscore)
                dffscore.drop(dffscore.index, inplace=True)
                for file in os.listdir(self.folderfscore):
                    dffscore = pd.concat(
                        [pd.read_csv(self.folderfscore + file, sep='\t', header=0, index_col=0), dffscore],
                        ignore_index=True)
                dffscore.to_csv('dffscore.csv', sep='\t')
                tp2 = 0
                fp2 = 0
                tn2 = 0
                fn2 = 0
                dffscore.TP.apply(lambda x: pd.to_numeric(x, errors='coerce'))
                dffscore.FP.apply(lambda x: pd.to_numeric(x, errors='coerce'))
                dffscore.TN.apply(lambda x: pd.to_numeric(x, errors='coerce'))
                dffscore.FN.apply(lambda x: pd.to_numeric(x, errors='coerce'))
                for erg in dffscore.itertuples():
                    if not (erg is None):
                        tp2 = tp2 + erg.TP
                        fp2 = fp2 + erg.FP
                        tn2 = tn2 + erg.TN
                        fn2 = fn2 + erg.FN
                try:
                    prcision = tp2 / (tp2 + fp2)
                    recall = tp2 / (tp2 + fn2)
                    accuracy = (tp2 + tn2) / (tp2 + fp2 + fn2 + tn2)

                    print('F-Score: ', str(2 * ((recall * prcision) / (recall + prcision))))
                    print('Genauigkeit: ', str(accuracy))
                except:
                    pass
                print('tp', tp2)
                print('fp', fp2)
                print('tn', tn2)
                print('fn', fn2)
                dffscorebyregion = dffscore.groupby(['Staat_oder_Region'])['TP', 'FP', 'TN', 'FN'].sum()
                dffscorebyregion['precision'] = dffscorebyregion['TP'] / (
                        dffscorebyregion['TP'] + dffscorebyregion['FP'])
                dffscorebyregion['recall'] = dffscorebyregion['TP'] / (
                        dffscorebyregion['TP'] + dffscorebyregion['FN'])
                dffscorebyregion['F-Score'] = 2 * ((dffscorebyregion['precision'] * dffscorebyregion['recall']) / (
                        dffscorebyregion['precision'] + dffscorebyregion['recall']))
                dffscorebyregion['Accuracy'] = (dffscorebyregion['TP'] + dffscorebyregion['TN']) / (
                        dffscorebyregion['TP'] + dffscorebyregion['FP'] + dffscorebyregion['TN'] + dffscorebyregion[
                    'FN'])
                # print(dffscore)
                # print(dffscorebyregion)
                dffscorebyregion.to_csv('dffscore_by_region.csv', '\t')
            print(
                '                        True Positives: ' + str(tp) + ' False Positive: ' + str(
                    fp) + ' True Negatives: ' + str(
                    tn) + ' False Negatives: ' + str(fn))

        def ngefwrite(name, staat_oder_region, region, code, namePlace, countBremen, placeindex):
            tn = fn = tp = fp = 0
            index = np.arange(0, 0)
            dfnotfound = pd.DataFrame(index=self.index,
                                      columns=['namePlace', self.table_region_name, 'region', self.table_place_country_code, 'countBremen'])
            dfnotfound.loc[len(dfnotfound)] = [namePlace, staat_oder_region, region, code, countBremen]
            zahl = len(os.listdir(self.foldernores))
            dfnotfound.to_pickle(self.foldernores + str(placeindex) + '.p', protocol=2)
            if self.setgold == True:
                trefferpia = self.geo_gold[(self.geo_gold[self.table_place_name_cleaned] == self.dfplaces.loc[placeindex, self.table_place_name_cleaned]) & (
                        self.geo_gold[self.goldstandard_region_name_assigned] == self.dfplaces.loc[placeindex, self.table_region_name])]
                if len(trefferpia) > 0:

                    trefferpia.reset_index(inplace=True, drop=True)
                    pfarreiauswahl = self.regions[self.regions['PFARREI'].isin(str(self.dfplaces.loc[placeindex, 'region']).split(';'))]
                    if len(pfarreiauswahl)==0:
                        print("übernehme georegion")
                        pfarreiauswahl = self.geo_region
                    pfarreiauswahl.reset_index(inplace=True, drop=True)
                    print('Region für', name, ':', self.dfplaces.loc[placeindex, 'region'])
                    print(name, ':', pfarreiauswahl)

                    trefferpia['gefName'] = str(trefferpia.get_value(0, self.table_place_name_cleaned))
                    # pfarreiauswahl = self.regions[self.regions['PFARREI'] == self.dfplaces.loc[placeindex, self.table_region_name]]
                    pfarreiauswahl.reset_index(inplace=True, drop=True)
                    # mplleaflet.show(fig=base.figure, crs=pfarreiauswahl.crs, tiles='cartodb_positron', path=str(placeindex) + '_' + str(self.dfplaces.loc[placeindex, 'ort']).replace('/','_')+ '_' + str(self.dfplaces.loc[placeindex, self.table_region_name]).replace('/','_') + '_ngef.html')
                    # plt.savefig(str(placeindex) + '_' + str(self.dfplaces.loc[placeindex, 'ort']).replace('/','_') + '_ngef.png')
                    curr_map = folium.Map(
                        location=[trefferpia.get_value(0, 'geometry').y, trefferpia.get_value(0, 'geometry').x],
                        tiles='openstreetmap',
                        zoom_start=10)
                    fg = folium.FeatureGroup(name="Treffer")
                    for i, row in trefferpia.iterrows():
                        # print(row)
                        textset = ''
                        textset = 'Index: ' + str(row.index) + ' <br>count: ' + str(
                            row.count) + ' <br>staat_oder_region: ' + str(
                            row[self.goldstandard_region_name_assigned]) + ' <br>OrtBereinigt: ' + str(
                            row[self.table_place_name_cleaned]) + ' <br>Ort: ' + str(
                            row[self.table_place_name_org]) + ' <br>Wo gefunden: ' + str(row[9]) + ' <br>ID: ' + str(
                            row.ID) + ' <br>Link:  <a href="' + str(row.Link) + '">Link</a> '
                        # textset2=unicode(row['name'], "utf-8")+' - '+unicode(row['Gubernija'], "utf-8")
                        print('Markertext:', textset)
                        fg.add_child(folium.Marker([row.geometry.y, row.geometry.x], icon=folium.Icon(color='green'),
                                                   popup=textset,
                                                   #                                  icon = folium.features.DivIcon(
                                                   #                                    icon_size=(400, 36),
                                                   #                                    icon_anchor=(0, 0),
                                                   #                                    html='<div style="font-size: 24pt"> <font size="-1">'+textset2+'</font> </div>',
                                                   #           )
                                                   ))
                    folium.GeoJson(pfarreiauswahl).add_to(fg)
                    curr_map.add_child(fg)
                    curr_map.save(
                        'maps/' + str(placeindex) + '_' + str(self.dfplaces.loc[placeindex, 'ort']).replace('/',
                                                                                                  '_') + '_ngef.html')
                    fn += 1
                else:
                    tn += 1
                print('ngefwrite: ', fn, fp, tp, fp)
                wrtiefscore(tp, fp, tn, fn, region, placeindex)

        if str(name) != 'nan' and str(name) != ' ':

            if first:
                result = auswahl(name, staat_oder_region, region, code, namePlace, countBremen, placeindex, kphwert,
                                 True, True, False)
            elif (str(region) != 'nan') and (len(self.search_layers)>0):
                if len(self.search_layers)>0:
                    region=self.search_layers.pop()
                    print(name,'                  ------------------- starte mit layer',region)
                    result = auswahl(name, staat_oder_region, region, code, namePlace, countBremen, placeindex,
                                     kphwert, True, True, False)
                else:
                    result = auswahl(name, staat_oder_region, np.nan, code, namePlace, countBremen, placeindex, kphwert,
                                     True, True, False)
            elif str(code) != 'nan':
                result = auswahl(name, staat_oder_region, region, np.nan, namePlace, countBremen, placeindex,
                                 kphwert, True, True, False)
            else:
                ngefwrite(name, staat_oder_region, region, code, namePlace, countBremen, placeindex)
                result = None

            if result != None:
                [name, staat_oder_region, region, code, namePlace,
                 countBremen, placeindex,
                 kphwert, diacritics, delregnames, first] = result
                if ((name == self.dfplaces.loc[result[6], self.table_place_name_cleaned]) and (len(name) > 4)) or diacritics or delregnames:
                    paargef = False
                    for paar in self.problempaare.keys():
                        if paar in name:
                            namealt = name
                            paargef = True
                            name = name.replace(paar, self.problempaare[paar])

                    if paargef:
                        print(namePlace, 'Neuer Versuch nach Ersetzung von von problematischen Buchstabenpaaren in ',
                              namealt,
                              ' zu ', name)
                        result = auswahl(name, staat_oder_region, region, code, namePlace, countBremen, placeindex,
                                         kphwert, diacritics, delregnames, False)
                        if result != None:
                            [name, staat_oder_region, region, code, namePlace,
                             countBremen, placeindex,
                             kphwert, diacritics, delregnames, first] = result
                            name = self.dfplaces.loc[result[6], self.table_place_name_cleaned]
                    if diacritics and result != None:
                        print(namePlace, 'Neuer Versuch nach Durch Entfernung von Diakritischen Zeichen.')
                        print(result[:-2] + [False] + result[-1:])
                        result = auswahl(name, staat_oder_region, region, code, namePlace, countBremen, placeindex,
                                         kphwert, diacritics, delregnames, False)

                        if result != None:
                            [name, staat_oder_region, region, code, namePlace,
                             countBremen, placeindex,
                             kphwert, diacritics, delregnames, first] = result
                            self.dfplaces.loc[result[6], self.table_place_name_cleaned]
                    if delregnames and result != None:
                        with open('regionen.p', 'rb') as f:
                            regnames = pickle.load(f)
                        namesplit = re.split(r'\s|,|\.|/|-|\)|\(|\*|\[|\]', name)
                        nameohnereg = ''
                        reggef = False
                        for teil in namesplit:
                            if teil not in regnames:
                                print(teil)
                                nameohnereg = nameohnereg + ' ' + teil
                            else:
                                reggef = True
                        if len(nameohnereg) > 3 and reggef:
                            print(namePlace, 'Neuer Versuch nach Entfernung von Regionennamen')
                            result = auswahl(name, staat_oder_region, region, code, namePlace, countBremen,
                                             placeindex, kphwert, diacritics, delregnames, False)
                            if result != None:
                                [name, staat_oder_region, region, code, namePlace,
                                 countBremen, placeindex,
                                 kphwert, diacritics, delregnames, first] = result
                                self.dfplaces.loc[result[6], self.table_place_name_cleaned]
                    if result != None:
                        self.neuerunde(name, staat_oder_region, region, code, namePlace, countBremen, placeindex,
                                  kphwert, True, True, False)

    def kphdist(self,word):
        word = str(word).lower()
        ortsplit = re.split(r'\s|,|\.|/|-|\)|\(|\*|\[|\]', word)
        out = []
        for word in ortsplit:
            out.append(kph.encode(word))
        return out
    def doublemetaphoncoding(self,word):
        word = str(word).lower()
        ortsplit = re.split(r'\s|,|\.|/|-|\)|\(|\*|\[|\]', word)
        out = []
        for word in ortsplit:
            coded = metaphone.doublemetaphone(word)
            if len(coded) > 0:
                out = out + [coded]

        return out
    def __init__(self,dfplaces, regions,geo_region, config):
        self.index = np.arange(0, 0)
        self.dfresults = pd.DataFrame(index=self.index, columns=[], )
        self.multis = pd.DataFrame(index=self.index, columns=[])
        self.dfnotfound = pd.DataFrame(index=self.index,
                                  columns=[])
        self.cwd = os.getcwd()
        self.indexplaces=[]
        with open(config, 'r') as fi:
            jsonconfig = json.load(fi)
        self.problempaare = jsonconfig['problempaare']
        self.neu = jsonconfig['new']
        self.setgold = jsonconfig['setgold']
        self.setmetphone = jsonconfig['setmetaphone']
        self.folderres = jsonconfig['folderres']
        self.foldermulti = jsonconfig['foldermulti']
        self.foldernores = jsonconfig['foldernores']
        self.folderfscore = jsonconfig['folderfscore']
        self.neighborhood = jsonconfig['neighborhood']
        self.folderregions = jsonconfig['folderregions']
        self.noplaces = jsonconfig['noplaces']
        self.allfolders = [self.folderres, self.foldermulti, self.foldernores, self.folderfscore]
        self.num_cores = jsonconfig['num_cores']
        self.table_region_name=jsonconfig['table_region_name']
        self.table_region_name_assigned=jsonconfig['table_region_name_assigned']
        self.table_place_name_org=jsonconfig['table_place_name_org']
        self.search_layers=jsonconfig['search_layers']
        self.table_place_country_code=jsonconfig['table_place_country_code']
        self.table_place_count=jsonconfig['table_place_count']
        self.table_place_name_cleaned=jsonconfig['table_place_name_cleaned']
        self.goldstandard_region_name_assigned=jsonconfig['goldstandard_region_name_assigned']
        self.table_place_name_cleaned=jsonconfig['table_place_name_cleaned']
        if self.neu:
            for ordner in self.allfolders:
                print('Bearbeite Ordner:', self.cwd, ordner)
                try:
                    gewordner = os.path.join(str(self.cwd), str(ordner))
                    print(gewordner)
                    shutil.rmtree(gewordner)
                except Exception as e:
                    print('Ordner nicht vorhanden', e)
                os.makedirs(os.path.join(str(self.cwd), str(ordner)))

        else:
            ordner = [self.folderres, self.foldermulti, self.foldernores]
            for x in ordner:
                for file in os.listdir(x):
                    # if int(file.split('.')[0])>self.indexplaces:
                    self.indexplaces.append(int(file.split('.')[0]))
            print('setze fort bei: ' + str(self.indexplaces))

        if self.setgold:
            gold = dfplaces.copy()
            gold.latitude = gold.latitude.apply(lambda x: pd.to_numeric(x, errors='coerce'))
            gold.longitude = gold.longitude.apply(lambda x: pd.to_numeric(x, errors='coerce'))
            gold['goldstandard_region_name_assigned'] = gold[self.table_region_name]
            print(len(gold))
            gold.dropna(axis=0, subset=['longitude'], inplace=True)
            gold.dropna(axis=0, subset=['latitude'], inplace=True)
            print(len(gold))
            geometry = [Point(xy) for xy in zip(gold.longitude, gold.latitude)]
            crs = {'init': 'epsg:4326'}
            self.geo_gold = gpd.GeoDataFrame(gold, crs=crs, geometry=geometry)
        datei = 'GOV-Ortstypen.csv'
        ortscodedb = pd.read_csv(datei, index_col=None, sep='\t', header=0, dtype={'id': str})
        # print(ortscodedb)
        ortscodedb2 = ortscodedb.dropna(axis=0, subset=['Kodierung'])
        noplacesdf = ortscodedb[~ortscodedb['Kodierung'].isin(ortscodedb2['Kodierung'])]
        self.dfplaces= dfplaces
        self.dfplaces['region']=self.dfplaces[self.table_region_name_assigned]
        self.dfplaces['code']=self.dfplaces[self.table_place_country_code]
        self.dfplaces['count']=self.dfplaces[self.table_place_count]
        self.dfplaces['staat_oder_region']=self.dfplaces[self.table_region_name]
        self.dfplaces['OrtBereinigt']=self.dfplaces[self.table_place_name_cleaned]
        self.dfplaces['ort']=self.dfplaces[self.table_place_name_org]
        self.regions = regions
        self.geo_region=geo_region
        self.levenshteinimput=''

        if self.setmetphone:
            self.dfplaces.loc[:, ('kphdist')] = self.dfplaces[self.table_place_name_cleaned].map(self.doublemetaphoncoding)
        else:
            self.dfplaces.loc[:, ('kphdist')] = self.dfplaces[self.table_place_name_cleaned].map(self.kphdist)


        print('kph erstellt')
        if not self.neu:
            self.dfplaces = self.dfplaces[~self.dfplaces.index.isin(self.indexplaces)]
            print('es verbleiben:', len(self.dfplaces), 'Fälle')
        # Starten des Suchalgorithmus mit num_cores parallelen Prozessen.
        tp = 0
        fp = 0
        tn = 0
        fn = 0
        a = datetime.datetime.now()
        ergsfind = Parallel(n_jobs=self.num_cores, verbose=10)(
            delayed(self.neuerunde)(ort.OrtBereinigt, ort.staat_oder_region, ort.region, ort.code, ort.ort, ort.count,
                               ort[0], ort.kphdist, True, True, True) for ort in self.dfplaces.itertuples())
        b = datetime.datetime.now()
        c = a - b
        print('Algorithmus brauchte:', c.seconds, 'Sekunden')
        index = np.arange(0, 0)
        dffscore = pd.DataFrame(index=self.index, columns=['Ortindex', 'TP', 'FP', 'TN', 'FN'])
        for file in os.listdir(self.folderfscore):
            dffscore = pd.concat([pd.read_csv(self.folderfscore + file, sep='\t', header=0, index_col=0), dffscore],
                                 ignore_index=True)
        dffscore.to_csv('dffscore.csv', sep='\t')
