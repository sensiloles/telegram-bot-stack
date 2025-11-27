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
telegram-bot-stack deploy status
```

Shows:

- Container status (running/stopped)
- Resource usage (CPU, memory)
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
# On VPS
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

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
docker-compose restart
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
5. **Rollback to previous version** if recent update caused the issue:
   ```bash
   telegram-bot-stack deploy rollback
   ```

### Update Broke the Bot

**Problem:** Bot stopped working after an update

**Solutions:**

1. **Immediate fix - Rollback to previous version:**

   ```bash
   telegram-bot-stack deploy rollback --yes
   ```

2. Check what changed:

   - View deployment history: `telegram-bot-stack deploy history`
   - Compare code changes: `git diff HEAD^`
   - Review recent commits

3. Fix the issue:

   - Fix code locally
   - Test thoroughly
   - Deploy again: `telegram-bot-stack deploy update`

4. If rollback failed:
   - Check if previous image exists: `telegram-bot-stack deploy history`
   - Restore from backup: `telegram-bot-stack deploy restore <backup-file>`
   - Manual rollback: SSH to VPS and use `docker images` to list available images

**Prevention:**

- Test updates locally before deploying
- Use staging environment for testing
- Keep automatic backups enabled
- Review deployment history regularly

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
