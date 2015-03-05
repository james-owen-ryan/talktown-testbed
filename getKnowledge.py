from game import *
allKnowledge = {}
for other in gameInstance.get_people_a_person_knows_of(id1):
    allKnowledge[other]=gameInstance.get_knowledge(id1,other)
    