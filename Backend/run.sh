#!/bin/bash

# Future Farmers Backend Startup Script

echo "🚀 Starting Future Farmers Backend..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if MongoDB is running
echo "🔍 Checking MongoDB connection..."
if ! nc -z localhost 27017 2>/dev/null; then
    echo "⚠️  Warning: MongoDB doesn't seem to be running on localhost:27017"
    echo "   Please start MongoDB with: docker run -d -p 27017:27017 --name mongodb mongo:latest"
    echo "   Or use your local MongoDB installation"
    echo ""
fi

# Start the application
echo "✅ Starting FastAPI server on http://localhost:8001..."
echo "📚 API Documentation: http://localhost:8001/docs"
echo ""
python -m app.main
