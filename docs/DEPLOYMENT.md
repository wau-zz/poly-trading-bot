# Deployment Guide

This guide covers different deployment options for your PolyMarket trading bot, from simple EC2 instances to advanced container orchestration.

---

## Deployment Options Overview

| Method | Complexity | Best For | Cost |
|--------|-----------|----------|------|
| **Direct EC2** | Low | Getting started, single bot | $6-20/mo |
| **Docker on EC2** | Medium | Multiple bots, easy updates | $6-20/mo |
| **ECS (Fargate)** | Medium | Serverless containers | $10-30/mo |
| **EKS (Kubernetes)** | High | Large scale, multiple strategies | $50+/mo |
| **Lambda/Serverless** | Medium | Event-driven, low traffic | $0-10/mo |

---

## Option 1: Direct EC2 Deployment (Simplest)

### **Best For:** Starting out, single strategy, learning

**Pros:**
- ✅ Simplest setup
- ✅ Full control
- ✅ Easy to debug
- ✅ Low cost ($6/month)

**Cons:**
- ❌ Manual updates
- ❌ No automatic restarts
- ❌ Harder to scale

### Setup Steps:

```bash
# 1. Launch EC2 instance
# - Ubuntu 22.04 LTS
# - t3.micro or t3.small ($6-12/month)
# - Add security group (SSH port 22)

# 2. SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# 3. Install dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install python3.11 python3-pip git -y

# 4. Clone repository
git clone https://github.com/wau-zz/poly-trading-bot.git
cd poly-trading-bot

# 5. Install Python packages
pip3 install -r requirements.txt
cd strategies/strategy_1_arbitrage/python
pip3 install -r requirements.txt

# 6. Set up environment
nano .env
# Add your API keys

# 7. Run with screen (keeps running after disconnect)
screen -S polymarket_bot
python3 bot.py
# Press Ctrl+A then D to detach

# 8. Reattach later
screen -r polymarket_bot
```

### Auto-Start on Boot (systemd):

```bash
# Create service file
sudo nano /etc/systemd/system/polymarket-bot.service
```

```ini
[Unit]
Description=PolyMarket Trading Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/poly-trading-bot/strategies/strategy_1_arbitrage/python
Environment="PATH=/usr/bin:/usr/local/bin"
EnvironmentFile=/home/ubuntu/poly-trading-bot/.env
ExecStart=/usr/bin/python3 /home/ubuntu/poly-trading-bot/strategies/strategy_1_arbitrage/python/bot.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/polymarket-bot.log
StandardError=append:/var/log/polymarket-bot-error.log

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable polymarket-bot.service
sudo systemctl start polymarket-bot.service

# Check status
sudo systemctl status polymarket-bot.service

# View logs
sudo journalctl -u polymarket-bot.service -f
```

---

## Option 2: Docker on EC2 (Recommended)

### **Best For:** Multiple strategies, easy updates, production-ready

**Pros:**
- ✅ Isolated environments
- ✅ Easy updates (just pull new image)
- ✅ Can run multiple bots
- ✅ Consistent across dev/prod
- ✅ Easy rollback

**Cons:**
- ⚠️ Slightly more complex setup
- ⚠️ Need to learn Docker basics

### Setup Steps:

#### 1. Create Dockerfile

```dockerfile
# infrastructure/docker/Dockerfile.strategy1
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy shared code
COPY shared/python /app/shared/python

# Copy strategy code
COPY strategies/strategy_1_arbitrage/python /app/strategy

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY strategies/strategy_1_arbitrage/python/requirements.txt /app/strategy/
RUN pip install --no-cache-dir -r strategy/requirements.txt

# Set Python path
ENV PYTHONPATH=/app:/app/shared/python

# Run bot
WORKDIR /app/strategy
CMD ["python", "bot.py"]
```

#### 2. Create docker-compose.yml

```yaml
# infrastructure/docker/docker-compose.yml
version: '3.8'

services:
  arbitrage-bot:
    build:
      context: ../..
      dockerfile: infrastructure/docker/Dockerfile.strategy1
    container_name: polymarket_arbitrage
    restart: always
    env_file:
      - ../../.env
    volumes:
      - ../../data/logs:/app/logs
      - ../../data/db:/app/data
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
  
  pairs-bot:
    build:
      context: ../..
      dockerfile: infrastructure/docker/Dockerfile.strategy2
    container_name: polymarket_pairs
    restart: always
    env_file:
      - ../../.env
    volumes:
      - ../../data/logs:/app/logs
```

#### 3. Deploy to EC2

```bash
# On EC2 instance
sudo apt update
sudo apt install docker.io docker-compose -y
sudo usermod -aG docker ubuntu
# Log out and back in

# Clone repo
git clone https://github.com/wau-zz/poly-trading-bot.git
cd poly-trading-bot

# Create .env file
nano .env
# Add your API keys

# Build and run
cd infrastructure/docker
docker-compose up -d

# View logs
docker-compose logs -f

# Update (pull latest code and rebuild)
git pull
docker-compose up -d --build
```

---

## Option 3: AWS ECS (Fargate) - Serverless Containers

### **Best For:** No server management, auto-scaling, production

**Pros:**
- ✅ No server management
- ✅ Auto-scaling
- ✅ Pay only for what you use
- ✅ High availability

**Cons:**
- ❌ More complex setup
- ❌ Higher cost ($10-30/month)
- ❌ Need AWS knowledge

### Setup Steps:

#### 1. Create ECR Repository

