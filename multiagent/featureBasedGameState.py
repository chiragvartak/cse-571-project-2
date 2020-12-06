# from model import Model
# from pacman import GameState
from util import euclidean_distance, Counter
from util import *
# from typing import List

class FeatureBasedGameState(object):
    def __init__(self, gameState):
        # type: (GameState) -> None

        # Storing the GameState; it might be needed
        self.rawGameState = gameState

        """-------------------------------------------------------------------------------------------------------------------------------"""
        """ [!!!] Area to change """
        # Please list all the features here. It becomes convenient; don't miss out any, or directly initialise elsewhere
        """FM: Good features to have; reflexive evasion of ghosts"""
        self.ghostWithin2UnitNorth = None
        self.ghostWithin2UnitWest = None
        self.ghostWithin2UnitSouth = None
        self.ghostWithin2UnitEast = None
        self.ghostNorthWest = None
        self.ghostSouthWest = None
        self.ghostSouthEast = None
        self.ghostNorthEast = None

        """FM: Bad set of features, need """
        #self.foodNorth = None
        #self.foodSouth = None
        #self.foodEast = None
        #self.foodWest = None

        self.closestFood = None
        """-------------------------------------------------------------------------------------------------------------------------------"""

        # Caching some stuff for faster calculations - don't change this please!
        self.closestGhosts = None

        # Some things you might need
        x, y = self.rawGameState.getPacmanPosition()

        """-------------------------------------------------------------------------------------------------------------------------------"""
        """ [!!!] Area to change """
        # This is where you will calculate the features you have listed above
        pacmanPosition = self.rawGameState.getPacmanPosition()
        self.ghostWithin2UnitNorth = self.doesGhostExist(pacmanPosition, 'North', 1) or self.doesGhostExist(pacmanPosition, 'North', 2)
        self.ghostWithin2UnitWest = self.doesGhostExist(pacmanPosition, 'West', 1) or self.doesGhostExist(pacmanPosition, 'West', 2)
        self.ghostWithin2UnitSouth = self.doesGhostExist(pacmanPosition, 'South', 1) or self.doesGhostExist(pacmanPosition, 'South', 2)
        self.ghostWithin2UnitEast = self.doesGhostExist(pacmanPosition, 'East', 1) or self.doesGhostExist(pacmanPosition, 'East', 2)
        self.ghostNorthWest = (x - 1, y + 1) in self.rawGameState.getGhostPositions()
        self.ghostSouthWest = (x - 1, y - 1) in self.rawGameState.getGhostPositions()
        self.ghostSouthEast = (x + 1, y - 1) in self.rawGameState.getGhostPositions()
        self.ghostNorthEast = (x + 1, y + 1) in self.rawGameState.getGhostPositions()

        """FM: Install manhattan distance/heuristic calculation of closest food pellet here"""
        #self.foodNorth = self.rawGameState.hasFood(x, y + 1)
        #self.foodSouth = self.rawGameState.hasFood(x, y - 1)
        #self.foodEast = self.rawGameState.hasFood(x + 1, y)
        #self.foodWest = self.rawGameState.hasFood(x - 1, y)

        self.closestFood = closestFoodEvalFunction(self.rawGameState)

        """-------------------------------------------------------------------------------------------------------------------------------"""

    def findClosestGhosts(self):
        "There can be multiple closest ghosts. So this returns a list of tuples. Eg. [(1,1), (5,4)]"
        if self.closestGhosts is not None:
            return self.closestGhosts
        pacmanPosition = self.rawGameState.getPacmanPosition()
        ghostPositions = self.rawGameState.getGhostPositions()
        minDistance = 999999999
        closestGhosts = []
        for ghostPosition in ghostPositions:
            ghostDistance = euclidean_distance(pacmanPosition, ghostPosition)
            if ghostDistance < minDistance:
                closestGhosts = [ghostPosition]
                minDistance = ghostDistance
            elif ghostDistance == minDistance:  # TODO: this might be problematic - floating point equality comparison
                closestGhosts.append(ghostPosition)
        self.closestGhosts = closestGhosts
        return self.closestGhosts

    def doesGhostExist(self, currentPos, direction, distance):
        "Find if a ghost exists in a certain direction from the given position: doesGhostExist((2,3), 'North', 1)"
        closestGhosts = self.findClosestGhosts()
        x, y = currentPos
        if direction == 'North':
            return (x, y+distance) in closestGhosts
        elif direction == 'West':
            return (x-distance, y) in closestGhosts
        elif direction == 'South':
            return (x, y-distance) in closestGhosts
        elif direction == 'East':
            return (x+distance, y) in closestGhosts
        else:
            raise Exception("You have provided an invalid direction: ", direction)

    """FM: My old eval function from project 2"""
    def closestFoodEvalFunction(currentGameState):
        # Borrowed and modified given boilerplate variables from Q1 evaluation function
        pacmanPosition = currentGameState.getPacmanPosition()
        foodPosition = currentGameState.getFood().asList()
        foodSum = 0

        # Took the sum of manhattan distances from all remaining food
        for food in foodPosition:
            foodSum += manhattanDistance(pacmanPosition, food)

        # Returns if Pacman has eaten ALL food capsules 
        if foodSum == 0:
            return currentGameState.getScore()

        # If food still remains on the map, return updated current score
        else:
            # (>>>) Converted to float to prevent unnecessary truncation, which caused failing test cases
            return currentGameState.getScore() + 400.0/foodSum

    """-------------------------------------------------------------------------------------------------------------------------------"""
    """ [!!!] Area to change """

    #Include all features here so you can hash properly
    def __key(self):
        return (self.ghostWithin2UnitNorth,
                self.ghostWithin2UnitWest,
                self.ghostWithin2UnitSouth,
                self.ghostWithin2UnitEast,
                self.ghostNorthWest,
                self.ghostSouthWest,
                self.ghostSouthEast,
                self.ghostNorthEast,
                self.closestFood
                #self.foodNorth,
                #self.foodSouth,
                #self.foodEast,
                #self.foodWest
                )
    """-------------------------------------------------------------------------------------------------------------------------------"""

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, FeatureBasedGameState):
            return self.__key() == other.__key()
        return NotImplemented

    """-------------------------------------------------------------------------------------------------------------------------------"""
    """ [!!!] Area to change """
    #Incorporate all features for metadata + debugging's sake
    def __repr__(self):
        return str({
            "ghostWithin2UnitNorth": self.ghostWithin2UnitNorth,
            "ghostWithin2UnitWest": self.ghostWithin2UnitWest,
            "ghostWithin2UnitSouth": self.ghostWithin2UnitSouth,
            "ghostWithin2UnitEast": self.ghostWithin2UnitEast,
            "ghostNorthWest": self.ghostNorthWest,
            "ghostSouthWest": self.ghostSouthWest,
            "ghostSouthEast": self.ghostSouthEast,
            "ghostNorthEast": self.ghostNorthEast,
            "closestFood": self.closestFood
            #"foodNorth": self.foodNorth,
            #"foodSouth": self.foodSouth,
            #"foodEast": self.foodEast,
            #"foodWest": self.foodWest
        })
    """-------------------------------------------------------------------------------------------------------------------------------"""

