# Security Policy

## Supported versions

This is a starter / reference implementation, not a long-lived versioned product. Security fixes are applied to `main`.

| Version | Supported |
| ------- | --------- |
| `main`  | ✅        |

## Reporting a vulnerability

**Do not file public GitHub issues for security vulnerabilities.**

Report privately via GitHub's [Security Advisories](https://github.com/epas-platform/starter/security/advisories/new). If you cannot use that channel, email the maintainer listed in [`CODEOWNERS`](CODEOWNERS).

Please include:

- A description of the issue and its impact.
- Steps to reproduce or a proof of concept.
- The affected commit SHA or component (backend / frontend / infra / profile bundle).

## Response expectations

- Acknowledgement within **2 business days**.
- Triage and severity assessment within **5 business days**.
- Coordinated disclosure: default embargo is 90 days from acknowledgement or until a fix ships, whichever is earlier.

## Scope

In scope: code, configuration, and profile bundles in this repository.

Out of scope: vulnerabilities in the third-party dependencies themselves (FastAPI, Next.js, Postgres, Redis, LocalStack) — report those upstream. We will still consume security advisories from those projects and update pinned versions in `requirements.txt` / `package.json` accordingly.
