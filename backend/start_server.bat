@echo off
cd /d c:\pulso\PULSO\backend
echo Checking dependencies... > c:\pulso\PULSO\backend\startup_log.txt
venv\Scripts\pip freeze >> c:\pulso\PULSO\backend\startup_log.txt 2>&1
echo. >> c:\pulso\PULSO\backend\startup_log.txt
echo Starting server... >> c:\pulso\PULSO\backend\startup_log.txt
venv\Scripts\python -u -m uvicorn app.main:app --host 0.0.0.0 --port 8000 >> c:\pulso\PULSO\backend\startup_log.txt 2>&1
