#!/bin/bash

start_django_server() {
    echo "Starting Django server..."
    cd backend
  
    # activate the virtual env
    source ../.venv/bin/activate

    # process any changes to Models
    python3 manage.py migrate

    # run the Django server in the background
    python3 manage.py runserver &

    DJANGO_PID=$!
    echo "Django server started with PID: $DJANGO_PID"

    # wait for Django server to be ready
    echo "Waiting for Django server to be up..."
    while ! curl -s http://localhost:8000/api > /dev/null; do
      sleep 1
    done
    echo "Django server is up and running!"
}

start_react_server() {
    echo "Starting React server..."
    cd ../frontend

    # install dependencies (if not installed already)
    npm install
    npm install react-router-dom
    npm install react-plotly.js plotly.js


    # run the React server
    npm start &

    REACT_PID=$!
    echo "React server started with PID: $REACT_PID"
}

# stop both servers gracefully
stop_servers() {
    echo "Stopping servers..."

    # check if the Django server is running and kill it
    if [ ! -z "$DJANGO_PID" ] && kill -0 $DJANGO_PID > /dev/null 2>&1; then
        kill $DJANGO_PID
        echo "Django server stopped"
    else
        echo "Django server is not running"
    fi

    # check if the React server is running and kill it
    if [ ! -z "$REACT_PID" ] && kill -0 $REACT_PID > /dev/null 2>&1; then
        kill $REACT_PID
        echo "React server stopped"
    else
        echo "React server is not running"
    fi
}

# Trap Ctrl+C (SIGINT) and call stop_servers
trap stop_servers SIGINT

start_servers() {
    # kill any running servers on port 3000 & 8000
    npx kill-port 3000  # react
    npx kill-port 8000  # django

    start_django_server

    # after Django server ready, start React server
    start_react_server

    # wait indefinitely for servers to continue running until CTRL+C
    wait $DJANGO_PID
    wait $REACT_PID
}

if [ "$1" == "stop" ]; then
    stop_servers
else
    start_servers
fi
