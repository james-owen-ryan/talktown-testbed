from occupation import *
from event import *
from business import *
from conversation import *
import math


class Config(object):
    """Configuration for a gameplay instance in terms of simulation and gameplay parameters."""

    def __init__(self):
        """Construct a Config object."""

                #################
                ##  WORLD GEN  ##
                #################
        self.chance_of_a_coal_mine_at_time_of_town_founding = 0.2
        self.chance_of_a_quarry_at_time_of_town_founding = 0.15
        # When to stop
        self.date_gameplay_begins = (1979, 8, 19)
        self.date_worldgen_begins = (1839, 8, 19)  # Date world gen begins
        self.year_worldgen_begins = self.date_worldgen_begins[0]
        self.date_of_epilogue = (2009, 8, 19)  # Date of epilogue 40 years after gameplay
        # City generation (in a topological sense)
        self.quadtree_loci = 3
        self.quadtree_samples = 32
        self.quadtree_size = 16
        self.quadtree_multiplier = 2
        self.n_buildings_per_parcel = 2
        self.largest_possible_house_number = 799
        self.smallest_possible_house_number = 100
        self.chance_city_gets_named_for_founder = 0.3
        self.chance_avenue_gets_numbered_name = 0.0
        self.chance_street_gets_numbered_name = 0.8
        # City founder
        self.age_of_city_founder = 30
        self.age_of_city_founders_spouse = 30
        self.money_city_founder_starts_with = 100000
        self.boost_to_the_founders_conception_chance = 0.2
        # City establishment and early development
        self.number_of_apartment_complexes_founder_builds_downtown = 3

                ############
                ##  SIM   ##
                ############

        self.chance_of_a_timestep_being_simulated = 0.005  # 3.6 timesteps a year on average
        # Daily routines
        self.chance_someone_locks_their_door = lambda neuroticism: neuroticism  # If random.random() > neuro: True
        self.chance_someone_calls_in_sick_to_work = 0.03
        self.chance_someone_doesnt_have_to_work_some_day = 0.00  # Can be used as proxy in lieu of weekends
        self.chance_someone_leaves_home_multiplier_due_to_kids = 0.3  # i.e., 30% as likely to leave if kids
        self.chance_someone_leaves_home_on_day_off_floor = {
            # The actual chance is a person's extroversion, but these represent
            # the minimum chance. (Keep in mind, they currently will be spending
            # the entire day/night cycle at some particular place in public
            "day": 0.3, "night": 0.15
        }
        self.chance_someone_leaves_home_on_day_off_cap = {
            # The actual chance is a person's extroversion, but these represent
            # the maximum chance. (Keep in mind, they currently will be spending
            # the entire day/night cycle at some particular place in public
            "day": 0.95, "night": 0.9
        }
        self.chance_someone_leaves_home_on_sick_day = 0.05
        self.chance_someone_goes_on_errand_vs_visits_someone = 0.75  # thus 0.25 of visiting someone
        self.who_someone_visiting_will_visit_probabilities = (
            ((0.0, 0.35), 'nb'),  # Visit neighbor
            ((0.35, 0.65), 'fr'),  # Visit friend
            ((0.65, 0.9), 'if'),  # immediate family
            ((0.9, 1.0), 'ef'),  # extended family
        )
        self.chance_someone_visiting_someone_visits_immediate_family = 0.3
        self.chance_someone_visiting_someone_visits_friend = 0.5
        self.chance_someone_visiting_someone_visits_extended_family = 0.15
        self.chance_someone_goes_to_closest_business_of_type = 0.75
        self.relative_frequencies_of_errands_for_service_types = {
            # Keep in mind, this person will be spending the entire day/night cycle there
            "day": {
                'baked goods': 3,
                'dairy': 3,
                'meat': 3,
                'clothes': 2.5,
                'banking': 2,
                'furniture': 2,
                'haircut': 2,
                'restaurant': 2,
                'park': 2,
                'medicine': 1.5,
                'shoes': 1.5,
                'tools': 1.5,
                'insurance': 1,
                'jewelry': 1,
                'confections': 0.5,
                'bar': 0.25,
                'dentist': 0.25,
                'eyeglasses': 0.15,
                'cemetery': 0.1,
                'tattoo': 0.1,
                'plastic surgery': 0.0,
                'transport': 0.0,  # No taxis or buses in this version
            },
            "night": {
                'restaurant': 5,
                'bar': 5,
                'cemetery': 0.05,
                'park': 0.05,
                'tattoo': 0.01,
                'baked goods': 0,
                'banking': 0,
                'clothes': 0,
                'confections': 0,
                'dairy': 0,
                'dentist': 0,
                'eyeglasses': 0,
                'furniture': 0,
                'haircut': 0,
                'insurance': 0,
                'jewelry': 0,
                'meat': 0,
                'medicine': 0,
                'plastic surgery': 0.0,
                'shoes': 0,
                'tools': 0,
                'transport': 0.0,  # No taxis or buses in this version
            },
        }
        # Fit a probability distribution to the above relative frequencies
        self.probabilities_of_errand_for_service_type = {
            "day": self.fit_probability_distribution(
                relative_frequencies_dictionary=self.relative_frequencies_of_errands_for_service_types["day"]
            ),
            "night": self.fit_probability_distribution(
                relative_frequencies_dictionary=self.relative_frequencies_of_errands_for_service_types["night"]
            )
        }
        self.business_type_to_occasion_for_visit = {
            'Bar': 'leisure',
            'Hotel': 'leisure',
            'Park': 'leisure',
            'Restaurant': 'leisure',
            'Bank': 'errand',
            'Barbershop': 'errand',
            'BusDepot': 'errand',
            'Cemetery': 'errand',
            'OptometryClinic': 'errand',
            'PlasticSurgeryClinic': 'errand',
            'Supermarket': 'errand',
            'TattooParlor': 'errand',
            'TaxiDepot': 'errand',
            'University': 'errand',
            'ApartmentComplex': 'errand',
            'Bakery': 'errand',
            'BlacksmithShop': 'errand',
            'Brewery': 'leisure',
            'ButcherShop': 'errand',
            'CandyStore': 'leisure',
            'CarpentryCompany': 'errand',
            'CityHall': 'errand',
            'ClothingStore': 'errand',
            'CoalMine': 'errand',
            'ConstructionFirm': 'errand',
            'Dairy': 'errand',
            'DayCare': 'errand',
            'Deli': 'leisure',
            'DentistOffice': 'errand',
            'DepartmentStore': 'leisure',
            'Diner': 'leisure',
            'Distillery': 'leisure',
            'DrugStore': 'errand',
            'Farm': 'errand',
            'FireStation': 'errand',
            'Foundry': 'errand',
            'FurnitureStore': 'errand',
            'GeneralStore': 'errand',
            'GroceryStore': 'errand',
            'HardwareStore': 'errand',
            'Hospital': 'errand',
            'Inn': 'errand',
            'InsuranceCompany': 'errand',
            'JeweleryShop': 'errand',
            'LawFirm': 'errand',
            'PaintingCompany': 'errand',
            'Pharmacy': 'errand',
            'PlumbingCompany': 'errand',
            'PoliceStation': 'errand',
            'Quarry': 'errand',
            'RealtyFirm': 'errand',
            'School': 'errand',
            'ShoemakerShop': 'errand',
            'TailorShop': 'errand',
            'Tavern': 'leisure',
        }
        # self.errand_business_types = ('Supermarket', 'Bank', 'BusDepot', 'Cemetery', 'TaxiDepot', 'University')
        # self.leisure_business_types = ('Restaurant', 'Park', 'Bar', 'Hotel')
        # Socializing
        # The chance someone will spark up an interaction with someone else has to
        # do with their extroversion, openness to experience (if they don't know
        # them already), and how well they already know that person; derivation of this
        # starts from the contribution of a person's extroversion (which gets floored
        # or capped according to parameters below)
        self.chance_of_interaction_extroversion_component_floor = 0.05
        self.chance_of_interaction_extroversion_component_cap = 0.7
        self.chance_of_interaction_openness_component_floor = 0.01
        self.chance_of_interaction_openness_component_cap = 0.7
        self.chance_of_interaction_friendship_component = 0.5  # Boost to chance if person is a friend
        self.chance_of_interaction_best_friend_component = 0.2  # Boost to chance if person is a best friend
        self.chance_someone_instigates_interaction_with_other_person_floor = 0.05
        self.chance_someone_instigates_interaction_with_other_person_cap = 0.95
        # Marriage
        self.min_mutual_spark_value_for_someone_to_propose_marriage = 5
        self.chance_one_newlywed_takes_others_name = 0.9
        self.chance_newlyweds_decide_children_will_get_hyphenated_surname = 0.4  # Given already not taking same name
        self.chance_a_newlywed_keeps_former_love_interest = 0.01
        self.chance_stepchildren_take_stepparent_name = 0.3
        self.age_after_which_stepchildren_will_not_take_stepparent_name = 6
        self.function_to_determine_chance_married_couple_are_trying_to_conceive = (
            # This is the chance they try to conceive across a given year -- it decreases
            # according to the number of kids they have
            lambda n_kids: 0.4 / (n_kids + 1)
        )
        # Divorce
        self.chance_a_divorce_happens_some_timestep = 0.002 / 720  # 1/500 chance of divorce each year
        self.chance_a_divorcee_falls_out_of_love = 0.9
        self.new_spark_value_for_divorcee_who_has_fallen_out_of_love = -500.0
        self.chance_a_male_divorcee_is_one_who_moves_out = 0.7
        self.function_to_derive_chance_spouse_changes_name_back = (
            lambda years_married: min(
                0.9 / ((years_married + 0.1) / 4.0),  # '+0.1' is to avoid ZeroDivisionError
                0.9
            )
        )
        # Sex
        self.chance_person_falls_in_love_after_sex = 0.8
        self.chance_protection_does_not_work = 0.01
        # Pregnancy
        self.function_to_determine_chance_of_conception = lambda female_age: max(
            female_age/10000., (100 - ((female_age**1.98) / 20.)) / 100  # Decreases exponentially with age
        )
        # Birth
        self.chance_new_mother_quits_job_even_if_day_care_in_town = 0.35
        # Aging
        self.age_when_people_start_graying = 48
        self.age_when_men_start_balding = 48
        self.chance_someones_hair_goes_gray_or_white = 0.02
        self.chance_someones_loses_their_hair_some_year = 0.02
        # Death
        self.chance_someone_dies_some_timestep = 0.125
        self.function_to_derive_chance_a_widow_remarries = (
            lambda years_married: 1.0 / (int(years_married) + 4)
        )
        # People finding new homes
        self.penalty_for_having_to_build_a_home_vs_buying_one = 0.1  # i.e., relative desire to build
        self.desire_to_live_near_family_base = 0.3  # Scale of -1 to 1; affected by personality
        self.desire_to_live_near_family_floor = -2
        self.desire_to_live_near_family_cap = 2
        self.pull_to_live_near_a_friend = 1.5
        self.pull_to_live_near_family = {
            # Arbitrary units (are just relative to each other; will also get
            # altered by the person's desire to live near family)
            'daughter': 7,
            'son': 7,
            'mother': 5,
            'father': 5,
            'granddaughter': 3,
            'grandson': 3,
            'sister': 2,
            'brother': 2,
            'grandmother': 2,
            'grandfather': 2,
            'greatgrandmother': 2,
            'greatgrandfather': 2,
            'niece': 1,
            'nephew': 1,
            'aunt': 1,
            'uncle': 1,
            'cousin': 1,
            None: 0,
        }
        self.pull_to_live_near_workplace = 5

                ###############
                ##  ECONOMY  ##
                ###############

        # Misc
        self.age_people_start_working = lambda year: 14 if year < 1920 else 16 if year < 1960 else 18
        self.amount_of_money_generated_people_from_outside_city_start_with = 5000
        # Housing
        self.number_of_apartment_units_in_new_complex_min = 4
        self.number_of_apartment_units_in_new_complex_max = 16
        # Company naming
        self.chance_company_gets_named_after_owner = 0.5
        # Companies deciding where to locate themselves
        self.function_to_determine_company_preference_for_local_population = (
            lambda secondary_pop, tertiary_pop: (secondary_pop * 5) + (tertiary_pop * 2)
        )
        self.function_to_determine_company_penalty_for_nearby_company_of_same_type = (
            # This is jury-rigged so that being within a few blocks of another company of the
            # same type will cancel out a relatively huge local population
            lambda dist_to_nearest_company_of_same_type: min(
                (((100-dist_to_nearest_company_of_same_type) ** 0.5) - 8) ** 10,
                0)
        )
        # Company types that are public resources, i.e., not privately owned
        self.public_company_types = (CityHall, FireStation, Hospital, PoliceStation, School, University, Cemetery, Park)
        self.public_places_closed_at_night = (Cemetery, Park)
        # Company types that get established on tracts, not on lots
        self.companies_that_get_established_on_tracts = (Cemetery, Park, Farm, Quarry, CoalMine)  # TODO maybe add University?
        # Companies hiring people
        self.preference_to_hire_immediate_family = 15
        self.preference_to_hire_extended_family = 7
        self.preference_to_hire_from_within_company = 5
        self.preference_to_hire_friend = 4  # TODO modify this according to charge
        self.preference_to_hire_immediate_family_of_an_employee = 3
        self.preference_to_hire_extended_family_of_an_employee = 2
        self.dispreference_to_hire_enemy = -1  # TODO modify this according to charge
        self.preference_to_hire_acquaintance = 0.5  # TODO modify this according to charge
        self.unemployment_occupation_level = 0.5  # Affects scoring of job candidates
        self.chance_a_business_opens_some_timestep = (1/730.) * 0.7  # 1.3 will open a year
        # This dictionary specifies three things about each business type: the year
        # at which it may be established in the simulation (its advent), the year at
        # which its closure will become highly likely (its demise), and the minimum
        # population that must live in the city in order for a business of this type
        # to be established; these are specified so that businesses don't appear
        # anachronistically or otherwise out of place
        self.business_types_advent_demise_and_minimum_population = {
            ApartmentComplex: (1880, 9999, 50),
            Bakery: (0, 9999, 50),
            Bank: (0, 9999, 100),
            Bar: (1920, 9999, 100),
            Barbershop: (0, 9999, 50),
            BlacksmithShop: (0, 1945, 0),
            Brewery: (0, 9999, 0),
            BusDepot: (1930, 9999, 9999),
            ButcherShop: (0, 1960, 50),
            CandyStore: (0, 1960, 100),
            CarpentryCompany: (0, 9999, 70),
            Cemetery: (0, 9999, 1),
            CityHall: (0, 9999, 100),
            ClothingStore: (0, 1880, 100),
            CoalMine: (0, 9999, 0),
            ConstructionFirm: (0, 9999, 80),
            Dairy: (0, 1945, 30),
            DayCare: (1960, 9999, 200),
            Deli: (1880, 9999, 100),
            DentistOffice: (0, 9999, 75),
            DepartmentStore: (1880, 9999, 200),
            Diner: (1945, 9999, 30),
            Distillery: (0, 1919, 0),
            DrugStore: (0, 1950, 30),
            Farm: (0, 1920, 0),
            FireStation: (0, 9999, 100),
            Foundry: (1830, 1950, 100),
            FurnitureStore: (0, 1930, 20),
            GeneralStore: (0, 1930, 20),
            GroceryStore: (0, 1950, 20),
            HardwareStore: (0, 9999, 40),
            Hospital: (0, 9999, 200),
            Hotel: (0, 9999, 50),
            Inn: (0, 9999, 0),
            InsuranceCompany: (0, 9999, 200),
            JeweleryShop: (0, 9999, 200),
            LawFirm: (0, 9999, 150),
            OptometryClinic: (1900, 9999, 200),
            PaintingCompany: (0, 9999, 100),
            Park: (0, 9999, 100),
            Pharmacy: (1960, 9999, 200),
            PlasticSurgeryClinic: (1970, 9999, 9999),
            PlumbingCompany: (0, 9999, 100),
            PoliceStation: (0, 9999, 100),
            Quarry: (0, 9999, 0),
            RealtyFirm: (0, 9999, 80),
            Restaurant: (0, 9999, 50),
            School: (0, 9999, 1),
            ShoemakerShop: (0, 1900, 20),
            Supermarket: (1945, 9999, 200),
            TailorShop: (0, 9999, 40),
            TattooParlor: (1970, 9999, 300),
            Tavern: (0, 1920, 20),
            TaxiDepot: (1930, 9999, 9999),
            University: (0, 9999, 9999),
        }
        # Max number of businesses of each type that may be in a city at the same time
        self.max_number_of_business_types_at_one_time = {
            ApartmentComplex: 99,
            Bakery: 2,
            Bank: 2,
            Bar: 3,
            Barbershop: 1,
            BlacksmithShop: 1,
            Brewery: 1,
            BusDepot: 1,
            ButcherShop: 2,
            CandyStore: 1,
            CarpentryCompany: 1,
            Cemetery: 1,
            CityHall: 1,
            ClothingStore: 2,
            CoalMine: 1,
            ConstructionFirm: 1,
            Dairy: 1,
            DayCare: 1,
            Deli: 2,
            DentistOffice: 1,
            DepartmentStore: 1,
            Diner: 3,
            Distillery: 1,
            DrugStore: 1,
            Farm: 99,
            FireStation: 1,
            Foundry: 1,
            FurnitureStore: 1,
            GeneralStore: 1,
            GroceryStore: 2,
            HardwareStore: 1,
            Hospital: 1,
            Hotel: 1,
            Inn: 2,
            InsuranceCompany: 1,
            JeweleryShop: 1,
            LawFirm: 1,
            OptometryClinic: 1,
            PaintingCompany: 1,
            Park: 99,
            Pharmacy: 1,
            PlasticSurgeryClinic: 1,
            PlumbingCompany: 2,
            PoliceStation: 1,
            Quarry: 1,
            RealtyFirm: 1,
            Restaurant: 5,
            School: 1,
            ShoemakerShop: 1,
            Supermarket: 1,
            TailorShop: 1,
            TattooParlor: 1,
            Tavern: 2,
            TaxiDepot: 1,
            University: 1,
        }
        # Services provided by each business type -- used to determine people's routines
        self.services_provided_by_business_of_type = {
            ApartmentComplex: (),
            Bakery: ('baked goods',),
            Bank: ('banking',),
            Bar: ('bar',),
            Barbershop: ('haircut',),
            BlacksmithShop: ('tools',),
            Brewery: (),
            BusDepot: ('transport',),
            ButcherShop: ('meat',),
            CandyStore: ('confections',),
            CarpentryCompany: (),  # MAYBE RANDOMLY HAVE PLUMBERS, ETC. VISIT HOMES AND BE THERE ON TIMESTEP
            Cemetery: ('cemetery',),
            CityHall: (),
            ClothingStore: ('clothes',),
            CoalMine: (),
            ConstructionFirm: (),
            Dairy: ('dairy',),
            DayCare: (),
            Deli: ('restaurant',),
            DentistOffice: ('dentist',),
            DepartmentStore: ('clothes', 'furniture', 'tools', 'confections', 'shoes'),
            Diner: ('restaurant',),
            Distillery: (),
            DrugStore: ('medicine', 'confections'),
            Farm: ('meat', 'dairy'),
            FireStation: (),
            Foundry: (),
            FurnitureStore: ('furniture',),
            GeneralStore: ('clothes', 'furniture', 'tools', 'confections'),
            GroceryStore: ('baked goods', 'meat', 'confections', 'dairy'),
            HardwareStore: ('tools',),
            Hospital: (),
            Hotel: ('restaurant', 'bar',),
            Inn: (),
            InsuranceCompany: ('insurance',),
            JeweleryShop: ('jewelry',),
            LawFirm: (),
            OptometryClinic: ('eyeglasses',),
            PaintingCompany: (),
            Park: ('park',),
            Pharmacy: ('medicine',),
            PlasticSurgeryClinic: ('plastic surgery',),
            PlumbingCompany: (),
            PoliceStation: (),
            Quarry: (),
            RealtyFirm: (),
            Restaurant: ('restaurant',),
            School: (),
            ShoemakerShop: ('shoes',),
            Supermarket: ('baked goods', 'meat', 'confections', 'medicine', 'dairy'),
            TailorShop: ('clothes',),
            TattooParlor: ('tattoo',),
            Tavern: ('bar', 'restaurant'),
            TaxiDepot: ('transport',),
            University: (),
        }
        # Chance a business shuts down some timestep -- TODO actually model how well business is doing
        self.chance_a_business_closes_some_timestep = (1/730.) / 60  # Average business will last 60 years
        # Chance a business shuts downs ome timestep after its specified demise -- i.e., chance a business
        # will shut down once its anachronistic, like a blacksmith shop after 1945
        self.chance_a_business_shuts_down_on_timestep_after_its_demise = (1/730.) / 3  # Average will last 3 years
        self.chance_a_new_adult_decides_to_leave_town = 0.1
        # Chance an unemployed person leaves the city on a *simulated* timestep
        self.chance_an_unemployed_person_departs_on_a_simulated_timestep = (
            # Currently set so that an unemployed person would be expected to leave the
            # city after three years of being unemployed (so change the 4 to change this) --
            # I have it set at four so that characters in times where people start working at
            # 18 may get a college degree (which currently happens automatically when someone
            # is 22 and unemployed)
            1.0 / (self.chance_of_a_timestep_being_simulated * 730 * 4)
        )
        # Occupation classes for owners/proprietors of each business type
        self.owner_occupations_for_each_business_type = {
            ApartmentComplex: Landlord,
            Bakery: Baker,
            Bank: Owner,
            Bar: Proprietor,
            Barbershop: Barber,
            BlacksmithShop: Blacksmith,
            Brewery: Owner,
            BusDepot: None,
            ButcherShop: Butcher,
            CandyStore: Proprietor,
            CarpentryCompany: Carpenter,
            Cemetery: None,
            CityHall: None,
            ClothingStore: Clothier,
            CoalMine: Owner,
            ConstructionFirm: Architect,
            Dairy: Milkman,
            DayCare: DaycareProvider,
            Deli: Proprietor,
            DentistOffice: Dentist,
            DepartmentStore: Owner,
            Diner: Proprietor,
            Distillery: Distiller,
            DrugStore: Druggist,
            Farm: Farmer,
            FireStation: None,
            Foundry: Owner,
            FurnitureStore: Woodworker,
            GeneralStore: Proprietor,
            GroceryStore: Grocer,
            HardwareStore: Proprietor,
            Hospital: None,
            Hotel: Owner,
            Inn: Innkeeper,
            InsuranceCompany: InsuranceAgent,
            JeweleryShop: Jeweler,
            LawFirm: Lawyer,
            OptometryClinic: Optometrist,
            PaintingCompany: Plasterer,
            Park: None,
            Pharmacy: Owner,
            PlasticSurgeryClinic: PlasticSurgeon,
            PlumbingCompany: Plumber,
            PoliceStation: None,
            Quarry: Owner,
            RealtyFirm: Realtor,
            Restaurant: Proprietor,
            School: None,
            ShoemakerShop: Shoemaker,
            Supermarket: Owner,
            TailorShop: Tailor,
            TattooParlor: TattooArtist,
            Tavern: Proprietor,
            TaxiDepot: Owner,
            University: None,
        }
        # Initial vacant positions for each business type
        self.initial_job_vacancies = {
            ApartmentComplex: {
                'day': (),
                'night': (Janitor,),
                'supplemental day': [Secretary, Janitor],
                'supplemental night': [],
            },
            Bank: {
                'day': (BankTeller,),
                'night': (Janitor,),
                'supplemental day': [BankTeller, BankTeller, Manager],
                'supplemental night': [],
            },
            Bar: {
                'day': (Bartender,),
                'night': (Bartender,),
                'supplemental day': [],
                'supplemental night': [Bartender, Bartender, Manager],
            },
            Barbershop: {
                'day': (),
                'night': (),
                'supplemental day': [Cashier],
                'supplemental night': [],
            },
            BusDepot: {
                'day': (Secretary, BusDriver, Manager),
                'night': (BusDriver,),
                'supplemental day': [BusDriver],
                'supplemental night': [],
            },
            CityHall: {
                'day': (Secretary,),  # Mayor excluded due to special hiring process
                'night': (),
                'supplemental day': [Secretary],
                'supplemental night': [Janitor],
            },
            ConstructionFirm: {
                'day': (Secretary, Bricklayer, Builder),
                'night': (),
                'supplemental day': [Builder, Builder],
                'supplemental night': [Janitor],
            },
            DayCare: {
                'day': (),
                'night': (Janitor,),
                'supplemental day': [DaycareProvider, DaycareProvider],
                'supplemental night': [],
            },
            FireStation: {
                'day': (Firefighter,),
                'night': (Firefighter,),
                'supplemental day': [FireChief, Secretary],
                'supplemental night': [Firefighter],
            },
            Hospital: {
                'day': (Secretary, Nurse, Doctor),
                'night': (Nurse, Doctor, Janitor),
                'supplemental day': [Nurse],
                'supplemental night': [Secretary, Nurse],
            },
            Hotel: {
                'day': (HotelMaid, Concierge),
                'night': (Concierge,),
                'supplemental day': [Manager, HotelMaid],
                'supplemental night': [],
            },
            LawFirm: {
                'day': (Secretary,),
                'night': (),
                'supplemental day': [Lawyer, Lawyer, Secretary, Lawyer],
                'supplemental night': [Janitor],
            },
            OptometryClinic: {
                'day': (),
                'night': (),
                'supplemental day': [Secretary, Nurse],
                'supplemental night': [Janitor],
            },
            PlasticSurgeryClinic: {
                'day': (),
                'night': (),
                'supplemental day': [Secretary, Nurse],
                'supplemental night': [Janitor],
            },
            PoliceStation: {
                'day': (PoliceOfficer,),
                'night': (PoliceOfficer,),
                'supplemental day': [Secretary, PoliceChief],
                'supplemental night': [PoliceOfficer],
            },
            RealtyFirm: {
                'day': (Secretary,),
                'night': (),
                'supplemental day': [Realtor, Realtor],
                'supplemental night': [Janitor],
            },
            Restaurant: {
                'day': (Waiter, Cook),
                'night': (Waiter, Cook),
                'supplemental day': [Busboy, Waiter, Manager, Dishwasher],
                'supplemental night': [Busboy, Waiter, Manager, Dishwasher],
            },
            School: {
                'day': (Janitor, Teacher, Teacher, Nurse, Principal),
                'night': (Janitor,),
                'supplemental day': [Teacher],
                'supplemental night': [Janitor],
            },
            Supermarket: {
                'day': (Cashier, Stocker, Manager),
                'night': (Stocker, Stocker),
                'supplemental day': [Cashier, Cashier, Stocker],
                'supplemental night': [Stocker],
            },
            TattooParlor: {
                'day': (),
                'night': (TattooArtist,),
                'supplemental day': [],
                'supplemental night': [Cashier],
            },
            TaxiDepot: {
                'day': (TaxiDriver,),
                'night': (TaxiDriver,),
                'supplemental day': [],
                'supplemental night': [TaxiDriver, Manager],
            },
            University: {
                'day': (Professor, Professor),
                'night': (Janitor,),
                'supplemental day': [Professor],
                'supplemental night': [Professor],
            },
            Cemetery: {
                'day': (Mortician,),
                'night': (Groundskeeper,),
                'supplemental day': [],
                'supplemental night': [],
            },
            Park: {
                'day': (Groundskeeper,),
                'night': (),
                'supplemental day': [Groundskeeper, Manager],
                'supplemental night': [],
            },
            # New businesses added after the above
            Bakery: {
                'day': (),
                'night': (),
                'supplemental day': [Cashier],
                'supplemental night': [Cashier],
            },
            BlacksmithShop: {
                'day': (),
                'night': (),
                'supplemental day': [Apprentice],
                'supplemental night': [],
            },
            Brewery: {
                'day': (Brewer, Bottler, Cooper),
                'night': (),
                'supplemental day': [Brewer, Bottler, Bottler, Cooper],
                'supplemental night': [Janitor],
            },
            ButcherShop: {
                'day': (),
                'night': (),
                'supplemental day': [Cashier, Butcher],
                'supplemental night': [Cashier],
            },
            CandyStore: {
                'day': (Cashier,),
                'night': (),
                'supplemental day': [Cashier],
                'supplemental night': [Cashier],
            },
            CarpentryCompany: {
                'day': (Woodworker,),
                'night': (),
                'supplemental day': [Turner, Joiner, Secretary],
                'supplemental night': [],
            },
            ClothingStore: {
                'day': (),
                'night': (),
                'supplemental day': [Dressmaker, Seamstress],
                'supplemental night': [],
            },
            Dairy: {
                'day': (Bottler,),
                'night': (),
                'supplemental day': [Bottler],
                'supplemental night': [Bottler],
            },
            Deli: {
                'day': (Cook, Cashier),
                'night': (Cook, Cashier),
                'supplemental day': [Dishwasher],
                'supplemental night': [Dishwasher],
            },
            DentistOffice: {
                'day': (),
                'night': (),
                'supplemental day': [Secretary, Dentist],
                'supplemental night': [Janitor],
            },
            DepartmentStore: {
                'day': (Cashier, Stocker, Manager),
                'night': (Stocker, Stocker, Janitor),
                'supplemental day': [Cashier, Cashier, Stocker],
                'supplemental night': [Stocker, Stocker, Janitor],
            },
            Diner: {
                'day': (Cook,),
                'night': (Cook, Waiter),
                'supplemental day': [Dishwasher],
                'supplemental night': [Dishwasher],
            },
            Distillery: {
                'day': (Distiller, Bottler, Cooper),
                'night': (),
                'supplemental day': [Bottler, Bottler, Cooper],
                'supplemental night': [Janitor],
            },
            DrugStore: {
                'day': (),
                'night': (),
                'supplemental day': [Cashier],
                'supplemental night': [],
            },
            Farm: {
                'day': (Farmhand,),
                'night': (),
                'supplemental day': [Farmhand, Farmhand],
                'supplemental night': [],
            },
            Foundry: {
                'day': (Molder, Puddler),
                'night': (),
                'supplemental day': [Molder, Molder],
                'supplemental night': [Janitor],
            },
            FurnitureStore: {
                'day': (),
                'night': (),
                'supplemental day': [Apprentice, Cashier, Woodworker],
                'supplemental night': [Janitor],
            },
            GeneralStore: {
                'day': (),
                'night': (),
                'supplemental day': [Cashier, Stocker],
                'supplemental night': [Janitor],
            },
            GroceryStore: {
                'day': (Stocker,),
                'night': (),
                'supplemental day': [Cashier],
                'supplemental night': [Stocker, Janitor],
            },
            HardwareStore: {
                'day': (Stocker,),
                'night': (),
                'supplemental day': [],
                'supplemental night': [Janitor],
            },
            Inn: {
                'day': (),
                'night': (Innkeeper,),
                'supplemental day': [Concierge],
                'supplemental night': [],
            },
            Tavern: {
                'day': (Bartender,),
                'night': (Bartender,),
                'supplemental day': [],
                'supplemental night': [Bartender],
            },
            InsuranceCompany: {
                'day': (),
                'night': (),
                'supplemental day': [Secretary, InsuranceAgent, InsuranceAgent],
                'supplemental night': [Janitor],
            },
            JeweleryShop: {
                'day': (),
                'night': (),
                'supplemental day': [Cashier],
                'supplemental night': [],
            },
            PaintingCompany: {
                'day': (Painter, Whitewasher),
                'night': (),
                'supplemental day': [Painter],
                'supplemental night': [],
            },
            Pharmacy: {
                'day': (Pharmacist, Cashier),
                'night': (),
                'supplemental day': [],
                'supplemental night': [Janitor],
            },
            PlumbingCompany: {
                'day': (),
                'night': (),
                'supplemental day': [Secretary, Plumber],
                'supplemental night': [],
            },
            Quarry: {
                'day': (Quarryman, Stonecutter, Laborer, Laborer, Engineer),
                'night': (),
                'supplemental day': [Laborer]*100,  # Endlessly hiring more laborers if someone needs a job
                'supplemental night': [],
            },
            CoalMine: {
                'day': (Miner, Miner, Engineer),
                'night': (Miner, Miner, Miner),
                'supplemental day': [Miner]*100,  # Endlessly hiring more miners if someone needs a job
                'supplemental night': [Miner]*100,
            },
            ShoemakerShop: {
                'day': (),
                'night': (),
                'supplemental day': [Apprentice],
                'supplemental night': [],
            },
            TailorShop: {
                'day': (),
                'night': (),
                'supplemental day': [Apprentice],
                'supplemental night': [],
            },
        }
        # Occupations for which a college degree is required
        self.occupations_requiring_college_degree = {
            Doctor, Architect, Optometrist, PlasticSurgeon, Lawyer, Professor, Pharmacist, Dentist
        }
        # Job levels of various occupations (indexed by their class names)
        self.job_levels = {
            None: 0,  # Unemployed
            Apprentice: 1,
            Cashier: 1,
            Janitor: 1,
            Builder: 1,
            HotelMaid: 1,
            Waiter: 1,
            Secretary: 1,
            Laborer: 1,
            Groundskeeper: 1,
            Whitewasher: 1,
            Bottler: 1,
            Bricklayer: 1,
            Cook: 1,
            Dishwasher: 1,
            Busboy: 1,
            Stocker: 1,
            Seamstress: 1,
            Farmhand: 1,
            Miner: 1,
            Painter: 1,
            BankTeller: 2,
            Grocer: 2,
            Bartender: 2,
            Concierge: 2,
            DaycareProvider: 2,
            Landlord: 2,
            Baker: 2,
            Cooper: 2,
            Barkeeper: 2,
            Milkman: 2,
            Plasterer: 2,
            Barber: 2,
            Butcher: 2,
            Firefighter: 2,
            PoliceOfficer: 2,
            Carpenter: 2,
            TaxiDriver: 2,
            BusDriver: 2,
            Blacksmith: 2,
            Woodworker: 2,
            Stonecutter: 2,
            Dressmaker: 2,
            Distiller: 2,
            Plumber: 2,
            Joiner: 2,
            Innkeeper: 2,
            Nurse: 2,
            Farmer: 2,
            Shoemaker: 2,
            Brewer: 2,
            TattooArtist: 2,
            Puddler: 2,
            Clothier: 2,
            Teacher: 2,
            Tailor: 2,
            Molder: 2,
            Turner: 2,
            Quarryman: 2,
            Proprietor: 2,
            Manager: 2,
            Druggist: 3,
            InsuranceAgent: 3,
            Jeweler: 3,
            FireChief: 3,
            PoliceChief: 3,
            Realtor: 3,
            Principal: 3,
            Mortician: 3,
            Doctor: 4,
            Engineer: 4,
            Pharmacist: 4,
            Architect: 4,
            Optometrist: 4,
            Dentist: 4,
            PlasticSurgeon: 4,
            Lawyer: 4,
            Professor: 4,
            Owner: 5,
            Mayor: 5,
        }
        # Preconditions to various occupations that enforce historical accuracy with
        # regard to gender and occupation
        self.employable_as_a = {
            Apprentice: lambda applicant: applicant.male,
            Cashier: lambda applicant: applicant.male if applicant.game.year < 1917 else True,
            Janitor: lambda applicant: applicant.male if applicant.game.year < 1966 else True,
            Builder: lambda applicant: applicant.male if applicant.game.year < 1977 else True,
            HotelMaid: lambda applicant: applicant.female,
            Waiter: lambda applicant: applicant.male if applicant.game.year < 1917 else True,
            Secretary: lambda applicant: applicant.female,
            Laborer: lambda applicant: applicant.male,
            Groundskeeper: lambda applicant: applicant.male if applicant.game.year < 1977 else True,
            Whitewasher: lambda applicant: applicant.male if applicant.game.year < 1977 else True,
            Bottler: lambda applicant: applicant.male if applicant.game.year < 1943 else True,
            Bricklayer: lambda applicant: applicant.male,
            Cook: lambda applicant: applicant.male if applicant.game.year < 1966 else True,
            Dishwasher: lambda applicant: applicant.male if applicant.game.year < 1966 else True,
            Busboy: lambda applicant: applicant.male if applicant.game.year < 1977 else True,
            Stocker: lambda applicant: applicant.male if applicant.game.year < 1943 else True,
            Seamstress: lambda applicant: applicant.female,
            Farmhand: lambda applicant: applicant.male,
            Miner: lambda applicant: applicant.male,
            Painter: lambda applicant: applicant.male if applicant.game.year < 1977 else True,
            BankTeller: lambda applicant: applicant.male if applicant.game.year < 1950 else True,
            Grocer: lambda applicant: applicant.male if applicant.game.year < 1966 else True,
            Bartender: lambda applicant: applicant.male if applicant.game.year < 1968 else True,
            Concierge: lambda applicant: applicant.male if applicant.game.year < 1968 else True,
            DaycareProvider: lambda applicant: applicant.female if applicant.game.year < 1977 else True,
            Landlord: lambda applicant: applicant.male if applicant.game.year < 1925 else True,
            Baker: lambda applicant: applicant.male if applicant.game.year < 1935 else True,
            Cooper: lambda applicant: applicant.male if applicant.game.year < 1977 else True,
            Barkeeper: lambda applicant: applicant.male if applicant.game.year < 1977 else True,
            Milkman: lambda applicant: applicant.male if applicant.game.year < 1977 else True,
            Plasterer: lambda applicant: applicant.male if applicant.game.year < 1977 else True,
            Barber: lambda applicant: applicant.male if applicant.game.year < 1977 else True,
            Butcher: lambda applicant: applicant.male,
            Firefighter: lambda applicant: applicant.male,
            PoliceOfficer: lambda applicant: applicant.male,
            Carpenter: lambda applicant: applicant.male,
            TaxiDriver: lambda applicant: applicant.male,
            BusDriver: lambda applicant: applicant.male if applicant.game.year < 1972 else True,
            Blacksmith: lambda applicant: applicant.male,
            Woodworker: lambda applicant: applicant.male if applicant.game.year < 1977 else True,
            Stonecutter: lambda applicant: applicant.male,
            Dressmaker: lambda applicant: applicant.female if applicant.game.year < 1977 else True,
            Distiller: lambda applicant: applicant.male,
            Plumber: lambda applicant: applicant.male,
            Joiner: lambda applicant: applicant.male if applicant.game.year < 1977 else True,
            Innkeeper: lambda applicant: applicant.male if applicant.game.year < 1928 else True,
            Nurse: lambda applicant: applicant.female if applicant.game.year < 1977 else True,
            Farmer: lambda applicant: applicant.male,
            Shoemaker: lambda applicant: applicant.male if applicant.game.year < 1960 else True,
            Brewer: lambda applicant: applicant.male,
            TattooArtist: lambda applicant: applicant.male if applicant.game.year < 1972 else True,
            Puddler: lambda applicant: applicant.male,
            Clothier: lambda applicant: applicant.male if applicant.game.year < 1930 else True,
            Teacher: lambda applicant: applicant.female if applicant.game.year < 1955 else True,
            Principal: lambda applicant: (
                applicant.male if applicant.game.year < 1965 else True and
                any(o for o in applicant.occupations if o.__class__ is Teacher)
            ),
            Tailor: lambda applicant: applicant.male if applicant.game.year < 1955 else True,
            Molder: lambda applicant: applicant.male,
            Turner: lambda applicant: applicant.male if applicant.game.year < 1977 else True,
            Quarryman: lambda applicant: applicant.male,
            Proprietor: lambda applicant: applicant.male if applicant.game.year < 1955 else True,
            Manager: lambda applicant: applicant.male if applicant.game.year < 1972 else True,
            Druggist: lambda applicant: applicant.male,
            InsuranceAgent: lambda applicant: applicant.male if applicant.game.year < 1972 else True,
            Jeweler: lambda applicant: applicant.male if applicant.game.year < 1972 else True,
            FireChief: lambda applicant: (
                applicant.male and any(o for o in applicant.occupations if o.__class__ is Firefighter)
            ),
            PoliceChief: lambda applicant: (
                applicant.male and any(o for o in applicant.occupations if o.__class__ is PoliceOfficer)
            ),
            Realtor: lambda applicant: applicant.male if applicant.game.year < 1966 else True,
            Mortician: lambda applicant: applicant.male if applicant.game.year < 1977 else True,
            Doctor: lambda applicant: (
                applicant.male if applicant.game.year < 1972 else True and
                not applicant.occupations
            ),
            Engineer: lambda applicant: (
                applicant.male if applicant.game.year < 1977 else True and
                not applicant.occupations
            ),
            Pharmacist: lambda applicant: applicant.male if applicant.game.year < 1972 else True,
            Architect: lambda applicant: (
                applicant.male if applicant.game.year < 1977 else True and
                not applicant.occupations
            ),
            Optometrist: lambda applicant: (
                applicant.male if applicant.game.year < 1972 else True and
                not applicant.occupations
            ),
            Dentist: lambda applicant: (
                applicant.male if applicant.game.year < 1972 else True and
                not applicant.occupations
            ),
            PlasticSurgeon: lambda applicant: (
                applicant.male if applicant.game.year < 1977 else True and
                not applicant.occupations
            ),
            Lawyer: lambda applicant: (
                applicant.male if applicant.game.year < 1977 else True and
                not applicant.occupations
            ),
            Professor: lambda applicant: applicant.male if applicant.game.year < 1962 else True,
            Owner: lambda applicant: applicant.male if applicant.game.year < 1977 else True,
            Mayor: lambda applicant: applicant.male if applicant.game.year < 1977 else True,
        }
        # Compensation for various occupations [MAJORLY INCOMPLETE TODO]
        self.compensations = {
            Birth: {
                Owner: 500,
                Doctor: 750,
                Nurse: 300,
            },
            BusinessConstruction: {
                Owner: 5000,
                Architect: 2000,
                Builder: 400,
            },
            Death: {
                Mortician: 1000,
               # [Cemetery doesn't have an owner]
            },
            Divorce: {
                Lawyer: 1000,
                Owner: 500,
            },
            HouseConstruction: {
                Owner: 2500,
                Architect: 1000,
                Builder: 200,
            },
            HomePurchase: {
                Owner: 2000,
                Realtor: 600,
            },
            NameChange: {
                Owner: 200,
                Lawyer: 200,
            },
        }
        self.compensation_upon_building_construction_for_construction_firm_owner = 5000
        self.compensation_upon_building_construction_for_architect = 2000
        self.compensation_upon_building_construction_for_construction_worker = 400
        self.compensation_upon_home_purchase_for_realty_firm_owner = 2000
        self.compensation_upon_home_purchase_for_realtor = 600
        # People contracting people (e.g., realtors, architects)
        self.function_to_derive_score_multiplier_bonus_for_experience = (
            lambda years_experience: years_experience**0.2
        )
        self.preference_to_contract_immediate_family = 9
        self.preference_to_contract_friend = 2  # TODO have this be modified by charge
        self.dispreference_to_contract_enemy = -2  # TODO have this be modified by charge
        self.preference_to_contract_former_contract = 2
        self.preference_to_contract_extended_family = 1
        self.preference_to_contract_acquaintance = 0.5  # TODO have this be modified by charge

                #############################
                ##  PEOPLE REPRESENTATION  ##
                #############################

        # People ex nihilo
        self.function_to_determine_person_ex_nihilo_age_given_job_level = (
            lambda job_level: 18 + random.randint(2*job_level, 7*job_level)
        )
        # self.function_to_determine_chance_person_ex_nihilo_starts_with_family = (
        #     lambda age: (age / 100.0) * 1.4
        # )
        self.function_to_determine_chance_person_ex_nihilo_starts_with_family = (
            # The larger the city population, the lower the chance a P.E.N. moves
            # into town with a family
            lambda city_pop: (200.0-city_pop) / 1000.0
        )
        self.person_ex_nihilo_age_at_marriage_mean = 23
        self.person_ex_nihilo_age_at_marriage_sd = 2.7
        self.person_ex_nihilo_age_at_marriage_floor = 17
        # Infertility
        self.male_infertility_rate = 0.07
        self.female_infertility_rate = 0.11
        # Sexuality
        self.homosexuality_incidence = 0.045
        self.bisexuality_incidence = 0.01
        self.asexuality_incidence = 0.002
        # Personality (Big Five source is [0])
        self.big_five_floor = -1.0
        self.big_five_cap = 1.0
        self.big_five_heritability_chance = {
            'openness': 0.57,
            'conscientiousness': 0.54,
            'extroversion': 0.49,
            'agreeableness': 0.48,
            'neuroticism': 0.42
        }
        self.big_five_mean = {
            # These represent population means for these five traits
            'openness': 0.375,
            'conscientiousness': 0.25,
            'extroversion': 0.15,
            'agreeableness': 0.35,
            'neuroticism': 0.0
        }
        self.big_five_sd = {
            # A person's value for a trait is generated from a normal distribution
            # around the trait's mean, with the value listed here as standard deviation --
            # these are very high to make enmity a possibility, because that requires
            # personality discord, which requires a decent amount of variance
            'openness': 0.5,
            'conscientiousness': 0.5,
            'extroversion': 0.5,
            'agreeableness': 0.5,
            'neuroticism': 0.5
        }
        self.big_five_inheritance_sd = {
            # PersonMentalModel will inherit a parent's trait, but with some variance
            # according to this standard deviation
            'openness': 0.05,
            'conscientiousness': 0.05,
            'extroversion': 0.05,
            'agreeableness': 0.05,
            'neuroticism': 0.05
        }
        self.threshold_for_high_binned_personality_score = 0.4
        self.threshold_for_low_binned_personality_score = -0.4
        # Face
        self.chance_eyebrows_are_same_color_as_hair = 0.8
        self.child_skin_color_given_parents = {
            ('black', 'brown'): 'brown',
            ('brown', 'black'): 'brown',
            ('black', 'beige'): 'brown',
            ('beige', 'black'): 'brown',
            ('black', 'pink'): 'beige',
            ('pink', 'black'): 'beige',
            ('black', 'white'): 'beige',
            ('white', 'black'): 'beige',
            ('brown', 'beige'): 'beige',
            ('beige', 'brown'): 'beige',
            ('brown', 'pink'): 'beige',
            ('pink', 'brown'): 'beige',
            ('brown', 'white'): 'beige',
            ('white', 'brown'): 'beige',
            ('beige', 'pink'): 'beige',
            ('pink', 'beige'): 'beige',
            ('beige', 'white'): 'beige',
            ('white', 'beige'): 'beige',
            ('pink', 'white'): 'pink',
            ('white', 'pink'): 'pink',
        }
        self.facial_feature_type_heritability = {
            "skin color": 1.0,
            "head size": 0.75,
            "head shape": 0.75,
            "hair length": 0.05,  # From nurture, not nature
            "hair color": 0.75,
            "eyebrow size": 0.75,
            "eyebrow color": 0.75,
            "mouth size": 0.75,
            "ear size": 0.75,
            "ear angle": 0.75,
            "nose size": 0.75,
            "nose shape": 0.75,
            "eye size": 0.75,
            "eye shape": 0.75,
            "eye color": 0.75,
            "eye horizontal settedness": 0.75,
            "eye vertical settedness": 0.75,
            "facial hair style": 0.05,  # From nurture
            "freckles": 0.75,
            "birthmark": 0.00,
            "scar": 0.00,
            "tattoo": 0.05,  # From nurture
            "glasses": 0.6,
            "sunglasses": 0.05  # From nurture
        }
        self.facial_feature_variant_heritability = {
            "skin color": 1.0,
            "head size": 0.75,
            "head shape": 0.75,
            "hair length": 0.05,  # From nurture, not nature
            "hair color": 0.75,
            "eyebrow size": 0.75,
            "eyebrow color": 0.75,
            "mouth size": 0.75,
            "ear size": 0.75,
            "ear angle": 0.75,
            "nose size": 0.75,
            "nose shape": 0.75,
            "eye size": 0.75,
            "eye shape": 0.75,
            "eye color": 0.75,
            "eye horizontal settedness": 0.75,
            "eye vertical settedness": 0.75,
            "facial hair style": 0.0,
            "freckles": 0.75,
            "birthmark": 0.0,
            "scar": 0.0,
            "tattoo": 0.05,  # From nurture
            "glasses": 0.6,
            "sunglasses": 0.05  # From nurture
        }
        self.facial_feature_chance_inheritance_according_to_sex = {
            # The chance someone inherits only from parent/grandparent of the same sex, given
            # the dice already has them inheriting and not generating from population distribution
            "head size": 0.8,
            "head shape": 0.8,
            "hair length": 1.0,
            "hair color": 0.0,
            "eyebrow size": 0.0,
            "eyebrow color": 0.0,
            "mouth size": 0.0,
            "ear size": 0.0,
            "ear angle": 0.0,
            "nose size": 0.0,
            "nose shape": 0.0,
            "eye size": 0.0,
            "eye shape": 0.0,
            "eye color": 0.0,
            "eye horizontal settedness": 0.0,
            "eye vertical settedness": 0.0,
            "facial hair style": 1.0,
            "freckles": 0.0,
            "birthmark": 0.0,
            "scar": 0.0,
            "tattoo": 0.0,  # From nurture
            "glasses": 0.0,
            "sunglasses": 0.00  # From nurture
        }
        self.facial_feature_distributions_male = {
            "skin color": [
                # A random float between 0.0 and 1.0 will be generated and the skin
                # color whose range that number falls in will be assigned
                ((0.0, 0.1), 'black'),
                ((0.1, 0.2), 'brown'),
                ((0.2, 0.4), 'beige'),
                ((0.4, 0.6), 'pink'),
                ((0.6, 1.0), 'white')
            ],
            "head size": [
                ((0.0, 0.2), 'small'),
                ((0.2, 0.5), 'medium'),
                ((0.5, 1.0), 'large'),
            ],
            "head shape": [
                ((0.0, 0.4), 'square'),
                ((0.4, 0.6), 'circle'),
                ((0.6, 0.65), 'heart'),
                ((0.65, 1.0), 'oval')
            ],
            "hair length": [
                # TODO make this depend on era
                ((0.0, 0.0), 'bald'),
                ((0.0, 0.65), 'short'),
                ((0.65, 0.95), 'medium'),
                ((0.95, 1.0), 'long')
            ],
            "hair color": [
                ((0.0, 0.4), 'black'),
                ((0.4, 0.75), 'brown'),
                ((0.75, 0.9), 'blonde'),
                ((0.9, 1.0), 'red'),
                ((999, 999), 'gray'),
                ((999, 999), 'white'),
                ((999, 999), 'green'),
                ((999, 999), 'blue'),
                ((999, 999), 'purple')
            ],
            "eyebrow size": [
                ((0.0, 0.3), 'small'),
                ((0.3, 0.7), 'medium'),
                ((0.7, 0.9), 'large'),
                ((0.9, 1.0), 'unibrow'),
            ],
            "eyebrow color": [
                ((0.0, 0.35), 'black'),
                ((0.35, 0.55), 'brown'),
                ((0.55, 0.75), 'blonde'),
                ((0.75, 0.8), 'red'),
                ((0.8, 0.875), 'gray'),
                ((0.875, 0.95), 'white'),
                ((0.95, 0.97), 'green'),
                ((0.97, 0.99), 'blue'),
                ((0.99, 1.0), 'purple')
            ],
            "mouth size": [
                ((0.0, 0.3), 'small'),
                ((0.3, 0.7), 'medium'),
                ((0.7, 1.0), 'large')
            ],
            "ear size": [
                ((0.0, 0.3), 'small'),
                ((0.3, 0.7), 'medium'),
                ((0.7, 1.0), 'large')
            ],
            "ear angle": [
                ((0.0, 0.8), 'flat'),
                ((0.8, 1.0), 'protruding')
            ],
            "nose size": [
                ((0.0, 0.3), 'small'),
                ((0.3, 0.7), 'medium'),
                ((0.7, 1.0), 'large')
            ],
            "nose shape": [
                ((0.0, 0.4), 'long'),
                ((0.4, 0.6), 'broad'),
                ((0.6, 0.8), 'upturned'),
                ((0.8, 1.0), 'pointy')
            ],
            "eye size": [
                ((0.0, 0.3), 'small'),
                ((0.3, 0.7), 'medium'),
                ((0.7, 1.0), 'large')
            ],
            "eye shape": [
                ((0.0, 0.6), 'round'),
                ((0.6, 0.7), 'almond'),
                ((0.7, 1.0), 'thin')
            ],
            "eye color": [
                ((0.0, 0.3), 'black'),
                ((0.3, 0.5), 'brown'),
                ((0.5, 0.65), 'blue'),
                ((0.65, 0.8), 'green'),
                ((0.8, 0.88), 'yellow'),
                ((0.88, 0.96), 'gray'),
                ((0.96, 0.98), 'red'),
                ((0.98, 0.99), 'purple'),
                ((0.99, 1.0), 'white'),
            ],
            "eye horizontal settedness": [
                ((0.0, 0.3), 'narrow'),
                ((0.3, 0.7), 'middle'),
                ((0.7, 1.0), 'wide'),
            ],
            "eye vertical settedness": [
                ((0.0, 0.3), 'high'),
                ((0.3, 0.7), 'middle'),
                ((0.7, 1.0), 'low'),
            ],
            "facial hair style": [
                ((0.0, 0.5), 'none'),
                ((0.5, 0.65), 'mustache'),
                ((0.65, 0.8), 'full beard'),
                ((0.8, 0.9), 'goatee'),
                ((0.9, 0.97), 'sideburns'),
                ((0.97, 1.0), 'soul patch'),
            ],
            "freckles": [
                ((0.0, 0.8), 'no'),  # These aren't booleans because Face.Feature extends str, not bool
                ((0.8, 1.0), 'yes'),
            ],
            "birthmark": [
                ((0.0, 0.85), 'no'),
                ((0.85, 1.0), 'yes'),
            ],
            "scar": [
                ((0.0, 0.85), 'no'),
                ((0.85, 1.0), 'yes'),
            ],
            "tattoo": [
                ((0.0, 0.95), 'no'),
                ((0.95, 1.0), 'yes'),
            ],
            "glasses": [
                ((0.0, 0.7), 'no'),
                ((0.7, 1.0), 'yes'),
            ],
            "sunglasses": [
                ((0.0, 0.8), 'no'),
                ((0.8, 1.0), 'yes'),
            ]
        }
        self.facial_feature_distributions_female = {
            "skin color": self.facial_feature_distributions_male["skin color"],
            "head size": [
                ((0.0, 0.6), 'small'),
                ((0.6, 0.8), 'medium'),
                ((0.8, 1.0), 'large'),
            ],
            "head shape": [
                ((0.0, 0.1), 'square'),
                ((0.1, 0.3), 'circle'),
                ((0.3, 0.8), 'heart'),
                ((0.8, 1.0), 'oval'),
            ],
            "hair length": [
                ((0.0, 0.0), 'bald'),
                ((0.0, 0.2), 'short'),
                ((0.2, 0.45), 'medium'),
                ((0.45, 1.0), 'long'),
            ],
            "hair color": self.facial_feature_distributions_male["hair color"],
            "eyebrow size": [
                ((0.0, 0.7), 'small'),
                ((0.7, 0.9), 'medium'),
                ((0.9, 0.95), 'large'),
                ((0.95, 1.0), 'unibrow'),
            ],
            "eyebrow color": self.facial_feature_distributions_male["eyebrow color"],
            "mouth size": [
                ((0.0, 0.6), 'small'),
                ((0.6, 0.85), 'medium'),
                ((0.85, 1.0), 'large'),
            ],
            "ear size": [
                ((0.0, 0.6), 'small'),
                ((0.6, 0.85), 'medium'),
                ((0.85, 1.0), 'large'),
            ],
            "ear angle": self.facial_feature_distributions_male["ear angle"],
            "nose size": self.facial_feature_distributions_male["nose size"],
            "nose shape": self.facial_feature_distributions_male["nose shape"],
            "eye size": self.facial_feature_distributions_male["eye size"],
            "eye shape": self.facial_feature_distributions_male["eye shape"],
            "eye color": self.facial_feature_distributions_male["eye color"],
            "eye horizontal settedness": self.facial_feature_distributions_male["eye horizontal settedness"],
            "eye vertical settedness": self.facial_feature_distributions_male["eye vertical settedness"],
            "facial hair style": [
                ((0.0, 1.0), 'none'),
                ((0.0, 0.0), 'mustache'),
                ((0.0, 0.0), 'full beard'),
                ((0.0, 0.0), 'goatee'),
                ((0.0, 0.0), 'sideburns'),
                ((0.0, 0.0), 'soul patch'),
            ],
            "freckles": self.facial_feature_distributions_male["freckles"],
            "birthmark": self.facial_feature_distributions_male["birthmark"],
            "scar": self.facial_feature_distributions_male["scar"],
            "tattoo": self.facial_feature_distributions_male["tattoo"],
            "glasses": self.facial_feature_distributions_male["glasses"],
            "sunglasses": self.facial_feature_distributions_male["sunglasses"],
        }
        # Names
        self.chance_son_inherits_fathers_exact_name = 0.03
        self.chance_child_inherits_first_name = 0.1
        self.chance_child_inherits_middle_name = 0.25
        self.frequency_of_naming_after_father = 12
        self.frequency_of_naming_after_grandfather = 5
        self.frequency_of_naming_after_greatgrandfather = 2
        self.frequency_of_naming_after_mother = 0
        self.frequency_of_naming_after_grandmother = 5
        self.frequency_of_naming_after_greatgrandmother = 2

                ##############
                ##  MEMORY  ##
                ##############

        self.memory_mean = 1.0
        self.memory_sd = 0.05
        self.memory_cap = 1.0
        self.memory_floor = 0.5  # After severe memory loss from aging
        self.memory_floor_at_birth = 0.8  # Worst possible memory of newborn
        self.memory_sex_diff = 0.03  # Men have worse memory, studies show
        self.memory_heritability = 0.6  # Couldn't quickly find a study on this -- totally made up
        self.memory_heritability_sd = 0.05

                ################
                ##  SALIENCE  ##
                ################

        self.salience_increment_for_social_interaction = 0.1  # Salience increment from a single social interaction
        self.salience_increment_from_relationship_change = {
            "acquaintance": 0.5,
            "former neighbor": 0.75,
            "former coworker": 1.0,
            "neighbor": 1.25,
            "coworker": 1.5,
            "descendant": 1.5,
            "ancestor": 1.5,
            "extended family": 1.5,
            "friend": 2,
            "enemy": 2,
            "immediate family": 2,
            "love interest": 3,
            "best friend": 1,  # Remember, this is a boost on top of the value for friend
            "worst enemy": 1,
            "significant other": 5,
            "self": 10,
        }
        self.salience_job_level_boost = (
            lambda job_level: job_level * 0.35
        )

                #################
                ##  KNOWLEDGE  ##
                #################

        # These parameters effect implant formation/strength
        self.social_and_salience_component_of_implant_strength = (
            # The salience * 10 is meant to simulate how many social interactions they
            # should have had, given how salient subject is to source -- this number
            # will eventually be multiplied by the strength of a single observation as
            # as a simulation of that many observations having occurred over that many
            # social interactions
            lambda total_interactions, salience: total_interactions + (salience * 5)
        )
        self.salience_of_features_with_regard_to_implants = {
            # These values are used to determine the strength of an implant piece
            # of evidence for a feature of the given type, and they are also used to
            # determine whether a feature type will even show up in an implant in
            # the first place
            "status":                      0.99,
            "first name":                  0.80,
            "last name":                   0.80,
            "home":                        0.70,
            "workplace":                   0.70,
            "surname ethnicity":           0.70,
            "skin color":                  0.70,
            "tattoo":                      0.50,
            "suffix":                      0.70,
            "approximate age":             0.70,
            "marital status":              0.65,
            "scar":                        0.40,
            "job title":                   0.40,
            "job status":                  0.35,
            "job shift":                   0.30,
            "hair color":                  0.20,
            "hair length":                 0.20,
            "hyphenated surname":          0.15,
            "death year":                  0.10,
            "departure year":              0.08,
            "birthmark":                   0.05,
            "facial hair style":           0.05,
            "freckles":                    0.05,
            "glasses":                     0.05,
            "sunglasses":                  0.05,
            "birth year":                  0.05,
            "head size":                   0.04,
            "eye color":                   0.01,
            "middle name":                 0.01,
            "ear angle":                   0.01,
            "eye horizontal settedness":   0.01,
            "nose size":                   0.01,
            # These simply won't come up in implants -- no point to
            # actually add them to the dictionary, so I keep them commented here
            # for reference only
            # ("eye vertical settedness",     0.00),
            # ("head shape",                  0.00),
            # ("eyebrow size",                0.00),
            # ("eyebrow color",               0.00),
            # ("mouth size",                  0.00),
            # ("ear size",                    0.00),
            # ("nose shape",                  0.00),
            # ("eye size",                    0.00),
            # ("eye shape",                   0.00),
        }
        self.general_salience_of_features = {
            # These values are multiplied against the strength of a piece of
            # evidence when determining the strength of a particular belief facet --
            # e.g., it will mean that an observation of a person's hair color is
            # self.general_salience_of_features["hair color"] *
            # self.strength_of_evidence_type["observation"]
            "status":                      1.50,  # Seeing someone alive or dead makes a very strong observation
            "approximate age":             1.00,
            "hair color":                  1.00,
            "skin color":                  1.00,
            "tattoo":                      1.00,
            "scar":                        1.00,
            "hyphenated surname":          1.00,
            "birthmark":                   1.00,
            "home is apartment":           1.00,
            "job status":                  1.00,
            "home":                        0.90,
            "hair length":                 0.90,
            "workplace":                   0.90,
            "job title":                   0.90,
            "job shift":                   0.90,
            "facial hair style":           0.90,
            "freckles":                    0.90,
            "glasses":                     0.85,
            "sunglasses":                  0.85,
            "marital status":              0.80,
            "first name":                  0.80,
            "surname ethnicity":           0.80,
            "suffix":                      0.80,
            "whereabouts XYZ":             0.80,  # This is handled a little differently due to whereabouts naming
            "last name":                   0.70,
            "business block":              0.70,
            "business name":               0.70,
            "home block":                  0.70,
            "nose size":                   0.40,
            "middle name":                 0.30,
            "home address":                0.30,
            "death year":                  0.15,
            "departure year":              0.15,
            "business address":            0.10,
            "eye color":                   0.10,
            "head size":                   0.10,
            "birth year":                  0.10,
            "ear angle":                   0.08,
            "eye horizontal settedness":   0.05,
            "eye vertical settedness":     0.05,
            "head shape":                  0.05,
            "eyebrow size":                0.05,
            "eyebrow color":               0.05,
            "mouth size":                  0.05,
            "ear size":                    0.05,
            "nose shape":                  0.05,
            "eye size":                    0.05,
            "eye shape":                   0.05,
        }
        self.chance_someone_observes_nearby_entity = 0.75
        self.chance_someone_eavesdrops_statement_or_lie = 0.05
        self.base_strength_of_evidence_types = {
            "reflection": 9999,
            "observation": 20,
            "examination": 15,
            "statement": 5,
            "lie": 5,
            "eavesdropping": 5,
            "confabulation": 3,
            "mutation": 3,
            "transference": 3,
            "declaration": 2,
            "forgetting": 0.001,
        }
        self.feature_types_that_do_not_mutate = {
            'job title', 'status', 'approximate age', 'suffix', 'marital status', 'business name'
        }
        self.decay_rate_of_belief_strength_per_day = 0.95  # Lose 5% of strength every day
        three_fourths_strength_of_firsthand_observation = (
            self.base_strength_of_evidence_types['observation'] /
            self.base_strength_of_evidence_types["statement"] *
            0.75
        )
        self.function_to_determine_trust_charge_boost = (
            # Min of 0.5, max equal to 3/4 strength of a firsthand observation, all else 1 + (charge/2500.)
            lambda charge: max(0.5, min(1 + (max(0.1, charge)/2500), three_fourths_strength_of_firsthand_observation))
        )
        self.minimum_teller_belief_strength = 1.0
        self.function_to_determine_teller_strength_boost = (
            # Min of 0.25, max of 1.5, and the denominator of 15.0 makes 225 equal to a 1.0 boost;
            # the max(0.1, teller_belief_strength) term is there to prevent a negative number being
            # passed to math.sqrt, which raises a 'math domain error'
            lambda teller_belief_strength: max(0.25, min(math.sqrt(max(0.1, teller_belief_strength))/15.0, 1.5))
        )
        self.trust_someone_has_for_random_person_they_eavesdrop = 0.5
        self.function_to_determine_evidence_boost_for_strength_of_teller_belief = (
            lambda teller_belief_strength: teller_belief_strength
        )
        self.status_feature_types = ("status", "departure_year", "marital_status")
        self.age_feature_types = ("birth year", "death year", "approximate age")
        self.name_feature_types = (
            "first name", "middle name", "last name", "suffix", "hyphenated surname", "surname ethnicity"
        )
        self.work_feature_types = ("workplace", "job title", "job shift", "job status")
        self.home_feature_types = ("home",)
        self.chance_someone_lies_floor = 0.02
        self.chance_someone_lies_cap = 0.2
        self.amount_of_people_people_talk_about_floor = 2
        # self.amount_of_people_people_talk_about_cap = 7  # CAP IS NOW NATURALLY AT 7
        self.chance_someones_feature_comes_up_in_conversation_about_them = (
            ("status",                      1.00),
            ("first name",                  0.80),
            ("approximate age",             0.70),
            ("job status",                  0.70),
            ("workplace",                   0.50),
            ("job title",                   0.30),
            ("job shift",                   0.30),
            ("last name",                   0.25),
            ("surname ethnicity",           0.15),
            ("hyphenated surname",          0.15),
            ("home",                        0.15),
            ("marital status",              0.15),
            ("tattoo",                      0.10),
            ("skin color",                  0.10),
            ("hair color",                  0.08),
            ("hair length",                 0.08),
            ("suffix",                      0.08),
            ("scar",                        0.05),
            ("birthmark",                   0.05),
            ("facial hair style",           0.05),
            ("freckles",                    0.05),
            ("glasses",                     0.05),
            ("sunglasses",                  0.05),
            ("head size",                   0.04),
            ("death year",                  0.04),
            ("birth year",                  0.04),
            ("departure year",              0.04),
            ("eye color",                   0.01),
            ("middle name",                 0.01),
            ("ear angle",                   0.01),
            # These simply won't come up in conversation -- no point to
            # actually iterate over them, so I keep them commented here
            # for reference only
            # ("eye horizontal settedness",   0.00),
            # ("eye vertical settedness",     0.00),
            # ("head shape",                  0.00),
            # ("eyebrow size",                0.00),
            # ("eyebrow color",               0.00),
            # ("mouth size",                  0.00),
            # ("ear size",                    0.00),
            # ("nose size",                   0.00),
            # ("nose shape",                  0.00),
            # ("eye size",                    0.00),
            # ("eye shape",                   0.00),
            # ("home address",                0.00),
        )
        self.feature_is_observable = {
            "first name": lambda subject: True,
            "last name": lambda subject: True,
            "surname ethnicity": lambda subject: True,
            "skin color": lambda subject: True,
            "workplace": lambda subject: subject.routine.working,
            "tattoo": lambda subject: True,
            "scar": lambda subject: True,
            "job status": lambda subject: subject.routine.working,
            "job title": lambda subject: subject.routine.working,
            "job shift": lambda subject: subject.routine.working,
            "hair color": lambda subject: True,
            "hair length": lambda subject: True,
            "hyphenated surname": lambda subject: True,
            "home": lambda subject: subject.location is subject.home,
            "birthmark": lambda subject: True,
            "facial hair style": lambda subject: True,
            "freckles": lambda subject: True,
            "glasses": lambda subject: True,
            "sunglasses": lambda subject: True,
            "head size": lambda subject: True,
            "eye color": lambda subject: True,
            "middle name": lambda subject: False,
            "suffix": lambda subject: False,
            "ear angle": lambda subject: True,
            "eye horizontal settedness": lambda subject: True,
            "nose size": lambda subject: True,
            "eye vertical settedness": lambda subject: True,
            "head shape": lambda subject: True,
            "eyebrow size": lambda subject: True,
            "eyebrow color": lambda subject: True,
            "mouth size": lambda subject: True,
            "ear size": lambda subject: True,
            "nose shape": lambda subject: True,
            "eye size": lambda subject: True,
            "eye shape": lambda subject: True,
            "birth year": lambda subject: False,
            "death year": lambda subject: False,
            "approximate age": lambda subject: True,
            "status": lambda subject: True,  # whether subject is alive, dead, or departed
            "marital_status": lambda subject: subject.wedding_ring_on_finger,
            "departure_year": lambda subject: False,
        }
        self.person_feature_salience = {
            # (Sources [2, 3] show that hair, eyes > mouth > nose, chin.)
            # These values represent means (for someone with memory value of self.memory_mean),
            # floors, and caps for the base chance someone perfectly remembers a feature of
            # a person of this type (the base chance gets multiplied by the person's memory);
            # if a feature isn't remembered perfectly, it will immediately deteriorate by
            # mutation, transference, or forgetting
            #                               MEAN    FLOOR   CAP
            "status":                       (1.00,  1.00,   1.00),
            "approximate age":              (0.99,  0.97,   0.99),
            "hyphenated surname":           (0.98,  0.90,   0.99),
            "skin color":                   (0.95,  0.80,   0.99),
            "tattoo":                       (0.95,  0.80,   0.99),
            "birthmark":                    (0.90,  0.70,   0.99),
            "job status":                   (0.90,  0.70,   0.99),
            "scar":                         (0.90,  0.70,   0.99),
            "facial hair style":            (0.90,  0.70,   0.99),
            "glasses":                      (0.90,  0.70,   0.96),
            "sunglasses":                   (0.90,  0.70,   0.96),
            "freckles":                     (0.85,  0.50,   0.95),
            "hair color":                   (0.85,  0.50,   0.95),
            "hair length":                  (0.80,  0.50,   0.95),
            "marital status":               (0.80,  0.50,   0.95),
            "head size":                    (0.75,  0.45,   0.90),
            "head shape":                   (0.75,  0.45,   0.90),
            "first name":                   (0.75,  0.45,   0.90),
            "surname ethnicity":            (0.70,  0.45,   0.90),
            "suffix":                       (0.70,  0.45,   0.90),
            "eye horizontal settedness":    (0.70,  0.40,   0.90),
            "eye vertical settedness":      (0.70,  0.40,   0.90),
            "eye size":                     (0.67,  0.40,   0.90),
            "eye color":                    (0.67,  0.40,   0.90),
            "eye shape":                    (0.65,  0.35,   0.90),
            "mouth size":                   (0.60,  0.25,   0.80),
            "workplace":                    (0.60,  0.25,   0.80),
            "job shift":                    (0.60,  0.25,   0.80),
            "last name":                    (0.55,  0.25,   0.75),
            "job title":                    (0.55,  0.25,   0.75),
            "nose size":                    (0.45,  0.20,   0.70),
            "nose shape":                   (0.45,  0.20,   0.70),
            "eyebrow size":                 (0.45,  0.20,   0.70),
            "eyebrow color":                (0.45,  0.20,   0.70),
            "ear size":                     (0.30,  0.10,   0.50),
            "ear angle":                    (0.30,  0.10,   0.50),
            "death year":                   (0.30,  0.10,   0.50),
            "departure year":               (0.20,  0.10,   0.35),
            "birth year":                   (0.20,  0.10,   0.35),
            "middle name":                  (0.01,  0.05,   0.30),
        }
        # Chance of memory deterioration happening on a given timestep -- the chance
        # for each belief facet of it deteriorating on a given timestep (can be thought
        # of as representing the expected number of days a belief facet will remain intact
        # without a person seeing the person in question to reinforce the true feature);
        # this gets divided by a person's memory and divided by the strength of the belief facet
        self.chance_of_memory_deterioration_on_a_given_timestep = {
            "status":                       0.0025,
            "hyphenated surname":           0.005,
            "approximate age":              0.01,
            "home block":                   0.01,
            "skin color":                   0.01,
            "tattoo":                       0.01,
            "birthmark":                    0.02,
            "scar":                         0.02,
            "job status":                   0.02,
            "suffix":                       0.03,
            "hair length":                  0.05,
            "facial hair style":            0.05,
            "glasses":                      0.05,
            "sunglasses":                   0.05,
            "job shift":                    0.05,
            "surname ethnicity":            0.05,
            "first name":                   0.08,
            "ear angle":                    0.10,
            "workplace":                    0.10,
            "home is apartment":            0.10,
            "home":                         0.10,
            "last name":                    0.15,
            "job title":                    0.15,
            "freckles":                     0.15,
            "hair color":                   0.15,
            "marital status":               0.15,
            "home address":                 0.15,
            "death year":                   0.20,
            "middle name":                  0.20,
            "head size":                    0.20,
            "head shape":                   0.20,
            "business block":               0.25,
            "business name":                0.25,
            "eye horizontal settedness":    0.25,
            "eye vertical settedness":      0.25,
            "eye size":                     0.25,
            "eye color":                    0.25,
            "eye shape":                    0.25,
            "mouth size":                   0.35,
            "birth year":                   0.35,
            "departure year":               0.35,
            "nose size":                    0.35,
            "nose shape":                   0.35,
            "eyebrow size":                 0.40,
            "eyebrow color":                0.40,
            "ear size":                     0.40,
            "business address":             0.65,
            "":                             0.03,  # Chance of confabulation, essentially
        }
        # Chance of certain types of memory deterioration -- note that these chances only
        # get reference when it's already been decided that some piece of knowledge
        # will get polluted/forgotten; as such, these chances are only relative to
        # one another
        self.memory_pollution_probabilities = (
            ((0.0, 0.7), 'f'),  # Random number in this range triggers forgetting
            ((0.7, 0.9), 'm'),  # Mutation
            ((0.9, 1.0), 't'),  # Transference
        )
        self.chance_of_confabulation_on_a_given_timestep = 0.02
        self.chance_someone_confabulates_a_suffix = 0.05  # Else they will confabulate 'None'
        self.age_confabulation_max_offset = lambda subject: subject.age/7.0
        self.memory_mutations = {
            # Probabilities specifying how feature values are likely to degrade
            # NAMES [handled differently]
            # WORK LIFE

            # APPEARANCE
            "skin color": {
                'black': (
                    ((0.0, 0.7), 'brown'),
                    ((0.7, 0.95), 'beige'),
                    ((0.95, 0.975), 'pink'),
                    ((0.975, 1.0), 'white'),
                ),
                'brown': (
                    ((0.0, 0.475), 'black'),
                    ((0.475, 0.95), 'beige'),
                    ((0.95, 0.975), 'pink'),
                    ((0.975, 1.0), 'white'),
                ),
                'beige': (
                    ((0.0, 0.24), 'black'),
                    ((0.24, 0.7), 'brown'),
                    ((0.7, 0.94), 'pink'),
                    ((0.94, 1.0), 'white'),
                ),
                'pink': (
                    ((0.0, 0.475), 'white'),
                    ((0.475, 0.95), 'beige'),
                    ((0.95, 0.975), 'brown'),
                    ((0.975, 1.0), 'black'),
                ),
                'white': (
                    ((0.0, 0.7), 'pink'),
                    ((0.7, 0.95), 'beige'),
                    ((0.95, 0.975), 'brown'),
                    ((0.975, 1.0), 'black'),
                ),
            },
            "head size": {
                'small': (
                    ((0.0, 0.8), 'medium'),
                    ((0.8, 1.0), 'large'),
                ),
                'medium': (
                    ((0.0, 0.5), 'small'),
                    ((0.5, 1.0), 'large'),
                ),
                'large': (
                    ((0.0, 0.8), 'medium'),
                    ((0.8, 1.0), 'small'),
                ),
            },
            "head shape": {
                'square': (
                    ((0.0, 0.4), 'circle'),
                    ((0.4, 0.8), 'oval'),
                    ((0.8, 1.0), 'heart'),
                ),
                'circle': (
                    ((0.0, 0.1), 'square'),
                    ((0.1, 0.7), 'oval'),
                    ((0.7, 1.0), 'heart'),
                ),
                'oval': (
                    ((0.0, 0.1), 'square'),
                    ((0.1, 0.7), 'circle'),
                    ((0.7, 1.0), 'heart'),
                ),
                'heart': (
                    ((0.0, 0.4), 'circle'),
                    ((0.4, 0.8), 'oval'),
                    ((0.8, 1.0), 'square'),
                ),
            },
            "hair length": {
                'bald': (
                    ((0.0, 0.9), 'short'),
                    ((0.9, 0.95), 'medium'),
                    ((0.95, 1.0), 'long'),
                ),
                'short': (
                    ((0.0, 0.2), 'bald'),
                    ((0.2, 0.9), 'medium'),
                    ((0.9, 1.0), 'long'),
                ),
                'medium': (
                    ((0.0, 0.05), 'bald'),
                    ((0.05, 0.525), 'short'),
                    ((0.525, 1.0), 'long'),
                ),
                'long': (
                    ((0.0, 0.9), 'medium'),
                    ((0.9, 0.95), 'short'),
                    ((0.95, 1.0), 'bald'),
                ),
            },
            "hair color": {
                'black': (
                    ((0.0, 0.8), 'brown'),
                    ((0.8, 0.85), 'purple'),
                    ((0.85, 0.9), 'blue'),
                    ((0.9, 0.95), 'red'),
                    ((0.95, 0.96), 'blonde'),
                    ((0.96, 0.97), 'gray'),
                    ((0.97, 0.98), 'white'),
                    ((0.98, 1.0), 'green'),
                ),
                'brown': (
                    ((0.0, 0.7), 'black'),
                    ((0.7, 0.95), 'red'),
                    ((0.95, 0.98), 'blonde'),
                    ((0.98, 0.985), 'purple'),
                    ((0.985, 0.99), 'blue'),
                    ((0.99, 0.995), 'gray'),
                    ((0.995, 0.999), 'white'),
                    ((0.999, 1.0), 'green'),
                ),
                'red': (
                    ((0.0, 0.8), 'brown'),
                    ((0.8, 0.95), 'black'),
                    ((0.95, 0.98), 'blonde'),
                    ((0.98, 0.985), 'purple'),
                    ((0.985, 0.99), 'blue'),
                    ((0.99, 0.995), 'gray'),
                    ((0.995, 0.999), 'white'),
                    ((0.999, 1.0), 'green'),
                ),
                'blonde': (
                    ((0.0, 0.7), 'brown'),
                    ((0.7, 0.95), 'gray'),
                    ((0.95, 0.98), 'red'),
                    ((0.98, 0.985), 'purple'),
                    ((0.985, 0.99), 'blue'),
                    ((0.99, 0.995), 'black'),
                    ((0.995, 0.999), 'white'),
                    ((0.999, 1.0), 'green'),
                ),
                'gray': (
                    ((0.0, 0.8), 'white'),
                    ((0.8, 0.85), 'black'),
                    ((0.85, 0.9), 'blonde'),
                    ((0.9, 0.95), 'red'),
                    ((0.95, 0.96), 'blue'),
                    ((0.96, 0.97), 'purple'),
                    ((0.97, 0.98), 'brown'),
                    ((0.98, 1.0), 'green'),
                ),
                'white': (
                    ((0.0, 0.8), 'gray'),
                    ((0.8, 0.85), 'black'),
                    ((0.85, 0.9), 'blonde'),
                    ((0.9, 0.95), 'red'),
                    ((0.95, 0.96), 'blue'),
                    ((0.96, 0.97), 'purple'),
                    ((0.97, 0.98), 'brown'),
                    ((0.98, 1.0), 'green'),
                ),
                'purple': (
                    ((0.0, 0.6), 'blue'),
                    ((0.6, 0.8), 'green'),
                    ((0.8, 0.85), 'red'),
                    ((0.85, 0.9), 'black'),
                    ((0.9, 0.93), 'brown'),
                    ((0.93, 0.95), 'gray'),
                    ((0.95, 0.96), 'blonde'),
                    ((0.96, 1.0), 'white'),
                ),
                'green': (
                    ((0.0, 0.6), 'blue'),
                    ((0.6, 0.8), 'purple'),
                    ((0.8, 0.85), 'red'),
                    ((0.85, 0.9), 'black'),
                    ((0.9, 0.93), 'brown'),
                    ((0.93, 0.95), 'gray'),
                    ((0.95, 0.96), 'blonde'),
                    ((0.96, 1.0), 'white'),
                ),
                'blue': (
                    ((0.0, 0.6), 'purple'),
                    ((0.6, 0.8), 'green'),
                    ((0.8, 0.85), 'red'),
                    ((0.85, 0.9), 'black'),
                    ((0.9, 0.93), 'brown'),
                    ((0.93, 0.95), 'gray'),
                    ((0.95, 0.96), 'blonde'),
                    ((0.96, 1.0), 'white'),
                ),
            },
            "ear angle": {
                'flat': (
                    ((0.0, 1.0), 'protruding'),  # Only one thing to possibly mutate into
                ),
                'protruding': (
                    ((0.0, 1.0), 'flat'),
                ),
            },
            "nose shape": {
                'long': (
                    ((0.0, 0.4), 'pointy'),
                    ((0.4, 0.6), 'broad'),
                    ((0.6, 1.0), 'upturned'),
                ),
                'pointy': (
                    ((0.0, 0.4), 'long'),
                    ((0.4, 0.6), 'broad'),
                    ((0.6, 1.0), 'upturned'),
                ),
                'broad': (
                    ((0.0, 0.4), 'pointy'),
                    ((0.4, 0.6), 'long'),
                    ((0.6, 1.0), 'upturned'),
                ),
                'upturned': (
                    ((0.0, 0.4), 'pointy'),
                    ((0.4, 0.6), 'broad'),
                    ((0.6, 1.0), 'long'),
                ),
            },
            "eye shape": {
                'round': (
                    ((0.0, 0.3), 'thin'),
                    ((0.3, 1.0), 'almond'),
                ),
                'thin': (
                    ((0.0, 0.5), 'round'),
                    ((0.5, 1.0), 'almond'),
                ),
                'almond': (
                    ((0.0, 0.3), 'thin'),
                    ((0.3, 1.0), 'round'),
                ),
            },
            "eye color": {
                'black': (
                    ((0.0, 0.8), 'brown'),
                    ((0.8, 0.85), 'purple'),
                    ((0.85, 0.9), 'blue'),
                    ((0.9, 0.95), 'red'),
                    ((0.95, 0.96), 'yellow'),
                    ((0.96, 0.97), 'gray'),
                    ((0.97, 0.98), 'white'),
                    ((0.98, 1.0), 'green'),
                ),
                'brown': (
                    ((0.0, 0.7), 'black'),
                    ((0.7, 0.95), 'red'),
                    ((0.95, 0.98), 'yellow'),
                    ((0.98, 0.985), 'purple'),
                    ((0.985, 0.99), 'blue'),
                    ((0.99, 0.995), 'gray'),
                    ((0.995, 0.999), 'white'),
                    ((0.999, 1.0), 'green'),
                ),
                'red': (
                    ((0.0, 0.8), 'brown'),
                    ((0.8, 0.95), 'black'),
                    ((0.95, 0.98), 'yellow'),
                    ((0.98, 0.985), 'purple'),
                    ((0.985, 0.99), 'blue'),
                    ((0.99, 0.995), 'gray'),
                    ((0.995, 0.999), 'white'),
                    ((0.999, 1.0), 'green'),
                ),
                'yellow': (
                    ((0.0, 0.7), 'brown'),
                    ((0.7, 0.95), 'gray'),
                    ((0.95, 0.98), 'red'),
                    ((0.98, 0.985), 'purple'),
                    ((0.985, 0.99), 'blue'),
                    ((0.99, 0.995), 'black'),
                    ((0.995, 0.999), 'white'),
                    ((0.999, 1.0), 'green'),
                ),
                'gray': (
                    ((0.0, 0.8), 'white'),
                    ((0.8, 0.85), 'black'),
                    ((0.85, 0.9), 'yellow'),
                    ((0.9, 0.95), 'red'),
                    ((0.95, 0.96), 'blue'),
                    ((0.96, 0.97), 'purple'),
                    ((0.97, 0.98), 'brown'),
                    ((0.98, 1.0), 'green'),
                ),
                'white': (
                    ((0.0, 0.8), 'gray'),
                    ((0.8, 0.85), 'black'),
                    ((0.85, 0.9), 'yellow'),
                    ((0.9, 0.95), 'red'),
                    ((0.95, 0.96), 'blue'),
                    ((0.96, 0.97), 'purple'),
                    ((0.97, 0.98), 'brown'),
                    ((0.98, 1.0), 'green'),
                ),
                'purple': (
                    ((0.0, 0.6), 'blue'),
                    ((0.6, 0.8), 'green'),
                    ((0.8, 0.85), 'red'),
                    ((0.85, 0.9), 'black'),
                    ((0.9, 0.93), 'brown'),
                    ((0.93, 0.95), 'gray'),
                    ((0.95, 0.96), 'yellow'),
                    ((0.96, 1.0), 'white'),
                ),
                'green': (
                    ((0.0, 0.6), 'blue'),
                    ((0.6, 0.8), 'purple'),
                    ((0.8, 0.85), 'red'),
                    ((0.85, 0.9), 'black'),
                    ((0.9, 0.93), 'brown'),
                    ((0.93, 0.95), 'gray'),
                    ((0.95, 0.96), 'yellow'),
                    ((0.96, 1.0), 'white'),
                ),
                'blue': (
                    ((0.0, 0.6), 'purple'),
                    ((0.6, 0.8), 'green'),
                    ((0.8, 0.85), 'red'),
                    ((0.85, 0.9), 'black'),
                    ((0.9, 0.93), 'brown'),
                    ((0.93, 0.95), 'gray'),
                    ((0.95, 0.96), 'yellow'),
                    ((0.96, 1.0), 'white'),
                ),
            },
            "eyebrow size": {
                'small': (
                    ((0.0, 0.8), 'medium'),
                    ((0.8, 0.95), 'unibrow'),
                    ((0.95, 1.0), 'large'),
                ),
                'medium': (
                    ((0.0, 0.5), 'small'),
                    ((0.5, 0.95), 'large'),
                    ((0.95, 1.0), 'unibrow'),
                ),
                'large': (
                    ((0.0, 0.8), 'medium'),
                    ((0.8, 0.95), 'unibrow'),
                    ((0.95, 1.0), 'small'),
                ),
                'unibrow': (
                    ((0.0, 0.8), 'large'),
                    ((0.8, 0.95), 'medium'),
                    ((0.95, 1.0), 'small'),
                ),
            },
            "eye horizontal settedness": {
                'narrow': (
                    ((0.0, 0.8), 'middle'),
                    ((0.8, 1.0), 'wide'),
                ),
                'middle': (
                    ((0.0, 0.5), 'narrow'),
                    ((0.5, 1.0), 'wide'),
                ),
                'wide': (
                    ((0.0, 0.8), 'middle'),
                    ((0.8, 1.0), 'narrow'),
                ),
            },
            "eye vertical settedness": {
                'low': (
                    ((0.0, 0.8), 'middle'),
                    ((0.8, 1.0), 'high'),
                ),
                'middle': (
                    ((0.0, 0.5), 'low'),
                    ((0.5, 1.0), 'high'),
                ),
                'high': (
                    ((0.0, 0.8), 'middle'),
                    ((0.8, 1.0), 'low'),
                ),
            },
            "facial hair style": {
                'none': (
                    ((0.0, 0.4), 'soul patch'),
                    ((0.4, 0.8), 'sideburns'),
                    ((0.8, 0.9), 'mustache'),
                    ((0.9, 0.98), 'goatee'),
                    ((0.98, 1.0), 'full beard'),
                ),
                'soul patch': (
                    ((0.0, 0.4), 'none'),
                    ((0.4, 0.8), 'sideburns'),
                    ((0.8, 0.9), 'mustache'),
                    ((0.9, 0.98), 'goatee'),
                    ((0.98, 1.0), 'full beard'),
                ),
                'sideburns': (
                    ((0.0, 0.4), 'soul patch'),
                    ((0.4, 0.8), 'none'),
                    ((0.8, 0.9), 'mustache'),
                    ((0.9, 0.98), 'goatee'),
                    ((0.98, 1.0), 'full beard'),
                ),
                'mustache': (
                    ((0.0, 0.4), 'soul patch'),
                    ((0.4, 0.8), 'sideburns'),
                    ((0.8, 0.9), 'none'),
                    ((0.9, 0.98), 'goatee'),
                    ((0.98, 1.0), 'full beard'),
                ),
                'goatee': (
                    ((0.0, 0.4), 'soul patch'),
                    ((0.4, 0.8), 'sideburns'),
                    ((0.8, 0.9), 'mustache'),
                    ((0.9, 0.98), 'none'),
                    ((0.98, 1.0), 'full beard'),
                ),
                'full beard': (
                    ((0.0, 0.4), 'soul patch'),
                    ((0.4, 0.8), 'sideburns'),
                    ((0.8, 0.9), 'mustache'),
                    ((0.9, 0.98), 'goatee'),
                    ((0.98, 1.0), 'none'),
                ),
            },
            "freckles": {
                'no': (
                    ((0.0, 1.0), 'yes'),  # Only one thing to possibly mutate into
                ),
                'yes': (
                    ((0.0, 1.0), 'no'),
                ),
            },
        }
        self.memory_mutations["eye size"] = self.memory_mutations["head size"]
        self.memory_mutations["nose size"] = self.memory_mutations["head size"]
        self.memory_mutations["eyebrow color"] = self.memory_mutations["hair color"]
        self.memory_mutations["mouth size"] = self.memory_mutations["head size"]
        self.memory_mutations["ear size"] = self.memory_mutations["head size"]
        self.memory_mutations["birthmark"] = self.memory_mutations["freckles"]
        self.memory_mutations["scar"] = self.memory_mutations["freckles"]
        self.memory_mutations["tattoo"] = self.memory_mutations["freckles"]
        self.memory_mutations["glasses"] = self.memory_mutations["freckles"]
        self.memory_mutations["sunglasses"] = self.memory_mutations["freckles"]

                ####################
                ##  SOCIAL STUFF  ##
                ####################

        #               CHARGE          #
        # These values help to determine the charge increment for an Acquaintance/Friendship/Enmity
        # and get multiplied by its owner's extroversion and subject's agreeableness, respectively;
        # the resulting value then gets added to the two people's compatibility, which will be on
        # a scale from -1 to 1, and so these represent the proportion, relative to compatibility,
        # that these values will play in determining charge increments
        self.owner_extroversion_boost_to_charge_multiplier = 0.25
        self.subject_agreeableness_boost_to_charge_multiplier = 0.25
        self.charge_intensity_reduction_due_to_sex_difference = 0.5
        self.function_to_determine_how_age_difference_reduces_charge_intensity = (
            # This makes people with large age differences more indifferent about potentially
            # becoming friends or enemies
            lambda age1, age2: max(0.05, 1 - (abs(math.sqrt(age1)-math.sqrt(age2))/4.5))
        )
        self.function_to_determine_how_job_level_difference_reduces_charge_intensity = (
            # This makes people with job-level differences more indifferent about potentially
            # becoming friends or enemies
            lambda job_level1, job_level2: max(0.05, 1 - (abs(math.sqrt(job_level1)-math.sqrt(job_level2))))
        )
        #               SPARK          #
        # These values help determine the initial spark increment for an Acquaintance; the accumulation
        # of spark represents a person's romantic attraction toward the acquaintance. Values here
        # come from source [5]: the first set are dependent on the acquaintance's personality, and the
        # second on the person themself's personality (i.e., generally how likely they are to be attracted
        # to other people based on their own personality alone)
        #       Affected by own personality        #
        self.self_openness_boost_to_spark_multiplier = {
            'm': 0.2, 'f': 0.55
        }
        self.self_conscientiousness_boost_to_spark_multiplier = {
            'm': -0.09, 'f': -0.1
        }
        self.self_extroversion_boost_to_spark_multiplier = {
            'm': 0.13, 'f': 0.43
        }
        self.self_agreeableness_boost_to_spark_multiplier = {
            'm': 0.3, 'f': 0.19
        }
        self.self_neuroticism_boost_to_spark_multiplier = {
            'm': 0.01, 'f': 0.05
        }
        #       Affected by partner personality     #
        self.openness_boost_to_spark_multiplier = {
            'm': -0.39, 'f': -0.37
        }
        self.conscientiousness_boost_to_spark_multiplier = {
            'm': 0.5, 'f': 0.38
        }
        self.extroversion_boost_to_spark_multiplier = {
            'm': 0.5, 'f': 0.49
        }
        self.agreeableness_boost_to_spark_multiplier = {
            'm': 0.52, 'f': 0.31
        }
        self.neuroticism_boost_to_spark_multiplier = {
            'm': -0.36, 'f': -0.63
        }
        #       Affected by age difference (this is not sourced currently)
        self.function_to_determine_how_age_difference_reduces_spark_increment = (
            lambda age1, age2: max(0.05, 1 - (abs(math.sqrt(age1)-math.sqrt(age2))/1.5))
        )
        self.function_to_determine_how_job_level_difference_reduces_spark_increment = (
            # This makes people with job-level differences less likely to develop romantic feelings
            # for one another
            lambda job_level1, job_level2: max(0.05, 1 - (abs(math.sqrt(job_level1)-math.sqrt(job_level2))))
        )
        # Spark decay rate
        self.spark_decay_rate = 0.8
        # Once the charge of an Acquaintance exceeds these thresholds, a Friendship or Enmity
        # (whichever is appropriate, of course) object will get instantiated
        self.charge_threshold_friendship = 15.0
        self.charge_threshold_enmity = -15.0

            #################
            ##  ARTIFACTS  ##
            #################

        self.occupations_that_may_appear_on_gravestones = [
            'Groundskeeper', 'Nurse', 'Architect', 'Doctor', 'FireChief', 'Firefighter',
            'Barber', 'Lawyer', 'Mortician', 'Optometrist', 'PoliceChief', 'PoliceOfficer',
            'Principal', 'Professor', 'Teacher', 'Baker', 'Barkeeper', 'Blacksmith', 'Brewer',
            'Bricklayer', 'Butcher', 'Carpenter', 'Clothier', 'Cooper', 'Dentist', 'Distiller',
            'Dressmaker', 'Druggist', 'Engineer', 'Farmer', 'Grocer', 'Innkeeper', 'Jeweler',
            'Joiner', 'Milkman', 'Miner', 'Painter', 'Plumber', 'Puddler', 'Quarryman', 'Seamstress',
            'Shoemaker', 'Stonecutter', 'Tailor', 'Turner', 'Woodworker'
        ]

            ####################
            ##  CONVERSATION  ##
            ####################

        self.path_to_json_grammar_specification = (
            './content/talktown.json'
        )
        # Frame definitions
        self.conversational_frames = {
            'FACE-TO-FACE': {
                'preconditions': lambda conversation: not conversation.phone_call,
                'obligations': {
                    'initiator': ['greet'],
                    'recipient': []
                },
                'goals': {
                    'initiator': [],
                    'recipient': []
                }
            },
            'PHONE CALL': {
                'preconditions': lambda conversation: conversation.phone_call,
                'obligations': {
                    'initiator': ['report identity'],
                    'recipient': ['answer phone']
                },
                'goals': {
                    'initiator': [],
                    'recipient': ['LEARN CALLER IDENTITY']
                }
            },
            'PHONE CALL FROM STRANGER': {
                'preconditions': lambda conversation: (
                    conversation.phone_call and conversation.initiator not in conversation.recipient.relationships
                ),
                'obligations': {
                    'initiator': ['EXPLAIN REASON FOR CALL'],
                    'recipient': []
                },
                'goals': {
                    'initiator': [],
                    'recipient': ['LEARN REASON FOR CALL']
                }
            },
            'STRANGERS IN PUBLIC': {
                'preconditions': lambda conversation: (
                    conversation.initiator not in conversation.recipient.relationships
                ),
                'obligations': {
                    'initiator': [],
                    'recipient': []
                },
                'goals': {
                    'initiator': ['LEARN NAME OF STRANGER IN PUBLIC', 'LEARN IF STRANGER IN PUBLIC IS FROM HERE'],
                    'recipient': ['LEARN NAME OF STRANGER IN PUBLIC']
                }
            },
            'EXTREMELY INTROVERTED RECIPIENT': {
                'preconditions': lambda conversation: conversation.recipient.personality.extroversion < -0.4,
                'obligations': {
                    'initiator': [],
                    'recipient': []
                },
                'goals': {
                    'initiator': [],
                    'recipient': ['END CONVERSATION']
                }
            },
            'TEST': {
                'preconditions': lambda conversation: True,
                'obligations': {
                    'initiator': [],
                    'recipient': []
                },
                'goals': {
                    'initiator': ['LEARN WORKPLACE OF STRANGER IN PUBLIC'],
                    'recipient': ['LEARN WORKPLACE OF STRANGER IN PUBLIC']
                }
            },
        }
        # Definitions for conversational goals in terms of their steps and subgoals
        self.conversational_goals = {
            # Goal name (in alphabetical order)
            #   Speaker, act name, number of times act must occur for step to be achieved
            'END CONVERSATION': [
                ('me', 'wrap up conversation', 1),
                ('them', 'say goodbye', 1),
                ('me', 'say goodbye', 1),
            ],
            'INTRODUCE SELF TO STRANGER IN PUBLIC': [
                ('either', 'make small talk', 4),
                ('me', 'introduce self', 1)
            ],
            'LEARN CALLER IDENTITY': [
                ('me', 'answer phone', 1),
                ('me', 'request caller identity', 1),
                ('them', 'report identity', 1),
            ],
            'LEARN NAME OF STRANGER IN PUBLIC': [
                ('me', 'INTRODUCE SELF TO STRANGER IN PUBLIC', 1),
                ('me', 'request name', 1),
                ('them', 'introduce self', 1)
            ],
            'LEARN IF STRANGER IN PUBLIC IS FROM HERE': [
                ('me', 'ask how are you', 1),
                ('me', 'ask are you from here', 1),
                ('them', 'answer are you from here', 1)
            ],
            'LEARN WORKPLACE OF STRANGER IN PUBLIC': [
                ('me', 'LEARN NAME OF STRANGER IN PUBLIC', 1),
                ('me', 'ask where do you work', 1),
                ('them', 'answer where do you work', 1)
            ],
        }

    @staticmethod
    def fit_probability_distribution(relative_frequencies_dictionary):
        """Return a probability distribution fitted to the given relative-frequencies dictionary."""
        frequencies_sum = float(sum(relative_frequencies_dictionary.values()))
        probabilities = {}
        for k in relative_frequencies_dictionary.keys():
            frequency = relative_frequencies_dictionary[k]
            probability = frequency/frequencies_sum
            probabilities[k] = probability
        fitted_probability_distribution = {}
        current_bound = 0.0
        for k in probabilities:
            probability = probabilities[k]
            probability_range_for_k = (current_bound, current_bound+probability)
            fitted_probability_distribution[k] = probability_range_for_k
            current_bound += probability
        # Make sure the last bound indeed extends to 1.0
        last_bound_attributed = list(probabilities)[-1]
        fitted_probability_distribution[last_bound_attributed] = (
            fitted_probability_distribution[last_bound_attributed][0], 1.0
        )
        return fitted_probability_distribution