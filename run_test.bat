@echo off
echo Running Registration Test...
call venv\Scripts\activate.bat
timeout /t 2 /nobreak >nul
python test_complete_registration.py
pause
