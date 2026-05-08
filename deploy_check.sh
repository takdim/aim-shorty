#!/bin/bash
# ── LinkCraft Deployment Validator ────────────────────────────────
# Run: bash deploy_check.sh

echo "🔍 LinkCraft Deployment Health Check"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2${NC}"
    else
        echo -e "${RED}✗ $2${NC}"
    fi
}

# 1. Python & Venv
echo "📦 Checking Python & Virtual Environment..."
if [ -d "venv" ]; then
    echo -e "${GREEN}✓ Virtual environment exists${NC}"
    source venv/bin/activate
    python --version
    check_status $? "Python accessible"
else
    echo -e "${RED}✗ Virtual environment not found${NC}"
fi
echo ""

# 2. Dependencies
echo "📚 Checking Dependencies..."
pip list | grep -q Flask && check_status 0 "Flask installed" || check_status 1 "Flask not found"
pip list | grep -q gunicorn && check_status 0 "Gunicorn installed" || check_status 1 "Gunicorn not found"
pip list | grep -q redis && check_status 0 "Redis client installed" || check_status 1 "Redis client not found"
echo ""

# 3. Environment
echo "⚙️ Checking .env Configuration..."
if [ -f ".env" ]; then
    echo -e "${GREEN}✓ .env file exists${NC}"
    grep -q "APP_BASE_URL" .env && check_status 0 "APP_BASE_URL configured" || check_status 1 "APP_BASE_URL missing"
    grep -q "DB_NAME" .env && check_status 0 "Database configured" || check_status 1 "Database not configured"
else
    echo -e "${RED}✗ .env file not found${NC}"
fi
echo ""

# 4. Database
echo "🗄️ Checking Database..."
if command -v mysql &> /dev/null; then
    DB_HOST=$(grep "DB_HOST" .env | cut -d= -f2 | tr -d ' ')
    DB_USER=$(grep "DB_USER" .env | cut -d= -f2 | tr -d ' ')
    DB_NAME=$(grep "DB_NAME" .env | cut -d= -f2 | tr -d ' ')
    
    mysql -h $DB_HOST -u $DB_USER -p$(grep "DB_PASSWORD" .env | cut -d= -f2 | tr -d ' ') $DB_NAME -e "SELECT 1;" &>/dev/null
    check_status $? "Database connection"
else
    echo -e "${YELLOW}⚠ MySQL client not installed${NC}"
fi
echo ""

# 5. Redis
echo "🔴 Checking Redis..."
if command -v redis-cli &> /dev/null; then
    redis-cli ping &>/dev/null
    check_status $? "Redis connection"
else
    echo -e "${YELLOW}⚠ Redis CLI not installed${NC}"
fi
echo ""

# 6. Services
echo "🔧 Checking Services..."
if command -v systemctl &> /dev/null; then
    systemctl is-active --quiet linkcraft && check_status 0 "Linkcraft service running" || check_status 1 "Linkcraft service not running"
    systemctl is-active --quiet nginx && check_status 0 "Nginx running" || check_status 1 "Nginx not running"
    systemctl is-active --quiet redis-server && check_status 0 "Redis running" || check_status 1 "Redis not running"
else
    echo -e "${YELLOW}⚠ Systemctl not available${NC}"
fi
echo ""

# 7. Ports
echo "🌐 Checking Ports..."
if command -v netstat &> /dev/null; then
    netstat -tuln | grep -q ":8006 " && check_status 0 "Port 8006 listening" || check_status 1 "Port 8006 not listening"
    netstat -tuln | grep -q ":80 " && check_status 0 "Port 80 listening" || check_status 1 "Port 80 not listening"
else
    echo -e "${YELLOW}⚠ Netstat not available${NC}"
fi
echo ""

# 8. Directories
echo "📁 Checking Directories..."
[ -d "app/static" ] && check_status 0 "Static files directory" || check_status 1 "Static files missing"
[ -d "app/static/qr_codes" ] && check_status 0 "QR codes directory" || check_status 1 "QR codes directory missing"
[ -d "app/uploads" ] && check_status 0 "Uploads directory" || check_status 1 "Uploads directory missing"
echo ""

# 9. Application Test
echo "🧪 Testing Application..."
source venv/bin/activate
python -c "
from app import create_app
app = create_app()
print('✓ Flask app initializes')
" 2>&1
echo ""

# Summary
echo "======================================"
echo -e "${GREEN}✓ Health check complete!${NC}"
echo ""
echo "📝 Next steps:"
echo "1. If all checks passed, application should be ready"
echo "2. Test: curl http://161.118.230.226:8006/"
echo "3. Check logs: tail -f /var/log/linkcraft/error.log"
echo ""
