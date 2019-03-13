import numpy as np
import matplotlib.pyplot as plt

# Classes to generate the graphs

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
            for time, lang in data[user]:
                if lang is current:
                    counter += 1
                elif lang is not current:
                    listlang.append(current)
                    listdata.append(counter)
                    current = lang
                    counter = 0
            result[user] = [listdata, listlang]
        return result

    def stacked_timeline(self):
        data = self._prepare_data()







