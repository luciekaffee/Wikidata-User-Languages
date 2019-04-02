import pandas as pd
from pandas import Timestamp
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import json
from dateutil.parser import parse
from scipy.stats.stats import pearsonr


# Classes to generate the graphs
# Mapping language family with languages based on:
# https://raw.githubusercontent.com/haliaeetus/iso-639/master/data/iso_639-1.json

# Class to generate all graphs for the results of the language number class
class LanguageNumbersGraphs():

    # double axis plot
    # limited to the top 50 languages by edits
    def ranking_graph(self, data):
        by_edits = data['language_ranking_by_edits']
        by_editors = data['language_ranking_by_editors']
        keys = sorted(by_edits, key=by_edits.get, reverse=True)[:50]
        edits_list = []
        editors_list = []
        for k in keys:
            edits_list.append(by_edits[k])
            editors_list.append(by_editors[k])

        fig = plt.figure()
        ax1 = fig.add_subplot(211)
        ax2 = ax1.twinx()
        ax1.set_ylabel('By edits', color='r')
        ax1.tick_params(axis='y', labelcolor='r')
        lns1 = ax1.plot(edits_list, 'ro-', label='By edits')
        ax2.set_ylabel('By editors', color='b')
        ax2.tick_params(axis='y', labelcolor='b')
        lns2 = ax2.plot(editors_list, 'bo--', label='By editor')

        #plt.xticks(range(0, len(keys)), keys, rotation='vertical')
        #ax1.xaxis.set_tick_params(rotation=45)
        ax1.set_xticks(range(0, len(keys)))
        ax1.set_xticklabels(keys, rotation=80)

        lns = lns1 + lns2
        labs = [l.get_label() for l in lns]
        ax1.legend(lns, labs, loc=0)

        plt.show()


# @todo: include threshold
class SequentialEditingGraphs():

    def get_matrix_graph(self, data):
        newdata = {}
        for k, v in data.iteritems():
            newdata[k] = dict([parse(x), y] for x, y in v.items())
        lists = []
        for k,v in newdata.iteritems():
            newl = []
            for x, y in v.iteritems():
                newl.append(hash(y))
            lists.append(newl)
        maxLen = max(map(len, lists))
        for row in lists:
            if len(row) < maxLen:
                row.extend(0 for _ in xrange(maxLen - len(row)))
        plt.matshow(lists)
        plt.show()

    # def _prepare_data(self, data):
    #     result = {}
    #     for user, dat in data.iteritems():
    #         current = ''
    #         counter = 0
    #         listdata = []
    #         listlang = []
    #         keys = sorted(dat.iterkeys())
    #         for k in keys:
    #             lang = dat[k]
    #             if lang == current:
    #                 counter += 1
    #             else:
    #                 listlang.append(current)
    #                 listdata.append(counter)
    #                 counter = 0
    #                 current = lang
    #         result[user] = listdata
    #     return result
    #
    # def longest(self, l):
    #     if (not isinstance(l, list)): return (0)
    #     return (max([len(l), ] + [len(subl) for subl in l if isinstance(subl, list)] +
    #                 [self.longest(subl) for subl in l]))
    #
    # def prepare_chart(self, result):
    #     graphdata = {}
    #     for _, l in result.iteritems():
    #         counter = 0
    #         for k in l:
    #             if counter in graphdata:
    #                 graphdata[counter].append(k)
    #             else:
    #                 graphdata[counter] = [k]
    #             counter += 1
    #     N = self.longest(graphdata.values())
    #     graphdata_balanced = {}
    #     for k, l in graphdata.iteritems():
    #         graphdata_balanced[k] = [i if i in l else 0 for i in range(0, N)]
    #     return graphdata
    #
    # def plot(self, graphdata):
    #     graphdata_balanced = graphdata.values()
    #     N = self.longest(graphdata_balanced)
    #     ind = np.arange(N)
    #     width = 0.35
    #     plt.bar(ind, graphdata_balanced[0], width)
    #     for x in xrange(1, len(graphdata_balanced)):
    #         plt.bar(ind, graphdata_balanced[x], width, bottom=graphdata_balanced[0])
    #
    # def stacked_timeline(self):
    #     data = self._prepare_data()


