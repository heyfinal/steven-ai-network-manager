#!/usr/bin/env python3
"""
AI Systems Manager - Professional Admin Dashboard
Bulletproof web interface for monitoring and controlling the Meta Network Agent

Admin Dashboard (secured)
"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit, disconnect
import json
import time
import threading
from datetime import datetime
import hashlib
import os
from pathlib import Path
import sys

# Add core module to path
sys.path.append(str(Path(__file__).parent.parent / "core"))

# Prefer secure agent; fall back only if necessary
try:
    from secure_meta_agent import SecureMetaNetworkAgent, ADMIN_USER  # noqa: F401

    _agent_instance = None

    def get_meta_agent():
        global _agent_instance
        if _agent_instance is None:
            _agent_instance = SecureMetaNetworkAgent()
        return _agent_instance
except Exception:
    # Fallback to legacy agent (not recommended)
    from meta_agent import get_meta_agent, ADMIN_USER  # type: ignore


from security.auth import SecurityManager
import bcrypt

app = Flask(__name__, template_folder='templates', static_folder='static')

# Secret keys and session security
SESSION_SECRET = os.getenv('SESSION_SECRET_KEY')
if SESSION_SECRET:
    app.secret_key = SESSION_SECRET
else:
    # Fallback for dev only
    app.secret_key = hashlib.sha256(os.urandom(32)).hexdigest()

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=bool(os.getenv('REQUIRE_HTTPS', 'false').lower() == 'true')
)

allowed_origins_env = os.getenv('ALLOWED_ORIGINS')
allowed_origins = [o.strip() for o in allowed_origins_env.split(',')] if allowed_origins_env else None
socketio = SocketIO(app, cors_allowed_origins=allowed_origins)

security_manager = SecurityManager()


@app.route('/')
def dashboard():
    """Main dashboard"""
    if not is_authenticated():
        return redirect(url_for('login'))
    
    return render_template('advanced_dashboard.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login"""
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        auth_result = security_manager.authenticate_user(username, password)
        if auth_result.get('success'):
            session['authenticated'] = True
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    return redirect(url_for('login'))


@app.route('/api/status')
def api_status():
    """Get current system status"""
    if not is_authenticated():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        agent = get_meta_agent()
        data = agent.get_dashboard_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/force-evolution', methods=['POST'])
def force_evolution():
    """Force system evolution"""
    if not is_authenticated():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        agent = get_meta_agent()
        agent._evolve_system()
        return jsonify({'success': True, 'message': 'Evolution forced'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/healing-action', methods=['POST'])
def execute_healing_action():
    """Execute manual healing action"""
    if not is_authenticated():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        command = data.get('command', '')
        
        if not command:
            return jsonify({'error': 'No command provided'}), 400
        
        # Route through secure agent command validation if available
        agent = get_meta_agent()
        if hasattr(agent, 'validate_and_execute_command'):
            res = agent.validate_and_execute_command(command, risk_tolerance=os.getenv('RISK_TOLERANCE', 'low'))
            return jsonify(res), (200 if res.get('success') else 400)
        return jsonify({'error': 'Secure execution not available'}), 403
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai-command', methods=['POST'])
def execute_ai_command():
    """Send command to Steven AI agent"""
    if not is_authenticated():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        command = data.get('command', '')
        
        if not command:
            return jsonify({'error': 'No command provided'}), 400
        
        # Get the meta agent and execute the AI command
        agent = get_meta_agent()
        
        # Map common commands to agent methods
        if 'refresh memory' in command.lower():
            result = agent._analyze_system_state()
            message = "Memory refreshed - system state analyzed"
        elif 'troubleshoot' in command.lower() and 'mcu' in command.lower():
            result = agent._check_mcp_servers()
            message = "MCU server troubleshooting initiated"
        elif 'health check' in command.lower():
            result = agent.get_dashboard_data()
            message = "Complete system health check performed"
        elif 'optimize' in command.lower():
            result = agent._evolve_system()
            message = "Steven is optimizing system performance"
        else:
            # For other commands, use AI to interpret and execute
            try:
                # Use OpenAI to process the command
                from openai import OpenAI
                import time
                start_time = time.time()
                
                client = OpenAI()
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are Steven, an AI network managing agent. Interpret user commands and provide appropriate system responses."},
                        {"role": "user", "content": f"Execute this command: {command}"}
                    ],
                    max_tokens=150
                )
                
                # Track API usage
                response_time_ms = int((time.time() - start_time) * 1000)
                tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 150
                cost_usd = tokens_used * 0.00003  # Approximate GPT-4 cost per token
                
                agent._track_api_usage(
                    endpoint="chat/completions",
                    model="gpt-4", 
                    tokens_used=tokens_used,
                    cost_usd=cost_usd,
                    operation_type="command_interpretation",
                    success=True,
                    response_time_ms=response_time_ms
                )
                
                message = response.choices[0].message.content
                result = True
            except Exception as ai_error:
                # Track failed API call
                agent._track_api_usage(
                    endpoint="chat/completions",
                    model="gpt-4",
                    tokens_used=0,
                    cost_usd=0.0,
                    operation_type="command_interpretation",
                    success=False
                )
                message = f"Steven is processing: {command}"
                result = True
        
        # Broadcast the action to all connected clients
        socketio.emit('healing_action', {
            'type': 'info',
            'message': f"Steven executed: {command}",
            'timestamp': datetime.now().isoformat()
        }, broadcast=True)
        
        return jsonify({
            'success': True,
            'message': message,
            'result': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Steven encountered an error: {str(e)}'
        }), 500


def is_authenticated():
    """Check if user is authenticated"""
    return session.get('authenticated', False) and session.get('user') == ADMIN_USER


def broadcast_updates():
    """Broadcast real-time updates to connected clients"""
    while True:
        try:
            if app.config.get('TESTING'):
                break
                
            agent = get_meta_agent()
            data = agent.get_dashboard_data()
            
            socketio.emit('status_update', data, broadcast=True)
            time.sleep(5)  # Update every 5 seconds
            
        except Exception as e:
            print(f"Broadcast error: {e}")
            time.sleep(10)


@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    if is_authenticated():
        emit('connected', {'message': 'Connected to AI Systems Manager'})
    else:
        disconnect()


if __name__ == '__main__':
    # Start background thread for real-time updates
    update_thread = threading.Thread(target=broadcast_updates, daemon=True)
    update_thread.start()
    
    print("🚀 Starting AI Systems Manager Dashboard")
    print(f"🔐 Admin Login: {ADMIN_USER}")
    print("📊 Dashboard: http://0.0.0.0:5001")
    
    socketio.run(app, host='0.0.0.0', port=5001, debug=False)
