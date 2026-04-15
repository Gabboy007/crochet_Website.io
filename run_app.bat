@echo off
setlocal

cd /d "%~dp0"

python run.py

if errorlevel 1 (
  echo.
  echo App exited with an error.
  pause
)
