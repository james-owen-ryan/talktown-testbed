from game import *
from city import *
from config import *
import pickle
gameInstance = Game()
gameInstance.advance_timestep()
blocks = gameInstance.city.blocks
lots = gameInstance.city.lots
people = gameInstance.city.residents
houses = gameInstance.city.houses 
apartments = gameInstance.city.apartment_complexes 
businesses = gameInstance.city.other_businesses   


pickle.dumps(gameInstance.city.getLots())
pickle.dumps(gameInstance.city.getBlocks())
pickle.dumps(gameInstance.city.getApartments())
pickle.dumps(gameInstance.city.getBusinesses())
pickle.dumps(gameInstance.city.getStreets())