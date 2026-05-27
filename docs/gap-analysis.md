# Toolcradle Gap Analysis

Comprehensive comparison between **toolcradle** (current state) and **engineering-standards** (target state).

---

## Executive Summary

Toolcradle is a solid foundation with good abstractions (SecretVault, BlobStore, AuditLogger), but is missing the fundamental **API-first microservices architecture** where all interfaces consume the core API through a shared SDK. It also uses a simplified auth model suitable for prototyping rather than the enterprise-grade OIDC + ReBAC stack. This analysis identifies all gaps and proposes a phased update plan.

---

## 0. API-First Microservices Architecture (CRITICAL)

### Current State (Toolcradle)

```
┌──────────────┐    ┌──────────────┐
│   Frontend   │───▶│   FastAPI    │
│  (Next.js)   │    │   (backend/) │
└──────────────┘    └──────────────┘
```

Single monolithic structure. Frontend calls API directly. No SDK, no MCP, no CLI.

### Target State (Engineering Standards)

**Design Principle**: API-first microservices. All interfaces consume the core API through the SDK.

```
┌─────────────────┐
│   Claude/AI     │
│   (via MCP)     │
└────────┬────────┘
         │
┌──────────────┐    ┌────────▼────────┐    ┌──────────────┐
│     CLI      │───▶│   Python SDK    │◀───│  n8n / Other │
│  (cradle)    │    │  (cradle-sdk)   │    │   Services   │
└──────────────┘    └────────┬────────┘    └──────────────┘
                             │
                    ┌────────▼────────┐
                    │    MCP Server   │
                    │  (cradle-mcp)   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   Cradle API    │
                    │    (FastAPI)    │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
┌────────▼────────┐ ┌────────▼────────┐ ┌────────▼────────┐
│   PostgreSQL    │ │     Redis       │ │   Event Bus     │
│   + pgvector    │ │    (cache)      │ │  (NATS/Kafka)   │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

### Interface Layers

| Layer | Package | Purpose | Current State |
|-------|---------|---------|---------------|
| **API** | `cradle-api` | Core REST service, source of truth | ✅ Exists (`backend/`) |
| **SDK** | `cradle-sdk` | Python client library for programmatic access | ❌ **Missing** |
| **MCP Server** | `cradle-mcp` | Expose tools to Claude/AI agents (uses SDK) | ❌ **Missing** |
| **CLI** | `cradle-cli` | Terminal interface (uses SDK) | ❌ **Missing** |
| **Frontend** | `cradle-web` | Next.js UI | ✅ Exists (`frontend/`) |

### Why This Matters

The SDK is the **single source of client logic**:

1. **No duplication** - MCP tools don't reimplement API calls
2. **No duplication** - CLI doesn't reimplement API calls
3. **No duplication** - n8n custom nodes use the SDK
4. **Type safety** - Pydantic models shared between SDK and API
5. **Versioning** - SDK version tracks API version
6. **Testing** - SDK is the integration test surface

### Gap Items

- [ ] **Restructure to monorepo** - `packages/` or separate repos
- [ ] **Create `cradle-sdk`** - Python client with async support
- [ ] **Create `cradle-mcp`** - MCP server using SDK
- [ ] **Create `cradle-cli`** - CLI using SDK (Click or Typer)
- [ ] **Rename `backend/` → `api/`** - Clarity
- [ ] **Rename `frontend/` → `web/`** - Clarity
- [ ] **Add shared types package** - Or generate from OpenAPI

### Proposed Package Structure

```
toolcradle/
├── packages/
│   ├── api/                    # FastAPI service (was backend/)
│   │   ├── app/
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   │
│   ├── sdk/                    # Python SDK
│   │   ├── cradle/
│   │   │   ├── __init__.py
│   │   │   ├── client.py       # CradleClient class
│   │   │   ├── models.py       # Pydantic models (shared or generated)
│   │   │   ├── auth.py         # Auth utilities
│   │   │   ├── users.py        # Users resource
│   │   │   └── exceptions.py   # SDK exceptions
│   │   └── pyproject.toml
│   │
│   ├── mcp/                    # MCP Server
│   │   ├── cradle_mcp/
│   │   │   ├── __init__.py
│   │   │   ├── server.py       # FastMCP server
│   │   │   ├── tools.py        # Tool definitions (uses SDK)
│   │   │   └── resources.py    # Resource definitions
│   │   └── pyproject.toml
│   │
│   ├── cli/                    # CLI Tool
│   │   ├── cradle_cli/
│   │   │   ├── __init__.py
│   │   │   ├── main.py         # Typer app
│   │   │   └── commands/       # Command modules
│   │   └── pyproject.toml
│   │
│   └── web/                    # Next.js frontend (was frontend/)
│       ├── src/
│       ├── package.json
│       └── Dockerfile
│
├── docker-compose.yml
├── pyproject.toml              # Workspace root (optional, for uv/poetry)
└── README.md
```

### SDK Design Pattern

```python
# packages/sdk/cradle/client.py
from cradle.users import UsersResource
from cradle.auth import AuthResource

