#!/bin/bash

# Find the PID of the running uvicorn process
PID=$(ps aux | grep "uvicorn main:app" | grep -v grep | awk '{print $2}')

if [ -n "$PID" ]; then
    echo "Stopping existing application (PID: $PID)..."
    kill $PID
    sleep 2 # Wait for it to shut down
else
    echo "No running application found."
fi

echo "Starting application..."
source venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 8080 > server.log 2>&1 &

NEW_PID=$!
echo "Application started with PID: $NEW_PID"
echo "Logs are being written to server.log"
echo "Tailing logs for 5 seconds..."
#timeout 5 tail -f server.log
