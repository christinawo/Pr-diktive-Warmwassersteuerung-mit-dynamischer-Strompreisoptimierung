from data.params import PARAMS
from evaluation.evaluation import calculate_comfort

# In the n-cheapest hour strategy, we heat at the n cheapest hours per day
def find_cheapest_hours(prices_df, n=3):
    hourly_prices = {}

    for step in range(96):
        hour = int(prices_df.iloc[step]["time_hours"])
        price = prices_df.iloc[step]["price_ct_per_kWh"]

        if hour not in hourly_prices:
            hourly_prices[hour] = price

    sorted_hours = sorted(hourly_prices, key=lambda hour: hourly_prices[hour])

    return sorted_hours[:n]

def cheapest_hours_strategy(daily_profile, prices_df, boiler, n=3):
    times = []
    temps = []
    prices = []
    energy_history = []
    cost_whole_day = 0.0
    energy_kwh = 0.0

    cheapest_hours = find_cheapest_hours(prices_df, n)

    for step in range(96):
        time_hours = prices_df.iloc[step]["time_hours"]
        current_price = prices_df.iloc[step]["price_ct_per_kWh"]

        events = daily_profile[step]
        draw_off = 0.0

        for event in events:
            mixed_volume = event["volume"]
            mixed_temperature = event["temperature"]

            if boiler.temp > mixed_temperature:
                hot_volume = (mixed_volume * (mixed_temperature - boiler.temp_cold) / (boiler.temp - boiler.temp_cold))
            else:
                hot_volume = mixed_volume

            draw_off += hot_volume / boiler.time_step

        current_hour = int(time_hours)

        heater_on = boiler.temp < PARAMS["temp_min"] or (current_hour in cheapest_hours and boiler.temp < PARAMS["temp_max"])

        temp, step_energy_kWh = boiler.thermical_model(heater_on, draw_off, boiler.time_step)

        energy_kwh += step_energy_kWh

        cost_eur = step_energy_kWh * (current_price / 100)
        cost_whole_day += cost_eur

        energy_history.append(energy_kwh)
        times.append(time_hours)
        temps.append(temp)
        prices.append(current_price)

    comfort = calculate_comfort(temps, PARAMS["temp_min"])

    return (times, temps, prices, cost_whole_day, comfort, energy_history, energy_kwh)