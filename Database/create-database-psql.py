import gzip
import json
import psycopg2
from dateutil.parser import parse

#psql frimelle -h 127.0.0.1 -d wikibabeldb

#SELECT COUNT(*) FROM (SELECT username, COUNT(DISTINCT language) as counter FROM bots2 WHERE COUNT(DISTINCT language^C> 5 GROUP BY username) AS countall;


bots2 = []

# List based on https://www.wikidata.org/wiki/Wikidata:List_of_bots2
with open('bots/bots-list.csv') as data_file:
    for line in data_file:
        bots2.append(line.strip())


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

errorlog = open('errorlog.csv', 'a+')

def create_db_data_entry(cur, conn, revision):
    query = ''
    if 'sha1' not in revision:
        revision['sha1'] = 'x'
    try:
        if 'username' not in revision and 'ip' in revision:
            print 'anonymous2'
            query = """INSERT INTO anonymous2(username, comment, sha1, language, format, timestamp, parentid, item_id, model, id)
                 VALUES('%s', '%s', '%s', '%s', '%s', '%s', %s, '%s', '%s', %s)""" % (revision['ip'], revision['comment'].replace("'", '"'),
                                        revision['sha1'], revision['language'], revision['format'], parse(revision['timestamp']),
                                        revision['parentid'], revision['item_id'], revision['model'], revision['id'])
            #if id in revision:
            #    query += """WHERE NOT EXISTS ( SELECT id FROM anonymous2 WHERE id = %s);""" % (revision[id])
        elif 'username' not in revision and 'ip' not in revision or 'language' not in revision:
            return
        elif revision['username'] in bots2 or revision['username'].lower().startswith('bot') or revision['username'].lower().endswith('bot'):
            print 'bots2'
            query = """INSERT INTO bots2(username, comment, sha1, language, format, timestamp, parentid, item_id, model, id)
                VALUES('%s', '%s', '%s', '%s', '%s', '%s', %s, '%s', '%s', %s)""" % (revision['username'].replace("'", '"'), revision['comment'].replace("'", '"'),
                                        revision['sha1'], revision['language'], revision['format'], parse(revision['timestamp']),
                                        revision['parentid'], revision['item_id'], revision['model'], revision['id'])
            #if id in revision:
            #    query += """WHERE NOT EXISTS ( SELECT id FROM bots2 WHERE id = %s);""" % (revision[id])
        else:
            print 'registered2'
            query = """INSERT INTO registered2(username, comment, sha1, language, format, timestamp, parentid, item_id, model, id)
                VALUES('%s', '%s', '%s', '%s', '%s', '%s', %s, '%s', '%s', %s)""" % (revision['username'].replace("'", '"'), revision['comment'].replace("'", '"'),
                                        revision['sha1'], revision['language'], revision['format'], parse(revision['timestamp']),
                                        revision['parentid'], revision['item_id'], revision['model'], revision['id'])
            #if id in revision:
            #    query += """WHERE NOT EXISTS ( SELECT id FROM registered2 WHERE id = %s);""" % (revision[id])
    except:
        if 'itemid' in revision and 'id' in revision:
            errorlog.write(revision['itemid'], revision['id'])
            return
    if query:
        try:
            cur.execute(query)
            conn.commit()
        except:
            if 'itemid' in revision and 'id' in revision:
                errorlog.write(revision['itemid'], revision['id'])


def get_lang(comment):
    if '|' in comment:
        value = comment[comment.find("/*")+1:comment.find("*/")].split('|')
        if len(value) >= 2:
            return value[1]
        else:
            return ''


def create_revision(revision):
    if 'comment' in revision:
        if 'wbsetlabel-set' in revision['comment'] or 'wbsetlabel-add' in revision['comment']:
            lang = get_lang(revision['comment'])
            if lang:
                revision['language'] = lang
            return revision


cursor, connection = connect_db()
item_id = ''
keys = ['username', 'ip', 'comment', 'sha1', 'language', 'format', 'parentid', 'item_id', 'model', 'id']
with gzip.open('wikidatawiki-20190302-stub-meta-history.xml.gz', 'rb') as file:
    revision = {key: None for key in keys}
    for l in file:
        if '<title>Q' in l:
            item_id = l[l.find(">")+1:l.find("</")].strip()
        if '</revision>' in l:
            revision = create_revision(revision)
            if revision:
                print revision
                create_db_data_entry(cursor, connection, revision)
            revision = {}
        else:
            revision['item_id'] = item_id
            key = l[l.find("<")+1:l.find(">")].replace('/', '').replace('.', '_').strip()
            value = l[l.find(">")+1:l.find("</")]

            if value:
                revision[key] = value

close_db(cursor, connection)
