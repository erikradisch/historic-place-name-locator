import matplotlib
matplotlib.use('Agg')
import pandas as pd
import functools
import regex as re
import kph
import numpy as np
import string
import numpy as np
import math
import time
import subprocess
from suds.client import Client
import geopandas as gpd
from shapely.geometry import Point
import mplleaflet
from joblib import Parallel, delayed
import gensim
import os
import metaphone
countrycode ={'A':'AT','B':'BE','CH':'CH','CZ':'CZ','D':'DE','ES':'ES','F':'FR','H':'HU', 'N':'NO','NL':'NL','PL':'PL','RUS':'RU','S':'SE','USA':'US','Azerbaijan':'AZ','Bulgaria':'BG','Georgia':'GE','Kazakhstan':'KZ','Moldova':'MD','Romainia':'RO','Russia':'RU','Ukraine':'UA'}
stopwort = open('german_stopwords_lite.txt','r')
stopw=[]
govneu=True


def reduce_mem_usage(props):
    start_mem_usg = props.memory_usage().sum() / 1024 ** 2
    print("Memory usage of properties dataframe is :", start_mem_usg, " MB")
    NAlist = []  # Keeps track of columns that have missing values filled in.
    for col in props.columns:
        print(props[col].dtype)
        if props[col].dtype != object and str(props[col].dtype) != 'category':  # Exclude strings

            # Print current column type
            print("******************************")
            print("Column: ", col)
            print("dtype before: ", props[col].dtype)

            # make variables for Int, max and min
            IsInt = False
            mx = props[col].max()
            mn = props[col].min()

            # Integer does not support NA, therefore, NA needs to be filled
            if not np.isfinite(props[col]).all():
                NAlist.append(col)
                props[col].fillna(mn - 1, inplace=True)

                # test if column can be converted to an integer
            asint = props[col].fillna(0).astype(np.int64)
            result = (props[col] - asint)
            result = result.sum()
            if result > -0.01 and result < 0.01:
                IsInt = True

            # Make Integer/unsigned Integer datatypes
            if IsInt:
                if mn >= 0:
                    if mx < 255:
                        props[col] = props[col].astype(np.uint8)
                    elif mx < 65535:
                        props[col] = props[col].astype(np.uint16)
                    elif mx < 4294967295:
                        props[col] = props[col].astype(np.uint32)
                    else:
                        props[col] = props[col].astype(np.uint64)
                else:
                    if mn > np.iinfo(np.int8).min and mx < np.iinfo(np.int8).max:
                        props[col] = props[col].astype(np.int8)
                    elif mn > np.iinfo(np.int16).min and mx < np.iinfo(np.int16).max:
                        props[col] = props[col].astype(np.int16)
                    elif mn > np.iinfo(np.int32).min and mx < np.iinfo(np.int32).max:
                        props[col] = props[col].astype(np.int32)
                    elif mn > np.iinfo(np.int64).min and mx < np.iinfo(np.int64).max:
                        props[col] = props[col].astype(np.int64)

                        # Make float datatypes 32 bit
            else:
                props[col] = props[col].astype(np.float32)

            # Print new column type
            print("dtype after: ", props[col].dtype)
            print("******************************")

    # Print final result
    print("___MEMORY USAGE AFTER COMPLETION:___")
    mem_usg = props.memory_usage().sum() / 1024 ** 2
    print("Memory usage is: ", mem_usg, " MB")
    print("This is ", 100 * mem_usg / start_mem_usg, "% of the initial size")
    return props
for line in stopwort:
    line = line.replace('\n', '')
    stopw.append(line)
def lettermass(word):
    abc=list(string.ascii_lowercase)
    out=0
    word =str(word).lower()
    for buchstabe in abc:
        if buchstabe in word:
            out=out+1
    return out

def kphdist(word):
    word =str(word).lower()
    ortsplit = re.split(r'\s|,|\.|/|-|\)|\(|\*|\[|\]', word)
    out=''
    for word in ortsplit:
        coded=kph.encode(word)
        if len(coded)>0:
                if len(out)>0:
                    out=out+';'+coded
                else:
                    out=coded
    return out

