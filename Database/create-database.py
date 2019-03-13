import gzip
import json
from pymongo import MongoClient

client = MongoClient()
db = client.wikibabeldb

bots = []

# List based on https://www.wikidata.org/wiki/Wikidata:List_of_bots
with open('bots/bots-list.csv') as data_file:
    for line in data_file:
        bots.append(line.strip())


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

def create_db_data_entry(revision):
    if 'username' not in revision and 'ip' in revision:
        print 'anonymous'
        db.anonymous.insert_one(revision)
    elif revision['username'] in bots or revision['username'].lower().startswith('bot') or revision['username'].lower().endswith('bot'):
        print('bots')
        db.bots.insert_one(revision)
    else:
        print('registered')
        db.registered.insert_one(revision)



item_id = ''
with gzip.open('wikidatawiki-20190302-stub-meta-history.xml.gz', 'rb') as file:
    revision = {}
    for l in file:
        if '<title>Q' in l:
            item_id = l[l.find(">")+1:l.find("</")].strip()
        if '</revision>' in l:
            revision = create_revision(revision)
            if revision:
                print revision
                create_db_data_entry(revision)
            revision = {}
        else:
            revision['item_id'] = item_id
            key = l[l.find("<")+1:l.find(">")].replace('/', '').replace('.', '_').strip()
            value = l[l.find(">")+1:l.find("</")]

            if value:
                revision[key] = value