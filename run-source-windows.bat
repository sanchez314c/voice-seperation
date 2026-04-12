@echo off
echo === Running Voice Separation from source (Windows) ===

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate

if exist "requirements.txt" (
    echo Checking Python dependencies...
    pip install -r requirements.txt -q
    echo Python dependencies OK
)

if not exist "node_modules" (
    echo Installing Node dependencies...
    call npm install
)

echo Launching Voice Separation...
call npm start
