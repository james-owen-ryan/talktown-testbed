from game import Game

game = Game()
print game
game.establish_setting()
print 'settings established'
#see what businesses are in the town with:
print 'city companies'
for c in game.city.companies:
    print c

print 'former companies'
#explore some of the history of the town:
for c in game.city.former_companies:
    print c

# list a random resident's social relations with everyone in the town:
p = game.random_person
print 'random person', p
for r in game.city.residents:
    print p.relation_to_me(r)

# explore a characters mental models:
p = game.random_person
print p
print 'random person mental models', p
for person_home_or_business in p.mind.mental_models:
    print p.mind.mental_models[person_home_or_business]