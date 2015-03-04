from game import *
from city import *
from config import *
gameInstance = Game()
gameInstance.advance_timestep()
blocks = gameInstance.city.blocks
lots = gameInstance.city.lots
people = gameInstance.city.residents
houses = gameInstance.city.houses 
apartments = gameInstance.city.apartment_complexes 
businesses = gameInstance.city.other_businesses   