# ADR-002: Asynchronous messaging and transactional outbox

- **Status:** Proposed — pending architecture approval
- **Date:** 2026-11-10
- **Decision owner:** Architecture owner / CTO (to be assigned)
- **Scope:** MVP event-driven communication

## Context

Accidion needs reliable asynchronous communication between workloads. The architecture baseline names Amazon SQS and EventBridge for the MVP and requires a transactional outbox. The product-wide architecture may describe other messaging technologies; the six-month MVP plan governs the MVP delivery path.

## Proposed decision

Use Amazon SQS and EventBridge for MVP asynchronous messaging, with a transactional outbox pattern where a business-state change must be reliably coupled to publication of an event. Event envelopes should remain CloudEvents-compatible as stated by the MVP baseline.

## Alternatives considered

- **Kafka / Amazon MSK:** A possible broader-platform option, not the active MVP messaging path.
- **Direct synchronous service-to-service calls for all interactions:** Not sufficient as the general approach for asynchronous work and event delivery.

## Consequences and constraints

- Event publication, retries, duplicate delivery, idempotency, ordering requirements, dead-letter handling, and outbox relay behavior need explicit designs and tests before implementation.
- This ADR does not define API/event schemas, compatibility rules, retention periods, queue topology, or retry values. Those require their own review and, where applicable, approval under repository rules.
- No queues, buses, schemas, or infrastructure are created by this document.

## Approval

- **Approver:** Pending
- **Approval date:** Pending
- **Implementation evidence:** Not established by this ADR.
