from models.boiler import Boiler
from data.params import PARAMS
import time
import numpy as np
import random
random.seed(1)

from controller.dummy_strategy import dummy_strategy
from controller.temperature_strategy import temperature_strategy
from controller.threshold_price_strategy import simple_price_strategy
from controller.n_cheapest_hours_strategy import cheapest_hours_strategy
from controller.predictive_simulation import predictive_simulation

from forecasting.prep_data import profile_to_timeseries, hourly_demand, forecast_to_15minutes
from forecasting.sarima import sarima_forecast, estimate_parameters

from demand_profile.family_household import family_demand_bathtub, family_demand_no_bathtub, family_demand_irregular
from demand_profile.single_household import single_demand_bathtub, single_demand_no_bathtub, single_demand_irregular

from data.database_evaluation import create_database, save_result
from data.database_prices import get_complete_days, load_price_data, convert_to_15minutes

from evaluation.evaluation import calculate_comfort, calculate_co2, calculate_runtime
from evaluation.evaluate_boiler_size import create_size_params
from evaluation.price_volatility import adjust_prices
from evaluation.export_results import export_results

create_database()
df = load_price_data()

profiles = [
    ("Family Household with bathtub", family_demand_bathtub),
    ("Family Household without bathtub", family_demand_no_bathtub),
    ("Family Household with irregular demand", family_demand_irregular),
    ("Single Household with bathtub", single_demand_bathtub),
    ("Single Household without bathtub", single_demand_no_bathtub),
    ("Single Household with irregular demand", single_demand_irregular)
]

strategies = [
    ("Temperature Strategy", temperature_strategy),
    ("Dummy Strategy", dummy_strategy),
    ("Threshold Price Strategy", simple_price_strategy),
    ("Cheapest Hour Strategy", cheapest_hours_strategy)
]

boiler_sizes = [
    100.0,
    200.0,
    300.0
]

volatility_scenarios = [
    ("Low Volatility", 0.5),
    ("Default Prices", 1.0),
    ("High Volatility", 1.5)
]

results = []

complete_days = get_complete_days(convert_to_15minutes(df))

training_days_count = 30
days_count = 365

training_days = complete_days[:training_days_count]

simulation_days = complete_days[training_days_count:training_days_count + days_count]

# Prepare volatility scenarios
mean_price = np.mean([price for day, daily_prices in simulation_days for price in daily_prices["price"]])

volatility_days = {}

for volatility_name, factor in volatility_scenarios:
    volatility_days[volatility_name] = [(day, adjust_prices(daily_prices, factor, mean_price)) for day, daily_prices in simulation_days]

for profile_name, profile_function in profiles:
    print(f"Processing: {profile_name}")
    training_demand_days = {}

    for day, daily_prices in training_days:
        training_demand_days[day] = profile_function(day.weekday(), day.month)

    training_data = []

    for day, daily_prices in training_days:
        daily_profile = training_demand_days[day]
        consumption_15min = profile_to_timeseries(daily_profile)
        consumption_hourly = hourly_demand(consumption_15min)
        training_data.extend(consumption_hourly)

    intercept, ar1, seasonal_ar1 = estimate_parameters(training_data)

    demand_days = {}

    for day, daily_prices in simulation_days:
        demand_days[day] = profile_function(day.weekday(), day.month)

    for boiler_size in boiler_sizes:
        print(f"Boiler size: {boiler_size:.0f} L")
        boiler_params = create_size_params(boiler_size)

        for volatility_name, factor in volatility_scenarios:
            current_days = volatility_days[volatility_name]

            # Baseline strategies
            for strategy_name, strategy_function in strategies:
                boiler = Boiler(boiler_params)

                total_cost = 0.0
                total_energy = 0.0
                all_temps = []

                start_time = time.perf_counter()

                for day, daily_prices in current_days:
                    daily_profile = demand_days[day]

                    (times, temps, prices, cost, comfort, energy_history, energy) = strategy_function(
                        daily_profile,
                        daily_prices,
                        boiler)

                    total_cost += cost
                    total_energy += energy
                    all_temps.extend(temps)

                runtime = calculate_runtime(start_time)
                total_comfort = calculate_comfort(all_temps, PARAMS["temp_min"])
                total_co2 = calculate_co2(total_energy, PARAMS["emission_factor"])

                print(f"{profile_name} | {strategy_name} | End temperature: {boiler.temp:.2f} °C")

                results.append((profile_name, boiler_size, volatility_name, strategy_name, total_cost, total_comfort, total_energy, total_co2, runtime))

                save_result(f"{volatility_name} - {profile_name} - {boiler_size:.0f} L - {strategy_name}", total_cost, total_comfort, total_energy)

            # Predictive Strategy
            boiler = Boiler(boiler_params)

            total_cost = 0.0
            total_energy = 0.0
            all_temps = []

            sarima_history = list(training_data)

            start_time = time.perf_counter()

            for day, daily_prices in current_days:
                hourly_forecast = sarima_forecast(
                    history=sarima_history,
                    intercept=intercept,
                    ar1=ar1,
                    seasonal_ar1=seasonal_ar1,
                    steps=24
                )

                demand_forecast = forecast_to_15minutes(hourly_forecast)

                daily_profile = demand_days[day]

                (times, temps, prices, cost, comfort, energy_history, energy) = predictive_simulation(
                    daily_profile,
                    daily_prices,
                    boiler,
                    demand_forecast,
                    horizon_steps=40
                )

                total_cost += cost
                total_energy += energy
                all_temps.extend(temps)

                actual_consumption = profile_to_timeseries(daily_profile)
                actual_hourly = hourly_demand(actual_consumption)
                sarima_history.extend(actual_hourly)

            runtime = calculate_runtime(start_time)
            total_comfort = calculate_comfort(all_temps, PARAMS["temp_min"])
            total_co2 = calculate_co2(total_energy, PARAMS["emission_factor"])

            print(f"{profile_name} | Predictive Strategy | End temperature: {boiler.temp:.2f} °C")

            results.append((profile_name, boiler_size, volatility_name, "Predictive Strategy", total_cost, total_comfort, total_energy, total_co2, runtime))

            save_result(f"{volatility_name} - {profile_name} - {boiler_size:.0f} L - Predictive Strategy", total_cost, total_comfort, total_energy)

# Export results
export_results(results, days_count)