class CradleClient:
    """Cradle API client."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: str | None = None,
        access_token: str | None = None,
    ):
        self._base_url = base_url
        self._session = httpx.AsyncClient(...)

        # Resource namespaces
        self.users = UsersResource(self)
        self.auth = AuthResource(self)

    async def request(self, method: str, path: str, **kwargs) -> Any:
        """Make authenticated request to API."""
        ...

# Usage:
client = CradleClient(api_key="...")
user = await client.users.get("user-id")
users = await client.users.list(limit=10)
```

### MCP Uses SDK

```python
# packages/mcp/cradle_mcp/tools.py
from cradle import CradleClient

client = CradleClient(api_key=os.environ["CRADLE_API_KEY"])

@mcp.tool()
async def get_user(user_id: str) -> User:
    """Get a user by ID."""
    return await client.users.get(user_id)

@mcp.tool()
async def list_users(limit: int = 10) -> list[User]:
    """List users."""
    return await client.users.list(limit=limit)
```

### CLI Uses SDK

```python
# packages/cli/cradle_cli/commands/users.py
import typer
from cradle import CradleClient

app = typer.Typer()
client = CradleClient()

@app.command()
def get(user_id: str):
    """Get a user by ID."""
    user = asyncio.run(client.users.get(user_id))
    typer.echo(user.model_dump_json(indent=2))

@app.command()
def list(limit: int = 10):
    """List users."""
    users = asyncio.run(client.users.list(limit=limit))
    for user in users:
        typer.echo(f"{user.id}: {user.email}")
```

---

## 1. Authentication & Authorization

### Current State (Toolcradle)

| Component | Implementation |
|-----------|----------------|
| Auth method | Email/password with bcrypt |
| Token type | Self-issued JWT (HS256) |
| Token storage | LocalStorage (frontend) |
| Session management | Manual token refresh |
| Authorization | Simple role array in JWT (`["user", "admin"]`) |
| Identity provider | None (self-managed users table) |

### Target State (Engineering Standards)

| Component | Implementation |
|-----------|----------------|
| Auth method | OIDC via external IdP |
| SSO Provider | Zitadel (or any OIDC-compliant IdP) |
| Frontend auth | NextAuth v5 |
| Token type | IdP-issued JWT with claims |
| Authorization | OpenFGA (ReBAC) |
| Tenant resolution | From OIDC claims |
| Service-to-service | API Keys or OAuth2 client credentials |

### Gap Items

- [ ] **Remove email/password auth** - Replace with OIDC redirect flow
- [ ] **Remove local User table auth fields** - No more `hashed_password`
- [ ] **Add NextAuth v5** - Handle OIDC on frontend
- [ ] **Add OIDC token validation** - Backend validates IdP tokens, not self-issued
- [ ] **Add OpenFGA integration** - Permission checks via ReBAC
- [ ] **Add tenant claim extraction** - Multi-tenant from claims
- [ ] **Add API key auth for SDK/CLI** - Service account pattern

---

## 2. Secrets Management

### Current State (Toolcradle)

| Component | Implementation |
|-----------|----------------|
| Abstraction | SecretVault (good!) |
| Dev implementation | LocalStack Secrets Manager |
| Prod implementation | AWS Secrets Manager |
| Fallback | Environment variables |

### Target State (Engineering Standards)

| Component | Implementation |
|-----------|----------------|
| Abstraction | SecretVault (keep) |
| Primary store | OpenBao (HashiCorp Vault fork) |
| Auth method | AppRole |
| Encryption | Transit engine for field-level encryption |
| Per-tenant | Separate mounts/keys per tenant |

### Gap Items

- [ ] **Add OpenBaoSecretVault implementation** - hvac client with AppRole auth
- [ ] **Add Transit encryption abstraction** - For field-level encryption
- [ ] **Remove LocalStack dependency** - Optional, not required
- [ ] **Update config** - `VAULT_ADDR`, `VAULT_ROLE_ID`, `VAULT_SECRET_ID`

---

## 3. Object Storage

### Current State (Toolcradle)

| Component | Implementation |
|-----------|----------------|
| Abstraction | BlobStore (good!) |
| Implementation | S3 via LocalStack or AWS |
| Features | Put, get, delete, presigned URLs, list |

### Target State (Engineering Standards)

| Component | Implementation |
|-----------|----------------|
| Abstraction | BlobStore (keep) |
| Implementation | S3-compatible (MinIO, actual S3, etc.) |
| Tenant isolation | Key prefix namespacing |

### Gap Items

- [ ] **Add MinIO as default dev option** - Instead of LocalStack
- [ ] **Add tenant namespace helper** - `{tenant_id}/{path}` key prefixing
- [ ] **LocalStack optional** - Not a hard dependency

---

## 4. Audit Logging

### Current State (Toolcradle)

| Component | Implementation |
|-----------|----------------|
| Abstraction | AuditLogger (good!) |
| Schema | Who/What/When/Context (good!) |
| Data classification | 4 levels (good!) |
| Storage | PostgreSQL or structured logs |

### Target State (Engineering Standards)

| Component | Implementation |
|-----------|----------------|
| Schema | Matches (good!) |
| Immutability | S3 with Object Lock (WORM) |
| Retention | 7 years minimum |
| Access reason | Required for restricted data |

### Gap Items

- [ ] **Add S3 archival for audit logs** - WORM storage for compliance
- [ ] **Add access_reason field** - Required for restricted data queries
- [ ] **Add support_ticket_id field** - For break-glass access
- [ ] **Verify REVOKE UPDATE/DELETE** - Immutability enforcement

---

## 5. Event-Driven Architecture

### Current State (Toolcradle)

**None** - No event publishing or subscription.

### Target State (Engineering Standards)

| Component | Implementation |
|-----------|----------------|
| Event bus | NATS JetStream (or Kafka/Redpanda) |
| Format | CloudEvents 1.0 |
| Pattern | Transactional outbox |
| Naming | `dev.ravenhelm.{domain}.{entity}.{action}` |

### Gap Items

- [ ] **Add CloudEvents schema** - Pydantic model for envelope
- [ ] **Add event_outbox table** - For transactional outbox pattern
- [ ] **Add outbox publisher** - Background worker to publish pending events
- [ ] **Add NATS client abstraction** - EventBus interface
- [ ] **Add event publishing to models** - Emit events on create/update/delete

---

## 6. Observability

### Current State (Toolcradle)

| Component | Implementation |
|-----------|----------------|
| Logging | Structured JSON (good!) |
| Metrics | None |
| Tracing | None |
| LLM observability | None |

### Target State (Engineering Standards)

| Component | Implementation |
|-----------|----------------|
| Metrics | Prometheus (service_requests_total, etc.) |
| Logs | Loki-compatible JSON |
| Traces | OpenTelemetry → Tempo |
| LLM observability | Langfuse |
| Dashboards | Grafana |

### Gap Items

- [ ] **Add Prometheus metrics** - FastAPI middleware with prometheus_client
- [ ] **Add required metrics** - `service_requests_total`, `service_request_duration_seconds`, etc.
- [ ] **Add OpenTelemetry** - OTEL SDK + trace context propagation
- [ ] **Add trace_id to logs** - W3C trace context in structured logs
- [ ] **Add Langfuse integration** - Optional, for AI services
- [ ] **Add /metrics endpoint** - Prometheus scrape target

---

## 7. API Standards

### Current State (Toolcradle)

| Component | Implementation |
|-----------|----------------|
| Framework | FastAPI (good!) |
| Response format | Default FastAPI |
| Error format | Default HTTPException |
| Health check | `/health` (good!) |
| Readiness | `/ready` (implied) |

### Target State (Engineering Standards)

| Component | Implementation |
|-----------|----------------|
| Response format | `{ data: {}, meta: { requestId, timestamp, traceId } }` |
| Error format | `{ error: { code, message, details }, meta: {} }` |
| Versioning | `/api/v1/*` |
| OpenAPI | Full spec required |
| SDK | Generated from OpenAPI or hand-written |

### Gap Items

- [ ] **Add standard response wrapper** - `ApiResponse` model
- [ ] **Add standard error response** - RFC 7807-style errors
- [ ] **Add request_id to all responses** - From middleware
- [ ] **Add trace_id to all responses** - From OTEL context
- [ ] **Version API routes** - `/api/v1/` prefix

---

## 8. Database Patterns

### Current State (Toolcradle)

| Component | Implementation |
|-----------|----------------|
| ORM | SQLAlchemy async (good!) |
| Primary keys | UUID (good!) |
| Timestamps | created_at, updated_at (good!) |
| Tenant isolation | tenant_id column (good!) |
| RLS | Not implemented |
| Soft deletes | Not implemented |

### Target State (Engineering Standards)

| Component | Implementation |
|-----------|----------------|
| RLS | Row-level security policies |
| Soft deletes | deleted_at column |
| created_by | Audit field |
| Vectors | pgvector for embeddings |

### Gap Items

- [ ] **Add RLS policies** - `current_setting('app.tenant_id')` based
- [ ] **Add deleted_at** - Soft delete support
- [ ] **Add created_by** - User ID audit field
- [ ] **Add pgvector support** - Optional, for AI features
- [ ] **Add set_tenant_context()** - Set RLS context per request

---

## 9. AI Agent Safety (Optional)

### Current State (Toolcradle)

**None** - No AI agent patterns.

### Target State (Engineering Standards)

| Component | Implementation |
|-----------|----------------|
| Tool schemas | Pydantic with strict validation |
| Policy guardrails | Pre-flight permission checks |
| Risk tiers | Minimal/Limited/High/Prohibited |
| HITL | Human-in-the-loop for high-risk |
| Circuit breakers | Automatic suspension on anomaly |
| Model registry | ISO 42001 inventory |

### Gap Items (Optional - for AI services)

- [ ] **Add tool schema patterns** - Pydantic models for agent tools
- [ ] **Add policy guardrail node** - LangGraph pre-flight check
- [ ] **Add HITL abstraction** - Approval workflow integration
- [ ] **Add circuit breaker** - Agent suspension on threshold breach
- [ ] **Add model_registry table** - Track deployed models

---

## 10. Frontend Patterns

### Current State (Toolcradle)

| Component | Implementation |
|-----------|----------------|
| Framework | Next.js 14 (good!) |
| Styling | Tailwind + shadcn/ui (good!) |
| Auth | Manual JWT handling |
| State | Local state |
| Dark mode | next-themes (good!) |

### Target State (Engineering Standards)

| Component | Implementation |
|-----------|----------------|
| Framework | Next.js 15+ |
| React | React 19+ |
| Styling | Tailwind v4 |
| Auth | NextAuth v5 with OIDC |
| Permission checks | OpenFGA via API |
| AI disclosure | Required for AI content |

### Gap Items

- [ ] **Upgrade to Next.js 15+** - Latest stable
- [ ] **Add NextAuth v5** - OIDC integration
- [ ] **Add permission-aware rendering** - Check OpenFGA before showing features
- [ ] **Add AI disclosure component** - Already exists, verify usage
- [ ] **Fix lib/ gitignore issue** - `frontend/src/lib/` being excluded

---

## 11. Infrastructure

### Current State (Toolcradle)

| Component | Implementation |
|-----------|----------------|
| Containerization | Docker Compose (good!) |
| Dependencies | LocalStack, PostgreSQL, Redis |
| Health checks | Configured (good!) |
| Networking | Bridge network (good!) |

### Target State (Engineering Standards)

| Component | Implementation |
|-----------|----------------|
| Reverse proxy | Traefik with Let's Encrypt |
| Container registry | GitLab Container Registry |
| CI/CD | GitLab CI with lint/test/build/deploy |
| IaC | Terraform (optional) |

### Gap Items

- [ ] **Add Traefik labels** - For reverse proxy routing
- [ ] **Add .gitlab-ci.yml** - CI/CD pipeline
- [ ] **Add Dockerfile best practices** - Non-root user, healthcheck
- [ ] **Remove LocalStack hard dependency** - Make optional
- [ ] **Add Zitadel to compose** - For local OIDC development
- [ ] **Add OpenFGA to compose** - For local authorization

---

## 12. Security

### Current State (Toolcradle)

| Component | Implementation |
|-----------|----------------|
| CORS | Configured (good!) |
| Request size limit | 10MB (good!) |
| Headers | Not configured |
| Input validation | Pydantic (good!) |

### Target State (Engineering Standards)

| Component | Implementation |
|-----------|----------------|
| Headers | X-Frame-Options, CSP, etc. |
| Rate limiting | Per IP/user |
| mTLS | For service mesh (future) |
| OWASP | Top 10 addressed |

### Gap Items

- [ ] **Add security headers middleware** - X-Frame-Options, CSP, etc.
- [ ] **Enable rate limiting** - Already has config, need implementation
- [ ] **Add rate limit middleware** - slowapi or custom

---

## 13. Configuration

### Current State (Toolcradle)

| Component | Implementation |
|-----------|----------------|
| Pattern | Profile-based YAML (good!) |
| Profiles | dev, prod |
| Validation | Pydantic settings (good!) |

### Target State (Engineering Standards)

| Component | Implementation |
|-----------|----------------|
| Pattern | Profile-based (matches!) |
| Additional vars | OIDC config, OpenFGA, OpenBao |

### Gap Items

- [ ] **Add OIDC settings** - Issuer, client ID, audience
- [ ] **Add OpenFGA settings** - API URL, store ID
- [ ] **Add OpenBao settings** - Address, role ID, secret ID
- [ ] **Add Langfuse settings** - Keys and host (optional)

---

## 14. Miscellaneous Bugs

- [ ] **Fix `.gitignore`** - `lib/` excludes `frontend/src/lib/` (Python convention applied incorrectly)

---

## Summary: Priority Matrix

### P0 - Architecture (Foundation)

1. **Monorepo restructure** - `packages/api`, `packages/sdk`, `packages/mcp`, `packages/cli`, `packages/web`
2. **Create SDK** - Python client with async, typed models
3. **Create MCP Server** - Uses SDK, exposes tools
4. **Create CLI** - Uses SDK, Typer-based

### P1 - Auth & Security (Must Have)

5. **OIDC Authentication** - Replace JWT auth with external IdP
6. **NextAuth v5** - Frontend auth handling
7. **OpenFGA Authorization** - ReBAC permission checks
8. **API Key auth** - For SDK/CLI service accounts
9. **OpenBao Secrets** - Replace LocalStack Secrets Manager

### P2 - Compliance (Should Have)

10. **CloudEvents** - Event publishing
11. **Prometheus Metrics** - Observability
12. **OpenTelemetry** - Distributed tracing
13. **RLS Policies** - Database tenant isolation
14. **Standard API response format** - Wrapper with meta

### P3 - Polish (Nice to Have)

15. **Security headers** - Hardening
16. **Rate limiting** - Protection
17. **GitLab CI/CD** - Pipeline template
18. **Traefik labels** - Deployment ready

### P4 - AI Features (Optional)

19. **Langfuse integration** - LLM observability
20. **Agent safety patterns** - Guardrails, HITL
21. **Model registry** - AI governance
22. **pgvector** - Embeddings support

---

## Proposed Update Phases

### Phase 0: Architecture Restructure
**Goal**: Establish the SDK-first multi-package architecture.

- [ ] Restructure repo to `packages/` layout
- [ ] Rename `backend/` → `packages/api/`
- [ ] Rename `frontend/` → `packages/web/`
- [ ] Create `packages/sdk/` with CradleClient
- [ ] Create `packages/mcp/` using SDK
- [ ] Create `packages/cli/` using SDK
- [ ] Update docker-compose for new structure
- [ ] Fix `.gitignore` lib/ issue
- [ ] Add workspace-level pyproject.toml (uv/poetry)

### Phase 1: Auth Overhaul
**Goal**: Enterprise-grade auth with OIDC + ReBAC.

- [ ] Remove email/password auth from API
- [ ] Add OIDC token validation
- [ ] Add API key auth for SDK/CLI
- [ ] Add NextAuth v5 to web
- [ ] Add OpenFGA client
- [ ] Update User model (external_id, no password)
- [ ] Add Zitadel + OpenFGA to docker-compose

### Phase 2: Secrets & Storage
**Goal**: Production-ready secrets and storage.

- [ ] Add OpenBaoSecretVault implementation
- [ ] Make LocalStack optional
- [ ] Add MinIO as default S3 for dev
- [ ] Add Transit encryption abstraction

### Phase 3: Observability
**Goal**: Full observability stack.

- [ ] Add Prometheus metrics endpoint
- [ ] Add OpenTelemetry SDK
- [ ] Add trace correlation to logs
- [ ] Add standard API response wrapper

### Phase 4: Events & Compliance
**Goal**: Event-driven + compliance ready.

- [ ] Add CloudEvents schema
- [ ] Add transactional outbox
- [ ] Add RLS policies
- [ ] Add security headers
- [ ] Add audit log archival

### Phase 5: CI/CD & Polish
**Goal**: Deployment ready.

- [ ] Add GitLab CI template
- [ ] Add Traefik labels
- [ ] Add rate limiting
- [ ] Documentation

---

## Files to Create/Modify

### New Packages

```
packages/sdk/
├── cradle/
│   ├── __init__.py
│   ├── client.py
│   ├── models.py
│   ├── auth.py
│   ├── users.py
│   └── exceptions.py
├── pyproject.toml
└── README.md

packages/mcp/
├── cradle_mcp/
│   ├── __init__.py
│   ├── server.py
│   ├── tools.py
│   └── resources.py
├── pyproject.toml
└── README.md

packages/cli/
├── cradle_cli/
│   ├── __init__.py
│   ├── main.py
│   └── commands/
│       ├── __init__.py
│       └── users.py
├── pyproject.toml
└── README.md
```

### Modified Files

**API (was backend/)**
- `app/config.py` - Add OIDC, OpenFGA, OpenBao settings
- `app/core/security.py` - Replace JWT with OIDC + API key validation
- `app/api/auth.py` - Remove or repurpose for API key management
- `app/api/deps.py` - Add OpenFGA checks
- `app/models/user.py` - Remove hashed_password, add external_id
- `app/abstractions/secret_vault.py` - Add OpenBaoSecretVault
- `app/main.py` - Add metrics, OTEL middleware

**Web (was frontend/)**
- `src/app/(auth)/login/page.tsx` - Replace with OIDC redirect
- NEW: `src/app/api/auth/[...nextauth]/route.ts` - NextAuth handler
- NEW: `src/lib/auth.ts` - NextAuth utilities

**Infrastructure**
- `docker-compose.yml` - Add Zitadel, OpenFGA, restructure for packages
- `.gitignore` - Fix lib/ exclusion
- NEW: `.gitlab-ci.yml` - CI/CD pipeline
- NEW: `pyproject.toml` - Workspace root
