import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class Plotter:
    def __init__(self, infile):
        self.infile = infile

    def _getdata(self):
        x_known = []
        y_unknown = []
        with open(self.infile) as infile:
            for line in infile:
                tmp = line.strip().split('\t')
                x_known.append(int(tmp[1]))
                y_unknown.append(int(tmp[2]))
        return [x_known, y_unknown]

    def _getdatalimited(self):
        x_known = []
        y_unknown = []
        with open(self.infile) as infile:
            for line in infile:
                tmp = line.strip().split('\t')
                if int(tmp[1]) < 600000 and int(tmp[1]) < 1000000:
                    x_known.append(int(tmp[1]))
                    y_unknown.append(int(tmp[2]))
        return [x_known, y_unknown]


    def plot(self):
        data = self._getdatalimited()
        plt.plot(data[0], data[1], 'ro')
        plt.xlabel('Known')
        plt.ylabel('Unkown')
        plt.show()
        plt.savefig('final-data.pdf')

    #def plotnormalized(self):


plot = Plotter('results/final-userdata.csv')
plot.plot()