```bash
# Create ECR repo
aws ecr create-repository --repository-name polymarket-bot

# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

# Build and push image
docker build -f infrastructure/docker/Dockerfile.strategy1 -t polymarket-bot:latest .
docker tag polymarket-bot:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/polymarket-bot:latest
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/polymarket-bot:latest
```

#### 2. Create ECS Task Definition

```json
{
  "family": "polymarket-bot",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "arbitrage-bot",
      "image": "YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/polymarket-bot:latest",
      "environment": [
        {"name": "POLYMARKET_API_KEY", "value": "your_key"},
        {"name": "POLYMARKET_API_SECRET", "value": "your_secret"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/polymarket-bot",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### 3. Create ECS Service

```bash
aws ecs create-service \
  --cluster polymarket-cluster \
  --service-name polymarket-bot \
  --task-definition polymarket-bot \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

---

## Option 4: AWS Lambda (Serverless)

### **Best For:** Event-driven, low-frequency trading, cost optimization

**Pros:**
- ✅ Pay per execution (very cheap)
- ✅ Auto-scaling
- ✅ No server management

**Cons:**
- ❌ 15-minute timeout limit
- ❌ Not ideal for continuous monitoring
- ❌ Cold starts

### Use Case:

```python
# For strategies that run periodically, not continuously
# Example: Check for arbitrage every 5 minutes

import json
import boto3

def lambda_handler(event, context):
    # Run arbitrage scan
    opportunities = scan_for_arbitrage()
    
    for opp in opportunities:
        execute_arbitrage(opp)
    
    return {
        'statusCode': 200,
        'body': json.dumps(f'Found {len(opportunities)} opportunities')
    }
```

**Trigger with EventBridge (CloudWatch Events):**
- Run every 5 minutes
- Cost: ~$0.20/month for 8,640 executions

---

## Option 5: Kubernetes (EKS) - Advanced

### **Best For:** Large scale, multiple strategies, enterprise

**Pros:**
- ✅ Ultimate scalability
- ✅ High availability
- ✅ Advanced orchestration

**Cons:**
- ❌ Very complex
- ❌ High cost ($50+/month minimum)
- ❌ Overkill for most traders

**Only use if:**
- Running 10+ strategies simultaneously
- Need auto-scaling across multiple regions
- Have DevOps expertise

---

## Recommended Deployment Path

### **Phase 1: Start Simple (Direct EC2)**
```
Week 1-2: Deploy directly to EC2
- Single strategy
- Manual monitoring
- Learn the system
```

### **Phase 2: Add Docker (Docker on EC2)**
```
Week 3-4: Containerize
- Multiple strategies
- Easy updates
- Better isolation
```

### **Phase 3: Scale Up (ECS Fargate)**
```
Month 2+: Move to ECS
- Auto-scaling
- High availability
- Production-ready
```

---

## Cost Comparison

### **EC2 Direct:**
- t3.micro: $6/month
- t3.small: $12/month
- **Total: $6-12/month**

### **Docker on EC2:**
- Same as EC2 Direct
- **Total: $6-12/month**

### **ECS Fargate:**
- 0.25 vCPU, 0.5GB RAM: ~$10/month
- 0.5 vCPU, 1GB RAM: ~$20/month
- **Total: $10-30/month**

### **Lambda:**
- First 1M requests free
- Then $0.20 per 1M requests
- **Total: $0-5/month** (for periodic checks)

---

## My Recommendation

### **For Most Traders:**

**Start:** Direct EC2 deployment
- Simplest to set up
- Easy to debug
- Low cost ($6/month)
- Learn the system

**Then:** Move to Docker on EC2
- When you have 2+ strategies
- Want easier updates
- Still low cost ($6-12/month)

**Later:** Consider ECS Fargate
- When you're making serious money
- Need high availability
- Want auto-scaling

### **Quick Start Command:**

```bash
# One-liner EC2 setup (after SSH)
sudo apt update && sudo apt install -y python3.11 python3-pip git screen && \
git clone https://github.com/wau-zz/poly-trading-bot.git && \
cd poly-trading-bot && pip3 install -r requirements.txt && \
cd strategies/strategy_1_arbitrage/python && \
pip3 install -r requirements.txt && \
screen -S bot python3 bot.py
```

---

## Monitoring & Maintenance

### **Essential Monitoring:**

1. **Logs:**
   ```bash
   # Direct EC2
   tail -f /var/log/polymarket-bot.log
   
   # Docker
   docker-compose logs -f
   ```

2. **Health Checks:**
   - API connection status
   - Trade execution success rate
   - Capital balance
   - Error rates

3. **Alerts:**
   - Email/SMS on errors
   - Telegram notifications
   - CloudWatch alarms (AWS)

---

## Security Best Practices

1. **Never commit API keys** - Use `.env` files
2. **Use IAM roles** (AWS) instead of hardcoded credentials
3. **Enable firewall** - Only allow necessary ports
4. **Regular updates** - Keep dependencies current
5. **Backup data** - Regular database backups

---

## Troubleshooting

### **Bot stops running:**
```bash
# Check if process is running
ps aux | grep python

# Check systemd status
sudo systemctl status polymarket-bot

# Check Docker
docker ps
docker logs polymarket-bot
```

### **Out of memory:**
- Upgrade instance size
- Or optimize code (reduce memory usage)

### **API errors:**
- Check API key validity
- Verify rate limits
- Check network connectivity

---

**Choose the deployment method that matches your current needs. Start simple, scale as you grow!**

