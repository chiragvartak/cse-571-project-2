import util
from util import euclidean_distance

class FeatureBasedGameState(object):
    def __init__(self, gameState):
        # type: (GameState) -> None

        # Storing the GameState; it might be needed
        self.rawGameState = gameState

        # Please list all the features here. It becomes convenient; don't miss out any, or directly initialise elsewhere
        self.directionToNearestGhost = None  # an integer; manhattan distance
        self.distanceToNearestGhost = None  # an integer representing the angle from pacman to the nearest ghost
        self.nearestGhostEdible = None  # is the nearest ghost scared? Is he scared for long enough for you to eat him if you get to him?
        self.directionToNearestFood = None  # an integer representing the angle from pacman to the nearest food pellet
        self.distanceToNearestFood = None  # an integer; manhattan distance
        self.numberOfFoods = None  # an integer; number of foods remaining
        self.canMoveNorth = None
        self.canMoveWest = None
        self.canMoveSouth = None
        self.canMoveEast = None

        # Caching some stuff for faster calculations - don't change this please!
        self.closestGhosts = None

        # This is where you will calculate the features you have listed above
        pacmanPosition = self.rawGameState.getPacmanPosition()
        
        self.distanceToNearestGhost = 99999999
        for ghost in self.findClosestGhosts():
            distance_to_ghost = util.manhattanDistance(pacmanPosition, ghost)
            if distance_to_ghost < self.distanceToNearestGhost:
                self.distanceToNearestGhost = distance_to_ghost
                # self.directionToNearestGhost = util.getAngle(pacmanPosition, ghost, round_to_nearest=45)
                self.directionToNearestGhost = util.getDominantDirection(pacmanPosition, ghost)

        if self.distanceToNearestGhost > 5:  # don't worry about the distance to ghost if it's more than 5 away
            self.distanceToNearestGhost = None

        self.nearestGhostEdible = None  # TODO: implement later
        
        self.distanceToNearestFood = 99999999
        foods = self.rawGameState.getFood().asList()
        for food in foods:
            distance_to_food = util.manhattanDistance(pacmanPosition, food)
            if distance_to_food < self.distanceToNearestFood:
                self.distanceToNearestFood = distance_to_food
                # self.directionToNearestFood = util.getAngle(pacmanPosition, food, round_to_nearest=45)
                self.directionToNearestFood = util.getDominantDirection(pacmanPosition, food)

        if self.distanceToNearestFood > 1:
            self.distanceToNearestFood = -1  # use this value to denote a food outside the range of immediate relevance
        
        if len(foods) < 5:  # don't worry about the number of foods left until it's very significant
            self.numberOfFoods = len(foods)

        # information about legal actions
        self.canMoveNorth = 'North' in self.rawGameState.getLegalPacmanActions()
        self.canMoveWest = 'West' in self.rawGameState.getLegalPacmanActions()
        self.canMoveSouth = 'South' in self.rawGameState.getLegalPacmanActions()
        self.canMoveEast = 'East' in self.rawGameState.getLegalPacmanActions()


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

    def __key(self):
        return (self.directionToNearestGhost,
                self.distanceToNearestGhost,
                self.nearestGhostEdible,
                self.directionToNearestFood,
                self.distanceToNearestFood,
                self.numberOfFoods,
                self.canMoveNorth,
                self.canMoveWest,
                self.canMoveSouth,
                self.canMoveEast
                )

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, FeatureBasedGameState):
            return self.__key() == other.__key()
        return NotImplemented

    def __repr__(self):
        return str({
            "directionToNearestGhost": self.directionToNearestGhost,
            "distanceToNearestGhost": self.distanceToNearestGhost,
            "nearestGhostEdible": self.nearestGhostEdible,
            "directionToNearestFood": self.directionToNearestFood,
            "distanceToNearestFood": self.distanceToNearestFood,
            "numberOfFoods": self.numberOfFoods,
            "canMoveNorth": self.canMoveNorth,
            "canMoveWest": self.canMoveWest,
            "canMoveSouth": self.canMoveSouth,
            "canMoveEast": self.canMoveEast
        })


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

