# type: ignore

from random_agent import RandomAgent
from bayes_agent import BayesAgent
from monte_agent import MonteAgent
from game import Game

agents = [RandomAgent(name='r1'),
          RandomAgent(name='r2'),
          RandomAgent(name='r3'),
          RandomAgent(name='r4'),
          RandomAgent(name='r5'),
          RandomAgent(name='r6'),
          MonteAgent()]

# agents = [BayesAgent(name='b1'),
#           BayesAgent(name='b2'),
#           BayesAgent(name='b3'),
#           BayesAgent(name='b4'),
#           BayesAgent(name='b5'),
#           BayesAgent(name='b6'),
#           BayesAgent(name='b7')]

times_won = 0
trials = 1

for i in range(trials):
    game = Game(agents)
    game.play()

    monte_spy = False
    for spy in game.spies:
        if agents[spy].name == 'Mr. Monte':
            monte_spy = True

    spys_won = game.missions_lost >= 3

    won_as_spy = monte_spy and spys_won
    won_as_resistance = not (monte_spy or spys_won)

    if won_as_spy or won_as_resistance:
        times_won += 1

print(f"{times_won * 100 / trials}%")

# textfile = open("game.txt", "w")
# textfile.write(game.__str__())
# textfile.close()
