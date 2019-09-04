from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
#results_df=pd.read_pickle('wiki_orte.p')
results_df = pd.DataFrame()
results_df.to_pickle('wiki_orte.p')
import time
queries=[]
queries.append("query1")
queries.append("query2")
language=['de','en','ru','cz','pl','fr','es','pt']
#off=len(results_df)
for query in queries:
    for lang in language:
        lim = 1000000
        off = 0
        while True:
#UNION
#{?item
#skos:altLabel ?itemLabel
#filter(lang(?itemLabel) = '""""" + str(lang) + """').}

#            try:                                 LIMIT """ + str(lim) + """ OFFSET """ + str(off) + """
                    print('Sprache:',lang)
                    print('Beginne Abfrage')
                    sparql = SPARQLWrapper("http://localhost:9999/bigdata/sparql")
                    querydic = {}
                    querydic['query1']="""PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        SELECT ?item ?itemLabel ?art ?coord ?staat ?kurz ?population
                                              WHERE
                                              {
                                                  ?item wdt:P31/wdt:P279* wd:Q486972.
                                                  ?item wdt:P31 ?art.
                                                  ?item rdfs:label ?itemLabel filter (lang(?itemLabel) = '""""" + str(lang) + """').
                                                  ?item  wdt:P625 ?coord.
                                                  OPTIONAL{?item wdt:P1082 ?population .}
                                                  OPTIONAL{?item wdt:P17 ?staat.
                                                        ?staat wdt:P297 ?kurz.}
                                              }
                                                          LIMIT """ + str(lim) + """ OFFSET """ + str(off) + """
                
                                                          """
                    querydic['query2'] = """PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        SELECT ?item ?itemLabel ?art ?coord ?staat ?kurz ?population
                                              WHERE
                                              {
                                                  ?item wdt:P31/wdt:P279* wd:Q486972.
                                                  ?item wdt:P31 ?art.
                                                  ?item skos:altLabel ?itemLabel filter (lang(?itemLabel) = '""""" + str(lang) + """').
                                                  ?item  wdt:P625 ?coord.
                                                  OPTIONAL{?item wdt:P1082 ?population .}
                                                  OPTIONAL{?item wdt:P17 ?staat.
                                                        ?staat wdt:P297 ?kurz.}
                                              }
                                                          LIMIT """ + str(lim) + """ OFFSET """ + str(off) + """                                                        
                    
                                                          """
                    sparql.setQuery(querydic[query])
                    print(querydic[query])
                    sparql.setReturnFormat(JSON)
                    sparql.timeout= 1000
                    results = sparql.query().convert()
                    print('Abfragenergebnis erhalten, beginne Formatierung.')
                    wikiorte = pd.io.json.json_normalize(results['results']['bindings'])
                    print('Formatierung abgeshclossen,lade bisherige ergebnisse.')
                    wikiorte.rename(columns={'coord.value': 'coord'}, inplace=True)
                    print('Länge der Resultate_DF:',len(wikiorte))

    #                wikiortefilter= wikiorte.groupby(['instanz.value','instanzLabel.value']).count()
    #                wikiortefilter.to_csv('wikiort.csv',sep='\t')
                    #print(wikiorte.columns,results_df.columns)
                    results_df=pd.read_pickle('wiki_orte.p')
                    print('länge der Wikidb vor concat:',len(results_df))
                    results_df= pd.concat([results_df,wikiorte],ignore_index=True)
    #                results_df['instanzLabel.xml:lang']=results_df['instanzLabel.xml:lang'].str.replace('en','1')
    #                results_df['itemLabel.xml:lang']=results_df['instanzLabel.xml:lang'].str.replace('en','1')
    #                results_df.sort_values(['itemLabel.xml:lang','item.value'],ascending=True,inplace=True)
                    print(results_df.head())
                    results_df.drop_duplicates(subset=['item.value','itemLabel.value','coord','kurz.value','art.value'],keep='first', inplace=True)

                    results_df.reset_index(inplace=True, drop=True)
                    #print(results_df)
                    results_df.to_pickle('wiki_orte.p')
                    results_df.to_csv('wiki_orte.csv',sep='\t')

                    off=off+lim
                    print('wir sind jetzt bei:',off)
                    print('länge der Wikidb nach concat:',len(results_df))
                    print('länge der Resultate resultdb:', len(wikiorte))

                    if len(wikiorte)==0:
                        print('Break bei offset:',off)
                        break
#            except Exception as ex:
#                    print('Fehler: '+ex)
#                    time.sleep(10)
print('Beginne Bearbeitung der Koorinaten')
results_df = results_df=pd.read_pickle('wiki_orte.p')
wikiorte['latitude'] = 0.1
wikiorte['longitude'] = 0.1
print(results_df[results_df['itemLabel.value'] == 'Царицын'])
for zeile in wikiorte.itertuples():
        # print(zeile)
        coords = zeile.coord.split('(')[1].split(')')[0].split(' ')
        wikiorte.set_value(zeile[0], 'longitude', float(coords[0]))
        wikiorte.set_value(zeile[0], 'latitude', float(coords[1]))
results_df.to_pickle('wiki_orte.p')
results_df.to_csv('wiki_orte.csv',sep='\t')
                #break

#for result in results:
#    print(result)


# SERVICE wikibase:label {
#     bd:serviceParam wikibase:language "en" .
# }
# import requests
# #import helpers
# import json
# import pandas as pd
# import matplotlib as mpl
# import matplotlib.pyplot as plt
# query = '''PREFIX wikibase: <http://wikiba.se/ontology#>
# PREFIX wd: <http://www.wikidata.org/entity/>
# PREFIX wdt: <http://www.wikidata.org/prop/direct/>
# PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
#

#
# #mpl.style.use('ramiro')
# chartinfo = 'Author: Ramiro Gómez - ramiro.org • Data: Wikidata - wikidata.org'
# infosize = 12
# url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql'
# data = requests.get(url, params={'query': query, 'format': 'json'},allow_redirects=True,timeout=10000)
# #print(data.text)
# #data.replace(''','"')
# jdata=json.loads(data.text, strict=False)
# presidents = []
# for item in jdata['results']['bindings']:
#     print(item)
#     presidents.append({
#         'item': item['item']['value'],
#         'itemLabel': item['itemLabel']['value'],
#         'coord': item['coord']['value'],
#     })
# df = pd.DataFrame(presidents)
# print(df)
# df.head()
# df.to_pickle('test_sparcle.p')

