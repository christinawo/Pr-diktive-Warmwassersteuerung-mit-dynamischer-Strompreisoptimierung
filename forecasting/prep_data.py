def profile_to_timeseries(daily_profile):
    consumption = []

    for events in daily_profile:
        step_volume = 0.0

        for event in events:
            step_volume += event["volume"]

        consumption.append(step_volume)

    return consumption

def generate_demand_dataset(complete_days, number_of_days, demand_profile):
    dataset = []

    for day, daily_prices in complete_days[:number_of_days]:
        daily_profile = demand_profile(day.weekday(), day.month)

        daily_consumption = profile_to_timeseries(daily_profile)

        dataset.append({"date": day, "consumption": daily_consumption})

    return dataset

def hourly_demand(consumption):
    hourly_consumption = []

    for hour in range(24):
        start = hour * 4
        end = start + 4

        hourly_volume = sum(consumption[start:end])
        hourly_consumption.append(hourly_volume)

    return hourly_consumption


def forecast_to_15minutes(hourly_forecast):
    forecast_15min = []

    for hourly_volume in hourly_forecast:
        volume_per_step = hourly_volume / 4.0

        for _ in range(4):
            forecast_15min.append(volume_per_step)

    return forecast_15min