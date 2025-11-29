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

### 2. Set Secrets (Recommended)

For secure production deployment, use secrets management:

```bash
telegram-bot-stack deploy secrets set BOT_TOKEN "your-bot-token-here"
```

Alternatively, you can use environment variables (less secure):

```bash
export BOT_TOKEN="your-bot-token-here"
```

### 3. Deploy to VPS

```bash
telegram-bot-stack deploy up
```

This will:

- Connect to VPS via SSH
- Install Docker and Docker Compose (if not installed)
- Transfer bot files to VPS
- Build Docker image
- Start bot container

**First deployment takes ~5 minutes. Updates take ~2 minutes.**

### 4. Check Status

```bash
# Check deployment status
telegram-bot-stack deploy status

# Check bot health
telegram-bot-stack deploy health
```

Shows:

- Container status (running/stopped)
- Health status (healthy/unhealthy)
- Resource usage (CPU, memory)
- Uptime and restart count
- Recent logs

### 5. View Logs

```bash
# View last 50 lines
telegram-bot-stack deploy logs

# Follow logs in real-time
telegram-bot-stack deploy logs --follow

# View last 100 lines
telegram-bot-stack deploy logs --tail 100
```

### 6. Update Bot

After making changes to your bot code:

```bash
telegram-bot-stack deploy update
```

This will:

- Create automatic backup (if enabled)
- Transfer updated files
- Rebuild Docker image
- Restart bot container (minimal downtime)

**Options:**

- `--backup` - Force backup before update
- `--no-backup` - Skip automatic backup

### 7. Rollback to Previous Version

If an update introduces issues, rollback to the previous working version:

```bash
# Rollback to previous deployment
telegram-bot-stack deploy rollback
```

This will:

- Show version information
- Request confirmation
- Create backup of current data
- Stop current bot
- Switch to previous Docker image
- Start bot with previous version

**Rollback to Specific Version:**

```bash
# View deployment history first
telegram-bot-stack deploy history

# Rollback to specific version
telegram-bot-stack deploy rollback --version mybot:v1234567890-abc123

# Skip confirmation prompt
telegram-bot-stack deploy rollback --yes
```

**Important:**

- Rollback is only available if you have deployed at least twice
- Previous Docker images must still exist (last 5 versions are kept)
- Rollback automatically creates a backup before switching versions
- Data is preserved during rollback (unless incompatible schema changes)

### 8. View Deployment History

Track all your deployments:

```bash
# View deployment history
telegram-bot-stack deploy history

# Limit number of versions shown
telegram-bot-stack deploy history --limit 5
```

**Output shows:**

- Version status (active/old/failed/rolled back)
- Docker image tag
- Git commit hash
- Deployment timestamp

**Example:**

```
📜 Deployment History

Status          Docker Tag                           Git Commit  Deployed At
✅ Active        mybot:v1706281800-abc123f           abc123f     2025-01-26 14:30:00
📦 Old          mybot:v1706278200-def456a           def456a     2025-01-26 13:30:00
📦 Old          mybot:v1706274600-789bcde           789bcde     2025-01-26 12:30:00
```

**Version Management:**

- Automatic version tracking on every deployment
- Last 5 deployments are kept (configurable)
- Old Docker images are automatically cleaned up
- Failed deployments are also tracked

### 9. Stop Bot

```bash
# Stop bot (keeps container and image)
telegram-bot-stack deploy down

# Stop and remove everything (with auto-backup)
telegram-bot-stack deploy down --cleanup

# Skip auto-backup before cleanup
telegram-bot-stack deploy down --cleanup --no-backup
```

**Note:** When using `--cleanup`, an automatic backup is created before removing containers and images (unless `--no-backup` is specified).

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

### Secrets Management (Recommended)

For production deployments, use the secure secrets management system instead of environment variables:

**1. Initialize deployment (generates encryption key):**

```bash
telegram-bot-stack deploy init
```

This automatically generates an encryption key and stores it in `deploy.yaml`.

**2. Set secrets on VPS:**

```bash
# Set bot token
telegram-bot-stack deploy secrets set BOT_TOKEN "your-bot-token-here"

# Set additional secrets
telegram-bot-stack deploy secrets set DB_PASSWORD "secure-password"
```

**3. List stored secrets:**

```bash
telegram-bot-stack deploy secrets list
```

Shows secret names only (values are hidden for security).

**4. Get secret value (for debugging):**

```bash
telegram-bot-stack deploy secrets get BOT_TOKEN
```

**5. Remove secret:**

```bash
telegram-bot-stack deploy secrets remove BOT_TOKEN
```

**How it works:**

- Secrets are encrypted using Fernet (symmetric encryption)
- Encrypted version stored in `/opt/{bot_name}/.secrets.env.encrypted` on VPS with 600 permissions (owner read/write only)
- During container startup, secrets are decrypted **in-memory** to `/dev/shm` (shared memory, RAM-based, not persisted to disk)
- Decrypted secrets are only available during container startup and never written to persistent storage
- Automatically loaded into Docker container via symlink from shared memory
- Not visible in `docker inspect` or process list

**Security benefits:**

- ✅ Secrets encrypted at rest on VPS (only encrypted version on filesystem)
- ✅ Decrypted secrets stored in RAM (`/dev/shm`) - cleared on reboot, never on disk
- ✅ Secure file permissions (600) for both encrypted and decrypted versions
- ✅ Not visible in environment variables or Docker inspect
- ✅ No plain text secrets ever written to persistent storage
- ✅ No need to export tokens before every deployment

**Important:** Keep `deploy.yaml` secure - it contains your encryption key!

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

## Provider-Specific Guides

### DigitalOcean Deployment

DigitalOcean is the recommended provider for beginners due to its simplicity and excellent documentation.

#### Step 1: Create Droplet

