import os
import random


class Names(object):

    def __init__(self):
        self.masculine_forenames = tuple(
            name[:-1] for name in
            open(os.getcwd()+'/corpora/masculine_names.txt', 'r')
        )
        self.feminine_forenames = tuple(
            name[:-1] for name in
            open(os.getcwd()+'/corpora/feminine_names.txt', 'r')
        )
        self.english_surnames = tuple(
            name.strip('\n') for name in
            open(os.getcwd()+'/corpora/english_surnames.txt', 'r')
        )
        self.french_surnames = tuple(
            name.strip('\n') for name in
            open(os.getcwd()+'/corpora/french_surnames.txt', 'r')
        )
        self.german_surnames = tuple(
            name.strip('\n') for name in
            open(os.getcwd()+'/corpora/german_surnames.txt', 'r')
        )
        self.irish_surnames = tuple(
            name.strip('\n') for name in
            open(os.getcwd()+'/corpora/irish_surnames.txt', 'r')
        )
        self.scandinavian_surnames = tuple(
            name.strip('\n') for name in
            open(os.getcwd()+'/corpora/scandinavian_surnames.txt', 'r')
        )
        self.all_surnames = (
            self.english_surnames + self.french_surnames + self.irish_surnames +
            self.scandinavian_surnames
        )

    @property
    def a_masculine_name(self):
        return random.choice(self.masculine_forenames)

    @property
    def a_feminine_name(self):
        return random.choice(self.feminine_forenames)

    @property
    def an_english_surname(self):
        return random.choice(self.english_surnames)

    @property
    def a_french_surname(self):
        return random.choice(self.french_surnames)

    @property
    def a_german_surname(self):
        return random.choice(self.german_surnames)

    @property
    def an_irish_surname(self):
        return random.choice(self.irish_surnames)

    @property
    def a_scandinavian_surname(self):
        return random.choice(self.scandinavian_surnames)

    @property
    def any_surname(self):
        return random.choice(self.all_surnames)