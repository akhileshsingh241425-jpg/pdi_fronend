#!/bin/bash

# IPQC Automation System - Quick Setup Script
# This script sets up both backend and frontend

echo "🚀 IPQC Automation System - Quick Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 14 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo "✅ Node.js found: $(node --version)"
echo ""

# Setup Backend
echo "📦 Setting up Backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Backend setup complete!"
echo ""

cd ..

# Setup Frontend
echo "📦 Setting up Frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install
else
    echo "Dependencies already installed, skipping..."
fi

echo "✅ Frontend setup complete!"
echo ""

cd ..

# Create .env file for frontend if it doesn't exist
if [ ! -f "frontend/.env" ]; then
    echo "Creating .env file for frontend..."
    echo "REACT_APP_API_URL=http://localhost:5000/api" > frontend/.env
    echo "✅ .env file created"
fi

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "To start the application:"
echo ""
echo "1. Start Backend (Terminal 1):"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python run.py"
echo ""
echo "2. Start Frontend (Terminal 2):"
echo "   cd frontend"
echo "   npm start"
echo ""
echo "Then open http://localhost:3000 in your browser"
echo ""
