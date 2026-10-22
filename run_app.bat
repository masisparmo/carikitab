@echo off
cd /d "%~dp0"
python -m app.main
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Aplikasi keluar dengan error code %ERRORLEVEL%.
    pause
)
