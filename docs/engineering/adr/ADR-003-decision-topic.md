# ADR-003: Aurora PostgreSQL and initial search strategy

- **Status:** Proposed — pending architecture approval
- **Date:** 2026-11-10
- **Decision owner:** Architecture owner / data owner (to be assigned)
- **Scope:** MVP persistence and search baseline

## Context

The MVP requires durable storage for identity, governance, workflow-related application data, and audit-related metadata. The architecture baseline identifies Aurora PostgreSQL as the initial data store and PostgreSQL-based search initially.

## Proposed decision

Use Aurora PostgreSQL as the proposed primary relational data store for the MVP. Begin with PostgreSQL capabilities for search rather than introducing a separate search platform at the start. Consider OpenSearch only through a later evidence-based architecture decision if PostgreSQL search does not meet validated requirements.

## Alternatives considered

- **OpenSearch from MVP launch:** Deferred until search volume, query needs, and operational requirements justify it.
- **Multiple primary persistence technologies:** Not proposed as the initial MVP baseline.

## Consequences and constraints

- Data ownership, schema boundaries, indexing, backup/restore, retention, encryption, and recovery objectives need detailed designs.
- Search performance and relevance must be measured against representative, synthetic test data before deciding whether a dedicated search engine is needed.
- This ADR does not approve database migrations, schemas, data contracts, or production database changes.
- No database or search infrastructure is created by this document.

## Approval

- **Approver:** Pending
- **Approval date:** Pending
- **Implementation evidence:** Not established by this ADR.
