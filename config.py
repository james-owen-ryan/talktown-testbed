from occupation import *
from event import *
from business import *
import math


class Config(object):
    """Configuration for a gameplay instance in terms of simulation and gameplay parameters."""

    def __init__(self):
        """Construct a Config object."""

                #################
                ##  WORLD GEN  ##
                #################
        # When to stop
        self.date_the_founder_dies = (1980, 10, 18)
        self.date_city_gets_founded = (1910, 10, 18)  # Date world gen begins
        # City generation
        self.loci = 3
        self.samples = 32
        self.size = 16
        self.n_buildings_per_block = 2
        self.largest_possible_house_number = 799
        self.smallest_possible_house_number = 100
        self.chance_city_gets_named_for_founder = 0.3
        self.chance_avenue_gets_numbered_name = 0.0
        self.chance_street_gets_numbered_name = 0.8
        self.public_institutions_started_upon_city_founding = (
            CityHall, Hospital, FireStation, PoliceStation, School, University, Park, Cemetery
        )
        self.businesses_started_upon_city_founding = (
            # Excluding construction firm, reality firm, and apartment complexes built by founder
            Bank, RealtyFirm, Hotel, Supermarket, BusDepot, TaxiDepot, Barbershop, DayCare,
            Restaurant, Restaurant, OptometryClinic, LawFirm, TattooParlor, PlasticSurgeryClinic,
            Bar, Bar,
        )
        # City founder
        self.age_of_city_founder = 30
        self.age_of_city_founders_spouse = 30
        self.money_city_founder_starts_with = 100000
        self.boost_to_the_founders_conception_chance = 0.2
        # City establishment and early development
        self.number_of_apartment_complexes_founder_builds_downtown = 3

                #################
                ##  FULL SIM   ##
                #################

        # Daily routines
        self.chance_someone_calls_in_sick_to_work = 0.03
        self.chance_someone_doesnt_have_to_work_some_day = 0.00  # Can be used as proxy in lieu of weekends
        self.chance_someone_leaves_home_multiplier_due_to_kids = 0.3  # i.e., 30% as likely to leave if kids
        self.chance_someone_leaves_home_on_day_off_floor = {
            # The actual chance is a person's extroversion, but these represent
            # the minimum chance. (Keep in mind, they currently will be spending
            # the entire day/night cycle at some particular place in public
            "day": 0.05, "night": 0.03
        }
        self.chance_someone_leaves_home_on_day_off_cap = {
            # The actual chance is a person's extroversion, but these represent
            # the maximum chance. (Keep in mind, they currently will be spending
            # the entire day/night cycle at some particular place in public
            "day": 0.7, "night": 0.5
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
        self.chance_someone_visiting_someone_visits_extended_family = 0.
        self.probabilities_of_errand_to_business_type = {
            # Keep in mind, this person will be spending the entire day/night cycle there
            "day": (
                ((0.00, 0.30), 'Restaurant'),
                ((0.30, 0.55), 'Supermarket'),
                ((0.55, 0.65), 'Park'),
                ((0.65, 0.75), 'Bank'),
                ((0.75, 0.80), 'BusDepot'),
                ((0.80, 0.85), 'Bar'),
                ((0.85, 0.88), 'Cemetery'),
                ((0.88, 0.90), 'TaxiDepot'),
                ((0.90, 0.95), 'Hotel'),
                ((0.95, 1.00), 'University'),
            ),
            "night": (
                ((0.00, 0.35), 'Restaurant'),
                ((0.35, 0.70), 'Bar'),
                ((0.70, 0.80), 'Hotel'),
                ((0.80, 0.88), 'Supermarket'),
                ((0.88, 0.95), 'TaxiDepot'),
                ((0.95, 0.97), 'BusDepot'),
                ((0.97, 0.99), 'Park'),
                ((0.99, 1.00), 'Cemetery'),
            ),
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
        }
        self.errand_business_types = ('Supermarket', 'Bank', 'BusDepot', 'Cemetery', 'TaxiDepot', 'University')
        self.leisure_business_types = ('Restaurant', 'Park', 'Bar', 'Hotel')
        self.chance_someone_gets_a_haircut_some_day = 0.02
        self.chance_someone_gets_contacts_or_glasses = 0.002
        self.chance_someone_gets_a_tattoo_some_day = 0.001  # Face tattoo, of course
        self.chance_someone_gets_plastic_surgery_some_day = 0.001
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
        self.chance_a_divorcee_falls_out_of_love = 0.9
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
        # Death
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
            'Daughter': 7,
            'Son': 7,
            'Mother': 5,
            'Father': 5,
            'Granddaughter': 3,
            'Grandson': 3,
            'Sister': 2,
            'Brother': 2,
            'Grandmother': 2,
            'Grandfather': 2,
            'Greatgrandmother': 2,
            'Greatgrandfather': 2,
            'Niece': 1,
            'Nephew': 1,
            'Aunt': 1,
            'Uncle': 1,
            'Cousin': 1,
            None: 0,
        }
        self.pull_to_live_near_workplace = 5

                ###############
                ##  ECONOMY  ##
                ###############

        # Misc
        self.age_people_start_working = 16
        self.amount_of_money_generated_people_from_outside_city_start_with = 5000
        # Housing
        self.number_of_apartment_units_per_complex = 8
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
        self.public_companies = (CityHall, FireStation, Hospital, PoliceStation, School, University, Cemetery, Park)
        # Company types that get established on tracts, not on lots
        self.companies_that_get_established_on_tracts = (Cemetery, Park)  # TODO maybe add University?
        # Companies hiring people
        self.preference_to_hire_immediate_family = 3
        self.preference_to_hire_from_within_company = 2
        self.preference_to_hire_extended_family = 1
        self.preference_to_hire_friend = 1  # TODO modify this according to charge
        self.dispreference_to_hire_enemy = -1  # TODO modify this according to charge
        self.preference_to_hire_acquaintance = 0.5  # TODO modify this according to charge
        self.unemployment_occupation_level = 0.5  # Affects scoring of job candidates
        # Initial vacant positions for each business type
        self.initial_job_vacancies = {
            ApartmentComplex: {
                'day': (Secretary, Janitor, Manager),
                'night': (Janitor,),
            },
            Bank: {
                'day': (BankTeller, BankTeller, Manager),
                'night': (Janitor,),
            },
            Bar: {
                'day': (Bartender,),
                'night': (Bartender, Bartender, Manager),
            },
            Barbershop: {
                'day': (HairStylist, Manager),
                'night': (Cashier, HairStylist, Manager),
            },
            BusDepot: {
                'day': (Secretary, BusDriver, Manager),
                'night': (BusDriver,),
            },
            CityHall: {
                'day': (Secretary, Secretary, Janitor),  # Mayor excluded due to special hiring process
                'night': (Janitor,),
            },
            ConstructionFirm: {
                'day': (
                    # Order matters for this one -- architect must come first to build the others'
                    # houses!
                    Architect, Secretary, ConstructionWorker, ConstructionWorker,
                ),
                'night': (Janitor,),
            },
            DayCare: {
                'day': (DayCareProvider, DayCareProvider, DayCareProvider),
                'night': (Janitor,),
            },
            OptometryClinic: {
                'day': (Secretary, Nurse, Optometrist),
                'night': (Janitor,),
            },
            FireStation: {
                'day': (Secretary, Firefighter, Firefighter, FireChief),
                'night': (Secretary, Firefighter),
            },
            Hospital: {
                'day': (Secretary, Nurse, Manager, Doctor),
                'night': (Secretary, Nurse, Manager, Doctor),
            },
            Hotel: {
                'day': (HotelMaid, HotelMaid, Concierge, Manager),
                'night': (Manager, Concierge),
            },
            LawFirm: {
                'day': (Secretary, Lawyer, Lawyer),
                'night': (Janitor,),
            },
            PlasticSurgeryClinic: {
                'day': (Secretary, Nurse, PlasticSurgeon),
                'night': (Janitor,),
            },
            PoliceStation: {
                'day': (Secretary, PoliceOfficer, PoliceChief),
                'night': (Secretary, PoliceOfficer),
            },
            RealtyFirm: {
                'day': (Secretary, Realtor, Realtor),
                'night': (Janitor,),
            },
            Restaurant: {
                'day': (Cashier, Waiter, Manager),
                'night': (Cashier, Waiter, Waiter, Manager),
            },
            School: {
                'day': (Janitor, Teacher, Teacher, Nurse),
                'night': (Janitor, Janitor)
            },
            Supermarket: {
                'day': (Cashier, Cashier, Manager),
                'night': (Cashier, Cashier, Manager),
            },
            TattooParlor: {
                'day': (Cashier, TattooArtist),
                'night': (Cashier, TattooArtist, Manager),
            },
            TaxiDepot: {
                'day': (TaxiDriver, Manager),
                'night': (TaxiDriver,)
            },
            University: {
                'day': (Professor, Professor),
                'night': (Janitor, Janitor)
            },
            Cemetery: {
                'day': (Groundskeeper, Mortician),
                'night': (),
            },
            Park: {
                'day': (Groundskeeper, Groundskeeper, Manager),
                'night': (),
            }
        }
        # Industries of various occupations (indexed by their class names)
        self.industries = {
            Cashier: None,
            Janitor: None,
            HotelMaid: 'Hospitality',
            Waiter: 'Hospitality',
            Secretary: None,
            Groundskeeper: 'Parks',
            BankTeller: 'Finance',
            Bartender: 'Hospitality',
            Concierge: 'Hospitality',
            DayCareProvider: 'Education',
            HairStylist: 'Cosmetic',
            ConstructionWorker: 'Construction',
            Firefighter: 'Fire',
            PoliceOfficer: 'Police',
            TaxiDriver: 'Transportation',
            BusDriver: 'Transportation',
            Nurse: 'Medical',
            TattooArtist: 'Cosmetic',
            Teacher: 'Education',
            Manager: None,
            FireChief: 'Fire',
            PoliceChief: 'Police',
            Realtor: 'Realty',
            Mortician: 'Medical',
            Doctor: 'Medical',
            Architect: 'Construction',
            Optometrist: 'Medical',
            PlasticSurgeon: 'Medical',
            Lawyer: 'Law',
            Professor: 'Academia',
            Owner: None,
            Mayor: 'Politics',
        }
        # Prerequisite industries for which experience is required to get hired
        # for various occupations
        self.prerequisite_industries = {
            Cashier: None,
            Janitor: None,
            HotelMaid: None,
            Waiter: None,
            Secretary: None,
            Groundskeeper: None,
            BankTeller: None,
            Bartender: None,
            Concierge: None,
            DayCareProvider: None,
            HairStylist: None,
            ConstructionWorker: None,
            Firefighter: None,
            PoliceOfficer: None,
            TaxiDriver: None,
            BusDriver: None,
            Nurse: None,
            TattooArtist: None,
            Teacher: None,
            Manager: 'Self',  # Must have worked in the industry for which you will manage
            FireChief: 'Fire',
            PoliceChief: 'Police',
            Realtor: None,
            Mortician: None,
            Doctor: 'Student',  # Requires graduation from college
            Architect: 'Student',
            Optometrist: 'Student',
            PlasticSurgeon: 'Student',
            Lawyer: 'Student',
            Professor: 'Student',
            Owner: None,
            Mayor: None,
        }
        # Job levels of various occupations (indexed by their class names)
        self.job_levels = {
            None: 0,  # Unemployed
            Cashier: 1,
            Janitor: 1,
            HotelMaid: 1,
            Waiter: 1,
            Secretary: 1,
            Groundskeeper: 1,
            BankTeller: 2,
            Bartender: 2,
            Concierge: 2,
            DayCareProvider: 2,
            HairStylist: 2,
            ConstructionWorker: 2,
            Firefighter: 2,
            PoliceOfficer: 2,
            TaxiDriver: 2,
            BusDriver: 2,
            Nurse: 2,
            TattooArtist: 2,
            Teacher: 2,
            Manager: 3,
            FireChief: 3,
            PoliceChief: 3,
            Realtor: 3,
            Mortician: 3,
            Doctor: 4,
            Architect: 4,
            Optometrist: 4,
            PlasticSurgeon: 4,
            Lawyer: 4,
            Professor: 4,
            Owner: 5,
            Mayor: 5,
        }
        # Compensation for various occupations
        self.compensations = {
            Birth: {
                Owner: 500,
                Doctor: 750,
                Nurse: 300,
            },
            BusinessConstruction: {
                Owner: 5000,
                Architect: 2000,
                ConstructionWorker: 400,
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
                ConstructionWorker: 200,
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
        self.preference_to_contract_immediate_family = 3
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
            lambda job_level: 18 + random.randint(2*job_level, 10*job_level)
        )
        self.function_to_determine_chance_person_ex_nihilo_starts_with_family = (
            lambda age: (age / 100.0) * 1.4
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
            "facial hair style": 0.5,  # From nurture
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
            "hair length": 0.99,
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
                ((0.0, 0.2), 'black'),
                ((0.2, 0.4), 'brown'),
                ((0.4, 0.6), 'beige'),
                ((0.6, 0.8), 'pink'),
                ((0.8, 1.0), 'white')
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
                ((0.0, 0.15), 'bald'),
                ((0.15, 0.65), 'short'),
                ((0.65, 0.85), 'medium'),
                ((0.85, 1.0), 'long')
            ],
            "hair color": [
                ((0.0, 0.3), 'black'),
                ((0.3, 0.5), 'brown'),
                ((0.5, 0.7), 'blonde'),
                ((0.7, 0.75), 'red'),
                ((0.75, 0.8), 'gray'),
                ((0.8, 0.85), 'white'),
                ((0.85, 0.9), 'green'),
                ((0.9, 0.95), 'blue'),
                ((0.95, 1.0), 'purple')
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
                ((0.0, 0.005), 'bald'),
                ((0.005, 0.2), 'short'),
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

                ########################
                ##  MEMORY/KNOWLEDGE  ##
                ########################

        self.memory_mean = 1.0
        self.memory_sd = 0.05
        self.memory_cap = 1.0
        self.memory_floor = 0.5  # After severe memory loss from aging
        self.memory_floor_at_birth = 0.8  # Worst possible memory of newborn
        self.memory_sex_diff = 0.03  # Men have worse memory, studies show
        self.memory_heritability = 0.6  # Couldn't quickly find a study on this -- totally made up
        self.memory_heritability_sd = 0.05
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
        self.chance_someone_observes_nearby_entity = 0.75
        self.chance_someone_eavesdrops_statement_or_lie = 0.05
        self.base_strength_of_evidence_types = {
            "reflection": 9999,
            "observation": 20,
            "statement": 5,
            "lie": 5,
            "eavesdropping": 5,
            "confabulation": 3,
            "mutation": 3,
            "transference": 3,
            "declaration": 2,
            "forgetting": 0.001,
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
        self.name_feature_types = ("first name", "middle name", "last name")
        self.work_feature_types = ("workplace", "job title", "job shift")
        self.home_feature_types = ("home",)
        self.chance_someone_lies_floor = 0.02
        self.chance_someone_lies_cap = 0.2
        self.amount_of_people_people_talk_about_floor = 2
        # self.amount_of_people_people_talk_about_cap = 7  # CAP IS NOW NATURALLY AT 7
        self.chance_someones_feature_comes_up_in_conversation_about_them = (
            ("first name",                  0.80),
            ("workplace",                   0.50),
            ("job title",                   0.30),
            ("job shift",                   0.30),
            ("last name",                   0.25),
            ("tattoo",                      0.10),
            ("skin color",                  0.10),
            ("hair color",                  0.08),
            ("scar",                        0.05),
            ("birthmark",                   0.05),
            ("home",                        0.05),
            ("facial hair style",           0.05),
            ("freckles",                    0.05),
            ("glasses",                     0.05),
            ("sunglasses",                  0.05),
            ("head size",                   0.04),
            ("hair length",                 0.03),
            ("eye color",                   0.03),
            ("eye horizontal settedness",   0.02),
            ("eye vertical settedness",     0.02),
            ("head shape",                  0.02),
            ("eyebrow size",                0.02),
            ("eyebrow color",               0.02),
            ("mouth size",                  0.02),
            ("ear size",                    0.02),
            ("ear angle",                   0.02),
            ("nose size",                   0.02),
            ("nose shape",                  0.02),
            ("eye size",                    0.02),
            ("eye shape",                   0.02),
            ("middle name",                 0.005),
        )
        self.person_feature_salience = {
            # (Sources [2, 3] show that hair, eyes > mouth > nose, chin.)
            # These values represent means (for someone with memory value of self.memory_mean),
            # floors, and caps for the base chance someone perfectly remembers a feature of
            # a person of this type (the base chance gets multiplied by the person's memory);
            # if a feature isn't remembered perfectly, it will immediately deteriorate by
            # mutation, transference, or forgetting
            #                               MEAN    FLOOR   CAP
            "skin color":                   (0.95,  0.80,   0.99),
            "tattoo":                       (0.95,  0.80,   0.99),
            "birthmark":                    (0.90,  0.70,   0.99),
            "scar":                         (0.90,  0.70,   0.99),
            "facial hair style":            (0.90,  0.70,   0.99),
            "glasses":                      (0.90,  0.70,   0.96),
            "sunglasses":                   (0.90,  0.70,   0.96),
            "freckles":                     (0.85,  0.50,   0.95),
            "hair color":                   (0.85,  0.50,   0.95),
            "hair length":                  (0.80,  0.50,   0.95),
            "head size":                    (0.75,  0.45,   0.90),
            "head shape":                   (0.75,  0.45,   0.90),
            "first name":                   (0.75,  0.45,   0.90),
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
            "middle name":                  (0.25,  0.05,   0.30),
        }
        # Chance of memory deterioration happening on a given timestep -- the chance
        # for each belief facet of it deteriorating on a given timestep (can be thought
        # of as representing the expected number of days a belief facet will remain intact
        # without a person seeing the person in question to reinforce the true feature);
        # this gets divided by a person's memory and divided by the strength of the belief facet
        self.chance_of_memory_deterioration_on_a_given_timestep = {
            "skin color":                   0.01,
            "tattoo":                       0.01,
            "birthmark":                    0.02,
            "scar":                         0.02,
            "hair length":                  0.05,
            "facial hair style":            0.05,
            "glasses":                      0.05,
            "sunglasses":                   0.05,
            "job shift":                    0.05,
            "first name":                   0.08,
            "ear angle":                    0.10,
            "workplace":                    0.10,
            "home is apartment":            0.10,
            "home":                         0.10,
            "last name":                    0.15,
            "job title":                    0.15,
            "freckles":                     0.15,
            "hair color":                   0.15,
            "middle name":                  0.20,
            "head size":                    0.20,
            "head shape":                   0.20,
            "business block":               0.25,
            "eye horizontal settedness":    0.25,
            "eye vertical settedness":      0.25,
            "eye size":                     0.25,
            "eye color":                    0.25,
            "eye shape":                    0.25,
            "home block":                   0.25,
            "mouth size":                   0.35,
            "nose size":                    0.35,
            "nose shape":                   0.35,
            "eyebrow size":                 0.40,
            "eyebrow color":                0.40,
            "ear size":                     0.40,
            "home address":                 0.60,
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

