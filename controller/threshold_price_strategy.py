from data.params import PARAMS
from evaluation.evaluation import calculate_comfort

# Here we are heating when the price is smaller than a threshold
def simple_price_strategy(daily_profile, prices_df, boiler):

    times = []
    temps = []
    prices = []
    energy_history = []
    cost_whole_day = 0.0
    price_threshold = 10.0      # ct/kWh
    energy_kwh = 0.0

    for step in range(96):
        time_hours = prices_df.iloc[step]["time_hours"]
        current_price = prices_df.iloc[step]["price_ct_per_kWh"]
        draw_off = 0.0

        events = daily_profile[step]

        for event in events:
            mixed_volume = event["volume"]
            mixed_temperature = event["temperature"]

            if boiler.temp > mixed_temperature:
                hot_volume = (mixed_volume * (mixed_temperature - boiler.temp_cold)
                              / (boiler.temp - boiler.temp_cold))
            else:
                hot_volume = mixed_volume

            draw_off += (hot_volume / boiler.time_step)

        heater_on = (
            boiler.temp < PARAMS["temp_min"]
            or (
                current_price < price_threshold
                and boiler.temp < 55.0
            )
        )
            
        temp, step_energy_kWh = boiler.thermical_model(heater_on, draw_off, boiler.time_step)

        energy_kwh += step_energy_kWh
        cost_eur = step_energy_kWh * (current_price / 100)
        cost_whole_day += cost_eur

        energy_history.append(energy_kwh)
        times.append(time_hours)
        temps.append(temp)
        prices.append(current_price)

    comfort = calculate_comfort(temps, PARAMS["temp_min"])

    return times, temps, prices, cost_whole_day, comfort, energy_history, energy_kwh