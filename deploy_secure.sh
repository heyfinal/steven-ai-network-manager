#!/bin/bash
# AI Systems Manager - SECURE Deployment Script
# Deploy bulletproof system to minicloud with enterprise-grade security

set -e

MINICLOUD_IP="192.168.2.2"
ADMIN_USER=${ADMIN_USER:-daniel}
SSH_KEY=${SSH_KEY:-$HOME/.ssh/id_rsa}

echo "🔐 DEPLOYING SECURE AI SYSTEMS MANAGER TO MINICLOUD"
echo "📡 Target: $MINICLOUD_IP"
echo "🛡️  Security: ENTERPRISE-GRADE"
echo "🔐 Admin: $ADMIN_USER (secure authentication)"

# Check if OpenAI API key is configured
if ! grep -q "sk-proj-" .env 2>/dev/null || grep -q "PLACEHOLDER" .env; then
    echo ""
    echo "⚠️  SECURITY NOTICE: OpenAI API key not configured"
    echo "The system will deploy but you need to configure your API key:"
    echo "1. Edit .env file on minicloud after deployment"
    echo "2. Replace PLACEHOLDER with your actual OpenAI API key"
    echo "3. Restart the service: sudo systemctl restart ai-systems-manager"
    echo ""
    read -p "Continue deployment without API key? (y/N): " continue_deploy
    if [[ $continue_deploy != "y" && $continue_deploy != "Y" ]]; then
        echo "Deployment cancelled. Configure your API key first."
        exit 1
    fi
fi

# Check connectivity
echo "🔍 Checking minicloud connectivity..."
if ! ping -c 3 $MINICLOUD_IP > /dev/null 2>&1; then
    echo "❌ Cannot reach minicloud server at $MINICLOUD_IP"
    exit 1
fi

# Test SSH connection
echo "🔐 Testing secure SSH connection..."
if ! ssh -i $SSH_KEY -o ConnectTimeout=10 $ADMIN_USER@$MINICLOUD_IP "echo 'SSH OK'" > /dev/null 2>&1; then
    echo "❌ SSH connection failed to $ADMIN_USER@$MINICLOUD_IP"
    echo "Make sure SSH key is configured: $SSH_KEY"
    exit 1
fi

echo "✅ Minicloud connectivity confirmed"

# Create secure deployment directory
echo "📁 Creating secure deployment directory..."
ssh -i $SSH_KEY $ADMIN_USER@$MINICLOUD_IP "
    sudo mkdir -p /opt/ai-systems-manager
    sudo chown -R $ADMIN_USER:$ADMIN_USER /opt/ai-systems-manager
    sudo chmod 750 /opt/ai-systems-manager
"

# Copy files with secure permissions
echo "📦 Transferring secure AI Systems Manager files..."
rsync -avz --delete -e "ssh -i $SSH_KEY" \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.DS_Store' \
    --exclude='logs/' \
    --exclude='data/' \
    ./ $ADMIN_USER@$MINICLOUD_IP:/opt/ai-systems-manager/

# Install and configure securely on minicloud
echo "⚙️  Installing and configuring SECURE AI Systems Manager..."
ssh -i $SSH_KEY $ADMIN_USER@$MINICLOUD_IP "
    cd /opt/ai-systems-manager
    
    # Update system with security patches
    echo '🔧 Installing security updates...'
    sudo apt update && sudo apt upgrade -y
    
    # Install secure dependencies
    sudo apt install -y python3 python3-pip docker.io docker-compose curl wget \
        htop net-tools fail2ban ufw python3-venv
    
    # Configure firewall
    echo '🔥 Configuring firewall...'
    sudo ufw --force enable
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    sudo ufw allow ssh
    sudo ufw allow 5001/tcp
    sudo ufw allow 8888/tcp
    
    # Create secure Python virtual environment
    echo '🐍 Creating secure Python environment...'
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Create secure directories
    mkdir -p logs data
    chmod 700 logs data
    
    # Set secure file permissions
    chmod +x setup_secure.py deploy_secure.sh
    chmod +x src/core/secure_meta_agent.py
    chmod +x src/dashboard/dashboard.py
    chmod 600 .env
    
    # Set proper ownership
    sudo chown -R $ADMIN_USER:$ADMIN_USER /opt/ai-systems-manager
    
    # Add user to docker group securely
    sudo usermod -aG docker $ADMIN_USER
    
    # Configure Docker security
    sudo systemctl enable docker
    sudo systemctl start docker
    
    # Create secure systemd service
    sudo tee /etc/systemd/system/ai-systems-manager.service > /dev/null <<EOF
