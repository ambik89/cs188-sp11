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

'''
NOTES:
- capsulelists get updated between gamestate and successor
'''

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
  agent1.setThreatened(False)
  agent2.setThreatened(False)
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

    # figure out chokepoints
    # vertical chokepoints
    

    self.setTarget(gameState)

  def getVerticalChokePoints(self, gameState):
    width = gameState.getWalls().width
    if self.red:
      start = 0
      end = width/2 - 1
    else:
      start = width
      end = width/2
    #TODO
      
  
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

  def setThreatened(self, val):
    self.threatened = val

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

  def getDistToPartner(self, gameState):
    distanceToAgent = None
    agentsList = self.agentsOnTeam
    if self.index == self.agentsOnTeam[0]:
      otherAgentIndex = self.agentsOnTeam[1]
    else:
      otherAgentIndex = self.agentsOnTeam[0]
    # The below code is indented under 'else'
    # so that only 1 of the agents cares how close it is to the other
      myPos = self.getMyPos(gameState)
      otherPos = gameState.getAgentState(otherAgentIndex).getPosition()
      distanceToAgent = self.getMazeDistance(myPos, otherPos)
      if distanceToAgent == 0: distanceToAgent = 0.5
    return distanceToAgent

  def getDistToClosestFood(self, gameState):
    myPos = self.getMyPos(gameState)
    foodList = self.getFood(gameState).asList()
    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      return min([self.getMazeDistance(myPos, food) for food in foodList])
    else:
      # somehow none of the opponent's food is left on the grid
      return None

  # Compute the index of, and distance to, closest enemy (if detected)
  def getIDDistToSeenEnemy(self, gameState):
    enemyIndex = None
    distToEnemy = None
    opponentPositions = self.getOpponentPositions(gameState)
    if len(opponentPositions) > 0:
      # if we're in here, we're threatened by a visible opponent
      min_dist = 10000
      min_index = None
      myPos = self.getMyPos(gameState)
      for index, pos in opponentPositions:
        dist = self.getMazeDistance(myPos, pos)
        if dist < min_dist:
          min_dist = dist
          min_index = index
          if min_dist == 0: min_dist = 0.5
      enemyIndex = min_index
      distToEnemy = min_dist      
      
    return (enemyIndex, distToEnemy)

  def getDistToClosestCapsule(self, gameState, successor):
    myPos = self.getMyPos(successor)
    oldCapsuleList = self.getCapsules(gameState)
    capsuleList = self.getCapsules(successor)
    
    minDistance = None
    if len(capsuleList) < len(oldCapsuleList):
      minDistance = 0
    elif len(capsuleList) > 0:
      minDistance = min([self.getMazeDistance(myPos, capsule) for capsule in capsuleList])
    return minDistance

  def getMyScaredTimer(self, gameState):
    return gameState.getAgentState(self.index).scaredTimer
  

