# multiAgents.py
# --------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
  """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
  """


  def getAction(self, gameState):
    """
    You do not need to change this method, but you're welcome to.

    getAction chooses among the best options according to the evaluation function.

    Just like in the previous project, getAction takes a GameState and returns
    some Directions.X for some X in the set {North, South, West, East, Stop}
    """
    # Collect legal moves and successor states
    legalMoves = gameState.getLegalActions()

    # Choose one of the best actions
    scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
    bestScore = max(scores)
    bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
    chosenIndex = random.choice(bestIndices) # Pick randomly among the best

    "Add more of your code here if you want to"

    return legalMoves[chosenIndex]

  def evaluationFunction(self, currentGameState, action):
    """
    Design a better evaluation function here.

    The evaluation function takes in the current and proposed successor
    GameStates (pacman.py) and returns a number, where higher numbers are better.

    The code below extracts some useful information from the state, like the
    remaining food (newFood) and Pacman position after moving (newPos).
    newScaredTimes holds the number of moves that each ghost will remain
    scared because of Pacman having eaten a power pellet.

    Print out these variables to see what you're getting, then combine them
    to create a masterful evaluation function.
    """
    # Useful information you can extract from a GameState (pacman.py)
    successorGameState = currentGameState.generatePacmanSuccessor(action)
    newPos = successorGameState.getPacmanPosition()
    newFood = successorGameState.getFood()
    newGhostStates = successorGameState.getGhostStates()
    newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

    "*** YOUR CODE HERE ***"
    """
    newPos: (x, y) -- (1, 1) at lower left corner. (0, 0) is the wall at lower left.
    newFood: A 2D array where food[x][y] is True if there is a food pellet at (x, y).
    newGhostStates: a list of ghost AgentState objects with instance variables:
                  start: startConfiguration           #initial configuration
                  configuration: pos = (x,y),         #represents current pos + dir
                                 direction = Directions.X (NORTH, SOUTH, STOP, etc.)
                  isPacman: True or False
                  scaredTimer = integer
    newScaredTimes: a list of scaredTimers extracted from Ghost States
    """

    # Our scoring will be done as follows:
    # k1 * foodScore + k2 * ghostScore
    foodScore = 0
    ghostScore = 0
    noMovePenalty = 0

    currentPos = currentGameState.getPacmanPosition()
    currentFood = currentGameState.getFood()
    currentFoodList = currentFood.asList()

    # debug
    """
    print "Position: ", newPos
    print "Food: ", newFood, "Food at (3,1)? ", newFood[3][1]
    print "Ghost states: ", newGhostStates
    print "newScaredTimes: ", newScaredTimes
    """
    
    # Calculate distance to closest food, unless we eat a food pellet
    # in the next state
    newFoodList = newFood.asList()
    distToClosestFood = 1000.0
    if len(newFoodList) < len(currentFoodList):
      foodScore = 4   # adjust
    else:
      if newFoodList:
        for food in newFoodList:
          dist = abs(newPos[0] - food[0]) + abs(newPos[1] - food[1])
          if dist < distToClosestFood:
            distToClosestFood = dist
      else:
        distToClosestFood = 0.5
      foodScore = 1.0 / distToClosestFood # adjust

    # Calculate distance to closest ghost and the rest of the ghosts
    distToClosestGhost = 1000.0
    distToRestOfGhosts = 1000.0
    if newGhostStates:
      for ghostState in newGhostStates:
        ghostPos = ghostState.configuration.pos
        dist = abs(newPos[0] - ghostPos[0]) + abs(newPos[1] - ghostPos[1])
        if dist < distToClosestGhost:
          distToClosestGhost = dist
          # TODO: calculate the distances to rest of the ghosts
    #else:
      # distToClosestGhost = 1000.0
    if distToClosestGhost == 0:
      distToClosestGhost = 0.03125
    ghostScore = 1.0 / distToClosestGhost # adjust

    # penalize Pacman for not moving
    if currentPos == newPos:
      noMovePenalty = 10 # adjust

    # Make Pacman move toward ghosts if they're scared.
    # Pacman will probably get owned if he faces multiple ghosts
    # since he'll move toward the closest ghost if at least one of
    # them is scared.
    totalScaredTime = 0
    for scaredTime in newScaredTimes:
      totalScaredTime += scaredTime
    if totalScaredTime > 0:
      ghostScore = ghostScore * (- totalScaredTime / 10) 
      
    # debug
