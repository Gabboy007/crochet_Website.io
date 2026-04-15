@echo off
setlocal

cd /d "%~dp0"

if not defined PORT set "PORT=8080"
set "HOST=0.0.0.0"
set "SESSION_COOKIE_SECURE=0"

set "LOCAL_IP="
for /f "tokens=2 delims=:" %%I in ('ipconfig ^| findstr /R /C:"IPv4"') do (
  if not defined LOCAL_IP set "LOCAL_IP=%%I"
)
if defined LOCAL_IP set "LOCAL_IP=%LOCAL_IP: =%"

echo.
echo Minn Miru Handcrafted production-style local server
echo Computer: http://127.0.0.1:%PORT%
if defined LOCAL_IP echo Phone:    http://%LOCAL_IP%:%PORT%
echo.
echo Phone must be connected to the same Wi-Fi as this computer.
echo.

python serve_prod.py

if errorlevel 1 (
  echo.
  echo Production server exited with an error.
  pause
)
