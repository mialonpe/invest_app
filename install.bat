@echo off
echo Installing dependencies...
py -m pip install yfinance

echo Creating scheduled task...
schtasks /create /tn "ETF Data Refresh" /tr "py \"%~dp0get_etf_data.py\"" /sc daily /st 00:00 /f

echo.
echo Done! Task scheduled to run every day at midnight.
pause