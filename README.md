# Lesson Organizer

A full-stack web application for managing English language learning programs at Toward the Goal English. The system tracks student progress across curriculum levels, manages lesson plans, and provides quiz assessments with comprehensive reporting.

## Overview

**Lesson Organizer** is a production-ready education management platform that handles student enrollment, curriculum progression, lesson scheduling, and assessment tracking. Built with modern web technologies and deployed with containerization, the application supports multiple instructors managing dozens of students across structured curriculum levels.

### Key Features

- **Student Management**: Track student enrollment, current level, lesson history, and status changes
- **Curriculum Organization**: Hierarchical structure (Curriculum → Levels → Units → Lessons)
- **Lesson Scheduling**: Assign lessons to students with completion tracking
- **Quiz System**: Create and administer quizzes with automatic scoring
- **Progress Tracking**: Monitor student advancement through curriculum levels
- **Multi-user Support**: Role-based access (Admin, Instructor, Assistant)
- **RESTful API**: Full backend API for programmatic access

## Tech Stack

### Backend
- **Python 3.12** with **Flask 3.1** - Web framework
- **SQLAlchemy 2.0** - ORM with SQLite database
- **Flask-JWT-Extended** - JWT authentication with secure cookie-based sessions
- **Flask-Security** - User management and password hashing (bcrypt)
- **Marshmallow** - Request/response serialization and validation
- **Gunicorn** - Production WSGI server with multi-worker support
- **Flask-Migrate** - Database migration management (Alembic)

### Frontend
- **SvelteKit 2.15** with **Svelte 5** - Modern reactive framework using Runes
- **TypeScript 5.7** - Type-safe development
- **Tailwind CSS 4.0** - Utility-first styling
- **DaisyUI 5.0** - UI component library
- **Vite 6.2** - Fast build tooling

