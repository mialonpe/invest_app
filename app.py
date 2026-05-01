import threading
import time
import webview
import sys
import os
import sqlite3
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ── Find files whether running as .exe or script ──────────────────────────────
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)

def get_db_path():
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(os.path.dirname(sys.executable), "comparison_data.db")
    return os.path.join(os.path.dirname(__file__), "comparison_data.db")

# ── Data layer ────────────────────────────────────────────────────────────────
def normalize(data):
    if not data:
        return []
    first = data[0][1]
    return [
        {"date": row[0], "value": round((row[1] - first) / first * 100, 4)}
        for row in data
    ]

def get_data():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    sp500 = cursor.execute("SELECT date, close FROM sp500 ORDER BY date").fetchall()
    msci  = cursor.execute("SELECT date, close FROM msci_world ORDER BY date").fetchall()
    dcam  = cursor.execute("SELECT date, close FROM dcam ORDER BY date").fetchall()
    conn.close()
    return {
        "sp500": normalize(sp500),
        "msci":  normalize(msci),
        "dcam":  normalize(dcam),
        "exported_at": datetime.now().isoformat()
    }

# ── Flask routes ──────────────────────────────────────────────────────────────
@app.route("/api/data")
def api_data():
    return jsonify(get_data())

@app.route("/")
def index():
    return send_from_directory(resource_path("."), "dashboard.html")

# ── Start Flask in background thread ─────────────────────────────────────────
def start_flask():
    app.run(port=5000, debug=False, use_reloader=False)

flask_thread = threading.Thread(target=start_flask, daemon=True)
flask_thread.start()

time.sleep(1.5)

# ── Open desktop window ───────────────────────────────────────────────────────
window = webview.create_window(
    title="Market Dashboard",
    url="http://localhost:5000",
    width=1280,
    height=820,
    min_size=(800, 600),
    resizable=True
)

webview.start()
print("✅ App closed")