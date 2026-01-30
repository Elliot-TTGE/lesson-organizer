#!/bin/bash

# Color codes for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper function to check SQLite integrity
check_sqlite_integrity() {
  local backup_file="$1"
  echo -e "${BLUE}[CHECK]${NC} Verifying database integrity..."
  
  # Use alpine image with sqlite3 package installed
  docker run --rm \
    -v "$(pwd)/db_backups":/backup \
    alpine sh -c "apk add --no-cache sqlite > /dev/null 2>&1 && sqlite3 /backup/$backup_file 'PRAGMA integrity_check;'" > /tmp/integrity_check.txt 2>&1
  
  if [ $? -eq 0 ] && grep -q "ok" /tmp/integrity_check.txt; then
    echo -e "${GREEN}✓ Database integrity check passed${NC}"
    rm -f /tmp/integrity_check.txt
    return 0
  else
    echo -e "${RED}✗ Database integrity check failed${NC}"
    cat /tmp/integrity_check.txt
    rm -f /tmp/integrity_check.txt
    return 1
  fi
}

# Helper function to check disk space
check_disk_space() {
  local backup_file="$1"
  local backup_size=$(stat -f%z "./db_backups/$backup_file" 2>/dev/null || stat -c%s "./db_backups/$backup_file" 2>/dev/null)
  local required_space=$((backup_size * 2))
  local available_space=$(df -k "./db_backups" | tail -1 | awk '{print $4}')
  local available_bytes=$((available_space * 1024))
  
  echo -e "${BLUE}[CHECK]${NC} Verifying disk space..."
  echo -e "  Backup size: $(numfmt --to=iec $backup_size 2>/dev/null || echo "$backup_size bytes")"
  echo -e "  Required space: $(numfmt --to=iec $required_space 2>/dev/null || echo "$required_space bytes")"
  echo -e "  Available space: $(numfmt --to=iec $available_bytes 2>/dev/null || echo "$available_bytes bytes")"
  
  if [ $available_bytes -gt $required_space ]; then
    echo -e "${GREEN}✓ Sufficient disk space available${NC}"
    return 0
  else
    echo -e "${RED}✗ Insufficient disk space${NC}"
    return 1
  fi
}

# Helper function to list available backups
list_backups() {
  echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}" >&2
  echo -e "${BLUE}  Available Database Backups${NC}" >&2
  echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}" >&2
  echo "" >&2
  
  if [ ! -d "./db_backups" ] || [ -z "$(ls -A ./db_backups/*.db 2>/dev/null)" ]; then
    echo -e "${YELLOW}No backups found in ./db_backups/${NC}" >&2
    return 1
  fi
  
  local count=0
  for backup in ./db_backups/backup-*.db; do
    if [ -f "$backup" ]; then
      count=$((count + 1))
      local filename=$(basename "$backup")
      local size=$(ls -lh "$backup" | awk '{print $5}')
      local date=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$backup" 2>/dev/null || stat -c "%y" "$backup" 2>/dev/null | cut -d'.' -f1)
      local age_days=$(echo "($(date +%s) - $(stat -f %m "$backup" 2>/dev/null || stat -c %Y "$backup" 2>/dev/null)) / 86400" | bc)
      
      echo -e "  ${GREEN}$count.${NC} $filename" >&2
      echo -e "     Size: $size | Created: $date | Age: ${age_days} days" >&2
      echo "" >&2
    fi
  done
  
  if [ $count -eq 0 ]; then
    echo -e "${YELLOW}No backups found in ./db_backups/${NC}" >&2
    return 1
  fi
  
  echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}" >&2
  read -p "Enter backup filename (or 'cancel' to abort): " SELECTED_BACKUP
  
  if [ "$SELECTED_BACKUP" = "cancel" ] || [ -z "$SELECTED_BACKUP" ]; then
    echo -e "${YELLOW}Operation cancelled.${NC}" >&2
    return 1
  fi
  
  if [ ! -f "./db_backups/$SELECTED_BACKUP" ]; then
    echo -e "${RED}✗ Backup file not found: $SELECTED_BACKUP${NC}" >&2
    return 1
  fi
  
  echo "$SELECTED_BACKUP"
  return 0
}

