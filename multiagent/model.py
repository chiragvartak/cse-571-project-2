from collections import namedtuple
from featureBasedGameState import FeatureBasedGameState

ModelEntry = namedtuple('ModelEntry', "nWins nSimulations avgReward")

class Model(object):
    def __init__(self):
        self.data = {}
        self.layout = None  # this is the layout you trained on
        self.win_threshold = None   # idea: moving threshold. When game is over, if the final score > self.win_threshold, count it as a win

        self.start_time = None  # time you started running simulations. Use to calculate self.total_time
        self.total_time = None  # total time it took to complete
        self.total_simulations = 0
        self.total_wins = 0

    def updateEntry(self, fbgs, actionTaken, nWins, nSimulations, avgReward):
        # type: (FeatureBasedGameState, str, int, int, float) -> None
        self.data[(fbgs, actionTaken)] = ModelEntry(nWins=nWins,
                                                    nSimulations=nSimulations,  
                                                    avgReward=avgReward)

    def writeModelToFile(self, file="model.txt"):
        with open(file, 'w') as f:
            f.write("Playing on %s\n" % self.layout)
            f.write("Took %s seconds\n" % self.total_time)
            f.write("Total number of simulations run: %s\n" % self.total_simulations)
            f.write("Total number of wins: %s\n" % self.total_wins)
            f.write("Total number of nodes: %s\n\n" % len(self.data))
            for key, value in self.data.items():
                f.write(str(key) + ": " + str(value) + "\n")

commonModel = Model()