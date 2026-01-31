#!/bin/bash

echo "============================================"
echo "OPD Token System - Python Setup"
echo "============================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "Python found!"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created!"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo ""

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt
echo ""
echo "Dependencies installed!"
echo ""

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "IMPORTANT: Please edit .env file with your MongoDB URI"
    echo ""
fi

echo "============================================"
echo "Setup Complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your MongoDB URI"
echo "2. Run: python main.py"
echo "3. Visit: http://localhost:8000/docs"
echo ""
echo "To run simulation: python simulation.py"
echo ""