def doublemetaphoncoding(word):
    word =str(word).lower()
    ortsplit = re.split(r'\s|,|\.|/|-|\)|\(|\*|\[|\]', word)
    out=''
    for word in ortsplit:
        coded=metaphone.doublemetaphone(word)
        if len(coded)>0:
            codedtxt=''
            #for teil in coded:
            #    if len(codedtxt)>0:
            #        codedtxt=codedtxt+';'+teil
            #    else:
            #        codedtxt=teil
            if len(out)>0:
                out=out+';'+codedtxt
            else:
                out=codedtxt
    return out

def minlen(word):
    word =str(word).lower()
    ortsplit = re.split(r'\s|,|\.|/|-|\)|\(|\*|\[|\]', word)
    out=10000
    for word in ortsplit:
        length=len(word)
        if (length<out) and length>1:
                out=length
    return out

#Einlesen der Liste der Wikidata Ortschaften
datei='osm-data.csv'
osm = pd.read_csv(datei , sep='\t',index_col=0)
osm.ldName=osm.name.str.lower()
aachendf=osm[osm.name=='aachen']
print(aachendf)
#print(osm)
osm.rename(columns={'alternative_names':'altname'},inplace=True)
osm.reset_index()
print(len(osm))
osm2=osm.dropna(axis=0,subset=['altname'])

print(len(osm2))
osm2.reset_index()
# for line in osm2.itertuples():
#     print(line.altname)
#     for ortsname in line.altname.split(','):
#         print(line.name,len(osm),ortsname)
#         neu=osm.index.max() +1
#         osm.loc[neu, :] = line
#         osm.set_value(neu, 'itemLabel', ortsname)
#         osm.set_value(neu, 'altname', np.nan)
#         #print(osm.loc[neu,:])
osm3 = osm2.altname.str.split(',', expand=True).stack().str.strip().reset_index(level=1, drop=True)

#osm2.dropna(axis=0, subset=['name'],inplace=True)
osm3= pd.concat([osm2, osm3], axis=1)
osm3.rename( columns={0:'name'},inplace=True)
osm3.columns=[       'namealt',      'altname',     'osm_type',       'osm_id',
              'class',         'type',          'lon',          'lat',
         'place_rank',   'importance',       'street',         'city',
             'county',        'state',      'country', 'country_code',
       'display_name',         'west',        'south',         'east',
              'north',     'wikidata',    'wikipedia', 'housenumbers',
                    'name']

osm_all= pd.concat([osm, osm3], axis=0,   ignore_index=True)
osm.dropna(axis=0, subset=['altname'], inplace=True)
print(osm.columns)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.max_columns', 500)
print(osm_all[osm_all.name=='Berlin'])
print(len(osm),len(osm3),len(osm_all))
print(osm_all.columns)
osm_all['place_rank'].replace({16:'city',18:'village',30:'city'},inplace=True)
osm_all['type'].replace({'administrative':np.nan},inplace=True)
print(osm_all.groupby(['type']).count())
osm_all['type'].fillna(osm_all['place_rank'],inplace=True)
osm_all.drop(['place_rank','city','class','country','county','display_name','east', 'housenumbers', 'importance','namealt', 'north','south',
       'state', 'street', 'west', 'wikidata', 'wikipedia','osm_type'],inplace=True, axis=1)
osm_all.rename(columns = {'osm_id':'ID','altname':'aktueller Name','name':'ldName','country_code':'Staat','lon':'longitude','lat':'latitude','type':'ObjekttypNr'}, inplace = True)
osm_all['Herkunft']='3OSM'
print(osm_all.columns)
print(osm_all[osm_all['aktueller Name']=='Berlin'])
osm_all.to_csv('osm_all.csv', sep='\t')