class LanguageOverlapGraph():

    def clean_data(self, data):
        results = {}
        for d in data:
            results[tuple(d['key'])] = d['value']
        return results

    def get_language_families(self, results):
        language_families = {}
        family = {}
        family_data = {}
        langs = set()
        with open('iso_639-1.json') as infile:
            family = json.load(infile)
        for k,v in family.iteritems():
            family_data[k + ' '] = v['family']
        for (l1, l2), v in results.iteritems():
            langs.add(l1)
            langs.add(l2)

        for l in langs:
            if l in family_data:
                language_families[l] = family_data[l]
        return language_families


    def create_network_graph(self, data):
        data = self.clean_data(data[0])
        language_families = self.get_language_families(data)

        fro = []
        to = []
        numbers = []
        for (l1, l2), v in data.iteritems():
            if l1 in language_families.keys() and l2 in language_families.keys():
                fro.append(l1)
                to.append(l2)
                numbers.append(v)
        df = pd.DataFrame({'from': fro, 'to': to, 'value': numbers})
        carac = pd.DataFrame({'ID': language_families.keys(), 'myvalue': language_families.values()})
        G = nx.from_pandas_edgelist(df, 'from', 'to')

        carac = carac.set_index('ID')
        carac = carac.reindex(G.nodes())

        # And I need to transform my categorical column in a numerical value: group1->1, group2->2...
        carac['myvalue'] = pd.Categorical(carac['myvalue'])
        carac['myvalue'].cat.codes
        type(carac['myvalue'].cat.codes)
        legend = {}
        for k, v in carac['myvalue'].cat.codes.iteritems():
            legend[language_families[k]] = v

        values = [carac['myvalue'].cat.codes.get(node, 0) for node in G.nodes()]
        f = plt.figure(1)
        ax = f.add_subplot(1, 1, 1)
        jet = cm = plt.get_cmap('jet')
        cNorm = colors.Normalize(vmin=0, vmax=max(values))
        scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)
        for label in legend:
            ax.plot([0], [0], color=scalarMap.to_rgba(legend[label]), label=label)
        # Custom the nodes:
        nx.draw(G, with_labels=True, node_color=carac['myvalue'].cat.codes,
                cmap=plt.cm.Set1, node_size=500, font_size=9, edge_color='black')

        #nx.draw(G, with_labels=True)
        params = {'axes.labelsize': 20, 'axes.titlesize': 20, 'text.fontsize': 20, 'legend.fontsize': 20,
                  'xtick.labelsize': 20, 'ytick.labelsize': 20}
        plt.rcParams.update(params)
        ax.legend(loc='lower right', bbox_to_anchor=(0.5, -0.05),
                  fancybox=True, ncol=5)
        plt.legend()
        plt.show()

    def create_boxplot(self, data):
        same_family_counter = data[1]
        different_family_counter = data[2]
        d = [same_family_counter, different_family_counter]
        fig1, ax1 = plt.subplots()
        #ax1.set_title('Editors that edit same and different language family')
        ax1.boxplot(d, showfliers=False)
        plt.xticks([1, 2], ['Same language famility', 'Different language family'])

        plt.show()


