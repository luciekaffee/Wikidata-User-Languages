from pymongo import MongoClient
import json
import numpy
from datetime import datetime


# Class to describe how many languages a user edits in average
# And how many editors edit each language (list of languages by edits)
# For registered, anonymous and bots
# And which languages the three groups edit
class LanguageNumbers():
    def __init__(self, db):
        self.db = db

    # Query the DB for editors and the languages they edited (not unique! All languages edited from all edits)
    # @return dict{editor: [languages (possibly duplicated)]} --> for unique use '$addToSet' instead of '$push'
    # db.revision.aggregate([{$group: {_id: "$username", langs: {$push: "$language"}}}], {allowDiskUse:true})
    def _get_editors_and_languages(self, col):
        editors_languages = {}
        query = [{'$group': {'_id': "$username", 'langs': {'$push': "$language"}}}]
        cur = self.db[col].aggregate(query, allowDiskUse=True)
        errorcounter = 0
        try:
            for doc in cur:
                editors_languages[doc['_id']] = doc['langs']
        except:
            errorcounter += 1
        print 'errorcounter: ' + str(errorcounter)
        print 'finished DB request'
        return editors_languages

    # get languages by editors based on editors_languages to avoid another DB request
    # @return dict{language: int_nr_of_editors}
    def _get_languages_by_nr_editors(self, editors_languages):
        languages_editors = {}
        for k, v in editors_languages.iteritems():
            langs = set(v)
            for l in langs:
                if l in languages_editors:
                    languages_editors[l] += 1
                else:
                    languages_editors[l] = 1
        return languages_editors

    # Number of languages per editor
    # @return int average/median number of languages per editor
    def languages_per_editor(self, editors_languages):
        print 'Number of editors ' + str(len(editors_languages.keys()))
        languages = []
        for _,v in editors_languages.iteritems():
            languages.append(len(set(v)))
        median = numpy.median(languages)
        avg = numpy.average(languages)
        maxv = max(languages)
        minv = min(languages)
        print 'languages per editor: ' + str(median) + ' average: ' + str(avg) + 'max/min: ' + str(maxv) + '/' + str(minv)
        return [median, avg, maxv, minv]

    # Number of editors that edit each language
    # @return int average/median number of editors per language
    def editors_per_language(self, languages_editors):
        print 'Number languages ' + str(len(languages_editors.values()))
        median = numpy.median(languages_editors.values())
        avg = numpy.average(languages_editors.values())
        maxv = max(languages_editors.values())
        minv = min(languages_editors.values())
        print 'editors per language: ' + str(median) + ' average: ' + str(avg) + 'max/min: ' + str(maxv) + '/' + str(minv)
        return [median, avg, maxv, minv]

    # Languages sorted by number of total edits
    # @return dict{languages:number_of_edits}
    def language_ranking_by_edits(self, editors_languages):
        languages_editors = {}
        for k, langs in editors_languages.iteritems():
            for l in langs:
                if l in languages_editors:
                    languages_editors[l] += 1
                else:
                    languages_editors[l] = 1
        print 'finished languages ranking by edits'
        return sorted(languages_editors.iteritems(), key=lambda (k, v): (v, k), reverse=True)

    # Languages sorted by number of editors editing the language
    # @return dict{language:number_of_editors}
    def language_ranking_by_editors(self, languages_editors):
        print 'finished languages ranking by editors'
        return sorted(languages_editors.iteritems(), key=lambda (k, v): (v, k), reverse=True)

    #@todo: add this for all three usertypes
    # @return dict ['languages_per_editor': [media, avg, max, min], 'editors_per_language': [media, avg, max, min],
    # 'language_ranking_by_edits': [sorted_list_languages], 'language_ranking_by_editors': [sorted_list_languages]]
    def run(self, db_field):
        results = {}
        editors_languages = self._get_editors_and_languages(db_field)
        languages_editors = self._get_languages_by_nr_editors(editors_languages)
        results['languages_per_editor'] = self.languages_per_editor(editors_languages)
        results['editors_per_language'] = self.editors_per_language(languages_editors)
        results['language_ranking_by_edits'] = self.language_ranking_by_edits(editors_languages)
        results['language_ranking_by_editors'] = self.language_ranking_by_editors(languages_editors)
        return results

# Class to find whether the edits of languages were done in bulge per language
# Or mixed per language (kind of a timeline)
# db.revision.aggregate([{$group: {_id: {"$ifNull": [ "$username", "$ip" ]},
# data: {$push: {language: "$language", time: "$timestamp"}}}}], {allowDiskUse:true})
class SequentialEditing():
    def __init__(self, db):
        self.db = db

    # get the data for languages and timestamps for all editors
    # @return dict {editor:{timestamp: language}}
    def _get_editor_data(self, col):
        date_format_string = "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'"
        editor_data = {}
        query = [{'$group': {'_id': {"$ifNull": ["$username", "$ip"]}, 'data': {'$push': {'language': "$language", 'time': "$timestamp"}}}}]
        cur = self.db[col].aggregate(query, allowDiskUse=True)
        for doc in cur:
            for d in doc['data']:
                editor_data[datetime.strptime(d['time'], date_format_string)] = d['language']
        return editor_data

    def run(self, db_field):
        editor_data = self._get_editor_data(db_field)
        print editor_data
        return editor_data


# Find overlaps between languages that editors edit (e.g. German is close to English, French to Spanish etc)
class LanguageOverlap:
    def __init__(self, db):
        self.db = db

# How fast is a label changed? Difference between registered, anonymous, bots
class LabelLifetime:
    def __init__(self, db):
        self.db = db

