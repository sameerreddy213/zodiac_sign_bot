@echo off
echo Stopping existing python processes...
taskkill /F /IM python.exe
timeout /t 2 /nobreak
taskkill /F /IM python.exe
timeout /t 2 /nobreak
echo Starting bot...
python main.py
