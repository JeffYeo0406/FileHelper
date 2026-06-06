@echo off
echo ========================================
echo   Simple File Helper — Starting...
echo ========================================
echo.

cd /d "%~dp0backend"

:: Check if venv exists
if not exist "venv\" (
    echo [!] Virtual environment not found. Running setup...
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
    echo [!] Creating database tables...
    python seed.py
) else (
    call venv\Scripts\activate
)

echo.
echo Starting server at http://localhost:8000
echo Open http://localhost:8000/app/index.html in your browser
echo.
echo Default login: admin / changeme123
echo Press Ctrl+C to stop
echo.

uvicorn main:app --host 0.0.0.0 --port 8000

pause
