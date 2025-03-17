#!/bin/bash

# filepath: /Users/elliota/Development/lesson-organizer/run.sh

# Function to display usage
usage() {
  echo "Usage: $0 {dev|prod}"
  exit 1
}

# Check if the correct number of arguments is provided
if [ "$#" -ne 1 ]; then
  usage
fi

# Determine the mode based on the argument
MODE=$1

case $MODE in
  dev)
    echo "Running in development mode..."
    docker-compose --env-file .env.dev up
    ;;
  prod)
    echo "Running in production mode..."
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod up -d
    ;;
  *)
    usage
    ;;
esac