#!/bin/bash

echo "Stopping application..."
bash app_stop.sh

echo "Starting application..."
if [ -f /.dockerenv ]; then
    echo "Running inside Docker container, using system python/uvicorn..."
elif [ -f "venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "No virtual environment found, using system python/uvicorn..."
fi

# Run uvicorn in background
nohup uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload --reload-dir app > server.log 2>&1 &

NEW_PID=$!
echo "Application started with PID: $NEW_PID"
echo "Logs are being written to server.log"
echo "Last 20 lines of server.log:"
tail -n 20 server.log
echo "To follow logs, run: tail -f server.log"
