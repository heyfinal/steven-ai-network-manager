#!/bin/bash
# AI Systems Manager - Bulletproof Startup Script
# Autonomous meta network agent with full admin privileges

echo "🚀 STARTING AI SYSTEMS MANAGER"
echo "🛡️  Secure mode with environment-based credentials"
echo "🤖 Autonomous operations enabled"

# Set environment
export PYTHONPATH=/app/src

cd /app

# Start Dashboard (which initializes SecureMetaNetworkAgent lazily)
echo "📊 Starting Admin Dashboard..."
exec python3 src/dashboard/dashboard.py
