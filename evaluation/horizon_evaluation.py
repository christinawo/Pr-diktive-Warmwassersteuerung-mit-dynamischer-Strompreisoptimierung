from models.boiler import Boiler
from data.params import PARAMS
import random
random.seed(1)

from controller.predictive_simulation import predictive_simulation

from forecasting.prep_data import profile_to_timeseries, hourly_demand, forecast_to_15minutes
from forecasting.sarima import sarima_forecast, estimate_parameters

from demand_profile.family_household import family_demand_bathtub, family_demand_no_bathtub
from demand_profile.single_household import single_demand_bathtub, single_demand_no_bathtub

from data.database_prices import get_complete_days, load_price_data, convert_to_15minutes

from evaluation.evaluation import calculate_comfort

df = load_price_data()

profiles = [
    ("Family Household with bathtub", family_demand_bathtub),
    ("Family Household without bathtub", family_demand_no_bathtub),
    ("Single Household with bathtub", single_demand_bathtub),
    ("Single Household without bathtub", single_demand_no_bathtub)
]

horizons = [
    (8, "2 h"),
    (16, "4 h"),
    (24, "6 h"),
    (32, "8 h"),
    (40, "10 h"),
    (48, "12 h"),
    (64, "16 h"),
    (96, "24 h")
]

results = []

complete_days = get_complete_days(convert_to_15minutes(df))

training_days_count = 30
days_count = 100

training_days = complete_days[:training_days_count]

simulation_days = complete_days[training_days_count: training_days_count + days_count]

for profile_name, profile_function in profiles:
    training_demand_days = {}
    print(f"Demand profile: {profile_name}")

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

    total_cost = 0.0
    total_energy = 0.0
    all_temps = []

    sarima_history = list(training_data)

    for horizon_steps, horizon_name in horizons:
        boiler = Boiler(PARAMS)
        total_cost = 0.0
        total_energy = 0.0
        all_temps = []
        sarima_history = list(training_data)

        for day, daily_prices in simulation_days:
            hourly_forecast = sarima_forecast(
                history=sarima_history,
                intercept=intercept,
                ar1=ar1,
                seasonal_ar1=seasonal_ar1,
                steps=24,
            )

            demand_forecast = forecast_to_15minutes(hourly_forecast)
            daily_profile = demand_days[day]

            (times, temps, prices, cost, comfort, energy_history, energy) = predictive_simulation(
                daily_profile,
                daily_prices,
                boiler,
                demand_forecast,
                horizon_steps)

            total_cost += cost
            total_energy += energy
            all_temps.extend(temps)


            actual_consumption = profile_to_timeseries(daily_profile)
            actual_hourly = hourly_demand(actual_consumption)
            sarima_history.extend(actual_hourly)

        total_comfort = calculate_comfort(all_temps, PARAMS["temp_min"])
        results.append((profile_name, horizon_name, total_cost, total_comfort, total_energy, boiler.temp))
        print(f"Horizon: {horizon_name} | Cost: {total_cost:.2f}€ | Comfort: {total_comfort:.2f}% | Energy: {total_energy:.2f} kWh | End temperature: {boiler.temp:.2f} °C")