# ADR-006: CI-controlled changes to production

- **Status:** Proposed — pending operational and security approval
- **Date:** 2026-11-10
- **Decision owner:** Engineering / DevSecOps owner (to be assigned)
- **Scope:** Production change governance

## Context

The architecture baseline states that production changes are CI-controlled and human-approved. Repository rules prohibit assistant workflows from accessing production, deploying, applying or destroying infrastructure, merging, approving, or bypassing protections.

## Proposed decision

Keep production changes within an approved CI/CD process with explicit human authorization at the required promotion gates. Assistant workflows may help prepare code, tests, documentation, and proposed pull requests, but must not perform production operations or bypass repository controls.

## Alternatives considered

- **Unreviewed direct production changes:** Not acceptable under the stated repository rules.
- **Assistant-initiated production deployment or infrastructure changes:** Prohibited by the current repository rules.

## Consequences and constraints

- The exact CI workflow, identities, environments, approvals, attestations, rollback process, and audit evidence must be specified and reviewed separately.
- Production credentials and secrets must not be exposed to assistant workflows.
- This ADR does not modify CI configuration, deployment workflows, infrastructure, branch protections, or production systems.
- No deployment or infrastructure operation is performed by this document.

## Approval

- **Approver:** Pending
- **Approval date:** Pending
- **Implementation evidence:** Not established by this ADR.
