# 📋 Panduan Deployment LinkCraft di VM

**Server**: `161.118.230.226:8006`  
**Database**: `aim_shorty_prod` (sudah dibuat)  
**Port**: `8006`

---

## **TAHAP 1: Persiapan Server (Jalankan di VM)**

### 1.1 Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 1.2 Install Dependencies Sistem
```bash
sudo apt install -y python3.11 python3.11-venv python3-pip
sudo apt install -y mysql-server redis-server nginx
sudo apt install -y git curl wget
```

### 1.3 Verifikasi Instalasi
```bash
python3.11 --version
mysql --version
redis-server --version
nginx -v
```

---

## **TAHAP 2: Clone & Setup Project**

### 2.1 Clone Repository
```bash
cd /opt  # atau folder pilihan Anda
sudo git clone https://github.com/YOUR_USERNAME/aim-shorty.git
cd aim-shorty
sudo chown -R $USER:$USER .
```

### 2.2 Create Virtual Environment
```bash
python3.11 -m venv venv
source venv/bin/activate
```

### 2.3 Upgrade pip & Install Dependencies
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

---

## **TAHAP 3: Konfigurasi Database**

### 3.1 Setup MySQL User & Permissions
```bash
sudo mysql -u root -p
```

Paste di MySQL prompt:
```sql
CREATE USER 'linkcraft_user'@'localhost' IDENTIFIED BY 'your-secure-db-password';
GRANT ALL PRIVILEGES ON aim_shorty_prod.* TO 'linkcraft_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3.2 Verifikasi Koneksi
```bash
mysql -u linkcraft_user -p -h localhost aim_shorty_prod -e "SELECT 1;"
```

### 3.3 Setup .env File
```bash
cp .env.production .env
nano .env  # Edit dengan nilai Anda yang sebenarnya
```

**Pastikan di `.env`:**
```
FLASK_ENV=production
DB_HOST=localhost
DB_NAME=aim_shorty_prod
DB_USER=linkcraft_user
DB_PASSWORD=<your-password>
APP_BASE_URL=http://161.118.230.226:8006
```

### 3.4 Run Database Migrations
```bash
source venv/bin/activate
export FLASK_ENV=production
flask db upgrade
```

**Output yang diharapkan:**
```
INFO  [alembic.runtime.migration] Context impl MySQLImpl with MySQL driver pymysql
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade...
```

---

## **TAHAP 4: Setup Gunicorn (Application Server)**

### 4.1 Install Gunicorn
```bash
pip install gunicorn
```

### 4.2 Test Gunicorn Locally
```bash
source venv/bin/activate
gunicorn -w 4 -b 127.0.0.1:8006 run:app
```

**Jika OK**, tekan `Ctrl+C` untuk stop.

### 4.3 Create Gunicorn Systemd Service

```bash
sudo nano /etc/systemd/system/linkcraft.service
```

Paste:
```ini
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
```

### 4.4 Create Log Directory
```bash
sudo mkdir -p /var/log/linkcraft
sudo chown www-data:www-data /var/log/linkcraft
```

### 4.5 Enable & Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable linkcraft
sudo systemctl start linkcraft
sudo systemctl status linkcraft
```

**Status diharapkan**: `● linkcraft.service - LinkCraft Flask Application
     Loaded: loaded (/etc/systemd/system/linkcraft.service; enabled; vendor preset: enabled)
     Active: active (running)...`

---

## **TAHAP 5: Setup Nginx (Reverse Proxy)**

### 5.1 Create Nginx Config

```bash
sudo nano /etc/nginx/sites-available/linkcraft
```