datei = 'wikiortetypen.p'
print(datei)
wikiorte=pd.read_pickle(datei)
wikiorte.rename( columns={'coord.value':'coord','altname.value':'altname','itemLabel.value':'itemLabel','typ':'ObjekttypNr'},inplace=True)
print(wikiorte.columns)
#wikialt=wikiorte.dropna(axis=0, subset=['altname'])
#print(wikialt)
#wikialt['itemLabel']=wikialt['altname']
#print(len(wikiorte))
#wikiorte = pd.concat([wikialt,wikiorte],ignore_index=True)
print(len(wikiorte))
wikiorte['latitude']=0.1
wikiorte['longitude']=0.1
for zeile in wikiorte.itertuples():
    if 'Point' in zeile.coord:
        coords=zeile.coord.split('(')[1].split(')')[0].split(' ')
        wikiorte.set_value(zeile[0],'longitude', float(coords[0]))
        wikiorte.set_value(zeile[0],'latitude', float(coords[1]))
    else:
        print('Fehler bei:',zeile[0])
        print(zeile)
        wikiorte.set_value(zeile[0],'longitude', np.nan)
        wikiorte.set_value(zeile[0],'latitude', np.nan)
    # if str(zeile.altname) != 'nan' and (len(wikiorte[(wikiorte.itemLabel==zeile.altname)&(wikiorte.coord==zeile.coord)])>0):
    #     neu=len(wikiorte)
    #     wikiorte.loc[neu, :] = wikiorte.loc[zeile[0]].values
    #     wikiorte.set_value(neu, 'itemLabel', zeile.altname)
    #     wikiorte.set_value(neu, 'altname', np.nan)
    #     print(len(wikiorte),'hinzugefügt aus Zeile:',zeile[0])
        #print(wikiorte[wikiorte.index==len(wikiorte)-1])

#geometry = [Point(xy) for xy in zip(wikiorte.longitude, wikiorte.latitude)]

#crs = {'init': 'epsg:4326'}
#geo_wiki = gpd.GeoDataFrame(wikiorte, crs=crs, geometry=geometry)
wikiorte.rename(columns = {'typ':'ObjekttypNr','item.value':'ID','altname':'aktueller Name','itemLabel':'ldName','kurz.value':'Staat','longitude':'longitude','latitude':'latitude'}, inplace = True)
wikiorte['Herkunft']='1Wiki'
wikiorte.drop(['coord', 'coord.datatype', 'coord.type', 'item.type','itemLabel.type',  'itemLabel.xml:lang', 'kurz.type', 'staat.type'],inplace=True, axis=1)
wikiorte[wikiorte['ldName'].str.lower()=='detroit'].to_csv('detroit.csv',sep='\t')
# Index(['level_0', 'altname.type', 'altname.value', 'altname.xml:lang', 'coord',
#        'coord.datatype', 'coord.type', 'index', 'item.type', 'item.value',
#        'itemLabel.type', 'itemLabel', 'itemLabel.xml:lang', 'kurz.type',
#        'kurz.value', 'staat.type', 'staat.value'],
#       dtype='object')

#print(geo_wiki)
#geo_wiki.plot(cmap='OrRd')
#plt.save_fig('test.png')
print('rudeu.csv')
datei = 'rudeu.csv'
russlanddeu = pd.read_csv(datei, sep=';', header=0) #.T.to_dict()     Bisheriger_Wohnort
russlanddeu['currcountry'].replace(countrycode,inplace=True)
russlanddeu.rename(columns = {'ID':'ID','currname':'aktueller Name','Name':'ldName','currcountry':'Staat','Gebiet':'adm1','Area':'adm2','lat':'longitude','lon':'latitude'}, inplace = True)
russlanddeu['Herkunft']='5RuDeu'
# Einlesen von Geonames
datei = 'allCountries.txt'
print(datei)
geonames = pd.read_csv(datei, sep='\t', names=['geonameid','name','asciiname','alternatenames','latitude','longitude','featureclass','featurecode','code','cc2','admin1code','admin2 code','admin3 code','admin4 code','population','elevation','dem','timezone','modification date' ], dtype={'geonameid':str,'alternatenames': str, 'latitude': str, 'cc2':str, 'admin1code':str,'admin2 code':str,'admin3 code':str,'admin4 code':str}) #.T.to_dict()
datei = 'alternateNames.txt'
#Einlesen und verknüpfen der deutschen Namen in das Geonames-df
print(datei)
altnamen = pd.read_csv(datei, sep='\t', names=['alternateNameId','geonameid','isolang','alternativname','isPreferredName','isShortName','isColloquial','isHistoric'], dtype={'geonameid':str,'alternateNameId':str})
#altnamen = altnamen[altnamen.isolanguage=='de']

