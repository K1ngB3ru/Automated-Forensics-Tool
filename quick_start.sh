#!/bin/bash

################################################################################
# Quick Start Script for BitProbe — Scan (Linux)
# Automatically sets up environment and runs the tool
################################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================================================"
echo -e "           BITPROBE \u2014 SCAN - QUICK START"
echo -e "========================================================================${NC}"
echo ""

# Check for root privileges
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}[ERROR] This script must be run as root or with sudo${NC}"
   echo "Please run: sudo ./quick_start.sh"
   exit 1
else
   echo -e "${GREEN}[OK] Running with root privileges${NC}"
fi

echo ""
echo -e "${BLUE}[STEP 1/5] Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}[OK] Python is installed${NC}"
    python3 --version
else
    echo -e "${RED}[ERROR] Python 3 is not installed!${NC}"
    echo "Please install Python 3.10+ using your package manager"
    exit 1
fi

echo ""
echo -e "${BLUE}[STEP 2/5] Checking virtual environment...${NC}"
if [ -d "venv" ]; then
    echo -e "${GREEN}[OK] Virtual environment exists${NC}"
else
    echo -e "${YELLOW}[INFO] Creating virtual environment...${NC}"
    python3 -m venv venv
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[OK] Virtual environment created${NC}"
    else
        echo -e "${RED}[ERROR] Failed to create virtual environment${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${BLUE}[STEP 3/5] Activating virtual environment...${NC}"
source venv/bin/activate
if [ $? -eq 0 ]; then
    echo -e "${GREEN}[OK] Virtual environment activated${NC}"
else
    echo -e "${RED}[ERROR] Failed to activate virtual environment${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}[STEP 4/5] Installing dependencies...${NC}"
pip install -r requirements.txt --quiet
if [ $? -eq 0 ]; then
    echo -e "${GREEN}[OK] Dependencies installed${NC}"
else
    echo -e "${YELLOW}[WARNING] Some dependencies may have failed to install${NC}"
    echo "Attempting to continue..."
fi

echo ""
echo -e "${BLUE}[STEP 5/5] Running Forensic Analysis Tool...${NC}"
echo ""
echo -e "${CYAN}========================================================================${NC}"
echo ""

python3 src/forensic_master.py

echo ""
echo -e "${CYAN}========================================================================"
echo -e "                      EXECUTION COMPLETED"
echo -e "========================================================================${NC}"
echo ""
echo "Check the following directories for output:"
echo "  - Reports: output/reports/master/"
echo "  - Artifacts: output/artifacts/"
echo "  - Logs: output/logs/"
echo ""