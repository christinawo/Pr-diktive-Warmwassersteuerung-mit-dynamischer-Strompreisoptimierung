from demand_profile.demand_generate import generate_day

# Single Household demand with bathtub
def single_demand_bathtub(weekday, month):

    single_person = [
        {"shower_time": "morning", "usual_shower_time": 6.5}
    ]

    profile = generate_day(single_person, weekday, month, True, False)

    return profile

# Single Household demand without bathtub
def single_demand_no_bathtub(weekday, month):

    single_person = [
        {"shower_time": "morning", "usual_shower_time": 6.0}
    ]

    profile = generate_day(single_person, weekday, month, False, False)

    return profile

# Single Household irregular demand
def single_demand_irregular(weekday, month):

    single_person = [
        {"shower_time": "morning", "usual_shower_time": 6.5}
    ]

    profile = generate_day(single_person, weekday, month, False, True)

    return profile