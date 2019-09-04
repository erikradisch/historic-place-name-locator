import pandas as pd

wiki_orte = pd.read_pickle('wiki_orte.p')
wikitype = pd.read_csv('wiki_typen_neu.csv', sep='\t')
wiki_orte_tpyen = pd.merge(wiki_orte, wikitype, how='left', on='art.value')
wiki_orte_tpyen.rename(columns={'population.value': 'population'}, inplace=True)
for ort in wiki_orte_tpyen.itertuples():
    try:
        if float(ort.population) > 1000000 and ort.typ!='Großstadt':
            print(ort)
            print(ort[0])
            wiki_orte_tpyen.set_value(ort[0],'typ','Großstadt')
        elif float(population) > 500000 and ort.typ != 'Großstadt':
            print(ort)
            print(ort[0])
            wiki_orte_tpyen.set_value(ort[0], 'typ', 'Große Stadt')

    except:
        pass
print(len(wiki_orte_tpyen))
print(len(wiki_orte))
print(wiki_orte_tpyen.groupby('typ').count())
wiki_orte_tpyen[wiki_orte_tpyen['itemLabel.value'].str.contains('Chicago')].to_csv('großstadt.csv', sep='\t')
wiki_orte_tpyen.to_pickle('wikiortetypen.p')
subprocess.call("python3 make-ortsdbn.py 1", shell=True)