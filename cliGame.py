from game_model import Model
from monteCarloAgent import MonteCarloTreeSearchAgent

print("Enter the board size")
size=int(input())
m=Model(size)
# m.place_stone(0,0)
# m.place_stone(0,1)
# m.place_stone(1,0)
# m.place_stone(1,1)
# m.place_stone(1,2)
# m.place_stone(0,2)


nextPlayerHuman=False
while not m.game_over:
  if nextPlayerHuman:
    while True:
      print("Play a move (-1,-1 = pass)")
      move=[int(x) for x in input().split(",")][::-1]
      # print("move:",move[0],move[1])
      if len(move)==2 and m.legal_move(move[0],move[1]):
        break
      else:
        print("Invalid move...")
  else:
    a=MonteCarloTreeSearchAgent(m.copy())
    move=a.mctsSearch() 
    # if not m.legal_move(move[0],move[1]):
    #   print("NIJE DOBAR POTEZ....",move[0],move[1]) 
  print("playing ",move[1]," ",move[0]) 
  m.place_stone(move[0],move[1])
  print(".......................................")
  m.printBoard()
  nextPlayerHuman=not nextPlayerHuman
#proveriti da li je ok rez
m.find_territory()
scores=m.getFinalScores()
print("The final score is ",scores[0]," for white and ",scores[1]," for black")