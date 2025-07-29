#!/bin/bash
# Backend build script for Render

echo "Starting backend build..."

# Install Python dependencies
cd backend
pip install --upgrade pip
pip install -r ../requirements.txt

echo "Backend build completed successfully!"
