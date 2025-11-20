@echo off
echo Starting ICCT26 Backend Server...
call venv\Scripts\activate.bat
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
