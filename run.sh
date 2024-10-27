#!/bin/sh
totalErrors=0

function pushService() {
  # Logic of Push Service
  logFile=$1
  errorLog=$(cat logs/${logFile} | nc termbin.com 9999 | tr -d '\0')
  lastLine=$(cat logs/${logFile} | tail -1)
  curl -s -H "Priority: 4" -H "Click: ${errorLog}" -d "${lastLine}" ntfy.sh/${NTFY_TOPIC} >/dev/null
}

function continue_handler() {
  # Create a lock of suspended process
  echo >suspend.lock
}

function cleanup() {
  if [ -n "$APP" ]; then
    kill "$APP"
  fi
  if [ -n "$MAIN" ]; then
    kill "$MAIN"
  fi
}

function logging() {
  if [ -n "$LOG_DATE" ]; then
    logFile="main_${LOG_DATE}.log"
    errors=$(grep -ic "error" "logs/${logFile}")
    # When error found in logFile
    if [ $errors -gt $totalErrors ]; then
      totalErrors=$errors
      pushService $logFile
      echo "Something went wrong: Check ${PWD}/logs/${logFile} for details"
    fi
  fi
}

# Catch SIGCONT Signal (Continue Suspend Process)
trap continue_handler SIGCONT

# Creating logs directory (If not exist)
if test ! -d "logs/"; then
  mkdir "logs/"
fi

# Starting and logging bot
LOG_DATE=$(date '+%Y-%m-%d_%H-%M-%S')
nohup python app.py > >(tee -a logs/main_${LOG_DATE}.log) 2>&1 </dev/null &
APP=$!
nohup python -u main.py START > >(tee -a logs/main_${LOG_DATE}.log) 2>&1 </dev/null &
MAIN=$!

# Catch SIGINT Terminate Signal and Kill the Python Processes
trap cleanup SIGINT SIGTERM

# On loop
while true; do
  sleep 1
  # If remote logging is enabled
  if [ -n "$NTFY_TOPIC" ]; then
    logging
  fi

  if test -f "main.lock"; then
    # Restart request
    rm -f main.lock
    rm -f terminate.lock
    LOG_DATE=$(date '+%Y-%m-%d_%H-%M-%S')
    echo "[MAIN] Process main.py has been restarted..." | tee -a logs/main_${LOG_DATE}.log
    nohup python -u main.py RESTART > >(tee -a logs/main_${LOG_DATE}.log) 2>&1 </dev/null &
    MAIN=$!
  elif test -f "terminate.lock" && ! test -f "main.lock"; then
    # Terminate request
    rm -f terminate.lock
    break
  else
    # Checks If main child process is running (if not then terminate the loop)
    if [ $(ps $MAIN | wc -l) != 2 ]; then
      break
    fi
  fi
done
