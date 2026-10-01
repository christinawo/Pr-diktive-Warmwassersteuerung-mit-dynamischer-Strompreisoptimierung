# The idea behind is, that no person/household is exactly stochastic, 
# so e.g. not every day is a shower or cooking event

# Jordan & Vajen (2001), "Realistic Domestic Hot-Water Profiles in Different Time Scales"
# - used as basis for event volumes and seasonal variations.

# Exact event probabilities and time windows are modeling assumptions

import random
from demand_profile.demand_events import (shower_event, bathing_event, small_draw_event, medium_draw_event)
from models.monthly_factors import MONTHLY_FACTORS

time_step_minutes = 15
steps_per_day = 96

def random_time(mean, std, min_hour, max_hour):
    hour = random.gauss(mean, std)
    return max(min_hour, min(hour, max_hour))

def generate_day(
        persons, 
        weekday,
        month,
        has_bathtub = False,
        irregular = False
):
    profile = [[] for _ in range(steps_per_day)]
    # Medium draw
    if irregular:
        medium_draw_count = random.randint(0, 4)
    else:
        medium_draw_count = random.randint(1, 3)
    for _ in range(medium_draw_count):
        volume, temperature = medium_draw_event()
        if irregular:
             hour = random.uniform(8.0, 22.0)
        else:
            if random.random() < 0.3:
                hour = random_time(12.5, 0.75, 11.0, 14.0)
            else:
                hour = random_time(18.0, 1.0, 16.0, 21.0)
        step = int(hour * 60 / time_step_minutes)
        profile[step].append({
            "type": "cooking",
            "volume": volume,
            "temperature": temperature
        })

    # Bathing
    if has_bathtub:
        if random.random() < 0.08:
            volume, temperature = bathing_event()
            hour = random.uniform(18.0, 22.0)
            step = int(hour * 60 / time_step_minutes)
            profile[step].append({
                "type": "bath",
                "volume": volume,
                "temperature": temperature
            })

    for person in persons:
        # Shower
        if random.random() < 0.9:
            volume, temperature = shower_event()
            if irregular:
                hour = random.uniform(6.0, 23.0)
            else:
                if person["shower_time"] == "morning":
                    if weekday < 5:
                        hour = random.gauss(person["usual_shower_time"], 0.25)
                    else: 
                        hour = random.gauss(person["usual_shower_time"] + 2, 0.25)
                elif person["shower_time"] == "evening":
                    hour = random.gauss(person["usual_shower_time"], 0.25)

            step = int(hour * 60 / time_step_minutes)
            profile[step].append({
                "type": "shower",
                "volume": volume,
                "temperature": temperature
            })
        # Small draw event
        if irregular:
            small_draw_count = random.randint(2, 9)
        else:
            small_draw_count = random.randint(4, 7)
        for _ in range(small_draw_count):
            volume, temperature = small_draw_event()
            if irregular:
                hour = random.uniform(6.0, 23.0)
            else:
                if weekday < 5:
                    hour = random.uniform(6.0, 22.0)
                else:
                    hour = random.uniform(7.5, 22.5)

            step = int(hour * 60 / time_step_minutes)
            profile[step].append({
                "type": "small draw",
                "volume": volume,
                "temperature": temperature
            })
 
    # Seasonal factor
    seasonal_factor = MONTHLY_FACTORS[month]
    for step_events in profile:
        for event in step_events:
            event["volume"] *= seasonal_factor

    return profile
