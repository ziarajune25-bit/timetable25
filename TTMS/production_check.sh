#!/bin/bash
# Production Readiness Checklist Script
# Run this before deploying to production

echo "======================================"
echo "TTMS Production Readiness Checker"
echo "======================================"
echo ""

ERRORS=0
WARNINGS=0
PASSES=0

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSES++))
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    ((ERRORS++))
}

echo "=== ENVIRONMENT CHECKS ==="
echo ""

# Check Python version
if command -v python3 &> /dev/null; then
    PY_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    check_pass "Python 3 found (version: $PY_VERSION)"
else
    check_fail "Python 3 not found"
fi

# Check .env file exists
if [ -f ".env" ]; then
    check_pass ".env file exists"
    
    # Check .env has required variables
    if grep -q "FLASK_ENV" .env; then
        FLASK_ENV=$(grep "FLASK_ENV" .env | cut -d '=' -f2 | tr -d ' ')
        if [ "$FLASK_ENV" = "production" ]; then
            check_pass "FLASK_ENV is set to production"
        else
            check_warn "FLASK_ENV is '$FLASK_ENV' (should be 'production' for production)"
        fi
    else
        check_fail "FLASK_ENV not found in .env"
    fi
    
    if grep -q "SECRET_KEY" .env; then
        check_pass "SECRET_KEY is set in .env"
    else
        check_fail "SECRET_KEY not found in .env"
    fi
    
    if grep -q "DB_HOST" .env && grep -q "DB_USER" .env && grep -q "DB_PASSWORD" .env; then
        check_pass "Database credentials are set"
    else
        check_fail "Database credentials missing in .env"
    fi
else
    check_fail ".env file not found (copy from .env.example)"
fi

echo ""
echo "=== CODE QUALITY CHECKS ==="
echo ""

# Check for debug mode in app.py
if grep -q "debug=True" backend/app.py; then
    check_fail "Flask debug mode is enabled (debug=True found)"
else
    check_pass "Flask debug mode is disabled"
fi

# Check for debug print statements
DEBUG_PRINTS=$(grep -r "print(f\"DEBUG" backend/ 2>/dev/null | wc -l)
if [ $DEBUG_PRINTS -gt 0 ]; then
    check_warn "Found $DEBUG_PRINTS debug print statements (should be removed)"
else
    check_pass "No debug print statements found"
fi

# Check for hardcoded credentials
if grep -r "password=" backend/app.py | grep -v ".getenv" > /dev/null; then
    check_warn "Possible hardcoded credentials in app.py (should use environment variables)"
else
    check_pass "No hardcoded credentials found in app.py"
fi

echo ""
echo "=== DEPENDENCY CHECKS ==="
echo ""

# Check requirements.txt exists
if [ -f "backend/requirement.txt" ]; then
    check_pass "requirements.txt found"
    
    # Check for critical packages
    if grep -q "Flask" backend/requirement.txt; then
        check_pass "Flask dependency listed"
    else
        check_fail "Flask not found in requirements.txt"
    fi
    
    if grep -q "pymysql" backend/requirement.txt; then
        check_pass "pymysql dependency listed"
    else
        check_fail "pymysql not found in requirements.txt"
    fi
    
    if grep -q "gunicorn" backend/requirement.txt; then
        check_pass "gunicorn dependency listed"
    else
        check_warn "gunicorn not found in requirements.txt (needed for production)"
    fi
    
    if grep -q "python-dotenv" backend/requirement.txt; then
        check_pass "python-dotenv dependency listed"
    else
        check_warn "python-dotenv not found in requirements.txt"
    fi
else
    check_fail "requirements.txt not found"
fi

# Check if packages are installed
if python3 -c "import flask" 2>/dev/null; then
    check_pass "Flask is installed"
else
    check_fail "Flask is not installed (run: pip install -r backend/requirement.txt)"
fi

if python3 -c "import pymysql" 2>/dev/null; then
    check_pass "pymysql is installed"
else
    check_fail "pymysql is not installed"
fi

echo ""
echo "=== DATABASE CHECKS ==="
echo ""

# Try to connect to database
if [ -f ".env" ]; then
    DB_HOST=$(grep "DB_HOST" .env | cut -d '=' -f2 | tr -d ' ')
    DB_USER=$(grep "DB_USER" .env | cut -d '=' -f2 | tr -d ' ')
    DB_PASS=$(grep "DB_PASSWORD" .env | cut -d '=' -f2 | tr -d ' ')
    DB_NAME=$(grep "DB_NAME" .env | cut -d '=' -f2 | tr -d ' ')
    
    if python3 -c "
import pymysql
import sys
try:
    conn = pymysql.connect(
        host='$DB_HOST',
        user='$DB_USER',
        password='$DB_PASS',
        database='$DB_NAME',
        connect_timeout=5
    )
    conn.close()
    sys.exit(0)
except Exception as e:
    print('Error: ' + str(e), file=sys.stderr)
    sys.exit(1)
" 2>/dev/null; then
        check_pass "Database connection successful"
    else
        check_fail "Cannot connect to database (verify credentials in .env)"
    fi
fi

echo ""
echo "=== FILE STRUCTURE CHECKS ==="
echo ""

# Check important directories exist
if [ -d "backend" ]; then
    check_pass "backend/ directory exists"
else
    check_fail "backend/ directory not found"
fi

if [ -d "template" ]; then
    check_pass "template/ directory exists"
else
    check_fail "template/ directory not found"
fi

if [ -d "static" ]; then
    check_pass "static/ directory exists"
else
    check_fail "static/ directory not found"
fi

if [ -d "database" ]; then
    check_pass "database/ directory exists"
else
    check_fail "database/ directory not found"
fi

# Check important files exist
if [ -f "backend/app.py" ]; then
    check_pass "backend/app.py exists"
else
    check_fail "backend/app.py not found"
fi

if [ -f "database/schema.sql" ]; then
    check_pass "database/schema.sql exists"
else
    check_fail "database/schema.sql not found"
fi

echo ""
echo "=== SECURITY CHECKS ==="
echo ""

# Check .env permissions (if on Unix-like system)
if [ -f ".env" ] && [ ! -z "$(command -v stat)" ]; then
    PERMS=$(stat -c "%a" .env 2>/dev/null)
    if [ "$PERMS" = "600" ] || [ "$PERMS" = "400" ]; then
        check_pass ".env has restrictive permissions ($PERMS)"
    else
        check_warn ".env permissions should be 600 (currently $PERMS)"
    fi
fi

# Check .git in gitignore
if [ -f ".gitignore" ] && grep -q ".env" .gitignore 2>/dev/null; then
    check_pass ".env is in .gitignore"
elif [ ! -f ".gitignore" ]; then
    check_warn ".gitignore not found (add .env to prevent credential leaks)"
else
    check_warn ".env not listed in .gitignore"
fi

echo ""
echo "======================================"
echo "SUMMARY"
echo "======================================"
echo -e "${GREEN}Passed:${NC}  $PASSES"
echo -e "${YELLOW}Warnings:${NC} $WARNINGS"
echo -e "${RED}Errors:${NC}   $ERRORS"
echo ""

if [ $ERRORS -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo -e "${GREEN}✓ ALL CHECKS PASSED - Ready for production!${NC}"
        exit 0
    else
        echo -e "${YELLOW}⚠ Some warnings found - Review before deploying${NC}"
        exit 0
    fi
else
    echo -e "${RED}✗ Critical errors found - Fix before deploying${NC}"
    exit 1
fi
