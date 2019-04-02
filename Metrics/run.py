#from metrics import *
#from graphs import *
#from pymongo import MongoClient
from metricspsql import *
import json
import psycopg2

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


def remap_keys(mapping):
    return [{'key': k, 'value': v} for k, v in mapping.iteritems()]

connection, cursor = connect_db()

ln = LanguageNumbers(connection, cursor)
se = SequentialEditing(connection, cursor)
lo = LanguageOverlap(connection, cursor)
et = EditTimeline(connection, cursor)
mvm = MonoVsMultilingual(connection, cursor)


print '--------------------for registered2 users--------------------'

# lnresult = ln.run('registered2')
# with open('registered2-ln-result.json', 'w') as outfile:
#     json.dump(lnresult, outfile)

seresult = se.run('registered2', 500)
with open('registered2-se-result.json', 'w') as outfile:
    outfile.write(json.dumps(seresult, indent=4, sort_keys=True, default=str))

# loresult = lo.run('registered2', lnresult['language_ranking_by_edits'])
# loresult = [remap_keys(loresult[0]), loresult[1], loresult[2]]
# with open('registered2-lo-result.json', 'w') as outfile:
#     outfile.write(json.dumps(loresult, indent=4, sort_keys=True, default=str))
#
# etresult = et.run('registered2')
# with open('registered2-et-result.json', 'w') as outfile:
#     outfile.write(json.dumps(etresult, indent=4, sort_keys=True, default=str))

mvmresult = mvm.get_edit_data('registered2')
with open('registered2-mvm-result.json', 'w') as outfile:
    outfile.write(json.dumps(mvmresult))


print '--------------------for anonymous2--------------------'

# lnresult = ln.run('anonymous2')
# with open('anonymous2-ln-result.json', 'w') as outfile:
#     json.dump(lnresult, outfile)

seresult = se.run('anonymous2', 100)
with open('anonymous2-se-result.json', 'w') as outfile:
    outfile.write(json.dumps(seresult, indent=4, sort_keys=True, default=str))
#
# loresult = lo.run('anonymous2', lnresult['language_ranking_by_edits'])
# loresult = [remap_keys(loresult[0]), loresult[1], loresult[2]]
# with open('anonymous2-lo-result.json', 'w') as outfile:
#     outfile.write(json.dumps(loresult, indent=4, sort_keys=True, default=str))
#
# etresult = et.run('anonymous2')
# with open('anonymous2-et-result.json', 'w') as outfile:
#     outfile.write(json.dumps(etresult, indent=4, sort_keys=True, default=str))

mvmresult = mvm.get_edit_data('anonymous2')
with open('anonymous2-mvm-result.json', 'w') as outfile:
    outfile.write(json.dumps(mvmresult))

print '--------------------for bots2--------------------'

# lnresult = ln.run('bots2')
# with open('bots2-ln-result.json', 'w') as outfile:
#     json.dump(lnresult, outfile)

seresult = se.run('bots2', 500)
with open('bots2-se-result.json', 'w') as outfile:
    outfile.write(json.dumps(seresult, indent=4, sort_keys=True, default=str))

# loresult = lo.run('bots2', lnresult['language_ranking_by_edits'])
# loresult = [remap_keys(loresult[0]), loresult[1], loresult[2]]
# with open('bots2-lo-result.json', 'w') as outfile:
#     outfile.write(json.dumps(loresult, indent=4, sort_keys=True, default=str))
#
# etresult = et.run('bots2')
# with open('bots2-et-result.json', 'w') as outfile:
#     outfile.write(json.dumps(etresult, indent=4, sort_keys=True, default=str))

mvmresult = mvm.get_edit_data('bots2')
with open('bots2-mvm-result.json', 'w') as outfile:
    outfile.write(json.dumps(mvmresult))


close_db(cursor, connection)
