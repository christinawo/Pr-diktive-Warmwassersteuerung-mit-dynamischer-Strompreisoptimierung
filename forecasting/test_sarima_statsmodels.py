from data.database_prices import get_complete_days, load_price_data, convert_to_15minutes


from demand_profile.family_household import family_demand_bathtub
from forecasting.prep_data import generate_demand_dataset, hourly_demand
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, root_mean_squared_error

import numpy as np
import random
random.seed(1)

from forecasting.sarima_statsmodels import sarima_forecast

df = load_price_data()
complete_days = get_complete_days(convert_to_15minutes(df))

results = {}

dataset = generate_demand_dataset(complete_days, 400, family_demand_bathtub)

training_windows = [
    30,
    60,
    90,
    180,
    365
]
test_start = 366

for training_window in training_windows:
    results[training_window] = {
        "mae": [],
        "rmse": [],
        "volume_error": [],
        "actual_volume": [],
        "forecast_volume": [],
        "converged": []
    }

for training_window in training_windows:
    print(f"Training window: {training_window} days")
    for test_index in range(test_start, len(dataset)):
        training_days = dataset[test_index - training_window:test_index]
        training_data = []

        for day in training_days:
            hourly_consumption = hourly_demand(day["consumption"])
            training_data.extend(hourly_consumption)

        test_day = dataset[test_index]

        actual_consumption = hourly_demand(test_day["consumption"])

        print(f"Test day: {test_day['date']}")

        forecast, converged, fitted_model = sarima_forecast(
            training_data,
            order=(1, 0, 0),
            seasonal_order=(1, 0, 0, 24),
            steps=24,
            trend="c")

        actual_volume = sum(actual_consumption)
        forecast_volume = sum(forecast)
        mae = mean_absolute_error(actual_consumption, forecast)
        rmse = root_mean_squared_error(actual_consumption, forecast)
        volume_error = abs(actual_volume - forecast_volume)

        results[training_window]["actual_volume"].append(actual_volume)
        results[training_window]["forecast_volume"].append(forecast_volume)
        results[training_window]["mae"].append(mae)
        results[training_window]["rmse"].append(rmse)
        results[training_window]["volume_error"].append(volume_error)
        results[training_window]["converged"].append(converged)

for training_window in training_windows:
    mean_actual_volume = np.mean(results[training_window]["actual_volume"])
    mean_forecast_volume = np.mean(results[training_window]["forecast_volume"])
    mean_mae = np.mean(results[training_window]["mae"])
    mean_rmse = np.mean(results[training_window]["rmse"])
    mean_volume_error = np.mean(results[training_window]["volume_error"])

    converged_count = sum(results[training_window]["converged"])
    total_fits = len(results[training_window]["converged"])

    print(f"Training window: {training_window} days")
    print(f"Mean actual daily volume: {mean_actual_volume:.2f} L")
    print(f"Mean forecast daily volume: {mean_forecast_volume:.2f} L")
    print(f"Mean MAE: {mean_mae:.2f} L")
    print(f"Mean RMSE: {mean_rmse:.2f} L")
    print(f"Mean daily volume error: {mean_volume_error:.2f} L")
    print(f"Converged: {converged_count}/{total_fits}")

plt.figure()
plt.plot(range(24), actual_consumption, label="Actual demand", marker="o")
plt.plot(range(24), forecast, label="SARIMA forecast", marker="o")
plt.xlabel("Hour")
plt.ylabel("Hot water demand [L]")
plt.title("Actual vs. predicted hot water demand")
plt.xticks(range(0, 24, 2))
plt.legend()
plt.grid()
plt.show()

plt.figure()
plt.plot(training_data[:24 * 7])
plt.xlabel("15 Minutes step")
plt.ylabel("Hot water demand [L]")
plt.title("Hot water consumption over 7 days")
plt.show()

# check_stationary(training_data)
# plot_correlations(training_data)