class BaseAgent(ReflexCaptureAgent):
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
    elif mode == 'start':
      features = self.getFeaturesStart(gameState, action)
      weights = self.getWeightsStart(gameState, action)
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
      min_idx, min_dist = self.getIDDistToSeenEnemy(successor)
      features['invaderDistance'] = min_dist
      if min_dist <= 1 and self.getMyScaredTimer(successor) > 0 and self.isAtHome(successor):
        features['suicide'] = 1
      if not self.isAtHome(successor) and min_dist <= 1:
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

    # Stopping is unfavorable
    if action == Directions.STOP:
      features['stop'] = 1

    # Compute distance to the nearest food
    features['distanceToFood'] = self.getDistToClosestFood(successor)

    # Just grab the capsule if it's really close
    distToCapsule = self.getDistToClosestCapsule(gameState, successor)
    if distToCapsule == 0:
      distToCapsule = 0.5
    if distToCapsule != None:
      features['distanceToCapsule'] = 1.0 / distToCapsule

    # Compute distance to partner
    if not self.isAtHome(successor):
      distanceToAgent = self.getDistToPartner(successor)
      # distanceToAgent is always None for one of the agents (so they don't get stuck)
      if distanceToAgent != None:
        features['distanceToOther'] = 1.0 / distanceToAgent

    # Compute distance to enemy (if detected)
    enemyIndex, distToEnemy = self.getIDDistToSeenEnemy(successor)
    distToCapsule = self.getDistToClosestCapsule(gameState, successor)
    if distToEnemy != None:
      if distToEnemy <= 4:
        self.threatened = True
        if gameState.getAgentState(enemyIndex).scaredTimer > 1:
          pass
          #features['distanceToOpponent'] = -1.0 / distToEnemy
          #results in pacman being kited and wasting time
        else:
          if distToCapsule != None:
            features['distanceToCapsuleThreatened'] = distToCapsule
          features['distanceToOpponent'] = 1.0 / distToEnemy
          if self.isAtHome(successor) and self.getMyScaredTimer(successor) <= 1:
            features['atHomeThreatened'] = 1
          if distToEnemy <= 1:
            features['suicide'] = 1
      
    if distToEnemy == None or distToEnemy > 4:
      self.threatened = False

    if self.otherAgent.threatened and distToCapsule != None and distToCapsule <= 5:
      features['distanceToCapsuleThreatened'] = distToCapsule
    return features

  def getWeightsOffense(self, gameState, action):
    return {'successorScore': 200,
            'distanceToFood': -5,
            'distanceToOther': -40,
            'distanceToOpponent': -225,
            'distanceToCapsule': 30,
            'distanceToCapsuleThreatened': -230,
            'stop': -100,
            'atHomeThreatened': 400,
            'suicide': -5000}

  def getFeaturesStart(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myPos = self.getMyPos(successor)

    features = util.Counter()
    dist = self.getMazeDistance(myPos, self.target)
    features['distanceToTarget'] = dist
    if myPos == self.target:
      features['atTarget'] = 1
    return features
  
  def getWeightsStart(self, gameState, action):
    return {'distanceToTarget': -10, 'atTarget': 100}

  def maxValue(self, gameState, depth):
    if gameState.isWin() or gameState.isLose() or depth == 0:
      return self.evaluationFunction(gameState)
    
    numAgents = gameState.getNumAgents()

    v = -1000
    actions = gameState.getLegalActions(0)
    for action in actions:
      successor = gameState.generateSuccessor(0, action)
      v = max(v, self.minValue(successor, depth, 1))
    return v

  def minValue(self, gameState, depth, agentIndex):
    if gameState.isWin() or gameState.isLose():
      return self.evaluationFunction(gameState)

    numAgents = gameState.getNumAgents()
    #if depth == 1 and agentIndex == numAgents-1:
    #  return self.evaluationFunction(gameState)

    v = 1000
    actions = gameState.getLegalActions(agentIndex)
    for action in actions:
      successor = gameState.generateSuccessor(agentIndex, action)
      if agentIndex < numAgents-1:
        v = min(v, self.minValue(successor, depth, agentIndex+1))
      else:
        v = min(v, self.maxValue(successor, depth-1))
    return v

class BlitzAgent(BaseAgent):
  def chooseAction(self, gameState):
    # default mode is 'offense'
    evalmode = 'offense'
    
    # Head for the target at the beginning
    if self.reachedTarget == False:
      evalmode = 'start'

    # Turn off 'start' mode if we've reached the target once
    myPos = self.getMyPos(gameState)
    if myPos == self.target and self.reachedTarget == False:
      evalmode = 'offense'
      self.reachedTarget = True
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

class BlitzTopAgent(BlitzAgent):
  def setTarget(self, gameState):
    self.reachedTarget = False
    x = gameState.getWalls().width / 2
    y = gameState.getWalls().height / 2
    if self.red: x -= 1
    # set self.target
    self.target = (x,y)
    yLimit = gameState.getWalls().height
    possibleTargets = []

    # Create a list of possible targets in the upper half
    for i in xrange(yLimit - y):
      if not gameState.hasWall(x, y):
        possibleTargets.append((x,y))
      y += 1

    startPos = self.getMyPos(gameState)
    min_dist = 1000
    min_pos = None
    # find the closest target position
    for pos in possibleTargets:
      dist = self.getMazeDistance(startPos, pos)
      if dist <= min_dist:
        min_dist = dist
        min_pos = pos
        
    self.target = min_pos
      
    
class BlitzBottomAgent(BlitzAgent):
  def setTarget(self, gameState):
    self.reachedTarget = False
    x = gameState.getWalls().width / 2
    y = gameState.getWalls().height / 2
    if self.red: x -= 1
    # set self.target
    self.target = (x,y)
    yLimit = 0
    possibleTargets = []

    # Create a list of possible targets in the lower half
    for i in xrange(y - yLimit):
      if not gameState.hasWall(x, y):
        possibleTargets.append((x,y))
      y -= 1

    startPos = self.getMyPos(gameState)
    min_dist = 1000
    min_pos = None
    # find the closest target position
    for pos in possibleTargets:
      dist = self.getMazeDistance(startPos, pos)
      if dist <= min_dist:
        min_dist = dist
        min_pos = pos
        
    self.target = min_pos
