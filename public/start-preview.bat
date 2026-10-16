@echo off
rem CraftFee - local preview
rem Double-click this file. A browser tab opens at http://127.0.0.1:8787/
rem Stop the preview by closing this window (or pressing Ctrl+C).

cd /d "%~dp0"
set PORT=8787

echo.
echo   ============================================
echo    Local preview :  http://127.0.0.1:%PORT%/
echo    Stop          :  close this window
echo   ============================================
echo.

start "" "http://127.0.0.1:%PORT%/"

where python >nul 2>nul
if %errorlevel%==0 (
  python -m http.server %PORT% --bind 127.0.0.1
) else (
  py -m http.server %PORT% --bind 127.0.0.1
)

pause
