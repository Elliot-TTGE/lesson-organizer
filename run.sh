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
  echo "  migrate     - Generate database migration (upgrade handled by entrypoint.py)"
  echo ""
  echo "Examples:"
  echo "  $0 dev up -d                    # Start development environment in background"
  echo "  $0 prod-local build --no-cache  # Build production images locally without cache"
  echo "  $0 clean                        # Clean up Docker resources"
  echo "  $0 backup                       # Backup database"
  echo "  $0 migrate \"Add user sharing\"     # Generate migration (applied on container restart)"
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
  migrate)
    if [ "$#" -lt 1 ]; then
      echo "Error: Migration message is required"
      echo "Usage: $0 migrate \"Migration message\""
      exit 1
    fi
    MIGRATION_MESSAGE="$1"
    echo "Generating database migration with message: $MIGRATION_MESSAGE"
    
    # Function to run migration generation
    run_migration() {
      docker compose --env-file .env.dev exec backend flask db migrate -m "$MIGRATION_MESSAGE"
      echo "Migration file generated successfully!"
      echo "Note: Migration will be applied automatically when backend container restarts (handled by entrypoint.py)"
      echo ""
      echo "Current database version:"
      docker compose --env-file .env.dev exec backend flask db current
    }
    
    # Check if backend container is running
    if docker compose --env-file .env.dev ps backend | grep -q "Up"; then
      echo "Backend container is running, generating migration..."
      run_migration
    else
      echo "Backend container is not running, starting services..."
      docker compose --env-file .env.dev up -d backend
      sleep 5  # Give the container time to start
      echo "Generating migration..."
      run_migration
    fi
    
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