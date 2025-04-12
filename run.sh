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
    echo "Running in production mode..."
    docker compose -f compose.yml -f compose.prod.yml --env-file .env.prod up -d
    ;;
  clean)
    echo "Cleaning up Docker containers, images, and volumes..."
    docker-compose down --volumes --rmi all
    echo "Cleanup complete."
    ;;
  *)
    usage
    ;;
esac

# Execute the constructed command
COMMAND="$BASE_COMMAND $*"
echo "Running: $COMMAND"
eval $COMMAND