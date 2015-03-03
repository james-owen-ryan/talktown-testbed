import os
import random


class Names(object):
    """A class that accesses names corpora to return random names."""
    masculine_forenames = tuple(
        name[:-1] for name in
        open(os.getcwd()+'/Assets/StreamingAssets/corpora/masculine_names.txt', 'r')
    )
    feminine_forenames = tuple(
        name[:-1] for name in
        open(os.getcwd()+'/Assets/StreamingAssets/corpora/feminine_names.txt', 'r')
    )
    english_surnames = tuple(
        name.strip('\n') for name in
        open(os.getcwd()+'/Assets/StreamingAssets/corpora/english_surnames.txt', 'r')
    )
    french_surnames = tuple(
        name.strip('\n') for name in
        open(os.getcwd()+'/Assets/StreamingAssets/corpora/french_surnames.txt', 'r')
    )
    german_surnames = tuple(
        name.strip('\n') for name in
        open(os.getcwd()+'/Assets/StreamingAssets/corpora/german_surnames.txt', 'r')
    )
    irish_surnames = tuple(
        name.strip('\n') for name in
        open(os.getcwd()+'/Assets/StreamingAssets/corpora/irish_surnames.txt', 'r')
    )
    scandinavian_surnames = tuple(
        name.strip('\n') for name in
        open(os.getcwd()+'/Assets/StreamingAssets/corpora/scandinavian_surnames.txt', 'r')
    )
    all_surnames = (
        english_surnames + french_surnames + irish_surnames +
        scandinavian_surnames
    )
    place_names = tuple(
        name.strip('\n') for name in
        open(os.getcwd()+'/Assets/StreamingAssets/corpora/US_settlement_names.txt', 'r')
    )
    restaurant_names = tuple(
        name.strip('\n') for name in
        open(os.getcwd()+'/Assets/StreamingAssets/corpora/restaurant_names.txt', 'r')
    )
    bar_names = tuple(
        name.strip('\n') for name in
        open(os.getcwd()+'/Assets/StreamingAssets/corpora/bar_names.txt', 'r')
    )

    @classmethod
    def a_masculine_name(cls):
        """Return a random masculine first name."""
        return random.choice(cls.masculine_forenames)

    @classmethod
    def a_feminine_name(cls):
        """Return a random feminine first name."""
        return random.choice(cls.feminine_forenames)

    @classmethod
    def an_english_surname(cls):
        """Return a random English surname."""
        return random.choice(cls.english_surnames)

    @classmethod
    def a_french_surname(cls):
        """Return a random French surname."""
        return random.choice(cls.french_surnames)

    @classmethod
    def a_german_surname(cls):
        """Return a random German surname."""
        return random.choice(cls.german_surnames)

    @classmethod
    def an_irish_surname(cls):
        """Return a random Irish surname."""
        return random.choice(cls.irish_surnames)

    @classmethod
    def a_scandinavian_surname(cls):
        """Return a random Scandinavian surname."""
        return random.choice(cls.scandinavian_surnames)

    @classmethod
    def any_surname(cls):
        """Return a random surname of any ethnicity."""
        return random.choice(cls.all_surnames)

    @classmethod
    def a_masculine_name_starting_with(cls, letter):
        """Return a random masculine name starting with the given letter."""
        names_that_start_with_that_letter = [
            name for name in cls.masculine_forenames if name[0].lower() == letter.lower()
        ]
        return random.choice(names_that_start_with_that_letter)

    @classmethod
    def a_feminine_name_starting_with(cls, letter):
        """Return a random feminine name starting with the given letter."""
        names_that_start_with_that_letter = [
            name for name in cls.feminine_forenames if name[0].lower() == letter.lower()
        ]
        return random.choice(names_that_start_with_that_letter)

    @classmethod
    def a_surname_starting_with(cls, letter):
        """Return a random surname starting with the given letter."""
        names_that_start_with_that_letter = [
            name for name in cls.all_surnames if name[0].lower() == letter.lower()
        ]
        return random.choice(names_that_start_with_that_letter)

    @classmethod
    def a_place_name(cls):
        """Return a random place name."""
        return random.choice(cls.place_names)

    @classmethod
    def a_restaurant_name(cls):
        """Return a random restaurant name."""
        return random.choice(cls.restaurant_names)

    @classmethod
    def a_bar_name(cls):
        """Return a random br name."""
        return random.choice(cls.bar_names)