#!/bin/bash

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3.9 -m venv venv
fi

source venv/bin/activate

if [ "$VIRTUAL_ENV" != "" ]; then
    echo "Virtual environment activated."
    pip3 install -r requirements.txt
    python3 main.py
else
    echo "Failed to activate virtual environment."
    exit 1
fi
