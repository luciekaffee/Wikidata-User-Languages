# -*- coding: utf-8 -*-
import json
from pymongo import MongoClient
import numpy

client = MongoClient()
db = client.wikibabeldb
# Total edits: 52580375
# db.revision.aggregate({$group: {_id:'$language', sum: {$sum: 1}}})
# db.revision.aggregate([ {$match:{'username' : 'Derzno'}}, {$group: {_id:'$language', sum: {$sum: 1}}}, {$sort: {'sum': -1}} ])
# db.revision.aggregate([{$group : { _id : '$username', count : {$sum : 1}}}, {$sort: {'count': -1}}])

def writeToFile(user, known, unknown, unknown_langs):
    with open('results/final-userdata.csv', 'a+') as csvfile:
        csvfile.write(user.encode('utf-8') + '\t' + str(known) + '\t' + str(unknown) + '\t' + str(unknown_langs))

def makeLangArray(langs):
    lang_arr = []
    for lang in langs:
        arr = lang.split('-')
        if len(arr) > 2:
            lang_arr.append(arr[0] + arr[1])
        else:
            lang_arr.append(arr[0])
    return lang_arr

users = {}

with open('../data/userdata.json') as data_file:
    users = json.load(data_file)

user_without_edit = 0
user_edits = {}
for user,langs in users.iteritems():
    user = user.replace('User:', '')
    lang_arr = makeLangArray(langs)
    aggregate_params = [ {'$match':{'username' : user}}, {'$group': {'_id':'$language', 'sum': {'$sum': 1}}}, {'$sort': {'sum': -1}} ]
    results = db.revision.aggregate(aggregate_params)
    known = 0
    unknown = 0
    unknown_langs = []
    for doc in results:
        if not doc['_id']:
            continue
        if doc['_id'].strip() in lang_arr:
            known += doc['sum']
        else:
            unknown_langs.append(doc['_id'].strip())
            unknown += doc['sum']
    user_edits[user] = {}
    user_edits[user]['edits_known'] = known
    if known == 0 and unknown == 0:
        user_without_edit += 1
        continue
    writeToFile(user, known, unknown, unknown_langs)


print "user without edits:" + str(user_without_edit)




def get_all_edits_by_user():
    with open('results/edits-by-user.json', 'w') as write_file:
        aggregate_params = [{'$group' : { '_id' : '$username', 'count' : {'$sum' : 1}}}, {'$sort': {'count': -1}}]
        result = db.revision.aggregate(aggregate_params)
        write_file.write(json.dumps([doc for doc in result]))

def get_avarage_edit():
        with open('results/edits-by-user.json') as file:
            user_edits = json.loads(file)
            user = 0
            edits = 0
            med_edits = []
            for doc in user_edits:
                user += 1
                edits += doc['count']
                med_edits.append(doc['count'])
            print 'user: ' + str(user)
            print 'edits: ' + str(edits)
            print 'average: ' + str(edits/user)
            print 'median: ' + str(numpy.median(med_edits))