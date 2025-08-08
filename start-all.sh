#!/bin/bash
echo "Starting all Open Policy services..."
echo "This will start backend, web interface, and mobile app"

# Start backend in background
./start-backend.sh &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 5

# Start web interface in background
./start-web.sh &
WEB_PID=$!

# Start mobile app in background
./start-mobile.sh &
MOBILE_PID=$!

echo "All services started!"
echo "Backend PID: $BACKEND_PID"
echo "Web PID: $WEB_PID"
echo "Mobile PID: $MOBILE_PID"
echo ""
echo "To stop all services, run: kill $BACKEND_PID $WEB_PID $MOBILE_PID"

# Wait for user to stop
wait
