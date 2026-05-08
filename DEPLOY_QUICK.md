# 🚀 LinkCraft Deployment Quick Guide

**Server**: `161.118.230.226:8006`  
**Environment**: Production  
**Database**: `aim_shorty_prod` (MySQL)

---

## **COPY-PASTE COMMANDS (Run these in order)**

### Step 1: SSH to VM & Clone Project
```bash
ssh user@161.118.230.226
cd /opt
sudo git clone https://github.com/YOUR_USERNAME/aim-shorty.git
cd aim-shorty
sudo chown -R $USER:$USER .
```

### Step 2: Setup Python Environment
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Configure .env (IMPORTANT!)
```bash
cat > .env << 'EOF'
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)
DB_HOST=localhost
DB_PORT=3306
DB_NAME=aim_shorty_prod
DB_USER=linkcraft_user
DB_PASSWORD=your-secure-db-password-here
REDIS_URL=redis://localhost:6379/1
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MIDTRANS_SERVER_KEY=your-midtrans-key
MIDTRANS_CLIENT_KEY=your-midtrans-key
MIDTRANS_IS_PRODUCTION=true
APP_BASE_URL=http://161.118.230.226:8006
EOF
```

**⚠️ EDIT .env dengan nilai real Anda:**
```bash
nano .env
# Ganti: DB_PASSWORD, MAIL_USERNAME, MAIL_PASSWORD, MIDTRANS keys
```

### Step 4: Install System Dependencies
```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip
sudo apt install -y mysql-server redis-server nginx
```

### Step 5: Setup MySQL
```bash
sudo mysql -u root -p << 'EOF'
CREATE USER 'linkcraft_user'@'localhost' IDENTIFIED BY 'your-secure-db-password-here';
GRANT ALL PRIVILEGES ON aim_shorty_prod.* TO 'linkcraft_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
EOF
```

### Step 6: Database Migrations
```bash
source venv/bin/activate
export FLASK_ENV=production
flask db upgrade
```

### Step 7: Create Log Directory
```bash
sudo mkdir -p /var/log/linkcraft
sudo chown www-data:www-data /var/log/linkcraft
```

### Step 8: Setup Gunicorn Service
```bash
sudo tee /etc/systemd/system/linkcraft.service > /dev/null << 'EOF'
[Unit]
Description=LinkCraft Flask Application
After=network.target redis-server.service mysql.service
Requires=redis-server.service

[Service]
Type=notify
User=www-data
WorkingDirectory=/opt/aim-shorty
Environment="PATH=/opt/aim-shorty/venv/bin"
EnvironmentFile=/opt/aim-shorty/.env
ExecStart=/opt/aim-shorty/venv/bin/gunicorn \
    --workers 4 \
    --worker-class sync \
    --bind 127.0.0.1:8006 \
    --timeout 120 \
    --access-logfile /var/log/linkcraft/access.log \
    --error-logfile /var/log/linkcraft/error.log \
    run:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable linkcraft
sudo systemctl start linkcraft
```

### Step 9: Setup Nginx
```bash
sudo tee /etc/nginx/sites-available/linkcraft > /dev/null << 'EOF'
upstream linkcraft {
    server 127.0.0.1:8006;
}

server {
    listen 80;
    server_name 161.118.230.226;
    client_max_body_size 5M;
    
    access_log /var/log/nginx/linkcraft_access.log;
    error_log /var/log/nginx/linkcraft_error.log;

    location /static/ {
        alias /opt/aim-shorty/app/static/;
        expires 30d;
    }

    location / {
        proxy_pass http://linkcraft;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/linkcraft /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 10: Enable Redis
```bash
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### Step 11: Verify Everything
```bash
sudo systemctl status linkcraft
sudo systemctl status nginx
redis-cli ping  # Should output: PONG
curl http://161.118.230.226:8006/
```

---

## **MONITORING & TROUBLESHOOTING**

### View Logs
```bash
# Gunicorn errors
sudo tail -f /var/log/linkcraft/error.log

# Request logs
sudo tail -f /var/log/linkcraft/access.log

# Nginx errors
sudo tail -f /var/log/nginx/linkcraft_error.log
```

### Restart Services
```bash
sudo systemctl restart linkcraft        # Restart app
sudo systemctl restart nginx             # Restart webserver
sudo systemctl restart redis-server      # Restart cache
```

### Check Database Connection
```bash
mysql -u linkcraft_user -p aim_shorty_prod -e "SELECT 1;"
```

### Check Service Status
```bash
sudo systemctl status linkcraft
sudo systemctl status nginx
sudo systemctl status redis-server
```

### Check Disk & Memory
```bash
df -h           # Disk usage
free -h         # Memory usage
du -sh /opt/aim-shorty  # Project size
```

---

## **COMMON ISSUES & FIXES**

### ❌ "Port 8006 already in use"
```bash
sudo lsof -i :8006
sudo kill -9 <PID>
```

### ❌ "Permission denied" on /opt/aim-shorty
```bash
sudo chown -R www-data:www-data /opt/aim-shorty
```

### ❌ "Database connection error"
```bash
# Check credentials in .env
mysql -u linkcraft_user -p -h localhost aim_shorty_prod -e "SELECT 1;"
```

### ❌ "502 Bad Gateway" from Nginx
```bash
# Check if Gunicorn is running
sudo systemctl status linkcraft
tail -f /var/log/linkcraft/error.log
```

### ❌ Application won't start
```bash
source venv/bin/activate
export FLASK_ENV=production
python -c "from app import create_app; app = create_app(); print('OK')"
```

---

## **HEALTH CHECK SCRIPT**

Run anytime to verify deployment:
```bash
bash deploy_check.sh
```

---

## **USEFUL COMMANDS**

```bash
# SSH to VM
ssh user@161.118.230.226

# Go to project
cd /opt/aim-shorty

# Activate venv
source venv/bin/activate

# Test app manually
gunicorn -w 1 -b 127.0.0.1:8006 run:app

# Database backup
mysqldump -u linkcraft_user -p aim_shorty_prod > backup.sql

# Database restore
mysql -u linkcraft_user -p aim_shorty_prod < backup.sql

# Update code (pull latest)
git pull origin main
pip install -r requirements.txt
flask db upgrade
sudo systemctl restart linkcraft
```

---

## **FINAL CHECKLIST**

- ✅ `http://161.118.230.226:8006/` accessible
- ✅ Database connected (can login to register)
- ✅ Redis working (cache active)
- ✅ Static files loading (CSS, JS visible)
- ✅ QR codes generating
- ✅ Logs clean (no errors)
- ✅ Services auto-start on reboot

---

**🎉 If everything is working, deployment complete!**

For detailed guide, see `DEPLOYMENT.md`