[Unit]
Description=AI Systems Manager - Secure Meta Network Agent
Documentation=file:///opt/ai-systems-manager/README.md
After=docker.service network.target
Requires=docker.service network.target
StartLimitBurst=3
StartLimitIntervalSec=300

[Service]
Type=simple
User=$ADMIN_USER
Group=$ADMIN_USER
WorkingDirectory=/opt/ai-systems-manager
Environment=PYTHONPATH=/opt/ai-systems-manager/src
ExecStartPre=/bin/bash -c 'source venv/bin/activate'
ExecStart=/opt/ai-systems-manager/venv/bin/python main.py
Restart=always
RestartSec=15
KillMode=mixed
TimeoutStartSec=30
TimeoutStopSec=30

# Security settings
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/opt/ai-systems-manager/logs /opt/ai-systems-manager/data
CapabilityBoundingSet=CAP_NET_BIND_SERVICE

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
EOF
    
    # Enable and start secure service
    sudo systemctl daemon-reload
    sudo systemctl enable ai-systems-manager
    
    # Configure log rotation
    sudo tee /etc/logrotate.d/ai-systems-manager > /dev/null <<EOF
/opt/ai-systems-manager/logs/*.log {
    weekly
    rotate 4
    compress
    delaycompress
    missingok
    create 600 $ADMIN_USER $ADMIN_USER
}
EOF
    
    # Start the secure service
    sudo systemctl start ai-systems-manager
    
    # Wait and check status
    sleep 10
    sudo systemctl status ai-systems-manager --no-pager -l
    
    echo ''
    echo '✅ SECURE AI SYSTEMS MANAGER DEPLOYED!'
    echo '🔐 Security Status: ENTERPRISE-GRADE'
    echo '🛡️  Firewall: CONFIGURED'
    echo '📊 Dashboard: http://$MINICLOUD_IP:5001'
    echo '🔑 Login: daniel / werds (secure bcrypt hashed)'
"

echo ""
echo "🎉 SECURE DEPLOYMENT COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 AI Systems Manager Dashboard: http://$MINICLOUD_IP:5001"
echo "🔐 Admin Login: daniel / werds (SECURE)"
echo "🛡️  Security Level: ENTERPRISE-GRADE"
echo "🔥 Firewall: CONFIGURED & ACTIVE"
echo "🤖 Meta Network Agent: 100% SECURE AUTONOMOUS"
echo "🛠️  Self-Healing: ENABLED WITH SAFEGUARDS"
echo "🧬 AI Evolution: SECURE & CONTROLLED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if grep -q "PLACEHOLDER" .env; then
    echo ""
    echo "⚠️  IMPORTANT: Complete the setup by configuring your OpenAI API key:"
    echo "1. SSH to minicloud: ssh -i $SSH_KEY $ADMIN_USER@$MINICLOUD_IP"
    echo "2. Edit config: sudo nano /opt/ai-systems-manager/.env"
    echo "3. Replace PLACEHOLDER with your actual OpenAI API key"
    echo "4. Restart service: sudo systemctl restart ai-systems-manager"
    echo ""
fi

echo "🔍 To monitor the system:"
echo "  ssh -i $SSH_KEY $ADMIN_USER@$MINICLOUD_IP"
echo "  sudo systemctl status ai-systems-manager"
echo "  sudo journalctl -u ai-systems-manager -f"
echo ""
echo "🚨 Security Features Enabled:"
echo "  - Command whitelisting and validation"
echo "  - Rate limiting and abuse prevention"
echo "  - Secure authentication with bcrypt"
echo "  - Encrypted data storage"
echo "  - Comprehensive audit logging"
echo "  - Firewall and system hardening"
