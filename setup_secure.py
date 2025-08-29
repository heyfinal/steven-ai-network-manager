#!/usr/bin/env python3
"""
AI Systems Manager - Secure Setup Script
Generates secure configuration for bulletproof deployment
"""
import os
import secrets
import bcrypt
import sys
from pathlib import Path
from dotenv import load_dotenv


def generate_secure_config():
    """Generate secure configuration file"""
    print("🔐 AI Systems Manager - Secure Configuration Setup")
    print("=" * 60)
    
    # Check if .env already exists
    env_path = Path(".env")
    if env_path.exists():
        response = input("⚠️  .env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
    
    print("\n📝 Setting up secure configuration...")
    
    # Get OpenAI API key securely
    openai_key = get_secure_input("Enter your OpenAI API key", required=True, secret=True)
    
    # Generate secure admin password hash
    admin_password = input("Enter admin password (default: werds): ").strip()
    if not admin_password:
        admin_password = "werds"
    
    # Hash the password securely
    password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Generate secure secrets
    session_secret = secrets.token_urlsafe(32)
    jwt_secret = secrets.token_urlsafe(32)
    db_encryption_key = secrets.token_urlsafe(32)
    
    # Network configuration
    minicloud_ip = input("Enter minicloud IP (default: 192.168.2.2): ").strip()
    if not minicloud_ip:
        minicloud_ip = "192.168.2.2"
    
    dashboard_port = input("Enter dashboard port (default: 5001): ").strip()
    if not dashboard_port:
        dashboard_port = "5001"
    
    # Create secure .env file
    env_content = f"""# AI Systems Manager - Secure Configuration
# Generated on {os.path.basename(__file__)} - DO NOT COMMIT TO VERSION CONTROL

# OpenAI API Configuration
OPENAI_API_KEY={openai_key}

# Admin Credentials (Secure)
ADMIN_USERNAME=daniel
ADMIN_PASSWORD_HASH={password_hash}

# Network Configuration
MINICLOUD_IP={minicloud_ip}
DASHBOARD_PORT={dashboard_port}
API_PORT=8888

# Security Configuration
SESSION_SECRET_KEY={session_secret}
JWT_SECRET_KEY={jwt_secret}

# Rate Limiting
MAX_REQUESTS_PER_MINUTE=60
MAX_HEALING_ACTIONS_PER_HOUR=10

# Database Configuration
DATABASE_PATH=/app/data/meta_agent.db
DATABASE_ENCRYPTION_KEY={db_encryption_key}

# Monitoring Configuration
LOG_LEVEL=INFO
MAX_LOG_SIZE_MB=100
LOG_RETENTION_DAYS=30

# Security Settings
REQUIRE_HTTPS=false
SSL_CERT_PATH=/etc/ssl/certs/ai-systems-manager.crt
SSL_KEY_PATH=/etc/ssl/private/ai-systems-manager.key
"""
    
    # Write .env file with secure permissions
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    # Set secure file permissions (readable only by owner)
    os.chmod(env_path, 0o600)
    
    print("✅ Secure configuration generated successfully!")
    print(f"📄 Configuration saved to: {env_path.absolute()}")
    print("🔒 File permissions set to 600 (owner read/write only)")
    
    print("\n🚨 SECURITY NOTES:")
    print("- Never commit .env file to version control")
    print("- Keep your OpenAI API key secure")
    print("- Admin password is properly hashed with bcrypt")
    print("- All secrets are cryptographically secure")
    
    print(f"\n🌐 Access Information:")
    print(f"- Dashboard: http://{minicloud_ip}:{dashboard_port}")
    print(f"- Admin Login: daniel")
    print(f"- Admin Password: {admin_password}")


def get_secure_input(prompt, required=False, secret=False):
    """Get secure input with validation"""
    import getpass
    
    while True:
        if secret:
            value = getpass.getpass(f"{prompt}: ")
        else:
            value = input(f"{prompt}: ").strip()
        
        if value or not required:
            return value
        
        print("❌ This field is required. Please enter a value.")


def create_gitignore():
    """Create .gitignore to prevent committing secrets"""
    gitignore_path = Path(".gitignore")
    gitignore_content = """# AI Systems Manager - Security
.env
*.log
logs/
data/
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.coverage
dist/
build/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# macOS
.DS_Store

# Database
*.db
*.sqlite
*.sqlite3

# SSL Certificates
*.crt
*.key
*.pem
"""
    
    if not gitignore_path.exists():
        with open(gitignore_path, 'w') as f:
            f.write(gitignore_content)
        print("✅ .gitignore created to protect secrets")


if __name__ == "__main__":
    try:
        generate_secure_config()
        create_gitignore()
        
        print("\n🚀 Setup Complete!")
        print("Next steps:")
        print("1. Review your .env configuration")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Test locally: python main.py")
        print("4. Deploy to minicloud: ./deploy.sh")
        
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)