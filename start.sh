#!/bin/bash
echo "📥 Fetching data..."
python fetch-data.py

echo "🚀 Starting server..."
python show_etf_data.py