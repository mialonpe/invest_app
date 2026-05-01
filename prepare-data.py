import sqlite3
import json

conn = sqlite3.connect("comparison_data.db")
cursor = conn.cursor()

sp500_data = cursor.execute("SELECT date, close FROM sp500 ORDER BY date").fetchall()
msci_data  = cursor.execute("SELECT date, close FROM msci_world ORDER BY date").fetchall()
dcam_data  = cursor.execute("SELECT date, close FROM dcam ORDER BY date").fetchall()
conn.close()

def normalize(data):
    first = data[0][1]
    return [{"date": row[0], "value": round((row[1] - first) / first * 100, 4)} for row in data]

output = {
    "sp500": normalize(sp500_data),
    "msci":  normalize(msci_data),
    "dcam":  normalize(dcam_data)
}

with open("market_data.json", "w") as f:
    json.dump(output, f)

print("✅ market_data.json exported successfully")