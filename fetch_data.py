import sqlite3
import os
import yfinance as yf
from datetime import datetime

def get_db_path():
    return os.path.join(os.path.dirname(__file__), "comparison_data.db")

def fetch_and_save():
    print(f"🔄 Fetching data at {datetime.now()}...")
    try:
        dcam       = yf.Ticker("DCAM.PA")
        sp500      = yf.Ticker("^GSPC")
        msci_world = yf.Ticker("URTH")

        dcam_hist  = dcam.history(period="1y")
        sp500_hist = sp500.history(period="1y")
        msci_hist  = msci_world.history(period="1y")

        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()

        cursor.execute("CREATE TABLE IF NOT EXISTS sp500 (date TEXT PRIMARY KEY, close REAL)")
        cursor.execute("CREATE TABLE IF NOT EXISTS msci_world (date TEXT PRIMARY KEY, close REAL)")
        cursor.execute("CREATE TABLE IF NOT EXISTS dcam (date TEXT PRIMARY KEY, close REAL)")

        for date, row in sp500_hist.iterrows():
            cursor.execute("INSERT OR REPLACE INTO sp500 VALUES (?, ?)", (str(date.date()), row["Close"]))
        for date, row in msci_hist.iterrows():
            cursor.execute("INSERT OR REPLACE INTO msci_world VALUES (?, ?)", (str(date.date()), row["Close"]))
        for date, row in dcam_hist.iterrows():
            cursor.execute("INSERT OR REPLACE INTO dcam VALUES (?, ?)", (str(date.date()), row["Close"]))

        conn.commit()
        conn.close()
        print(f"✅ Data updated at {datetime.now()}")
    except Exception as e:
        print(f"❌ Error: {e}")

fetch_and_save()