import random
import numpy as np

from forecasting.prep_data import profile_to_timeseries, hourly_demand
from forecasting.sarima import sarima_forecast, estimate_parameters

from demand_profile.family_household import  family_demand_no_bathtub, family_demand_bathtub, family_demand_irregular
from demand_profile.single_household import single_demand_no_bathtub, single_demand_bathtub, single_demand_irregular

from data.database_prices import get_complete_days, load_price_data, convert_to_15minutes

random.seed(1)

training_days_count = 30
test_days_count = 100


profiles = [
    ("Family without bathtub", family_demand_no_bathtub),
    ("Family with bathtub", family_demand_bathtub),
    ("Family irregular", family_demand_irregular),
    ("Single without bathtub", single_demand_no_bathtub),
    ("Single with bathtub", single_demand_bathtub),
    ("Single irregular", single_demand_irregular)
]

df = load_price_data()

complete_days = get_complete_days(convert_to_15minutes(df))

training_days = complete_days[:training_days_count]

test_days = complete_days[training_days_count: training_days_count + test_days_count]

for profile_name, profile_function in profiles:
    training_data = []

    for day, daily_prices in training_days:
        daily_profile = profile_function(day.weekday(), day.month)

        consumption_15min = profile_to_timeseries(daily_profile)

        consumption_hourly = hourly_demand(consumption_15min)

        training_data.extend(consumption_hourly)


    intercept, ar1, seasonal_ar1 = estimate_parameters(training_data)

    sarima_history = list(training_data)

    all_actual = []
    all_forecast = []
    daily_volume_errors = []

    for day, daily_prices in test_days:
        forecast = sarima_forecast(
            history=sarima_history,
            intercept=intercept,
            ar1=ar1,
            seasonal_ar1=seasonal_ar1,
            steps=24
        )

        daily_profile = profile_function(day.weekday(), day.month)

        consumption_15min = profile_to_timeseries(daily_profile)

        actual = hourly_demand(consumption_15min)

        all_actual.extend(actual)
        all_forecast.extend(forecast)
        actual_volume = sum(actual)
        forecast_volume = sum(forecast)

        daily_volume_errors.append(abs(actual_volume - forecast_volume))

        sarima_history.extend(actual)


    actual_array = np.array(all_actual)
    forecast_array = np.array(all_forecast)

    mae = np.mean(np.abs(actual_array - forecast_array))
    rmse = np.sqrt(np.mean((actual_array - forecast_array) ** 2))
    daily_volume_error = np.mean(daily_volume_errors)

    print(profile_name)
    print(f"MAE: {mae:.2f} L/h")
    print(f"RMSE: {rmse:.2f} L/h")
    print(f"Daily volume error: {daily_volume_error:.2f} L/day")
    print()