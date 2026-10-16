@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Virtual environment not found.
  echo Run these commands first:
  echo python -m venv .venv
  echo .venv\Scripts\activate
  echo python -m pip install -r requirements.txt
  pause
  exit /b 1
)
start "VoicePath Server" cmd /k ".venv\Scripts\python.exe app.py"
timeout /t 2 /nobreak >nul
start "" http://127.0.0.1:8001
