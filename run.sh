#!/bin/bash

# Function to display usage
usage() {
  echo "Usage: $0 {MODE} [docker-compose-commands...]"
  echo ""
  echo "DOCKER COMMAND WRAPPERS:"
  echo "  dev         - Development mode with hot reload (docker compose --env-file .env.dev)"
  echo "  prod        - Production deployment (docker compose -f compose.prod.yml --env-file .env.prod)"
  echo "  prod-local  - Test production builds locally (docker compose -f compose.prod.local.yml --env-file .env.prod.local)"
  echo ""
  echo "EXCLUSIVE COMMANDS:"
  echo "  clean       - Clean up all Docker containers, images, and volumes"
  echo "  backup      - Create timestamped database backup in ./db_backups/"
  echo ""
  echo "Examples:"
  echo "  $0 dev up -d                    # Start development environment in background"
  echo "  $0 prod-local build --no-cache  # Build production images locally without cache"
  echo "  $0 clean                        # Clean up Docker resources"
  echo "  $0 backup                       # Backup database"
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
    BASE_COMMAND="docker compose --env-file .env.dev"
    ;;
  prod)
    BASE_COMMAND="docker compose -f compose.prod.yml --env-file .env.prod"
    ;;
  prod-local)
    BASE_COMMAND="docker compose -f compose.prod.local.yml --env-file .env.prod.local"
    ;;
  clean)
    echo "Cleaning up Docker containers, images, and volumes..."
    docker-compose down --volumes --rmi all
    echo "Cleanup complete."
    exit 0
    ;;
  backup)
    TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
    BACKUP_FILE="backup-$TIMESTAMP.db"
    echo "Backing up database to ./db_backups/$BACKUP_FILE"
    docker run --rm \
      -v lesson-organizer_backend_db:/db \
      -v "$(pwd)/db_backups":/backup \
      alpine \
      cp /db/lesson_organizer.db /backup/$BACKUP_FILE
    echo "Backup complete."
    exit 0
    ;;
  *)
    usage
    ;;
esac

# Execute the constructed command (only for docker wrapper modes)
COMMAND="$BASE_COMMAND $*"
echo "Running: $COMMAND"
eval $COMMAND