@echo off
echo Starting ResQ-Grid Disaster System...
start cmd /k "venv\Scripts\activate && uvicorn server:app --reload --host 0.0.0.0 --port 8000"
timeout /t 3
start cmd /k "venv\Scripts\activate && streamlit run dashboard.py"