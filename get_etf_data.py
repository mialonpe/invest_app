import yfinance as yf
import sqlite3

# Ticker format for Euronext Paris = SYMBOL.PA
dcam = yf.Ticker("DCAM.PA")
sp500 = yf.Ticker("^GSPC")
msci_world = yf.Ticker("URTH")

# Get all available history
dcam_hist  = dcam.history(period="1y")
sp500_hist = sp500.history(period="1y")
msci_hist  = msci_world.history(period="1y")

conn = sqlite3.connect("comparison_data.db")
cursor = conn.cursor()

# ── Create tables ─────────────────────────────────────────────────────────────
cursor.execute("""
    CREATE TABLE IF NOT EXISTS sp500 (
        date TEXT PRIMARY KEY,
        close REAL
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS msci_world (
        date TEXT PRIMARY KEY,
        close REAL
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS dcam (
        date TEXT PRIMARY KEY,
        close REAL
    )
""")

# ── Insert SP500 ───────────────────────────────────────────────────────────────
for date, row in sp500_hist.iterrows():
    close = row["Close"]  # ✅ close updated each iteration
    cursor.execute("""
        INSERT OR REPLACE INTO sp500 (date, close)
        VALUES (?, ?)
    """, (str(date.date()), close))

# ── Insert MSCI World ──────────────────────────────────────────────────────────
for date, row in msci_hist.iterrows():
    close = row["Close"]  # ✅ was missing — was reusing SP500's last close value!
    cursor.execute("""
        INSERT OR REPLACE INTO msci_world (date, close)
        VALUES (?, ?)
    """, (str(date.date()), close))

# ── Insert DCAM ────────────────────────────────────────────────────────────────
for date, row in dcam_hist.iterrows():
    close = row["Close"]  # ✅ close updated each iteration
    cursor.execute("""
        INSERT OR REPLACE INTO dcam (date, close)
        VALUES (?, ?)
    """, (str(date.date()), close))

# ── Save and close ─────────────────────────────────────────────────────────────
conn.commit()
conn.close()

print(f"✅ Data saved to comparison_data.db")
print(f"   S&P 500 rows    : {len(sp500_hist)}")
print(f"   MSCI World rows : {len(msci_hist)}")
print(f"   DCAM rows       : {len(dcam_hist)}")
print(f"\nDCAM sample:")
print(dcam_hist[["Close"]].head())
print(f"\nFrom: {dcam_hist.index[0].date()} to {dcam_hist.index[-1].date()}")