#!/bin/sh
# Starting bot
nohup python app.py 2>&1 &
python -u main.py START &

# On loop
while true; do
    sleep 1
    if test -f "main.lock"; then
        # Restart request
        rm -f main.lock
        rm -f terminate.lock
        echo [MAIN] Process main.py has been restarted...
        python -u main.py RESTART &
    elif test -f "terminate.lock"; then
        # Termiate request
        rm -f terminate.lock
        break
    fi
done