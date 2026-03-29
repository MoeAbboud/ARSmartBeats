@echo off
REM trigger_clap.bat - Toggle clap pad
curl -X POST http://localhost:5000/pad/trigger -H "Content-Type: application/json" -d "{\"pad_id\": \"clap\"}" -s -w "\n"
