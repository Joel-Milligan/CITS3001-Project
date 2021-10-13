# type: ignore

from random_agent import RandomAgent
from detective_agent import DetectiveAgent
from game import Game

agents = [RandomAgent(name='r1'),
          RandomAgent(name='r2'),
          RandomAgent(name='r3'),
          RandomAgent(name='r4'),
          RandomAgent(name='r5'),
          RandomAgent(name='r6'),
          DetectiveAgent()]

game = Game(agents)
game.play()
print(game)

textfile = open("game.txt", "w")
textfile.write(game.__str__())
textfile.close()
