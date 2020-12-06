import random
import util

from featureBasedGameState import FeatureBasedGameState
from math import sqrt, log
from model import commonModel
from multiAgents import MultiAgentSearchAgent

class MCTSAgent(MultiAgentSearchAgent):
    def __init__(self, evalFn = 'franksEvaluationFunction', numTraining = '0', isReal = False):
        self.currentGame = 0
        self.numberOfTrainingGames = int(numTraining)
        self.evaluationFunction = util.lookup(evalFn, globals())

        # For testing and analysis, we can toggle a flag that prevents pacman allows pacman to use evalFn in certain cases
        self.use_heuristic = True

    def registerInitialState(self, state):
        self.currentGame += 1
        # print "state\n", state
        # print "type(state)\n", type(state)
        # print "state.__class__.__name__\n", state.__class__.__name__

    def getAction(self, state):
        # type: (GameState) -> str
        fbgs = FeatureBasedGameState(state)
        if self.currentGame <= self.numberOfTrainingGames:
            return self.trainingActionToTake(fbgs, commonModel)
        else:  # This is real game - do the best move!
            return self.realActionToTake(fbgs, commonModel)

    def realActionToTake(self, fbgs, model):
        # print "Choosing real action"
        actionToReturn = None
        actionTuples = []
        for action in fbgs.rawGameState.getLegalActions():
            nSimulations = 0
            nWins = 0
            if (fbgs, action) in model.data:
                nSimulations = model.data[(fbgs, action)].nSimulations
                nWins = model.data[(fbgs, action)].nWins
            actionTuples.append((action, nSimulations, nWins))

        # pick the action that has been visited the most (max nSimulations)
        max_nSimulations = max([actionTuple[1] for actionTuple in actionTuples])
        prunedActionTuples = [actionTuple for actionTuple in actionTuples if actionTuple[1] == max_nSimulations]
        # if there are multiple elements with the max value, pick the one with the max wins
        max_nWins = max([actionTuple[2] for actionTuple in prunedActionTuples])
        prunedActionTuples = [actionTuple for actionTuple in prunedActionTuples if actionTuple[2] == max_nWins]
        
        if len(prunedActionTuples) > 1:
            if self.use_heuristic:
                # print("using heuristic for tiebreak")
                if sum([actionTuple[1] for actionTuple in prunedActionTuples]) == 0:
                    # print("never saw this state in training")
                    # print(fbgs)
                    model.states_you_didnt_see_in_training.append(fbgs)
                actionToReturn = self.getActionFromHeuristic(fbgs.rawGameState, 
                                                            [actionTuple[0] for actionTuple in prunedActionTuples])
            else:
                # if there are still multiple elements with the max wins, pick randomly
                actionToReturn = random.choice(prunedActionTuples)[0]
        else:
            actionToReturn = prunedActionTuples[0][0]

        return actionToReturn

    def trainingActionToTake(self, fbgs, model):
        # type: (FeatureBasedGameState, Model) -> List[(float, str)]
        actionToReturn = None

        w = {}
        n = {}
        N = 0
        c = sqrt(2)
        # c = 0.1  # clamp down exploration?
        legalActions = fbgs.rawGameState.getLegalActions()
        for action in legalActions:
            if (fbgs, action) not in model.data:
                n[action] = 0
                w[action] = 0
            else:
                n[action] = model.data[(fbgs, action)].nSimulations
                w[action] = model.data[(fbgs, action)].nWins
            N += n[action]

        if sum(n.values()) == 0 and self.use_heuristic:
            # You have not won in any of the children. Use an evaluation function to pick the action by weighted value
            actionToReturn = self.getActionByWeight(fbgs.rawGameState)
        else:
        # You have visited at least one of the children. Use UCT to pick the action
            uctValues = []
            for action in legalActions:
                uctValue = self.getUCTValue(w[action], n[action], N, c)
                uctValues.append((uctValue, action))

            # if there are multiple elements with the max value, pick randomly between them
            actionToReturn = random.choice([
                uctValue 
                for uctValue in uctValues 
                    if uctValue[0]==max(uctValues)[0]
                ])[1]

        return actionToReturn

    def getActionByWeight(self, gameState):
        """
        Simulation: ... We can use heuristic knowledge to give larger weights to actions that look more promising.
        """
        values_and_actions = []
        for action in gameState.getLegalActions():
            values_and_actions.append((self.evaluationFunction(gameState.generateSuccessor(0, action)), action))

        # some values could be non-positive; if so, shift all values evenly so that the smallest value is 1
        min_value = min([value_and_action[0] for value_and_action in values_and_actions])
        if min_value <= 0:
            for i in range(len(values_and_actions)):
                values_and_actions[i] = (values_and_actions[i][0]-min_value+1, values_and_actions[i][1])

        # turn values into probabilities based on the sum of your values
        sum_of_values = sum([value_and_action[0] for value_and_action in values_and_actions])
        probabilities_and_actions = [(value_and_action[0]/sum_of_values, value_and_action[1]) for value_and_action in values_and_actions]

        return util.chooseFromDistribution(probabilities_and_actions)

    def getActionFromHeuristic(self, gameState, actions):
        max_value = float("-inf")
        best_action = None
        for action in actions:
            value = self.evaluationFunction(gameState.generateSuccessor(0, action))
            if value > max_value:
                max_value = value
                best_action = action

        return best_action

    def getUCTValue(self, w, n, N, c):
        return w/(n+1.0) + c*sqrt(log(N+1.0)/(n+1.0))


def franksEvaluationFunction(gameState):
    # Useful information you can extract from a GameState (pacman.py)
    newPos = gameState.getPacmanPosition()
    newFood = gameState.getFood()
    newGhostStates = gameState.getGhostStates()
    newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

    FEAR_GHOST_SCALAR = float(100)  # be very afraid of ghosts!
    EAT_FOOD_SCALAR = float(100)  # but also really want food

    # how far away is nearest food? You should get higher score for being nearer
    foods = newFood.asList()
    if foods:
      distance_to_nearest_food = float("inf")
      for food in newFood.asList():
        distance_to_food = util.manhattanDistance(newPos, food)
        if distance_to_food < distance_to_nearest_food:
          distance_to_nearest_food = distance_to_food
    else:
      # if there's no food, this is great because the game is over!
      distance_to_nearest_food = -10000  # game doesnt seem to understand negative infinity, so make it a very large negative number

    # how far away are the ghosts?
    ghost_score = 0
    for ghost in newGhostStates:
      distance_to_ghost = util.manhattanDistance(newPos, ghost.getPosition())

      # you should get a higher score for being further from the ghost
      # but you shouldnt really care about the ghost if it's not in your immediate vicinity
      if distance_to_ghost < 3:
        ghost_score -= FEAR_GHOST_SCALAR/(distance_to_ghost+1)

    # score should be inversely related to distance to food, and negatively correlated with number of food left
    return gameState.getScore() + EAT_FOOD_SCALAR/(len(newFood.asList())+1) + float(1)/distance_to_nearest_food + ghost_score
