# from model import Model
# from pacman import GameState
from util import euclidean_distance
# from typing import List
import searchAgents
import search

class FeatureBasedGameState(object):
    def __init__(self, gameState):
        # type: (GameState) -> None

        # Storing the GameState; it might be needed
        self.rawGameState = gameState

        # Please list all the features here. It becomes convenient; don't miss out any, or directly initialise elsewhere
        self.moveToClosestFood = None
        self.ghostWithin1UnitOfClosestFoodDirectionPoint = None
        self.ghostOnClosestFoodDirectionPoint = None
        self.moveToClosestCapsule = None
        self.ghostWithin1UnitOfClosestCapsuleDirectionPoint = None
        self.ghostOnClosestCapsuleDirectionPoint = None
        self.canMoveNorth = None
        self.canMoveWest = None
        self.canMoveSouth = None
        self.canMoveEast = None

        # Caching some stuff for faster calculations - don't change this please!
        self.ghostStartPositions = None
        self.closestGhosts = None
        self.closestCapsules = None
        self.scaredGhosts = None
        self.unscaredGhosts = None
        self.legalActions = self.rawGameState.getLegalPacmanActions()
        self.sequenceOfMovesToClosestGhost = None
        self.sequenceOfMovesToClosestCapsule = None
        self.sequenceOfMovesToClosestEdibleGhost = None
        self.ghostPositions = self.rawGameState.getGhostPositions()

        # This is where you will calculate the features you have listed above
        self.moveToClosestFood = self.getMoveToClosestFood()
        self.ghostWithin1UnitOfClosestFoodDirectionPoint = self.isGhostWithin1UnitOfDirectionPoint(self.moveToClosestFood)
        self.ghostOnClosestFoodDirectionPoint = self.isGhostOnDirectionPoint(self.moveToClosestFood)
        self.moveToClosestCapsule = self.getMoveToClosestCapsule()
        self.ghostWithin1UnitOfClosestCapsuleDirectionPoint = self.isGhostWithin1UnitOfDirectionPoint(self.moveToClosestCapsule)
        self.ghostOnClosestCapsuleDirectionPoint = self.isGhostOnDirectionPoint(self.moveToClosestCapsule)
        self.canMoveNorth = 'North' in self.rawGameState.getLegalPacmanActions()
        self.canMoveWest = 'West' in self.rawGameState.getLegalPacmanActions()
        self.canMoveSouth = 'South' in self.rawGameState.getLegalPacmanActions()
        self.canMoveEast = 'East' in self.rawGameState.getLegalPacmanActions()

    def isGhostWithin1UnitOfDirectionPoint(self, directionPoint):
        if not directionPoint:
            return None
        x, y = self.rawGameState.getPacmanPosition()
        closestFoodMovePoint = None
        if directionPoint == "North":
            closestFoodMovePoint = (x, y+1)
        elif directionPoint == "South":
            closestFoodMovePoint = (x, y-1)
        elif directionPoint == "East":
            closestFoodMovePoint = (x+1, y)
        elif directionPoint == "West":
            closestFoodMovePoint = (x-1, y)
        else:
            raise Exception("Invalid move " + str(directionPoint))

        x, y = closestFoodMovePoint

        unscaredGhostStates = self.findUnscaredGhostStates()
        if unscaredGhostStates:
            unscaredGhostPositions = [state.getPosition() for state in self.findUnscaredGhostStates()]
            # Check if ghost is present in any of the adjacent positions
            intersection = {(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)} & set(unscaredGhostPositions)
        else:
            unscaredGhostPositions = None
            intersection = []
        return len(intersection) > 0

    def isGhostOnDirectionPoint(self, directionPoint):
        if not directionPoint:
            return None
        x, y = self.rawGameState.getPacmanPosition()
        closestFoodMovePoint = None
        if directionPoint == "North":
            closestFoodMovePoint = (x, y+1)
        elif directionPoint == "South":
            closestFoodMovePoint = (x, y-1)
        elif directionPoint == "East":
            closestFoodMovePoint = (x+1, y)
        elif directionPoint == "West":
            closestFoodMovePoint = (x-1, y)
        else:
            raise Exception("Invalid move " + str(directionPoint))

        x, y = closestFoodMovePoint

        unscaredGhostStates = self.findUnscaredGhostStates()
        if unscaredGhostStates:
            unscaredGhostPositions = [state.getPosition() for state in self.findUnscaredGhostStates()]
            # Check if ghost is present on the direction point
            intersection = {(x, y)} & set(unscaredGhostPositions)
        else:
            unscaredGhostPositions = None
            intersection = []
        return len(intersection) > 0

    def isPacmanWithin1UnitOfGhostRespawn(self):
        # you should only care about this if there are scared ghosts at the moment
        if not self.scaredGhosts:
            return 0
        x, y = self.rawGameState.getPacmanPosition()
        intersection = {(x, y), (x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)} & set(self.findGhostStartPositions())
        return len(intersection) > 0

    def findGhostStartPositions(self):
        if self.ghostStartPositions is not None:
            return self.ghostStartPositions
        ghostStartPositions = [state.start.pos for state in self.rawGameState.getGhostStates()]
        if not ghostStartPositions:
            ghostStartPositions = None  # turn empty list into None
        self.ghostStartPositions = ghostStartPositions
        return ghostStartPositions

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

    def findClosestCapsules(self):
        "There can be multiple closest powers. So this returns a list of tuples. Eg. [(1,1), (5,4)]"
        if self.closestCapsules is not None:
            return self.closestCapsules
        pacmanPosition = self.rawGameState.getPacmanPosition()
        capsulePositions = self.rawGameState.getCapsules()
        minDistance = 999999999
        closestCapsules = []
        for capsulePosition in capsulePositions:
            capsuleDistance = euclidean_distance(pacmanPosition, capsulePosition)
            if capsuleDistance < minDistance:
                closestCapsules = [capsulePosition]
                minDistance = capsuleDistance
            elif capsuleDistance == minDistance:  # TODO: this might be problematic - floating point equality comparison
                closestCapsules.append(capsulePosition)
        if not closestCapsules:
            closestCapsules = None  # turn empty list into None
        self.closestCapsules = closestCapsules
        return self.closestCapsules

    def findScaredGhostStates(self):
        "There can be multiple scared ghosts. So this returns a list of tuples. Eg. [(1,1), (5,4)]"
        if self.scaredGhosts is not None:
            return self.scaredGhosts
             
        scaredGhosts = [state for state in self.rawGameState.getGhostStates() if state.scaredTimer]
        if not scaredGhosts:
            scaredGhosts = None  # turn empty list into None
        self.scaredGhosts = scaredGhosts
        return self.scaredGhosts

    def findUnscaredGhostStates(self):
        "There can be multiple unscared ghosts. So this returns a list of tuples. Eg. [(1,1), (5,4)]"
        if self.unscaredGhosts is not None:
            return self.unscaredGhosts
             
        unscaredGhosts = [state for state in self.rawGameState.getGhostStates() if state.scaredTimer < 1]
        if not unscaredGhosts:
            unscaredGhosts = None  # turn empty list into None
        self.unscaredGhosts = unscaredGhosts
        return self.unscaredGhosts

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
        return (
            self.moveToClosestFood,
            self.ghostWithin1UnitOfClosestFoodDirectionPoint,
            self.ghostOnClosestFoodDirectionPoint,
            self.moveToClosestCapsule,
            self.ghostWithin1UnitOfClosestCapsuleDirectionPoint,
            self.ghostOnClosestCapsuleDirectionPoint,
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
            "moveToClosestFood": self.moveToClosestFood,
            "ghostWithin1UnitOfClosestFoodDirectionPoint": self.ghostWithin1UnitOfClosestFoodDirectionPoint,
            "ghostOnClosestFoodDirectionPoint": self.ghostOnClosestFoodDirectionPoint,
            "moveToClosestCapsule": self.moveToClosestCapsule,
            "ghostWithin1UnitOfClosestCapsuleDirectionPoint": self.ghostWithin1UnitOfClosestCapsuleDirectionPoint,
            "ghostOnClosestCapsuleDirectionPoint": self.ghostOnClosestCapsuleDirectionPoint,
            "canMoveNorth": self.canMoveNorth,
            "canMoveWest": self.canMoveWest,
            "canMoveSouth": self.canMoveSouth,
            "canMoveEast": self.canMoveEast
        })

    def getMoveToClosestFood(self):
        problem = searchAgents.AnyFoodSearchProblem(self.rawGameState)
        # sequenceOfActions = search.aStarSearch(problem, heuristic=searchAgents.util.manhattanDistance)
        sequenceOfActions = search.aStarSearch(problem)
        return sequenceOfActions[0]

    def getMoveToClosestGhost(self):
        closestGhostPosition = self.findClosestGhosts()[0]
        problem = searchAgents.PositionSearchProblem(self.rawGameState, goal=closestGhostPosition, warn=False, visualize=False)
        sequenceOfActions = search.aStarSearch(problem)
        self.sequenceOfMovesToClosestGhost = sequenceOfActions
        return sequenceOfActions[0]

    def getMoveToClosestCapsule(self):
        closestCapsules = self.findClosestCapsules()
        if not closestCapsules:
            return None
        closestCapsulePosition = closestCapsules[0]
        problem = searchAgents.PositionSearchProblem(self.rawGameState, goal=closestCapsulePosition, warn=False, visualize=False)
        sequenceOfActions = search.aStarSearch(problem)
        self.sequenceOfMovesToClosestCapsule = sequenceOfActions
        if not sequenceOfActions:
            return None
        return sequenceOfActions[0]

    def __getstate__(self):
        return (
            self.moveToClosestFood,
            self.ghostWithin1UnitOfClosestFoodDirectionPoint,
            self.ghostOnClosestFoodDirectionPoint,
            self.moveToClosestCapsule,
            self.ghostWithin1UnitOfClosestCapsuleDirectionPoint,
            self.ghostOnClosestCapsuleDirectionPoint,
            self.canMoveNorth,
            self.canMoveWest,
            self.canMoveSouth,
            self.canMoveEast
            )

    def __setstate__(self, state):
        self.moveToClosestFood = state[0]
        self.ghostWithin1UnitOfClosestFoodDirectionPoint = state[1]
        self.ghostOnClosestFoodDirectionPoint = state[2]
        self.moveToClosestCapsule = state[3]
        self.ghostWithin1UnitOfClosestCapsuleDirectionPoint = state[4]
        self.ghostOnClosestCapsuleDirectionPoint = state[5]
        self.canMoveNorth = state[6]
        self.canMoveWest = state[7]
        self.canMoveSouth = state[8]
        self.canMoveEast = state[9]

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

