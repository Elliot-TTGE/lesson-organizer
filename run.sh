#!/bin/bash

# Color codes for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display usage
usage() {
  echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
  echo -e "${BLUE}  Lesson Organizer Docker Management Script${NC}"
  echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
  echo ""
  echo -e "${GREEN}USAGE:${NC} $0 {MODE} [docker-compose-commands...]"
  echo ""
  echo -e "${GREEN}DEVELOPMENT MODES:${NC}"
  echo -e "  ${YELLOW}dev${NC}            - Development mode with hot reload"
  echo -e "                   Uses: compose.yml + .env.dev"
  echo -e "                   Features: Live code reloading, local builds"
  echo ""
  echo -e "  ${YELLOW}dev-test${NC}       - Test pre-production builds locally"
  echo -e "                   Uses: compose.prod.local.yml + .env.prod.local"
  echo -e "                   Features: Test production images without Caddy/Tailscale"
  echo ""
  echo -e "  ${YELLOW}dev-caddy${NC}      - Test Caddy reverse proxy locally"
  echo -e "                   Uses: compose.prod.yml + .env (manual setup)"
  echo -e "                   Features: Test Caddy configuration before production"
  echo ""
  echo -e "${GREEN}PRODUCTION MODES:${NC}"
  echo -e "  ${YELLOW}prod${NC}           - Standard production deployment"
  echo -e "                   Uses: compose.prod.yml + .env.prod"
  echo -e "                   Features: Pulls GHCR images, includes Caddy"
  echo ""
  echo -e "  ${YELLOW}prod-tailscale${NC} - Production with Tailscale VPN"
  echo -e "                   Uses: compose.prod.tailscale.yml + .env.prod.tailscale"
  echo -e "                   Features: Tailscale network integration"
  echo ""
  echo -e "${GREEN}QUICK PRODUCTION COMMANDS:${NC}"
  echo -e "  ${YELLOW}pull${NC}           - Pull latest images from GHCR (prod mode)"
  echo -e "                   Equivalent to: prod pull"
  echo ""
  echo -e "  ${YELLOW}deploy${NC}         - Pull latest images and restart (prod mode)"
  echo -e "                   Equivalent to: prod pull && prod up -d"
  echo ""
  echo -e "  ${YELLOW}pull-ts${NC}        - Pull latest images from GHCR (prod-tailscale mode)"
  echo -e "                   Equivalent to: prod-tailscale pull"
  echo ""
  echo -e "  ${YELLOW}deploy-ts${NC}      - Pull and restart with Tailscale"
  echo -e "                   Equivalent to: prod-tailscale pull && prod-tailscale up -d"
  echo ""
  echo -e "${GREEN}UTILITY COMMANDS:${NC}"
  echo -e "  ${YELLOW}clean${NC}          - Stop containers and remove volumes/images"
  echo -e "                   WARNING: Destructive operation!"
  echo ""
  echo -e "  ${YELLOW}backup${NC}         - Create timestamped database backup"
  echo -e "                   Saves to: ./db_backups/backup-{timestamp}.db"
  echo ""
  echo -e "  ${YELLOW}logs${NC}           - View logs for a specific service"
  echo -e "                   Usage: $0 logs [service] [follow]"
  echo -e "                   Example: $0 logs backend follow"
  echo ""
  echo -e "  ${YELLOW}status${NC}         - Show running containers status"
  echo ""
  echo -e "${GREEN}EXAMPLES:${NC}"
  echo -e "  ${BLUE}# Development - start with hot reload${NC}"
  echo -e "  $0 dev up -d"
  echo ""
  echo -e "  ${BLUE}# Development - rebuild and restart${NC}"
  echo -e "  $0 dev up -d --build"
  echo ""
  echo -e "  ${BLUE}# Test production build locally${NC}"
  echo -e "  $0 dev-test build --no-cache"
  echo -e "  $0 dev-test up -d"
  echo ""
  echo -e "  ${BLUE}# Test Caddy configuration${NC}"
  echo -e "  $0 dev-caddy up -d caddy"
  echo ""
  echo -e "  ${BLUE}# Production - pull latest and deploy${NC}"
  echo -e "  $0 deploy"
  echo ""
  echo -e "  ${BLUE}# Production - just pull images${NC}"
  echo -e "  $0 pull"
  echo ""
  echo -e "  ${BLUE}# Production - manual deploy${NC}"
  echo -e "  $0 prod pull"
  echo -e "  $0 prod up -d"
  echo ""
  echo -e "  ${BLUE}# View backend logs${NC}"
  echo -e "  $0 logs backend follow"
  echo ""
  echo -e "  ${BLUE}# Stop everything${NC}"
  echo -e "  $0 prod down"
  echo ""
  echo -e "  ${BLUE}# Backup database${NC}"
  echo -e "  $0 backup"
  echo ""
  exit 1
}

