# ADR-009: Valkey evaluation and conditional adoption

- **Status:** Proposed — evaluation required; adoption not approved
- **Date:** 2026-11-10
- **Decision owner:** Architecture owner / platform owner (to be assigned)
- **Scope:** MVP cache layer

## Context

The architecture baseline identifies Valkey as subject to approval. A cache may support performance-sensitive workloads, but its need, compatibility requirements, operating model, and security implications must be validated.

## Proposed decision

Do not treat Valkey as an approved or mandatory MVP dependency yet. Evaluate whether a managed Valkey-compatible cache is required for validated MVP use cases. Adoption requires an explicit decision documenting the use cases, compatibility differences, operational ownership, security controls, failure behavior, and cost.

## Alternatives considered

- **No dedicated cache initially:** Keep this option open until a measurable requirement is established.
- **Redis-compatible managed cache:** Evaluate only through the approval process; compatibility must not be assumed without testing.

## Consequences and constraints

- Application behavior must not depend on an unapproved cache service.
- Cache keys, tenant boundaries, data sensitivity, TTLs, invalidation, and outage behavior require review before adoption.
- This ADR does not approve a dependency change, infrastructure change, or production configuration.
- No cache resources are provisioned by this document.

## Approval

- **Approver:** Pending
- **Approval date:** Pending
- **Implementation evidence:** Not established by this ADR.
