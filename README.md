**A lesson organizer for Toward the Goal English**

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Setup

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/lesson-organizer.git
   cd lesson-organizer
   ```

2. Create environment variable files:
   - `.env.dev` for development:
     ```sh
     cp .env.example .env.dev
     # Edit .env.dev with your development environment variables
     ```

   - `.env.prod` for production:
     ```sh
     cp .env.example .env.prod
     # Edit .env.prod with your production environment variables
     ```

3. Make the script executable:
   ```sh
   chmod +x run.sh
   ```

### Running the Application

To run the application, use the `run.sh` script with the appropriate mode:

- For development:
  ```sh
  ./run.sh dev
  ```

- For production:
  ```sh
  ./run.sh prod
  ```

### Stopping the Services

To stop the services, run:

```sh
docker-compose down
```

For production, use:

```sh
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
```

### Additional Information

- The backend service is built using Python and Flask.
- The frontend service is built using Node.js and Svelte.
- Tailscale is used for secure networking in production.
- Caddy is used as a web server and reverse proxy in production.

For more detailed information, refer to the individual Dockerfiles and Docker Compose files.