@echo off
REM Future Farmers Backend Startup Script for Windows

echo 🚀 Starting Future Farmers Backend...
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Check if .env exists
if not exist ".env" (
    echo ⚠️  .env file not found. Copying from .env.example...
    copy .env.example .env
    echo ⚙️  Please edit .env with your MongoDB connection details
)

REM Start the server
echo.
echo ✅ Starting FastAPI server on port 8001...
echo 📚 API Documentation: http://localhost:8001/docs
echo.
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

