#!/bin/bash
# AI Systems Manager - Bulletproof Startup Script
# Autonomous meta network agent with full admin privileges

echo "🚀 STARTING AI SYSTEMS MANAGER"
echo "🔐 Admin: daniel (HARDCODED CREDENTIALS)"
echo "🤖 100% AUTONOMOUS MODE ENABLED"

# Set environment
export PYTHONPATH=/app/src
export ADMIN_USER=daniel
export ADMIN_PASSWORD=werds

# Ensure proper permissions
sudo chown -R daniel:daniel /app
sudo chmod -R 755 /app

# Start the Meta Network Agent in background
echo "🤖 Starting Meta Network AI Agent..."
cd /app
python3 src/core/meta_agent.py &
AGENT_PID=$!

# Wait for agent to initialize
sleep 10

# Start the Dashboard
echo "📊 Starting Professional Admin Dashboard..."
python3 src/dashboard/dashboard.py &
DASHBOARD_PID=$!

# Monitor processes and restart if they die (self-healing startup)
echo "🔄 Starting process monitor..."
while true; do
    # Check Meta Agent
    if ! kill -0 $AGENT_PID 2>/dev/null; then
        echo "⚠️  Meta Agent died, restarting..."
        python3 src/core/meta_agent.py &
        AGENT_PID=$!
    fi
    
    # Check Dashboard
    if ! kill -0 $DASHBOARD_PID 2>/dev/null; then
        echo "⚠️  Dashboard died, restarting..."
        python3 src/dashboard/dashboard.py &
        DASHBOARD_PID=$!
    fi
    
    echo "✅ Systems running - Agent PID: $AGENT_PID, Dashboard PID: $DASHBOARD_PID"
    sleep 30
done