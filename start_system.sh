#!/bin/bash

echo "🔥 Starting Stubble Burning Detection System..."

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "Port $1 is already in use"
        return 1
    else
        return 0
    fi
}

# Function to start backend
start_backend() {
    echo "📡 Starting Backend API..."
    cd backend
    
    # Install dependencies if needed
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install -r requirements.txt > /dev/null 2>&1
    
    # Start the backend server
    python run.py &
    BACKEND_PID=$!
    echo "Backend started with PID: $BACKEND_PID"
    
    cd ..
}

# Function to start frontend
start_frontend() {
    echo "🌐 Starting Frontend..."
    cd frontend
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo "Installing npm dependencies..."
        npm install > /dev/null 2>&1
    fi
    
    # Start the frontend server
    npm run dev &
    FRONTEND_PID=$!
    echo "Frontend started with PID: $FRONTEND_PID"
    
    cd ..
}

# Check if ports are available
if ! check_port 8000; then
    echo "❌ Backend port 8000 is busy. Please stop the existing service."
    exit 1
fi

if ! check_port 3000; then
    echo "❌ Frontend port 3000 is busy. Please stop the existing service."
    exit 1
fi

# Start services
start_backend
sleep 3  # Give backend time to start

start_frontend
sleep 3  # Give frontend time to start

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