# Helper function to cleanup old backups
cleanup_old_backups() {
  echo -e "${BLUE}[CLEANUP]${NC} Removing backups older than 30 days..."
  
  local deleted_count=0
  for backup in ./db_backups/backup-*.db; do
    if [ -f "$backup" ]; then
      local filename=$(basename "$backup")
      # Only process files matching the exact backup naming pattern: backup-YYYY-MM-DD_HH-MM-SS.db
      if [[ "$filename" =~ ^backup-[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{2}-[0-9]{2}-[0-9]{2}\.db$ ]]; then
        local age_days=$(echo "($(date +%s) - $(stat -f %m "$backup" 2>/dev/null || stat -c %Y "$backup" 2>/dev/null)) / 86400" | bc)
        if [ $age_days -gt 30 ]; then
          echo -e "  Deleting: $filename (${age_days} days old)"
          rm "$backup"
          deleted_count=$((deleted_count + 1))
        fi
      fi
    fi
  done
  
  if [ $deleted_count -gt 0 ]; then
    echo -e "${GREEN}✓ Deleted $deleted_count old backup(s)${NC}"
  else
    echo -e "${GREEN}✓ No old backups to delete${NC}"
  fi
}

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
  echo -e "                   Automatically removes backups older than 30 days"
  echo ""
  echo -e "  ${YELLOW}restore${NC}        - Restore database from backup (with safety checks)"
  echo -e "                   Usage: $0 restore [mode] [backup-file]"
  echo -e ""
  echo -e "                   ${GREEN}Interactive Mode:${NC} $0 restore"
  echo -e "                   - Lists all available backups with details"
  echo -e "                   - Prompts you to type the backup filename"
  echo -e "                   - Defaults to 'dev' environment"
  echo -e ""
  echo -e "                   ${GREEN}Direct Mode:${NC} $0 restore backup-2026-01-29_19-13-39.db"
  echo -e "                   - Uses specified backup file"
  echo -e "                   - Restores to 'dev' environment"
  echo -e ""
  echo -e "                   ${GREEN}Production Mode:${NC} $0 restore prod backup-2026-01-29.db"
  echo -e "                   - Restores to production environment"
  echo -e "                   - Shows prominent warnings"
  echo -e ""
  echo -e "                   ${BLUE}Safety features:${NC}"
  echo -e "                   • Validates backup integrity before restore"
  echo -e "                   • Creates automatic pre-restore backup"
  echo -e "                   • Requires two confirmations (yes + filename)"
  echo -e "                   • Auto-rollback if backend fails to start"
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
  echo -e "  ${BLUE}# Restore database (interactive)${NC}"
  echo -e "  $0 restore"
  echo ""
  echo -e "  ${BLUE}# Restore specific backup in dev${NC}"
  echo -e "  $0 restore backup-2026-01-29_19-13-39.db"
  echo ""
  echo -e "  ${BLUE}# Restore to production${NC}"
  echo -e "  $0 restore prod backup-2026-01-29_19-13-39.db"
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
      cleanup_old_backups
    else
      echo -e "${RED}✗ Backup failed${NC}"
      exit 1
    fi
    exit 0
    ;;
  
  restore)
    # Parse optional parameters
    RESTORE_MODE=""
    RESTORE_BACKUP=""
    
    # Check if first arg is a mode
    if [ "$1" = "dev" ] || [ "$1" = "dev-test" ] || [ "$1" = "dev-caddy" ] || [ "$1" = "prod" ] || [ "$1" = "prod-tailscale" ]; then
      RESTORE_MODE="$1"
      shift
      RESTORE_BACKUP="$1"
    else
      RESTORE_BACKUP="$1"
    fi
    
    # Default to dev mode if not specified
    if [ -z "$RESTORE_MODE" ]; then
      RESTORE_MODE="dev"
    fi
    
    # Set compose command based on mode
    case $RESTORE_MODE in
      dev)
        RESTORE_COMPOSE="docker compose --env-file .env.dev"
        ;;
      dev-test)
        RESTORE_COMPOSE="docker compose -f compose.prod.local.yml --env-file .env.prod.local"
        ;;
      dev-caddy)
        RESTORE_COMPOSE="docker compose -f compose.prod.yml --env-file .env"
        ;;
      prod)
        RESTORE_COMPOSE="docker compose -f compose.prod.yml --env-file .env.prod"
        ;;
      prod-tailscale)
        RESTORE_COMPOSE="docker compose -f compose.prod.tailscale.yml --env-file .env.prod.tailscale"
        ;;
    esac
    
    echo -e "${GREEN}[RESTORE]${NC} Database restore utility"
    echo -e "${BLUE}Target environment:${NC} $RESTORE_MODE"
    echo ""
    
    # List backups if none specified
    if [ -z "$RESTORE_BACKUP" ]; then
      RESTORE_BACKUP=$(list_backups)
      if [ $? -ne 0 ] || [ -z "$RESTORE_BACKUP" ]; then
        exit 1
      fi
    fi
    
    # Verify backup file exists
    if [ ! -f "./db_backups/$RESTORE_BACKUP" ]; then
      echo -e "${RED}✗ Backup file not found: ./db_backups/$RESTORE_BACKUP${NC}"
      exit 1
    fi
    
    echo -e "${BLUE}Selected backup:${NC} $RESTORE_BACKUP"
    echo ""
    
    # Check SQLite integrity
    check_sqlite_integrity "$RESTORE_BACKUP"
    if [ $? -ne 0 ]; then
      echo -e "${RED}✗ Backup file is corrupted or invalid${NC}"
      exit 1
    fi
    
    # Check disk space
    check_disk_space "$RESTORE_BACKUP"
    if [ $? -ne 0 ]; then
      echo -e "${RED}✗ Not enough disk space for restore${NC}"
      exit 1
    fi
    
    echo ""
    
    # Create pre-restore backup
    TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
    PRERESTORE_BACKUP="backup-$TIMESTAMP.db"
    echo -e "${GREEN}[PRE-RESTORE BACKUP]${NC} Creating safety backup: $PRERESTORE_BACKUP"
    
    mkdir -p db_backups
    docker run --rm \
      -v lesson-organizer_backend_db:/db \
      -v "$(pwd)/db_backups":/backup \
      alpine \
      cp /db/lesson_organizer.db /backup/$PRERESTORE_BACKUP 2>/dev/null
    
    if [ $? -eq 0 ]; then
      echo -e "${GREEN}✓ Pre-restore backup created${NC}"
    else
      echo -e "${YELLOW}⚠ No existing database to backup (this may be a fresh install)${NC}"
    fi
    
    echo ""
    
    # Production warning
    if [ "$RESTORE_MODE" = "prod" ] || [ "$RESTORE_MODE" = "prod-tailscale" ]; then
      echo -e "${RED}════════════════════════════════════════════════════════════════${NC}"
      echo -e "${RED}  WARNING: PRODUCTION DATABASE RESTORE${NC}"
      echo -e "${RED}════════════════════════════════════════════════════════════════${NC}"
      echo -e "${YELLOW}You are about to restore the PRODUCTION database!${NC}"
      echo -e "${YELLOW}This will REPLACE the current production database.${NC}"
      echo -e "${YELLOW}A backup has been created: $PRERESTORE_BACKUP${NC}"
      echo -e "${RED}════════════════════════════════════════════════════════════════${NC}"
      echo ""
    fi
    
    # First confirmation
    echo -e "${YELLOW}About to restore database from:${NC} $RESTORE_BACKUP"
    echo -e "${YELLOW}To environment:${NC} $RESTORE_MODE"
    echo -e "${YELLOW}Safety backup created:${NC} $PRERESTORE_BACKUP"
    echo ""
    read -p "Do you want to proceed? (yes/no): " CONFIRM1
    
    if [ "$CONFIRM1" != "yes" ]; then
      echo -e "${YELLOW}Restore cancelled.${NC}"
      exit 0
    fi
    
    # Second confirmation - type backup filename
    echo ""
    echo -e "${YELLOW}To confirm, please type the backup filename exactly:${NC}"
    read -p "Backup filename: " CONFIRM2
    
    if [ "$CONFIRM2" != "$RESTORE_BACKUP" ]; then
      echo -e "${RED}✗ Filename does not match. Restore cancelled.${NC}"
      exit 1
    fi
    
    echo ""
    echo -e "${GREEN}[RESTORE]${NC} Starting restore process..."
    
    # Stop backend service
    echo -e "${BLUE}[STEP 1/4]${NC} Stopping backend service..."
    $RESTORE_COMPOSE stop backend
    if [ $? -eq 0 ]; then
      echo -e "${GREEN}✓ Backend stopped${NC}"
    else
      echo -e "${RED}✗ Failed to stop backend${NC}"
      exit 1
    fi
    
    # Restore database
    echo -e "${BLUE}[STEP 2/4]${NC} Restoring database from backup..."
    docker run --rm \
      -v lesson-organizer_backend_db:/db \
      -v "$(pwd)/db_backups":/backup \
      alpine \
      cp /backup/$RESTORE_BACKUP /db/lesson_organizer.db
    
    if [ $? -ne 0 ]; then
      echo -e "${RED}✗ Database restore failed${NC}"
      echo -e "${YELLOW}Rolling back to pre-restore backup...${NC}"
      docker run --rm \
        -v lesson-organizer_backend_db:/db \
        -v "$(pwd)/db_backups":/backup \
        alpine \
        cp /backup/$PRERESTORE_BACKUP /db/lesson_organizer.db
      echo -e "${GREEN}✓ Rollback complete${NC}"
      exit 1
    fi
    echo -e "${GREEN}✓ Database restored${NC}"
    
    # Start backend service
    echo -e "${BLUE}[STEP 3/4]${NC} Starting backend service..."
    $RESTORE_COMPOSE up -d backend
    
    if [ $? -ne 0 ]; then
      echo -e "${RED}✗ Failed to start backend${NC}"
      echo -e "${YELLOW}Rolling back to pre-restore backup...${NC}"
      docker run --rm \
        -v lesson-organizer_backend_db:/db \
        -v "$(pwd)/db_backups":/backup \
        alpine \
        cp /backup/$PRERESTORE_BACKUP /db/lesson_organizer.db
      $RESTORE_COMPOSE up -d backend
      echo -e "${GREEN}✓ Rollback complete${NC}"
      exit 1
    fi
    
    # Wait for service to start and verify
    echo -e "${BLUE}Waiting for backend to start...${NC}"
    sleep 5
    
    # Check if backend is running
    BACKEND_RUNNING=$($RESTORE_COMPOSE ps backend | grep -i "up" || echo "")
    
    if [ -z "$BACKEND_RUNNING" ]; then
      echo -e "${RED}✗ Backend failed to start properly${NC}"
      echo -e "${YELLOW}Rolling back to pre-restore backup...${NC}"
      $RESTORE_COMPOSE stop backend
      docker run --rm \
        -v lesson-organizer_backend_db:/db \
        -v "$(pwd)/db_backups":/backup \
        alpine \
        cp /backup/$PRERESTORE_BACKUP /db/lesson_organizer.db
      $RESTORE_COMPOSE up -d backend
      echo -e "${GREEN}✓ Rollback complete${NC}"
      exit 1
    fi
    
    echo -e "${GREEN}✓ Backend started successfully${NC}"
    
    # Cleanup old backups
    echo -e "${BLUE}[STEP 4/4]${NC} Cleaning up old backups..."
    cleanup_old_backups
    
    echo ""
    echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  ✓ RESTORE COMPLETE${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}Restored from:${NC} $RESTORE_BACKUP"
    echo -e "${GREEN}Environment:${NC} $RESTORE_MODE"
    echo -e "${GREEN}Pre-restore backup:${NC} $PRERESTORE_BACKUP"
    echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
    echo ""
    
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