Paste:
```nginx
upstream linkcraft {
    server 127.0.0.1:8006;
}

server {
    listen 80;
    server_name 161.118.230.226;
    client_max_body_size 5M;
    
    # Logs
    access_log /var/log/nginx/linkcraft_access.log;
    error_log /var/log/nginx/linkcraft_error.log;

    # Static files
    location /static/ {
        alias /opt/aim-shorty/app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # QR Codes & Uploads
    location /qr_codes/ {
        alias /opt/aim-shorty/app/static/qr_codes/;
        expires 7d;
    }

    location /uploads/ {
        alias /opt/aim-shorty/app/uploads/;
        expires 1d;
    }

    # Main app
    location / {
        proxy_pass http://linkcraft;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### 5.2 Enable Nginx Config
```bash
sudo ln -s /etc/nginx/sites-available/linkcraft /etc/nginx/sites-enabled/
sudo nginx -t  # Test syntax
sudo systemctl restart nginx
```

---

## **TAHAP 6: Redis Setup**

### 6.1 Start Redis
```bash
sudo systemctl enable redis-server
sudo systemctl start redis-server
sudo systemctl status redis-server
```

### 6.2 Test Redis Connection
```bash
redis-cli ping  # Response: PONG
```

---

## **TAHAP 7: Testing & Verification**

### 7.1 Check Gunicorn Status
```bash
sudo systemctl status linkcraft
tail -f /var/log/linkcraft/error.log  # Monitor errors
```

### 7.2 Check Nginx Status
```bash
sudo systemctl status nginx
```

### 7.3 Test Application
Buka browser:
```
http://161.118.230.226:8006/
```

**Diharapkan**: Landing page LinkCraft tampil.

### 7.4 Test Database Connection
```bash
curl http://161.118.230.226:8006/auth/register
# Harusnya tampil halaman register
```

### 7.5 Check Logs
```bash
sudo tail -f /var/log/linkcraft/error.log      # Gunicorn errors
sudo tail -f /var/log/linkcraft/access.log     # Request logs
sudo tail -f /var/log/nginx/linkcraft_error.log # Nginx errors
```

---

## **TAHAP 8: Troubleshooting**

### ❌ Port Already in Use
```bash
sudo lsof -i :8006
sudo kill -9 <PID>
```

### ❌ Permission Denied
```bash
sudo chown -R www-data:www-data /opt/aim-shorty
```

### ❌ Database Connection Error
```bash
mysql -u linkcraft_user -p -h localhost aim_shorty_prod -e "SELECT 1;"
# Jika error, cek password di .env
```

### ❌ Redis Connection Error
```bash
redis-cli ping
# Jika tidak reply PONG, restart: sudo systemctl restart redis-server
```

### ❌ Gunicorn Not Starting
```bash
source /opt/aim-shorty/venv/bin/activate
export FLASK_ENV=production
gunicorn -w 4 -b 127.0.0.1:8006 run:app --log-level debug
```

---

## **TAHAP 9: Maintenance Commands**

### Restart Application
```bash
sudo systemctl restart linkcraft
```

### View Logs
```bash
sudo tail -f /var/log/linkcraft/error.log
sudo tail -f /var/log/linkcraft/access.log
```

### Database Backup
```bash
mysqldump -u linkcraft_user -p aim_shorty_prod > backup_$(date +%Y%m%d).sql
```

### Database Restore
```bash
mysql -u linkcraft_user -p aim_shorty_prod < backup_20260508.sql
```

### Update Code
```bash
cd /opt/aim-shorty
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
flask db upgrade
sudo systemctl restart linkcraft
```

### Check Disk Space
```bash
df -h
```

### Check Memory
```bash
free -h
```

---

## **TAHAP 10: Optional - Setup SSL (HTTPS)**

### Dengan Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d 161.118.230.226
# Follow prompts
```

Update `/etc/nginx/sites-available/linkcraft` untuk redirect HTTP ke HTTPS.

---

## **Checklist Deployment**

- [ ] Server siap (Ubuntu, dependencies installed)
- [ ] Project di-clone
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] `.env` file dikonfigurasi dengan benar
- [ ] Database migrations selesai
- [ ] Gunicorn berjalan
- [ ] Nginx berjalan
- [ ] Redis berjalan
- [ ] Test akses `http://161.118.230.226:8006/`
- [ ] Database connection OK
- [ ] Static files serve correctly
- [ ] Logs clear (no errors)
- [ ] SSL setup (optional tapi recommended)

---

## **Quick Start Reference**

```bash
# SSH ke VM
ssh user@161.118.230.226

# Go to project
cd /opt/aim-shorty
source venv/bin/activate

# Check status
sudo systemctl status linkcraft nginx redis-server

# Restart all
sudo systemctl restart linkcraft nginx

# View logs
sudo tail -f /var/log/linkcraft/error.log
```

---

**Done! 🚀 Aplikasi sekarang live di: `http://161.118.230.226:8006`**

Untuk support, cek logs dan error messages. Tanya jika ada yang stuck!
