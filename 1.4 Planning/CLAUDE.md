# EPAS Starter - Agent Context

## Project Overview

EPAS Starter is the reference implementation of the Enterprise Platform Architecture Specification (EPAS). This codebase demonstrates how to implement EPAS standards in a real application with FastAPI backend and Next.js frontend.

## Tech Stack

- **Language**: Python 3.11+
- **API Framework**: FastAPI
- **Frontend**: Next.js 14 (upgrading to 15)
- **Database**: PostgreSQL + Redis
- **ORM**: SQLAlchemy async
- **Styling**: Tailwind + shadcn/ui

## Current State

The starter is a functional boilerplate but needs updates to align with EPAS v1.4:
- Uses simple JWT auth (needs OIDC + OpenFGA)
- Monolithic structure (needs SDK-first packages)
- No MCP server or CLI

## Coding Standards

- Always use async/await for I/O operations
- Use Pydantic for all data validation
- Follow repository pattern for database access
- Use abstractions (SecretVault, BlobStore, AuditLogger)

## Architecture Rules (Target State)

- All interfaces (CLI, MCP, frontend) must use the SDK
- Never make direct API calls from CLI or MCP tools
- Events published via transactional outbox
- Auth via OIDC tokens, not self-issued JWTs

## Key Abstractions

### SecretVault (`backend/app/abstractions/secret_vault.py`)
- Use for all secret retrieval
- Current: LocalStack/AWS Secrets Manager
- Target: OpenBao

### BlobStore (`backend/app/abstractions/blob_store.py`)
- Use for all file storage
- S3-compatible interface

### AuditLogger (`backend/app/abstractions/audit_logger.py`)
- Use for all audit events
- Includes data classification

## Common Mistakes to Avoid

- Don't hardcode environment-specific values
- Don't bypass the SecretVault abstraction
- Don't add auth logic outside the security module
- Don't create new endpoints without SDK method planning

## Testing Requirements

- All new code requires unit tests
- Integration tests for API endpoints
- Mock external services in tests

## Agent Guardrails

### Allowed Operations
- Create/modify files in /backend, /frontend
- Run tests via `pytest`
- Run linting via `ruff`
- Update docker-compose.yml

### Approval Required
- Database migrations
- Changes to authentication
- New external dependencies
- Restructuring to packages/ layout

### Prohibited Operations
- Never commit secrets or API keys
- Never modify .env files to include real credentials
- Never remove existing abstractions without replacement
