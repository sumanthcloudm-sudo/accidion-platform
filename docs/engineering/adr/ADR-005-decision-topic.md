# ADR-005: Tenant isolation and fail-closed authorization principles

- **Status:** Proposed — pending security and architecture approval
- **Date:** 2026-11-10
- **Decision owner:** Security owner / architecture owner (to be assigned)
- **Scope:** Platform-wide security boundary

## Context

Accidion is a multi-tenant Identity Governance and Administration platform. The architecture baseline identifies tenant isolation as a security boundary and requires authorization and tenant-context validation to fail closed.

## Proposed decision

Treat tenant isolation and server-side authorization as mandatory security properties across every workload, API, background job, connector, workflow, data access path, and administrative operation. If authorization or tenant context is missing, invalid, ambiguous, or cannot be verified, the operation must be denied rather than allowed by default.

## Alternatives considered

- **Trusting client-supplied tenant identifiers without server-side validation:** Rejected as inconsistent with the stated security boundary.
- **Fail-open behavior during authorization or tenant-context failures:** Rejected.

## Consequences and constraints

- Tenant identity must be established and validated by trusted server-side mechanisms; untrusted input must not override trusted context.
- Cross-tenant access must be explicitly authorized, narrowly scoped, and auditable; default behavior is isolation.
- Security design must define and test tenant context propagation, data-access enforcement, cache boundaries, background processing, connector credentials, and administrative access.
- Because tenant isolation and authorization changes are explicitly approval-gated by RULES.md, this ADR is a principle-level proposal only. It does not authorize implementation, schema, authentication, authorization, cryptographic, or data-layer changes.
- Required threat modelling and negative cross-tenant tests remain to be designed and evidenced.

## Approval

- **Security approver:** Pending
- **Architecture approver:** Pending
- **Approval date:** Pending
- **Implementation evidence:** Not established by this ADR.
