#!/bin/bash
# Frontend build script for Render

echo "Starting frontend build..."

# Install Node dependencies and build
cd frontend
npm ci --only=production
npm run build

echo "Frontend build completed successfully!"
echo "Static files ready in frontend/dist/"
