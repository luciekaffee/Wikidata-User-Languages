from metrics import *
#from graphs import *
from pymongo import MongoClient
import json

client = MongoClient()
db = client.wikibabeldb

ln = LanguageNumbers(db)
lnresult = ln.run('revision')
with open('ln-result.json', 'w') as outfile:
    json.dump(lnresult, outfile)

#lng = LanguageNumbersGraphs(languagenumberresult)
#lng.ranking_graph()

se = SequentialEditing(db)
seresult = se.run('revision')
with open('se-result.json', 'w') as outfile:
    json.dump(seresult, outfile)
