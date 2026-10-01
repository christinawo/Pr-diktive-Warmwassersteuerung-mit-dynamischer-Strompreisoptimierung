from statsmodels.tsa.arima.model import ARIMA
import numpy as np

def arima_forecast(training_data, order, steps=96):
    model = ARIMA(training_data, order=order)

    fitted_model = model.fit()

    forecast = fitted_model.forecast(steps=steps)

    # No negative forecast
    forecast = np.maximum(forecast, 0.0)

    return forecast