altnamen = altnamen[altnamen.isolang.isin(['de','en','ru',np.nan,'es','pt','pl','cz','it','fr'])]
print('Geonames Namen einfach: ', len(geonames))
print(altnamen.head())
geonames2 = pd.merge(geonames, altnamen, how='left', on='geonameid')
geonames2.drop(['name'], inplace=True, axis=1)
geonames2.rename(columns={'alternativname':'name'},inplace=True)
geonames = pd.concat([geonames, geonames2], ignore_index=True)
geonames.drop_duplicates(subset=['geonameid', 'name'], keep='first', inplace=True)
print('Geonames mit allen Namen: ', len(geonames))

geonames=geonames[geonames['featureclass']=='P']
print('Geonames nach Filterung auf Orte: ', len(geonames))
geonames.drop(['alternatenames','featureclass','cc2','elevation','timezone','isolang','dem','modification date','alternateNameId','isPreferredName','isShortName','isColloquial','isHistoric'], inplace=True, axis=1)
geonames.drop(['asciiname'], inplace=True, axis=1)
geonames.rename(columns = {'geonameid':'ID','featurecode':'ObjekttypNr','alternatenames2':'aktueller Name','name':'ldName','code':'Staat','admin1code':'adm1','admin2 code':'adm2','admin3 code':'adm3','admin4 code':'adm4','latitude':'latitude','longitude':'longitude'}, inplace = True)
geonames['Herkunft']='4Geonames'
for ort in geonames.itertuples():
    try:
        if float(ort.population) >= 1000000:
            geonames.set_value(ort[0],'ObjekttypNr','Großstadt')
            #print('----------------------',ort[0])
        elif float(ort.population) >= 100000:
            #print(ort[0])
            geonames.set_value(ort[0], 'ObjekttypNr', 'Große Stadt')
        elif float(ort.population) >= 50000:
            #print(ort[0])
            geonames.set_value(ort[0], 'ObjekttypNr', 'Mittlere Stadt')
    except:
        pass
geonames.to_csv('geonamesfinal.csv', sep='\t')
gov= pd.read_csv('geonamesfinal.csv', index_col=0, sep='\t', header=0) #.T.to_dict()

if govneu==False:
    gov=pd.read_pickle('gov.p')
    print('Govdb-Länge:',len(gov))
    print(gov.groupby(['Herkunft']).count())
    govalt=pd.read_pickle('gov-altname.p')
    govalt['Herkunft'] = '2GOV'
    gov=pd.concat([gov,govalt],ignore_index=True)
    gov.to_csv('gov.csv',sep='\t')

