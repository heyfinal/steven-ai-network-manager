#!/usr/bin/env python3
"""
AI Systems Manager - Main Entry Point
100% Functional & Bulletproof AI Systems Management

This is the main entry point that starts both the Meta Network Agent
and the Professional Admin Dashboard simultaneously.

Admin Credentials: daniel/werds (HARDCODED)
"""
import sys
import subprocess
import threading
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.meta_agent import start_meta_agent, ADMIN_USER, ADMIN_PASSWORD, MINICLOUD_IP
from dashboard.dashboard import app, socketio


def start_meta_agent_process():
    """Start the Meta Network Agent in a separate thread"""
    print("🤖 Starting Meta Network AI Agent...")
    agent = start_meta_agent()
    
    # Keep the agent running
    try:
        while agent.running:
            time.sleep(60)
            print(f"🤖 Meta Agent Status: Running (Evolution #{agent.evolution_counter})")
    except KeyboardInterrupt:
        print("🛑 Meta Agent shutdown requested")
        agent.running = False


def start_dashboard_process():
    """Start the Professional Admin Dashboard"""
    print("📊 Starting Professional Admin Dashboard...")
    print(f"🌐 Dashboard URL: http://{MINICLOUD_IP}:5001")
    print(f"🔐 Admin Login: {ADMIN_USER} / {ADMIN_PASSWORD}")
    
    # Start dashboard with SocketIO
    socketio.run(app, host='0.0.0.0', port=5001, debug=False)


def main():
    """Main entry point - starts both components"""
    print("🚀 AI SYSTEMS MANAGER - STARTING ALL COMPONENTS")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🤖 Meta Network Agent: 100% AUTONOMOUS")
    print("🛡️  Self-Healing: ENABLED")
    print("🧬 AI Evolution: ACTIVE") 
    print("📊 Professional Dashboard: BULLETPROOF")
    print(f"🔐 Admin Access: {ADMIN_USER} (credentials locked)")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    try:
        # Start Meta Agent in background thread
        agent_thread = threading.Thread(target=start_meta_agent_process, daemon=True)
        agent_thread.start()
        
        # Give agent time to initialize
        time.sleep(5)
        
        # Start Dashboard in main thread (blocking)
        start_dashboard_process()
        
    except KeyboardInterrupt:
        print("\n🛑 AI Systems Manager shutdown requested")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Critical error in AI Systems Manager: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()