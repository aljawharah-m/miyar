@echo off
python scripts\judge_verify.py
if errorlevel 1 exit /b 1
pause
