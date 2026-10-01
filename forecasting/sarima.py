import numpy as np

def sarima_forecast(history, intercept, ar1, seasonal_ar1, steps):
    data = list(history)
    forecast = []

    for _ in range(steps):
        y_1 = data[-1]
        y_24 = data[-24]
        y_25 = data[-25]

        # Sarima(1,0,0)(1,0,0,24) forecast
        prediction = (intercept + ar1 * y_1 + seasonal_ar1 * y_24 - ar1 * seasonal_ar1 * y_25)

        # Hot-water demand cannot be negative
        prediction = max(prediction, 0.0)

        forecast.append(prediction)
        data.append(prediction)

    return np.array(forecast)


# Helper function: calculates the intercept and training error for given AR parameters
def evaluate_parameters(data, ar1, seasonal_ar1):
    residual_values = []

    for t in range(25, len(data)):
        residual_value = (data[t] - ar1 * data[t - 1] - seasonal_ar1 * data[t - 24] + ar1 * seasonal_ar1 * data[t - 25])
        residual_values.append(residual_value)

    # Optimal intercept for these AR parameters
    intercept = np.mean(residual_values)

    sum_squared_errors = 0.0

    for value in residual_values:
        error = value - intercept
        sum_squared_errors += error ** 2
    
    return intercept, sum_squared_errors


def estimate_parameters(data):
    data = np.asarray(data, dtype=float)

    # Coarse grid search
    best_sse = float("inf")
    best_intercept = 0.0
    best_ar1 = 0.0
    best_seasonal = 0.0

    ar1_values = np.arange(-0.5, 0.51, 0.05)

    seasonal_values = np.arange(0.0, 0.81, 0.05)

    for ar1 in ar1_values:
        for seasonal_ar1 in seasonal_values:
            intercept, sse = evaluate_parameters(data, ar1,seasonal_ar1)

            # Smaller sum squared error = better Parameters
            if sse < best_sse:
                best_sse = sse
                best_intercept = intercept
                best_ar1 = ar1
                best_seasonal = seasonal_ar1


    # Fine grid search
    fine_ar1_values = np.arange(best_ar1 - 0.05, best_ar1 + 0.051, 0.01)

    fine_seasonal_values = np.arange(max(0.0, best_seasonal - 0.05), best_seasonal + 0.051, 0.01)

    for ar1 in fine_ar1_values:
        for seasonal_ar1 in fine_seasonal_values:
            intercept, sse = evaluate_parameters(data, ar1,seasonal_ar1)

            if sse < best_sse:
                best_sse = sse
                best_intercept = intercept
                best_ar1 = ar1
                best_seasonal = seasonal_ar1

    return best_intercept, best_ar1, best_seasonal