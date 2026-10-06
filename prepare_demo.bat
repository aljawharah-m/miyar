@echo off
cd /d %~dp0
set PIP_DEFAULT_TIMEOUT=300
set HF_HUB_DOWNLOAD_TIMEOUT=300
set HF_HUB_ETAG_TIMEOUT=30
echo [1/3] Installing MIYAR requirements with extended timeout...
python -m pip install --retries 10 --default-timeout 300 -r requirements.txt
if errorlevel 1 goto :fail
echo.
echo [2/3] Preparing semantic analysis and checking trusted-source connectivity...
python scripts\preflight.py
if errorlevel 1 goto :fail
echo.
echo [3/3] Running the complete deterministic release verification...
python scripts\release_check.py
if errorlevel 1 goto :fail
echo.
echo MIYAR is ready. Next time run run_miyar.bat
echo No API key is required for the public release.
pause
exit /b 0
:fail
echo.
echo Setup did not finish. Re-run this file; completed downloads are cached.
pause
exit /b 1
