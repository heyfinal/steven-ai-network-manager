#!/usr/bin/env python3
"""
AI Systems Manager - Secure Authentication & Authorization
Enterprise-grade security for autonomous infrastructure management
"""
import bcrypt
import jwt
import os
import time
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from functools import wraps
from flask import request, jsonify, session
import logging
from pathlib import Path


class SecurityManager:
    """Enterprise-grade security manager with proper authentication and authorization"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        
        # Load security configuration from environment
        self.admin_username = os.getenv('ADMIN_USERNAME', 'daniel')
        self.admin_password_hash = os.getenv('ADMIN_PASSWORD_HASH', self._generate_default_hash())
        self.jwt_secret = os.getenv('JWT_SECRET_KEY', secrets.token_urlsafe(32))
        self.session_secret = os.getenv('SESSION_SECRET_KEY', secrets.token_urlsafe(32))
        
        # Rate limiting configuration
        self.max_requests_per_minute = int(os.getenv('MAX_REQUESTS_PER_MINUTE', '60'))
        self.max_healing_actions_per_hour = int(os.getenv('MAX_HEALING_ACTIONS_PER_HOUR', '10'))
        
        # Request tracking for rate limiting
        self.request_history = {}
        self.healing_action_history = {}
        
        # Allowed commands whitelist (security critical)
        self.allowed_commands = {
            'system_status': ['systemctl status', 'ps aux', 'df -h', 'free -m', 'uptime'],
            'docker_management': ['docker ps', 'docker stats', 'docker restart', 'docker logs'],
            'process_management': ['pkill', 'killall', 'systemctl restart'],
            'system_maintenance': ['sync', 'apt update', 'apt upgrade', 'docker system prune']
        }
        
        self.logger.info("🔐 Security Manager initialized with enterprise-grade protection")
    
    def _setup_logger(self) -> logging.Logger:
        """Setup secure logging"""
        logger = logging.getLogger('SecurityManager')
        logger.setLevel(logging.INFO)
        
        # Secure log handler
        logs_dir = Path.cwd() / 'logs'
        logs_dir.mkdir(parents=True, exist_ok=True)
        log_path = logs_dir / 'security.log'
        handler = logging.FileHandler(log_path)
        formatter = logging.Formatter(
            '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _generate_default_hash(self) -> str:
        """Generate secure default password hash for 'werds'"""
        # Default password: 'werds' - but properly hashed
        return bcrypt.hashpw('werds'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user with secure password hashing
        
        Args:
            username: Username to authenticate
            password: Plain text password
            
        Returns:
            Authentication result with token if successful
        """
        try:
            # Security audit log
            client_ip = request.remote_addr if request else 'unknown'
            self.logger.info(f"Authentication attempt: {username} from {client_ip}")
            
            # Check username
            if username != self.admin_username:
                self.logger.warning(f"Invalid username attempt: {username} from {client_ip}")
                time.sleep(2)  # Prevent timing attacks
                return {'success': False, 'error': 'Invalid credentials'}
            
            # Check password using bcrypt
            if not bcrypt.checkpw(password.encode('utf-8'), self.admin_password_hash.encode('utf-8')):
                self.logger.warning(f"Invalid password attempt for {username} from {client_ip}")
                time.sleep(2)  # Prevent timing attacks
                return {'success': False, 'error': 'Invalid credentials'}
            
            # Generate secure JWT token
            token = self._generate_jwt_token(username)
            
            self.logger.info(f"Successful authentication: {username} from {client_ip}")
            
            return {
                'success': True,
                'token': token,
                'user': username,
                'expires_at': (datetime.utcnow() + timedelta(hours=8)).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return {'success': False, 'error': 'Authentication failed'}
    
    def _generate_jwt_token(self, username: str) -> str:
        """Generate secure JWT token"""
        payload = {
            'user': username,
            'exp': datetime.utcnow() + timedelta(hours=8),
            'iat': datetime.utcnow(),
            'iss': 'ai-systems-manager',
            'aud': 'dashboard'
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return payload if valid"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            self.logger.warning("Expired JWT token used")
            return None
        except jwt.InvalidTokenError:
            self.logger.warning("Invalid JWT token used")
            return None
    
    def require_auth(self, f):
        """Decorator to require authentication for routes"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check for JWT token
            auth_header = request.headers.get('Authorization')
            if auth_header:
                try:
                    token = auth_header.split(' ')[1]  # Bearer <token>
                    payload = self.verify_jwt_token(token)
                    if payload:
                        request.current_user = payload['user']
                        return f(*args, **kwargs)
                except (IndexError, KeyError):
                    pass
            
            # Check session authentication
            if session.get('authenticated') and session.get('user') == self.admin_username:
                request.current_user = session.get('user')
                return f(*args, **kwargs)
            
            return jsonify({'error': 'Authentication required'}), 401
        
        return decorated_function
    
    def rate_limit(self, limit_type: str = 'general'):
        """Rate limiting decorator"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                client_ip = request.remote_addr
                current_time = time.time()
                
                # Clean old entries
                self._cleanup_rate_limit_history(current_time)
                
                # Check rate limit
                if not self._check_rate_limit(client_ip, limit_type, current_time):
                    self.logger.warning(f"Rate limit exceeded: {client_ip} for {limit_type}")
                    return jsonify({'error': 'Rate limit exceeded'}), 429
                
                # Record request
                self._record_request(client_ip, limit_type, current_time)
                
                return f(*args, **kwargs)
            
            return decorated_function
        return decorator
    
    def _check_rate_limit(self, client_ip: str, limit_type: str, current_time: float) -> bool:
        """Check if request is within rate limits"""
        if limit_type == 'healing_action':
            # Check healing action rate limit (per hour)
            history = self.healing_action_history.get(client_ip, [])
            hour_ago = current_time - 3600
            recent_actions = [t for t in history if t > hour_ago]
            return len(recent_actions) < self.max_healing_actions_per_hour
        else:
            # Check general rate limit (per minute)
            history = self.request_history.get(client_ip, [])
            minute_ago = current_time - 60
            recent_requests = [t for t in history if t > minute_ago]
            return len(recent_requests) < self.max_requests_per_minute
    
    def _record_request(self, client_ip: str, limit_type: str, current_time: float):
        """Record request for rate limiting"""
        if limit_type == 'healing_action':
            if client_ip not in self.healing_action_history:
                self.healing_action_history[client_ip] = []
            self.healing_action_history[client_ip].append(current_time)
        else:
            if client_ip not in self.request_history:
                self.request_history[client_ip] = []
            self.request_history[client_ip].append(current_time)
    
    def _cleanup_rate_limit_history(self, current_time: float):
        """Clean up old rate limiting entries"""
        hour_ago = current_time - 3600
        minute_ago = current_time - 60
        
        # Clean general request history
        for ip in list(self.request_history.keys()):
            self.request_history[ip] = [t for t in self.request_history[ip] if t > minute_ago]
            if not self.request_history[ip]:
                del self.request_history[ip]
        
        # Clean healing action history
        for ip in list(self.healing_action_history.keys()):
            self.healing_action_history[ip] = [t for t in self.healing_action_history[ip] if t > hour_ago]
            if not self.healing_action_history[ip]:
                del self.healing_action_history[ip]
    
    def validate_command(self, command: str) -> Dict[str, Any]:
        """
        Validate command against whitelist for security
        
        Args:
            command: Command to validate
            
        Returns:
            Validation result with sanitized command if approved
        """
        if not command or not command.strip():
            return {'valid': False, 'error': 'Empty command'}
        
        command = command.strip()
        
        # Check against whitelist
        for category, allowed_cmds in self.allowed_commands.items():
            for allowed_cmd in allowed_cmds:
                if command.startswith(allowed_cmd):
                    # Additional validation for specific commands
                    if self._validate_specific_command(command, category):
                        self.logger.info(f"Command approved: {command} (category: {category})")
                        return {
                            'valid': True,
                            'command': command,
                            'category': category,
                            'risk_level': self._assess_risk_level(command)
                        }
        
        self.logger.warning(f"Command rejected: {command}")
        return {'valid': False, 'error': 'Command not allowed'}
    
    def _validate_specific_command(self, command: str, category: str) -> bool:
        """Additional validation for specific command categories"""
        if category == 'docker_management':
            # Ensure docker commands are safe
            dangerous_docker = ['rm -f', 'rmi -f', 'system prune -a', 'network rm', 'volume rm']
            return not any(danger in command for danger in dangerous_docker)
        
        elif category == 'process_management':
            # Ensure we're not killing critical system processes
            critical_processes = ['systemd', 'kernel', 'init', 'ssh', 'networking']
            return not any(critical in command for critical in critical_processes)
        
        elif category == 'system_maintenance':
            # Ensure maintenance commands are safe
            dangerous_maintenance = ['rm -rf', 'dd ', 'mkfs', 'fdisk', 'parted']
            return not any(danger in command for danger in dangerous_maintenance)
        
        return True
    
    def _assess_risk_level(self, command: str) -> str:
        """Assess risk level of validated command"""
        high_risk_indicators = ['restart', 'stop', 'kill', 'rm', 'prune']
        medium_risk_indicators = ['start', 'create', 'update', 'upgrade']
        
        if any(indicator in command.lower() for indicator in high_risk_indicators):
            return 'high'
        elif any(indicator in command.lower() for indicator in medium_risk_indicators):
            return 'medium'
        else:
            return 'low'
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security events for audit trail"""
        client_ip = request.remote_addr if request else 'system'
        user = getattr(request, 'current_user', 'anonymous')
        
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'user': user,
            'client_ip': client_ip,
            'details': details
        }
        
        self.logger.info(f"SECURITY EVENT: {log_entry}")
    
    def generate_secure_session_id(self) -> str:
        """Generate cryptographically secure session ID"""
        return secrets.token_urlsafe(32)
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


# Global security manager instance
security_manager = SecurityManager()
