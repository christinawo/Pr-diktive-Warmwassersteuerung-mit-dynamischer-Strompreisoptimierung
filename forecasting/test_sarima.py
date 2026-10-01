# Compares different training window sizes for the Sarima model

from data.database_prices import (
    get_complete_days,
    load_price_data,
    convert_to_15minutes
)

from demand_profile.family_household import family_demand_bathtub

from forecasting.prep_data import (generate_demand_dataset, hourly_demand)
from forecasting.sarima_statsmodels import sarima_forecast_statsmodels
from forecasting.sarima import (sarima_forecast, estimate_sarima_parameters)

from sklearn.metrics import (mean_absolute_error, root_mean_squared_error)

import matplotlib.pyplot as plt
import numpy as np
import random
random.seed(1)


df = load_price_data()

complete_days = get_complete_days(convert_to_15minutes(df))

dataset = generate_demand_dataset(
    complete_days,
    100,
    family_demand_bathtub
)

training_window = 30

training_days = dataset[:training_window]
test_day = dataset[training_window]

training_data = []

for day in training_days:
    hourly_consumption = hourly_demand(day["consumption"])
    training_data.extend(hourly_consumption)

actual_consumption = np.array(hourly_demand(test_day["consumption"]))

# Statsmodels
statsmodels_forecast, converged, fitted_model = (
    sarima_forecast_statsmodels(
        training_data,
        order=(1, 0, 0),
        seasonal_order=(1, 0, 0, 24),
        steps=24,
        trend="c"
    )
)

params = dict(
    zip(
        fitted_model.param_names,
        fitted_model.params
    )
)

stats_intercept = params["intercept"]
stats_ar1 = params["ar.L1"]
stats_seasonal = params["ar.S.L24"]

own_intercept, own_ar1, own_seasonal = (
    estimate_sarima_parameters(
        training_data
    )
)
own_forecast = sarima_forecast(
    history=training_data,
    intercept=own_intercept,
    ar1=own_ar1,
    seasonal_ar1=own_seasonal,
    steps=24
)

print("PARAMETER COMPARISON")
print("Statsmodels:")
print(f"Intercept: {stats_intercept:.6f}")
print(f"AR(1): {stats_ar1:.6f}")
print(f"Seasonal AR(24): {stats_seasonal:.6f}")

print("Own estimation:")
print(f"Intercept: {own_intercept:.6f}")
print(f"AR(1): {own_ar1:.6f}")
print(f"Seasonal AR(24): {own_seasonal:.6f}")

print("Hour | statsmodels | own model | difference")

for hour in range(24):
    difference = abs(statsmodels_forecast[hour] - own_forecast[hour])

    print(
        f"{hour:02d}   | "
        f"{statsmodels_forecast[hour]:10.4f} | "
        f"{own_forecast[hour]:9.4f} | "
        f"{difference:10.4f}"
    )

stats_mae = mean_absolute_error(actual_consumption, statsmodels_forecast)
own_mae = mean_absolute_error(actual_consumption, own_forecast)
stats_rmse = root_mean_squared_error(actual_consumption, statsmodels_forecast)
own_rmse = root_mean_squared_error(actual_consumption, own_forecast)
stats_volume_error = abs(np.sum(actual_consumption) - np.sum(statsmodels_forecast))
own_volume_error = abs(np.sum(actual_consumption) - np.sum(own_forecast))

print("FORECAST QUALITY")
print(f"Actual daily volume: {np.sum(actual_consumption):.2f} L")

print("Statsmodels:")
print(f"Forecast volume: {np.sum(statsmodels_forecast):.2f} L")
print(f"MAE: {stats_mae:.2f} L")
print(f"RMSE: {stats_rmse:.2f} L")
print(f"Volume error:    {stats_volume_error:.2f} L")

print("Own model:")
print(f"Forecast volume: {np.sum(own_forecast):.2f} L")
print(f"MAE: {own_mae:.2f} L")
print(f"RMSE: {own_rmse:.2f} L")
print(f"Volume error: {own_volume_error:.2f} L")

plt.figure()
plt.plot(
    range(24),
    actual_consumption,
    label="Actual demand",
    marker="o"
)

plt.plot(
    range(24),
    own_forecast,
    label="SARIMA forecast",
    marker="o"
)
plt.show()