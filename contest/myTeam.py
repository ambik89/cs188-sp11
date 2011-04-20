# myTeam.py
# ---------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util
from game import Directions
import game
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'BlitzTopAgent', second = 'BlitzBottomAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  agent1 = eval(first)(firstIndex)
  agent2 = eval(second)(secondIndex)
  agent1.setOtherAgent(agent2)
  agent2.setOtherAgent(agent1)
  return [agent1, agent2]

##########
# Agents #
##########

class DummyAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on). 
    
    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    ''' 
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py. 
    '''
    CaptureAgent.registerInitialState(self, gameState)

    ''' 
    Your initialization code goes here, if you need any.
    '''

  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)

    ''' 
    You should change this in your own agent.
    '''

    return random.choice(actions)


class ReflexCaptureAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on). 
    
    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    ''' 
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py. 
    '''
    CaptureAgent.registerInitialState(self, gameState)

    ''' 
    Your initialization code goes here, if you need any.
    '''
    if self.red:
      self.agentsOnTeam = gameState.getRedTeamIndices()
    else:
      self.agentsOnTeam = gameState.getBlueTeamIndices()

    self.setTarget(gameState)
  
  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)

    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    return random.choice(bestActions)

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}

  def setOtherAgent(self, other):
    self.otherAgent = other

  def getMyPos(self, gameState):
    return gameState.getAgentState(self.index).getPosition()

  def isAtHome(self, gameState):
    return not gameState.getAgentState(self.index).isPacman

  def getOpponentPositions(self, gameState):
    # might want to implement inference to store the most likely position
    # if the enemy position can't be detected (is None)
    opponentPositions = []
    for opponentIndex in self.getOpponents(gameState):
      pos = gameState.getAgentPosition(opponentIndex)
      if pos != None:
        opponentPositions.append((opponentIndex,pos))
    return opponentPositions

  def getDistToClosestCapsule(self, gameState):
    myPos = self.getMyPos(gameState)
    capsuleList = self.getCapsules(gameState)
    minDistance = 0
    if len(capsuleList) > 0:
      minDistance = min([self.getMazeDistance(myPos, capsule) for capsule in capsuleList])
    return minDistance

  def getMyScaredTimer(self, gameState):
    return gameState.getAgentState(self.index).scaredTimer
    
class BlitzAgent(ReflexCaptureAgent):
  def chooseAction(self, gameState):
    evalmode = 'offense'
    # For now, just do the same thing as OFFENSE unless if we can detect
    # the enemy. Later we probably want to infer the position of the enemy...
    myPos = self.getMyPos(gameState)
    opponentPositions = self.getOpponentPositions(gameState)
    
    if len(opponentPositions) > 0:
      # do minimax here?
      # for now, go defense mode if close enough
      for index, pos in opponentPositions:
        if self.getMazeDistance(myPos, pos) < 6 and self.isAtHome(gameState):
          evalmode = 'defense'
          break
    
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)
    
    # You can profile your evaluation time by uncommenting these lines
    #start = time.time()
    values = [self.evaluate(gameState, a, evalmode) for a in actions]
    #print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    return random.choice(bestActions)

  def evaluate(self, gameState, action, mode = 'offense'):
    """
    Computes a linear combination of features and feature weights
    """
    if mode == 'offense':
      features = self.getFeaturesOffense(gameState, action)
      weights = self.getWeightsOffense(gameState, action)
    elif mode == 'defense':
      features = self.getFeaturesDefense(gameState, action)
      weights = self.getWeightsDefense(gameState, action)
    else:
      print "UNDEFINED MODE: ", mode
      return 0
    return features * weights

  def getFeaturesDefense(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myPos = self.getMyPos(successor)

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      min_dist = min(dists)
      features['invaderDistance'] = min_dist
      if min_dist <= 1 and self.getMyScaredTimer(successor) > 0 and self.isAtHome():
        features['suicide'] = 1

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    return features
  
  def getWeightsDefense(self, gameState, action):
    return {'numInvaders': -1000, 'invaderDistance': -10, 'stop': -100, 'reverse': -2, 'suicide': -5000}
  
  def getFeaturesOffense(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)

    myPos = self.getMyPos(successor)

    # Compute distance to the nearest food
    foodList = self.getFood(successor).asList()
    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance

    # Compute distance to partner
    if not self.isAtHome(successor):
      agentsList = self.agentsOnTeam
      if self.index == self.agentsOnTeam[0]:
        otherAgentIndex = self.agentsOnTeam[1]
      else:
        otherAgentIndex = self.agentsOnTeam[0]
        otherPos = successor.getAgentState(otherAgentIndex).getPosition()
        distanceToAgent = self.getMazeDistance(myPos, otherPos)
        if distanceToAgent == 0: distanceToAgent = 0.5
        features['distanceToOther'] = 1.0 / distanceToAgent

    # Compute distance to enemy (if detected)
    opponentPositions = self.getOpponentPositions(successor)
    if len(opponentPositions) > 0:
      # if we're in here, we're threatened
      min_dist = 10000
      min_index = None
      
      for index, pos in opponentPositions:
        dist = self.getMazeDistance(myPos, pos)
        if dist < min_dist:
          min_dist = dist
          min_index = index
          if min_dist == 0: min_dist = 0.5

      threshold = 4
      if min_dist <= threshold:
        if gameState.getAgentState(min_index).scaredTimer > 1:
          pass
          #features['distanceToOpponent'] = -1.0 / min_dist
          #results in pacman being kited and wasting time
        else:
          features['distanceToCapsule'] = self.getDistToClosestCapsule(successor)
          features['distanceToOpponent'] = 1.0 / min_dist
          if min_dist <= 1:
            features['suicide'] = 1

    return features

  def getWeightsOffense(self, gameState, action):
    return {'successorScore': 100,
            'distanceToFood': -5,
            'distanceToOther': -40,
            'distanceToOpponent': -225,
            'scaredTimer': -20,
            'distanceToCapsule': -200,
            'suicide': -5000}

class BlitzTopAgent(BlitzAgent):
  def setTarget(self, gameState):
    pass

class BlitzBottomAgent(BlitzAgent):
  def setTarget(self, gameState):
    pass