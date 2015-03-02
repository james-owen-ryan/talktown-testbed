from game import *


gameInstance = Game()
blocks = gameInstance.city.blocks
lots = gameInstance.city.lots | gameInstance.city.tracts
people = gameInstance.city.residents