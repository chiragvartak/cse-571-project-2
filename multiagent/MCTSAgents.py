import random

from featureBasedGameState import FeatureBasedGameState
from math import sqrt, log
from model import commonModel
from multiAgents import MultiAgentSearchAgent

class MCTSAgent(MultiAgentSearchAgent):
    def __init__(self, evalFn = 'betterEvaluationFunction', numTraining = '0', isReal = False):
        self.currentGame = 0
        self.numberOfTrainingGames = int(numTraining)

    def registerInitialState(self, state):
        self.currentGame += 1
        # print "state\n", state
        # print "type(state)\n", type(state)
        # print "state.__class__.__name__\n", state.__class__.__name__

    def getAction(self, state):
        # type: (GameState) -> str
        fbgs = FeatureBasedGameState(state)
        if self.currentGame <= self.numberOfTrainingGames:
            uctValues = self.getUCTValues(fbgs, commonModel)
            # print "uctValues", uctValues
            # actionToReturn = max(uctValues)[1]

            # if there are multiple elements with the max value, pick randomly between them
            actionToReturn = random.choice([
                uctValue 
                for uctValue in uctValues 
                    if uctValue[0]==max(uctValues)[0]
                ])[1]
            return actionToReturn
        else:  # This is real game - do the best move!
            return self.realActionToTake(fbgs, commonModel)

    def realActionToTake(self, fbgs, model):
        # print "Choosing real action"
        valueActionPairs = []  # Value can be whatever you formulate it to be
        for action in fbgs.rawGameState.getLegalActions():
            value = None
            if (fbgs, action) not in model.data:
                value = 0
            else:
                value = model.data[(fbgs, action)].nSimulations  # MCTS thing for now - select action with max simulations
                # value = model.data[(fbgs, action)].avgReward
            valueActionPairs.append((value, action))
            
        # if there are multiple elements with the max value, pick randomly between them
        return random.choice([
            valueActionPair 
            for valueActionPair in valueActionPairs 
                if valueActionPair[0]==max(valueActionPairs)[0]
            ])[1]

    def getUCTValues(self, fbgs, model):
        # type: (FeatureBasedGameState, Model) -> List[(float, str)]
        w = {}
        n = {}
        N = 0
        c = sqrt(2)
        # c = 1
        legalActions = fbgs.rawGameState.getLegalActions()
        for action in legalActions:
            if (fbgs, action) not in model.data:
                n[action] = 0
                w[action] = 0
            else:
                n[action] = model.data[(fbgs, action)].nSimulations
                w[action] = model.data[(fbgs, action)].nWins
            N += n[action]
        uctValues = []
        for action in legalActions:
            uctValue = self.getUCTValue(w[action], n[action], N, c)
            uctValues.append((uctValue, action))
        return uctValues

    def getUCTValue(self, w, n, N, c):
        return w/(n+1.0) + c*sqrt(log(N+1.0)/(n+1.0))
