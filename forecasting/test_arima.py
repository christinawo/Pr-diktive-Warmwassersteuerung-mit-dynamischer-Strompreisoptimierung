from data.database_prices import get_complete_days, load_price_data, convert_to_15minutes

from demand_profile.family_household import family_demand_bathtub

from forecasting.prep_data import generate_demand_dataset
from forecasting.arima import arima_forecast

import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, root_mean_squared_error

import numpy as np
import random
random.seed(1)

df = load_price_data()
complete_days = get_complete_days(convert_to_15minutes(df))

orders = [
    (2, 0, 0),
    (2, 0, 1),
    (1, 0, 0),
    (1, 0, 1)
]

results = {}

for order in orders:
    results[order] = {
        "mae": [],
        "rmse": [],
        "volume_error": []
    }

dataset = generate_demand_dataset(complete_days, 60, family_demand_bathtub)

training_window = 30

for test_index in range(training_window, len(dataset)):
    training_days = dataset[test_index - training_window:test_index]
    training_data = []

    for day in training_days:
        training_data.extend(day["consumption"])

    test_day = dataset[test_index]
    actual_consumption = test_day["consumption"]

    print(f"Test day: {test_day['date']}")

    for order in orders:
        forecast = arima_forecast(training_data, order=order, steps=96)
        
        mae = mean_absolute_error(actual_consumption, forecast)
        rmse = root_mean_squared_error(actual_consumption, forecast)
        volume_error = abs(sum(actual_consumption) - sum(forecast))

        results[order]["mae"].append(mae)
        results[order]["rmse"].append(rmse)
        results[order]["volume_error"].append(volume_error)

for order in orders:
    mean_mae = np.mean(results[order]["mae"])
    mean_rmse = np.mean(results[order]["rmse"])
    mean_volume_error = np.mean(results[order]["volume_error"])

    print(f"Arima order: {order}")
    print(f"Mean MAE: {mean_mae:.2f} L")
    print(f"Mean RMSE: {mean_rmse:.2f} L")
    print(f"Mean daily volume error: {mean_volume_error:.2f} L")

# plt.figure()
# plt.plot(training_data[:96 * 7])
# plt.xlabel("15 Minutes step")
# plt.ylabel("Hot water demand [L]")
# plt.title("Hot water consumption over 7 days")
# plt.show()
