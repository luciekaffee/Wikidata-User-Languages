import psycopg2
import json
import numpy
from dateutil.parser import parse
import itertools


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
    def __init__(self, cursor, connection):
        self.cursor = cursor
        self.connection = connection

    # get the data for languages and timestamps for all editors
    # @return dict {editor:{timestamp: language}}
    def _get_editor_data_language(self, table, min_edits):
        editor_data = {}
        errorcount = 0
        query = "SELECT username, json_agg(json_build_array(timestamp, language)) AS users FROM %s GROUP BY username;" %(table)
        self.cursor.execute(query)
        self.connection.commit()
        rows = self.cursor.fetchall()
        for r in rows:
            if not len(r[1]) > min_edits:
                continue
            timedict = {}
            for k, v in r[1]:
                timedict[k] = v
            editor_data[r[0]] = timedict
        print 'number of editors for sequential metric: ' + str(len(editor_data.keys()))
        return editor_data

    def _get_editor_data_items(self, table, min_edits):
        editor_data = {}
        errorcount = 0
        query = "SELECT username, json_agg(json_build_array(timestamp, item_id)) AS users FROM %s GROUP BY username;" %(table)
        self.cursor.execute(query)
        self.connection.commit()
        rows = self.cursor.fetchall()
        for r in rows:
            if not len(r[1]) > min_edits:
                continue
            timedict = {}
            for k, v in r[1]:
                timedict[k] = v
            editor_data[r[0]] = timedict
        print 'number of editors for sequential metric: ' + str(len(editor_data.keys()))
        return editor_data

    # @todo: normalize based on the number of languages/timestamps
    def calculate_jumps(self, editor_data, edits=False):
        jumps = []
        for k, v in editor_data.iteritems():
            curr = ''
            counter = 0
            langs = set(v.values())
            total = len(v)
            for time in sorted(v.keys()):
                if v[time] == curr:
                    continue
                else:
                    counter += 1
                    curr = v[time]
            jumps.append(counter/float(total))
        median = numpy.median(jumps)
        avg = numpy.average(jumps)
        maxv = max(jumps)
        minv = min(jumps)
        print 'JUMPS: ' + str(median) + ' average: ' + str(avg) + 'max/min: ' + str(maxv) + '/' + str(minv)
        return [median, avg, maxv, minv]

    def run(self, table, min_edits):
        print 'JUMPS IN LANGUAGES'
        editor_data = self._get_editor_data_language(table, min_edits)
        self.calculate_jumps(editor_data)
        print 'JUMPS IN ENTITIES'
        editor_data_entities = self._get_editor_data_items(table, min_edits)
        self.calculate_jumps(editor_data_entities, edits=True)
        return editor_data


# Find overlaps between languages that editors edit (e.g. German is close to English, French to Spanish etc)
class LanguageOverlap:
    def __init__(self, cursor, connection):
        self.cursor = cursor
        self.connection = connection

    # @return dict{(tuple language pair): int co-occurence}
    def _get_data(self, table):
        language_overlap = {}
        query = """SELECT array_agg(DISTINCT language) FROM %s GROUP BY username;""" % (table)
        self.cursor.execute(query)
        self.connection.commit()
        rows = self.cursor.fetchall()

        for r in rows:
            combi = list(itertools.combinations(r[0], 2))
            for c in combi:
                if c not in language_overlap:
                    language_overlap[c] = 1
                else:
                    language_overlap[c] += 1
        return language_overlap

    # boxplot
    # correlation between the languages that are used together and the same language family
    def correlation_overlap_language_family(self, language_overlap):
        family = {}
        family_data = {}
        with open('iso_639-1.json') as infile:
            family = json.load(infile)
        for k,v in family.iteritems():
            family_data[k + ' '] = v['family']
        same_family_counter = []
        different_family_counter = []
        for (l1, l2), v in language_overlap.iteritems():
            if l1 in family_data and l2 in family_data:
                if family_data[l1] == family_data[l2]:
                    same_family_counter.append(v)
                else:
                    different_family_counter.append(v)
        return same_family_counter, different_family_counter



    # limit to values over the mean
    # @todo set the mean limit properly
    def limit(self, language_overlap, language_ranking=None):
        language_overlap_limited = {}
        mean = numpy.mean(language_overlap.values())
        for (l1, l2), v in language_overlap.iteritems():
            if v > (mean * 5):
                language_overlap_limited[(l1, l2)] = v
        if language_ranking:
            language_overlap_limited_rank = {}
            top_50 = sorted(language_ranking, key=language_ranking.get, reverse=True)[:50]
            for (l1, l2), v in language_overlap_limited.iteritems():
                if l1 in top_50 and l2 in top_50:
                    language_overlap_limited_rank[(l1, l2)] = v
            language_overlap_limited = language_overlap_limited_rank
        return language_overlap_limited

    def run(self, table, language_ranking=None):
        language_overlap = self._get_data(table)
        language_overlap_limited = self.limit(language_overlap, language_ranking)
        print 'number combinations: ' + str(len(language_overlap_limited))
        same_family_counter, different_family_counter = self.correlation_overlap_language_family(language_overlap)
        return [language_overlap_limited, same_family_counter, different_family_counter]


class EditTimeline:
    def __init__(self, cursor, connection):
        self.cursor = cursor
        self.connection = connection

    def get_time_data(self, table):
        time_data = {}
        query = """SELECT date_trunc('month', timestamp), COUNT(username) FROM %s GROUP BY date_trunc('month', timestamp);""" % (table)
        self.cursor.execute(query)
        self.connection.commit()
        rows = self.cursor.fetchall()
        for r in rows:
            time_data[r[0].strftime("%m/%Y")] = r[1]
        return time_data

    def run(self, table):
        return self.get_time_data(table)

# Query: SELECT username, COUNT(DISTINCT language), COUNT(id) FROM registered GROUP BY username LIMIT 10;
class MonoVsMultilingual:
    def __init__(self, cursor, connection):
        self.cursor = cursor
        self.connection = connection

    def get_edit_data(self, table):
        data = {}
        query = """SELECT username, COUNT(DISTINCT language), COUNT(id) FROM %s GROUP BY username;""" % (table)
        self.cursor.execute(query)
        self.connection.commit()
        rows = self.cursor.fetchall()
        for r in rows:
            data[r[0]] = [r[1], r[2]]
        return data



# How fast is a label changed? Difference between registered, anonymous, bots
#class LabelLifetime:
#    def __init__(self, cursor, connection):
#        self.cursor = cursor
#        self.connection = connection

