#from metrics import *
#from graphs import *
#from pymongo import MongoClient
from metricspsql import *
import json

#client = MongoClient()
#db = client.wikibabeldb


def connect_db():
    try:
        connection = psycopg2.connect(user="frimelle",
                                      password="password",
                                      host="127.0.0.1",
                                      port="5432",
                                      database="wikibabeldb")
        cursor = connection.cursor()
        return cursor, connection
    except (Exception, psycopg2.Error) as error:
        print ("Error while connecting to PostgreSQL", error)


def close_db(cursor, connection):
    if (connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")

connection, cursor = connect_db()

ln = LanguageNumbers(connection, cursor)
se = SequentialEditing(connection, cursor, 1000)


print 'for registered users'

lnresult = ln.run('registered')
with open('registered-ln-result.json', 'w') as outfile:
    json.dump(lnresult, outfile)

#lng = LanguageNumbersGraphs(languagenumberresult)
#lng.ranking_graph()


seresult = se.run('registered')
with open('registered-se-result.json', 'w') as outfile:
    outfile.write(json.dumps(seresult, indent=4, sort_keys=True, default=str))

print 'for anonymous'

lnresult = ln.run('anonymous')
with open('anonymous-ln-result.json', 'w') as outfile:
    json.dump(lnresult, outfile)

seresult = se.run('anonymous')
with open('anonymous-se-result.json', 'w') as outfile:
    outfile.write(json.dumps(seresult, indent=4, sort_keys=True, default=str))


print 'for bots'

lnresult = ln.run('bots')
with open('bots-ln-result.json', 'w') as outfile:
    json.dump(lnresult, outfile)

seresult = se.run('bots')
with open('bots-se-result.json', 'w') as outfile:
    outfile.write(json.dumps(seresult, indent=4, sort_keys=True, default=str))

close_db(cursor, connection)