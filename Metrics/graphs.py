import numpy as np
import matplotlib.pyplot as plt

# Classes to generate the graphs

# Class to generate all graphs for the results of the language number class
class LanguageNumbersGraphs():
    def __init__(self, data):
        self.data = data

    def ranking_graph(self):
        by_edits = self.data['language_ranking_by_edits']
        by_editors = self.data['language_ranking_by_editors']
        by_edits_dict = {}
        by_editors_dict = {}
        for e in by_edits:
            by_edits_dict[e[0]] = e[1]
        for e in by_editors:
            by_editors_dict[e[0]] = e[1]
        plt.plot(by_edits_dict, by_edits_dict, 'r--', by_edits_dict, by_editors_dict, 'bs')
        plt.savefig()
