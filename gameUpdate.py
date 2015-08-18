from game import *

gameInstance.enact_hi_fi_simulation()
blocks = gameInstance.city.blocks
lots = gameInstance.city.lots | gameInstance.city.tracts
people = gameInstance.city.residents