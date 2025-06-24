#!/bin/bash

echo "🔥 Starting Stubble Burning Detection System..."

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo "⚠️  Port $1 is already in use. Killing existing process..."
        lsof -ti:$1 | xargs kill -9 2>/dev/null || true
        sleep 2
        return 0
    else
        return 0
    fi
}

# Function to start backend
start_backend() {
    echo "📡 Starting Backend API..."
    
    if [ ! -d "backend" ]; then
        echo "❌ Backend directory not found!"
        exit 1
    fi
    
    cd backend
    
    # Install dependencies if needed
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
        if [ $? -ne 0 ]; then
            echo "❌ Failed to create virtual environment"
            exit 1
        fi
    fi
    
    source venv/bin/activate
    if [ $? -ne 0 ]; then
        echo "❌ Failed to activate virtual environment"
        exit 1
    fi
    
    # Check if key dependencies are installed
    if ! python -c "import fastapi, uvicorn" 2>/dev/null; then
        echo "Installing Python dependencies..."
        pip install -r requirements.txt
        if [ $? -ne 0 ]; then
            echo "❌ Failed to install Python dependencies"
            exit 1
        fi
    else
        echo "✅ Python dependencies already installed"
    fi
    
    # Start the backend server
    echo "Starting backend server..."
    python run.py &
    BACKEND_PID=$!
    echo "✅ Backend started with PID: $BACKEND_PID"
    
    cd ..
}

# Function to start frontend  
start_frontend() {
    echo "🌐 Starting Frontend..."
    
    if [ ! -d "frontend" ]; then
        echo "❌ Frontend directory not found!"
        exit 1
    fi
    
    cd frontend
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ] || [ ! -f "node_modules/.package-lock.json" ]; then
        echo "Installing npm dependencies..."
        npm install --silent
        if [ $? -ne 0 ]; then
            echo "❌ Failed to install npm dependencies"
            exit 1
        fi
    else
        echo "✅ npm dependencies already installed"
    fi
    
    # Start the frontend server
    echo "Starting frontend server..."
    npm run dev &
    FRONTEND_PID=$!
    echo "✅ Frontend started with PID: $FRONTEND_PID"
    
    cd ..
}

# Check and clear ports if needed
echo "🔍 Checking ports..."
check_port 8000
check_port 3000

# Start services
start_backend
echo "⏳ Waiting for backend to initialize..."
sleep 5  # Give backend time to start

start_frontend
echo "⏳ Waiting for frontend to initialize..."
sleep 5  # Give frontend time to start

# Verify services are running
echo "🔍 Verifying services..."
if curl -s http://localhost:8000 > /dev/null 2>&1; then
    echo "✅ Backend is responding on port 8000"
else
    echo "⚠️  Backend may still be starting on port 8000"
fi

if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is responding on port 3000"
else
    echo "⚠️  Frontend may still be starting on port 3000"
fi

echo ""
echo "🚀 System started successfully!"
echo ""
echo "📊 Services:"
echo "   Backend API: http://localhost:8000"
echo "   API Docs:    http://localhost:8000/docs"
echo "   Frontend:    http://localhost:3000"
echo ""
echo "🔍 Fire Detection Features:"
echo "   • Real-time NASA FIRMS data (24hr/7day)"
echo "   • Historical database queries (custom dates)"
echo "   • Regional filtering (states/cities)"
echo "   • Multi-source data (MODIS/VIIRS)"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for user interrupt
trap 'echo ""; echo "🛑 Stopping services..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo "✅ All services stopped"; exit 0' INT

# Keep script running
while true; do
    sleep 1
done