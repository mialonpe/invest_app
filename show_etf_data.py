import sqlite3
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)


def get_data():
    conn = sqlite3.connect("comparison_data.db")
    cursor = conn.cursor()

    sp500 = cursor.execute(
    "SELECT date, close FROM sp500 WHERE date >= '1990-01-01' ORDER BY date ASC"
    ).fetchall()

    msci = cursor.execute(
        "SELECT date, close FROM msci_world ORDER BY date ASC"
    ).fetchall()

    dcam = cursor.execute(
        "SELECT date, close FROM dcam ORDER BY date ASC"
    ).fetchall()

    conn.close()

    def to_records(rows):
        return [{"date": row[0], "value": row[1]} for row in rows]

    return {
        "sp500": to_records(sp500),
        "msci":  to_records(msci),
        "dcam":  to_records(dcam),
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