#@todo: work over sorting!!
class EditTimelineGraph():

    def get_time(self, data):
        time = {}
        for k, v in data.iteritems():
            date = parse(str(k.year) + '-' + str(k.month))
            if date in time.keys():
                time[date] += v
            else:
                time[date] = v
        return time

    def clean_data(self, databots, dataregistered, dataanonymous):
        #diff = list(set(dataregistered) - set(databots))
        #for d in diff:
        #    del dataregistered[d]
        #    del dataanonymous[d]
        dataregistered = {parse(k): v for k, v in dataregistered.items()}
        dataanonymous = {parse(k): v for k, v in dataanonymous.items()}
        databots = {parse(k): v for k, v in databots.items()}

        dataregistered_sorted_tmp = self.get_time(dataregistered)
        dataanonymous_sorted_tmp = self.get_time(dataanonymous)
        databots_sorted_tmp = self.get_time(databots)
        databots_sorted = []
        dataregistered_sorted = []
        dataanonymous_sorted = []
        keys = sorted(databots_sorted_tmp.keys())

        for k in keys:
            if k in dataregistered_sorted_tmp:
                dataregistered_sorted.append(dataregistered_sorted_tmp[k])
            if k in dataanonymous_sorted_tmp:
                dataanonymous_sorted.append(dataanonymous_sorted_tmp[k])
            databots_sorted.append(databots_sorted_tmp[k])

        return keys, databots_sorted, dataregistered_sorted, dataanonymous_sorted


    def create_timeline_graph(self, databots, dataregistered, dataanonymous):
        keys, databots_sorted, dataregistered_sorted, dataanonymous_sorted = self.clean_data(databots, dataregistered, dataanonymous)
        keys = databots_sorted.keys()
        index = np.arange(len(keys))
        bar_width = 0.35
        # keys = sorted(databots.keys())
        # bots, registered, anonymous = [], [], []
        # for k in keys:
        #     if k in dataanonymous and dataregistered and databots:
        #         bots.append(databots[k])
        #         registered.append(dataregistered[k])
        #         anonymous.append(dataanonymous[k])
        # n_groups = len(keys)
        # fig, ax = plt.subplots()
        # index = np.arange(n_groups)
        # bar_width = 0.35
        # opacity = 0.8

        # rects1 = plt.plot(index - bar_width, bots, bar_width,
        #                  alpha=opacity,
        #                  color='b',
        #                  label='Bots')
        # rects2 = plt.plot(index, registered, bar_width,
        #                  alpha=opacity,
        #                  color='g',
        #                  label='Registered')
        # rects3 = plt.plot(index + bar_width, anonymous, bar_width,
        #                  alpha=opacity,
        #                  color='r',
        #                  label='Anonymous')

        fig, ax = plt.subplots()
        plt.plot(databots_sorted[:-1], 'b-', label='Bots')
        plt.plot(dataregistered_sorted[:-1], 'r--', label='Registered')#[-len(databots):]
        plt.plot(dataanonymous_sorted[:-1], 'g-+', label='Anonymous')#[-len(databots):]
        plt.legend()
        plt.rc('xtick', labelsize=10)
        plt.xticks(index + bar_width, [k.strftime("%m/%Y") for k in keys], rotation='vertical')
        #plt.xticks([])
        plt.ylabel('Number of label edits (log)')
        plt.legend()
        plt.tight_layout()
        params = {'axes.labelsize': 22, 'axes.titlesize': 22, 'text.fontsize': 22, 'legend.fontsize': 22,
                  'xtick.labelsize': 22, 'ytick.labelsize': 22}
        plt.rcParams.update(params)
        plt.rcParams['figure.figsize'] = 100, 100
        plt.yscale('log')
        n = 5  # Keeps every 6th label
        [l.set_visible(False) for (i, l) in enumerate(ax.xaxis.get_ticklabels()) if i % n != 0]
        plt.show()

class MonoVsMultilingualGraphs():

    def createScatterPlot(self, data):
        x = []
        y = []
        #plt.rcParams.update({'font.size': 22})
        params = {'axes.labelsize': 22, 'axes.titlesize': 22, 'text.fontsize': 22, 'legend.fontsize': 22,
                  'xtick.labelsize': 22, 'ytick.labelsize': 22}
        plt.rcParams.update(params)
        plt.rcParams['figure.figsize'] = 3, 3
        for k,v in data.iteritems():
            x.append(v[0])
            y.append(v[1])
        print pearsonr(x,y)
        plt.xlabel('Number of languages')
        plt.ylabel('Number of edits')
        plt.scatter(x, y)
        plt.show()

    # "Rule of thumb" interpretation:
    #0.00-0.19: very weak
    #0.20-0.39: weak
    #0.40-0.59: moderate
    #0.60-0.79: strong
    #0.80-1.00: very strong
    def calculatatePearsonr(self, x, y):
        return pearsonr(x,y)




