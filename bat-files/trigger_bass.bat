@echo off
REM trigger_bass.bat - Toggle bass pad
curl -X POST http://localhost:5000/pad/trigger -H "Content-Type: application/json" -d "{\"pad_id\": \"bass\"}" -s -w "\n"
