from collections import namedtuple
from featureBasedGameState import FeatureBasedGameState
import pickle
import os

ModelEntry = namedtuple('ModelEntry', "nWins pseudoWins nSimulations avgReward")

class Model(object):
    def __init__(self):
        self.data = {}

    def updateEntry(self, fbgs, actionTaken, nWins, pseudoWins, nSimulations, avgReward):
        # type: (FeatureBasedGameState, str, int, float, int, float) -> None
        self.data[(fbgs, actionTaken)] = ModelEntry(nWins=nWins, pseudoWins=pseudoWins,
                                                    nSimulations=nSimulations, avgReward=avgReward)

    def writeModelToFile(self, file="model.txt"):
        with open(file, 'w') as f:
            for key, value in self.data.items():
                f.write(str(key) + ": " + str(value) + "\n")
        self.saveModel()

    def saveModel(self):
        print("pickling the model")
        with open("model.pkl", 'wb') as f:
            pickle.dump(self.data, f)
        print("successfully pickled the model")


def getModel(filename = "model.pkl"):
    model = Model()
    if os.path.exists(filename):
        with open(filename, 'rb') as f: 
            data = pickle.load(f)
        model.data = data
    return model


# commonModel = Model()
commonModel = getModel()