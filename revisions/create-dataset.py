import gzip
import json
from pymongo import MongoClient

client = MongoClient()
db = client.wikibabeldb

users = []

with open('data/userdata.json') as data_file:    
    users = json.load(data_file).keys()


def get_lang(comment):
    if '|' in comment:
        value = comment[comment.find("/*")+1:comment.find("*/")].split('|')
        if len(value) >= 2:
            return value[1]
        else:
            return ''

def create_revision(revision, user):
    if 'comment' in revision:
        if 'wbsetlabel-set' in revision['comment'] or 'wbsetlabel-add' in revision['comment']:
            lang = get_lang(revision['comment'])
            if lang:
                revision['language'] = lang
            return revision

            #if not 'username' in revision or 'timestamp' in revision or revision['timestamp'].split('-')[0] < 2014:
            #   return None


item_id = ''
with gzip.open('wikidatawiki-20170701-stub-meta-history.xml.gz', 'rb') as file:
    revision = {}
    for l in file:
        if '<title>Q' in l:
            item_id = l[l.find(">")+1:l.find("</")].strip()
        if '</revision>' in l:
            revision = create_revision(revision, users)
            if revision:
                print revision
                db.revision.insert_one(revision)
            revision = {}
        else:
            revision['item_id'] = item_id
            key = l[l.find("<")+1:l.find(">")].replace('/', '').replace('.', '_').strip()
            value = l[l.find(">")+1:l.find("</")]

            if value:
                revision[key] = value