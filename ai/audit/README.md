# Accidion AI Audit

**Status: PROPOSED — NOT APPROVED**

This directory contains proposed documentation for recording privacy-minimized AI operation metadata through a future host-owned Accidion `acc-audit` capability, if defined and approved. It does not define an approved event contract, API, transport, storage system, service, or runtime implementation.

## Current status

- `ai/audit/` contains documentation only; there is no AI audit integration or implementation.
- `services/acc-audit/` is a placeholder directory. No host audit API, event schema, implementation, or operational contract was found in the repository.
- The exact host audit boundary, producer identity mechanism, delivery acknowledgment, persistence, access controls, retention, integrity mechanism, and outage behavior have not been established here.
- ADR-002 and ADR-003 are Proposed, not accepted. Neither approves a transport, event schema, database, or audit implementation.
- ADR-007 and ADR-008 remain Proposed with approvals pending. They do not approve Copilot scope or enable AI.

The proposed integration point is a host-owned audit capability once its owner defines and approves an interface. AI components must not create a separate audit service, database, event bus, deployment, or source of audit authority. `ai/audit/` is intended for AI-specific event definitions and integration guidance only.

## Documents

- [AI_AUDIT_EVENT_CONTRACT.md](./AI_AUDIT_EVENT_CONTRACT.md) describes a candidate event envelope, operation event categories, privacy and validation requirements, audit-delivery separation, failure handling, acceptance criteria, and unresolved approvals.

## Non-goals and boundaries

- This proposal does not claim that `acc-audit` or an AI audit publisher is implemented.
- This proposal does not select an API, event bus, database, transport, framework, dependency, or deployment model.
- AI event metadata is not host authorization evidence and cannot grant access or approve an operation.
- Do not record raw prompts, raw model responses, credentials, secrets, or unnecessary personal or identity data by default.
- Tenant and actor references must come from trusted authenticated host context; untrusted request or provider fields are not authoritative.
- Copilot remains disabled by default. Audit documentation does not enable or authorize AI processing.

## Approval dependencies

Any future contract or implementation requires decisions from Product, Security, Privacy/Data Governance, Architecture, the host audit owner, and maintainers as applicable. In particular, the host audit owner must first identify the actual integration boundary and its semantics. Data retention, audit integrity, tenant-scoped access, and audit-failure behavior require explicit approval before implementation.

All proposals remain subject to root `AGENTS.md`, `RULES.md`, the architecture baseline, accepted ADRs, and applicable security policies. Proposed ADRs are not approvals.
