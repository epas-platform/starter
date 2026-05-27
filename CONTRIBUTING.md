# Contributing

Thanks for contributing to the EPAS starter.

This repo is a **starter / reference implementation**. Changes here become the default new-project shape for EPAS-aligned applications, so we keep the layout deliberately conservative.

## Local setup

```bash
# Start the full stack (Postgres, Redis, LocalStack, backend, frontend)
make up

# Tear down
make down

# Reset everything (volumes included)
make reset
```

Service URLs once running:

- Frontend: <http://localhost:3010>
- Backend API: <http://localhost:8010>
- API docs: <http://localhost:8010/docs>

## Branching

- Branch from `main` using `feat/<topic>` or `fix/<topic>`.
- Open a PR; do not push directly to `main`.

## Commits

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>
```

Common types: `feat`, `fix`, `chore`, `refactor`, `docs`, `test`, `ci`.

## Pre-PR checks

```bash
make test           # backend pytest + frontend unit tests
```

Add equivalents for any new package you introduce.

## Profile bundles

The starter ships with both relational and entity-native profile bundles in `profiles/`. When changing schemas or seed data, update **all** affected bundle variants (prototype / mvp / demo / production) to keep them in sync.

## Pull requests

- One concern per PR.
- Update `CHANGELOG.md` under `[Unreleased]` for any user-visible change.
- Update affected docs in `docs/`.

## Reporting issues

File issues on the repo. For security issues, follow [`SECURITY.md`](SECURITY.md) — do not file public issues for vulnerabilities.
