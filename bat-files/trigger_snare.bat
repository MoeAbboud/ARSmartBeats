@echo off
REM trigger_snare.bat - Toggle snare pad
curl -X POST http://localhost:5000/pad/trigger -H "Content-Type: application/json" -d "{\"pad_id\": \"snare\"}" -s -w "\n"
