# Accidion AI Module

## Purpose

The `ai/` directory is the product-engineering area for AI capabilities that may be incorporated into Accidion Identity Cloud. It is not the configuration directory for developer tools such as Codex or Claude Code.

Accidion Identity Cloud is a multi-tenant Identity Governance and Administration (IGA) platform. Any product AI capability must operate within the platform's identity, authorization, tenant-isolation, governance, privacy, and audit boundaries.

## Status and authority

This directory currently establishes documentation and intended organisation. A directory or design description is not evidence that a service, control, provider integration, evaluation suite, or production capability exists.

The repository's root `AGENTS.md`, `RULES.md`, `docs/ARCHITECTURE.md`, accepted Architecture Decision Records (ADRs), security policies, and maintainer decisions remain authoritative. Documents in this directory supplement those sources; they never override them.

The six-month MVP plan governs delivery scope. The current product AI boundary, if enabled and approved for the MVP, is limited to **observe, reason, and recommend**. AI Copilot remains disabled by default. Autonomous execution and autonomous access provisioning are out of scope.

## Directory responsibilities

| Directory | Intended responsibility |
| --- | --- |
| `gateway/` | Controlled application boundary for AI requests, provider routing, request validation, timeouts, and response normalisation. |
| `providers/` | Adapters for explicitly approved model providers. Provider-specific details must not leak into business-domain services. |
| `prompts/` | Versioned, reviewed prompt templates and their metadata. Prompts are not a substitute for authorization or deterministic policy. |
| `guardrails/` | Input/output safety checks, data minimisation, injection-aware handling, and policy enforcement around model interactions. |
| `policies/` | Product rules defining permitted AI use cases, data handling, model capabilities, and prohibited behaviour. |
| `evaluations/` | Repeatable quality, safety, regression, and adversarial evaluations for AI behaviour. |
| `audit/` | Audit event definitions and integration guidance for AI requests, model/version metadata, outcomes, and human review where applicable. |

These are intended responsibilities, not claims that implementations exist.

## Product boundaries

- AI may explain, summarise, reason over approved context, and recommend within an explicitly approved use case.
- AI output is advisory. It is not an authorization decision, policy decision, approval, or provisioning command.
- Existing Accidion authorization and workflow controls remain authoritative.
- No AI feature may independently grant, revoke, modify, or approve identity access.
- Tenant context must come from trusted authenticated platform context. A model or prompt must never establish tenant authority.
- Do not send tenant data to a model provider until the provider, data categories, processing terms, region, retention, and technical controls have been reviewed and approved.
- Do not place secrets, credentials, tokens, or unnecessary personal data in prompts, logs, test fixtures, or evaluation datasets.
- AI features must be disabled by default until the required product, security, privacy, and operational approvals are complete.

## Development entry points

Before changing this module:

1. Read the root `AGENTS.md`, `RULES.md`, `docs/ARCHITECTURE.md`, `CONTRIBUTING.md`, and relevant accepted ADRs.
2. Read `ai/AGENTS.md`, `ai/ARCHITECTURE.md`, `ai/DEVELOPMENT.md`, and `ai/SAFETY.md`.
3. Inspect the existing code, tests, build configuration, and actual implementation status.
4. Confirm scope and acceptance criteria. Ask the maintainer when an approval-sensitive decision is missing.
5. Add appropriate software tests and AI evaluations for behaviour changes.
6. Run the repository's documented verification commands, including `make verify` where available, and report results accurately.

## Implementation status

This README documents intended module boundaries and engineering expectations. It does not assert that an AI gateway, provider, guardrail, policy engine, prompt registry, evaluation framework, or audit integration has been implemented or deployed.
