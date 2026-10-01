import requests
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

DATABASE = "evaluation.db"


def create_price_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS price_history (
        timestamp INTEGER PRIMARY KEY,
        price REAL
    )
    """)

    conn.commit()
    conn.close()


def download_price_history(days=900):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    start_ms = int(start_date.timestamp() * 1000)
    end_ms = int(end_date.timestamp() * 1000)

    url = (f"https://api.awattar.at/v1/marketdata"
           f"?start={start_ms}&end={end_ms}")

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    data = response.json()["data"]

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    for row in data:

        cursor.execute("""
        INSERT OR REPLACE INTO price_history
        VALUES (?, ?)
        """,
        (row["start_timestamp"], row["marketprice"])
        )

    conn.commit()
    conn.close()

    print(f"{len(data)} price points stored.")

def load_price_data():
    conn = sqlite3.connect(DATABASE)

    df = pd.read_sql_query("""
        SELECT timestamp, price
        FROM price_history
        ORDER BY timestamp
        """, conn)

    conn.close()

    df["date"] = pd.to_datetime(df["timestamp"], unit = "ms", utc = True)

    df["date"] = df["date"].dt.tz_convert("Europe/Vienna")

    # EUR/MWh --> ct/kWh
    df["price_ct_per_kWh"] = df["price"] / 10

    return df

# We get from the API hourly data, so for my implementation I need to convert it to 15min data
def convert_to_15minutes(df):
    df = df.copy()
    df = df.set_index("date")
    df_15min = df.resample("15min").ffill()
    df_15min = df_15min.reset_index()
    df_15min["month"] = df_15min["date"].dt.month
    df_15min["weekday"] = df_15min["date"].dt.weekday

    df_15min["time_hours"] = (df_15min["date"].dt.hour + df_15min["date"].dt.minute / 60)

    return df_15min

def get_complete_days(df_15min):
    df = df_15min.copy()
    df["day"] = df["date"].dt.date

    complete_days = []

    for day, day_data in df.groupby("day"):
        if len(day_data) == 96:
            complete_days.append(
                (day, day_data.reset_index(drop=True))
            )

    return complete_days