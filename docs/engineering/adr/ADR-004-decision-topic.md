# ADR-004: Temporal Cloud for MVP workflow orchestration

- **Status:** Proposed — pending architecture approval
- **Date:** 2026-11-10
- **Decision owner:** Architecture owner / workflow owner (to be assigned)
- **Scope:** MVP long-running business workflows

## Context

Identity lifecycle, access requests, approvals, certifications, and remediation can span multiple steps and require durable workflow state. The architecture baseline identifies Temporal Cloud as the MVP workflow platform and allows a local Temporal server for development.

## Proposed decision

Use Temporal Cloud as the proposed managed workflow orchestration platform for MVP environments. A local Temporal server may be used for local development where appropriate. Workflow definitions and activities must preserve authorization checks and tenant context at each relevant boundary.

## Alternatives considered

- **Custom workflow engine:** Not proposed as the MVP baseline.
- **Self-managed Temporal deployment:** Not the proposed managed MVP path; any change requires a separate decision.

## Consequences and constraints

- Workflow retries, idempotency, timeouts, compensation, visibility, tenant context propagation, and failure handling require explicit design and tests.
- Workflow histories and payloads must not become a channel for secrets or unnecessary sensitive data.
- This ADR does not approve workflow API contracts, event schemas, or implementation changes.
- No Temporal account, namespace, worker, or infrastructure is provisioned by this document.

## Approval

- **Approver:** Pending
- **Approval date:** Pending
- **Implementation evidence:** Not established by this ADR.
