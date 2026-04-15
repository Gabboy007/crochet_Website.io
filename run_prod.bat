@echo off
setlocal

cd /d "%~dp0"

python serve_prod.py

if errorlevel 1 (
  echo.
  echo Production server exited with an error.
  pause
)
