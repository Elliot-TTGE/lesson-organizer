#!/bin/bash

# Function to display usage
usage() {
  echo "Usage: $0 {dev|prod|clean} [docker-compose-commands...]"
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
    BASE_COMMAND="docker compose -f compose.yml -f compose.prod.yml --env-file .env.prod"
    ;;
  clean)
    echo "Cleaning up Docker containers, images, and volumes..."
    docker-compose down --volumes --rmi all
    echo "Cleanup complete."
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
    ;;
  *)
    usage
    ;;
esac

# Execute the constructed command
COMMAND="$BASE_COMMAND $*"
echo "Running: $COMMAND"
eval $COMMAND