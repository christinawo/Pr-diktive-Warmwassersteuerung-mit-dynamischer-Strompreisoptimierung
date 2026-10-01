# This file compares my own Sarima implementation with the statsmodels implementation
import random
import numpy as np

from sklearn.metrics import mean_absolute_error, root_mean_squared_error

from data.database_prices import get_complete_days, load_price_data, convert_to_15minutes

from demand_profile.family_household import family_demand_bathtub

from forecasting.prep_data import generate_demand_dataset, hourly_demand
from forecasting.sarima_statsmodels import sarima_forecast_statsmodels
from forecasting.sarima import sarima_forecast, estimate_parameters

random.seed(1)

df = load_price_data()

complete_days = get_complete_days(convert_to_15minutes(df))

dataset = generate_demand_dataset(complete_days, 100, family_demand_bathtub)

training_window = 30
number_of_test_days = 34

stats_mae_values = []
stats_rmse_values = []
stats_volume_errors = []

own_mae_values = []
own_rmse_values = []
own_volume_errors = []

for test_index in range(training_window, training_window + number_of_test_days):
    training_days = dataset[test_index - training_window:test_index]

    test_day = dataset[test_index]

    training_data = []

    for day in training_days:
        hourly_consumption = hourly_demand(day["consumption"])
        training_data.extend(hourly_consumption)

    actual_consumption = np.array(hourly_demand(test_day["consumption"]))


    statsmodels_forecast, converged, fitted_model = sarima_forecast_statsmodels(
            training_data,
            order=(1, 0, 0),
            seasonal_order=(1, 0, 0, 24),
            steps=24,
            trend="c"
        )
    
    own_intercept, own_ar1, own_seasonal = estimate_parameters(training_data)

    own_forecast = sarima_forecast(
        history=training_data,
        intercept=own_intercept,
        ar1=own_ar1,
        seasonal_ar1=own_seasonal,
        steps=24
    )

    stats_mae = mean_absolute_error(actual_consumption, statsmodels_forecast)
    stats_rmse = root_mean_squared_error(actual_consumption, statsmodels_forecast)
    stats_volume_error = abs(np.sum(actual_consumption) - np.sum(statsmodels_forecast))

    stats_mae_values.append(stats_mae)
    stats_rmse_values.append(stats_rmse)
    stats_volume_errors.append(stats_volume_error)


    own_mae = mean_absolute_error(actual_consumption, own_forecast)
    own_rmse = root_mean_squared_error(actual_consumption, own_forecast)
    own_volume_error = abs(np.sum(actual_consumption) - np.sum(own_forecast))

    own_mae_values.append(own_mae)
    own_rmse_values.append(own_rmse)
    own_volume_errors.append(own_volume_error)

    print(f"Day {test_index - training_window + 1:02d} | Stats MAE: {stats_mae:6.2f} | Own MAE: {own_mae:6.2f}")

print(f"Test days: {number_of_test_days}")
print("Statsmodels:")
print(f"Mean MAE: {np.mean(stats_mae_values):.2f} L")
print(f"Mean RMSE: {np.mean(stats_rmse_values):.2f} L")
print(f"Mean volume error: {np.mean(stats_volume_errors):.2f} L")

print("Own SARIMA:")
print(f"Mean MAE: {np.mean(own_mae_values):.2f} L")
print(f"Mean RMSE: {np.mean(own_rmse_values):.2f} L")
print(f"Mean volume error: {np.mean(own_volume_errors):.2f} L")