import psycopg2
import json
import numpy
from dateutil.parser import parse


# Class to describe how many languages a user edits in average
# And how many editors edit each language (list of languages by edits)
# For registered, anonymous and bots
# And which languages the three groups edit
class LanguageNumbers():
    def __init__(self, cursor, connection):
        self.cursor = cursor
        self.connection = connection

    # Query the DB for editors and the languages they edited (not unique! All languages edited from all edits)
    # @return dict{editor: [languages (possibly duplicated)]}
    # SELECT username, array_agg(language) FROM registered GROUP BY username;
    def _get_editors_and_languages(self, table):
        editors_languages = {}
        query = """SELECT username, array_agg(language) FROM %s GROUP BY username;""" %(table)
        self.cursor.execute(query)
        self.connection.commit()
        rows = self.cursor.fetchall()

        for r in rows:
            editors_languages[r[0]] = r[1]
        print 'finished DB request'
        return editors_languages

    def _get_editors_and_languages_unique(self, table):
        editors_languages_uni = {}
        query = """SELECT username, array_agg(DISTINCT language) FROM %s GROUP BY username;""" %(table)
        self.cursor.execute(query)
        self.connection.commit()
        rows = self.cursor.fetchall()

        for r in rows:
            editors_languages_uni[r[0]] = r[1]
        print 'finished DB request'
        return editors_languages_uni

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

    # Get the edit counts for all editors
    # @return list[average, median, max, min] number of edits
    def get_edit_count(self, editors_languages):
        edit_counts = []
        for _,v in editors_languages.iteritems():
            edit_counts.append(len(v))
        median = numpy.median(edit_counts)
        avg = numpy.average(edit_counts)
        maxv = max(edit_counts)
        minv = min(edit_counts)
        print 'edit counts: ' + str(median) + ' average: ' + str(avg) + 'max/min: ' + str(maxv) + '/' + str(minv)
        return [median, avg, maxv, minv]


    # Number of languages per editor
    # @return list [average, median, max, min] number of languages per editor
    # SELECT username, count(DISTINCT language) FROM registered GROUP BY username;
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
    # @return list [average, median, max, min] number of editors per language
    def editors_per_language(self, languages_editors):
        print 'Number languages ' + str(len(languages_editors.values()))
        median = numpy.median(languages_editors.values())
        avg = numpy.average(languages_editors.values())
        maxv = max(languages_editors.values())
        minv = min(languages_editors.values())
        print 'editors per language: ' + str(median) + ' average: ' + str(avg) + 'max/min: ' + str(maxv) + '/' + str(minv)
        return [median, avg, maxv, minv]

    # Languages sorted by number of total edits
    # @return dict{languages:number_of_edits} unsorted!
    def language_ranking_by_edits(self, editors_languages):
        languages_editors = {}
        for k, langs in editors_languages.iteritems():
            for l in langs:
                if l in languages_editors:
                    languages_editors[l] += 1
                else:
                    languages_editors[l] = 1
        print 'finished languages ranking by edits'
        return languages_editors

    # Languages sorted by number of editors editing the language
    # @return dict{language:number_of_editors} unsorted!
    def language_ranking_by_editors(self, languages_editors):
        print 'finished languages ranking by editors'
        return languages_editors

    #@todo: add this for all three usertypes
    # @return dict ['edit_count':[media, avg, max, min], languages_per_editor': [media, avg, max, min],
    # 'editors_per_language': [media, avg, max, min],
    # 'language_ranking_by_edits': [sorted_list_languages], 'language_ranking_by_editors': [sorted_list_languages]]
    def run(self, table):
        results = {}
        editors_languages = self._get_editors_and_languages(table)
        #editors_languages_uni = self._get_editors_and_languages_unique(table)
        languages_editors = self._get_languages_by_nr_editors(editors_languages)
        results['edit_count'] = self.get_edit_count(editors_languages)
        results['languages_per_editor'] = self.languages_per_editor(editors_languages)
        results['editors_per_language'] = self.editors_per_language(languages_editors)
        results['language_ranking_by_edits'] = self.language_ranking_by_edits(editors_languages)
        results['language_ranking_by_editors'] = self.language_ranking_by_editors(languages_editors)
        return results

# Class to find whether the edits of languages were done in bulge per language
# Or mixed per language (kind of a timeline)
class SequentialEditing():
    def __init__(self, cursor, connection, minEdits):
        self.cursor = cursor
        self.connection = connection
        self.minEdits = minEdits

    # get the data for languages and timestamps for all editors
    # @return dict {editor:{timestamp: language}}
    def _get_editor_data(self, table):
        editor_data = {}
        errorcount = 0
        query = "SELECT username, json_agg(json_build_array(timestamp, language)) AS users FROM %s GROUP BY username;" %(table)
        self.cursor.execute(query)
        self.connection.commit()
        rows = self.cursor.fetchall()
        for r in rows:
            if not len(r[1]) > self.minEdits:
                continue
            timedict = {}
            for k, v in r[1]:
                timedict[k] = v
            editor_data[r[0]] = timedict
        print 'number of editors: ' + str(len(editor_data.keys()))
        return editor_data

    def run(self, table):
        editor_data = self._get_editor_data(table)
        return editor_data


# Find overlaps between languages that editors edit (e.g. German is close to English, French to Spanish etc)
class LanguageOverlap:
    def __init__(self, cursor, connection):
        self.cursor = cursor
        self.connection = connection

    def _get_data(self, table):


# How fast is a label changed? Difference between registered, anonymous, bots
class LabelLifetime:
    def __init__(self, cursor, connection):
        self.cursor = cursor
        self.connection = connection