else:
    #gov = pd.read_pickle('gov.p')
    datei = 'gov-data-names_20171230_205716.txt'
    print(datei)
    gov = pd.read_csv(datei ,sep='\t', names=["ID","Objekttyp","ObjekttypNr","aktueller Name","ldName","Staat","adm1","adm2","adm3","adm4",'Postleitzahl',"latitude","longitude" ]) #.T.to_dict()
    gov.drop(['Postleitzahl'], inplace=True, axis=1)
    gov['ldName'] = gov['ldName'].fillna(gov['aktueller Name'])
    gov['Staat'].replace(countrycode,inplace=True)
    gov['Herkunft']='2GOV'
    datei = 'Ortstypen.csv'
    print(datei)
    ortscodedb = pd.read_csv(datei, index_col=None, sep='\t', header=0, dtype={'id':str})
    #print(ortscodedb)
    ortscodedb2 = ortscodedb.dropna(axis=0, subset=['Kodierung'])
    ortscodedb2 = ortscodedb2[ortscodedb2['Kodierung']!='Land']
    ortscodedb2.to_csv('ortscodedb2.csv',sep='\t')
    nonortedf = ortscodedb[~ortscodedb['Kodierung'].isin(ortscodedb2['Kodierung'])]
    print(len(gov))
    ortscodedb['Kodierung']=ortscodedb['Kodierung'].astype(str)
    gov['ObjekttypNr']=gov['ObjekttypNr'].astype(str)
    print(nonortedf)
    gov =gov[~gov['ObjekttypNr'].isin(nonortedf['id_ortart'])]
    print('gov vor hinzufügen von Alternativen Namen:',len(gov))
    WSDL_URL = 'http://gov.genealogy.net/services/SimpleService?wsdl'
    client = Client(WSDL_URL)
    gov.reset_index(inplace=True, drop=True)
    x=0
    y=len(gov)
    gov['namegesetzt']='nein'
    def exgetcoorts(row):
       try:
          erg=getcoords(row)
       except:
          print('Fehler beim Empfangen von',row,'. Neuer Versuch in 10 Sekunden.' )
          time.sleep(5)
          erg=getcoords(row)
       return erg
    def getcoords(row):
                erg = []
                print('setzt Abfrage ab für:', row[1])
                result = client.service.getObject(row[1])
                print('Ergebnis empfangen')
                longitude=0.1
                latitude=0.1
                #print(result)
                if 'position' in Client.dict(result):
                    for eintrag in Client.dict(result)['position']:
                        print(eintrag)
                        if (eintrag[0] == '_lon') and (longitude==0.1):
                            longitude=eintrag[1]
                        if (eintrag[0] == '_lat') and  (latitude==0.1):
                            latitude = eintrag[1]
                    erg.append([row[0], longitude,latitude])
                    print(erg)

                print('---------------------------bearbeitet:', row[0], 'von:', y)
                return erg

    def getaltname(row):
        erg = []
        try:
                print('setzt Abfrage ab für:', row[1])
                result = client.service.getObject(row[1])
                print('Ergebnis empfangen')
                if 'name' in Client.dict(result):
                    for eintrag in Client.dict(result)['name']:
                        if Client.dict(eintrag)['_value'] != gov.loc[row[0], 'aktueller Name']:
                            print(Client.dict(eintrag)['_value'], ' != ', gov.loc[row[0], 'aktueller Name'])
                            erg.append([row[0], Client.dict(eintrag)['_value']])
                            print(erg)

                print('---------------------------bearbeitet:', row[0], 'von:', y)
        except  Exception as e:
            print('hier eine Fehlermeldung',e, row)
        return erg

    def saveeintrag(eintrag):
        print('speichere:', eintrag)
        dummy = gov.loc[eintrag[0]]
        print(dummy.to_frame().T)
        dummy['ldName'] = eintrag[1]
        print('Typ:',type(dummy.to_frame()).T)
        return dummy.to_frame().T
    def saveeintragcoords(eintrag):
        print('speichere:', eintrag)
        dummy = gov.loc[eintrag[0]]
        print(dummy.to_frame().T)
        dummy['longitude'] = eintrag[1]
        dummy['latitude'] = eintrag[2]
        print('Typ:',type(dummy.to_frame()).T)
        return dummy.to_frame().T
    num_cores = 24
    govcoords=gov[(pd.isna(gov['longitude']))|(pd.isna(gov['latitude']))]
    govidcoords=govcoords['ID']
    ergsfind = Parallel(n_jobs=num_cores)(delayed(exgetcoorts)(row) for row in govidcoords.iteritems())
    flat_list = [item for sublist in ergsfind for item in sublist]
    ordner = 'altname/'
    #ergsfind = Parallel(n_jobs=num_cores)(delayed(saveeintrag)(eintrag) for eintrag in flat_list)
    index = np.arange(0, 0)
    ergebnisse = pd.DataFrame(index=index,
                              columns=[], )
    neugovs = Parallel(n_jobs=num_cores)(delayed(saveeintragcoords)(eintrag) for eintrag in flat_list)
    print('Füge ergebnisse zusammen')
    ergebnisse = pd.concat(neugovs, ignore_index=True)
    gov['ldName'] = gov['ldName'].fillna(gov['aktueller Name'])
    gov['Staat'].replace(countrycode,inplace=True)
    gov['Herkunft']='2GOV'
    datei = 'Ortstypen.csv'
    print(datei)

    ergebnisse.to_csv('ergenisse_coords.csv', sep='\t')
    print('Füge ergebnisse zu GOV')
    gov = pd.concat([ergebnisse, gov], ignore_index=True)
    gov.dropna(axis=0, subset=["latitude", "longitude", "aktueller Name"], inplace=True)
    govid=gov['ID']
    ergsfind = Parallel(n_jobs=num_cores)(delayed(getaltname)(row) for row in govid.iteritems())
    flat_list = [item for sublist in ergsfind for item in sublist]
    ordner = 'altname/'
    #ergsfind = Parallel(n_jobs=num_cores)(delayed(saveeintrag)(eintrag) for eintrag in flat_list)
    index = np.arange(0, 0)
    ergebnisse = pd.DataFrame(index=index,
                              columns=[], )
    neugovs = Parallel(n_jobs=num_cores)(delayed(saveeintrag)(eintrag) for eintrag in flat_list)
    print('Füge ergebnisse zusammen')
    ergebnisse = pd.concat(neugovs, ignore_index=True)
    ergebnisse.to_csv('ergenisse_altname.csv', sep='\t')
    print('Füge ergebnisse zu GOV')
    gov = pd.concat([ergebnisse, gov], ignore_index=True)
    print('Speicher GOV')
    gov.to_pickle('gov.p')