1. Go to [DigitalOcean](https://www.digitalocean.com/)
2. Click "Create" → "Droplets"
3. Choose:
   - **Image:** Ubuntu 22.04 LTS
   - **Plan:** Basic ($5/month - 1 GB RAM, 1 vCPU, 25 GB SSD)
   - **Region:** Choose nearest to your users
   - **Authentication:** Add your SSH key
4. Click "Create Droplet"

#### Step 2: Get Droplet IP

After creation, you'll see the droplet IP address. Copy it:

```bash
export VPS_IP=xxx.xxx.xxx.xxx
```

#### Step 3: Deploy Bot

```bash
# Initialize deployment
telegram-bot-stack deploy init
# Enter VPS_IP when prompted for "VPS Host"

# Deploy
export BOT_TOKEN="your-bot-token"
telegram-bot-stack deploy up
```

**Cost:** $5/month
**Performance:** Handles 1000+ users easily
**Support:** Excellent documentation and community

### Hetzner Cloud Deployment

Hetzner offers the best price/performance ratio, especially for European users.

#### Step 1: Create Server

1. Go to [Hetzner Cloud](https://www.hetzner.com/cloud)
2. Click "Add Server"
3. Choose:
   - **Location:** Choose nearest data center
   - **Image:** Ubuntu 22.04
   - **Type:** CX11 (€3.79/month - 2 GB RAM, 1 vCPU, 20 GB SSD)
   - **SSH Key:** Add your SSH key
4. Click "Create & Buy"

#### Step 2: Deploy Bot

```bash
# Initialize deployment
telegram-bot-stack deploy init
# Enter server IP when prompted

# Deploy
export BOT_TOKEN="your-bot-token"
telegram-bot-stack deploy up
```

**Cost:** €3.79/month (cheapest option)
**Performance:** Excellent value, 2 GB RAM
**Support:** Good documentation, European data centers

### AWS Lightsail Deployment

AWS Lightsail is ideal if you're already using AWS services or need global data centers.

#### Step 1: Launch Instance

1. Go to [AWS Lightsail](https://lightsail.aws.amazon.com/)
2. Click "Create instance"
3. Choose:
   - **Platform:** Linux/Unix
   - **Blueprint:** Ubuntu 22.04 LTS
   - **Instance plan:** $3.50/month (512 MB RAM, 1 vCPU, 20 GB SSD)
   - **Region:** Choose nearest to your users
   - **SSH key pair:** Create new or use existing
4. Click "Create instance"

#### Step 2: Configure Security Group

1. Go to instance → "Networking" tab
2. Add firewall rule:
   - **Application:** Custom
   - **Protocol:** TCP
   - **Port:** 22 (SSH)
   - **Source:** Your IP address

#### Step 3: Deploy Bot

```bash
# Initialize deployment
telegram-bot-stack deploy init
# Enter Lightsail public IP

# Deploy
export BOT_TOKEN="your-bot-token"
telegram-bot-stack deploy up
```

**Cost:** $3.50/month (free tier eligible for 12 months)
**Performance:** Good for small bots
**Support:** Integrated with AWS ecosystem

### AWS EC2 Deployment

For more control and scalability, use AWS EC2.

#### Step 1: Launch Instance

1. Go to [AWS EC2 Console](https://console.aws.amazon.com/ec2/)
2. Click "Launch Instance"
3. Configure:
   - **Name:** telegram-bot
   - **AMI:** Ubuntu Server 22.04 LTS (Free tier eligible)
   - **Instance type:** t3.micro (free tier) or t3.small
   - **Key pair:** Create new or use existing
   - **Security group:** Allow SSH (port 22) from your IP
4. Click "Launch instance"

#### Step 2: Deploy Bot

```bash
# Initialize deployment
telegram-bot-stack deploy init
# Enter EC2 public IPv4 address

# Deploy
export BOT_TOKEN="your-bot-token"
telegram-bot-stack deploy up
```

**Cost:** Free tier (12 months), then ~$10/month
**Performance:** Highly scalable
**Support:** Full AWS ecosystem integration

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

## Deployment Methods

### Docker Deployment (Recommended)

Docker is the default and recommended deployment method. It provides:

- Isolation from system dependencies
- Easy updates and rollbacks
- Consistent environment across servers
- Built-in health checks and auto-restart

Docker is automatically installed during first deployment. If you want to install manually:

```bash
# On VPS - installs Docker with built-in Compose v2
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Verify installation (Compose v2 is built-in)
docker --version
docker compose version
```

**Note:** Modern Docker (20.10+) includes Docker Compose v2 as `docker compose` (built-in). The old standalone `docker-compose` is no longer needed.

### Systemd Deployment (Alternative)

Systemd deployment is a lightweight alternative to Docker, suitable for:

- Simple VPS setups without Docker
- Direct system integration
- Lower resource overhead
- Native Linux service management

#### When to Use Systemd

- You prefer native Linux services over containers
- You have limited resources (very small VPS)
- You need direct system integration
- You're comfortable with systemd configuration

#### Systemd Setup

**Note:** Systemd deployment is not yet fully automated via CLI. Manual setup required:

1. **Create systemd service file** (`/etc/systemd/system/telegram-bot.service`):

```ini
[Unit]
Description=Telegram Bot Service
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/opt/telegram-bot
Environment="BOT_TOKEN=your-bot-token"
Environment="PYTHONPATH=/opt/telegram-bot"
ExecStart=/usr/bin/python3 /opt/telegram-bot/bot.py
Restart=always
RestartSec=10

# Resource limits
MemoryLimit=256M
CPUQuota=50%

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=telegram-bot

[Install]
WantedBy=multi-user.target
```

2. **Create bot user:**

```bash
sudo adduser --system --group --home /opt/telegram-bot botuser
sudo mkdir -p /opt/telegram-bot
sudo chown botuser:botuser /opt/telegram-bot
```

3. **Deploy bot files:**

```bash
# Transfer files to /opt/telegram-bot
rsync -avz --exclude '.git' --exclude 'venv' ./ botuser@vps:/opt/telegram-bot/
```

4. **Install dependencies:**

```bash
sudo -u botuser python3 -m pip install --user -r /opt/telegram-bot/requirements.txt
```

5. **Enable and start service:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

6. **Check status:**

```bash
sudo systemctl status telegram-bot
sudo journalctl -u telegram-bot -f  # View logs
```

#### Systemd vs Docker Comparison

| Feature               | Docker                   | Systemd                      |
| --------------------- | ------------------------ | ---------------------------- |
| **Isolation**         | Full container isolation | Process-level                |
| **Resource Overhead** | ~50-100 MB               | ~10-20 MB                    |
| **Setup Complexity**  | Automated via CLI        | Manual configuration         |
| **Portability**       | High (works anywhere)    | Medium (OS-specific)         |
| **Updates**           | Easy (rebuild image)     | Manual (restart service)     |
| **Health Checks**     | Built-in                 | Manual setup                 |
| **Best For**          | Production, scalability  | Simple setups, low resources |

**Recommendation:** Use Docker for production deployments. Use Systemd only if you have specific requirements or constraints.

## Advanced Usage

### Custom Dockerfile

If you need custom Docker configuration, create `Dockerfile` in your project root. It will be used instead of the template.

**Example custom Dockerfile:**

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY . .

# Run bot
CMD ["python", "bot.py"]
```

### Multiple Bots on Same VPS

Deploy multiple bots to the same VPS efficiently:

**Step 1: Create separate configs for each bot**

```bash
# Bot 1
cd bot1/
telegram-bot-stack deploy init --bot-name bot1
# Creates deploy.yaml

# Bot 2
cd bot2/
telegram-bot-stack deploy init --bot-name bot2
# Creates deploy.yaml
```

**Step 2: Deploy each bot**

```bash
# Deploy bot1
cd bot1/
export BOT_TOKEN="bot1-token"
telegram-bot-stack deploy up

# Deploy bot2
cd bot2/
export BOT_TOKEN="bot2-token"
telegram-bot-stack deploy up
```

**Step 3: Manage bots independently**

```bash
# Check status of bot1
cd bot1/
telegram-bot-stack deploy status

# Update bot2
cd bot2/
telegram-bot-stack deploy update

# View logs of bot1
cd bot1/
telegram-bot-stack deploy logs
```

**Resource allocation:** Each bot runs in its own container with separate resource limits. Ensure your VPS has enough resources (RAM, CPU) for all bots.

### Version Management and Rollback Strategies

Every deployment is automatically versioned and tracked. This enables safe rollbacks and deployment auditing.

**How Version Tracking Works:**

1. **Automatic Versioning:**

   - Each deployment creates a new Docker image tag: `botname:v{timestamp}-{git-commit}`
   - Example: `mybot:v1706281800-abc123f`
   - Timestamp allows sorting by deployment time
   - Git commit links deployment to code version

2. **Version History:**

   - Last 5 deployments are kept by default
   - Each version tracks: timestamp, git commit, status
   - Old Docker images are automatically cleaned up

3. **Version States:**
   - **Active** - Currently running version
   - **Old** - Previous successful deployments
   - **Failed** - Deployments that didn't complete
   - **Rolled Back** - Reverted deployments

**Rollback Strategies:**

**1. Quick Rollback (Emergency Fix):**

```bash
# Instant rollback to previous version
telegram-bot-stack deploy rollback --yes

# No questions asked, minimal downtime
# Creates backup automatically before rollback
```

**2. Selective Rollback (Choose Version):**

```bash
# Step 1: View deployment history
telegram-bot-stack deploy history

# Output:
# Status     Docker Tag                      Git Commit  Deployed At
# ✅ Active   mybot:v1706281800-abc123f      abc123f     2025-01-26 14:30:00
# 📦 Old     mybot:v1706278200-def456a      def456a     2025-01-26 13:30:00
# 📦 Old     mybot:v1706274600-789bcde      789bcde     2025-01-26 12:30:00

# Step 2: Rollback to specific version
telegram-bot-stack deploy rollback --version mybot:v1706274600-789bcde
```

**3. Canary Deployment (Test Before Full Rollout):**

```bash
# Deploy to staging first
cd staging-bot/
telegram-bot-stack deploy update

# Test thoroughly
# If issues found, rollback immediately
telegram-bot-stack deploy rollback

# If OK, deploy to production
cd ../production-bot/
telegram-bot-stack deploy update
```

**Best Practices:**

1. **Always keep automatic backups enabled:**

   ```yaml
   # deploy.yaml
   backup:
     enabled: true
     auto_backup_before_update: true
   ```

2. **Test rollback process regularly:**

   ```bash
   # Practice rollback in staging environment
   telegram-bot-stack deploy update
   telegram-bot-stack deploy rollback
   telegram-bot-stack deploy update  # Re-deploy
   ```

3. **Monitor deployments:**

   ```bash
   # After deployment, watch logs
   telegram-bot-stack deploy logs --follow

   # If issues appear, rollback immediately
   telegram-bot-stack deploy rollback --yes
   ```

4. **Keep deployment notes:**

   ```bash
   # Use git tags to mark deployments
   git tag -a v1.2.3 -m "Fixed user authentication bug"
   git push --tags

   # View history with git info
   telegram-bot-stack deploy history
   git log --oneline
   ```

**Rollback Limitations:**

- ⚠️ **Database Schema Changes:** If update modified database schema, rollback may fail
- ⚠️ **Old Images Deleted:** Can only rollback to kept versions (last 5 by default)
- ⚠️ **Data Format Changes:** If data format changed, old version may not read new data

**Advanced: Manual Version Management:**

```bash
# SSH to VPS
ssh root@your-vps-ip

# List all Docker images
docker images mybot

# Manually tag specific image as latest
docker tag mybot:v1706274600-789bcde mybot:latest

# Restart with that image
cd /opt/mybot
docker compose restart
```

### Custom Domain with HTTPS

Add custom domain to your bot for webhook support:

**Step 1: Point domain to VPS**

1. Go to your domain registrar
2. Add A record: `bot.yourdomain.com` → `your-vps-ip`
3. Wait for DNS propagation (5-60 minutes)

**Step 2: Install Nginx and Certbot**

```bash
# SSH to VPS
ssh root@your-vps-ip

# Install Nginx
apt update
apt install -y nginx certbot python3-certbot-nginx

# Get SSL certificate
certbot --nginx -d bot.yourdomain.com
```

**Step 3: Configure Nginx reverse proxy**

Create `/etc/nginx/sites-available/telegram-bot`:

```nginx
server {
    listen 80;
    server_name bot.yourdomain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Step 4: Enable site and reload**

```bash
ln -s /etc/nginx/sites-available/telegram-bot /etc/nginx/sites-enabled/
nginx -t  # Test configuration
systemctl reload nginx
```

**Step 5: Configure bot for webhooks**

Update your bot code to use webhooks:

```python
from telegram_bot_stack import BotBase

bot = BotBase(token="your-token")

# Set webhook
bot.set_webhook(url="https://bot.yourdomain.com/webhook")

# Your bot handlers...
```

### PostgreSQL Database Setup

Deploy bot with PostgreSQL for production-grade data storage:

**Step 1: Update deploy.yaml**

```yaml
storage:
  backend: "postgres"
  postgres_host: "postgres" # Docker service name
  postgres_port: 5432
  postgres_db: "bot_db"
  postgres_user: "bot"
  postgres_password_env: "DB_PASSWORD"
```

**Step 2: Create docker-compose.yml with PostgreSQL**

Create `docker-compose.override.yml` in your project:

```yaml
version: "3.8"

services:
  postgres:
    image: postgres:15-alpine
    container_name: ${BOT_NAME}-postgres
    environment:
      POSTGRES_DB: bot_db
      POSTGRES_USER: bot
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - bot-network
    restart: always

  bot:
    depends_on:
      - postgres
    environment:
      - DB_PASSWORD=${DB_PASSWORD}

volumes:
  postgres_data:

networks:
  bot-network:
    external: true
    name: ${BOT_NAME}-network
```

**Step 3: Set database password**

```bash
export DB_PASSWORD="secure-password-here"
```

**Step 4: Deploy**

```bash
telegram-bot-stack deploy up
```

**Step 5: Initialize database**

The bot will automatically create tables on first run. To verify:

```bash
# SSH to VPS
ssh root@your-vps-ip

# Connect to PostgreSQL
docker exec -it bot-name-postgres psql -U bot -d bot_db

# List tables
\dt
```

### Redis Caching Setup

Add Redis for session caching and improved performance:

**Step 1: Add Redis to docker-compose.override.yml**

```yaml
services:
  redis:
    image: redis:7-alpine
    container_name: ${BOT_NAME}-redis
    volumes:
      - redis_data:/data
    networks:
      - bot-network
    restart: always
    command: redis-server --appendonly yes

  bot:
    depends_on:
      - redis
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379

volumes:
  redis_data:
```

**Step 2: Update bot code to use Redis**

```python
from telegram_bot_stack import BotBase
from telegram_bot_stack.storage import get_storage

# Use Redis storage
storage = get_storage("redis", host="redis", port=6379)
bot = BotBase(token="your-token", storage=storage)
```

**Step 3: Deploy**

```bash
telegram-bot-stack deploy up
```

### CI/CD Integration

Automate deployments with GitHub Actions:

**Create `.github/workflows/deploy.yml`:**

```yaml
name: Deploy to VPS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install telegram-bot-stack
        run: pip install telegram-bot-stack

      - name: Deploy to VPS
        env:
          BOT_TOKEN: ${{ secrets.BOT_TOKEN }}
        run: |
          telegram-bot-stack deploy up
```

**Setup secrets in GitHub:**

1. Go to repository → Settings → Secrets
2. Add `BOT_TOKEN` secret
3. Push to `main` branch triggers deployment

### Backup and Restore

Automated backup and restore system for protecting your bot data.

#### Create Backup

```bash
# Create a backup of bot data
telegram-bot-stack deploy backup
```

This will:

- Stop bot container temporarily (if running)
- Backup data directory (`/opt/{bot_name}/data/`)
- Backup `.env` file (if exists)
- Backup encrypted secrets file (if exists)
- Create tarball: `backup-{timestamp}.tar.gz`
- Store in `/opt/{bot_name}/backups/`
- Restart bot container
- Clean up old backups (based on retention policy)

**Example output:**

```
📦 Creating backup...

✓ Stopped bot container
✓ Backed up data directory (2.3 MB)
✓ Backed up .env file
✓ Created backup: backup-20250126-143022.tar.gz
✓ Started bot container

✅ Backup created successfully!
Location: /opt/my-bot/backups/backup-20250126-143022.tar.gz
```

#### List Backups

```bash
# List all available backups
telegram-bot-stack deploy backup list
```

Shows all backups with:

- Filename
- Size
- Creation date

**Example output:**

```
📦 Available Backups

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Filename                            ┃ Size  ┃ Date                 ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ backup-20250126-143022.tar.gz      │ 2.3M  │ 2025-01-26 14:30:22  │
│ backup-20250125-120000.tar.gz      │ 1.5M  │ 2025-01-25 12:00:00  │
└────────────────────────────────────┴───────┴──────────────────────┘
```

#### Restore from Backup

```bash
# Restore from backup (with confirmation)
telegram-bot-stack deploy restore backup-20250126-143022.tar.gz

# Restore without confirmation prompt
telegram-bot-stack deploy restore backup-20250126-143022.tar.gz --yes
```

This will:

- Stop bot container
- Extract backup tarball
- Restore data directory
- Restore `.env` file
- Restore encrypted secrets file
- Start bot container
- Verify restoration

**⚠️ Warning:** This will replace current bot data! Make sure you have a recent backup before restoring.

#### Download Backup

```bash
# Download backup to local machine
telegram-bot-stack deploy backup download backup-20250126-143022.tar.gz

# Download to specific directory
telegram-bot-stack deploy backup download backup-20250126-143022.tar.gz --output ./backups/
```

#### Auto-Backup Configuration

Backups are automatically created before critical operations:

**Before update:**

```bash
# Auto-backup before update (enabled by default)
telegram-bot-stack deploy update

# Skip auto-backup
telegram-bot-stack deploy update --no-backup

# Force backup even if auto-backup disabled
telegram-bot-stack deploy update --backup
```

**Before cleanup:**

```bash
# Auto-backup before cleanup (enabled by default)
telegram-bot-stack deploy down --cleanup

# Skip auto-backup
telegram-bot-stack deploy down --cleanup --no-backup
```

#### Backup Configuration

Configure backup settings in `deploy.yaml`:

```yaml
backup:
  enabled: true # Enable backup system
  auto_backup_before_update: true # Auto-backup before updates
  auto_backup_before_cleanup: true # Auto-backup before cleanup
  retention_days: 7 # Keep backups for 7 days
  max_backups: 10 # Maximum number of backups to keep
```

**Retention Policy:**

- Backups older than `retention_days` are automatically deleted
- If more than `max_backups` exist, oldest backups are deleted first
- Cleanup runs automatically after each backup creation

#### Backup Contents

Each backup includes:

- **Data directory** (`/opt/{bot_name}/data/`) - All bot data (JSON/SQL files)
- **Environment file** (`.env`) - Environment variables
- **Encrypted secrets** (`.secrets.env.encrypted`) - Encrypted secrets file

**Note:** Secrets are included in encrypted form only. The encryption key is stored in `deploy.yaml` (local only, not transferred to VPS).

#### Best Practices

1. **Regular Backups:** Create backups before major updates or changes
2. **Test Restores:** Periodically test restore process to ensure backups work
3. **Offsite Storage:** Download important backups to local machine or cloud storage
4. **Retention Policy:** Adjust `retention_days` and `max_backups` based on your needs
5. **Before Cleanup:** Always backup before running `deploy down --cleanup`

#### Manual Backup (Alternative)

If you prefer manual backup via SSH:

```bash
# SSH to VPS
ssh root@your-vps-ip

# Create backup manually
cd /opt/bot-name
tar -czf backups/manual-backup-$(date +%Y%m%d).tar.gz data/ .env .secrets.env.encrypted

# Download backup
scp root@your-vps-ip:/opt/bot-name/backups/manual-backup-*.tar.gz ./
```

### Health Monitoring

The deployed bot includes automatic health checks and recovery:

- **Automatic health checks** every 30 seconds
- **Auto-restart on failure** (up to 3 retries within 5 minutes)
- **Process monitoring** - detects if bot process crashes
- **Container monitoring** - detects if container stops

#### Check Bot Health

View comprehensive health status:

```bash
telegram-bot-stack deploy health
```

Shows:

- **Container Status:** Running, stopped, or restarting
- **Health Status:** Healthy, unhealthy, or starting
- **Uptime:** How long bot has been running
- **Restart Count:** Number of automatic restarts
- **Auto-Recovery:** Whether automatic restart is enabled

**Example output:**

```
🏥 Bot Health Check

┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Metric        ┃ Status                   ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Container     │ ✓ Running                │
│ Health Status │ ✓ Healthy                │
│ Uptime        │ 2d 5h 30m                │
│ Restarts      │ 0 restarts               │
└───────────────┴──────────────────────────┘

Automatic Recovery:
  ✓ Enabled - Container will restart on failure
  Max retries: 3 within 5 minutes
```

#### Check Recent Errors

View recent errors from bot logs:

```bash
telegram-bot-stack deploy health --errors
```

This shows only ERROR, EXCEPTION, FAILED, and CRITICAL log entries, making it easy to diagnose issues.

#### Health Check Configuration

Health checks are configured in `docker-compose.yml`:

```yaml
healthcheck:
  test: ["CMD", "pgrep", "-f", "python.*bot"]
  interval: 30s # Check every 30 seconds
  timeout: 10s # Timeout after 10 seconds
  retries: 3 # Mark unhealthy after 3 failed checks
  start_period: 30s # Grace period for bot startup
```

To customize health check settings, edit your `docker-compose.yml` after deployment.

#### Automatic Recovery

Automatic restart is enabled by default in `docker-compose.yml`:

```yaml
restart: always # Always restart on failure
```

**Restart policies:**

- `always` - Always restart (recommended for production)
- `unless-stopped` - Restart unless manually stopped
- `on-failure` - Restart only on error exit
- `no` - Never restart automatically

#### Health Monitoring Best Practices

1. **Regular Health Checks:**

   ```bash
   # Check health daily
   telegram-bot-stack deploy health
   ```

2. **Monitor Restarts:**

   - If restart count > 3, investigate the issue
   - Check errors: `telegram-bot-stack deploy health --errors`

3. **Set Up Alerts:**

   - Use external monitoring (e.g., UptimeRobot, Pingdom)
   - Monitor bot's Telegram status via [@BotFather](https://t.me/BotFather)

4. **Log Monitoring:**

   - Review logs regularly: `telegram-bot-stack deploy logs`
   - Look for patterns in errors

5. **Resource Monitoring:**
   - Check resource usage: `telegram-bot-stack deploy status`
   - Ensure bot has enough memory/CPU

#### Troubleshooting Health Issues

**Bot marked as unhealthy:**

```bash
# Check what's wrong
telegram-bot-stack deploy health --errors

# View full logs
telegram-bot-stack deploy logs --tail 100

# Restart if needed
telegram-bot-stack deploy up
```

**Multiple restarts detected:**

```bash
# View deployment history
telegram-bot-stack deploy history

# Rollback to previous version
telegram-bot-stack deploy rollback
```

**Container not running:**

```bash
# Check status
telegram-bot-stack deploy status

# View logs for crash reason
telegram-bot-stack deploy logs

# Restart bot
telegram-bot-stack deploy up
```

### Log Rotation

Logs are automatically rotated to prevent disk space issues:

- Max log size: 5 MB (configurable)
- Max log files: 5 (configurable)
- Old logs are compressed

## Troubleshooting

This comprehensive guide covers common deployment issues and their solutions. Each issue includes symptoms, diagnosis commands, and step-by-step fixes.

### Quick Diagnosis Commands

Before troubleshooting specific issues, use these commands to gather information:

```bash
# Check bot health
telegram-bot-stack deploy health

# View recent logs
telegram-bot-stack deploy logs --tail 100

# Check deployment status
telegram-bot-stack deploy status

# View recent errors only
telegram-bot-stack deploy health --errors

# View deployment history
telegram-bot-stack deploy history
```

---

## SSH Connection Issues

### 1. SSH Connection Failed

**Symptoms:**

- Cannot connect to VPS
- "Connection timed out" error
- "Permission denied" error

**Diagnosis:**

```bash
# Test SSH connection with verbose output
ssh -v root@your-vps-ip

# Check if SSH key exists
ls -la ~/.ssh/id_rsa

# Verify SSH key permissions
ls -l ~/.ssh/id_rsa
```

**Solutions:**

**1.1 Fix SSH Key Permissions:**

```bash
# SSH key must have restricted permissions
chmod 600 ~/.ssh/id_rsa
chmod 700 ~/.ssh

# Try connecting again
ssh root@your-vps-ip
```

**1.2 Wrong SSH Key Path:**

```bash
# Check which key is being used
ssh -v root@your-vps-ip 2>&1 | grep "identity file"

# Specify correct key explicitly
ssh -i ~/.ssh/your-key root@your-vps-ip

# Update deploy.yaml with correct path
# vps:
#   ssh_key: "~/.ssh/your-key"
```

**1.3 Firewall Blocking SSH:**

```bash
# Check if port 22 is open (from local machine)
nc -zv your-vps-ip 22

# Contact VPS provider to:
# - Open port 22 in firewall
# - Check if SSH is enabled
# - Verify VPS is running
```

**1.4 Host Key Verification Failed:**

```bash
# Remove old host key
ssh-keygen -R your-vps-ip

# Or edit ~/.ssh/known_hosts and remove the line for your VPS

# Try connecting again (will ask to accept new key)
ssh root@your-vps-ip
```

---

## Bot Already Running/Deployed

### 1.5. Bot Already Running Locally (Dev Mode)

**Symptoms:**

- Error: "Bot is already running (PID: ...)"
- Cannot start dev mode
- Port already in use

**Diagnosis:**

```bash
# Check if process is running
ps aux | grep python | grep bot.py

# Check lock file
ls -la .bot.lock
cat .bot.lock
```

**Solutions:**

**1.5.1 Stop Existing Process:**

```bash
# Find process ID from error message
# Example: "Bot is already running (PID: 12345)"

# Kill the process
kill 12345

# Or use force kill if it doesn't respond
kill -9 12345

# Try dev mode again
telegram-bot-stack dev
```

**1.5.2 Use Force Mode:**

```bash
# Automatically kill existing process and start new one
telegram-bot-stack dev --force

# This will:
# - Detect running process
# - Terminate it (SIGTERM)
# - Force kill if needed (SIGKILL)
# - Start new instance
```

**1.5.3 Use Existing Dev Session:**

```bash
# If another terminal is running dev mode, just use that terminal
# Don't start multiple dev instances - they'll conflict

# Check which terminal has the running instance
ps aux | grep "telegram-bot-stack dev"
```

**1.5.4 Clean Up Stale Lock:**

```bash
# If process is dead but lock exists, remove it manually
rm .bot.lock

# Then try again
telegram-bot-stack dev
```

### 1.6. Bot Already Deployed on VPS

**Symptoms:**

- Warning: "Bot is already deployed and running"
- Deploy up shows existing container
- Asked for confirmation to redeploy

**Diagnosis:**

```bash
# Check deployment status
telegram-bot-stack deploy status

# Check bot health
telegram-bot-stack deploy health

# View deployment history
telegram-bot-stack deploy history
```

**Solutions:**

**1.6.1 Update Existing Deployment:**

```bash
# If bot is running and you want to update code
telegram-bot-stack deploy update

# This will:
# - Create automatic backup
# - Transfer new code
# - Rebuild container
# - Restart with new code
# - Keep data intact
```

**1.6.2 Force Redeploy:**

```bash
# Force complete redeployment (stops existing, deploys fresh)
telegram-bot-stack deploy up --force

# This will:
# - Stop existing container
# - Remove old container
# - Deploy fresh
# - ⚠️  Warning: Use update instead to preserve data
```

**1.6.3 Stop and Redeploy:**

```bash
# Manual approach: stop first, then deploy
telegram-bot-stack deploy down
telegram-bot-stack deploy up

# Or with cleanup (removes container and image)
telegram-bot-stack deploy down --cleanup
telegram-bot-stack deploy up
```

**1.6.4 Check if Update is Needed:**

```bash
# View current deployment version
telegram-bot-stack deploy status

# Check deployment history
telegram-bot-stack deploy history

# If already running latest version, no action needed
# Bot will show message: "Bot is already running (Container: my-bot (running, X hours uptime))"
```

### 1.7. Stale/Zombie Containers

**Symptoms:**

- Container exists but not running
- "Found stale container" message
- Old containers not cleaned up

**Diagnosis:**

```bash
# Check all containers (including stopped)
ssh root@your-vps-ip "docker ps -a"

# Check for exited containers
ssh root@your-vps-ip "docker ps -a --filter status=exited"

# Check container status
telegram-bot-stack deploy status
```

**Solutions:**

**1.7.1 Automatic Cleanup:**

```bash
# Deploy commands automatically clean up stale containers
telegram-bot-stack deploy up

# You'll see:
# "⚠️  Found stale container 'my-bot' (exited 3 hours ago)"
# "Auto-cleaning stale container... ✅ Done"
```

**1.7.2 Manual Cleanup:**

```bash
# Remove stopped containers manually
ssh root@your-vps-ip "docker rm bot-name"

# Remove all stopped containers
ssh root@your-vps-ip "docker container prune -f"

# Clean up everything (containers, images, volumes)
ssh root@your-vps-ip "docker system prune -a -f"
```

**1.7.3 Restart Stuck Container:**

```bash
# If container exists but isn't responding
ssh root@your-vps-ip "docker restart bot-name"

# Or stop and start
ssh root@your-vps-ip "docker stop bot-name && docker start bot-name"
```

### 1.8. Multiple Bot Instances Conflict

**Symptoms:**

- Bot running both locally and on VPS
- Webhook errors ("conflict: terminated by other getUpdates request")
- Messages processed twice
- Unexpected behavior

**Diagnosis:**

```bash
# Check local dev mode
ps aux | grep "telegram-bot-stack dev"

# Check VPS deployment
telegram-bot-stack deploy status

# Check Telegram bot status via curl
curl "https://api.telegram.org/bot<YOUR_TOKEN>/getMe"
```

**Solutions:**

**1.8.1 Stop Local Instance:**

```bash
# Find and kill local dev process
ps aux | grep bot.py
kill <PID>

# Or use force mode to auto-stop
# (Not recommended - better to stop manually)
```

**1.8.2 Stop VPS Instance:**

```bash
# If testing locally, stop VPS deployment
telegram-bot-stack deploy down

# Later resume VPS deployment
telegram-bot-stack deploy up
```

**1.8.3 Best Practice - Use One Environment:**

```bash
# For development:
telegram-bot-stack deploy down  # Stop VPS
telegram-bot-stack dev          # Run locally

# For production:
# (Stop local dev with Ctrl+C)
telegram-bot-stack deploy up    # Run on VPS
```

**1.8.4 Use Different Tokens:**

```bash
# Development: Use test bot token
export BOT_TOKEN="test-bot-token"
telegram-bot-stack dev

# Production: Use production bot token
telegram-bot-stack deploy secrets set BOT_TOKEN "prod-bot-token"
telegram-bot-stack deploy up
```

---

### 2. SSH Key Not Authorized

**Symptoms:**

- "Permission denied (publickey)" error
- Can connect with password but not with key

**Diagnosis:**

```bash
# Test with password authentication
ssh -o PreferredAuthentications=password root@your-vps-ip

# Check authorized keys on VPS
ssh root@your-vps-ip "cat ~/.ssh/authorized_keys"
```

**Solutions:**

**2.1 Add SSH Key to VPS:**

```bash
# Copy public key to VPS
ssh-copy-id -i ~/.ssh/id_rsa.pub root@your-vps-ip

# Or manually:
cat ~/.ssh/id_rsa.pub | ssh root@your-vps-ip "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"

# Verify permissions on VPS
ssh root@your-vps-ip "chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"
```

**2.2 Wrong Public Key:**

```bash
# Check your public key
cat ~/.ssh/id_rsa.pub

# Check key fingerprint
ssh-keygen -lf ~/.ssh/id_rsa.pub

# Compare with VPS authorized_keys
ssh root@your-vps-ip "ssh-keygen -lf ~/.ssh/authorized_keys"
```

### 3. Connection Timeout

**Symptoms:**

- Connection hangs
- "Operation timed out" after long wait
- Cannot reach VPS at all

**Diagnosis:**

```bash
# Test basic connectivity
ping your-vps-ip

# Check if any port is open
nc -zv your-vps-ip 22

# Trace route to VPS
traceroute your-vps-ip
```

**Solutions:**

**3.1 VPS is Down:**

- Check VPS provider dashboard
- Restart VPS from provider's control panel
- Contact VPS support

**3.2 Firewall Blocking:**

- Configure VPS firewall (allow port 22)
- Check cloud provider security groups
- Temporarily disable local firewall for testing

**3.3 Wrong IP Address:**

```bash
# Verify IP in deploy.yaml
cat deploy.yaml | grep host

# Get correct IP from VPS provider
# Update deploy.yaml with correct IP
```

---

## Docker Issues

### 4. Docker Installation Failed

**Symptoms:**

- Error during `deploy up` when installing Docker
- "Docker installation failed" message
- Cannot install Docker packages

**Diagnosis:**

```bash
# Check if Docker is installed
ssh root@your-vps-ip "docker --version"

# Check OS version
ssh root@your-vps-ip "cat /etc/os-release"

# Check available disk space
ssh root@your-vps-ip "df -h"
```

**Solutions:**

**4.1 Unsupported OS Version:**

```bash
# Upgrade OS or use compatible VPS
# Supported: Ubuntu 20.04+, Debian 11+, CentOS 8+

# For Ubuntu:
ssh root@your-vps-ip "lsb_release -a"
```

**4.2 Insufficient Disk Space:**

```bash
# Clean up disk space
ssh root@your-vps-ip "apt-get clean"
ssh root@your-vps-ip "apt-get autoremove -y"

# Check space again
ssh root@your-vps-ip "df -h"
```

**4.3 Manual Docker Installation:**

See [Docker Setup](#docker-deployment-recommended) section for manual installation steps.

### 5. Docker Daemon Not Running

**Symptoms:**

- "Cannot connect to Docker daemon" error
- Docker commands fail with connection error
- Bot won't start after VPS reboot

**Diagnosis:**

```bash
# Check Docker service status
ssh root@your-vps-ip "systemctl status docker"

# Check if Docker socket exists
ssh root@your-vps-ip "ls -l /var/run/docker.sock"
```

**Solutions:**

**5.1 Start Docker Service:**

```bash
# Start Docker
ssh root@your-vps-ip "systemctl start docker"

# Enable auto-start on boot
ssh root@your-vps-ip "systemctl enable docker"

# Verify it's running
ssh root@your-vps-ip "systemctl status docker"
```

**5.2 Docker Socket Permission Issues:**

```bash
# Add user to docker group
ssh root@your-vps-ip "usermod -aG docker $USER"

# Fix socket permissions
ssh root@your-vps-ip "chmod 666 /var/run/docker.sock"

# Restart Docker
ssh root@your-vps-ip "systemctl restart docker"
```

### 6. Docker Image Build Failed

**Symptoms:**

- "Error during build" message
- "Failed to build Docker image"
- Build hangs at certain step

**Diagnosis:**

```bash
# Check recent logs
telegram-bot-stack deploy logs --tail 100

# Check Docker images
ssh root@your-vps-ip "docker images"

# Check build cache
ssh root@your-vps-ip "docker system df"
```

**Solutions:**

**6.1 Missing Dependencies:**

```bash
# Check requirements.txt exists
ls requirements.txt

# Verify all dependencies are listed
cat requirements.txt

# Add missing packages
echo "missing-package>=1.0.0" >> requirements.txt

# Try deployment again
telegram-bot-stack deploy update
```

**6.2 Network Issues During Build:**

```bash
# Test internet connection on VPS
ssh root@your-vps-ip "ping -c 3 8.8.8.8"

# Try building with no cache
ssh root@your-vps-ip "cd /opt/your-bot && docker compose build --no-cache"
```

**6.3 Disk Space Full:**

```bash
# Check disk space
ssh root@your-vps-ip "df -h"

# Clean Docker cache
ssh root@your-vps-ip "docker system prune -af"

# Remove unused images
ssh root@your-vps-ip "docker image prune -af"
```

### 7. Container Won't Start

**Symptoms:**

- Container status: "Exited (1)" or "Restarting"
- Bot starts then immediately stops
- Health check shows "Not running"

**Diagnosis:**

```bash
# Check bot health
telegram-bot-stack deploy health

# View logs
telegram-bot-stack deploy logs --tail 50

# Check container status
ssh root@your-vps-ip "docker ps -a"

# Inspect container
ssh root@your-vps-ip "docker inspect bot-name"
```

**Solutions:**

**7.1 Check Error Logs:**

```bash
# View detailed logs
telegram-bot-stack deploy logs --tail 200

# Look for specific error messages:
# - "ModuleNotFoundError" → Missing dependency
# - "Unauthorized" → Wrong bot token
# - "Connection refused" → Network/database issue
# - "Permission denied" → File permission issue
```

**7.2 Invalid Bot Token:**

```bash
# Test bot token locally
python3 -c "
import telegram, os
token = 'YOUR_BOT_TOKEN'
bot = telegram.Bot(token=token)
print(bot.get_me())
"

# Update token on VPS
telegram-bot-stack deploy secrets set BOT_TOKEN "your-correct-token"

# Restart bot
telegram-bot-stack deploy up
```

**7.3 Port Already in Use:**

```bash
# Check what's using the port
ssh root@your-vps-ip "netstat -tlnp | grep :8080"

# Stop conflicting service
ssh root@your-vps-ip "docker stop $(docker ps -q --filter 'publish=8080')"

# Or change bot port in docker-compose.yml
```

**7.4 File Permission Issues:**

```bash
# Fix data directory permissions
ssh root@your-vps-ip "cd /opt/your-bot && chown -R 1000:1000 data/ logs/"

# Restart container
telegram-bot-stack deploy up
```

---

## Deployment Failures

### 8. File Transfer Failed

**Symptoms:**

- "Failed to transfer files" error
- rsync errors
- Deployment stuck at "Transferring files"

**Diagnosis:**

```bash
# Test file transfer manually
rsync -avz --dry-run ./ root@vps-ip:/tmp/test/

# Check VPS disk space
ssh root@your-vps-ip "df -h /opt/"

# Test SSH connection
ssh root@your-vps-ip "echo 'Connection OK'"
```

**Solutions:**

**8.1 Disk Space Full on VPS:**

```bash
# Clean up space
ssh root@your-vps-ip "docker system prune -af"
ssh root@your-vps-ip "apt-get clean"

# Check space
ssh root@your-vps-ip "df -h"

# Try deployment again
telegram-bot-stack deploy update
```

**8.2 Large Files Not in .gitignore:**

```bash
# Add large files to .gitignore
echo "*.db" >> .gitignore
echo "data/*.json" >> .gitignore
echo "venv/" >> .gitignore

# Commit changes
git add .gitignore
git commit -m "chore: update .gitignore"

# Deploy again
telegram-bot-stack deploy update
```

**8.3 SSH Connection Unstable:**

```bash
# Use compression for transfer
# Add to deploy.yaml:
# transfer:
#   compression: true
#   retries: 3
```

### 9. Deployment Succeeds But Bot Not Responding

**Symptoms:**

- Deployment completes without errors
- Container is running
- Bot doesn't respond to messages
- No errors in logs

**Diagnosis:**

```bash
# Check bot health
telegram-bot-stack deploy health

# Test bot is alive
ssh root@your-vps-ip "docker exec bot-name python3 -c 'import telegram; print(\"OK\")'"

# Check bot in Telegram
# Send /start to your bot
```

**Solutions:**

**9.1 Bot Token Issues:**

```bash
# Verify bot token is set
ssh root@your-vps-ip "docker exec bot-name env | grep BOT_TOKEN"

# Test bot token
python3 -c "
import telegram
bot = telegram.Bot(token='YOUR_TOKEN')
print(bot.get_me())
"

# Update token if wrong
telegram-bot-stack deploy secrets set BOT_TOKEN "correct-token"
telegram-bot-stack deploy up
```

**9.2 Webhook Issues (If Using Webhooks):**

```bash
# Check webhook status
curl "https://api.telegram.org/botYOUR_TOKEN/getWebhookInfo"

# Delete webhook (if using polling)
curl "https://api.telegram.org/botYOUR_TOKEN/deleteWebhook"

# Restart bot
telegram-bot-stack deploy up
```

**9.3 Firewall Blocking Telegram:**

```bash
# Test Telegram API connectivity
ssh root@your-vps-ip "curl -I https://api.telegram.org"

# Check if bot can reach Telegram
ssh root@your-vps-ip "docker exec bot-name ping -c 3 api.telegram.org"
```

### 10. Update Deployment Failed

**Symptoms:**

- Update fails midway
- Bot stops working after update
- "Deployment failed" error

**Diagnosis:**

```bash
# Check deployment history
telegram-bot-stack deploy history

# Check what's running
ssh root@your-vps-ip "docker ps -a"

# View recent errors
telegram-bot-stack deploy health --errors
```

**Solutions:**

**10.1 Rollback to Previous Version:**

```bash
# Immediate rollback
telegram-bot-stack deploy rollback --yes

# Verify bot is working
telegram-bot-stack deploy health

# Check logs
telegram-bot-stack deploy logs
```

**10.2 Backup Restore:**

```bash
# List available backups
telegram-bot-stack deploy backup list

# Restore from backup
telegram-bot-stack deploy restore backup-20250127-120000.tar.gz
```

**10.3 Manual Recovery:**

```bash
# SSH to VPS
ssh root@your-vps-ip

# Check available images
docker images

# Start previous image manually
docker run -d --name bot-recovery previous-image:tag

# Or rebuild from clean state
cd /opt/your-bot
docker compose down
docker compose up -d --build
```

---

## Runtime Issues

### 11. Bot Crashes Randomly

**Symptoms:**

- Bot works then suddenly stops
- Container restarts frequently
- Health check shows multiple restarts

**Diagnosis:**

```bash
# Check restart count
telegram-bot-stack deploy health

# View crash logs
telegram-bot-stack deploy logs --tail 200

# Check resource usage
ssh root@your-vps-ip "docker stats --no-stream bot-name"
```

**Solutions:**

**11.1 Memory Leak:**

```bash
# Increase memory limit in deploy.yaml
# resources:
#   memory_limit: "512M"  # Increase from 256M

# Restart bot
telegram-bot-stack deploy up

# Monitor memory usage
ssh root@your-vps-ip "watch docker stats bot-name"
```

**11.2 Unhandled Exceptions:**

```bash
# Check for Python errors in logs
telegram-bot-stack deploy health --errors

# Add error handling to bot code
# Wrap handlers in try-except blocks

# Update and redeploy
telegram-bot-stack deploy update
```

**11.3 Resource Limits Too Low:**

```bash
# Check current limits
ssh root@your-vps-ip "docker inspect bot-name | grep -A 5 Memory"

# Adjust in deploy.yaml:
# resources:
#   memory_limit: "512M"
#   memory_reservation: "256M"
#   cpu_limit: "1.0"
#   cpu_reservation: "0.5"

# Redeploy
telegram-bot-stack deploy update
```

### 12. High Memory Usage

**Symptoms:**

- Bot uses more memory over time
- Eventually crashes with OOM error
- System becomes slow

**Diagnosis:**

```bash
# Monitor memory usage
ssh root@your-vps-ip "docker stats bot-name"

# Check memory limit
ssh root@your-vps-ip "docker inspect bot-name | grep Memory"

# View memory-related errors
telegram-bot-stack deploy logs | grep -i "memory\|oom"
```

**Solutions:**

**12.1 Memory Leak in Code:**

```python
# Common causes:
# - Storing too much in memory (use database)
# - Not cleaning up old data
# - Large conversation states

# Fix: Implement proper data cleanup
# Example:
async def cleanup_old_data(context):
    # Clear old conversation data
    for user_id in list(context.user_data.keys()):
        if should_cleanup(user_id):
            del context.user_data[user_id]
```

**12.2 Increase Memory Limit:**

```yaml
# In deploy.yaml
resources:
  memory_limit: "1G" # Increase limit
  memory_reservation: "512M"
```

**12.3 Use External Storage:**

```python
# Instead of storing in memory, use database
# Example: Store conversation state in SQL/Redis
from telegram_bot_stack import SQLStorage

storage = SQLStorage("bot.db")
```

### 13. Bot Response Slow

**Symptoms:**

- Bot takes long time to respond
- Timeout errors
- Users complain about slowness

**Diagnosis:**

```bash
# Check CPU/memory usage
ssh root@your-vps-ip "docker stats bot-name"

# Check network latency
ssh root@your-vps-ip "ping -c 10 api.telegram.org"

# Profile bot code
# Add timing logs to identify slow operations
```

**Solutions:**

**13.1 Optimize Database Queries:**

```python
# Add indexes to frequently queried columns
# Use batch operations instead of loops
# Cache frequently accessed data
```

**13.2 Increase Resources:**

```yaml
# In deploy.yaml
resources:
  cpu_limit: "2.0" # Increase CPU
  memory_limit: "1G"
```

**13.3 Use Async Operations:**

```python
# Use async/await for I/O operations
async def slow_operation():
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()
```

### 14. Rate Limiting Issues

**Symptoms:**

- "Too many requests" errors
- Bot stops responding temporarily
- 429 HTTP errors in logs

**Diagnosis:**

```bash
# Check logs for rate limit errors
telegram-bot-stack deploy logs | grep -i "429\|rate limit\|too many"

# Monitor request frequency
# Add logging to track API calls
```

**Solutions:**

**14.1 Implement Rate Limiting:**

```python
# Use telegram-bot-stack's rate limiting
from telegram_bot_stack import BotBase

class MyBot(BotBase):
    def __init__(self):
        super().__init__(
            rate_limiter={"enabled": True, "calls": 30, "period": 1}
        )
```

**14.2 Batch Updates:**

```python
# Instead of sending many messages one by one
# Batch them together or add delays
import asyncio

async def send_multiple(chat_ids, text):
    for chat_id in chat_ids:
        await bot.send_message(chat_id, text)
        await asyncio.sleep(0.1)  # Small delay between messages
```

**14.3 Use Queues:**

```python
# Implement message queue for high-volume bots
from queue import Queue
import threading

message_queue = Queue()

def process_queue():
    while True:
        chat_id, text = message_queue.get()
        bot.send_message(chat_id, text)
        time.sleep(0.05)  # Rate limit
```

---

## Network and Connectivity Issues

### 15. Cannot Reach Telegram API

**Symptoms:**

- "Connection refused" errors
- "Unable to connect to api.telegram.org"
- Bot works locally but not on VPS

**Diagnosis:**

```bash
# Test Telegram API connectivity
ssh root@your-vps-ip "curl -I https://api.telegram.org"

# Check DNS resolution
ssh root@your-vps-ip "nslookup api.telegram.org"

# Test from within container
ssh root@your-vps-ip "docker exec bot-name ping -c 3 api.telegram.org"
```

**Solutions:**

**15.1 VPS Firewall Blocking:**

```bash
# Check iptables rules
ssh root@your-vps-ip "iptables -L -n"

# Allow outbound HTTPS
ssh root@your-vps-ip "iptables -A OUTPUT -p tcp --dport 443 -j ACCEPT"

# Or configure cloud provider firewall/security groups
```

**15.2 DNS Issues:**

```bash
# Add Google DNS to container
# In docker-compose.yml:
# dns:
#   - 8.8.8.8
#   - 8.8.4.4

# Redeploy
telegram-bot-stack deploy update
```

**15.3 Proxy Required:**

```python
# Configure proxy in bot code
from telegram.ext import Application

application = (
    Application.builder()
    .token(TOKEN)
    .proxy_url("http://proxy:port")
    .build()
)
```

### 16. Webhook Not Working

**Symptoms:**

- Bot doesn't respond to messages
- Webhook URL returns errors
- SSL certificate errors

**Diagnosis:**

```bash
# Check webhook info
curl "https://api.telegram.org/botYOUR_TOKEN/getWebhookInfo"

# Test webhook URL
curl -I https://your-domain.com/webhook

# Check SSL certificate
curl -v https://your-domain.com/webhook 2>&1 | grep -i ssl
```

**Solutions:**

**16.1 Invalid SSL Certificate:**

```bash
# Use Let's Encrypt for free SSL
# Install certbot
apt-get install certbot

# Get certificate
certbot certonly --standalone -d your-domain.com

# Configure in bot
# Set webhook with certificate
```

**16.2 Webhook URL Not Accessible:**

```bash
# Ensure port 443 is open
ssh root@your-vps-ip "netstat -tlnp | grep :443"

# Check nginx/reverse proxy configuration
# Make sure webhook path is routed correctly
```

**16.3 Switch to Polling:**

```python
# If webhooks are problematic, use polling
# In bot code:
application.run_polling()

# Instead of:
# application.run_webhook()
```

### 17. Port Already in Use

**Symptoms:**

- "Address already in use" error
- Cannot bind to port
- Container fails to start

**Diagnosis:**

```bash
# Check what's using the port
ssh root@your-vps-ip "netstat -tlnp | grep :8080"
ssh root@your-vps-ip "lsof -i :8080"

# Check Docker port mappings
ssh root@your-vps-ip "docker ps --format '{{.Names}}: {{.Ports}}'"
```

**Solutions:**

**17.1 Stop Conflicting Container:**

```bash
# Find and stop container using the port
ssh root@your-vps-ip "docker stop \$(docker ps -q --filter 'publish=8080')"

# Start your bot
telegram-bot-stack deploy up
```

**17.2 Change Bot Port:**

```yaml
# In docker-compose.yml
ports:
  - "8081:8080" # Use different external port

# Or remove port mapping if not needed (for polling bots)
```

**17.3 Kill Process Using Port:**

```bash
# Kill process (use with caution)
ssh root@your-vps-ip "kill \$(lsof -t -i:8080)"

# Restart bot
telegram-bot-stack deploy up
```

---

## Database and Storage Issues

### 18. Database Connection Failed

**Symptoms:**

- "Could not connect to database" errors
- Bot crashes when accessing data
- SQL/database errors in logs

**Diagnosis:**

```bash
# Check if database file exists
ssh root@your-vps-ip "ls -la /opt/your-bot/data/bot.db"

# Check file permissions
ssh root@your-vps-ip "ls -l /opt/your-bot/data/"

# Test database connection
ssh root@your-vps-ip "docker exec bot-name python3 -c 'import sqlite3; conn=sqlite3.connect(\"data/bot.db\"); print(\"OK\")'"
```

**Solutions:**

**18.1 Database File Missing:**

```bash
# Initialize database
ssh root@your-vps-ip "cd /opt/your-bot && docker exec bot-name python3 -c 'from storage import init_db; init_db()'"

# Or restore from backup
telegram-bot-stack deploy restore backup-*.tar.gz
```

**18.2 Permission Issues:**

```bash
# Fix permissions
ssh root@your-vps-ip "cd /opt/your-bot && chown -R 1000:1000 data/"

# Ensure data directory is writable
ssh root@your-vps-ip "chmod 755 /opt/your-bot/data"
```

**18.3 Database Locked:**

```bash
# Check for multiple processes accessing database
ssh root@your-vps-ip "docker ps | grep bot"

# Stop duplicate containers
ssh root@your-vps-ip "docker stop \$(docker ps -q --filter name=bot)"

# Start only one instance
telegram-bot-stack deploy up
```

### 19. Data Loss After Update

**Symptoms:**

- User data disappeared after update
- Bot "forgets" previous conversations
- Empty database after deployment

**Diagnosis:**

```bash
# Check if data volume is mounted
ssh root@your-vps-ip "docker inspect bot-name | grep -A 10 Mounts"

# Check data directory
ssh root@your-vps-ip "ls -la /opt/your-bot/data/"

# List available backups
telegram-bot-stack deploy backup list
```

**Solutions:**

**19.1 Restore from Backup:**

```bash
# List backups
telegram-bot-stack deploy backup list

# Restore latest backup
telegram-bot-stack deploy restore backup-20250127-120000.tar.gz

# Verify data is restored
telegram-bot-stack deploy logs
```

**19.2 Fix Volume Mounting:**

```yaml
# In docker-compose.yml, ensure volumes are correct:
volumes:
  - ./data:/app/data:rw  # Must be read-write
  - ./logs:/app/logs:rw

# Redeploy
telegram-bot-stack deploy update
```

**19.3 Enable Automatic Backups:**

```yaml
# In deploy.yaml
backup:
  enabled: true
  auto_backup_before_update: true
  retention_days: 7
  max_backups: 10
```

### 20. Storage Full

**Symptoms:**

- "No space left on device" errors
- Bot crashes randomly
- Cannot write to database

**Diagnosis:**

```bash
# Check disk usage
ssh root@your-vps-ip "df -h"

# Check bot data size
ssh root@your-vps-ip "du -sh /opt/your-bot/data/"

# Find large files
ssh root@your-vps-ip "du -sh /opt/your-bot/* | sort -h"
```

**Solutions:**

**20.1 Clean Old Logs:**

```bash
# Remove old logs
ssh root@your-vps-ip "cd /opt/your-bot/logs && rm -f *.log.gz"

# Or configure log rotation in deploy.yaml:
# logging:
#   max_size: "5m"
#   max_files: "3"
```

**20.2 Clean Docker Resources:**

```bash
# Remove unused Docker resources
ssh root@your-vps-ip "docker system prune -af"

# Remove old images
ssh root@your-vps-ip "docker image prune -af"

# Check space freed
ssh root@your-vps-ip "df -h"
```

**20.3 Archive Old Data:**

```bash
# Archive and compress old data
ssh root@your-vps-ip "cd /opt/your-bot/data && tar -czf old-data.tar.gz *.old"

# Download archive locally
scp root@your-vps-ip:/opt/your-bot/data/old-data.tar.gz ./

# Remove old data from VPS
ssh root@your-vps-ip "cd /opt/your-bot/data && rm *.old old-data.tar.gz"
```

**20.4 Upgrade VPS:**

- Upgrade to VPS plan with more storage
- Or add additional volume/disk

---

## Performance Issues

### 21. Deployment Takes Too Long

**Symptoms:**

- Deployment hangs at certain steps
- File transfer very slow
- Build takes 10+ minutes

**Diagnosis:**

```bash
# Test network speed to VPS
ssh root@your-vps-ip "curl -o /dev/null http://speedtest.tele2.net/100MB.zip"

# Check VPS CPU/memory during deployment
ssh root@your-vps-ip "top"

# Check disk I/O
ssh root@your-vps-ip "iostat -x 2 5"
```

**Solutions:**

**21.1 Slow Network:**

```bash
# Use compression for file transfer
# Already enabled by default in rsync

# Consider smaller deployments (exclude unnecessary files)
echo "tests/" >> .gitignore
echo "docs/" >> .gitignore
```

**21.2 VPS Performance Issues:**

```bash
# Upgrade VPS plan for better CPU/disk
# Or optimize build process

# Enable build cache in docker-compose.yml
# Add: cache_from: ["${DOCKER_IMAGE}"]
```

**21.3 Large Dependencies:**

```bash
# Optimize requirements.txt
# Remove unused packages
# Pin versions to avoid resolving latest

# Example:
# python-telegram-bot==22.5  # Instead of >=22.0
```

### 22. Out of Memory Errors

**Symptoms:**

- "OOMKilled" in container status
- Bot crashes with memory errors
- System becomes unresponsive

**Diagnosis:**

```bash
# Check memory usage
ssh root@your-vps-ip "free -h"

# Check container memory
ssh root@your-vps-ip "docker stats bot-name --no-stream"

# Check memory limit
ssh root@your-vps-ip "docker inspect bot-name | grep Memory"
```

**Solutions:**

**22.1 Increase Memory Limit:**

```yaml
# In deploy.yaml
resources:
  memory_limit: "1G"  # Increase from 256M
  memory_reservation: "512M"

# Redeploy
telegram-bot-stack deploy update
```

**22.2 Optimize Bot Code:**

```python
# Common memory issues:
# 1. Storing too much user data
# 2. Large file processing in memory
# 3. No data cleanup

# Fix: Implement cleanup
def cleanup_old_data():
    # Remove old user data
    # Clear expired cache
    # Cleanup temporary files
    pass
```

**22.3 Upgrade VPS:**

- Switch to VPS plan with more RAM
- Current plan insufficient for bot's needs

### 23. High CPU Usage

**Symptoms:**

- Bot becomes slow
- CPU constantly at 100%
- VPS provider throttles resources

**Diagnosis:**

```bash
# Check CPU usage
ssh root@your-vps-ip "docker stats bot-name --no-stream"

# Profile bot code
# Add timing logs to identify slow operations

# Check for infinite loops
telegram-bot-stack deploy logs | grep -i "loop\|recursion"
```

**Solutions:**

**23.1 Optimize Code:**

```python
# Common CPU issues:
# - Inefficient loops
# - Heavy computations
# - Blocking operations

# Use async/await for I/O
# Cache expensive operations
# Use background tasks for heavy work
```

**23.2 Increase CPU Limit:**

```yaml
# In deploy.yaml
resources:
  cpu_limit: "2.0" # Increase from 0.5
```

**23.3 Offload Heavy Tasks:**

```python
# Use external services for:
# - Image processing
# - File conversions
# - Heavy computations

# Or use background workers
from celery import Celery
```

---

## Miscellaneous Issues

### 24. Secrets Not Loading

**Symptoms:**

- Bot token not found
- Environment variables missing
- "BOT_TOKEN is not set" error

**Diagnosis:**

```bash
# Check if secrets file exists
ssh root@your-vps-ip "ls -la /opt/your-bot/.secrets.env.encrypted"

# Check environment variables in container
ssh root@your-vps-ip "docker exec bot-name env | grep BOT"

# Verify secrets are set
telegram-bot-stack deploy secrets list
```

**Solutions:**

**24.1 Set Secrets:**

```bash
# Set bot token
telegram-bot-stack deploy secrets set BOT_TOKEN "your-token-here"

# Set other secrets
telegram-bot-stack deploy secrets set DATABASE_URL "postgres://..."

# Redeploy
telegram-bot-stack deploy up
```

**24.2 Check Encryption Key:**

```bash
# Verify encryption key in deploy.yaml
cat deploy.yaml | grep encryption_key

# If missing, regenerate:
# telegram-bot-stack deploy init
```

**24.3 Manual Fix:**

```bash
# SSH to VPS
ssh root@your-vps-ip

# Create .env file manually (temporary fix)
cd /opt/your-bot
echo "BOT_TOKEN=your-token" > .env

# Restart bot
docker compose restart
```

### 25. Time Zone Issues

**Symptoms:**

- Scheduled tasks run at wrong time
- Timestamps are incorrect
- Time-based features don't work

**Diagnosis:**

```bash
# Check container timezone
ssh root@your-vps-ip "docker exec bot-name date"

# Check VPS timezone
ssh root@your-vps-ip "timedatectl"

# Check timezone in bot logs
telegram-bot-stack deploy logs | grep -i time
```

**Solutions:**

**25.1 Set Timezone in Deploy Config:**

```yaml
# In deploy.yaml
environment:
  timezone: "Europe/London"  # Your timezone

# Or in docker-compose.yml:
environment:
  - TZ=Europe/London
```

**25.2 Set Timezone in Bot Code:**

```python
import os
import pytz

# Set timezone
os.environ['TZ'] = 'Europe/London'

# Use timezone-aware datetime
from datetime import datetime
now = datetime.now(pytz.timezone('Europe/London'))
```

### 26. SSL Certificate Errors

**Symptoms:**

- "SSL certificate verify failed" errors
- Cannot connect to external APIs
- HTTPS requests fail

**Diagnosis:**

```bash
# Test SSL connectivity
ssh root@your-vps-ip "docker exec bot-name curl -v https://api.telegram.org"

# Check SSL certificates in container
ssh root@your-vps-ip "docker exec bot-name ls -la /etc/ssl/certs/"
```

**Solutions:**

**26.1 Update CA Certificates:**

```dockerfile
# Add to Dockerfile if needed:
RUN apt-get update && apt-get install -y ca-certificates
RUN update-ca-certificates
```

**26.2 Disable SSL Verification (NOT RECOMMENDED for production):**

```python
# Only for testing/debugging
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
```

**26.3 Use Specific CA Bundle:**

```python
import certifi
import httpx

# Use certifi's CA bundle
client = httpx.Client(verify=certifi.where())
```

---

## Prevention and Best Practices

### Prevent Deployment Issues

**1. Test Locally First:**

```bash
# Always test before deploying
telegram-bot-stack dev

# Run tests
pytest

# Check for errors
telegram-bot-stack validate
```

**2. Use Staging Environment:**

- Deploy to test VPS first
- Verify everything works
- Then deploy to production

**3. Enable Automatic Backups:**

```yaml
# In deploy.yaml
backup:
  enabled: true
  auto_backup_before_update: true
  retention_days: 7
```

**4. Monitor Regularly:**

```bash
# Daily health check
telegram-bot-stack deploy health

# Weekly review
telegram-bot-stack deploy history
telegram-bot-stack deploy backup list
```

**5. Keep Dependencies Updated:**

```bash
# Update dependencies regularly
pip list --outdated

# Update requirements.txt
pip freeze > requirements.txt

# Test locally before deploying
telegram-bot-stack dev
```

### Quick Recovery Checklist

When something goes wrong:

1. **Check Health:**

   ```bash
   telegram-bot-stack deploy health
   telegram-bot-stack deploy health --errors
   ```

2. **Review Logs:**

   ```bash
   telegram-bot-stack deploy logs --tail 100
   ```

3. **Check History:**

   ```bash
   telegram-bot-stack deploy history
   ```

4. **Rollback if Needed:**

   ```bash
   telegram-bot-stack deploy rollback --yes
   ```

5. **Restore from Backup:**
   ```bash
   telegram-bot-stack deploy backup list
   telegram-bot-stack deploy restore backup-*.tar.gz
   ```

### Getting Help

If you're still stuck:

1. **Check Documentation:**

   - [Deployment Guide](deployment_guide.md)
   - [Architecture](architecture.md)
   - [API Reference](api_reference.md)

2. **Search Issues:**

   - [GitHub Issues](https://github.com/sensiloles/telegram-bot-stack/issues)
   - Search for similar problems

3. **Ask for Help:**

   - [GitHub Discussions](https://github.com/sensiloles/telegram-bot-stack/discussions)
   - Include: logs, deploy.yaml (without secrets), error messages

4. **Report Bugs:**
   - [Create Issue](https://github.com/sensiloles/telegram-bot-stack/issues/new)
   - Include: minimal reproduction steps, environment details

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
