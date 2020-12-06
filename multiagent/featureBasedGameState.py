import util
from util import euclidean_distance

class FeatureBasedGameState(object):
    def __init__(self, gameState):
        # type: (GameState) -> None

        # Storing the GameState; it might be needed
        self.rawGameState = gameState

        # Please list all the features here. It becomes convenient; don't miss out any, or directly initialise elsewhere
        self.ghostWithin2UnitNorth = None
        self.ghostWithin2UnitWest = None
        self.ghostWithin2UnitSouth = None
        self.ghostWithin2UnitEast = None
        self.ghostWithin1UnitNorth = None
        self.ghostWithin1UnitWest = None
        self.ghostWithin1UnitSouth = None
        self.ghostWithin1UnitEast = None
        self.ghostNorthWest = None
        self.ghostSouthWest = None
        self.ghostSouthEast = None
        self.ghostNorthEast = None
        self.foodNorth = None
        self.foodSouth = None
        self.foodEast = None
        self.foodWest = None
        self.directionToNearestFood = None  # an integer representing the angle from pacman to the nearest food pellet
        self.distanceToNearestFood = None  # an integer; manhattan distance
        self.numberOfFoods = None  # an integer; number of foods remaining
        self.canMoveNorth = None
        self.canMoveWest = None
        self.canMoveSouth = None
        self.canMoveEast = None

        # Caching some stuff for faster calculations - don't change this please!
        # self.closestGhosts = None

        # Some things you might need
        x, y = self.rawGameState.getPacmanPosition()

        # This is where you will calculate the features you have listed above
        pacmanPosition = self.rawGameState.getPacmanPosition()
        self.ghostWithin2UnitNorth = self.doesGhostExist(pacmanPosition, 'North', 2)
        self.ghostWithin2UnitWest = self.doesGhostExist(pacmanPosition, 'West', 2)
        self.ghostWithin2UnitSouth = self.doesGhostExist(pacmanPosition, 'South', 2)
        self.ghostWithin2UnitEast = self.doesGhostExist(pacmanPosition, 'East', 2)
        self.ghostWithin1UnitNorth = self.doesGhostExist(pacmanPosition, 'North', 1)
        self.ghostWithin1UnitWest = self.doesGhostExist(pacmanPosition, 'West', 1)
        self.ghostWithin1UnitSouth = self.doesGhostExist(pacmanPosition, 'South', 1)
        self.ghostWithin1UnitEast = self.doesGhostExist(pacmanPosition, 'East', 1)
        self.ghostNorthWest = (x - 1, y + 1) in self.rawGameState.getGhostPositions()
        self.ghostSouthWest = (x - 1, y - 1) in self.rawGameState.getGhostPositions()
        self.ghostSouthEast = (x + 1, y - 1) in self.rawGameState.getGhostPositions()
        self.ghostNorthEast = (x + 1, y + 1) in self.rawGameState.getGhostPositions()
        # self.foodNorth = self.rawGameState.hasFood(x, y + 1)
        # self.foodSouth = self.rawGameState.hasFood(x, y - 1)
        # self.foodEast = self.rawGameState.hasFood(x + 1, y)
        # self.foodWest = self.rawGameState.hasFood(x - 1, y)    
        
        self.distanceToNearestFood = 99999999
        foods = self.rawGameState.getFood().asList()
        for food in foods:
            distance_to_food = util.manhattanDistance(pacmanPosition, food)
            if distance_to_food < self.distanceToNearestFood:
                self.distanceToNearestFood = distance_to_food
                self.directionToNearestFood = util.getAngle(pacmanPosition, food)
        
        if len(foods) < 5:  # don't worry about the number of foods left until it's very significant
            self.numberOfFoods = len(foods)

        # information about legal actions
        self.canMoveNorth = 'North' in self.rawGameState.getLegalPacmanActions()
        self.canMoveWest = 'West' in self.rawGameState.getLegalPacmanActions()
        self.canMoveSouth = 'South' in self.rawGameState.getLegalPacmanActions()
        self.canMoveEast = 'East' in self.rawGameState.getLegalPacmanActions()


    def findClosestGhosts(self):
        "There can be multiple closest ghosts. So this returns a list of tuples. Eg. [(1,1), (5,4)]"
        # if self.closestGhosts is not None:
        #     return self.closestGhosts
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
        # self.closestGhosts = closestGhosts
        # return self.closestGhosts
        return closestGhosts

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
        return (self.ghostWithin2UnitNorth,
                self.ghostWithin2UnitWest,
                self.ghostWithin2UnitSouth,
                self.ghostWithin2UnitEast,
                self.ghostWithin1UnitNorth,
                self.ghostWithin1UnitWest,
                self.ghostWithin1UnitSouth,
                self.ghostWithin1UnitEast,
                self.ghostNorthWest,
                self.ghostSouthWest,
                self.ghostSouthEast,
                self.ghostNorthEast,
                self.foodNorth,
                self.foodSouth,
                self.foodEast,
                self.foodWest,
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
            "ghostWithin2UnitNorth": self.ghostWithin2UnitNorth,
            "ghostWithin2UnitWest": self.ghostWithin2UnitWest,
            "ghostWithin2UnitSouth": self.ghostWithin2UnitSouth,
            "ghostWithin2UnitEast": self.ghostWithin2UnitEast,
            "ghostWithin1UnitNorth": self.ghostWithin1UnitNorth,
            "ghostWithin1UnitWest": self.ghostWithin1UnitWest,
            "ghostWithin1UnitSouth": self.ghostWithin1UnitSouth,
            "ghostWithin1UnitEast": self.ghostWithin1UnitEast,
            "ghostNorthWest": self.ghostNorthWest,
            "ghostSouthWest": self.ghostSouthWest,
            "ghostSouthEast": self.ghostSouthEast,
            "ghostNorthEast": self.ghostNorthEast,
            "foodNorth": self.foodNorth,
            "foodSouth": self.foodSouth,
            "foodEast": self.foodEast,
            "foodWest": self.foodWest,
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