govalt=pd.read_pickle('gov-altname.p')
govalt['Herkunft'] = '2GOV'
gov=pd.concat([gov,govalt],ignore_index=True)
gov.to_csv('gov.csv',sep='\t')
print('Gov vor Entfernung von Nonorte',len(gov))
gov['ObjekttypNr']=gov['ObjekttypNr'].astype(str)
gov =gov[~gov['ObjekttypNr'].isin(nonortedf['id_ortart'])]
print('Gov nach Entfernung von Nonorte',len(gov))

placenamedb = pd.concat([geonames, gov, russlanddeu,wikiorte,osm_all], ignore_index=True)
placenamedb.drop([ 'adm1', 'adm2', 'adm3', 'adm4', 'art.type', 'artlabel.value',
        'namegesetzt', 'population.datatype', 'population.type', 'staat.value'],inplace=True, axis=1)
print('alle collumns:',placenamedb.columns)
datei = 'Ortstypen.csv'
ortscodedb = pd.read_csv(datei, index_col=None, sep='\t', header=0, dtype={'id_ortart':str})
print(ortscodedb.columns)
ortscodedb = ortscodedb.dropna(axis=0, subset=['Kodierung'])
placenamedb = pd.merge(placenamedb, ortscodedb, how='left',left_on='ObjekttypNr',right_on='id_ortart')
placenamedb.drop(['code_index','ortart','id_ortart','zusatz','Unnamed: 5'], axis=1, inplace=True)
placenamedb['Kodierung']= placenamedb['Kodierung'].fillna('nan')
placenamedb.Kodierung = placenamedb.Kodierung.astype('category')
placenamedb.Herkunft = placenamedb.Herkunft.astype('category')
placenamedb.Objekttyp = placenamedb.Objekttyp.astype('category')
placenamedb.ObjekttypNr = placenamedb.ObjekttypNr.astype('category')
placenamedb.Staat = placenamedb.Staat.str.upper()
placenamedb.Staat = placenamedb.Staat.astype('category')
placenamedb.art = placenamedb.art.astype('category')
placenamedb.ObjekttypNr = placenamedb.ObjekttypNr.astype('category')
#placenamedb = pd.concat([geonames, gov, russlanddeu,osm_all], ignore_index=True)
del geonames
del gov
del osm_all
del osm
tr={u'\u0410': 'A', u'\u0430': 'a',
u'\u0411': 'B', u'\u0431': 'b',
u'\u0412': 'V', u'\u0432': 'v',
u'\u0413': 'G', u'\u0433': 'g',
u'\u0414': 'D', u'\u0434': 'd',
u'\u0415': 'E', u'\u0435': 'e',
u'\u0416': 'Zh', u'\u0436': 'zh',
u'\u0417': 'Z', u'\u0437': 'z',
u'\u0418': 'I', u'\u0438': 'i',
u'\u0419': 'Y', u'\u0439': 'y',
u'\u041a': 'K', u'\u043a': 'k',
u'\u041b': 'L', u'\u043b': 'l',
u'\u041c': 'M', u'\u043c': 'm',
u'\u041d': 'N', u'\u043d': 'n',
u'\u041e': 'O', u'\u043e': 'o',
u'\u041f': 'P', u'\u043f': 'p',
u'\u0420': 'R', u'\u0440': 'r',
u'\u0421': 'S', u'\u0441': 's',
u'\u0422': 'T', u'\u0442': 't',
u'\u0423': 'U', u'\u0443': 'u',
u'\u0424': 'F', u'\u0444': 'f',
u'\u0425': 'Kh', u'\u0445': 'kh',
u'\u0426': 'Ts', u'\u0446': 'ts',
u'\u0427': 'Ch', u'\u0447': 'ch',
u'\u0428': 'Sh', u'\u0448': 'sh',
u'\u0429': 'Shch', u'\u0449': 'shch',
u'\u042a': '"', u'\u044a': '"',
u'\u042b': 'Y', u'\u044b': 'y',
u'\u042c': "'", u'\u044c': "'",
u'\u042d': 'E', u'\u044d': 'e',
u'\u042e': 'Yu', u'\u044e': 'yu',
u'\u042f': 'Ya', u'\u044f': 'ya',
'ё':'e','Ё':'E'}
def transru(word, translit_table):
    converted_word = ''
    for char in word:
        transchar = ''
        if char in translit_table:
            transchar = translit_table[char]
        else:
            transchar = char
        converted_word += transchar
    return converted_word
