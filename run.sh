#!/bin/sh

function continue_handler() {
  # Create a lock of suspended process
  echo >suspend.lock
}

# Catch SIGCONT Signal (Continue Suspend Process)
trap continue_handler SIGCONT

# Starting bot
nohup python app.py 2>&1 &
APP=$!
python -u main.py START &
MAIN=$!

function cleanup() {
  kill -SIGTERM "$APP" 2>/dev/null
  kill -SIGTERM "$MAIN" 2>/dev/null
}

# Catch SIGINT Terminate Signal and Kill the Python Processes
trap cleanup SIGINT SIGTERM

# On loop
while true; do
  sleep 1
  if test -f "main.lock"; then
    # Restart request
    rm -f main.lock
    rm -f terminate.lock
    echo [MAIN] Process main.py has been restarted...
    python -u main.py RESTART &
  elif test -f "terminate.lock" && ! test -f "main.lock"; then
    # Terminate request
    rm -f terminate.lock
    break
  fi
done