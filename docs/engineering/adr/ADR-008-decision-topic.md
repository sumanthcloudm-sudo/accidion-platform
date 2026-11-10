# ADR-008: Six-month MVP scope governs delivery

- **Status:** Proposed — pending product and delivery approval
- **Date:** 2026-11-10
- **Decision owner:** Product owner / delivery owner (to be assigned)
- **Scope:** First design-partner MVP

## Context

The repository architecture baseline states that the six-month MVP plan governs delivery scope and that deployable services for deferred features must not be created. The broader product architecture may describe capabilities beyond the first MVP.

## Proposed decision

Use the six-month MVP plan as the delivery authority for what must be implemented for the first design-partner release. Do not create deployable services or claim delivery commitments for deferred capabilities solely because they appear in the broader product architecture. Changes to MVP scope require explicit product and delivery review.

## Alternatives considered

- **Implement the full long-term product catalogue in the MVP:** Not proposed because it conflicts with the stated six-month delivery boundary.
- **Create empty deployable services for future capabilities:** Not proposed.

## Consequences and constraints

- Backlog items should be labelled MVP MUST, MVP SHOULD, or deferred, with acceptance criteria and owners.
- Repository structure may reserve documented future locations, but placeholders are not implemented services or delivery evidence.
- Scope changes must be reflected consistently in planning and architecture documentation.
- This ADR does not independently redefine feature-level acceptance criteria or authorize implementation of deferred work.

## Approval

- **Product approver:** Pending
- **Delivery approver:** Pending
- **Approval date:** Pending
- **Implementation evidence:** Not established by this ADR.
