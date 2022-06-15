
'''
go implementation copied from: https://github.com/nikzaugg/Go-Game
Model class:
  fields:
    self.size - board size
    self.turn - BLACK or WHITE
    self.blocked_field - some boolean for ko rule, idk
    self.has_passed - to check if the last move is a pass
    self.game_over - to check if game is over
    self.board - current board state?
    self.territory - current teritory state?
    self.score - score at the end for both sides
    self.captured - number captured from both sides
  methods:
    place_stone(self,x,y) - tries to place stone at the given position, updates the board state
    legal_move(self,x,y) - returns true if move is legal, false otherwise
    add_scores(self) - returns an array [x,y] of scores for both of the players
    get_data(self) - returns all of the relevant data
  we probably only need to use the two methods and teh game_over function here          
'''
from cmath import inf
import datetime
from typing import Type
from copy import copy, deepcopy
import random
from game_model import Model 
import numpy as np
'''
2nd step here:
We will just use the standard monte-carlo tree search technique with fixed parameters
We can just iterate the serach for about 2 seconds per turn and return the most promising move
This move is probably going to be the one that is the most visited in our traversal???
or the one with the highest winrate??? not sure, might be some better way
The exploration function is probably going to be the standard one which explores the child of the current node which maximizes
wi/ni+c*sqrt(ln(Ni)/ni), wi-wins for the i-th node,ni-games,Ni-parent games,ci-probably sqrt(2)
'''  
class MonteCarloTreeSearchAgent(object):
  '''
    This class gets passed the model containing the current game state
    it returns the best move calculated by the Monte Carlo tree search algorithm
  '''
  possibleMoves=[]
  def __init__(self,board):
    self.model=board
    self.n=board.size
    self.parent=None
    self.children=[]
    self.visits=0
    self.scoreSum=0
    self.lastMove=None 
    self.expanded=True
    self.playedMove=False
    self.setPossibleMoves()

  def setPossibleMoves(self):
    if(len(self.possibleMoves)==0):
      self.possibleMoves=[(x,y) for x in range(self.n) for y in range(self.n)]+[(-1,-1)]

  def playMove(self,x,y):
    # print("BOARD BEFORE....")
    # self.model.printBoard()
    newBoard=MonteCarloTreeSearchAgent(self.model.copy())
    newBoard.n=self.n
    newBoard.children=[]
    newBoard.parent=self
    # print("BOARD AFTER COPY....")
    # newBoard.model.printBoard()
    newBoard.model.place_stone(y,x)
    # print("BOARD AFTER ADDING...",y," ",x)
    # newBoard.model.printBoard()
    newBoard.visits=0
    newBoard.scoreSum=0
    newBoard.expanded=False
    newBoard.lastMove=(y,x)
    return newBoard
      
  def getLastMove(self):
    return self.lastMove

  def legalMoves(self):
    allLegalMoves=[]
    for (x,y) in self.possibleMoves:
      if(self.model.legal_move(y,x)):
        allLegalMoves.append((x,y))
    return allLegalMoves

  def defaultPolicy(self,startNode):
    '''
      This function plays random (legal) moves until the game is over
      The return value is the evaulation of the final position
    '''
    currBoard=startNode.model.copy()
    # print("starting from:")
    # currBoard.model.printBoard()
    while not currBoard.game_over:
      next_move=random.choice(self.possibleMoves)
        # next_move=random.choice(self.legalMoves())
      currBoard.place_stone(next_move[1],next_move[0])
    # print("ending with:")
    # currBoard.model.printBoard()
    currBoard.find_territory() 
    # print("reward is ",currBoard.model.getReward())
    return currBoard.getReward()
    
  def expand(self):
    '''
    we add the best move that is not in our current child list to our tree 
    we mark which states have already been visited (all false by default)
    when we expand a node, we set its visit value to true
    '''
    self.expanded=True
    if len(self.children)==0:
      self.children=[self.playMove(x,y) for (x,y) in self.legalMoves()]
    return self


  def score(self,child):
    if(child.visits==0):
      return float(inf)
    return 1.0*child.scoreSum/child.visits+np.sqrt(2.0*np.log(self.visits)/child.visits)
  
  def avgEval(self,child):
    if(child.visits==0):
      return 0
    return 1.0*child.scoreSum/child.visits
  
  def bestChild(self):
    #we choose the move with the lowest score (because the computer is the second player)
    if len(self.children)==0:
      self.children=[self.playMove(x,y) for (x,y) in self.legalMoves()]
    options=[(self.score(child),child) for child in self.children]
    bestOption=max(options,key=lambda x:x[0])
    return bestOption[1]

  def bestAvgScoreChild(self):
    if len(self.children)==0:
      self.children=[self.playMove(x,y) for (x,y) in self.legalMoves()]
    options=[(self.avgEval(child),child) for child in self.children]
    bestOption=max(options,key=lambda x:x[0])
    return bestOption[1]
  
  def mostVisitedChild(self):
    if len(self.children)==0:
      self.children=[self.playMove(x,y) for (x,y) in self.legalMoves()]
    assert(len(self.children)>0)
    bestChild=self.children[0]
    for child in self.children:
      if child.visits>bestChild.visits or (child.visits==bestChild.visits and self.avgEval(child)>=self.avgEval(bestChild)):
        bestChild=child
    return bestChild
    
  def backup(self,v,delta):
    while v!=None:
      v.visits+=1
      v.scoreSum+=delta
      v=v.parent
    
  def treePolicy(self):
    v=self
    # print("starting iteration...")
    while not v.model.game_over:
      # print("iterating in tree policy...")
      if not v.expanded: #if this node is not in the tree, we add it
        # print("not expanded")
        #we expand the child that's the best according to our eval function
        return v.expand()
      else:
        # print("expanded,going to child")
        v=v.bestChild()
    return v

  def mctsSearch(self):
    #TODO: write the treePolicy and backup methods
    '''
      This function plays the best move found by the monte carlo tree search and returns the x and y values (-1,-1) for pass
    '''
    move_start_time = datetime.datetime.now()
    move_max_seconds=3
    while datetime.datetime.now()<move_start_time+datetime.timedelta(seconds=move_max_seconds):
    # cnt=0
    # while cnt<3:
      # print("treePolicy:")
      vl=self.treePolicy()
      # print("got :",vl.lastMove[0],vl.lastMove[1])
      delta=self.defaultPolicy(vl)
      self.backup(vl,delta)
      # cnt+=1
    #we return the best move
    for child in self.children:
      print("c:",child.lastMove[1],child.lastMove[0])
      # print ("childBoard:")
      # child.model.printBoard()
      print("visits:",child.visits," scoreSum:",child.scoreSum) #not getting updated at all
    
    return self.mostVisitedChild().getLastMove()

