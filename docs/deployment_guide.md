# VPS Deployment Guide

Deploy your Telegram bot to a VPS (Virtual Private Server) in one command with `telegram-bot-stack`.

## Quick Start

### Prerequisites

- VPS with Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- SSH access to VPS (root or sudo user)
- Bot token from [@BotFather](https://t.me/BotFather)

### 1. Initialize Deployment

```bash
telegram-bot-stack deploy init
```

This will:

- Prompt for VPS connection details (host, user, SSH key)
- Test SSH connection
- Generate `deploy.yaml` configuration file

**Example:**

```
🚀 VPS Deployment Setup

VPS Host: 142.93.100.50
SSH User: root
SSH Key Path [~/.ssh/id_rsa]:
Bot Name: my-awesome-bot
Bot Token (from @BotFather): 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

✓ SSH connection successful
✅ Configuration saved to deploy.yaml
```

### 2. Deploy to VPS

```bash
export BOT_TOKEN="your-bot-token-here"
telegram-bot-stack deploy up
```

This will:

- Connect to VPS via SSH
- Install Docker and Docker Compose (if not installed)
- Transfer bot files to VPS
- Build Docker image
- Start bot container

**First deployment takes ~5 minutes. Updates take ~2 minutes.**

### 3. Check Status

```bash
telegram-bot-stack deploy status
```

Shows:

- Container status (running/stopped)
- Resource usage (CPU, memory)
- Recent logs

### 4. View Logs

```bash
# View last 50 lines
telegram-bot-stack deploy logs

# Follow logs in real-time
telegram-bot-stack deploy logs --follow

# View last 100 lines
telegram-bot-stack deploy logs --tail 100
```

### 5. Update Bot

After making changes to your bot code:

```bash
telegram-bot-stack deploy update
```

This will:

- Transfer updated files
- Rebuild Docker image
- Restart bot container (minimal downtime)

### 6. Stop Bot

```bash
# Stop bot (keeps container and image)
telegram-bot-stack deploy down

# Stop and remove everything
telegram-bot-stack deploy down --cleanup
```

## Configuration

### deploy.yaml

The `deploy.yaml` file contains all deployment settings:

```yaml
vps:
  host: "your-vps.com" # VPS hostname or IP
  user: "root" # SSH user
  ssh_key: "~/.ssh/id_rsa" # SSH private key path
  port: 22 # SSH port

bot:
  name: "my-telegram-bot" # Bot name (container/image name)
  token_env: "BOT_TOKEN" # Environment variable for bot token
  entry_point: "bot.py" # Main bot file
  python_version: "3.11" # Python version (3.9-3.12)

deployment:
  method: "docker" # Deployment method
  auto_restart: true # Auto-restart on failure
  log_rotation: true # Enable log rotation

resources:
  memory_limit: "256M" # Maximum memory
  memory_reservation: "128M" # Reserved memory
  cpu_limit: "0.5" # Maximum CPU cores
  cpu_reservation: "0.25" # Reserved CPU cores

logging:
  level: "INFO" # Log level
  max_size: "5m" # Max log file size
  max_files: "5" # Number of log files to keep

environment:
  timezone: "UTC" # Container timezone
  # Add custom environment variables here
```

### Environment Variables

Set bot token and other secrets via environment variables:

```bash
export BOT_TOKEN="your-bot-token"
export CUSTOM_VAR="value"
```

These will be automatically added to the `.env` file on VPS.

## VPS Providers

### Recommended Providers

**DigitalOcean** ($5/month)

- Easy to use
- Good documentation
- Fast deployment

**Hetzner** (€3.79/month)

- Best price/performance
- European data centers

**AWS Lightsail** ($3.50/month)

- Integrated with AWS ecosystem
- Global data centers

**Vultr** ($2.50/month)

- Cheapest option
- Multiple locations

### Minimum Requirements

- **RAM:** 512 MB (1 GB recommended)
- **CPU:** 1 core
- **Storage:** 10 GB
- **OS:** Ubuntu 20.04+ / Debian 11+

## SSH Setup

### Generate SSH Key (if you don't have one)

```bash
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"
```

### Add SSH Key to VPS

```bash
ssh-copy-id root@your-vps-ip
```

Or manually:

```bash
cat ~/.ssh/id_rsa.pub | ssh root@your-vps-ip "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

### Test SSH Connection

```bash
ssh root@your-vps-ip
```

## Docker Setup

Docker is automatically installed during first deployment. If you want to install manually:

```bash
# On VPS
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## Advanced Usage

### Custom Dockerfile

If you need custom Docker configuration, create `Dockerfile` in your project root. It will be used instead of the template.

### Multiple Bots

Deploy multiple bots to the same VPS:

```bash
# Bot 1
telegram-bot-stack deploy init --bot-name bot1
telegram-bot-stack deploy up --config deploy-bot1.yaml

# Bot 2
telegram-bot-stack deploy init --bot-name bot2
telegram-bot-stack deploy up --config deploy-bot2.yaml
```

### Custom Domain

Add custom domain to your bot (for webhooks):

1. Point domain to VPS IP
2. Install nginx on VPS
3. Configure reverse proxy
4. Add SSL certificate (Let's Encrypt)

### Health Monitoring

The deployed bot includes automatic health checks:

- Container restarts automatically on failure
- Health check every 30 seconds
- 3 retries before marking unhealthy

View health status:

```bash
telegram-bot-stack deploy status
```

### Log Rotation

Logs are automatically rotated to prevent disk space issues:

- Max log size: 5 MB (configurable)
- Max log files: 5 (configurable)
- Old logs are compressed

## Troubleshooting

### SSH Connection Failed

**Problem:** Cannot connect to VPS

**Solutions:**

1. Check SSH key permissions: `chmod 600 ~/.ssh/id_rsa`
2. Verify VPS IP address
3. Check firewall rules (port 22 must be open)
4. Try password authentication: `ssh root@your-vps-ip`

### Docker Installation Failed

**Problem:** Docker installation fails

**Solutions:**

1. Check VPS OS compatibility (Ubuntu 20.04+)
2. Ensure you have root access
3. Install Docker manually (see Docker Setup section)

### Bot Not Starting

**Problem:** Bot container starts but immediately stops

**Solutions:**

1. Check logs: `telegram-bot-stack deploy logs`
2. Verify bot token is correct: `echo $BOT_TOKEN`
3. Check bot code for errors
4. Ensure all dependencies are in `requirements.txt`

### Out of Memory

**Problem:** Bot crashes due to memory issues

**Solutions:**

1. Increase memory limit in `deploy.yaml`:
   ```yaml
   resources:
     memory_limit: "512M" # Increase from 256M
   ```
2. Upgrade VPS plan
3. Optimize bot code (reduce memory usage)

### Deployment Takes Too Long

**Problem:** Deployment hangs or takes very long

**Solutions:**

1. Check VPS internet connection
2. Verify Docker is installed: `ssh root@vps "docker --version"`
3. Check VPS disk space: `ssh root@vps "df -h"`
4. Use verbose mode: `telegram-bot-stack deploy up --verbose`

## Security Best Practices

### 1. Use SSH Keys (Not Passwords)

Always use SSH key authentication instead of passwords.

### 2. Keep Bot Token Secret

Never commit bot token to git:

```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo "deploy.yaml" >> .gitignore
```

### 3. Update VPS Regularly

```bash
ssh root@your-vps-ip
apt update && apt upgrade -y
```

### 4. Configure Firewall

```bash
# On VPS
ufw allow 22/tcp  # SSH
ufw enable
```

### 5. Use Non-Root User

Create dedicated user for bot:

```bash
# On VPS
adduser botuser
usermod -aG docker botuser
```

Then use `botuser` in `deploy.yaml`:

```yaml
vps:
  user: "botuser"
```

## Cost Estimation

### Monthly Costs

| Provider      | Plan    | RAM    | CPU    | Storage | Price    |
| ------------- | ------- | ------ | ------ | ------- | -------- |
| DigitalOcean  | Basic   | 1 GB   | 1 core | 25 GB   | $5/mo    |
| Hetzner       | CX11    | 2 GB   | 1 core | 20 GB   | €3.79/mo |
| AWS Lightsail | Nano    | 512 MB | 1 core | 20 GB   | $3.50/mo |
| Vultr         | Regular | 512 MB | 1 core | 10 GB   | $2.50/mo |

**Recommendation:** Start with DigitalOcean $5/mo plan for simplicity.

### Traffic Costs

Most VPS plans include generous bandwidth (1-2 TB/month). Telegram bots typically use <1 GB/month.

## Performance Optimization

### 1. Use Polling Instead of Webhooks

For small bots (<1000 users), polling is simpler and sufficient.

### 2. Optimize Docker Image

Reduce image size by using slim Python image (already done in template).

### 3. Enable Caching

Use Redis for caching (optional, for larger bots):

```yaml
# In deploy.yaml
services:
  redis:
    image: redis:alpine
    restart: always
```

### 4. Monitor Resource Usage

```bash
# Check CPU and memory usage
telegram-bot-stack deploy status

# View detailed stats
ssh root@your-vps-ip "docker stats"
```

## Next Steps

- [Storage Guide](storage_guide.md) - Configure database storage
- [Architecture](architecture.md) - Understand framework internals
- [API Reference](api_reference.md) - Explore available APIs

## Support

- **Issues:** [GitHub Issues](https://github.com/sensiloles/telegram-bot-stack/issues)
- **Discussions:** [GitHub Discussions](https://github.com/sensiloles/telegram-bot-stack/discussions)
- **Documentation:** [Full Documentation](README.md)
