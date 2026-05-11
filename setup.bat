@echo off
echo ============================================
echo  DharmaSetu – Environment Setup (Python 3.11)
echo ============================================

:: Step 1: Create virtual environment with Python 3.11
echo [1/4] Creating virtual environment...
python3.11 -m venv .venv
if errorlevel 1 (
    echo ERROR: Python 3.11 not found. Install from https://www.python.org/downloads/release/python-3119/
    pause
    exit /b 1
)

:: Step 2: Activate virtual environment
echo [2/4] Activating virtual environment...
call .venv\Scripts\activate

:: Step 3: Upgrade pip
echo [3/4] Upgrading pip...
python -m pip install --upgrade pip

:: Step 4: Install dependencies
echo [4/4] Installing dependencies...
pip install -r requirements.txt

echo.
echo ============================================
echo  Setup complete!
echo  To run the app:
echo    .venv\Scripts\activate
echo    streamlit run streamlit_app.py
echo ============================================
pause
