#!/bin/bash

# Call args 
# + nohup mode (run in the background):
#
# Default campaign campaign_linux_kpi.cfg:
#   ./campaign_linux_kpi.sh
#   ./campaign_linux_kpi.sh --nohup

# Default campaign campaign_linux_kpi.cfg, override repeats:
#   ./campaign_linux_kpi.sh 9999
#   ./campaign_linux_kpi.sh 9999 --nohup
#
# Custom campaign, override repeats:
#   ./campaign_linux_kpi.sh campaign_linux_kpi.cfg 9999
#   ./campaign_linux_kpi.sh campaign_linux_kpi.cfg 9999 --nohup
#
# Randomize campaign, infinite:
#   ./campaign_linux_kpi.sh --random
#   ./campaign_linux_kpi.sh --random --nohup
#
# Run all tests sequentially in a loop, infinite:
#   ./campaign_linux_kpi.sh --loop
#   ./campaign_linux_kpi.sh --loop --nohup
#
#
#
# To cancel execution in nohup mode:
# ./campaign_linux_kpi.sh --kill


function line () {
    printf '%58s\n' | tr ' ' -
}

REPEAT=1
RANDOMIZE=0
LOOP=0
FILE=0

NOHUP=0

for arg do
    shift
    [ "$arg" = "--nohup" ] && NOHUP=1 && continue
    set -- "$@" "$arg"
done

if [[ "$1" == *"--kill"* ]]; then
    scriptname=`basename "$0"`
    echo "INFO: Kill $scriptname"
    ps -ef | grep $scriptname | grep -v grep | grep -v kill 
    retval=$?
    if [ $retval -ne 0 ]; then
        echo "INFO: No $scriptname process is currently running."
    else
        ps -ef | grep $scriptname | grep -v grep | grep -v kill | awk '{print $2}' | xargs kill -9 
    fi
    exit 0
fi


if [[ "$NOHUP" -eq "1" ]]; then
    echo "INFO: Nohup mode             :  $NOHUP"    
    echo "Call: $0 $@ &"
    nohup $0 "$@" &
    exit 0
fi


TARGET=$(basename "$0")
DIR=$(dirname "$0")
DIR=$(realpath $DIR)

if [ -n "$1" ]; then
    TARGET=$1 
else
    TARGET=$(echo "$TARGET" | sed "s/sh/cfg/")
fi   

line

if [[ "$1" == *"--loop"* ]]; then
    LOOP=1
    TARGET=$1
elif [[ "$1" == *"--random"* ]]; then
    RANDOMIZE=1
    TARGET=$1
elif [[ -f "$TARGET" ]]; then
    FILE=1
else
    echo "ERROR: Target file/mode $TARGET does not exist!"
    exit 3
fi

if [ -n "$2" ]; then
    REPEAT=$2
fi

echo "INFO: Using target           :  $(echo "$TARGET" | sed -e "s/^--//")"
echo "INFO: Repeats                :  $REPEAT"

line

if [[ "$FILE" -eq 1 ]]; then
    echo "INFO: Mode: campaign file"
    TARGET=$(realpath $TARGET)
    for ((i=1;i<=REPEAT;i++)); do
        unicorn $TARGET
        sleep 1
    done       
elif [[ "$LOOP" -eq 1 ]]; then
    echo "INFO: Mode: loop"
    while true
    do
        for filename in $DIR/*.py; do
            TEST_FILE="$filename" || continue
            unicorn $TEST_FILE
            sleep 1
        done
    done  
elif [[ "$RANDOMIZE" -eq 1 ]]; then
    echo "INFO: Mode: random"
    DIR=$(realpath $DIR)
    while true
    do
        TEST_FILE=$(ls $DIR/*.py | shuf -n 1)
        unicorn $TEST_FILE
        sleep 1
    done    
else
    echo "ERROR: Unmatched mode!"
    exit 3
fi

exit 0