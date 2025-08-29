#!/bin/bash
# AI Systems Manager - Bulletproof Deployment Script
# Deploy to minicloud server with full autonomous capabilities

set -e

MINICLOUD_IP="192.168.2.2"
ADMIN_USER=${ADMIN_USER:-daniel}
SSH_KEY=${SSH_KEY:-$HOME/.ssh/id_rsa}

echo "🚀 DEPLOYING AI SYSTEMS MANAGER TO MINICLOUD"
echo "📡 Target: $MINICLOUD_IP"
echo "🔐 Admin: $ADMIN_USER"

# Check if we can connect to minicloud
echo "🔍 Checking minicloud connectivity..."
if ! ping -c 3 $MINICLOUD_IP > /dev/null 2>&1; then
    echo "❌ Cannot reach minicloud server at $MINICLOUD_IP"
    exit 1
fi

# Check SSH connection
echo "🔐 Testing SSH connection..."
if ! ssh -i $SSH_KEY -o ConnectTimeout=10 $ADMIN_USER@$MINICLOUD_IP "echo 'SSH OK'" > /dev/null 2>&1; then
    echo "❌ SSH connection failed to $ADMIN_USER@$MINICLOUD_IP"
    echo "Make sure SSH key is configured: $SSH_KEY"
    exit 1
fi

echo "✅ Minicloud connectivity confirmed"

# Create deployment directory on minicloud
echo "📁 Creating deployment directory..."
ssh -i $SSH_KEY $ADMIN_USER@$MINICLOUD_IP "
    sudo mkdir -p /opt/ai-systems-manager
    sudo chown -R $ADMIN_USER:$ADMIN_USER /opt/ai-systems-manager
    cd /opt/ai-systems-manager
"

# Copy all files to minicloud
echo "📦 Transferring AI Systems Manager files..."
rsync -avz --delete -e "ssh -i $SSH_KEY" \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.DS_Store' \
    ./ $ADMIN_USER@$MINICLOUD_IP:/opt/ai-systems-manager/

# Install dependencies and start system on minicloud
echo "⚙️  Installing and starting AI Systems Manager on minicloud..."
ssh -i $SSH_KEY $ADMIN_USER@$MINICLOUD_IP "
    cd /opt/ai-systems-manager
    
    # Install system dependencies
    echo '🔧 Installing system dependencies...'
    sudo apt update
    sudo apt install -y python3 python3-pip docker.io docker-compose curl wget htop net-tools
    
    # Install Python dependencies
    echo '🐍 Installing Python dependencies...'
    pip3 install -r requirements.txt
    
    # Make scripts executable
    chmod +x start.sh deploy.sh
    chmod +x src/core/meta_agent.py
    chmod +x src/dashboard/dashboard.py
    
    # Set proper ownership
    sudo chown -R $ADMIN_USER:$ADMIN_USER /opt/ai-systems-manager
    
    # Add user to docker group
    sudo usermod -aG docker $ADMIN_USER
    
    # Start Docker service
    sudo systemctl enable docker
    sudo systemctl start docker
    
    # Create systemd service for auto-start
    sudo tee /etc/systemd/system/ai-systems-manager.service > /dev/null <<EOF
[Unit]
Description=AI Systems Manager - Meta Network Agent
After=docker.service
Requires=docker.service

[Service]
Type=simple
User=$ADMIN_USER
WorkingDirectory=/opt/ai-systems-manager
ExecStart=/opt/ai-systems-manager/start.sh
Restart=always
RestartSec=10
KillMode=mixed
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
EOF
    
    # Enable and start the service
    sudo systemctl daemon-reload
    sudo systemctl enable ai-systems-manager
    sudo systemctl start ai-systems-manager
    
    # Show service status
    sleep 5
    sudo systemctl status ai-systems-manager --no-pager -l
    
    echo '✅ AI Systems Manager deployed and started!'
    echo '📊 Dashboard: http://$MINICLOUD_IP:5001'
    echo '🔐 Ensure ADMIN_PASSWORD_HASH is configured in .env on target'
"

echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 AI Systems Manager Dashboard: http://$MINICLOUD_IP:5001"
echo "🔐 Admin Login: $ADMIN_USER / $ADMIN_PASSWORD"
echo "🤖 Meta Network Agent: 100% AUTONOMOUS"
echo "🛡️  Self-Healing: ENABLED"
echo "🧬 AI Evolution: ACTIVE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "The AI Systems Manager is now running autonomously on your minicloud."
echo "It will monitor, heal, and evolve your infrastructure without intervention."
echo ""
echo "To check status on minicloud:"
echo "  ssh -i $SSH_KEY $ADMIN_USER@$MINICLOUD_IP"
echo "  sudo systemctl status ai-systems-manager"
echo "  docker ps"
