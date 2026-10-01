from demand_profile.demand_generate import generate_day

# Family household demand with bathtub
def family_demand_bathtub(weekday, month):

    family_persons = [
        {"shower_time": "morning", "usual_shower_time": 6.75},
        {"shower_time": "morning", "usual_shower_time": 7.00},
        {"shower_time": "evening", "usual_shower_time": 19.75},
        {"shower_time": "evening", "usual_shower_time": 21.50}
    ]

    profile = generate_day(family_persons, weekday, month, True, False)

    return profile

# Family household demand without bathtub
def family_demand_no_bathtub(weekday, month):

    family_persons = [
        {"shower_time": "morning", "usual_shower_time": 6.75},
        {"shower_time": "morning", "usual_shower_time": 7.00},
        {"shower_time": "evening", "usual_shower_time": 19.75},
        {"shower_time": "evening", "usual_shower_time": 21.50}
    ]

    profile = generate_day(family_persons, weekday, month, False, False)

    return profile

# Family household irregular demand
def family_demand_irregular(weekday, month):

    family_persons = [
        {"shower_time": "morning", "usual_shower_time": 6.75},
        {"shower_time": "morning", "usual_shower_time": 7.00},
        {"shower_time": "evening", "usual_shower_time": 19.75},
        {"shower_time": "evening", "usual_shower_time": 21.50}
    ]

    profile = generate_day(family_persons, weekday, month, False, True)

    return profile