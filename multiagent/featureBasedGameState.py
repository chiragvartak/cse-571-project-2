# from model import Model
# from pacman import GameState
from util import euclidean_distance, Counter
from util import *
# from typing import List

"""FM: Imported from my own multiAgents.py"""
from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

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

        self.manhattanFood = None

        #[!!!]TODO
        #self.manhattanGhosts = None

        self.wholeKitchenSink = None
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

        self.manhattanFood = self.closestFoodEvalFunction(self.rawGameState)

        tempAction = self.getAction(self, rawGameState)
        self.wholeKitchenSink = self.evaluationFunction(self, rawGameState, tempAction)

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
    def closestFoodEvalFunction(self, rawGameState):
        # Borrowed and modified given boilerplate variables from Q1 evaluation function

        """ [!!!] NEW ADDITION """
        currentGameState = self.rawGameState    

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

    """FM: New Eval Function to track ghosts"""
    #[!!!]TODO

    """FM: Old boilerplate to assist with ghost eval function"""
    def getAction(self, rawGameState):
            """
            You do not need to change this method, but you're welcome to.
            getAction chooses among the BEST OPTIONS according to the evaluation function.
            Just like in the previous project, getAction takes a GameState and returns
            some Directions.X for some X in the set {North, South, West, East, Stop}
            """
            # Collect legal moves and successor states
            """ [!!!] NEW ADDITION """
            gameState = self.rawGameState   

            legalMoves = gameState.getLegalActions()

            # Choose one of the best actions
            scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
            bestScore = max(scores)
            bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
            chosenIndex = random.choice(bestIndices) # Pick randomly among the best

            "Add more of your code here if you want to"

            return legalMoves[chosenIndex]

    """FM: Old boilerplate to assist with ghost eval function"""
    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.
        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where HIGHER numbers are better.
        The code below extracts some useful information from the state, like the
        REMAINING food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.
        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()  # REMAINING food to acquire
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        "*** YOUR CODE HERE ***"
        # (!!!) 
        # REMEMBER: Reflex Agents perform based on the CURRENT percept only. Behavioral rules are static. 
            # Agent seeks out maximum score. 
                # (Move Away If Vulnerable): PENALIZE closing ghosts
                # (Move Toward If Clear or Invulnerable): REWARD food consumption
            # newFood can be converted to list
            # evaluate state-action pairs for evaluation

        # --- FOOD DISTANCE: Distance heuristic for ALL the food pellets ---
        foodDistanceSum = 0
        foodDistanceMIN = MAX
        foodDistanceList = []

        # Calculate total distances of all food
        for remaniningFoodPellet in newFood.asList():
            # Append to list of food distances, update global sum value
            remainingFoodVal = manhattanDistance(remaniningFoodPellet, newPos)
            foodDistanceList.append(remainingFoodVal)
            foodDistanceSum += remainingFoodVal

            # Calculate "rush attract" value to eliminate pacman oscillation
            if remainingFoodVal <= foodDistanceMIN or foodDistanceMIN == MAX:
                foodDistanceMIN = remainingFoodVal

        # --- GHOST DISTANCE: Distance Heuristic for ALL the GHOST Positions respective to PACMAN ---
        ghostDistanceSum = 0
        ghostDistanceMIN = MAX
        ghostDistanceList = []

        # GHOST DISTANCE: Distance Heuristic for Ghost Positions
        ghostDistance = 0
        ghostProximityCount = 0

        # Calculate total distances of all ghosts. Encourage FARTHER AWAY FROM ghosts -> less penalty
        successorGhostPositions = successorGameState.getGhostPositions()
        distanceToClosestGhost = manhattanDistance(newPos, newGhostStates[0].getPosition())

        for ghost in successorGhostPositions:
            # Append to list of ghost distances, update global sum value
            ghostDistance = manhattanDistance(newPos, ghost)
            ghostDistanceList.append(ghostDistance)
            ghostDistanceSum += ghostDistance

            # Calculate closest ghost to ensure Pacman survival
            if ghostDistance <= ghostDistanceMIN or ghostDistanceMIN == MIN:
                ghostDistanceMIN = ghostDistance

            # Calculate number of ghosts that could compromise Pacman
            if ghostDistance <= 1:
                ghostProximityCount += 1

        # --- Primary Evaluation Function Calculations ---
        # Pre-calculated successorGameState to save runtime
        finalScore = successorGameState.getScore()

        # Took into account remaining foodPellets
        if foodDistanceSum != 0:
            finalScore += (12.0/min(foodDistanceList))

        # Took into account distance of closest ghost and promximity of ghosts near Pacman
        # More accurate to take into account distance of SINGLE CLOSEST ghost, as bugs could scale with net ghost distance (each w diff behavior)
        
        # Use of 'or' to consider edge case of eaten ghost that is revived and now hunting for pacman. Pacman must evade, not destroy rest of vulnerable ghosts
        if distanceToClosestGhost > 0 or len(newScaredTimes) == 0:
            finalScore -= (12.0/ float(ghostDistanceMIN)) + ghostProximityCount

        # If Ghosts are scared, ignore and eat pellets like normal
        elif distanceToClosestGhost > 0 and len(newScaredTimes) != 0:
            finalScore += (12.0/min(foodDistanceList))

        return finalScore

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
                self.manhattanFood,
                self.wholeKitchenSink
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
            "manhattanFood": self.manhattanFood,
            "wholeKitchenSink": self.wholeKitchenSink
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

