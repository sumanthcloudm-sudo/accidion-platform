# ADR-001: AWS ECS Fargate for the MVP runtime

- **Status:** Proposed — pending architecture approval
- **Date:** 2026-11-10
- **Decision owner:** Architecture owner / CTO (to be assigned)
- **Scope:** Six-month design-partner MVP only

## Context

The Accidion Identity Cloud MVP needs a deployable runtime within the six-month delivery window. The current architecture baseline identifies AWS ECS Fargate as the active MVP runtime and explicitly keeps Kubernetes inactive until a separate ADR is approved.

## Proposed decision

Use AWS ECS Fargate as the active compute/runtime target for MVP workloads. Treat Kubernetes manifests and related deployment assets as inactive reference/future-target material. Do not deploy workloads to Kubernetes or make Kubernetes a runtime dependency unless a later, explicitly approved ADR changes this position.

## Alternatives considered

- **Kubernetes / EKS:** Retain as a possible future platform, but do not activate it for this MVP without a separate approved decision.
- **Multiple active runtime platforms:** Not proposed for the MVP because it would create additional operational paths to deliver and validate.

## Consequences and constraints

- MVP deployment documentation and implementation should describe the ECS path.
- Kubernetes assets must be clearly marked inactive and must not be presented as production-ready.
- This ADR does not select detailed networking, service sizing, scaling, ingress, or deployment-pipeline configurations.
- No infrastructure is created or changed by this document.

## Approval

- **Approver:** Pending
- **Approval date:** Pending
- **Implementation evidence:** Not established by this ADR.
