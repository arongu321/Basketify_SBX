#!/bin/bash

# Define the Python script to run
PYTHON_SCRIPT="nba_future_games.py"

# Step 1: Process teams (this will be done in one run)
echo "Processing teams..."
python3 $PYTHON_SCRIPT --process teams

# Step 2: Process players in batches of 500
BATCH_SIZE=500
TOTAL_PLAYERS=4500
for ((start=0; start<TOTAL_PLAYERS; start+=BATCH_SIZE)); do
    end=$((start + BATCH_SIZE))
    if ((end > TOTAL_PLAYERS)); then
        end=$TOTAL_PLAYERS
    fi

    echo "Processing players $start to $end..."
    python3 $PYTHON_SCRIPT --process players --start $start --end $end
    sleep 1
done

# Step 3: Process future games
echo "Processing future games..."
python3 $PYTHON_SCRIPT --process future

echo "Finished processing all players and teams."
