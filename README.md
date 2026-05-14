# EPAS Prototype

Prototype starter for relational-operational applications.

## Stack

- **Backend**: FastAPI (Python 3.11)
- **Frontend**: Next.js 14 (TypeScript)
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **AWS Emulation**: LocalStack (S3, Secrets Manager)
- **Containerization**: Docker Compose

## Quick Start

```bash
# Start all services
docker compose up

# Or run in background
make up
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

## Available Pages

- **Dashboard**: /dashboard
- **Workspaces**: /workspaces
- **Runs**: /runs
- **Settings**: /settings

## Common Commands

```bash
make up              # Start services (background)
make down            # Stop services
make logs            # View logs
make shell-backend   # Backend shell
make shell-frontend  # Frontend shell
make test            # Run tests
make reset           # Reset everything
```

## Configuration

This project was configured with:
- **Primary Color**: green
- **Pages**: Dashboard, Workspaces, Runs, Settings

## Profile Bundle

- **Bundle**: EPAS Prototype - Relational
- **EPAS Lifecycle**: prototype
- **Audience**: internal_platform
- **Environment**: local_dev
- **Data Model**: relational_operational
- **Primary Stack**: PostgreSQL


To reconfigure, edit `quickstart.config.json` and run:
```bash
python scripts/configure.py --from-file
```

To apply a profile bundle, run:
```bash
python scripts/configure.py --bundle <bundle-id> --yes
```

Or run interactively:
```bash
python scripts/configure.py
```

## License

MIT
