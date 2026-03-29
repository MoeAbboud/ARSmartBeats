@echo off
REM trigger_synth.bat - Toggle synth pad
curl -X POST http://localhost:5000/pad/trigger -H "Content-Type: application/json" -d "{\"pad_id\": \"synth\"}" -s -w "\n"
