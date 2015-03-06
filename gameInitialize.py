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


allKnowledge = {}
id1 = 0
for other in gameInstance.get_people_a_person_knows_of(id1):
    allKnowledge[other]=gameInstance.get_knowledge(id1,other)
    
print allKnowledge