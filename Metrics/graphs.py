import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import json
from dateutil.parser import parse


# Classes to generate the graphs
# Mapping language family with languages based on:
# https://raw.githubusercontent.com/haliaeetus/iso-639/master/data/iso_639-1.json

# Class to generate all graphs for the results of the language number class
class LanguageNumbersGraphs():

    # double axis plot
    def ranking_graph(self, data):
        by_edits = data['language_ranking_by_edits']
        by_editors = data['language_ranking_by_editors']
        keys = sorted(by_edits, key=by_edits.get, reverse=True)
        edits_list = []
        editors_list = []
        for k in keys:
            edits_list.append(by_edits[k])
            editors_list.append(by_editors[k])

        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        ax1.plot(by_edits)
        ax1.set_ylabel('y1')

        ax2 = ax1.twinx()
        ax2.plot(by_editors, 'r-')
        ax2.set_ylabel('y2', color='r')
        for tl in ax2.get_yticklabels():
            tl.set_color('r')
        #ax1.set_xticklabels(keys)
        plt.savefig()


# @todo: include threshold
class SequentialEditingGraphs():

    def _prepare_data(self, data):
        result = {}
        for user, dat in data.iteritems():
            current = ''
            counter = 0
            listdata = []
            listlang = []
            keys = sorted(dat.iterkeys())
            for k in keys:
                lang = dat[k]
                if lang == current:
                    counter += 1
                else:
                    listlang.append(current)
                    listdata.append(counter)
                    counter = 0
                    current = lang
            result[user] = listdata
        return result

    def longest(self, l):
        if (not isinstance(l, list)): return (0)
        return (max([len(l), ] + [len(subl) for subl in l if isinstance(subl, list)] +
                    [self.longest(subl) for subl in l]))

    def prepare_chart(self, result):
        graphdata = {}
        for _, l in result.iteritems():
            counter = 0
            for k in l:
                if counter in graphdata:
                    graphdata[counter].append(k)
                else:
                    graphdata[counter] = [k]
                counter += 1
        N = self.longest(graphdata.values())
        graphdata_balanced = {}
        for k, l in graphdata.iteritems():
            graphdata_balanced[k] = [i if i in l else 0 for i in range(0, N)]
        return graphdata

    def plot(self, graphdata):
        graphdata_balanced = graphdata.values()
        N = self.longest(graphdata_balanced)
        ind = np.arange(N)
        width = 0.35
        plt.bar(ind, graphdata_balanced[0], width)
        for x in xrange(1, len(graphdata_balanced)):
            plt.bar(ind, graphdata_balanced[x], width, bottom=graphdata_balanced[0])

    def stacked_timeline(self):
        data = self._prepare_data()


class LanguageOverlapGraph():

    def clean_data(self, data):
        results = {}
        for d in data:
            results[tuple(d['key'])] = d['value']
        return results

    def get_language_families(self, data):
        language_families = {}
        family = {}
        family_data = {}
        langs = set()
        with open('iso_639-1.json') as infile:
            family = json.load(infile)
        for k,v in family.iteritems():
            family_data[k + ' '] = v['family']
        for (l1, l2), v in data.iteritems():
            langs.add(l1)
            langs.add(l2)

        for l in langs:
            if l in family_data:
                language_families[l] = family_data[l]
        return language_families


    def create_network_graph(self, data):
        data = self.clean_data(data)
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

        # Custom the nodes:
        nx.draw(G, with_labels=True, node_color=carac['myvalue'].cat.codes,
                cmap=plt.cm.Set1, node_size=150, font_size=9, edge_color=df['value'])

        #nx.draw(G, with_labels=True)
        plt.show()



class EditTimelineGraph():

    def clean_data(self, databots, dataregistered, dataanonymous):
        diff = list(set(dataregistered) - set(databots))
        for d in diff:
            del dataregistered[d]
            del dataanonymous[d]
        dataregistered = {parse(k): v for k, v in dataregistered.items()}
        dataanonymous = {parse(k): v for k, v in dataanonymous.items()}
        databots = {parse(k): v for k, v in databots.items()}

        return databots, dataregistered, dataanonymous


    def create_timeline_graph(self, databots, dataregistered, dataanonymous):
        databots, dataregistered, dataanonymous = self.clean_data(databots, dataregistered, dataanonymous)
        keys = sorted(databots.keys())
        keys = sorted(databots.keys())
        bots, registered, anonymous = [], [], []
        for k in keys:
            if k in dataanonymous and dataregistered and databots:
                bots.append(databots[k])
                registered.append(dataregistered[k])
                anonymous.append(dataanonymous[k])
        n_groups = len(keys)
        fig, ax = plt.subplots()
        index = np.arange(n_groups)
        bar_width = 0.35
        opacity = 0.8

        rects1 = plt.bar(index - bar_width, bots, bar_width,
                         alpha=opacity,
                         color='b',
                         label='Bots')
        rects2 = plt.bar(index, registered, bar_width,
                         alpha=opacity,
                         color='g',
                         label='Registered')
        rects3 = plt.bar(index + bar_width, anonymous, bar_width,
                         alpha=opacity,
                         color='r',
                         label='Anonymous')
        plt.rc('xtick', labelsize=10)
        plt.xticks(index + bar_width, [k.strftime("%m/%Y") for k in keys])
        plt.legend()
        plt.tight_layout()
        n = 6  # Keeps every 6th label
        [l.set_visible(False) for (i, l) in enumerate(ax.xaxis.get_ticklabels()) if i % n != 0]
        plt.show()

