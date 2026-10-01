import requests
import pandas as pd

API_URL = "https://apis.smartenergy.at/market/v1/price"

def fetch_prices() -> pd.DataFrame:
    # Current day-ahead prices
    response = requests.get(API_URL, timeout=10)
    response.raise_for_status()

    payload = response.json()

    rows = payload["data"]

    df = pd.DataFrame(rows)
    df = df.rename(columns={"value": "price_ct_per_kWh"})
    df["date"] = pd.to_datetime(df["date"])

    df["month"] = df["date"].dt.month
    df["weekday"] = df["date"].dt.weekday
    df["time_hours"] = df["date"].dt.hour + df["date"].dt.minute / 60

    return df