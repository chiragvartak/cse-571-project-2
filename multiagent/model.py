from collections import namedtuple
from featureBasedGameState import FeatureBasedGameState


WinTuple = namedtuple('WinTuple', "didWin score")
ModelEntry = namedtuple('ModelEntry', "nWins nSimulations listOfWinTuples")

class Model(object):
    def __init__(self):
        self.data = {}
        self.layout = None  # this is the layout you trained on

        self.start_time = None  # time you started running simulations. Use to calculate self.total_time
        self.total_time = None  # total time it took to complete
        self.total_simulations = 0
        
        # experimental:
        self.win_threshold = 460  # idea: moving threshold. When game is over, if the final score > self.win_threshold, count it as a win
        self.overall_winTuples = []  # will be a list of one WinTuple per simulation ran
        self.max_score_so_far = -9999999  # inform your win_threshold based on the max score you've seen so far.

    def updateEntry(self, fbgs, actionTaken, didWin, score):
        # type: (FeatureBasedGameState, str, bool, int) -> None
        nWins = 0
        nSimulations = 0
        listOfWinTuples = []

        if (fbgs, actionTaken) in self.data.keys():
            # DO NOT GET nWins FROM HERE!!!! RECALCULATE nWins BASED ON self.winThreshold
            nSimulations = self.data[(fbgs, actionTaken)].nSimulations
            listOfWinTuples = self.data[(fbgs, actionTaken)].listOfWinTuples

        nSimulations += 1  # increment nSimulations, always
        listOfWinTuples.append(WinTuple(didWin=didWin, score=score))

        for winTuple in listOfWinTuples:
            nWins += winTuple.didWin or winTuple.score > self.win_threshold  # count a win either as a literal win, or as a score over the threshold

        self.data[(fbgs, actionTaken)] = ModelEntry(nWins,
                                                    nSimulations=nSimulations,
                                                    listOfWinTuples=listOfWinTuples)

    def writeModelToFile(self, file="model.txt"):
        with open(file, 'w') as f:
            f.write("Playing on %s\n" % self.layout)
            f.write("Took %s seconds\n" % self.total_time)
            f.write("Total number of simulations run: %s\n" % self.total_simulations)
            f.write("Total number of literal wins: %s\n" % self.total_literalWins())
            f.write("Total number of effective wins: %s\n" % self.total_effectiveWins())
            f.write("Total number of nodes: %s\n\n" % len(self.data))
            for key, value in self.data.items():
                f.write(str(key) + ": " + str(value) + "\n")

    def total_effectiveWins(self):
        nWins = 0
        for winTuple in self.overall_winTuples:
            nWins += winTuple.score > self.win_threshold
        return nWins

    def total_literalWins(self):
        nWins = 0
        for winTuple in self.overall_winTuples:
            nWins += winTuple.didWin
        return nWins

commonModel = Model()