### Infrastructure
- **Docker** & **Docker Compose** - Containerization and orchestration
- **Caddy 2** - Reverse proxy with automatic HTTPS (Let's Encrypt)
- **GitHub Actions** - CI/CD pipeline
- **Tailscale** - Secure remote access (optional)

### Architecture

```
┌─────────────────────────────────────────────┐
│         Caddy Reverse Proxy (HTTPS)         │
│              goal-english.com               │
└────────────┬──────────────┬─────────────────┘
             │              │
    ┌────────▼──────┐  ┌───▼───────────┐
    │   Frontend    │  │    Backend    │
    │ SvelteKit +   │  │  Flask API +  │
    │   Node.js     │  │   Gunicorn    │
    │  (Port 4173)  │  │  (Port 4000)  │
    └───────────────┘  └───────┬───────┘
                               │
                       ┌───────▼────────┐
                       │  SQLite DB     │
                       │   (Volume)     │
                       └────────────────┘
```

## Getting Started

### Prerequisites

- **Docker** (20.10+) and **Docker Compose** (2.0+)
- **Python 3.10+** (for local development without Docker)
- **Node.js 18+** (for frontend development)

### Initial Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Elliot-TTGE/lesson-organizer.git
   cd lesson-organizer
   ```

2. **Generate security secrets**:
   ```bash
   # Generate three unique secrets (run three times)
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```

3. **Configure environment variables**:
   
   Create `.env.local` for local development:
   ```bash
   cp .env.example .env.local
   ```
   
   Edit `.env.local` and set:
   - Admin user credentials (`ADMIN_EMAIL`, `ADMIN_PASSWORD`, etc.)
   - Security secrets (paste generated values from step 2):
     - `SECRET_KEY` - Flask session encryption
     - `JWT_SECRET_KEY` - JWT token signing
     - `SECURITY_PASSWORD_SALT` - Password reset tokens
   
   For production, create `.env.prod` with production values:
   ```bash
   cp .env.example .env.prod
   # Edit with production credentials and secrets
   # Add CLOUDFLARE_API_TOKEN if using Caddy with Cloudflare DNS
   ```

4. **Make run script executable**:
   ```bash
   chmod +x run.sh
   ```

### Running the Application

#### Development Mode

Start with hot-reload for both frontend and backend:
```bash
./run.sh dev
# Or: docker compose up
```

Access the application:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:4000
- **API Docs**: http://localhost:4000/api/

Development features:
- Live code reloading (changes reflect immediately)
- Detailed error pages with stack traces
- Flask debugger enabled
- Source maps for debugging

#### Production Mode

Build and run with production optimizations:
```bash
./run.sh prod
# Or: docker compose -f compose.prod.yml up
```

Production features:
- Gunicorn with 4 worker processes (concurrent request handling)
- Minified and optimized frontend build
- HTTPS via Caddy with automatic SSL certificates
- Secure cookie settings enabled
- No debugger or verbose errors

#### Production with Tailscale (Remote Access)

For secure remote access without exposing ports:
```bash
# Set TS_AUTH_KEY in .env.prod.tailscale first
docker compose -f compose.prod.tailscale.yml up
```

### Stopping Services

```bash
# Development
docker compose down

# Production
docker compose -f compose.prod.yml down
```

## Development Workflow

### Database Migrations

Database schema changes are managed with Flask-Migrate:

```bash
# Access backend container
docker compose exec backend sh

# Create a new migration after model changes
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback last migration
flask db downgrade
```

Migrations run automatically on container startup via `entrypoint.py`.

### Project Structure

```
lesson-organizer/
├── backend-flask/          # Flask API
│   ├── app/
│   │   ├── models/        # SQLAlchemy models
│   │   ├── routes/        # API endpoints
│   │   ├── schemas/       # Marshmallow schemas
│   │   ├── services/      # Business logic
│   │   └── data/          # Data initialization
│   ├── migrations/        # Alembic migrations
│   └── requirements.txt   # Python dependencies
│
├── frontend-svelte/       # SvelteKit app
│   ├── src/
│   │   ├── routes/       # Page components
│   │   ├── lib/          # Shared components
│   │   ├── api/          # API client
│   │   └── types/        # TypeScript types
│   └── package.json      # Node dependencies
│
├── caddy/                # Reverse proxy config
├── .github/workflows/    # CI/CD pipelines
└── compose*.yml          # Docker orchestration
```

### API Development

The backend provides a RESTful API with the following endpoints:

- `POST /api/login` - User authentication
- `GET /api/students` - List all students
- `GET /api/lessons` - List all lessons
- `GET /api/curriculum` - Get curriculum structure
- `POST /api/student-lesson-quiz` - Submit quiz results

All protected endpoints require JWT authentication via HTTP-only cookies.

### Environment-Specific Configuration

The application uses different configurations per environment:

| File | Environment | Purpose |
|------|-------------|---------|
| `.env.local` | Local development | Hot reload, verbose logging |
| `.env.prod.local` | Local production test | Test production build locally |
| `.env.prod` | Production deployment | Live environment |
| `.env.prod.tailscale` | Remote Tailscale access | Secure remote deployment |

## Security Features

- **JWT Authentication**: Secure, stateless authentication with 5-hour token expiration
- **HTTP-Only Cookies**: Tokens stored securely, inaccessible to JavaScript (prevents XSS)
- **Bcrypt Password Hashing**: Industry-standard password protection
- **Environment-based Secrets**: No hardcoded credentials in source code
- **Automatic HTTPS**: Caddy handles SSL certificate provisioning and renewal
- **CORS Protection**: Configured for specific origins
- **Secure Cookie Settings**: HTTPS-only cookies in production

## Deployment

### Local Production Testing

Test production build without deploying:
```bash
docker compose -f compose.prod.local.yml up --build
```

### Production Deployment

1. **Set up production server** with Docker and Docker Compose installed

2. **Configure environment**:
   - Copy `.env.prod` to server
   - Set domain in `caddy/Caddyfile`
   - Add DNS A record pointing to server IP

3. **Deploy**:
   ```bash
   # Pull latest code
   git pull origin main
   
   # Build and start services
   docker compose -f compose.prod.yml up --build -d
   ```

4. **Verify deployment**:
   - Caddy automatically provisions SSL certificate
   - Access at https://your-domain.com
   - Check logs: `docker compose -f compose.prod.yml logs -f`

### CI/CD Pipeline

GitHub Actions automatically:
- Runs on push to `main` branch
- Builds Docker images
- Runs linting and type checking
- Builds production frontend
- Pushes images to GitHub Container Registry

## Database Schema

The application uses a relational database with the following core models:

- **User**: Instructor/admin accounts with role-based permissions
- **Student**: Enrolled students with status tracking
- **Curriculum**: Top-level curriculum (e.g., "Elementary English")
- **Level**: Curriculum levels (e.g., "Level 1", "Level 2")
- **Unit**: Units within levels (e.g., "Unit 1: Greetings")
- **Lesson**: Individual lessons with content
- **Quiz**: Assessments with questions
- **StudentLessonQuiz**: Student quiz attempts and scores
- **StudentLevelHistory**: Student progression through levels
- **StudentStatusHistory**: Changes in student enrollment status

## Performance Considerations

- **Backend**: Gunicorn with 4 workers handles concurrent requests efficiently
- **Frontend**: Static asset generation with SvelteKit for fast initial loads
- **Database**: SQLite suitable for small-to-medium deployments (dozens of concurrent users)
- **Caching**: Static assets cached by Caddy with proper headers

For larger deployments (100+ concurrent users), consider:
- Migrating to PostgreSQL
- Increasing Gunicorn workers
- Adding Redis for session storage
- Implementing CDN for static assets

## Contributing

This is a personal project for Toward the Goal English. For questions or suggestions, please open an issue.

## License

All rights reserved. This software is proprietary to Toward the Goal English.