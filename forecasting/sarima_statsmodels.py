from statsmodels.tsa.statespace.sarimax import SARIMAX
import numpy as np

def sarima_forecast_statsmodels(training_data, order, seasonal_order, steps, trend):
    model = SARIMAX(
        training_data,
        order=order,
        seasonal_order=seasonal_order,
        trend=trend
        )

    fitted_model = model.fit(disp=False)

    forecast = fitted_model.forecast(steps=steps)

    # No negative forecast
    forecast = np.maximum(forecast, 0.0)

    converged = fitted_model.mle_retvals["converged"]

    return forecast, converged, fitted_model