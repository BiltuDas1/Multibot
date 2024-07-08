#!/bin/sh
# Starting bot
nohup python app.py 2>&1 &
APP=$!
python -u main.py START &
MAIN=$!

function cleanup() {
  kill -SIGINT "$APP" 2>/dev/null
  kill -SIGINT "$MAIN" 2>/dev/null
}

# Catch SIGINT Terminate Signal and Kill the Python Processes
trap cleanup SIGINT

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