placenamedbnoname= placenamedb.dropna(axis=0, subset=['ldName'])
print(len(placenamedbnoname),len(placenamedb))
placenamedb.ldName=placenamedb.ldName.str.lower()
aachendf=placenamedb[placenamedb.ldName=='aachen']
print(placenamedb.groupby(['Herkunft']).count())
print('Länge placenamedb vor Duplikatfilterung:',len(placenamedb))
placenamedb.dropna(axis=0, subset=['longitude'],inplace=True)
placenamedb.dropna(axis=0, subset=['latitude'],inplace=True)
placenamedb.latitude = placenamedb.latitude.apply(lambda x: pd.to_numeric(x, errors='ignore'))
placenamedb.longitude = placenamedb.longitude.apply(lambda x: pd.to_numeric(x, errors='ignore'))
placenamedb.dropna(axis=0, subset=['longitude'],inplace=True)
placenamedb.dropna(axis=0, subset=['latitude'],inplace=True)
print('Länge placenamedb vor Bearbeitung von Koordinaten:',len(placenamedb))
placenamedb['lakurz'] = placenamedb['latitude']
placenamedb['lokurz'] = placenamedb['longitude']
testdf = placenamedb.round({'lakurz': 1, 'lokurz': 1})
placenamedb['ObjekttypNr']=placenamedb['ObjekttypNr'].astype(str)
placenamedb.sort_values(['ObjekttypNr'],ascending=False,inplace=True)
placenamedb.sort_values(['Herkunft'],ascending=True,inplace=True)
print(ortscodedb.columns)
ortscodedb = ortscodedb.dropna(axis=0, subset=['Kodierung'])
#placenamedb = pd.merge(placenamedb, ortscodedb, how='left',left_on='ObjekttypNr',right_on='id_ortart')

