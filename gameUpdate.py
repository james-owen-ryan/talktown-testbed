from game import *

gameInstance.advance_timestep()
blocks = gameInstance.city.blocks
lots = gameInstance.city.lots | gameInstance.city.tracts
people = gameInstance.city.residents