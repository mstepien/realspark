#!/bin/bash

echo "Stopping application..."
bash app_stop.sh

echo "Starting application..."
source venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port 8080 > server.log 2>&1 &

NEW_PID=$!
echo "Application started with PID: $NEW_PID"
echo "Logs are being written to server.log"
echo "Tailing logs for 5 seconds..."
#timeout 5 
#tail -f server.log
