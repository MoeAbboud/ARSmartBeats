@echo off
setlocal enabledelayedexpansion

REM reprompt_pad.bat - Regenerate a pad using number (1-8)
REM Usage: reprompt_pad.bat <number> <prompt>
REM Example: reprompt_pad.bat 8 Piano C major chord seamless loop
REM Example: reprompt_pad.bat 8 "Piano C major chord, seamless loop"

set PAD_NUMBER=%1

if "%PAD_NUMBER%"=="" (
    echo Error: No pad number provided
    echo Usage: reprompt_pad.bat [1-8] [prompt text]
    exit /b 1
)

REM Map number to pad_id
if "%PAD_NUMBER%"=="1" set PAD_ID=kick
if "%PAD_NUMBER%"=="2" set PAD_ID=snare
if "%PAD_NUMBER%"=="3" set PAD_ID=hihat
if "%PAD_NUMBER%"=="4" set PAD_ID=bass
if "%PAD_NUMBER%"=="5" set PAD_ID=atmosphere
if "%PAD_NUMBER%"=="6" set PAD_ID=synth
if "%PAD_NUMBER%"=="7" set PAD_ID=clap
if "%PAD_NUMBER%"=="8" set PAD_ID=arp

if "%PAD_ID%"=="" (
    echo Error: Invalid pad number '%PAD_NUMBER%'. Valid: 1-8
    exit /b 1
)

REM Collect all remaining arguments as the prompt
shift
set PROMPT_TEXT=
:loop
if "%~1"=="" goto endloop
if defined PROMPT_TEXT (
    set PROMPT_TEXT=!PROMPT_TEXT! %~1
) else (
    set PROMPT_TEXT=%~1
)
shift
goto loop
:endloop

if "!PROMPT_TEXT!"=="" (
    echo Error: No prompt provided
    echo Usage: reprompt_pad.bat [1-8] [prompt text]
    exit /b 1
)

echo Regenerating pad %PAD_NUMBER% (%PAD_ID%) with prompt: !PROMPT_TEXT!

curl -X POST http://localhost:5000/pad/reprompt -H "Content-Type: application/json" -d "{\"pad_id\": \"%PAD_ID%\", \"prompt\": \"!PROMPT_TEXT!\"}" -s

endlocal