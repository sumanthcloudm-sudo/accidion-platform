# Accidion Identity Cloud

A multi-tenant Identity Governance and Administration (IGA) platform.

> **Status:** Repository scaffold. Directory structure is an implementation baseline, not evidence that services, integrations, controls, or infrastructure are implemented.

## Architecture and delivery principles

- MVP runtime: AWS ECS Fargate. Kubernetes assets remain inactive until an approved ADR.
- MVP messaging: Amazon SQS and EventBridge with transactional outbox patterns.
- Data: Aurora PostgreSQL initially; Valkey where approved.
- Workflow orchestration: Temporal Cloud.
- Authorization: fail closed; enforce tenant isolation at every trust boundary.
- AI Copilot: disabled by default; observe, reason, and recommend only. No autonomous execution.
- Infrastructure changes are plan-first and CI-controlled; no local production applies.

## Repository map

See [the engineering architecture](docs/engineering/architecture/README.md), [ADRs](docs/engineering/adr/README.md), [implementation plan](docs/engineering/implementation-plan/README.md), and [security policy](SECURITY.md).

## Getting started

This repository is initially a scaffold. Follow [CONTRIBUTING.md](CONTRIBUTING.md) before adding implementation code. Run `make help` to see available local validation targets as they are implemented.

## Security

Report vulnerabilities privately as described in [SECURITY.md](SECURITY.md). Never commit credentials, customer data, production exports, or secret material.
