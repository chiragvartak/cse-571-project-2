from collections import namedtuple
from featureBasedGameState import FeatureBasedGameState
from util import TopList


WinTuple = namedtuple('WinTuple', "didWin score")
ModelEntry = namedtuple('ModelEntry', "nWins nSimulations listOfWinTuples")

class Model(object):
    def __init__(self):
        self.data = {}
        self.layout = None  # this is the layout you trained on

        self.start_time = None  # time you started running simulations. Use to calculate self.total_time
        self.total_time = None  # total time it took to complete
        self.total_simulations = 0

        self.states_you_didnt_see_in_training = []
        
        # experimental:
        self.use_winThreshold = True
        self.winThreshold = -9999999  # moving threshold. When game is over, if the final score > self.win_threshold, count it as a win
        self.top_scores = TopList(10)  # keep track of top scores seen. The number of elements in this list indirectly determines your winThreshold and how fast it changes
        self.overall_winTuples = []  # will be a list of one WinTuple per simulation ran
        self.total_effectiveWins = 0
        self.total_literalWins = 0

    def updateEntry(self, fbgs, actionTaken, didWin, score):
        # type: (FeatureBasedGameState, str, bool, float) -> None
        nWins = 0
        nSimulations = 0
        listOfWinTuples = []

        if (fbgs, actionTaken) in self.data.keys():
            entry = self.data[(fbgs, actionTaken)]
            nWins = entry.nWins
            nSimulations = entry.nSimulations
            listOfWinTuples = entry.listOfWinTuples

        if not self.use_winThreshold:
            nWins += didWin
        nSimulations += 1  # increment nSimulations, always
        listOfWinTuples.append(WinTuple(didWin=didWin, score=score))  # append your new WinTuple, always

        # for winTuple in listOfWinTuples:
            # nWins += winTuple.didWin or winTuple.score > self.winThreshold  # count a win either as a literal win, or as a score over the threshold

        self.data[(fbgs, actionTaken)] = ModelEntry(nWins=nWins,
                                                    nSimulations=nSimulations,
                                                    listOfWinTuples=listOfWinTuples)
               
    def update_nWins_for_all_entries(self):
        for key in self.data.keys():
            entry = self.data[key]
            nWins = 0
            nSimulations = entry.nSimulations
            listOfWinTuples = entry.listOfWinTuples

            for winTuple in listOfWinTuples:
                nWins += winTuple.didWin or winTuple.score >= self.winThreshold  # count a win either as a literal win, or as a score over the threshold

            self.data[key] = ModelEntry(nWins=nWins, nSimulations=nSimulations, listOfWinTuples=listOfWinTuples)

    def update_winThreshold(self, score):
        # type: float

        # threshold is the average of the top scores seen so far
        self.top_scores.update(score)
        self.winThreshold = self.top_scores.get_median()  # guarantees half of the top scores count as effective wins

    def writeModelToFile(self, file="model.txt"):
        with open(file, 'w') as f:
            f.write("Playing on %s\n" % self.layout)
            f.write("Took %s seconds\n" % self.total_time)
            f.write("Total number of simulations run: %s\n" % self.total_simulations)
            f.write("Total number of literal wins: %s\n" % self.total_literalWins)
            f.write("Use win threshold: %s\n" % self.use_winThreshold)
            f.write("Total number of effective wins: %s\n" % self.total_effectiveWins)
            f.write("Final win threshold: %s\n" % self.winThreshold)
            f.write("Average score: %s\n" % self.get_average_score())
            f.write("Total number of nodes: %s\n\n" % len(self.data))
            f.write("Number of states you saw in real games which you had not seen in training: %s\n" % len(self.states_you_didnt_see_in_training))
            f.write("States you saw in real games which you had not seen in training:\n\n")
            for state in self.states_you_didnt_see_in_training:
                f.write("%s\n" % state)

            f.write("\nData:\n\n")
            for key, value in self.data.items():
                f.write(str(key) + ": " + str(value) + "\n")

    def get_total_effectiveWins(self):
        nWins = 0
        for winTuple in self.overall_winTuples:
            nWins += winTuple.didWin or winTuple.score >= self.winThreshold
        return nWins

    def get_total_literalWins(self):
        nWins = 0
        for winTuple in self.overall_winTuples:
            nWins += winTuple.didWin
        return nWins

    def get_average_score(self):
        sum_of_scores = sum([winTuple.score for winTuple in self.overall_winTuples])
        return sum_of_scores/len(self.overall_winTuples)

commonModel = Model()