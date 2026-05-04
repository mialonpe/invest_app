import sqlite3
import os
import yfinance as yf
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import schedule
import threading
import time

app = Flask(__name__)
CORS(app)

def get_db_path():
    return os.path.join(os.path.dirname(__file__), "comparison_data.db")

# ── Fetch & save data ─────────────────────────────────────────────────────────
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
        print(f"❌ Fetch error: {e}")

# ── Scheduler ─────────────────────────────────────────────────────────────────
def run_scheduler():
    schedule.every().day.at("00:00").do(fetch_and_save)
    while True:
        schedule.run_pending()
        time.sleep(30)

# ── Normalize ─────────────────────────────────────────────────────────────────
def normalize(data):
    if not data:
        return []
    first = data[0][1]
    return [
        {"date": row[0], "value": round((row[1] - first) / first * 100, 4)}
        for row in data
    ]

# ── Flask routes ──────────────────────────────────────────────────────────────
@app.route("/api/data")
def api_data():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    sp500 = cursor.execute("SELECT date, close FROM sp500 ORDER BY date").fetchall()
    msci  = cursor.execute("SELECT date, close FROM msci_world ORDER BY date").fetchall()
    dcam  = cursor.execute("SELECT date, close FROM dcam ORDER BY date").fetchall()
    conn.close()
    return jsonify({
        "sp500": normalize(sp500),
        "msci":  normalize(msci),
        "dcam":  normalize(dcam),
        "exported_at": datetime.now().isoformat()
    })

@app.route("/")
def index():
    return send_from_directory(".", "dashboard.html")

# ── Start scheduler on startup ────────────────────────────────────────────────
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

# ── Fetch data on first launch if db is empty ─────────────────────────────────
def init_data():
    if not os.path.exists(get_db_path()):
        fetch_and_save()

init_data()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)