#from business import *
#from landmark import *
#from occupation import *
#from event import *


class Config(object):
    """Configuration for a gameplay instance in terms of simulation and gameplay parameters."""

    def __init__(self):
        """Construct a Config object."""
        self.n_buildings_per_block = 4
                ## WORLD GEN ##
        # Misc
        self.year_city_gets_founded = 1909  # Year world gen begins
        # City dimensions
        self.city_width_in_blocks = 8
        self.city_height_in_blocks = 8
        self.city_downtown_blocks_displaced_from_center_max = 2
                ## FULL SIMULATION ##
        # Marriage
        self.chance_one_newlywed_takes_others_name = 0.9
        self.chance_newlyweds_decide_children_will_get_hyphenated_surname = 0.02
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
        self.function_to_determine_chance_of_conception = lambda female_age: min(
            female_age/10000., (100 - ((female_age**1.98) / 20.)) / 100  # Decreases exponentially with age
        )
        # Death
        self.function_to_derive_chance_a_widow_remarries = (
            lambda years_married: 1.0 / (int(years_married) + 4)
        )
        # People finding new homes
        self.penalty_for_having_to_build_a_home_vs_buying_one = 0.5  # i.e., relative desire to build
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
                ## ECONOMY ##
        # Misc
        self.age_people_start_working = 16
        self.amount_of_money_generated_people_from_outside_city_start_with = 5000
        # Companies hiring people
        self.preference_to_hire_immediate_family = 3
        self.preference_to_hire_from_within_company = 2
        self.preference_to_hire_friend = 1
        self.preference_to_hire_extended_family = 1
        self.preference_to_hire_known_person = 0.5
        self.unemployment_occupation_level = 0.5  # Affects scoring of job candidates
        # Initial vacant positions for each business type
        self.initial_job_vacancies = {
            ApartmentComplex: (Janitor, Janitor, Manager),
            Bank: (Janitor, BankTeller, BankTeller, Manager),
            Barbershop: (Cashier, HairStylist, HairStylist, Manager),
            BusDepot: (BusDriver, BusDriver, Manager),
            CityHall: (Secretary, Secretary),  # Mayor excluded due to special hiring process
            ConstructionFirm: (
                Secretary, ConstructionWorker, ConstructionWorker, ConstructionWorker,
                ConstructionWorker, Architect
            ),
            OptometryClinic: (Secretary, Nurse, Nurse, Manager, Optometrist),
            FireStation: (Secretary, Firefighter, Firefighter, FireChief),
            Hospital: (Secretary, Nurse, Nurse, Manager, Doctor),
            Hotel: (HotelMaid, HotelMaid, Concierge, Manager),
            LawFirm: (Secretary, Lawyer, Lawyer),
            PlasticSurgeryClinic: (Secretary, Nurse, Nurse, Manager, PlasticSurgeon),
            PoliceStation: (Secretary, PoliceOfficer, PoliceOfficer, PoliceChief),
            RealtyFirm: (Secretary, Realtor, Realtor),
            Restaurant: (Cashier, Cashier, Waiter, Waiter, Waiter, Manager),
            Supermarket: (Cashier, Cashier, Waiter, Waiter, Waiter, Manager),
            TattooParlor: (Cashier, TattooArtist, TattooArtist, Manager),
            TaxiDepot: (TaxiDriver, TaxiDriver, Manager),
            University: (Professor, Professor),
            Cemetery: (Groundskeeper, Groundskeeper, Mortician),
            Park: (Groundskeeper, Groundskeeper, Manager),
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
            Concierge: 'Hospitality',
            HairStylist: 'Cosmetic',
            ConstructionWorker: 'Construction',
            Firefighter: 'Fire',
            PoliceOfficer: 'Police',
            TaxiDriver: 'Transportation',
            BusDriver: 'Transportation',
            Nurse: 'Medical',
            TattooArtist: 'Cosmetic',
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
            Concierge: None,
            HairStylist: None,
            ConstructionWorker: None,
            Firefighter: None,
            PoliceOfficer: None,
            TaxiDriver: None,
            BusDriver: None,
            Nurse: None,
            TattooArtist: None,
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
            Owner: None,
            Mayor: None,
        }
        # Job levels of various occupations (indexed by their class names)
        self.job_levels = {
            Cashier: 1,
            Janitor: 1,
            HotelMaid: 1,
            Waiter: 1,
            Secretary: 1,
            Groundskeeper: 1,
            BankTeller: 2,
            Concierge: 2,
            HairStylist: 2,
            ConstructionWorker: 2,
            Firefighter: 2,
            PoliceOfficer: 2,
            TaxiDriver: 2,
            BusDriver: 2,
            Nurse: 2,
            TattooArtist: 2,
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
            BuildingConstruction: {
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
        self.preference_to_contract_friend = 2
        self.preference_to_contract_former_contract = 2
        self.preference_to_contract_extended_family = 1
        self.preference_to_contract_known_person = 0.5
                ## PEOPLE REPRESENTATION ##
        # People ex nihilo
        self.function_to_determine_person_ex_nihilo_age_given_job_level = (
            lambda job_level: 18 + (random.randint(2, 5) * job_level)
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
        # Memory
        self.memory_mean = 0.7
        self.memory_sd = 0.1
        self.memory_cap = 0.9
        self.memory_floor = 0.1
        self.memory_floor_at_birth = 0.55  # Worst possible memory of newborn
        self.memory_sex_diff = 0.03  # Men have worse memory, studies show
        self.memory_heritability = 0.6  # Couldn't quickly find a study on this -- totally made up
        self.memory_heritability_sd = 0.05
        # Big Five personality traits (source [0])
        self.big_5_floor = -1.0
        self.big_5_cap = 1.0
        self.big_5_sd = 0.35
        self.big_5_o_mean = 0.375
        self.big_5_c_mean = 0.25
        self.big_5_e_mean = 0.15
        self.big_5_a_mean = 0.35
        self.big_5_n_mean = 0.0
        self.big_5_o_heritability = 0.57
        self.big_5_c_heritability = 0.54
        self.big_5_e_heritability = 0.49
        self.big_5_a_heritability = 0.48
        self.big_5_n_heritability = 0.42
        self.big_5_heritability_sd = 0.05
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

        # Businesses  -- DELETE???
        self.business_frequencies = self.set_frequency_of_each_business_type()

    @staticmethod
    def set_frequency_of_each_business_type():
        """Sets the frequency of each business type (relative to one another)."""
        business_frequency = {
            "Supermarket": 8,
            "Bank": 6,
            "Hotel": 5,
            "Barbershop": 5,
            "Eyeglass Shop": 3,
            "Tattoo Parlor": 3,
            "LASIK": 2,
            "Plastic Surgeon": 2,
            "Tattoo Removal": 1,
        }
        return business_frequency