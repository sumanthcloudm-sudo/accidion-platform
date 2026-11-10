# Architecture Decision Records

These records document proposed architecture decisions for Accidion Identity Cloud. **A proposed ADR is not an approval.** Each record remains pending until the named decision owners explicitly approve it.

## Proposed records

| ADR | Topic | Current status |
|---|---|---|
| [ADR-001](ADR-001-decision-topic.md) | AWS ECS Fargate for the MVP runtime | Proposed — pending approval |
| [ADR-002](ADR-002-decision-topic.md) | SQS, EventBridge and transactional outbox | Proposed — pending approval |
| [ADR-003](ADR-003-decision-topic.md) | Aurora PostgreSQL and initial search strategy | Proposed — pending approval |
| [ADR-004](ADR-004-decision-topic.md) | Temporal Cloud for MVP workflow orchestration | Proposed — pending approval |
| [ADR-005](ADR-005-decision-topic.md) | Tenant isolation and fail-closed authorization | Proposed — pending security and architecture approval |
| [ADR-006](ADR-006-decision-topic.md) | CI-controlled production changes | Proposed — pending operational and security approval |
| [ADR-007](ADR-007-decision-topic.md) | AI Copilot disabled by default and non-autonomous | Proposed — pending product, security and architecture approval |
| [ADR-008](ADR-008-decision-topic.md) | Six-month MVP scope governs delivery | Proposed — pending product and delivery approval |
| [ADR-009](ADR-009-decision-topic.md) | Valkey evaluation and conditional adoption | Evaluation required; adoption not approved |
| [ADR-010](ADR-010-decision-topic.md) | Kubernetes remains an inactive future target | Proposed — pending architecture approval |

## Approval and change process

1. Read `RULES.md` and `docs/ARCHITECTURE.md` before changing an ADR.
2. Confirm the decision owner and required security, product, delivery, or operations reviewers.
3. Record the decision, rationale, alternatives, consequences, approver, and approval date.
4. Keep the status as **Proposed** until explicit approval is recorded.
5. If an approved decision changes, create a superseding ADR and link the records; do not silently rewrite history.

ADR presence does not authorize implementation. Changes involving dependencies, migrations, API/event contracts, authentication/authorization, cryptography, tenant isolation, CI, or IaC remain subject to the approval requirements in `RULES.md`.

These documents are proposals only. They do not prove that any component is implemented, deployed, or production-ready.
