# Steven - AI Network Managing Agent

**Autonomous AI System Manager & Self-Healing Infrastructure**

## Overview

Steven is an advanced AI-powered network managing agent and autonomous repair tech designed for managing minicloud servers and infrastructure. Built with enterprise-grade security and featuring self-healing capabilities, Steven continuously monitors, optimizes, and evolves your system infrastructure without human intervention.

## Features

### 🤖 Autonomous Operation
- 100% autonomous system management
- Self-healing infrastructure with automatic issue resolution
- AI-powered evolution and optimization
- Real-time monitoring and response

### 🛡️ Security
- Enterprise-grade authentication (admin: daniel/werds)
- Secure API key management
- Command validation and whitelisting
- Comprehensive audit logging
- Rate limiting and abuse prevention

### 📊 Professional Dashboard
- Modern 2025 glassmorphism UI design
- Real-time WebSocket updates
- Tabbed interfaces for containers and MCP servers
- OpenAI API usage tracking and metrics
- Integrated terminal for command execution
- Interactive healing actions log
- AI evolution tracking

### 🔧 System Management
- Docker container orchestration
- MCP (Model Context Protocol) server management
- Automatic service restart and recovery
- Performance optimization
- Resource monitoring (CPU, Memory, Disk, Network)

### 🧠 AI Integration
- OpenAI GPT-4 powered decision making
- Intelligent command interpretation
- Predictive failure analysis
- Machine learning-based anomaly detection
- Cost tracking and usage metrics

## Dashboard Features

- **Container Management**: Active, suggested, and catalog views
- **MCP Server Monitoring**: Real-time status with auto-healing
- **MCU Tools**: Development tool integration
- **Healing Actions**: Live log with command interface
- **AI Evolution Log**: Track system improvements
- **Analytics**: Visual performance metrics
- **Settings**: System configuration panel
- **API Usage Metrics**: 
  - Tokens used today/month
  - Average daily usage
  - Cost tracking
  - Usage history

## Status Display

Steven never shows services as "down" - instead displays:
- "Steven is currently fixing [service]" - for stopped services
- "Steven is optimizing [service]" - for degraded services
- Alert system for issues requiring manual intervention

## Technology Stack

- **Backend**: Python 3.x, Flask, SQLite
- **Frontend**: HTML5, JavaScript, WebSockets
- **AI**: OpenAI GPT-4 API
- **ML**: Scikit-learn (Isolation Forest, Random Forest)
- **Monitoring**: psutil, Docker SDK
- **Security**: bcrypt, JWT, rate limiting

## Deployment

Steven is deployed on minicloud server (192.168.2.2) with:
- Systemd service management
- Auto-start on boot
- UFW firewall configuration
- Secure file permissions
- Professional admin dashboard at port 5001

## Architecture

```
Steven AI System Manager
├── Meta Network Agent (Core AI)
│   ├── Self-Healing Engine
│   ├── Evolution System
│   └── API Usage Tracker
├── Dashboard (Flask Web)
│   ├── Real-time WebSocket
│   ├── Command Interface
│   └── Metrics Display
└── Security Layer
    ├── Authentication
    ├── Command Validation
    └── Audit Logging
```

## Created By

Built using MCP servers and tools with Claude Code assistant.

**Admin Access**: daniel / werds

---

*Steven - Your AI Network Managing Agent & Autonomous Repair Tech*
