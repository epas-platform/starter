# Cradle

> *"The Regeneration Cradle - where new creations are born."*

Enterprise Multi-Platform Architecture Boilerplate. A production-ready foundation for building modern web applications.

## Stack

| Layer | Technology |
|-------|------------|
| **Backend** | FastAPI (Python 3.11) |
| **Frontend** | Next.js 14 (TypeScript) |
| **Database** | PostgreSQL 15 |
| **Cache** | Redis 7 |
| **UI** | Tailwind CSS + shadcn/ui |
| **AWS Emulation** | LocalStack (S3, Secrets Manager) |
| **Containerization** | Docker Compose |

## Quick Start

```bash
# Start all services
docker compose up

# Or run in background
docker compose up -d
```

Once running:
- **Frontend**: http://localhost:3010
- **Backend API**: http://localhost:8010
- **API Docs**: http://localhost:8010/docs

### Default Credentials

```
Email: admin@example.com
Password: password
```

## Features

### Authentication
- JWT-based auth with access/refresh tokens
- Login, register, token refresh endpoints
- Protected routes with automatic token refresh

### UI/UX
- Dark/Light mode with system preference support
- shadcn/ui components (Button, Card, Input, Toast, etc.)
- Responsive design with Tailwind CSS

### Backend
- Async SQLAlchemy with PostgreSQL
- Redis caching integration
- Profile-based configuration (dev/prod)
- Health and readiness endpoints
- CORS configured for local development

### Infrastructure
- Docker Compose orchestration
- LocalStack for AWS service emulation
- Hot reload for both frontend and backend
- Health checks on all services

### Abstractions
Based on the Enterprise Multi-Platform Architecture Specification:
- **SecretVault**: Unified interface for secrets management
- **BlobStore**: Unified interface for object storage (S3)
- **AuditLogger**: Compliance-ready audit logging foundation

## Project Structure

```
cradle/
├── backend/               # FastAPI application
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── abstractions/ # SecretVault, BlobStore, AuditLogger
│   │   ├── core/         # Middleware, security, context
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── db/           # Database session
│   └── tests/
│
├── frontend/              # Next.js application
│   └── src/
│       ├── app/          # App Router pages
│       ├── components/   # React components + shadcn/ui
│       ├── lib/          # API client, auth utilities
│       └── types/        # TypeScript types
│
├── config/                # Profile-based configuration
│   ├── profile.dev.yaml
│   └── profile.prod.yaml
│
├── infra/                 # Infrastructure setup
│   ├── localstack/       # AWS emulation init
│   └── postgres/         # Database init
│
└── docker-compose.yml     # Service orchestration
```

## Common Commands

```bash
# Start/Stop
docker compose up -d      # Start in background
docker compose down       # Stop all services
docker compose down -v    # Stop and remove volumes

# Logs
docker compose logs -f              # All services
docker compose logs -f backend      # Backend only
docker compose logs -f frontend     # Frontend only

# Shell access
docker compose exec backend bash    # Backend container
docker compose exec postgres psql -U cradle -d cradle  # Database

# Testing
docker compose exec backend bash -c "PYTHONPATH=/app pytest -v"

# Rebuild
docker compose up -d --build        # Rebuild and restart
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PROFILE` | `dev` | Configuration profile (dev/prod) |
| `DATABASE_URL` | (see compose) | PostgreSQL connection |
| `REDIS_URL` | (see compose) | Redis connection |
| `AWS_ENDPOINT_URL` | LocalStack | AWS endpoint override |
| `JWT_SECRET` | dev-secret | JWT signing key |

### Customization

Edit `quickstart.config.json` to customize:

```json
{
  "projectName": "Cradle",
  "description": "Enterprise Multi-Platform Architecture",
  "primaryColor": "blue",
  "features": {
    "darkMode": true,
    "multiTenant": true
  }
}
```

## API Endpoints

### Health
- `GET /health` - Basic health check
- `GET /ready` - Readiness check (DB, Redis)

### Auth
- `POST /auth/login` - Login with email/password
- `POST /auth/register` - Register new user
- `POST /auth/refresh` - Refresh access token

### Users
- `GET /users/me` - Current user profile
- `PATCH /users/me` - Update profile
- `GET /users` - List users (admin)

## Production Deployment

For production:
1. Set `PROFILE=prod`
2. Use real AWS services (remove `AWS_ENDPOINT_URL`)
3. Set strong `JWT_SECRET`
4. Configure proper `CORS_ORIGINS`
5. Use managed PostgreSQL and Redis
6. Enable rate limiting

## License

MIT