placenamedb.drop_duplicates(subset=['lakurz', 'lokurz', 'ldName','Kodierung'], keep='first', inplace=True)
print('Länge placenamedb nach Duplikatfilterung:',len(placenamedb))
aachendf=placenamedb[placenamedb.ldName=='aachen']
print(aachendf.groupby(['Herkunft']).count())
#print(len(geonames)+len(russlanddeu)+len(gov))
placenamedb.dropna(axis=0, subset=['ldName'], inplace=True)
print(len(placenamedb))
#placenamedb = pd.read_csv('placenamedb.csv', sep='\t',header=0,index_col=0)
placenamedb['neuername']=''
x=0
duplicates=[]
dropped =[]
processed=[]
placenamedb=reduce_mem_usage(placenamedb)
print('Erstelle GeoDF')
placenamedb.dropna(axis=0, subset=['longitude'], inplace=True)
placenamedb.dropna(axis=0, subset=['latitude'], inplace=True)
geometry = [Point(xy) for xy in zip(placenamedb.longitude, placenamedb.latitude)]
crs = {'init': 'epsg:4326'}
placenamedb = gpd.GeoDataFrame(placenamedb, crs=crs, geometry=geometry)
print('GeoDF erstellt')
for line in placenamedb.itertuples():
    x+=1
    #print(line)
    #print(str(x)+'    '+str(line[12])+'    '+str(line))
    #print(line)
    dummy = line.ldName
    dummy = dummy.replace('ß','ss')
    dummy = transru(dummy,tr)
    dummy = dummy.lower()
    #print(dummy)
    # ortsteile = re.split(r'(\s|,|\.|/|-|\)|\(|\*|\[|\])', zeile[2])
    ortsteile = functools.reduce(lambda acc, elem: acc[:-1] + [acc[-1] + elem] if elem == "." else acc + [elem],
                                 re.split(r'(\s|,|\.|/|-|\)|\(|\*|\[|\])', dummy), [])
    if len(ortsteile) > 1:
        for ortsteil in ortsteile:
            gef=False
            for stop in stopw:
                if stop==ortsteil:
                    gef=True
            if not gef:
                placenamedb.set_value(line[0], 'neuername', placenamedb.get_value(line[0], 'neuername') + ' ' + ortsteil)
                placenamedb.set_value(line[0], 'neuername', placenamedb.get_value(line[0], 'neuername').strip())
    else:
        placenamedb.set_value(line[0], 'neuername', placenamedb.get_value(line[0], 'neuername') + ' ' + dummy)
        placenamedb.set_value(line[0], 'neuername', placenamedb.get_value(line[0], 'neuername').strip())
placenamedb['neuername'] = placenamedb['neuername'].fillna(placenamedb['ldName'])
placenamedb['neuername2']=''
placenamedb.neuername2 = placenamedb['neuername'].map(gensim.utils.deaccent)
placenamedb.loc[:, ('lettermass')]=placenamedb.neuername
placenamedb.loc[:, ('lettermass')]=placenamedb['lettermass'].map(lettermass)
placenamedb.loc[:, ('kphdist')]=placenamedb.neuername
placenamedb.loc[:, ('kphdist')]=placenamedb['kphdist'].map(kphdist)
placenamedb.loc[:, ('minlen')]=placenamedb['neuername'].map(minlen)
placenamedb.loc[:, ('doublemetaphone')]=placenamedb['neuername'].map(doublemetaphoncoding)
placenamedb=reduce_mem_usage(placenamedb)

print(placenamedb.columns)
placenamedb.drop(['Objekttyp', 'ObjekttypNr', 'aktueller Name',
       'art', 'latitude', 'ldName', 'longitude', 'population',
       'lakurz', 'lokurz'], axis=1, inplace=True)
#placenamedb.drop(['aktueller Name','population','lakurz','lokurz','ldName'], axis=1, inplace=True)
placenamedb.to_csv('placenamedb.csv', sep='\t')
placenamedb.to_pickle('placenamedb.p')
#placenamedb.to_file('placenamedb.bak')

#placenamedb[placenamedb['neuername'].str.lower()=='neuername'].to_csv('detroit.csv',sep='\t')
#placenamedb[placenamedb['art'].str.contains('Q133442')].groupby('ObjekttypNr').count().to_csv('placenamedb1.csv',sep='\t')
subprocess.call("python3 make-region.py 1", shell=True)
