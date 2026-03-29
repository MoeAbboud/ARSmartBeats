@echo off
REM trigger_atmosphere.bat - Toggle atmosphere pad
curl -X POST http://localhost:5000/pad/trigger -H "Content-Type: application/json" -d "{\"pad_id\": \"atmosphere\"}" -s -w "\n"
