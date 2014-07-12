#!/usr/bin/env bash

## The command you want to run, change this to whatever
## command you actually want.
COMMAND='sleep 10';

## Define the log file
LOGFILE=$HOME/.last_run;
PIDFILE=$HOME/.last_pid;

if [ -f $PIDFILE ]; then
    echo "running?"
   kill -0 `cat $PIDFILE` 2>/dev/null && exit 1
   echo "nope..."
fi

## If the log file doesn't exist, run your command
if [ ! -f $LOGFILE ]; then
    ## If the command succeeds, update the log file
    $COMMAND &
    echo $! > $PIDFILE
    fg 2>/dev/null
    touch $LOGFILE
else
    ## If the file does exist, check its age
    AGE=$(stat -f "%m" $LOGFILE);
    ## Get the current time
    DATE=$(date -v-1d -v14H -v0M -v0S +%s);
    ## If the file is more than 24h old, run the command again
    #if [[ $((DATE - AGE)) -gt 86400 ]]; then
    if [[ $DATE -gt $AGE ]]; then
    #  $COMMAND && touch $LOGFILE;
      $COMMAND &
      echo $! > $PIDFILE
      fg 2>/dev/null
      touch $LOGFILE
    else
        echo "not 24 hours old..."
    fi
fi
