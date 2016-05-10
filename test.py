from game import Game


game = Game()  # Objects of the class Game are Talk of the Town simulations
print "Simulating a town's history..."
# Simulate until the summer of 1979, when gameplay takes place
try:
    game.establish_setting()  # This is the worldgen procedure
except KeyboardInterrupt:  # Enter "ctrl+C" (a keyboard interrupt) to end worldgen early
    pass
print "\nPreparing for gameplay..."
game.enact_no_fi_simulation()  # This will tie up a few loose ends in the case of worldgen being terminated early
print '\nIt is now the {date}, in the town of {city}, pop. {population}.\n'.format(
    date=game.date[0].lower()+game.date[1:],
    city=game.city.name,
    population=game.city.population
)
# Print out businesses in town
print '\nThe following companies currently operate in {city}:\n'.format(
    city=game.city.name
)
for c in game.city.companies:
    print c
# Print out former businesses in town to briefly explore its history
for c in game.city.former_companies:
    print c
# Procure and print out a random character in the town
p = game.random_person
print '\nRandom character: {random_character}\n'.format(
    random_character=p
)
# Print out this character's relationships with every other resident in town
for r in game.city.residents:
    print p.relation_to_me(r)
# Explore this person's mental models
print "\n{random_character}'s mental models:\n".format(
    random_character=p.name
)
for person_home_or_business in p.mind.mental_models:
    print p.mind.mental_models[person_home_or_business]
g = game
