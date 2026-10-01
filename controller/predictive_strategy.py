from data.params import PARAMS

import copy

def calculate_upcoming_demand(demand_forecast, current_step, horizon_steps):
    end_step = min(current_step + horizon_steps, len(demand_forecast))

    upcoming_demand = sum(demand_forecast[current_step:end_step])

    return upcoming_demand

def predict_temperature_without_heating(boiler, demand_forecast, current_step, horizon_steps):
    # Copy boiler, so the real boiler state does not change
    predicted_boiler = copy.deepcopy(boiler)

    end_step = min(current_step + horizon_steps, len(demand_forecast))

    temperatures = []

    for step in range(current_step, end_step):
        mixed_volume = demand_forecast[step]

        # Hot water demand for a target temperature of 40°C
        if predicted_boiler.temp > 40.0:
            hot_volume = (mixed_volume * (40.0 - predicted_boiler.temp_cold)/
                    (predicted_boiler.temp - predicted_boiler.temp_cold))
        else:
            hot_volume = mixed_volume

        draw_off = (hot_volume / predicted_boiler.time_step)

        temperature, energy_kWh_step = (predicted_boiler.thermical_model(heater_on=False, draw_off=draw_off, dt_s=predicted_boiler.time_step))

        temperatures.append(temperature)

    return temperatures

def predict_temperature_with_heating(boiler, demand_forecast, current_step, horizon_steps, heating_steps):
    # Copy boiler, so the real boiler state does not change
    predicted_boiler = copy.deepcopy(boiler)

    end_step = min(current_step + horizon_steps, len(demand_forecast))

    temperatures = []

    for step in range(current_step, end_step):
        mixed_volume = demand_forecast[step]

        # Hot water demand for a target temperature of 40°C
        if predicted_boiler.temp > 40.0: 
            hot_volume = (mixed_volume * (40.0 - predicted_boiler.temp_cold)
                          / (predicted_boiler.temp - predicted_boiler.temp_cold))
        else:
            hot_volume = mixed_volume

        draw_off = (hot_volume / predicted_boiler.time_step)

        heater_on = step in heating_steps

        temperature, energy_kWh_step = predicted_boiler.thermical_model(heater_on=heater_on, draw_off=draw_off, dt_s=predicted_boiler.time_step)
        temperatures.append(temperature)

    return temperatures

def find_first_critical_step(predicted_temperatures, temp_min):
    for step, temperature in enumerate(predicted_temperatures):
        if temperature < temp_min:
            return step
    return None

def find_required_heating_steps(boiler, demand_forecast, prices, current_step, horizon_steps, temp_min):
    heating_steps = []

    horizon_end = min(current_step + horizon_steps, len(demand_forecast))

    while True:
        predicted_temperatures = predict_temperature_with_heating(
            boiler,
            demand_forecast,
            current_step,
            horizon_steps,
            heating_steps
        )

        critical_step = find_first_critical_step(predicted_temperatures, temp_min)

        # Entire horizon is safe
        if critical_step is None:
            break

        # Convert relative forecast position to absolute simulation step
        critical_absolute_step = current_step + critical_step

        # Candidate heating steps before the critical point
        candidate_steps = [
            step
            for step in range(current_step, critical_absolute_step + 1)
            if step not in heating_steps
        ]

        if not candidate_steps:
            break

        # Cheapest available step before the critical point
        cheapest_step = min(candidate_steps, key=lambda step: prices.iloc[step]["price_ct_per_kWh"])

        heating_steps.append(cheapest_step)

        if len(heating_steps) >= horizon_end - current_step:
            break

    return heating_steps

def predictive_strategy(boiler, demand_forecast, prices, current_step, horizon_steps=40):
    if boiler.temp >= boiler.temp_max:
        return False

    if boiler.temp < PARAMS["temp_min"]:
        return True

    predicted_temperatures = predict_temperature_without_heating(boiler, demand_forecast, current_step, horizon_steps)
    
    critical_step = find_first_critical_step(predicted_temperatures, PARAMS["temp_min"])

    if critical_step is None:
        current_price = prices.iloc[current_step]["price_ct_per_kWh"]

        end_step = min(current_step + horizon_steps, len(prices))

        future_prices = prices.iloc[current_step:end_step]["price_ct_per_kWh"]

        cheap_price_limit = future_prices.quantile(0.25)

        upcoming_demand = calculate_upcoming_demand(demand_forecast, current_step, horizon_steps)

        if (current_price <= cheap_price_limit
            and upcoming_demand > 20.0
            and boiler.temp < 60.0):
            return True

        return False

    heating_steps = find_required_heating_steps(
        boiler,
        demand_forecast,
        prices,
        current_step,
        horizon_steps,
        PARAMS["temp_min"]
    )

    return current_step in heating_steps