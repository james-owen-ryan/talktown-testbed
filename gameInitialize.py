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

pickle.dump(gameInstance.city.getLots(),open( "lots.dat", "wb" ))
pickle.dump(gameInstance.city.getBlocks(),open( "blocks.dat", "wb" ))
pickle.dump(gameInstance.city.getApartments(),open( "apartments.dat", "wb" ))
pickle.dump(gameInstance.city.getBusinesses(),open( "businesses.dat", "wb" ))
pickle.dump(gameInstance.city.getHouses(),open( "houses.dat", "wb" ))
pickle.dump(gameInstance.city.getStreets(),open( "streets.dat", "wb" ))