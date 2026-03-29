@echo off
REM trigger_hihat.bat - Toggle hi-hat pad
curl -X POST http://localhost:5000/pad/trigger -H "Content-Type: application/json" -d "{\"pad_id\": \"hihat\"}" -s -w "\n"