# Some utility functions that I require, I am putting here
def _getSuccessorsAtDepth(gameState, agentIndex, depth):
    # type: (GameState, int, int) -> List[GameState]
    immediateSuccessors = [gameState.generateSuccessor(agentIndex, action) for action
                           in gameState.getLegalActions(agentIndex)]
    if depth == 1:
        return immediateSuccessors
    nAgents = gameState.getNumAgents()
    successors = []
    for successor in immediateSuccessors:
        successors += _getSuccessorsAtDepth(successor, (agentIndex+1)%nAgents, depth-1)
    return successors


def getActionSuccessorPairs(gameState):
    # type: (GameState) -> List[(str, GameState)]
    nAgents = gameState.getNumAgents()
    legalActions = gameState.getLegalPacmanActions()
    actionSuccessorPairs = []
    for action in legalActions:
        nextGameState = gameState.generatePacmanSuccessor(action)
        actionSuccessorPairs.append([(action, successor) for successor
                                     in _getSuccessorsAtDepth(nextGameState, 1, nAgents-1)])
    print "There are", len(actionSuccessorPairs), "actionSuccessorPairs"
    return actionSuccessorPairs

def isFullyExplored(gameState, model):
    # type: (GameState, Model) -> (bool, str)
    actionSuccessorPairs = getActionSuccessorPairs(gameState)
    actionVsNUnvisited = {}
    actionVsNTotal = {}
    for action, successor in actionSuccessorPairs:
        fbgs = FeatureBasedGameState(gameState)
        if (fbgs, action) not in model:
            if action not in actionVsNUnvisited:
                actionVsNUnvisited[action] = 1
            else:
                actionVsNUnvisited[action] += 1
        if action not in actionVsNTotal:
            actionVsNTotal[action] = 1
        else:
            actionVsNTotal[action] += 1
    if len(actionVsNUnvisited) == 0:
        return (True, None)
    bestAction = None
    highestProbabilityOfVisitingUnvisitedState = 0.0
    for action, nUnvisited in actionVsNUnvisited.items():
        probabilityOfVisitingUnvisitedState = actionVsNUnvisited[action] / actionVsNTotal[action]
        if probabilityOfVisitingUnvisitedState > highestProbabilityOfVisitingUnvisitedState:
            highestProbabilityOfVisitingUnvisitedState = probabilityOfVisitingUnvisitedState
            bestAction = action
    return (False, bestAction)

