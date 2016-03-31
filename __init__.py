from game import Game

g = Game()  # Objects of the class Game are Talk of the Town simulations
# Simulate until the summer of 1979
try:
    g.establish_setting()  # 'Game.establish_setting()' is the worldgen procedure
except KeyboardInterrupt:  # Enter "ctrl+C" (a keyboard interrupt) to end worldgen early
    pass
print "\nPreparing for gameplay..."
g.enact_no_fi_simulation()  # This will tie up a few loose ends in the case of worldgen being terminated early