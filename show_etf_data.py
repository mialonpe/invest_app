import sqlite3
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)  # ← fixes the browser blocking issue

def normalize(data):
    if not data:
        return []
    first = data[0][1]
    return [
        {"date": row[0], "value": round((row[1] - first) / first * 100, 4)}
        for row in data
    ]

def get_data():
    conn = sqlite3.connect("comparison_data.db")
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

@app.route("/api/data")
def api_data():
    return jsonify(get_data())

@app.route("/")
def index():
    return send_from_directory(".", "dashboard.html")

if __name__ == "__main__":
    print("✅ Server running at http://localhost:5000")
    print("   Press Ctrl+C to stop")
    app.run(debug=True, port=5000)