@echo off
REM trigger_kick.bat - Toggle kick drum pad
curl -X POST http://localhost:5000/pad/trigger -H "Content-Type: application/json" -d "{\"pad_id\": \"kick\"}" -s -w "\n"