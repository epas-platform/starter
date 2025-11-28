#!/bin/bash
#
# Setup script - checks prerequisites and provides guidance
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

print_check() { echo -en "  Checking $1... "; }
print_ok() { echo -e "${GREEN}✓${NC}"; }
print_fail() { echo -e "${RED}✗${NC}"; }
print_warn() { echo -e "${YELLOW}⚠${NC}"; }

echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║              Enterprise Platform Setup                     ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${CYAN}Checking prerequisites...${NC}\n"

# Check Docker
print_check "Docker"
if command -v docker &> /dev/null; then
    print_ok
    DOCKER_OK=true
else
    print_fail
    DOCKER_OK=false
fi

# Check Docker Compose
print_check "Docker Compose"
if docker compose version &> /dev/null; then
    print_ok
    COMPOSE_OK=true
else
    print_fail
    COMPOSE_OK=false
fi

# Check if Docker daemon is running
print_check "Docker daemon"
if docker info &> /dev/null 2>&1; then
    print_ok
    DAEMON_OK=true
else
    print_fail
    DAEMON_OK=false
fi

# Check Make
print_check "Make"
if command -v make &> /dev/null; then
    print_ok
else
    print_warn
    echo -e "    ${YELLOW}(optional - can use docker compose directly)${NC}"
fi

# Check Python (for configure script)
print_check "Python 3"
if command -v python3 &> /dev/null; then
    print_ok
else
    print_warn
    echo -e "    ${YELLOW}(optional - needed for configure.py)${NC}"
fi

echo ""

# Summary
if [ "$DOCKER_OK" = true ] && [ "$COMPOSE_OK" = true ] && [ "$DAEMON_OK" = true ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✓ All prerequisites met!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "Next steps:"
    echo ""
    echo -e "  ${CYAN}1. Configure your project (optional):${NC}"
    echo -e "     python scripts/configure.py"
    echo ""
    echo -e "  ${CYAN}2. Start all services:${NC}"
    echo -e "     docker compose up"
    echo ""
    echo -e "  ${CYAN}3. Open your browser:${NC}"
    echo -e "     Frontend: http://localhost:3010"
    echo -e "     API Docs: http://localhost:8010/docs"
    echo ""
    echo -e "  ${CYAN}4. Login with:${NC}"
    echo -e "     Email:    admin@example.com"
    echo -e "     Password: password"
    echo ""
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}✗ Missing prerequisites${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Please install the following:"
    echo ""

    if [ "$DOCKER_OK" = false ]; then
        echo -e "  ${YELLOW}Docker:${NC}"
        echo "    macOS: brew install --cask docker"
        echo "    Linux: https://docs.docker.com/engine/install/"
        echo ""
    fi

    if [ "$DAEMON_OK" = false ] && [ "$DOCKER_OK" = true ]; then
        echo -e "  ${YELLOW}Docker daemon is not running${NC}"
        echo "    Start Docker Desktop or run: sudo systemctl start docker"
        echo ""
    fi
fi
