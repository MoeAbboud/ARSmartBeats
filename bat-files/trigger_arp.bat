@echo off
REM trigger_arp.bat - Toggle arp pad
curl -X POST http://localhost:5000/pad/trigger -H "Content-Type: application/json" -d "{\"pad_id\": \"arp\"}" -s -w "\n"