# Check if at least one argument is provided
if [ "$#" -lt 1 ]; then
  usage
fi

# Determine the mode based on the first argument
MODE=$1
shift # Remove the first argument (mode) to process the rest as Docker commands

# Set the base Docker Compose command based on the mode
case $MODE in
  dev)
    echo -e "${GREEN}[DEV MODE]${NC} Starting development environment with hot reload..."
    BASE_COMMAND="docker compose --env-file .env.dev"
    ;;
  
  dev-test)
    echo -e "${GREEN}[DEV-TEST MODE]${NC} Testing production builds locally..."
    BASE_COMMAND="docker compose -f compose.prod.local.yml --env-file .env.prod.local"
    ;;
  
  dev-caddy)
    echo -e "${GREEN}[DEV-CADDY MODE]${NC} Testing Caddy configuration..."
    if [ ! -f .env ]; then
      echo -e "${YELLOW}Warning:${NC} .env file not found. Using default environment."
    fi
    BASE_COMMAND="docker compose -f compose.prod.yml --env-file .env"
    ;;
  
  prod)
    echo -e "${GREEN}[PROD MODE]${NC} Managing production deployment..."
    BASE_COMMAND="docker compose -f compose.prod.yml --env-file .env.prod"
    ;;
  
  prod-tailscale)
    echo -e "${GREEN}[PROD-TAILSCALE MODE]${NC} Managing production with Tailscale..."
    BASE_COMMAND="docker compose -f compose.prod.tailscale.yml --env-file .env.prod.tailscale"
    ;;
  
  pull)
    echo -e "${GREEN}[PULL]${NC} Pulling latest production images from GHCR..."
    docker compose -f compose.prod.yml --env-file .env.prod pull
    echo -e "${GREEN}✓ Pull complete!${NC}"
    exit 0
    ;;
  
  deploy)
    echo -e "${GREEN}[DEPLOY]${NC} Pulling latest images and restarting production..."
    docker compose -f compose.prod.yml --env-file .env.prod pull
    if [ $? -eq 0 ]; then
      echo -e "${GREEN}✓ Pull complete. Starting containers...${NC}"
      docker compose -f compose.prod.yml --env-file .env.prod up -d
      if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Deployment complete!${NC}"
        echo ""
        echo -e "${BLUE}Running containers:${NC}"
        docker compose -f compose.prod.yml --env-file .env.prod ps
      else
        echo -e "${RED}✗ Failed to start containers${NC}"
        exit 1
      fi
    else
      echo -e "${RED}✗ Failed to pull images${NC}"
      exit 1
    fi
    exit 0
    ;;
  
  pull-ts)
    echo -e "${GREEN}[PULL-TS]${NC} Pulling latest production images from GHCR (Tailscale)..."
    docker compose -f compose.prod.tailscale.yml --env-file .env.prod.tailscale pull
    echo -e "${GREEN}✓ Pull complete!${NC}"
    exit 0
    ;;
  
  deploy-ts)
    echo -e "${GREEN}[DEPLOY-TS]${NC} Pulling latest images and restarting production (Tailscale)..."
    docker compose -f compose.prod.tailscale.yml --env-file .env.prod.tailscale pull
    if [ $? -eq 0 ]; then
      echo -e "${GREEN}✓ Pull complete. Starting containers...${NC}"
      docker compose -f compose.prod.tailscale.yml --env-file .env.prod.tailscale up -d
      if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Deployment complete!${NC}"
        echo ""
        echo -e "${BLUE}Running containers:${NC}"
        docker compose -f compose.prod.tailscale.yml --env-file .env.prod.tailscale ps
      else
        echo -e "${RED}✗ Failed to start containers${NC}"
        exit 1
      fi
    else
      echo -e "${RED}✗ Failed to pull images${NC}"
      exit 1
    fi
    exit 0
    ;;
  
  clean)
    echo -e "${RED}[CLEAN]${NC} Cleaning up Docker containers, images, and volumes..."
    echo -e "${YELLOW}Warning: This will remove all containers, volumes, and images!${NC}"
    read -p "Are you sure? (yes/no): " CONFIRM
    if [ "$CONFIRM" = "yes" ]; then
      docker compose down --volumes --rmi all 2>/dev/null
      docker compose -f compose.prod.yml down --volumes --rmi all 2>/dev/null
      docker compose -f compose.prod.local.yml down --volumes --rmi all 2>/dev/null
      docker compose -f compose.prod.tailscale.yml down --volumes --rmi all 2>/dev/null
      echo -e "${GREEN}✓ Cleanup complete.${NC}"
    else
      echo -e "${YELLOW}Cleanup cancelled.${NC}"
    fi
    exit 0
    ;;
  
  backup)
    TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
    BACKUP_FILE="backup-$TIMESTAMP.db"
    echo -e "${GREEN}[BACKUP]${NC} Backing up database to ./db_backups/$BACKUP_FILE"
    
    # Create backup directory if it doesn't exist
    mkdir -p db_backups
    
    docker run --rm \
      -v lesson-organizer_backend_db:/db \
      -v "$(pwd)/db_backups":/backup \
      alpine \
      cp /db/lesson_organizer.db /backup/$BACKUP_FILE
    
    if [ $? -eq 0 ]; then
      echo -e "${GREEN}✓ Backup complete: ./db_backups/$BACKUP_FILE${NC}"
    else
      echo -e "${RED}✗ Backup failed${NC}"
      exit 1
    fi
    exit 0
    ;;
  
  logs)
    SERVICE=$1
    FOLLOW=$2
    if [ -z "$SERVICE" ]; then
      echo -e "${YELLOW}Usage:${NC} $0 logs <service> [follow]"
      echo -e "${YELLOW}Available services:${NC} backend, frontend, caddy"
      exit 1
    fi
    
    if [ "$FOLLOW" = "follow" ] || [ "$FOLLOW" = "-f" ]; then
      echo -e "${GREEN}[LOGS]${NC} Following logs for $SERVICE (Ctrl+C to exit)..."
      docker logs -f $SERVICE
    else
      echo -e "${GREEN}[LOGS]${NC} Showing last 50 lines for $SERVICE..."
      docker logs --tail 50 $SERVICE
    fi
    exit 0
    ;;
  
  status)
    echo -e "${GREEN}[STATUS]${NC} Container status:"
    echo ""
    echo -e "${BLUE}Development containers:${NC}"
    docker compose --env-file .env.dev ps 2>/dev/null || echo "  (none running)"
    echo ""
    echo -e "${BLUE}Production containers:${NC}"
    docker compose -f compose.prod.yml --env-file .env.prod ps 2>/dev/null || echo "  (none running)"
    echo ""
    exit 0
    ;;
  
  help|--help|-h)
    usage
    ;;
  
  *)
    echo -e "${RED}Error:${NC} Unknown mode '$MODE'"
    echo ""
    usage
    ;;
esac

# Execute the constructed command (only for docker wrapper modes)
COMMAND="$BASE_COMMAND $*"
echo -e "${BLUE}Running:${NC} $COMMAND"
eval $COMMAND

# Show status after command completes (for up/down/restart commands)
if [[ "$*" == *"up"* ]] || [[ "$*" == *"down"* ]] || [[ "$*" == *"restart"* ]]; then
  echo ""
  echo -e "${GREEN}✓ Command complete.${NC}"
fi