#    print "foodScore: ", 50 * foodScore
#    print "ghostScore: ", 25 * ghostScore
#    print "****total score****: ", 50 * foodScore - 25 * ghostScore    
    
    return 50 * foodScore - (25 * ghostScore) - noMovePenalty 
    #return successorGameState.getScore()

def scoreEvaluationFunction(currentGameState):
  """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
  """
  return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
  """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
  """

  def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
    self.index = 0 # Pacman is always agent index 0
    self.evaluationFunction = util.lookup(evalFn, globals())
    self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
  """
    Your minimax agent (question 2)
  """

  def getAction(self, gameState):
    """
      Returns the minimax action from the current gameState using self.depth
      and self.evaluationFunction.

      Here are some method calls that might be useful when implementing minimax.

      gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

      Directions.STOP:
        The stop direction, which is always legal

      gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

      gameState.getNumAgents():
        Returns the total number of agents in the game
    """
    "*** YOUR CODE HERE ***"

    v = self.maxValue(gameState, self.depth)

    actions = gameState.getLegalActions(0)
    for action in actions:
      successor = gameState.generateSuccessor(0, action)
      if v == self.evaluationFunction(successor):
        return action
    return None
    """
    for agentIndex in range(0, gameState.getNumAgents()):  
        # pacman
        if agentIndex == 0:
          highestScore = -1000
          highestAction = None
          actions = gameState.getLegalActions(0)
          for action in actions:
            successor = gameState.generateSuccessor(0, action)
            if successor.isWin():
              return action
            if successor.isLose():
              continue
            #score = self.evaluationFunction(successor)
            if score > highestScore:
              highestScore = score
              highestAction = action
          return highestAction
    """
    print "Nooooo"
    util.raiseNotDefined()

  def maxValue(self, gameState, depth):
    if gameState.isWin():
      return self.evaluationFunction(gameState)
    if gameState.isLose():
      return self.evaluationFunction(gameState)
    v = -1000
    actions = gameState.getLegalActions(0)
    for action in actions:
      successor = gameState.generateSuccessor(0, action)
      v = max(v, self.minValue(successor, depth, 1))
    return v

  def minValue(self, gameState, depth, agentIndex):
    if gameState.isWin():
      return self.evaluationFunction(gameState)
    if gameState.isLose():
      return self.evaluationFunction(gameState)

    numAgents = gameState.getNumAgents()
    if depth == 0 and agentIndex == numAgents-1:
      return self.evaluationFunction(gameState)

    v = 1000
    actions = gameState.getLegalActions(agentIndex)
    for action in actions:
      successor = gameState.generateSuccessor(agentIndex, action)
      if agentIndex < numAgents-1:
        v = min(v, self.minValue(successor, depth, agentIndex+1))
      else:
        v = min(v, self.maxValue(successor, depth-1))
    return v
    
class AlphaBetaAgent(MultiAgentSearchAgent):
  """
    Your minimax agent with alpha-beta pruning (question 3)
  """

  def getAction(self, gameState):
    """
      Returns the minimax action using self.depth and self.evaluationFunction
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()

class ExpectimaxAgent(MultiAgentSearchAgent):
  """
    Your expectimax agent (question 4)
  """

  def getAction(self, gameState):
    """
      Returns the expectimax action using self.depth and self.evaluationFunction

      All ghosts should be modeled as choosing uniformly at random from their
      legal moves.
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()

def betterEvaluationFunction(currentGameState):
  """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
  """
  "*** YOUR CODE HERE ***"
  util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction

class ContestAgent(MultiAgentSearchAgent):
  """
    Your agent for the mini-contest
  """

  def getAction(self, gameState):
    """
      Returns an action.  You can use any method you want and search to any depth you want.
      Just remember that the mini-contest is timed, so you have to trade off speed and computation.

      Ghosts don't behave randomly anymore, but they aren't perfect either -- they'll usually
      just make a beeline straight towards Pacman (or away from him if they're scared!)
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()

