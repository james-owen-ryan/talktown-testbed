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
        # Founding residents of the city
        self.n_founding_families_mean = 5
        self.n_founding_families_sd = 1
        self.n_founding_families_floor = 3
        self.n_founding_families_cap = 7
        self.n_single_founders_mean = 4
        self.n_single_founders_sd = 2
        self.n_single_founders_floor = 2
        self.n_single_founders_cap = 11
        self.founding_mother_age_floor = 19
        self.founding_mother_age_cap = 59
        self.founding_father_age_floor = 19
        self.founding_father_age_diff_floor = -2
        self.founding_father_age_diff_cap = 8
        self.founding_father_age_at_marriage_mean = 21
        self.founding_father_age_at_marriage_sd = 2.7
        self.founding_father_age_at_marriage_floor = 17
        self.founding_mother_age_at_marriage_floor = 17
                ## FULL SIMULATION ##
        # Marriage
        self.chance_newlyweds_keep_former_love_interests = 0.01
        self.chance_stepchildren_take_stepparent_name = 0.3
        self.age_after_which_stepchildren_will_not_take_stepparent_name = 6
        # Divorce
        self.chance_a_divorcee_falls_out_of_love = 0.9
        self.chance_a_male_divorcee_is_one_who_moves_out = 0.7
        self.function_to_derive_chance_spouse_changes_name_back = (
            lambda years_married: min((0.9 / (years_married / 4.0)), 0.9)
        )
        # People finding new homes
        self.desire_to_live_near_family_base = 0.3  # Scale of -1 to 1; affected by personality
        self.desire_to_live_near_family_floor = -2
        self.desire_to_live_near_family_cap = 2
        self.pull_to_live_near_a_child = 7  # Arbitrary units (are just relative to each other; family ones get altered)
        self.pull_to_live_near_a_parent = 5
        self.pull_to_live_near_a_grandchild = 3
        self.pull_to_live_near_a_sibling = 2
        self.pull_to_live_near_a_grandparent = 2
        self.pull_to_live_near_a_friend = 1.5
        self.pull_to_live_near_a_greatgrandparent = 1
        self.pull_to_live_near_a_niece_or_nephew = 1
        self.pull_to_live_near_an_aunt_or_uncle = 1
        self.pull_to_live_near_a_first_cousin = 1
        self.penalty_for_having_to_build_a_home_vs_buying_one = 0.5  # i.e., relative desire to build
                ## ECONOMY ##
        self.age_people_start_working = 16
        # Companies hiring people
        self.preference_to_hire_immediate_family = 3
        self.preference_to_hire_from_within_company = 2
        self.preference_to_hire_friend = 1
        self.preference_to_hire_extended_family = 1
        self.preference_to_hire_known_person = 0.5
        self.unemployment_occupation_level = 0.5  # Affects scoring of job candidates
        self.generated_job_candidate_from_outside_city_age_mean = 24
        self.generated_job_candidate_from_outside_city_age_sd = 3
        self.generated_job_candidate_from_outside_city_age_floor = 17
        self.generated_job_candidate_from_outside_city_age_cap = 60
        self.amount_of_money_generated_people_from_outside_city_start_with = 5000
        # Job levels of various occupations
        self.job_level_cashier = 1
        self.job_level_janitor = 1
        self.job_level_hotel_maid = 1
        self.job_level_waiter = 1
        self.job_level_bank_teller = 2
        self.job_level_concierge = 2
        self.job_level_hair_stylist = 2
        self.job_level_construction_worker = 2
        self.job_level_firefighter = 2
        self.job_level_police_officer = 2
        self.job_level_nurse = 2
        self.job_level_tattoo_artist = 2
        self.job_level_manager = 3
        self.job_level_fire_chief = 3
        self.job_level_police_chief = 3
        self.job_level_realtor = 3
        self.job_level_doctor = 4
        self.job_level_architect = 4
        self.job_level_optometrist = 4
        self.job_level_plastic_surgeon = 4
        self.job_level_owner = 5
        # Compensation for various occupations
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
        # Businesses
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